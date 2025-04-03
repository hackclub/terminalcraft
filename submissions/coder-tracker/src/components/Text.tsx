import { type TextProps, Text as _Text } from 'ink'
import { type Theme, useTheme } from './providers/ThemeProvider'

export default function Text({ color, children, ...props }: Omit<TextProps, 'color'> & { color?: keyof Theme }) {
    const theme = useTheme()

    return (
        <_Text {...props} color={color ? theme[color] : theme.neutral}>
            {children}
        </_Text>
    )
}
