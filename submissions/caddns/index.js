#!/usr/bin/env node
import chalk from 'chalk';
import chalkAnimation from 'chalk-animation';
import inquirer from 'inquirer';
import { createSpinner } from 'nanospinner';
import os from 'os';
import path from 'path';
import fs from 'fs';
import { execSync } from "child_process";
let v = '1.0.1'
const configPath = path.join(os.homedir(), '.ca-ddns.json');

let apiKey = loadApiKey();
let domains = loadDomains();

// Tasks Setup Functions

function removeScheduledTaskAndFile() {
    const scriptPath = path.join(os.homedir(), "caddns.js");
    try {
        if (os.platform() === "win32") {
            const taskName = "UpdateDNSRecords";
            execSync(`schtasks /delete /tn ${taskName} /f`, { stdio: "ignore" });
        } else {
            const crontab = execSync("crontab -l", { encoding: "utf-8" }).split("\n");
            const filteredCrontab = crontab.filter(line => !line.includes(scriptPath)).join("\n");

            execSync(`echo "${filteredCrontab}" | crontab -`);
        }
    } catch (err) {
        console.warn("⚠️ No scheduled task found or error removing it:", err.message);
    }

    try {
        if (fs.existsSync(scriptPath)) {
            fs.unlinkSync(scriptPath);
        } else {
            console.log("⚠️ Script file not found, skipping deletion.");
        }
    } catch (err) {
        console.error("❌ Failed to delete script file:", err.message);
    }
}

async function createUpdateScript(apiKey, zoneId, domains) {
    const scriptContent = `const fs = require("fs");

const apiKey = "${apiKey}";
const zoneId = "${zoneId}";
const domainsToUpdate = ${JSON.stringify(domains)};

async function updateDNSRecords() {
    for (const domain of domainsToUpdate) {
        try {
            const url = \`https://api.cloudflare.com/client/v4/zones/\${zoneId}/dns_records?type=A&name=\${domain}\`;
            
            const response = await fetch(url, {
                method: "GET",
                headers: {
                    "Authorization": \`Bearer \${apiKey}\`,
                    "Content-Type": "application/json"
                }
            });

            const data = await response.json();
            if (!data.success || data.result.length === 0) {
                console.error(\`❌ Failed to get record for \${domain}:\`, data.errors);
                continue;
            }

            const record = data.result[0]; 
            const recordId = record.id;
            const currentIP = record.content;

            const publicIp = await (await fetch("https://api64.ipify.org?format=json")).json();
            const newIP = publicIp.ip;

            if (currentIP === newIP) {
                console.log(\`✅ \${domain} is already up to date (\${newIP})\`);
                continue;
            }

            const updateUrl = \`https://api.cloudflare.com/client/v4/zones/\${zoneId}/dns_records/\${recordId}\`;
            const updateResponse = await fetch(updateUrl, {
                method: "PUT",
                headers: {
                    "Authorization": \`Bearer \${apiKey}\`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    type: "A",
                    name: domain,
                    content: newIP,
                    ttl: 120,
                    proxied: false
                })
            });

            const updateData = await updateResponse.json();
            if (!updateData.success) {
                console.error(\`❌ Failed to update \${domain}:\`, updateData.errors);
                continue;
            }

            console.log(\`✅ Successfully updated \${domain} to \${newIP}\`);

        } catch (err) {
            console.error(\`❌ Error updating \${domain}:\`, err);
        }
    }
}

updateDNSRecords();`;

    const scriptPath = path.join(os.homedir(), "caddns.js");

    fs.writeFileSync(scriptPath, scriptContent);

    return scriptPath;
}

function setupCronJob(scriptPath) {
    try {
        const cronJob = `0 0 * * * /usr/bin/node ${scriptPath} >> /var/log/dns-update.log 2>&1`;
        execSync(`(crontab -l 2>/dev/null; echo "${cronJob}") | crontab -`);
    } catch (error) {
        console.error("❌ Failed to schedule cron job:", error.message);
    }
}

function setupWindowsTask(scriptPath) {
    const taskName = "UpdateDNSRecords";
    const escapedScriptPath = scriptPath.replace(/\\/g, '\\\\');
    const nodePath = `"${process.env['ProgramFiles']}\\nodejs\\node.exe"`;
    const taskCmd = `\\"${nodePath} ${escapedScriptPath}\\"`;
    const powershellCmd = `SchTasks /Create /SC DAILY /TN "${taskName}" /TR ${taskCmd} /ST 00:00 /F`;
    try {
        execSync(`powershell.exe -Command "${powershellCmd}"`, { stdio: "inherit" });
    } catch (error) {
        console.error("❌ Failed to schedule task in Windows:", error.message);
    }
}


async function setupAutoUpdate(apiKey, zoneId, domains) {
    const scriptPath = await createUpdateScript(apiKey, zoneId, domains);

    if (process.platform === "win32") {
        setupWindowsTask(scriptPath);
    } else {
        setupCronJob(scriptPath);
    }
}



// Helper functions

const sleep = (ms = 2000) => new Promise((r) => setTimeout(r, ms))


async function getARecords(zoneId) {
    const url = `https://api.cloudflare.com/client/v4/zones/${zoneId}/dns_records?type=A`;
    
    const response = await fetch(url, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${apiKey}`,
            "Content-Type": "application/json"
        }
    });

    const data = await response.json();

    if (!data.success) {
        console.error("❌ Error fetching A records:", data.errors);
        return [];
    }

    return data.result.map(record => (record.name));
}

function ensureConfigFile() {
    if (!fs.existsSync(configPath)) {
        fs.writeFileSync(configPath, JSON.stringify({}, null, 2)); 
    }
}

function loadConfig() {
    ensureConfigFile(); 
    return JSON.parse(fs.readFileSync(configPath, "utf-8"));
}

function saveConfig(updatedData, onlyDomains = false) {
    ensureConfigFile(); 
    const config = loadConfig();
    let newConfig;
    if(onlyDomains) {
        newConfig = { ...config, domains: Array.isArray(updatedData) ? updatedData.flat() : updatedData };
        } else {
        newConfig = { ...config, ...updatedData }; 
    }
    fs.writeFileSync(configPath, JSON.stringify(newConfig, null, 2));
}

async function saveApiKey(apiKey) {
    saveConfig({ apiKey });
    console.log('✅ Api key saved. Please restart the program to continue.')
}

function loadApiKey() {
    return loadConfig().apiKey || null;
}

async function saveZoneId(zoneId) {
    saveConfig({ zoneId });
}

function loadZoneId() {
    return loadConfig().zoneId || null;
}

function loadDomains() {
    return loadConfig().domains || null;
}

function loadPossibleRecords() {
    return loadConfig().possible || null;
}

async function getZoneId(zoneName) {
    const cachedZoneId = loadZoneId(); 

    if (cachedZoneId) {
        return cachedZoneId; 
    }

    try {
        const response = await fetch(`https://api.cloudflare.com/client/v4/zones?name=${zoneName}`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${apiKey}`,
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();

        if (!data.success || data.result.length === 0) {
            console.error("❌ Error fetching Zone ID:", JSON.stringify(data.errors, null, 2));
            return null;
        }

        const zoneId = data.result[0].id;
        saveZoneId(zoneId); 
        return zoneId;

    } catch (error) {
        console.error("❌ Request failed:", error);
        return null;
    }
}



// Text, prompts & other stuff

async function mainMenu(domains = null) {
    const greet = chalkAnimation.pulse(`Cloudflare automatic DDNS Version ${v}`)
    await sleep();
    greet.stop();

    if(domains == null) {
        const whatToDo = await inquirer.prompt({
            name: 'WhatToDo',
            type: 'list',
            message: 'What would you like to do?\n',
            choices: [
                "Create new configuration",
            ]
        })
        return handleAnswer(whatToDo.WhatToDo);
    } else {
        const whatToDo = await inquirer.prompt({
            name: 'WhatToDo',
            type: 'list',
            message: 'What would you like to do?\n',
            choices: [
                "Status",
                "Create new configuration",
                "Add record to rule",
                "Remove record from rule",
                "Remove all CADDNS entries"
            ]
        })
        return handleAnswer(whatToDo.WhatToDo);
    }

}

async function getApiKey() {
    const getapikey = await inquirer.prompt({
        name: 'getapikey',
        type: 'password',
        message: 'Please paste your Cloudflare api key\n',
    })
    return getapikey.getapikey;
}


async function getFromUser(name, message = '') {
    const getInput = await inquirer.prompt({
        name,
        type: 'input',
        message,
    })
    return getInput[name];
}

async function correct() {
    const confirmIp = await inquirer.prompt({
        name: 'confirmIp',
        type: 'confirm',
        message: 'Is this correct?'
    })
    return confirmIp.confirmIp;
}

async function selectRecordsPrompt(records) {
    const selectRecords = await inquirer.prompt({
        name: 'selectRecords',
        type: 'checkbox',
        message: 'What records would you like to add to this rule?\n',
        choices: records, 
    })
    return selectRecords.selectRecords;
}

async function addRecordPrompt() {
    const enabledDomains = loadDomains();

    console.log(`
        ${chalk.bgBlue.black(' QUICK OVERVIEW ')}
        
        ${chalk.red('TL;DR - Use this to add records to the IP update rule.')}
        
        This option allows you to select records to add to the automatic IP update rule.  
        The existing configuration will be updated, including only the selected records.  
        
        Need to remove some or all records later? You can do that from the main menu.
        `);
    await sleep(4000);
    const allDomains = loadPossibleRecords();
    const possibleToEnableDomains = allDomains.filter(item => !enabledDomains.includes(item));
    const choices = [
        ...possibleToEnableDomains.map(domain => ({ name: domain, value: domain })), 
        ...enabledDomains.map(domain => ({ name: domain, value: domain, checked: true, disabled: "(Already Enabled)" }))
    ];
    const response = await inquirer.prompt([
        {
            name: "selectedRecords",
            type: "checkbox",
            message: "Select records to add:",
            choices: choices
        }
    ]);

    return [response.selectedRecords, ...enabledDomains];
}

async function removeRecordPrompt() {
    const enabledDomains = loadDomains();

    console.log(`
        ${chalk.bgBlue.black(' QUICK OVERVIEW ')}
        
        ${chalk.red('TL;DR - Use this to remove records from the IP update rule.')}
        
        This option allows you to select records to remove from the automatic IP update rule.  
        The existing configuration will be updated, keeping only the remaining records.  
        
        Need to add more records later? You can do that from the main menu.
        `);
    await sleep(1000);
    const response = await inquirer.prompt([
        {
            name: "selectedRecords",
            type: "checkbox",
            message: "Select records to remove:",
            choices: enabledDomains
        }
    ]);
    const newRecords = enabledDomains.filter(record => !response.selectedRecords.includes(record))
    if(response.selectedRecords.length == enabledDomains.length) {
        return [];
    } else {
        return [newRecords];
    }
}

// Main menu handler function

async function handleAnswer(opt) {
    if(opt == 'Remove all CADDNS entries') {
        const spinner = createSpinner('Loading...').start();
        fs.unlink(configPath, (err) => {
            if (err) {
                console.error("❌ Error deleting file:", err);
            }
        });
        removeScheduledTaskAndFile();
        spinner.success('Data deleted successfully.');
        process.exit(0);
    } else if(opt == 'Create new configuration') {
        const spinner = createSpinner('Loading...').start();
        try {
            const res = await fetch('https://api64.ipify.org?format=json');
            const data = await res.json();
            spinner.stop();
            await createNewConfig(data.ip);
        } catch (error) {
            spinner.stop();
            await createNewConfig();
        }
    } else if(opt == 'Add record to rule') {
        const zoneID = loadZoneId();
        const allRecords = await addRecordPrompt();
        const spinner = createSpinner('Creating automated task...').start();
        removeScheduledTaskAndFile();
        try {
            await setupAutoUpdate(apiKey, zoneID, allRecords);
            spinner.success();
        } catch (error) {
            spinner.error();
            console.error("❌ Error setting up auto-update:", error);
            return;
        }
        console.log(`
            ${chalk.bgRed(' TASK ADDED SUCCESSFULLY ')}
            
            This script is set to automatically update Cloudflare IPs for the following record(s):  
            ${chalk.red(allRecords.join(', '))}
            
            The update will run daily at midnight, ensuring they match this machine's public IP.
            `);

        saveConfig(allRecords, true)
    } else if(opt == 'Remove record from rule') {
        const zoneID = loadZoneId();
        const allRecords = await removeRecordPrompt();
        if(allRecords.length == 0) {
            console.log(`
                ${chalk.bgYellow.black(' WARNING ')}
                
                ${chalk.red('All records have been removed from the rule.')}
                Since there are no records left, this automation is no longer needed.
                Cleaning up your configuration...
                `);

            const spinner = createSpinner('Removing your configs...').start();
            fs.unlink(configPath, (err) => {
                if (err) {
                    console.error("❌ Error deleting file:", err);
                }
            });
            removeScheduledTaskAndFile();
            spinner.success('Data deleted successfully.');
            process.exit(0);
        }
        const spinner = createSpinner('Creating automated task...').start();
        removeScheduledTaskAndFile();
        try {
            await setupAutoUpdate(apiKey, zoneID, allRecords);
            spinner.success();
        } catch (error) {
            spinner.error();
            console.error("❌ Error setting up auto-update:", error);
            return;
        }
        console.log(`
            ${chalk.bgRed(' TASK ADDED SUCCESSFULLY ')}
            
            This script is set to automatically update Cloudflare IPs for the following record(s):  
            ${chalk.red(allRecords.join(', '))}
            
            The update will run daily at midnight, ensuring they match this machine's public IP.
            `);
        saveConfig(allRecords, true)
    } else if(opt == 'Status') {
        const enabledDomains = loadDomains();

        console.log(`
        ${chalk.bgRed('STATUS')}
        Running ${chalk.red(`Cloudflare Automatic Dynamic DNS | Version ${v} | @rocristoi`)}
        Active domain(s): ${chalk.cyan(enabledDomains.join(', '))}

        ${chalk.gray('Restart the program to continue.')}
        `)
    }
    await sleep();

}

async function createNewConfig(ip = null) {
    if( ip ==  null || ip ==  undefined) {
        console.log(chalk.red(`Unable to automatically determine your IP address.`));  
        console.log(chalk.red(`This indicates an issue with the internet configuration on this machine.`));  
        console.log(chalk.white(`CADDNS cannot proceed.`));  
        process.exit(1);
    }
    console.log(chalk.red(`Detected public IP address is ${ip}`))
    const cont = await correct();
    if(cont) {
        let zoneId = loadZoneId();
        let records;

        if(zoneId) {
            const spinner = createSpinner('Loading Data...').start();
            records = await getARecords(zoneId);
            spinner.success();
        } else {
            const zoneName = await getFromUser('zoneName', 'Please enter your zone name (domain name):');
            const spinner = createSpinner('Loading Data...').start();
            zoneId = await getZoneId(zoneName);
            records = await getARecords(zoneId);
            spinner.success();
        }
        const slectedDomainNames = await selectRecordsPrompt(records);
        if (!slectedDomainNames || slectedDomainNames.length === 0) {
            console.log("⚠️ No records selected. Exiting...");
            return;
        }
        const lastSpinner = createSpinner('Creating automated task...').start();
        try {
            await setupAutoUpdate(apiKey, zoneId, slectedDomainNames);
            lastSpinner.success();
        } catch (error) {
            lastSpinner.error();
            console.error("❌ Error setting up auto-update:", error);
            return;
        }
        
        console.log(`
            ${chalk.bgRed(' TASK ADDED SUCCESSFULLY ')}
            
            This script is set to automatically update Cloudflare IPs for the following record(s):  
            ${chalk.red(slectedDomainNames.join(', '))}
            
            The update will run daily at midnight, ensuring they match this machine's public IP.
            `);
        saveConfig(slectedDomainNames, true)
        saveConfig({
            possible: records,
        })
        

    } else {
        console.log(chalk.red(`Unable to automatically determine your IP address.`));  
        console.log(chalk.red(`This indicates an issue with the internet configuration on this machine.`));  
        console.log(chalk.white(`CADDNS cannot proceed.`));  
        process.exit(1);
    }
}

async function Welcome() {
    const greet = chalkAnimation.pulse("Cloudflare automatic DDNS V1.0")
    await sleep();
    greet.stop();

    console.log(`
        ${chalk.bgBlue.black(' GETTING STARTED ')}
        
        It looks like you're running CADDNS for the first time.
        Hosting a service on this machine, but the IP changes often?
        This tool will automatically update your Cloudflare records ${chalk.red('daily')}.
        
        ${chalk.red('Built with ❤️ by @rocristoi')}
        `);
    await sleep(4000);
}

// Main Program

if (!apiKey) {
    await Welcome();
    const newApiKey = await getApiKey();
    await saveApiKey(newApiKey);
} else {
    await mainMenu(domains);
}

