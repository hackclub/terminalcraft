import { useInput } from 'ink'
import { MemoryRouter, Route, Routes, useNavigate } from 'react-router'
import PlaceholderPage from './components/pages/PlaceholderPage'
import ThemeProvider from './components/providers/ThemeProvider'
import UserProvider from './components/providers/UserProvider'
import MainMenu from './routes/(main-menu)'
import GoalsMenu from './routes/goals/(menu)'
import NewGoal from './routes/goals/new'
import ActiveSession from './routes/sessions/@active/(page)'
import SessionsHistory from './routes/sessions/history'
import NewSession from './routes/sessions/new'
import Settings from './routes/settings/(menu)'
import NukeConfirmation from './routes/settings/nuke'
import ProjectSettings from './routes/settings/project'
import Shop from './routes/shop'
import { onMount } from './utils/react'

export default function App() {
    onMount(() => {
        process.title = 'Coder Tracker'
    })

    return (
        <UserProvider>
            <ThemeProvider>
                <MemoryRouter>
                    <AppRoutes />
                </MemoryRouter>
            </ThemeProvider>
        </UserProvider>
    )
}

function AppRoutes() {
    const navigate = useNavigate()

    useInput((_, key) => {
        if (key.escape) navigate(-1)
    })

    return (
        <Routes>
            <Route path="/" Component={MainMenu} />

            <Route path="/sessions/new" Component={NewSession} />
            <Route path="/sessions/@active" Component={ActiveSession} />
            <Route path="/sessions/history" Component={SessionsHistory} />

            <Route path="/goals" Component={GoalsMenu} />
            <Route path="/goals/new" Component={NewGoal} />
            <Route path="/goals/:goal" Component={PlaceholderPage} />

            <Route path="/shop" Component={Shop} />

            {/* TODO */}
            <Route path="/usage" Component={PlaceholderPage} />

            <Route path="/settings" Component={Settings} />
            <Route path="/settings/project" Component={ProjectSettings} />
            <Route path="/settings/nuke" Component={NukeConfirmation} />

            <Route path="*" Component={PlaceholderPage} />
        </Routes>
    )
}
