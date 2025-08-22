import { Box, Transform, useInput } from 'ink'
import Gradient from 'ink-gradient'
import SelectInput, { type Item } from 'ink-select-input'
import Text from './Text'
import { useTheme } from './providers/ThemeProvider'

import { type ComponentProps, type Key, useMemo, useRef } from 'react'

export interface SelectMenuProps<K extends string = string> {
    focused?: boolean
    items: SelectMenuItem[]
    alsoSubmitWithSpace?: boolean
    onSubmit: (key: K) => void
}

interface SelectMenuItem {
    key: Key
    label: string
    description?: string
    danger?: boolean
    separator?: 'space'
    separatorTop?: 'space'
}

export default function SelectMenu<K extends string>({
    items,
    onSubmit,
    alsoSubmitWithSpace: submitWithSpace,
    focused,
}: SelectMenuProps<K>) {
    const highlighted = useRef<K | null>(items[0]!.key as K)
    const theme = useTheme()
    const actualItems = useMemo(
        () =>
            items.map((item, i) => ({
                ...item,
                value: item.key,
                index: i,
            })),
        [items],
    )

    useInput(
        k => {
            if (k === ' ' && highlighted.current) onSubmit(highlighted.current as K)
        },
        {
            isActive: focused && submitWithSpace,
        },
    )

    return (
        <Box paddingX={1}>
            <SelectInput<string>
                isFocused={focused}
                onSelect={item => onSubmit(item.key as K)}
                indicatorComponent={() => null}
                onHighlight={item => {
                    highlighted.current = item.key as K
                }}
                // @ts-expect-error: Bad typings
                itemComponent={({
                    label,
                    description,
                    isSelected,
                    danger,
                    separator,
                    separatorTop,
                    index,
                }: ComponentProps<typeof Item> & SelectMenuItem & { index: number }) => {
                    const isActuallySelected = (focused ?? true) && isSelected

                    return (
                        <Box
                            marginY={Number(isActuallySelected)}
                            marginTop={index && Number(isActuallySelected)}
                            flexDirection="column"
                        >
                            {/* TODO: Other separators */}
                            {separatorTop && <Box height={1} />}
                            <Gradient
                                colors={
                                    isActuallySelected
                                        ? danger
                                            ? [theme.danger, theme.danger]
                                            : [theme.primary, theme.secondary]
                                        : [theme.neutral, theme.neutral]
                                }
                            >
                                {isActuallySelected ? '> ' : '  '}
                                {isActuallySelected ? label.toUpperCase() : label}
                            </Gradient>
                            {description && isActuallySelected && (
                                // Proper indentation for descriptions
                                <Transform transform={(line, index) => (index ? `  ${line}` : line)}>
                                    <Text dimColor>
                                        {'  '}
                                        {description}
                                    </Text>
                                </Transform>
                            )}
                            {/* TODO: Other separators */}
                            {separator && <Box height={1} />}
                        </Box>
                    )
                }}
                // @ts-expect-error: Bad typings
                items={actualItems}
            />
        </Box>
    )
}
