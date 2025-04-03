import { Text, useInput } from 'ink'
import Gradient from 'ink-gradient'
import Card from './Card'
import { useTheme } from './providers/ThemeProvider'

export default function Button({
    children,
    onSubmit,
    focused,
}: {
    children: string
    onSubmit: () => void
    focused?: boolean
}) {
    const theme = useTheme()
    useInput(
        (_, key) => {
            if (focused && key.return) onSubmit()
        },
        { isActive: focused },
    )

    return (
        <Card borderColor="primary" borderDimColor={false}>
            <Gradient colors={focused ? [theme.primary, theme.secondary] : [theme.neutral, theme.neutral]}>
                <Text underline={focused}>{children}</Text>
            </Gradient>
        </Card>
    )
}
