export const CoolBadge = ['COOL', 'blue', 'white'] satisfies BadgeConfig
export const StarBadge = ['⭐', 'white', 'yellow'] satisfies BadgeConfig
export const ErrorBadge = ['🚫 ERROR', 'red', 'white'] satisfies BadgeConfig
export const MeowBadge = ['😺 MEOW', 'white', 'black'] satisfies BadgeConfig
export const InsaneProcrastinatorBadge = ['INSANE PROCRASTINATOR', 'red', 'white'] satisfies BadgeConfig

type BadgeConfig = [text: string, bgColor: string, textColor: string]

export const BadgeByUnlockBit = [
    // biome-ignore lint/suspicious/noSparseArray: It's okay
    [, , StarBadge, CoolBadge],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [InsaneProcrastinatorBadge],
] as const
