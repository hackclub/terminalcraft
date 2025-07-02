TICKET_PRICE = 15
ANIMAL_CONFIG = {
    'Lion': {
        'price': 1000, 'food_cost': 50, 'habitat': 'Savannah', 'appeal': 80, 'base_happiness': 60,
        'preferences': {'temperature': (20, 35), 'enrichment': 60},
        'lifespan': 400, 'maturity_age': 100
    },
    'Penguin': {
        'price': 500, 'food_cost': 20, 'habitat': 'Arctic', 'appeal': 60, 'base_happiness': 75,
        'preferences': {'temperature': (-10, 5), 'enrichment': 50},
        'lifespan': 300, 'maturity_age': 75
    },
    'Monkey': {
        'price': 300, 'food_cost': 15, 'habitat': 'Jungle', 'appeal': 50, 'base_happiness': 70,
        'preferences': {'temperature': (22, 32), 'enrichment': 70},
        'lifespan': 250, 'maturity_age': 50
    },
    'Giraffe': {
        'price': 3000, 'food_cost': 70, 'habitat': 'Savannah', 'appeal': 80, 'base_happiness': 65,
        'preferences': {'temperature': (20, 35), 'enrichment': ['Tall Trees', 'Viewing Platform']},
        'lifespan': 25 * 365, 'maturity_age': 7 * 365
    },
    'Tiger': {
        'price': 7000, 'food_cost': 100, 'habitat': 'Jungle', 'appeal': 90, 'base_happiness': 60,
        'preferences': {'temperature': (10, 30), 'enrichment': ['Pool', 'Rocks']},
        'lifespan': 22 * 365, 'maturity_age': 4 * 365,
        'unlockable': True
    },
    'Panda': {
        'price': 10000, 'food_cost': 120, 'habitat': 'Jungle', 'appeal': 95, 'base_happiness': 65,
        'preferences': {'temperature': (15, 25), 'enrichment': ['Bamboo Forest', 'Climbing Frame']},
        'lifespan': 20 * 365, 'maturity_age': 6 * 365,
        'unlockable': True
    },
    'Velociraptor': {
        'price': 50000, 'food_cost': 200, 'habitat': 'Prehistoric Paddock', 'appeal': 100, 'base_happiness': 50,
        'preferences': {'temperature': (25, 40), 'enrichment': 80},
        'lifespan': 40 * 365, 'maturity_age': 5 * 365,
        'attraction_bonus': 100, 
        'required_habitat': 'Prehistoric Paddock',
        'quest_item': True
    }
}
HABITAT_CONFIG = {
    'Savannah': {'cost': 2000, 'capacity': 4, 'base_temp': 25, 'base_enrichment': 40},
    'Arctic': {'cost': 2500, 'capacity': 6, 'base_temp': 0, 'base_enrichment': 30},
    'Jungle': {'cost': 1500, 'capacity': 8, 'base_temp': 28, 'base_enrichment': 60},
    'Prehistoric Paddock': {
        'cost': 25000, 'capacity': 4, 'security': 95, 'maintenance_cost': 1500,
        'base_temp': 30, 'base_enrichment': 70,
        'quest_item': True
    }
}
STAFF_CONFIG = {
    'Zookeeper': {'salary': 100, 'base_skill': 50, 'description': 'Feeds animals and cleans habitats.'},
    'Veterinarian': {'salary': 150, 'base_skill': 70, 'description': 'Heals sick and injured animals.'}
}
VISITOR_CONFIG = {
    "Family": {
        "spawn_weight": 4,
        "interests": ["Lion", "Penguin", "Monkey"],
        "donation_chance": 0.15,
        "donation_amount": (10, 50) 
    },
    "Student": {
        "spawn_weight": 3,
        "interests": ["Snake", "Crocodile", "Spider"],
        "donation_chance": 0.05,
        "donation_amount": (5, 20)
    },
    "Animal Enthusiast": {
        "spawn_weight": 2,
        "interests": ["Panda", "Tiger", "Gorilla"], 
        "donation_chance": 0.30,
        "donation_amount": (50, 200)
    },
    "Regular": {
        "spawn_weight": 5,
        "interests": [], 
        "donation_chance": 0.10,
        "donation_amount": (10, 30)
    }
}
RANDOM_EVENTS = {
    'disease_outbreak': {
        'chance': 0.05, 'type': 'negative', 'message': "A disease is spreading among the {species}!",
        'effect': {'type': 'health_decline', 'species': 'all', 'amount': 20}
    },
    'pr_scandal': {
        'chance': 0.03, 'type': 'negative', 'message': "A PR scandal has erupted, damaging the zoo's reputation!",
        'effect': {'type': 'reputation_loss', 'amount': 15}
    },
    'philanthropist_visit': {
        'chance': 0.02, 'type': 'positive', 'message': "A wealthy philanthropist visited and was impressed!",
        'effect': {'type': 'donation', 'amount': (5000, 15000)}
    },
    'surprise_birth': {
        'chance': 0.04, 'type': 'positive', 'message': "Surprise! A new {species} has been born!",
        'effect': {'type': 'new_animal'}
    },
    'positive_press': {
        'chance': 0.06, 'type': 'positive', 'message': "The zoo received glowing reviews in the local paper!",
        'effect': {'type': 'visitor_boost', 'multiplier': 1.5, 'duration': 3 
        }
    },
    'habitat_malfunction': {
        'chance': 0.05, 'type': 'negative', 'message': "The {habitat_name} habitat's {system} system has failed!",
        'effect': {'type': 'habitat_damage', 'cost': (500, 2000)}
    },
    'food_spoilage': {
        'chance': 0.07, 'type': 'negative', 'message': "A batch of animal food has spoiled!",
        'effect': {'type': 'financial_loss', 'amount': (200, 800)}
    },
    'fossil_discovery': {
        'chance': 0.05, 'type': 'neutral', 'message': "While expanding a habitat, your team unearthed a mysterious, large fossil!",
        'effect': {'type': 'fossil_found'}
    }
}
ESCAPE_CONFIG = {
    'base_chance': 0.01, 
    'capture_cost': (2000, 5000), 
    'reputation_penalty': 25, 
    'visitor_reduction_multiplier': 0.5, 
    'penalty_duration': 3
}
VIP_VISITORS = {
    'chance': 0.15, 
    'vips': [
        {
            'name': 'Bernard Wealthyworth',
            'title': 'the Philanthropist',
            'objectives': [
                {
                    'type': 'animal_happiness',
                    'text': 'see a {animal} with happiness above 85.',
                    'params': {'species': ['Lion', 'Elephant', 'Panda'], 'value': 85},
                    'reward': {'money': 5000, 'reputation': 5}
                },
                {
                    'type': 'habitat_cleanliness',
                    'text': 'inspect the {habitat} and expects it to be pristine (cleanliness > 90).',
                    'params': {'habitat_type': ['Savannah', 'Jungle', 'Arctic'], 'value': 90},
                    'reward': {'money': 3000, 'reputation': 4}
                }
            ]
        },
        {
            'name': 'Dr. Anya Sharma',
            'title': 'the Famous Zoologist',
            'objectives': [
                {
                    'type': 'see_baby_animal',
                    'text': 'see a newborn animal.',
                    'params': {},
                    'reward': {'money': 4000, 'reputation': 7}
                },
                {
                    'type': 'animal_health',
                    'text': 'check on the {animal}s, hoping to see them in perfect health.',
                    'params': {'species': ['Tiger', 'Penguin'], 'value': 100},
                    'reward': {'money': 6000, 'reputation': 6}
                }
            ]
        }
    ]
}
RESEARCH_PROJECTS = {
    'Advanced Nutrition': {
        'cost': 2000, 'description': 'Improves animal health and happiness through better food.',
        'effect': {'type': 'nutrition_boost', 'value': 10}
    },
    'Efficient Staff Training': {
        'cost': 1500, 'description': 'Reduces the cost and increases the effectiveness of staff training.',
        'effect': {'type': 'training_boost', 'cost_reduction': 0.8, 'skill_gain': 1.2}
    },
    'Exotic Animal Acquisition': {
        'cost': 5000, 'description': 'Unlocks the ability to acquire rare and exotic animals.',
        'effect': {'type': 'unlock_animal', 'species': ['Tiger', 'Panda']}
    },
    'Prehistoric DNA Sequencing': {
        'cost': 10000, 'description': 'A high-risk, high-reward project to sequence the DNA from the fossil.',
        'effect': {'type': 'unlock_dinosaur'},
        'quest_item': True
    }
}