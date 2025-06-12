import { eq } from 'drizzle-orm'
import { useApp } from 'ink'
import { useCallback } from 'react'
import { useNavigate } from 'react-router'
import { db } from '../../db'
import { sessions } from '../../db/schema'
import { useAsync } from '../../utils/react'
import SelectMenu, { type SelectMenuProps } from '../SelectMenu'
import { useUser } from '../providers/UserProvider'

export default function MainSelectMenu() {
    const user = useUser()
    const { exit } = useApp()
    const navigate = useNavigate()

    const activeSession = useAsync(() =>
        user.activeSessionId
            ? db.query.sessions.findFirst({ where: eq(sessions.id, user.activeSessionId) })
            : Promise.resolve(null),
    )

    const SelectOptions = [
        user.activeSessionId
            ? {
                  key: 'c',
                  label: `Continue session: ${activeSession?.name ?? '...'}`,
                  description: activeSession
                      ? `Ends: ${new Date(activeSession.start.getTime() + activeSession.duration * 1000).toLocaleString('en-US')}`
                      : '...',
                  separator: 'space',
              }
            : { key: 'n', label: 'New session', description: 'Start and track a new session' },
        { key: 'g', label: 'Goals', description: 'View and create goals to complete in your sessions' },
        { key: 'h', label: 'History', description: 'See your performance for previous sessions', separator: 'space' },
        { key: 's', label: 'Shop', description: '(COMING SOON) Buy cosmetics & more!', separator: 'space' },
        { key: '?', label: 'How to use?', description: 'Documentation? where?' },
        { key: ',', label: 'Settings', description: 'Configure stuff' },
        {
            key: 'q',
            label: 'Quit',
            danger: true,
            description: "It's better than CTRL+C :D",
        },
    ] as const satisfies SelectMenuProps['items']

    const SelectKeyToUrl: { [K in (typeof SelectOptions)[number]['key']]?: string } = {
        n: '/sessions/new',
        c: '/sessions/@active',
        g: '/goals',
        h: '/sessions/history',
        s: '/shop',
        ',': '/settings',
        '?': '/usage',
    }

    const handleSubmit = useCallback(
        (key: (typeof SelectOptions)[number]['key']) => {
            if (key in SelectKeyToUrl) return navigate(SelectKeyToUrl[key]!)
            if (key === 'q') return exit()

            throw new Error(`Unhandled key: ${key}`)
        },
        [navigate, exit],
    )

    return <SelectMenu onSubmit={handleSubmit} items={SelectOptions} />
}
