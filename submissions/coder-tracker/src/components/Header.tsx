import { Box, Static } from 'ink'

import Text from './Text'

import { and, eq } from 'drizzle-orm'
import pkg from '../../package.json'
import { db } from '../db'
import { notifications } from '../db/schema'
import { useAsync } from '../utils/react'
import Card from './Card'
import { useUser } from './providers/UserProvider'

export default function Header() {
    const user = useUser()
    const notifs = useAsync(() =>
        db.query.notifications.findMany({
            where: and(eq(notifications.read, false), eq(notifications.userId, user.id)),
        }),
    )

    return (
        <>
            <Card>
                <Text>
                    <Text color="brandPrimary">Coder</Text>
                    {'|>'}
                    <Text color="brandSecondary">Tracker</Text> <Text dimColor>v{pkg.version}</Text>
                </Text>
                <Text dimColor>Leveling up in your programming sessions, literally.</Text>
            </Card>
            {(notifs?.length || null) && (
                <Box key="notifications">
                    <Text color="brandPrimary">Notifications</Text>
                </Box>
            )}
        </>
    )
}
