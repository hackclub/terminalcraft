def get_species_list ():
    return [
    {
    "name":"Fluffball",
    "base_stats":{
    "strength":10 ,
    "intelligence":15 ,
    "agility":20 ,
    "charisma":25 
    },
    "evolution_paths":{
    "strength":"MightyFluff",
    "intelligence":"WisdomFluff",
    "agility":"SwiftFluff",
    "charisma":"CharmFluff"
    }
    },
    {
    "name":"Aqualing",
    "base_stats":{
    "strength":15 ,
    "intelligence":20 ,
    "agility":25 ,
    "charisma":10 
    },
    "evolution_paths":{
    "strength":"TidalForce",
    "intelligence":"DeepThought",
    "agility":"WaveRider",
    "charisma":"SirenCall"
    }
    },
    {
    "name":"Emberspark",
    "base_stats":{
    "strength":25 ,
    "intelligence":15 ,
    "agility":15 ,
    "charisma":15 
    },
    "evolution_paths":{
    "strength":"InfernoTitan",
    "intelligence":"PyroSage",
    "agility":"FlameStrider",
    "charisma":"HeartBlaze"
    }
    },
    {
    "name":"Stoneshell",
    "base_stats":{
    "strength":30 ,
    "intelligence":10 ,
    "agility":5 ,
    "charisma":15 
    },
    "evolution_paths":{
    "strength":"MountainGuard",
    "intelligence":"CrystalMind",
    "agility":"QuickStone",
    "charisma":"GemHeart"
    }
    },
    {
    "name":"Leafling",
    "base_stats":{
    "strength":10 ,
    "intelligence":20 ,
    "agility":15 ,
    "charisma":20 
    },
    "evolution_paths":{
    "strength":"AncientRoot",
    "intelligence":"WisdomBloom",
    "agility":"WindDancer",
    "charisma":"FlowerCharm"
    }
    }
    ]
def create_pet (species_data ,name ):
    from pets .pet_base import Pet 
    return Pet (
    species =species_data ["name"],
    name =name ,
    base_stats =species_data ["base_stats"],
    evolution_paths =species_data ["evolution_paths"]
    )