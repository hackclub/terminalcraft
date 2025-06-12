import { eq } from 'drizzle-orm'
import { Box } from 'ink'
import { useNavigate } from 'react-router'
import Card from '../../components/Card'
import SelectMenu from '../../components/SelectMenu'
import Text from '../../components/Text'
import { useUser } from '../../components/providers/UserProvider'
import { db } from '../../db'
import { goals } from '../../db/schema'
import { useAsync } from '../../utils/react'

export default function GoalsMenu() {
    const user = useUser()
    const navigate = useNavigate()
    const goalItems = useAsync(() =>
        db.query.goals
            .findMany({
                where: eq(goals.userId, user.id),
            })
            .then(goals =>
                goals.map(goal => ({
                    key: goal.id,
                    label: `${goal.name}${goal.finished ? ' ✓' : ''}`,
                    // TODO: add session name as description (if tied to one)
                })),
            ),
    )

    return (
        <Box flexDirection="column" gap={1}>
            <Card>
                <Text>Goals</Text>
            </Card>
            <SelectMenu
                items={[
                    { key: 'n', label: 'New goal', description: 'Create a new goal', separator: 'space' },
                    ...(goalItems ?? []),
                    { key: 'b', label: 'Back', description: 'Go back to the main menu', separatorTop: 'space' },
                ]}
                onSubmit={k => {
                    switch (k) {
                        case 'n':
                            return navigate('/goals/new')
                        case 'b':
                            return navigate(-1)

                        default: {
                            // TODO: navigate to goal management page
                            // return navigate(`/goals/${k}`)
                        }
                    }
                }}
            />
        </Box>
    )
}
