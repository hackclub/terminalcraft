export const ResetUnlocks = [
    {
        HackerTheme: [1 << 0, 499],
        MonochromeTheme: [1 << 1, 999],
        BadgeCool: [1 << 2, 999],
        BadgeStar: [1 << 3, 1499],
        BadgeError: [1 << 4, 1999],
        BadgeMeow: [1 << 5, 1999],
    },
    {},
    {},
    {},
    {},
    {},
    {},
    {},
    {},
    {
        // TODO: send a notification reminding the user to take a break
        BadgeInsaneProcrastinator: [1 << 0, 10000],
    },
] as const satisfies Readonly<
    Record<
        0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9,
        Record<string, [bit: number, price: number, onUnlock?: () => unknown]>
    >
>

export const MaxResets = ResetUnlocks.length - 1

if (MaxResets > 1 << 5) throw new Error('Database currently does not support this many resets')
