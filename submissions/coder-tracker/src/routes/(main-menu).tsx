import { Box } from 'ink'

import Header from '../components/Header'
import UserInfo from '../components/UserInfo'
import MainSelectMenu from '../components/menus/MainSelectMenu'

export default function MainMenu() {
    return (
        <Box gap={1} flexDirection="column">
            <Header />
            <UserInfo />
            <MainSelectMenu />
        </Box>
    )
}
