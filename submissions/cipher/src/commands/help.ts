import chalk from "chalk"
import os from "node:os"

export default function help() {
    // lowkey gotta fill this out innit
    console.log(helpMessage)
}

const helpMessage = chalk.gray(`What's up, ${os.userInfo().username}! I see that ` +
                `you've stumbled upon this little tool I've created. ` +
                `What does it do, exactly? \n\n Cipher`) + chalk.green(" encodes and decodes plain text ") + 
                chalk.gray(`based on a set of`) + chalk.green(` rules defined in nifty little JSON files`) +
                chalk.gray(` uncreatively called "ciphers". Right now, there are 2 options: `) + 
                chalk.green(`caesar `)+
                chalk.gray(`ciphers, which are simple transpositional ciphers that ` +
                `shift any given character by a given number; and`) + chalk.green(` substitution`) +
                chalk.gray(` ciphers, which replace characters and character combinations ` +
                `with others. Look in `) + chalk.green(`example.json`) + chalk.gray(` for an example of how they're `+
                `used! I'm working on more documentation at the moment. \n\n`);