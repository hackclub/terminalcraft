import { DurationFormatter } from '@sapphire/duration'
import { desc, eq } from 'drizzle-orm'
import { Box } from 'ink'
import { useNavigate } from 'react-router'
import Card from '../../components/Card'
import SelectMenu from '../../components/SelectMenu'
import Text from '../../components/Text'
import { useUser } from '../../components/providers/UserProvider'
import { db } from '../../db'
import { sessions } from '../../db/schema'
import { useAsync } from '../../utils/react'

const fmt = new DurationFormatter()

export default function SessionsHistory() {
    const user = useUser()
    const navigate = useNavigate()
    const ss = useAsync(() =>
        db.query.sessions.findMany({ where: eq(sessions.userId, user.id!), orderBy: [desc(sessions.start)] }),
    )

    return (
        <Box flexDirection="column" gap={1}>
            <Card>
                <Text>History</Text>
            </Card>
            <SelectMenu
                items={[
                    ...(ss?.map(s => ({
                        label: `${s.name}${s.finished ? ' ✓' : ''}`,
                        key: s.id,
                        description: [
                            `Duration: ${fmt.format(s.duration * 1000)}`,
                            s.actualDuration && `Used duration: ${fmt.format(s.actualDuration * 1000)}`,
                            s.files && `Files changed: ${s.files.length}`,
                            `Tracked on: ${s.start.toLocaleString('en-US')}`,
                        ]
                            .filter(Boolean)
                            .join('\n'),
                    })) ?? [{ key: '*', label: 'Loading...' }]),
                    {
                        separatorTop: 'space',
                        key: 'b',
                        label: 'Back',
                        description: 'Go back to the main menu',
                    },
                ]}
                onSubmit={k => {
                    if (k === 'b') return navigate(-1)
                }}
            />
        </Box>
    )
}
