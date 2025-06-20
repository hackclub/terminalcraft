import { rmSync } from 'fs'
import { TextInput } from '@inkjs/ui'
import { Box, Newline, render, useApp } from 'ink'
import Badge from '../../components/Badge'
import Card from '../../components/Card'
import Text from '../../components/Text'
import { DataDirectoryPath } from '../../constants'
import { sqlite } from '../../db'

export default function NukeConfirmation() {
    const { exit } = useApp()

    return (
        <Box flexDirection="column" gap={1}>
            <Card>
                <Text>Are you absolutely sure?</Text>
            </Card>
            <Box flexDirection="column" gap={1} paddingX={1}>
                <Text>
                    Type <Text color="danger">nuke confirm</Text> then press enter to continue. This will also exit the
                    app.
                </Text>
                <Text>
                    To go back, press <Badge>ESC</Badge>.
                </Text>
                <TextInput
                    suggestions={['nuke confirm']}
                    placeholder="Waiting for your confirmation..."
                    onSubmit={text => {
                        if (text === 'nuke confirm') {
                            sqlite.close()
                            rmSync(DataDirectoryPath, { recursive: true })
                            exit()
                            render(
                                <Text color="danger">
                                    <Newline /> Deleted all data. Exiting...
                                </Text>,
                            )
                        }
                    }}
                />
            </Box>
        </Box>
    )
}
