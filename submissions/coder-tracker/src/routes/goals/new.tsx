import { Alert, TextInput } from '@inkjs/ui'
import { Duration } from '@sapphire/duration'
import { Box, useInput } from 'ink'
import { useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import Button from '../../components/Button'
import Card from '../../components/Card'
import Text from '../../components/Text'
import { useUser } from '../../components/providers/UserProvider'
import { MinimumSessionDuration } from '../../constants/leveling'
import { db } from '../../db'
import { goals } from '../../db/schema'

export default function NewGoal() {
    const user = useUser()
    const navigate = useNavigate()
    const [focus, setFocus] = useState(0)
    const [error, setError] = useState('')
    const goalName = useRef('')

    useInput((_, key) => {
        if (key.upArrow) setFocus(f => (f - 1) % 3)
        if (key.downArrow || key.tab) setFocus(f => (f + 1) % 3)
    })

    return (
        <Box flexDirection="column" gap={1}>
            <Card>
                <Text>New goal</Text>
            </Card>
            {error && <Alert variant="error">{error}</Alert>}
            <Box flexDirection="column" gap={1} paddingX={1}>
                <Text>Goal: </Text>
                <TextInput
                    isDisabled={focus !== 0}
                    placeholder="What's your goal?"
                    onChange={text => {
                        goalName.current = text
                    }}
                />
            </Box>
            <Box gap={1}>
                <Button
                    focused={focus === 1}
                    onSubmit={() => {
                        createGoal(goalName.current, user.id)
                            .then(() => navigate(-1))
                            .catch(e => setError(String(e)))
                    }}
                >
                    Create
                </Button>
                <Button focused={focus === 2} onSubmit={() => navigate(-1)}>
                    Back
                </Button>
            </Box>
        </Box>
    )
}

async function createGoal(name: string, uid: string) {
    if (!name.length) throw 'All fields are required!'

    await db.insert(goals).values({
        id: Bun.randomUUIDv7('base64url'),
        name: name,
        userId: uid,
    })
}
