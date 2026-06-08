import chalk from "chalk";
import {
    checkbox,
    editor,
    input,
    select,
    confirm
} from "@inquirer/prompts";
import fileSelector from "inquirer-file-selector"
import fs from "fs/promises"
import addslashes from "./dev-utils/add-slashes"
import help from "./commands/help"
import {
    GetCipherConfigs,
    ListCipherFiles
} from "./dev-utils/config-loader";
import {
    Cipher
} from "./types";
import {
    file
} from "googleapis/build/src/apis/file";
import path from "node:path"

console.log("hello world!");


function printIntroText() {
    console.clear()
    console.log(chalk.green(" ______     __     ______   __  __     ______     ______    "));
    console.log(chalk.green("/\\  ___\\   /\\ \\   /\\  == \\ /\\ \\_\\ \\   /\\  ___\\   /\\  == \\   "));
    console.log(chalk.green("\\ \\ \\____  \\ \\ \\  \\ \\  _-/ \\ \\  __ \\  \\ \\  __\\   \\ \\  __<   "));
    console.log(chalk.green(" \\ \\_____\\  \\ \\_\\  \\ \\_\\    \\ \\_\\ \\_\\  \\ \\_____\\  \\ \\_\\ \\_\\ "));
    console.log(chalk.green("  \\/_____/   \\/_/   \\/_/     \\/_/\\/_/   \\/_____/   \\/_/ /_/ "))
}

async function startInteractiveMode() {
    const command = await select({
        message: "pick something to do!",
        choices: [{
                name: "help me!!",
                value: "help",
                description: "don't know what to do?"
            },

            {
                name: "encode some text .w.",
                value: "encode",
                description: "take some readable text and make it unreadable!"
            },
            {
                name: "decode some text *m*",
                value: "decode",
                description: "make some unreadable text and make it readable!"
            },
            {
                name: "exit :(",
                value: "exit",
                description: "exit this earth's atomosphere"
            }
        ]
    })

    switch (command) {
        case "help":
            help();
            startInteractiveMode();
            break;
        case "exit":
            exit();
            break;
        case "list":
            await ListCipherFiles();
            startInteractiveMode();
            break;
        case "encode":
            await encode();
            break;
        case "decode":
            await decode();
            break;
        default:
            console.log(chalk.red("command not found! run " + chalk.blue("help") + chalk.red(" to find a list of available commands.")))
    }
}

function exit() {
    console.log(chalk.green("thanks for using this tool!"))
    process.exit(0)
}

function biofuel() {
    console.log(chalk.redBright("err: in_progress"))
}

async function encode() {
    const cipher_files: Array < string > = await ListCipherFiles()
    const cipher_selection: string = await select({
        message: "pick a cipher file to use!",
        choices: cipher_files.map(cipherFile => {
            return {
                value: cipherFile
            }
        })
    })

    const ciphers: Array < Cipher > | undefined = await GetCipherConfigs(cipher_selection)
    if (!ciphers) {
        console.log(chalk.red("cipher file seems to be empty... maybe try editing it?"))
        startInteractiveMode()
    }

    const options = await checkbox({
        message: "select some optional things!",
        choices: [{
                value: "verbose",
                description: "show how each cipher transforms the text"
            },
            {
                name: "more verbose",
                value: "moreVerbose",
                description: "shows how each cipher transforms each character."
            }
        ]
    })


    const text_input_option = await select({
        message: "where do you want to get the text to cipher?",
        choices: [{
                value: "file",
                name: "from a file",
                description: "any plaintext-style file (.txt, .md, etc) should work!"
            },
            {
                value: "input",
                name: "i'll input it here",
                description: "this will open up your default text editor."
            }
        ]
    })

    let text: string = ""

    if (text_input_option == "file") {
        const filePath = await fileSelector({
            message: "select your file:"
        })
        text = await fs.readFile(filePath, "utf8")
    } else {
        if (process.env.EDITOR == "vi" || process.env.EDITOR == "vim") {
            console.log(chalk.redBright("imagine using vim. i pity you"))
            await new Promise((resolve) => setTimeout(resolve, 500))
        }
        text = await editor({
            message: "enter the text to be ciphered!"
        })
    }

    const saveToOutputFile: boolean = await confirm({message: "would you like to save this to an output file?"})
    let outputFileName: string = "";
    let outputFileDir: string = "";
    if (saveToOutputFile) {
        outputFileName = await input({
            message: "please specify a file name:"
        })
        outputFileDir = await fileSelector({
            message: "where should it be saved to?",
            type: "directory",
            filter: (file) => file.isDirectory()
        })
    }

    const moreVerbose = (options.indexOf("moreVerbose") != -1) ? true : false;
    const verbose = (options.indexOf("verbose") != -1) ? true : false;

    ciphers?.forEach(cipher => {
        cipher.setVerbosity(moreVerbose)
        text = cipher.encode(text)
        if (verbose && (ciphers.indexOf(cipher) + 1) < ciphers.length) {
            console.log(chalk.green(`result after pass ${ciphers.indexOf(cipher) + 1}: \n`) + text)
        }
    })
    console.log(chalk.green(`final result:\n`) + text)

    if (saveToOutputFile) {
        const outputFilePath = path.join(outputFileDir + "/" + outputFileName + ".txt")
        await fs.writeFile(outputFilePath, text)
        console.log(`file written to ${outputFilePath}`)
    }
}

async function decode() {
    const cipher_files: Array < string > = await ListCipherFiles()
    const cipher_selection: string = await select({
        message: "pick a cipher file to use!",
        choices: cipher_files.map(cipherFile => {
            return {
                value: cipherFile
            }
        })
    })

    const ciphers: Array < Cipher > | undefined = await GetCipherConfigs(cipher_selection)
    if (!ciphers) {
        console.log(chalk.red("cipher file seems to be empty... maybe try editing it?"))
        startInteractiveMode()
    }

    const options = await checkbox({
        message: "select some optional things!",
        choices: [{
                value: "verbose",
                description: "show how each cipher transforms the text"
            },
            {
                name: "more verbose",
                value: "moreVerbose",
                description: "shows how each cipher transforms each character."
            }
        ]
    })


    const text_input_option = await select({
        message: "where do you want to get the text to decipher?",
        choices: [{
                value: "file",
                name: "from a file",
                description: "any plaintext-style file (.txt, .md, etc) should work!"
            },
            {
                value: "input",
                name: "i'll input it here",
                description: "this will open up your default text editor."
            }
        ]
    })

    let text: string = ""

    if (text_input_option == "file") {
        const filePath = await fileSelector({
            message: "select your file:"
        })
        text = await fs.readFile(filePath, "utf8")
    } else {
        if (process.env.EDITOR == "vi" || process.env.EDITOR == "vim") {
            console.log(chalk.redBright("imagine using vim. i pity you"))
            await new Promise((resolve) => setTimeout(resolve, 500))
        }
        text = await editor({
            message: "enter the text to be deciphered!"
        })
    }

    const saveToOutputFile: boolean = await confirm({message: "would you like to save this to an output file?"})
    let outputFileName: string = "";
    let outputFileDir: string = "";
    if (saveToOutputFile) {
        outputFileName = await input({
            message: "please specify a file name:"
        })
        outputFileDir = await fileSelector({
            message: "where should it be saved to?",
            type: "directory",
            filter: (file) => file.isDirectory()
        })
    }

    const moreVerbose = (options.indexOf("moreVerbose") != -1) ? true : false;
    const verbose = (options.indexOf("verbose") != -1) ? true : false;


    ciphers?.reverse().forEach(cipher => {
        cipher.setVerbosity(moreVerbose)
        text = cipher.decode(text)
        if (verbose && (ciphers.indexOf(cipher) + 1) < ciphers.length) {
            console.log(chalk.green(`result after pass ${ciphers.indexOf(cipher) + 1}: \n`) + text)
        }
    })
    console.log(chalk.green(`final result:\n`) + text)

    if (saveToOutputFile) {
        const outputFilePath = path.join(outputFileDir + "/" + outputFileName + ".txt")
        await fs.writeFile(outputFilePath, text)
        console.log(`file written to ${outputFilePath}`)
    }
}

printIntroText()
startInteractiveMode()