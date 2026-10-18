export interface CipherConfiguration {
    type: string,
    key: {},
    caseSensitive?: boolean,
    moreVerbose: boolean
}

export interface CaesarCipherConfiguration extends CipherConfiguration {
    key: {
        shift: number
    }
}

export type AlphabetList = Array<Array<string>>

export interface Cipher {
    encode(data: string): string
    decode(data: string): string
    setVerbosity(newValue: boolean): void
}