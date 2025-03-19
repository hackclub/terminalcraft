import { ThemeProvider as InkThemeProvider, defaultTheme, extendTheme } from '@inkjs/ui'
import { type ReactNode, createContext, useContext } from 'react'
import { DefaultTheme } from '../../constants/themes'

export interface Theme {
    brandPrimary: string
    brandSecondary: string
    primary: string
    secondary: string
    neutral: string
    danger: string
    success: string
}

const ThemeContext = createContext(DefaultTheme)

export default function ThemeProvider({ theme, children }: { children: ReactNode; theme?: Theme }) {
    const actualTheme = theme ?? DefaultTheme

    return (
        <ThemeContext.Provider value={actualTheme}>
            <InkThemeProvider
                theme={extendTheme(defaultTheme, {
                    components: {
                        MultiSelect: {
                            styles: {
                                label: ({ isFocused, isSelected }) => ({
                                    color: isFocused
                                        ? actualTheme.primary
                                        : isSelected
                                          ? actualTheme.success
                                          : actualTheme.neutral,
                                }),
                                focusIndicator: () => ({
                                    color: actualTheme.primary,
                                }),
                                selectedIndicator: () => ({
                                    color: actualTheme.success,
                                }),
                            },
                        },
                        ProgressBar: {
                            styles: {
                                completed: () => ({
                                    color: actualTheme.primary,
                                }),
                                remaining: () => ({
                                    color: actualTheme.neutral,
                                    dimColor: true,
                                }),
                            },
                        },
                    },
                })}
            >
                {children}
            </InkThemeProvider>
        </ThemeContext.Provider>
    )
}

export const useTheme = () => useContext(ThemeContext)
