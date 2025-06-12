class Skill:
    def __init__(self, name, description, tier, prerequisites=None, effect=None):
        self.name = name
        self.description = description
        self.tier = tier
        self.prerequisites = prerequisites if prerequisites else []
        self.effect = effect if effect else {}
ENGINEER_SKILL_TREE = {
    'mechanic': Skill('Mechanic', 'Basic repairs are 10% more effective.', 1, 
                      effect={'type': 'stat_modifier', 'stat': 'repair_amount', 'value': 1.1}),
    'power_management': Skill('Power Management', 'Reduces power consumption of systems by 5%.', 1, 
                            effect={'type': 'stat_modifier', 'stat': 'power_consumption', 'value': 0.95}),
    'advanced_mechanics': Skill('Advanced Mechanics', 'Unlocks targeted system overclocking.', 2, prerequisites=['mechanic'],
                                effect={'type': 'unlock_ability', 'ability': 'overclock'}),
    'reactor_tuning': Skill('Reactor Tuning', 'Increases reactor output by 10%.', 2, prerequisites=['power_management'],
                          effect={'type': 'stat_modifier', 'stat': 'reactor_output', 'value': 1.1}),
}
SCIENTIST_SKILL_TREE = {
    'biologist': Skill('Biologist', 'Gain 10% more samples from fauna.', 1,
                     effect={'type': 'stat_modifier', 'stat': 'sample_yield', 'value': 1.1}),
    'geologist': Skill('Geologist', 'Increases chances of finding rare minerals.', 1,
                     effect={'type': 'stat_modifier', 'stat': 'rare_find_chance', 'value': 1.1}),
    'xenobiology': Skill('Xenobiology', 'Allows identifying monster weaknesses.', 2, prerequisites=['biologist'],
                       effect={'type': 'unlock_ability', 'ability': 'scan_weakness'}),
    'sample_analysis': Skill('Sample Analysis', 'Reduces research time by 15%.', 2, prerequisites=['biologist', 'geologist'],
                         effect={'type': 'stat_modifier', 'stat': 'research_speed', 'value': 0.85}),
}
PILOT_SKILL_TREE = {
    'evasive_maneuvers': Skill('Evasive Maneuvers', '10% chance to dodge an attack.', 1,
                               effect={'type': 'stat_modifier', 'stat': 'dodge_chance', 'value': 0.1}),
    'silent_running_expert': Skill('Silent Running Expert', 'Reduces noise from silent running by a further 25%.', 1,
                                   effect={'type': 'stat_modifier', 'stat': 'silent_running_efficiency', 'value': 0.75}),
    'precision_targeting': Skill('Precision Targeting', 'Increases accuracy of offensive systems by 20%.', 2, prerequisites=['evasive_maneuvers'],
                                 effect={'type': 'stat_modifier', 'stat': 'accuracy', 'value': 1.2}),
    'terrain_navigator': Skill('Terrain Navigator', 'Reduces chance of environmental hazards.', 2, prerequisites=['silent_running_expert'],
                             effect={'type': 'stat_modifier', 'stat': 'hazard_chance', 'value': 0.9}),
}
ALL_SKILL_TREES = {
    "Engineer": ENGINEER_SKILL_TREE,
    "Scientist": SCIENTIST_SKILL_TREE,
    "Pilot": PILOT_SKILL_TREE,
}