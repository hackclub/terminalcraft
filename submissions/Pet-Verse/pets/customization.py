import random 
class PetCustomization :
    def __init__ (self ):
        self .categories ={
        "hat":[
        {"name":"None","description":"No hat","rarity":"common"},
        {"name":"Party Hat","description":"A colorful party hat","rarity":"common"},
        {"name":"Explorer Hat","description":"Perfect for adventures","rarity":"uncommon"},
        {"name":"Wizard Hat","description":"Increases mystical appearance","rarity":"uncommon"},
        {"name":"Crown","description":"A royal crown fit for a king or queen","rarity":"rare"},
        {"name":"Legendary Helm","description":"An ancient helmet of great power","rarity":"rare"}
        ],
        "accessory":[
        {"name":"None","description":"No accessory","rarity":"common"},
        {"name":"Bow Tie","description":"A stylish bow tie","rarity":"common"},
        {"name":"Scarf","description":"A warm, cozy scarf","rarity":"common"},
        {"name":"Backpack","description":"A small backpack for carrying treasures","rarity":"uncommon"},
        {"name":"Amulet","description":"A mysterious glowing amulet","rarity":"rare"},
        {"name":"Wings","description":"Decorative wings that shimmer in the light","rarity":"rare"}
        ],
        "color":[
        {"name":"Default","description":"Natural coloring","rarity":"common"},
        {"name":"Blue","description":"A cool blue tint","rarity":"common"},
        {"name":"Red","description":"A warm red hue","rarity":"common"},
        {"name":"Green","description":"A vibrant green shade","rarity":"common"},
        {"name":"Purple","description":"A royal purple color","rarity":"uncommon"},
        {"name":"Gold","description":"A shimmering gold effect","rarity":"rare"},
        {"name":"Rainbow","description":"Constantly shifting rainbow colors","rarity":"rare"}
        ]
        }
        self .locked_items ={
        "hat":[
        {"name":"Pirate Hat","description":"Arrrr, matey!","rarity":"uncommon"},
        {"name":"Astronaut Helmet","description":"Ready for space adventures","rarity":"rare"}
        ],
        "accessory":[
        {"name":"Monocle","description":"Quite distinguished","rarity":"uncommon"},
        {"name":"Jetpack","description":"It doesn't actually work, but looks cool","rarity":"rare"}
        ],
        "color":[
        {"name":"Nebula","description":"Cosmic space patterns","rarity":"rare"},
        {"name":"Glitch","description":"Digital pixelated patterns","rarity":"rare"}
        ]
        }
    def get_available_items (self ,category ,unlocked_items =None ):
        """Get all available items for a category, including any unlocked special items"""
        if unlocked_items is None :
            unlocked_items =[]
        available =self .categories .get (category ,[])
        for item in self .locked_items .get (category ,[]):
            if item ["name"]in unlocked_items :
                available .append (item )
        return available 
    def get_item_by_name (self ,category ,name ):
        """Find an item by its name within a category"""
        for item in self .categories .get (category ,[]):
            if item ["name"]==name :
                return item 
        for item in self .locked_items .get (category ,[]):
            if item ["name"]==name :
                return item 
        return None 
    def get_random_item (self ,rarity =None ):
        """Get a random item, optionally filtered by rarity"""
        category =random .choice (list (self .categories .keys ()))
        if rarity :
            items =[item for item in self .categories [category ]if item ["rarity"]==rarity and item ["name"]!="None"and item ["name"]!="Default"]
            locked_items =[item for item in self .locked_items [category ]if item ["rarity"]==rarity ]
        else :
            items =[item for item in self .categories [category ]if item ["name"]!="None"and item ["name"]!="Default"]
            locked_items =self .locked_items [category ]
        all_items =items +locked_items 
        if not all_items :
            return None 
        return random .choice (all_items )
    def get_item_description (self ,pet ):
        """Generate a description of the pet's current customization"""
        if not hasattr (pet ,'customization'):
            return "Your pet has no customizations."
        custom =pet .customization 
        description =[]
        if custom .get ("hat","None")!="None":
            hat =self .get_item_by_name ("hat",custom ["hat"])
            if hat :
                description .append (f"wearing a {hat ['name']}")
        if custom .get ("accessory","None")!="None":
            accessory =self .get_item_by_name ("accessory",custom ["accessory"])
            if accessory :
                description .append (f"adorned with a {accessory ['name']}")
        if custom .get ("color","Default")!="Default":
            color =self .get_item_by_name ("color",custom ["color"])
            if color :
                description .append (f"with a {color ['name'].lower ()} coloration")
        if not description :
            return "Your pet has a natural appearance with no customizations."
        return "Your pet is "+", ".join (description )+"."