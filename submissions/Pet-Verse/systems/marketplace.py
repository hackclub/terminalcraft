import random 
class Marketplace :
    def __init__ (self ):
        self .items_for_sale ={
        "Food":[
        {"name":"Basic Kibble","type":"Food","price":5 ,"description":"A simple, nutritious meal.","effect":{"type":"feed","value":20 }},
        {"name":"Gourmet Meal","type":"Food","price":15 ,"description":"A delicious, high-quality meal.","effect":{"type":"feed","value":40 }},
        ],
        "Toys":[
        {"name":"Ball","type":"Toys","price":10 ,"description":"A classic toy for playing fetch.","effect":{"type":"play","value":15 }},
        {"name":"Feather Wand","type":"Toys","price":12 ,"description":"A fun toy to chase.","effect":{"type":"play","value":18 }},
        ],
        "Customization":[
        {"name":"Red Bow","type":"Customization","price":50 ,"description":"A stylish red bow.","effect":{"type":"unlock_customization","category":"accessory"}},
        {"name":"Top Hat","type":"Customization","price":75 ,"description":"A dapper top hat.","effect":{"type":"unlock_customization","category":"hat"}},
        ],
        "Furniture":[
        {"name":"Comfy Bed","type":"Furniture","price":100 ,"description":"A cozy bed for your pet to sleep in.","effect":{"type":"energy_recovery","value":0.1 }},
        {"name":"Scratching Post","type":"Furniture","price":60 ,"description":"A post for scratching, keeps furniture safe!","effect":{"type":"happiness_boost","value":0.05 }},
        {"name":"Food Bowl","type":"Furniture","price":30 ,"description":"A nice bowl for your pet's meals.","effect":{"type":"hunger_reduction","value":0.1 }},
        {"name":"Potted Plant","type":"Furniture","price":40 ,"description":"A decorative plant to liven up the room.","effect":{"type":"happiness_boost","value":0.02 }}
        ]
        }
    def get_available_items (self ):
        return self .items_for_sale 
    def buy_item (self ,pet ,item ):
        price =item ['price']
        discount =0.0 
        if any (t ['name']=='Frugal'for t in pet .talents ):
            talent =next ((t for t in pet .talents if t ['name']=='Frugal'),None )
            if talent :
                discount =talent ['effect']['value']
                price =int (price *(1 -discount ))
                print (f"Frugal talent applied! You get a {discount *100 }% discount.")
        if pet .pet_coins >=price :
            pet .pet_coins -=price 
            item_category =item ['type']
            if item_category in ['Food','Toys']:
                pet .add_to_inventory (item )
            elif item_category =='Customization':
                pet .unlock_customization (item )
            elif item_category =='Furniture':
                pass 
            print (f"You bought a {item ['name']} for {price } PetCoins.")
            return True 
        else :
            print ("You don't have enough PetCoins.")
            return False 
    def save_data (self ):
        return {
        'items_for_sale':self .items_for_sale 
        }
    def load_data (self ,data ):
        self .items_for_sale =data .get ('items_for_sale',self .items_for_sale )
    def sell_item (self ,pet ,item_name ):
        item_to_sell =next ((item for item in pet .inventory if item ['name']==item_name ),None )
        if not item_to_sell :
            print ("You don't have that item in your inventory.")
            return False 
        sell_price =int (item_to_sell .get ('price',0 )*0.5 )
        pet .pet_coins +=sell_price 
        pet .inventory .remove (item_to_sell )
        print (f"You sold a {item_name } for {sell_price } PetCoins.")
        return True 