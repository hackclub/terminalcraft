import { ProgressBar } from '@inkjs/ui'
import { Box } from 'ink'
import Gradient from 'ink-gradient'
import { LevelNames } from '../constants/leveling'
import { getLevel, getLevelProgress, getTotalXpRequirementForLevel, getXpRequirementForLevel } from '../utils/leveling'
import Badge from './Badge'
import Card from './Card'
import Text from './Text'
import { useTheme } from './providers/ThemeProvider'
import { useUser } from './providers/UserProvider'

export default function UserInfo() {
    const user = useUser()
    const theme = useTheme()
    const lvl = getLevel(user.xp)

    return (
        <Box flexDirection="column" alignSelf="flex-start">
            <Card>
                <Text>
                    Hello, <Gradient colors={[theme.primary, theme.secondary]}>{user.id}</Gradient>!{' '}
                    <Badge>
                        LVL {lvl} - {LevelNames[lvl]}
                    </Badge>
                </Text>
                <UserLevelDisplay />
            </Card>
        </Box>
    )
}

function UserLevelDisplay() {
    const user = useUser()

    const lvl = getLevel(user.xp)
    const levelReq = getTotalXpRequirementForLevel(lvl)
    const nextLevelReq = getXpRequirementForLevel(lvl + 1)
    const prog = getLevelProgress(user.xp) * 100

    return (
        <Box flexDirection="column">
            <Box flexDirection="row" minWidth={40}>
                <ProgressBar value={prog} />
                <Text>
                    <Text>
                        {' '}
                        ({user.xp - levelReq}/{nextLevelReq} XP)
                    </Text>
                </Text>
            </Box>
            <Text dimColor>
                Next:{' '}
                <Badge>
                    LVL {lvl + 1} - {LevelNames[lvl + 1]}
                </Badge>
            </Text>
        </Box>
    )
}
