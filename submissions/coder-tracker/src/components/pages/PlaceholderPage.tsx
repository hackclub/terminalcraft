import { useInput } from 'ink'
import { useNavigate } from 'react-router'
import Badge from '../Badge'
import Card from '../Card'
import Text from '../Text'

export default function PlaceholderPage() {
    const navigate = useNavigate()
    useInput(() => navigate(-1))

    return (
        <Card>
            <Text color="danger">This page has not been implemented yet!</Text>
            <Badge>Press any key to go back</Badge>
        </Card>
    )
}
