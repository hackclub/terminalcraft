#!/usr/bin/env node
import inquirer from "inquirer";
import fs from 'fs';
import os from 'os';
import path from 'path';
import axios from 'axios';  
import { createSpinner } from 'nanospinner';
import chalk from 'chalk';
import gradient from 'gradient-string';

const STORAGE_DIR = path.join(os.homedir(), '.essays')
const essaysFilePath = path.join(STORAGE_DIR, 'essays.json');
const DEEPSEEK_API_URL = 'https://ai.hackclub.com/chat/completions';

if(!fs.existsSync(STORAGE_DIR)) {
    fs.mkdirSync(STORAGE_DIR, {recursive: true});
}

if(!fs.existsSync(essaysFilePath)) {
    fs.writeFileSync(essaysFilePath, '[]');
}

// click 'add new essay'
async function addEssay() {
    const {prompt, content, program, program_name} = await inquirer.prompt([
        {type:'input', name: 'prompt', message: 'Enter essay prompt: '},
        {type:'input', name: 'content', message: 'Enter Essay: '},
        {type:'input', name: 'program', message: 'short desc (eng, math, etc.): '},
        {type:'input', name: 'program_name', message: 'Name of program: '},
    ]);

    const essays = JSON.parse(fs.readFileSync(essaysFilePath, 'utf8'));
    essays.push({title: prompt, content: content, program: program, name: program_name});
    fs.writeFileSync(essaysFilePath, JSON.stringify(essays, null, 2));
    
    console.log('Essay added successfully!');
}

async function addLongEssay() {
    const {prompt, filePath, program, program_name} = await inquirer.prompt([
        {type:'input', name: 'prompt', message: 'Enter essay prompt: '},
        {type:'input', name: 'filePath', message: 'Enter file path of the essay (MUST BE TXT): '},
        {type:'input', name: 'program', message: 'short desc (eng, math, etc.): '},
        {type:'input', name: 'program_name', message: 'Name of program: '},
    ]);

    const essays = JSON.parse(fs.readFileSync(essaysFilePath, 'utf8'));
    const essay = fs.readFileSync(filePath, 'utf8');
    essays.push({title: prompt, content: essay, program: program, name: program_name});
    fs.writeFileSync(essaysFilePath, JSON.stringify(essays, null, 2));
    
    console.log('Essay added successfully!');
}

// click 'view all essays'
async function viewEssays() {
    const essays = JSON.parse(fs.readFileSync(essaysFilePath, 'utf8'));

    if (essays.length === 0) {
        console.log(chalk.yellow('\nNo essays found. Add some essays first!\n'));
        return;
    }

    console.log(chalk.cyan('\n📚 Your Essays:\n'));
    
    essays.forEach((essay, index) => {
        console.log(chalk.blue(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`));
        console.log(chalk.green(`Essay #${index + 1}`));
        console.log(chalk.yellow(`Prompt: ${essay.title}`));
        console.log(chalk.magenta(`Program: ${essay.program}`));
        console.log(chalk.cyan(`Program Name: ${essay.name}`));
        console.log(chalk.white(`\nContent:\n${essay.content}\n`));
    });
    
    console.log(chalk.blue(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`));
}

// click 'find similar essay'
async function findSimilarEssay() {
    const {prompt} = await inquirer.prompt([
        {type:'input', name: 'prompt', message: 'Enter new essay prompt (include max word count): '},
    ]);

    const essays = JSON.parse(fs.readFileSync(essaysFilePath, 'utf8'));
    const prompts = essays.map(essay => essay.title);

    const spinner = createSpinner('Deepseek thinking...').start();

    try {
        const response = await axios.post(DEEPSEEK_API_URL, {
            messages: [
                {
                    role: 'user',
                    content: 'look at this essay prompt: ' + prompt + ' and compare it with all these prompts:' + prompts + '. which prompt is the MOST SIMILAR to the prompt above? ONLY RETURN THE MOST SIMILAR PROMPT AND NOTHING ELSE. You must return a prompt that is in the list of prompts provided.'
                }
            ]
        });

        spinner.success({ text: 'API request completed!' });

        const mostSimilarPrompt = response.data.choices[0].message.content;
        const mostSimilarEssay = essays.find(essay => essay.title === mostSimilarPrompt);
        console.log(mostSimilarEssay.content);
    } catch (error) {
        spinner.error({ text: 'No similar essay found' });
        console.log('No similar essay found. Try writing a new essay for this prompt & add it to this program');
    }
}

// remove 'essay'
async function removeEssay() {
    const {prompt} = await inquirer.prompt([
        {type:'input', name: 'prompt', message: 'Enter the EXACT essay prompt: '},
    ]);
    
    const essays = JSON.parse(fs.readFileSync(essaysFilePath, 'utf8'));
    const filteredEssays = essays.filter(essay => essay.title !== prompt);

    fs.writeFileSync(essaysFilePath, JSON.stringify(filteredEssays, null, 2));
    console.log('Essay removed successfully!');
}

// click 'write new essay'
async function writeNewEssay() {
    const {prompt} = await inquirer.prompt([
        {type:'input', name: 'prompt', message: 'Enter essay prompt: '},
    ]);

    const essays = JSON.parse(fs.readFileSync(essaysFilePath, 'utf8'));
    const essayContent = essays.map(essay => essay.content).join('\n');
    
    const spinner = createSpinner('Deepseek thinking...').start();

    const response = await axios.post(DEEPSEEK_API_URL, {
        messages: [
            {
                role: 'user',
                content: 'write an essay for this prompt: ' + prompt + 'based on previous essays for this user: ' + essayContent
            }
        ]
    })

    spinner.success({ text: 'Essay generated!' });

    const essay = response.data.choices[0].message.content;
    console.log(essay);
    console.log('THIS ESSAY IS AI WRITTEN. ONLY USE THIS FOR INSPIRATION. After editing the essay as you like, add it to your list by rerunning this program.')
}


// main
async function main() {

    console.log(gradient.rainbow('Welcome to your AI essay assistant!'));
    console.log(chalk.cyan(`
📝 INSTRUCTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This program helps you organize essays for college/camp applications. 
If you're a new user, add at least 5 (preferably 10+) essays that you've already written

This program helps you do the following:
1. Store, view, remove, and find essays you've written 
2. Find similar essays you've already written to save time
3. Streamline writing w/ AI as a starting point

Please note: This program is powered by HackClub's DeepSeek API, so don't abuse the AI features. 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    `));

    const { action } = await inquirer.prompt({
        type: 'list',
        name: 'action',
        message: 'What would you like to do?',
        choices: [
            'Add new essay',
            'Add long essay via file',
            'View all essays',
            'Find similar essay',
            'Remove essay',
            'Write new essay'
        ]
    });

    if (action === 'Add new essay') {
        await addEssay();
    } else if (action === 'View all essays') {
        await viewEssays();
    } else if (action === 'Find similar essay') {
        await findSimilarEssay();
    } else if(action === 'Remove essay') {
        await removeEssay();
    } else if(action === 'Add long essay via file') {
        console.log('If you\'re essay is very long, you can upload it through a text filef')
        await addLongEssay();
    } else if(action === 'Write new essay') {
        console.log('This works best if you have a few essays already written')
        await writeNewEssay();
    } else {
        console.log('You selected:', action);
    }
}

main().catch(console.error);