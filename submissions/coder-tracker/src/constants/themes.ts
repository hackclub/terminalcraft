import type { Theme } from '../components/providers/ThemeProvider'
import type { ResetUnlocks } from './unlocks'

export const HackerTheme: Theme = {
    brandPrimary: 'rgb(0, 255, 0)',
    brandSecondary: 'rgb(0, 255, 0)',
    primary: 'rgb(0, 255, 0)',
    secondary: 'rgb(0, 255, 0)',
    neutral: 'rgb(0, 255, 0)',
    danger: 'rgb(255, 0, 0)',
    success: 'rgb(0, 255, 0)',
}

export const MonochromeTheme: Theme = {
    brandPrimary: 'white',
    brandSecondary: 'white',
    primary: 'white',
    secondary: 'white',
    neutral: 'white',
    danger: 'white',
    success: 'white',
}

export const DefaultTheme: Theme = {
    brandPrimary: 'cyanBright',
    brandSecondary: 'yellowBright',
    primary: 'rgb(27, 183, 255)',
    secondary: 'rgb(47, 142, 250)',
    neutral: 'white',
    danger: 'rgb(255, 56, 56)',
    success: 'rgb(59, 240, 105)',
}

export const ThemeByResetAndUnlockBit = [
    [HackerTheme, MonochromeTheme],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [], // Commenting here so the formatter can align the array
] as Record<keyof typeof ResetUnlocks, unknown> as unknown as Record<keyof typeof ResetUnlocks, Theme[]>
