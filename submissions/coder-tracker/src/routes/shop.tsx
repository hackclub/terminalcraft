import { Box } from 'ink'
import Badge from '../components/Badge'
import Card from '../components/Card'
import Text from '../components/Text'

export default function Shop() {
    return (
        <Box flexDirection="column" gap={1}>
            <Card>
                <Text>Shop</Text>
            </Card>
            <Box paddingX={1} flexDirection="column">
                <Text>Coming soon!</Text>
                <Text>
                    Press <Badge>ESC</Badge> to go back.
                </Text>
            </Box>
        </Box>
    )
}
