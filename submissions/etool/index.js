#!/usr/bin/env node
const { program } = require("commander")
const crypto = require('crypto')
const fs =require ('fs')
const path = require ('path');
const { buffer } = require("stream/consumers");

if (process.argv.includes("-h") || process.argv.includes("--help")) {
    console.log(`
        Usage:
          -e, --encrypt <text>   Encrypt the given text
          -d, --decrypt <text>   Decrypt the given text
          -p, --password <pass>  Set the encryption password
          -n, --folder-encrypt <path>  Encrypt all files in a folder
          -f, --folder-decrypt <path>  Decrypt all files in a folder
        `);
    process.exit(0);
}

program
    .option('-e, --encrypt [encrypt]')
    .option('-p, --password [password]')
    .option('-d, --decrypt [decrypt]')
    .option("-n, --folder-encrypt <folderEncrypt>") 
    .option("-f, --folder-decrypt <folderDecrypt>")
program.parse()

const options = program.opts();
const password = options.password
const encrypt = options.encrypt
const decrypt = options.decrypt
const folderEncrypt = options.folderEncrypt
const folderDecrypt = options.folderDecrypt

const key = crypto.pbkdf2Sync(password, 'salt', 1, 256/8, 'sha512')
const iv = crypto.createHash('sha256').update(password).digest('hex').slice(0, 16)

if (encrypt) {
    const cipher = crypto.createCipheriv('aes-256-cbc', key, iv) 
    let encrypted = cipher.update(encrypt, 'utf8', 'hex') + cipher.final('hex')
    console.log(encrypted);
}

if (decrypt) {
    try {
        const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv)
        let decrypted = decipher.update(decrypt, 'hex', 'utf8') + decipher.final('utf8')
        console.log(decrypted)
    } catch (error) {
        if (error.message.includes('bad decrypt')) {
            return console.error('Invalid password')
        } else {
            return console.error(error)
        }
    }
}

if (folderEncrypt) {
    const key = crypto.pbkdf2Sync(password, 'salt', 1, 256/8, 'sha512')
    fs.readdirSync(folderEncrypt).forEach(file => {
        const filepath = path.join(folderEncrypt, file)
        if (fs.statSync(filepath).isFile() && !file.endsWith('.enc')) {
            const data = fs.readFileSync(filepath)
            const cipher = crypto.createCipheriv('aes-256-cbc', key, iv)
            const encrypted = Buffer.concat([cipher.update(data), cipher.final()])
            fs.writeFileSync(filepath + '.enc', encrypted)
            fs.unlinkSync(filepath)
        }
    })
    console.log('Folder encrypted successfully.');
}

if (folderDecrypt) {
    const key = crypto.pbkdf2Sync(password, 'salt', 1, 256/8, 'sha512')
    fs.readdirSync(folderDecrypt).forEach(file => {
        if (file.endsWith('.enc')) {
            const filepath = path.join(folderDecrypt, file)
            const data = fs.readFileSync(filepath)
            try {
                const iv = crypto.createHash('sha256').update(password).digest('hex').slice(0, 16);
                const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv)
                const decrypted = Buffer.concat([decipher.update(data), decipher.final()])
                fs.writeFileSync(filepath.replace('.enc', ''), decrypted)
                fs.unlinkSync(filepath)
            } catch (error) {
                return console.error(`Failed to decrypt ${file}. Possible incorrect password.`);
            }
            console.log('Folder decrypted successfully.')
        }
    })
}