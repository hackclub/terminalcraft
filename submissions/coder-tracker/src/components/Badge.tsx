import Text from './Text'

import type { ComponentProps } from 'react'

export default function Badge({
    children,
    dimColor,
}: Pick<ComponentProps<typeof Text>, 'backgroundColor' | 'dimColor' | 'children'>) {
    return (
        <Text inverse dimColor={dimColor}>
            {' '}
            {children}{' '}
        </Text>
    )
}
