import { Box, Newline } from 'ink'
import Badge from '../../components/Badge'
import Card from '../../components/Card'
import Text from '../../components/Text'

export default function ProjectSettings() {
    return (
        <Box flexDirection="column" gap={1}>
            <Card>
                <Text>Project settings</Text>
            </Card>
            <Box paddingX={1} flexDirection="column">
                <Text>
                    For now, project settings can be edited in:
                    <Newline />
                    <Badge>(project dir)/.cdrtkr/proj.json</Badge>
                </Text>
                <Newline />
                <Text dimColor>Make sure to restart the app after editing the file.</Text>
            </Box>
        </Box>
    )
}
