#!/usr/bin/env node

import speedTest from 'speedtest-net';
import chalk from 'chalk';
import cliProgress from 'cli-progress';

async function runSpeedTest() {
    console.log(chalk.cyan('Running Speed Test...'));

    const downloadBar = new cliProgress.SingleBar({
        format: `${chalk.green('Download')} |{bar}| {speed} Mbps`,
        barCompleteChar: '\u2588',
        barIncompleteChar: '\u2591',
        hideCursor: true,
    });

    const uploadBar = new cliProgress.SingleBar({
        format: `${chalk.blue('Upload  ')} |{bar}| {speed} Mbps`,
        barCompleteChar: '\u2588',
        barIncompleteChar: '\u2591',
        hideCursor: true,
    });

    try {
        const result = await speedTest({ acceptLicense: true, acceptGdpr: true });

        //download progress bar
        downloadBar.start(100, 0, { speed: '0.00' });
        for (let i = 0; i <= 100; i += 10) {
            downloadBar.update(i, {
                speed: ((result.download.bandwidth / 125000) * (i / 100)).toFixed(2),
            });
            await new Promise(resolve => setTimeout(resolve, 200));
        }
        downloadBar.stop();

        //upload progress bar
        uploadBar.start(100, 0, { speed: '0.00' });
        for (let i = 0; i <= 100; i += 10) {
            uploadBar.update(i, {
                speed: ((result.upload.bandwidth / 125000) * (i / 100)).toFixed(2),
            });
            await new Promise(resolve => setTimeout(resolve, 200));
        }
        uploadBar.stop();

        //final results
        console.log(chalk.green('\nSpeed Test Results:'));
        console.log(`${chalk.bold('Download Speed:')} ${(result.download.bandwidth / 125000).toFixed(2)} Mbps`);
        console.log(`${chalk.bold('Upload Speed:')} ${(result.upload.bandwidth / 125000).toFixed(2)} Mbps`);
        console.log(`${chalk.bold('Ping:')} ${result.ping.latency} ms`);
        console.log(`${chalk.bold('Jitter:')} ${result.ping.jitter} ms`);
        console.log(`${chalk.bold('ISP:')} ${result.isp}`);
        console.log(`${chalk.bold('Location:')} ${result.server.location}`);
        console.log(`${chalk.bold('Link:')} ${result.result.url}`);
    } catch (error) {
        downloadBar.stop();
        uploadBar.stop();
        console.error(chalk.red(`Error: ${error.message}`));
    }
}

runSpeedTest();
