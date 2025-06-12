class HousingSystem :
    def __init__ (self ):
        self .rooms ={
        "Living Room":{"furniture":[]},
        "Bedroom":{"furniture":[]},
        "Garden":{"furniture":[]}
        }
        self .owned_furniture =[]
    def add_furniture_to_room (self ,furniture_item ,room_name ):
        if room_name in self .rooms :
            if furniture_item in self .owned_furniture :
                self .rooms [room_name ]["furniture"].append (furniture_item )
                self .owned_furniture .remove (furniture_item )
                print (f"Placed {furniture_item ['name']} in the {room_name }.")
                return True 
            else :
                print ("You don't own that furniture.")
                return False 
        else :
            print ("Invalid room.")
            return False 
    def buy_furniture (self ,furniture_item ):
        self .owned_furniture .append (furniture_item )
    def get_all_placed_furniture (self ):
        all_furniture =[]
        for room in self .rooms .values ():
            all_furniture .extend (room ['furniture'])
        return all_furniture 
    def save_data (self ):
        return {
        'rooms':self .rooms ,
        'owned_furniture':self .owned_furniture 
        }
    def load_data (self ,data ):
        self .rooms =data .get ('rooms',self .rooms )
        self .owned_furniture =data .get ('owned_furniture',self .owned_furniture )