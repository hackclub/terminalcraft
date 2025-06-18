def get_talents_list ():
    return [
    {
    "name":"Night Owl",
    "description":"Reduces energy decay during the night.",
    "effect":{"type":"night_owl","value":0.2 },
    "cost":2 
    },
    {
    "name":"Gourmand",
    "description":"Increases the effectiveness of food items.",
    "effect":{"type":"gourmand","value":0.1 },
    "cost":1 
    },
    {
    "name":"Quick Learner",
    "description":"Boosts experience gain in all mini-games.",
    "effect":{"type":"quick_learner","value":0.15 },
    "cost":3 
    },
    {
    "name":"Naturalist",
    "description":"Provides a happiness boost when in the Garden.",
    "effect":{"type":"naturalist","value":0.1 },
    "cost":1 
    },
    {
    "name":"Frugal",
    "description":"Reduces the cost of items in the marketplace.",
    "effect":{"type":"frugal","value":0.1 },
    "cost":2 
    }
    ]