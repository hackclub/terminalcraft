#!/usr/bin/env node
const { program } = require('commander');
const stego = require('./stego');
const path = require('path');

program
    .option('-s, --string [string]', 'A string argument')
    .option('-f, --file [file]', 'A file argument')
    .option('-p, --password [password]', 'A password argument')
    .option('-o, --output [output]', 'An output argument')
    .argument('<file>', 'A file argument')
program.parse();

const string = program.opts().string;
const password = program.opts().password;
let fileToHide = program.opts().file;
let output = program.opts().output;
const file = path.resolve(program.args[0]);

if (fileToHide) fileToHide = path.resolve(fileToHide);
if (output) output = path.resolve(output);

if (string && fileToHide) {
    console.error('Please provide either a string or a file to hide, not both');
    return;
}

if (fileToHide) {
    stego.hideSecretFileinFile(fileToHide, file, { password, output });
}

if (string) {
    stego.hideSecretInFile(string, file, { password, output });
}

if (!string && !fileToHide) {
    stego.extractSecretFromFile(file, password);
}

// console.log(program.opts());