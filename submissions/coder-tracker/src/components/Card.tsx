import { Box } from 'ink'
import type { ReactNode } from 'react'
import { type Theme, useTheme } from './providers/ThemeProvider'

export default function Card({
    children,
    borderColor,
    borderDimColor,
}: { children: ReactNode; borderColor?: keyof Theme; borderDimColor?: boolean }) {
    const theme = useTheme()

    return (
        <Box
            flexDirection="column"
            alignSelf="flex-start"
            gap={1}
            paddingX={1}
            borderStyle="round"
            borderDimColor={borderDimColor ?? true}
            borderColor={theme[borderColor ?? 'neutral']}
        >
            {children}
        </Box>
    )
}
