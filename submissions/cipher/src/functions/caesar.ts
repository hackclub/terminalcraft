/*
export async function CipherCaesar(input: string, shift: number, preserveCase: boolean = false): Promise<null | string> {
    try {
        const letterPattern: RegExp = /[a-zA-Z]/g
        const letterShift = ((shift % 26) + 26)  % 26

        const text = preserveCase? input : input.toLowerCase()

        const result = text.replace(letterPattern, char => {
            const base = char === char.toUpperCase() ? 65 : 97

            return String.fromCharCode(
                ((char.charCodeAt(0) - base + letterShift) % 26) + base
            )
        })
        console.log(result) //TODO: replace logging

        return result
    } catch (err) {
        console.error(err)
        return null
    }
}

export async function DecipherCaesar(input: string, shift: number) {
    //augh.
}
    */

import chalk from "chalk";
import {AlphabetList, Cipher, CipherConfiguration} from "../types"

export class CaesarCipher implements Cipher {
    private key: number = 0;
    private caseSensitive: boolean = false
    private alphabets: AlphabetList = []
    private moreVerbose: boolean = false

    constructor(config: CipherConfiguration, alphabets: AlphabetList) {
        if ("shift" in config.key){
            this.key = config.key.shift as number
        } else {
            const err = new Error(`Invalid configuration! "key.shift" not found in configuration for cipher type ${config.type}.`)
            console.error(err)
            throw err
        }
        this.caseSensitive = config.caseSensitive ? config.caseSensitive : false
        this.alphabets = alphabets
    }

    public setVerbosity(newValue: boolean): void {
        this.moreVerbose = newValue
    }

    private remapAlphabet(encrypt: boolean = true): {[key: string] : string} {
        const remappedCharacters: {[key: string]: string} = {};
        for (const alphabet of this.alphabets) {
            const offset = ((encrypt ? this.key : -this.key) % alphabet.length + alphabet.length) % alphabet.length;
            const transformedAlphabet = alphabet.slice(offset).concat(alphabet.slice(0, offset));
            for (let character = 0; character < alphabet.length; character++) {
                remappedCharacters[alphabet[character]] = transformedAlphabet[character]
            }
        }
        return remappedCharacters
    }

    public encode(data: string) {
        const alphabet = this.remapAlphabet(true)
        const cleanedData = this.caseSensitive? data : data.toLowerCase()
        let result: string = ""
        for (const char of cleanedData) {
            if (alphabet[char]) {
                if (this.moreVerbose) {
                    console.log(chalk.gray(`Shifted `) + chalk.blue(char) + chalk.gray(` to `) + chalk.green(alphabet[char]) )
                }
                result += alphabet[char]
            } else {
                if (this.moreVerbose) {
                    console.log(chalk.gray(`Character `) + chalk.red(char) + chalk.gray(` not found in alphabet.`))
                }
                result += char
            }
        }

        return result
    }

    public decode(data: string) {
        const alphabet = this.remapAlphabet(false)
        const cleanedData = this.caseSensitive? data : data.toLowerCase()
        let result: string = ""
        for (const char of cleanedData) {
            if (alphabet[char]) {
                result += alphabet[char]
            } else {
                result += char
            }
        }

        return result
    }
}