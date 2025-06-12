import SelectInput from 'ink-select-input'
import type { FallbackProps } from 'react-error-boundary'
import Card from '../Card'
import Text from '../Text'

export default function ErrorPage({ error, resetErrorBoundary }: FallbackProps) {
    return (
        <Card>
            <Text color="danger">Woah, something just went seriously wrong!</Text>
            <Text dimColor>{error instanceof Error ? error.stack : String(error)}</Text>
            <SelectInput
                items={[
                    { label: 'Quit', value: 'q' },
                    { label: 'Retry', value: 'r' },
                ]}
                onSelect={item => {
                    if (item.value === 'r') resetErrorBoundary()
                    else process.exit(1)
                }}
            />
        </Card>
    )
}
