import { existsSync, readFileSync } from 'fs'
import { MultiSelect, ProgressBar } from '@inkjs/ui'
import watcher from '@parcel/watcher'
import { DurationFormatter } from '@sapphire/duration'
import { eq, inArray } from 'drizzle-orm'
import { Box, Newline, useInput } from 'ink'
import parseGitignore from 'parse-gitignore'
import { useEffect, useRef, useState } from 'react'
import { Navigate, useNavigate } from 'react-router'
import Badge from '../../../components/Badge'
import SelectMenu from '../../../components/SelectMenu'
import Text from '../../../components/Text'
import { useUser } from '../../../components/providers/UserProvider'
import { MaxXpObtainable, MaxXpPerSession, XpGainAmounts } from '../../../constants/leveling'
import { DefaultProjectConfig } from '../../../constants/project'
import { db } from '../../../db'
import { type InferResultType, goals, sessions, users } from '../../../db/schema'
import { ProjConfig } from '../../../utils/project'
import { onCleanup, onMount, useAsync } from '../../../utils/react'

const fmt = new DurationFormatter()

export default function ActiveSession() {
    const [timeLeft, setTimeLeft] = useState<number | null>(null)
    const [focus, setFocus] = useState(0)
    const [completed, setCompleted] = useState(false)
    const user = useUser()
    const completedGoals = useRef<string[]>([])
    const navigate = useNavigate()
    const files: InferResultType<'sessions'>['files'] = {}

    const progress = useRef(0)
    const session = useAsync(
        async () =>
            user.activeSessionId &&
            (await db.query.sessions.findFirst({
                where: eq(sessions.id, user.activeSessionId!),
                with: { goals: true },
            })),
    )

    const ends = session && session.start.getTime() + session.duration * 1000

    useInput((_, key) => {
        if (key.tab) setFocus(f => (f + 1) % 2)
    })

    useEffect(() => {
        const update = () => {
            if (session) {
                const timeLeft = (ends as number) - Date.now()
                setTimeLeft(timeLeft)
                progress.current = (timeLeft / (session.duration * 1000)) * 100
            }
        }

        update()

        const interval = setInterval(update, 1000)
        return () => clearInterval(interval)
    }, [session, ends])

    useEffect(() => {
        if (session) {
            for (const goal of session.goals) {
                if (goal.finished) completedGoals.current.push(goal.id)
            }

            if (completedGoals.current.length === session.goals.length) setCompleted(true)
        }
    }, [session])

    useEffect(() => {
        let unsub: () => void

        const gitignoreFiles =
            (ProjConfig.track?.followGitIgnore ?? DefaultProjectConfig.track.followGitIgnore)
                ? existsSync('.gitignore')
                    ? parseGitignore(readFileSync('.gitignore'))
                    : []
                : []

        watcher
            .subscribe(
                process.cwd(),
                (err, evts) => {
                    if (err) console.error(err)

                    for (const evt of evts) {
                        const prv = files[evt.path] ?? [0, 0]
                        // TODO: diff tracking
                        if (evt.type === 'update') files[evt.path] = [prv[0] + 1, prv[1]]
                    }
                },
                {
                    ignore: [...(ProjConfig.track?.exclude ?? DefaultProjectConfig.track.exclude), ...gitignoreFiles],
                },
            )
            .then(sub => {
                unsub = sub.unsubscribe
            })

        return () => unsub?.()
    }, [])

    if (!user.activeSessionId) return <Navigate to="/" replace />

    if (session && timeLeft !== null && timeLeft <= 0) {
        quitSession(
            user.id,
            user.xp,
            session.duration,
            session.duration - timeLeft / 1000,
            completedGoals.current.length,
            0,
        ).then(() => user.refetch())

        return <Navigate to="/" replace />
    }

    return (
        session && (
            <Box flexDirection="column" gap={1}>
                <Box justifyContent="center" borderStyle="round" width="100%" paddingX={1} borderDimColor>
                    <Text wrap="wrap">{session.name}</Text>
                </Box>
                <Box flexDirection="column" width="100%" borderStyle="round" borderDimColor paddingX={1}>
                    <Text>{timeLeft ? fmt.format(timeLeft) : 'Loading...'}</Text>
                    <Text dimColor>Ends: {new Date(ends!).toLocaleString('en-US')}</Text>
                    <ProgressBar value={progress.current} />
                </Box>
                <Box paddingX={1}>
                    <Text dimColor>
                        Press <Badge>TAB</Badge> to switch focus between sections.
                        <Newline />
                        <Newline />
                        To complete a goal, select the goal and tap <Badge>SPACE</Badge> to mark it as complete.
                    </Text>
                </Box>
                <Box
                    flexDirection="column"
                    width="100%"
                    paddingX={1}
                    gap={1}
                    borderStyle="round"
                    borderDimColor={focus !== 0}
                >
                    <Text>Goals</Text>
                    <MultiSelect
                        isDisabled={focus !== 0}
                        defaultValue={session.goals.filter(goal => goal.finished).map(goal => goal.id)}
                        onChange={async completed => {
                            const oldGoals = new Set(completedGoals.current)
                            completedGoals.current = completed

                            await db.update(goals).set({ finished: true }).where(inArray(goals.id, completed))

                            const removed = oldGoals.difference(new Set(completed))
                            if (removed.size)
                                await db
                                    .update(goals)
                                    .set({ finished: false })
                                    .where(inArray(goals.id, [...removed]))

                            setCompleted(completed.length === session.goals.length)
                        }}
                        options={session.goals.map(goal => ({
                            label: goal.name,
                            value: goal.id,
                        }))}
                    />
                </Box>
                <Box flexDirection="column" width="100%" gap={1} borderStyle="round" borderDimColor={focus !== 1}>
                    <SelectMenu
                        focused={focus === 1}
                        items={[
                            completed
                                ? {
                                      key: 'e',
                                      label: 'End this session',
                                      description: 'You can complete this session early!',
                                  }
                                : {
                                      key: 'q',
                                      label: 'Quit session',
                                      description: 'Giving up already? (you will lose XP!)',
                                      danger: true,
                                  },
                            {
                                key: 'b',
                                label: 'Back',
                                description: 'Go back to the main menu',
                            },
                        ]}
                        onSubmit={async key => {
                            if (timeLeft === null) return

                            switch (key) {
                                case 'b':
                                    return navigate(-1)

                                case 'e': {
                                    await endSession(
                                        user.id,
                                        user.xp,
                                        user.activeSessionId!,
                                        session.duration,
                                        session.duration - timeLeft / 1000,
                                        completedGoals.current.length,
                                    )
                                    break
                                }

                                case 'q': {
                                    await quitSession(
                                        user.id,
                                        user.xp,
                                        session.duration,
                                        session.duration - timeLeft / 1000,
                                        completedGoals.current.length,
                                        session.goals.length - completedGoals.current.length,
                                    )
                                    break
                                }
                            }

                            await user.refetch()
                            // TODO: navigate to summary
                            return navigate('/', { replace: true })
                        }}
                    />
                </Box>
            </Box>
        )
    )
}

async function endSession(
    uid: string,
    uxp: number,
    sid: string,
    duration: number,
    actualDuration: number,
    goals: number,
) {
    const xpGain = Math.min(
        XpGainAmounts.SessionFinished +
            goals * XpGainAmounts.GoalFinished +
            duration * XpGainAmounts.SessionUsedPerMinute,
        MaxXpPerSession,
    )

    await db
        .update(users)
        .set({
            activeSessionId: null,
            xp: Math.min(uxp + xpGain, MaxXpObtainable),
        })
        .where(eq(users.id, uid))

    await db
        .update(sessions)
        .set({
            finished: true,
            actualDuration,
        })
        .where(eq(sessions.id, sid))
}

async function quitSession(
    uid: string,
    uxp: number,
    duration: number,
    durationUsed: number,
    goalsCompleted: number,
    goalsUncompleted: number,
) {
    const xpGain =
        XpGainAmounts.SessionCanceled +
        goalsCompleted * XpGainAmounts.GoalFinished +
        Math.round(durationUsed) * XpGainAmounts.SessionUsedPerMinute +
        goalsUncompleted * XpGainAmounts.GoalUnfinished

    await db.update(sessions).set({
        actualDuration: Math.min(duration, durationUsed),
    })

    await db
        .update(users)
        .set({
            activeSessionId: null,
            xp: Math.max(uxp + xpGain, 0),
        })
        .where(eq(users.id, uid))
}
