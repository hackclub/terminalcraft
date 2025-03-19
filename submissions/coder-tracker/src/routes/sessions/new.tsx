import { Alert, MultiSelect, TextInput } from '@inkjs/ui'
import { Duration } from '@sapphire/duration'
import { and, eq, inArray } from 'drizzle-orm'
import { Box, Newline, useInput } from 'ink'
import { useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import Button from '../../components/Button'
import Card from '../../components/Card'
import Text from '../../components/Text'
import { useUser } from '../../components/providers/UserProvider'
import { MinimumSessionDuration } from '../../constants/leveling'
import { db } from '../../db'
import { goals, sessions, users } from '../../db/schema'
import { useAsync } from '../../utils/react'

export default function NewSession() {
    const user = useUser()
    const navigate = useNavigate()

    const unfinishedGoals = useAsync(() =>
        db.query.goals.findMany({ where: and(eq(goals.userId, user.id), eq(goals.finished, false)) }),
    )

    const [focus, setFocus] = useState(0)
    const [error, setError] = useState('')

    const summary = useRef('')
    const desc = useRef('')
    const goalIds = useRef<string[]>([])

    useInput((_, key) => {
        if (key.upArrow) setFocus(f => (f - 1) % 5)
        if (key.downArrow || key.tab) setFocus(f => (f + 1) % 5)
    })

    return (
        <Box flexDirection="column" gap={1}>
            <Card>
                <Text>New session</Text>
            </Card>
            {error && <Alert variant="error">{error}</Alert>}
            {unfinishedGoals?.length === 0 ? (
                <Alert variant="warning">
                    You have no goals to select! Create some first.
                    <Newline />
                    Completed goals cannot be selected.
                </Alert>
            ) : null}
            <Box flexDirection="column" gap={1} paddingX={1}>
                <Text>Summary: </Text>
                <TextInput
                    isDisabled={focus !== 0}
                    placeholder="What are you doing in this session?"
                    onChange={text => {
                        summary.current = text
                    }}
                />
            </Box>
            <Box flexDirection="column" gap={1} paddingX={1}>
                <Text>Duration: </Text>
                <TextInput
                    isDisabled={focus !== 1}
                    placeholder="How long will this session be? (eg. 1h30m)"
                    onChange={text => {
                        desc.current = text
                    }}
                />
            </Box>
            <Box flexDirection="column" gap={1} paddingX={1}>
                <Text>Goals to complete (space to select): </Text>
                <MultiSelect
                    options={
                        unfinishedGoals?.length
                            ? unfinishedGoals.map(goal => ({ label: goal.name, value: goal.id }))
                            : [
                                  {
                                      label: '...',
                                      value: '*',
                                  },
                              ]
                    }
                    isDisabled={unfinishedGoals?.length ? focus !== 2 : true}
                    onChange={i => {
                        goalIds.current = i
                    }}
                />
            </Box>
            <Box gap={1}>
                <Button
                    focused={focus === 3}
                    onSubmit={async () => {
                        try {
                            await createSessionAndSetAsActive(summary.current, desc.current, goalIds.current, user.id)
                            await user.refetch()
                            navigate('/sessions/@active', { replace: true })
                        } catch (e) {
                            setError(String(e))
                        }
                    }}
                >
                    Start
                </Button>
                <Button focused={focus === 4} onSubmit={() => navigate(-1)}>
                    Back
                </Button>
            </Box>
        </Box>
    )
}

async function createSessionAndSetAsActive(summary: string, duration: string, goalIds: string[], uid: string) {
    if (!summary.length || !duration.length || !goalIds.length) throw 'All fields are required!'
    const actualDuration = new Duration(duration).offset
    if (!actualDuration) throw 'Invalid duration! Duration usually looks like 1h30m, 1h, 1 hour 30 minutes, etc.'
    if (actualDuration < MinimumSessionDuration) throw 'Session duration must be at least 10 minutes!'

    const sid = Bun.randomUUIDv7('base64url')

    await db.insert(sessions).values({
        id: sid,
        name: summary,
        duration: actualDuration / 1000,
        userId: uid,
    })

    await db.update(goals).set({ sessionId: sid }).where(inArray(goals.id, goalIds))

    await db
        .update(users)
        .set({
            activeSessionId: sid,
        })
        .where(eq(users.id, uid))
}
