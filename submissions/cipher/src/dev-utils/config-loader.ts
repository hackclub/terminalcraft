import path from "node:path"
import fs from "node:fs/promises"
import chalk from "chalk"

import { AlphabetList, Cipher, CipherConfiguration } from "../types"
import { CaesarCipher } from "../functions/caesar"
import { SubstitutionCipher } from "../functions/substitution"

export async function ListCipherFiles() {
    const files = await fs.readdir(path.join(__dirname, "../../config/ciphers/"));

    let result: Array<string> = []

    files.forEach(file => {
        if (file.includes(".json")) {
            result.push(file.split(".")[0])
        }
    })
    return result
}

export async function GetCipherConfigs(name: string) {
    const filePath = path.join(__dirname, "../../config/ciphers/" + name + ".json")
    console.log(chalk.gray(`Reading cipher from ${filePath}.`))
    /*
    const fileExists: boolean = await fs.access(filePath).then(() => true).catch(() => false)
    
    if (!fileExists) {
        console.log(chalk.red(`Cipher ${name} not found!!! Are you sure you have the right name?`))
        return null
    }
*/
    const config: {ciphers: Array<CipherConfiguration>, alphabets: Array<string>} = JSON.parse(await fs.readFile(filePath, "utf8"))
    
    let alphabets: AlphabetList = []

    if (!config.alphabets) {
        //console.log(chalk.red(`Cipher ${name} seems to not contain any alphabets...`))
        return;
    }

    for (const alphabet of config.alphabets) {
        const charsetFilePath = path.join(__dirname, "../../config/charsets/" + alphabet + ".json")
        await fs.readFile(charsetFilePath, "utf8")
            .then((result) => alphabets.push(JSON.parse(result)))
            .catch(() => {console.error(`Alphabet ${alphabet} not found!!! Did you spell it correctly?`); return;})
    }

    let ciphers: Array<Cipher> = []
    //temp code for debugging? idk
    config.ciphers.forEach(configuration => {
        switch (configuration.type) {
            case "caesar":
                ciphers.push(new CaesarCipher(configuration, alphabets))
                break;
            case "substitution":
                ciphers.push(new SubstitutionCipher(configuration))
                break;
            default:
                throw new Error(`No cipher type ${configuration.type} found. Did you misspell something?`)
        }
    });

    return ciphers
}