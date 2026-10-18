import chalk from "chalk"
import { Cipher, CipherConfiguration } from "../types"

export class SubstitutionCipher implements Cipher {
    private key: {[key: string] : string} = {}
    private caseSensitive: boolean = false
    private moreVerbose: boolean = false

    constructor(config: CipherConfiguration) {
        this.key = config.key
        this.caseSensitive = config.caseSensitive? config.caseSensitive : false
    }

    public setVerbosity(newValue: boolean) {
        this.moreVerbose = newValue
    }

    public encode(data: string) {
        let i: number = 0;
        let result: string = ""
        const keys = Object.keys(this.key).sort((a,b) => b.length - a.length)
        const dataArray = (this.caseSensitive? data : data.toLowerCase()).split("")
        while (i < dataArray.length) {
            let matched = false;

            for (const char of keys) {
                if (dataArray.slice(i, i+char.length).join("") === char) {
                    if (this.moreVerbose) {
                        console.log(chalk.gray(`Replaced character(s) `) + chalk.blue(`"${dataArray.slice(i, i+char.length).join("")}"`) + chalk.gray(` with `) + chalk.green(`"${char}"`))
                    }
                    result += this.key[char];
                    i += char.length;
                    matched = true;
                    break;
                }
            }
            
            if (!matched) {
                if (this.moreVerbose) {
                    console.log(chalk.gray("Character ") + chalk.red(dataArray[i]) + chalk.gray(" not found in table."))
                }
                result += dataArray[i]
                i += 1
            }
        }

        return result
    }

    private swapKeys(object: { [key: string] : string}) {
        let result: {[key: string] : string} = {}
        for (const key in object) {
            result[object[key]] =  key
        }
        return result
    }

    public decode(data: string) {
        let i: number = 0;
        let result: string = ""
        const swappedKeys = this.swapKeys(this.key)
        const keys = Object.keys(swappedKeys).sort((a,b) => b.length - a.length)
        const dataArray = (this.caseSensitive? data : data.toLowerCase()).split("")
        while (i < dataArray.length) {
            let matched = false;

            for (const char of keys) {
                if (dataArray.slice(i, i+char.length).join("") === char) {
                    if (this.moreVerbose) {
                        console.log(chalk.gray(`Replaced character(s) `) + chalk.blue(`"${dataArray.slice(i, i+char.length).join("")}"`) + chalk.gray(` with `) + chalk.green(`"${char}"`))
                    }
                    result += swappedKeys[char];
                    i += char.length;
                    matched = true;
                    break;
                }
            }
            
            if (!matched) {
                if (this.moreVerbose) {
                    console.log(chalk.gray("Character ") + chalk.red(dataArray[i]) + chalk.gray(" not found in table."))
                }
                result += dataArray[i]
                i += 1
            }
        }

        return result
    }
}