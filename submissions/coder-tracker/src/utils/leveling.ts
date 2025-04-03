import { FirstLevelXpRequirement, MaxLevel, XpRequirementIncreasePerLevel } from '../constants/leveling'

export function getXpRequirementForLevel(level: number) {
    return level ? FirstLevelXpRequirement + (level - 1) * XpRequirementIncreasePerLevel : 0
}

export function getTotalXpRequirementForLevel(level: number): number {
    let total = 0
    for (let i = 0; i < level; i++) total += getXpRequirementForLevel(i)
    return total
}

export function getLevelProgress(xp: number): number {
    const level = getLevel(xp)
    const levelReq = getXpRequirementForLevel(level + 1)
    const levelXp = xp - getTotalXpRequirementForLevel(level)

    return levelXp / levelReq
}

export function getLevel(currentXP: number): number {
    let totalXP = 0
    for (let level = 0; level <= MaxLevel; level++) {
        totalXP += getXpRequirementForLevel(level)
        if (currentXP <= totalXP) return level
    }

    return MaxLevel
}
