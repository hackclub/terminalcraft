import { Box, Text } from 'ink'
import { useNavigate } from 'react-router'
import Card from '../../components/Card'
import SelectMenu, { type SelectMenuProps } from '../../components/SelectMenu'

const SelectOptions = [
    // { key: 't', label: 'Theme', description: 'Change the theme of the app' },
    { key: 'p', label: 'Project settings', description: '(COMING SOON) Edit project settings' },
    {
        key: 'n',
        label: 'Nuke!',
        description: 'Nuke everything... You will lose all progress, this is NOT prestiging!',
        danger: true,
        separatorTop: 'space',
    },
    { key: 'b', label: 'Back', description: 'Go back to the main menu', separatorTop: 'space' },
] as const satisfies SelectMenuProps['items']

const SelectKeyToUrl: { [K in (typeof SelectOptions)[number]['key']]?: string } = {
    // t: '/settings/theme',
    n: '/settings/nuke',
    p: '/settings/project',
}

export default function Settings() {
    const navigate = useNavigate()

    return (
        <Box flexDirection="column" gap={1}>
            <Card>
                <Text>Settings</Text>
            </Card>
            <SelectMenu
                items={SelectOptions}
                onSubmit={(key: (typeof SelectOptions)[number]['key']) => {
                    if (key in SelectKeyToUrl) return navigate(SelectKeyToUrl[key]!)
                    if (key === 'b') return navigate(-1)

                    throw new Error(`Unhandled key: ${key}`)
                }}
            />
        </Box>
    )
}
