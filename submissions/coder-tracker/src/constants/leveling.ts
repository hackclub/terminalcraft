import { getXpRequirementForLevel } from '../utils/leveling'

export const MinimumSessionDuration = 10 * 60 * 1000
// Saving or typing in the app resets the timer
export const MaxDurationBeforeProcrastination = 5 * 60 * 1000

export const FirstLevelXpRequirement = 500
export const XpRequirementIncreasePerLevel = 250

export const MaxXpPerSession = 1000

export const XpGainAmounts = {
    GoalFinished: 50,
    SessionFinished: 100,
    SessionCanceled: -25,
    GoalUnfinished: -20,
    SessionUsedPerMinute: 2,
    ProcrastinationPerMinute: -3,
} as const

export const LevelNames = [
    'Beginner',
    'Typo Fixer',
    'Copy-Paste Master',
    'Script Kiddie',
    'Bug Generator',
    'LLM Prompt Engineering Expert',
    'Google Search Professional',
    'Stack Overflow Scholar',
    '0.1x Engineer',
    'CVE Making Expert',
    'Software Underlord',
]

export const MaxLevel = LevelNames.length - 1

export const MaxXpObtainable = getXpRequirementForLevel(MaxLevel)
