import random 
import time 
class Pet :
    def display_needs (self ):
        print ("\nNeeds:")
        for need ,value in self .needs .items ():
            print (f"{need .capitalize ()}: {value :.1f}/100")
    def __init__ (self ,species ,name ,base_stats ,evolution_paths ):
        self .species =species 
        self .name =name 
        self .age =0.0 
        self .evolution_stage =1 
        self .evolution_paths =evolution_paths 
        self .needs ={
        "hunger":50.0 ,
        "energy":100.0 ,
        "hygiene":100.0 ,
        "happiness":50.0 ,
        "social":50.0 
        }
        self .stats ={
        "strength":base_stats .get ("strength",10.0 ),
        "intelligence":base_stats .get ("intelligence",10.0 ),
        "agility":base_stats .get ("agility",10.0 ),
        "charisma":base_stats .get ("charisma",10.0 )
        }
        self .moods =["happy","content","neutral","sad","angry","sick"]
        self .behaviors =["playing","sleeping","eating","exploring","bored","mischievous"]
        self .mood ="neutral"
        self .current_behavior ="sleeping"
        self .is_alive =True 
        self .last_interaction_time =time .time ()
        self .customization ={
        "hat":"None",
        "accessory":"None",
        "color":"Default"
        }
        self .inventory =[]
        self .unlocked_customizations =[]
        self .pet_coins =0 
        self .talents =[]
        self .talent_points =0 
    def feed (self ,success_level =1.0 ):
        increase =20.0 *success_level 
        if any (t ['name']=='Gourmand'for t in self .talents ):
            talent =next ((t for t in self .talents if t ['name']=='Gourmand'),None )
            if talent :
                increase *=(1 +talent ['effect']['value'])
                print ("Gourmand talent activated! Extra nutrients absorbed.")
        self .needs ["hunger"]=max (0.0 ,self .needs ["hunger"]-increase )
        self .needs ["energy"]=min (100.0 ,self .needs ["energy"]+(increase /2 ))
        self .needs ["happiness"]=min (100.0 ,self .needs ["happiness"]+(increase /4 ))
        print (f"You fed {self .name }! Hunger decreased by {increase :.1f}")
        self .update_mood ()
        self .last_interaction_time =time .time ()
    def play (self ):
        if self .needs ["energy"]<20 :
            print (f"{self .name } is too tired to play!")
            return 
        self .needs ["happiness"]=min (100.0 ,self .needs ["happiness"]+15.0 )
        self .needs ["social"]=min (100.0 ,self .needs ["social"]+10.0 )
        self .needs ["energy"]=max (0.0 ,self .needs ["energy"]-15.0 )
        self .needs ["hunger"]=min (100.0 ,self .needs ["hunger"]+5.0 )
        self .stats ["agility"]=min (100.0 ,self .stats ["agility"]+0.5 )
        self .stats ["charisma"]=min (100.0 ,self .stats ["charisma"]+0.3 )
        print (f"You played with {self .name }! Happiness increased!")
        self .update_mood ()
        self .last_interaction_time =time .time ()
    def clean (self ):
        self .needs ["hygiene"]=100.0 
        self .needs ["happiness"]=min (100.0 ,self .needs ["happiness"]+5.0 )
        print (f"You cleaned {self .name }! They're sparkling clean now!")
        self .update_mood ()
        self .last_interaction_time =time .time ()
    def train (self ,success_level =1.0 ,xp_boost =0.0 ):
        if self .needs ["energy"]<30 :
            print (f"{self .name } is too tired to train!")
            return 
        increase =10.0 *success_level 
        increase *=(1 +xp_boost )
        self .stats ["strength"]=min (100.0 ,self .stats ["strength"]+(increase /2 ))
        self .stats ["intelligence"]=min (100.0 ,self .stats ["intelligence"]+(increase /2 ))
        self .needs ["energy"]=max (0.0 ,self .needs ["energy"]-20.0 )
        self .needs ["hunger"]=min (100.0 ,self .needs ["hunger"]+10.0 )
        print (f"You trained {self .name }! Stats improved!")
        self .update_mood ()
        self .last_interaction_time =time .time ()
    def rest (self ):
        self .needs ["energy"]=min (100.0 ,self .needs ["energy"]+30.0 )
        self .needs ["happiness"]=min (100.0 ,self .needs ["happiness"]+5.0 )
        print (f"{self .name } is resting. Energy restored!")
        self .update_mood ()
        self .last_interaction_time =time .time ()
    def socialize (self ,success_level =1.0 ,xp_boost =0.0 ):
        if self .needs ["energy"]<20 :
            print (f"{self .name } is too tired to socialize!")
            return 
        increase =10.0 *success_level 
        increase *=(1 +xp_boost )
        if any (t ['name']=='Quick Learner'for t in self .talents ):
            talent =next ((t for t in self .talents if t ['name']=='Quick Learner'),None )
            if talent :
                increase *=(1 +talent ['effect']['value'])
                print ("Quick Learner talent activated! Extra experience gained.")
        self .stats ["charisma"]=min (100.0 ,self .stats ["charisma"]+increase )
        self .needs ["happiness"]=min (100.0 ,self .needs ["happiness"]+(increase *1.5 ))
        self .needs ["social"]=min (100.0 ,self .needs ["social"]+(increase *2 ))
        self .needs ["energy"]=max (0.0 ,self .needs ["energy"]-10.0 )
        print (f"You socialized with {self .name }! They seem more confident.")
        self .update_mood ()
        self .last_interaction_time =time .time ()
    def groom (self ,success_level =1.0 ):
        increase =20.0 *success_level 
        self .needs ["hygiene"]=min (100.0 ,self .needs ["hygiene"]+increase )
        self .needs ["happiness"]=min (100.0 ,self .needs ["happiness"]+(increase /4 ))
        self .stats ["charisma"]=min (100.0 ,self .stats ["charisma"]+(success_level *0.5 ))
        print (f"You groomed {self .name }! They look fantastic! Hygiene increased by {increase :.1f}")
        self .update_mood ()
        self .last_interaction_time =time .time ()
    def heal (self ,success_level =1.0 ):
        if self .mood !="sick":
            print (f"{self .name } isn't sick right now, but they appreciate the checkup!")
            self .needs ["happiness"]=min (100.0 ,self .needs ["happiness"]+5.0 )
            return 
        increase =20.0 *success_level 
        self .needs ["hygiene"]=min (100.0 ,self .needs ["hygiene"]+(increase /2 ))
        self .needs ["energy"]=min (100.0 ,self .needs ["energy"]+(increase /2 ))
        self .needs ["hunger"]=max (0.0 ,self .needs ["hunger"]-(increase /4 ))
        print (f"You treated {self .name }'s illness! They're feeling much better!")
        self .update_mood ()
        self .last_interaction_time =time .time ()
    def update_mood (self ):
        well_being =(
        (100 -self .needs ["hunger"])*0.2 +
        self .needs ["energy"]*0.2 +
        self .needs ["hygiene"]*0.2 +
        self .needs ["happiness"]*0.2 +
        self .needs ["social"]*0.2 
        )
        if well_being >=80 :
            self .mood ="happy"
        elif well_being >=60 :
            self .mood ="content"
        elif well_being >=40 :
            self .mood ="neutral"
        elif well_being >=20 :
            self .mood ="sad"
        else :
            self .mood ="angry"
        if self .needs ["hygiene"]<20 and random .random ()<0.3 :
            self .mood ="sick"
    def check_evolution (self ):
        if self .evolution_stage <3 :
            required_age =self .evolution_stage *5 
            if self .age >=required_age and sum (self .stats .values ())>=(self .evolution_stage *100 ):
                self .evolution_stage +=1 
                highest_stat =max (self .stats ,key =self .stats .get )
                evolution_path =self .evolution_paths .get (highest_stat ,"balanced")
                print (f"\n*** {self .name } has evolved to stage {self .evolution_stage }! ***")
                print (f"Evolution path: {evolution_path }")
                for stat in self .stats :
                    if stat ==highest_stat :
                        self .stats [stat ]+=15.0 
                    else :
                        self .stats [stat ]+=5.0 
                self .talent_points +=1 
                print ("You earned 1 Talent Point!")
                return True 
        return False 
    def evolve (self ):
        highest_stat =max (self .stats ,key =self .stats .get )
        if highest_stat in self .evolution_paths :
            new_species =self .evolution_paths [highest_stat ]
            old_species =self .species 
            self .species =new_species 
            self .evolution_stage +=1 
            for stat in self .stats :
                self .stats [stat ]=min (100.0 ,self .stats [stat ]*1.2 )
            print (f"\n*** EVOLUTION! ***")
            print (f"{self .name } evolved from {old_species } to {new_species }!")
            print ("All stats have been boosted!")
            return True 
        return False 
    def check_death (self ):
        if self .needs ["hunger"]>=100 or self .needs ["energy"]<=0 :
            self .is_alive =False 
            print (f"\n*** {self .name } has passed away due to neglect. ***")
            return True 
        return False 
    def go_adventure (self ,success_level =1.0 ,found_treasure =None ,xp_boost =0.0 ,coins_earned =0 ):
        if self .needs ["energy"]<30 :
            print (f"{self .name } is too tired to go on an adventure!")
            return 
        self .needs ["energy"]=max (0.0 ,self .needs ["energy"]-25.0 )
        self .needs ["hunger"]=min (100.0 ,self .needs ["hunger"]+15.0 )
        self .needs ["hygiene"]=max (0.0 ,self .needs ["hygiene"]-10.0 )
        self .pet_coins +=coins_earned 
        print (f"{self .name } earned {coins_earned } PetCoins from the adventure!")
        base_stat_gain =2.0 *success_level 
        base_stat_gain *=(1 +xp_boost )
        self .stats ["strength"]=min (100.0 ,self .stats ["strength"]+base_stat_gain *0.2 )
        self .stats ["agility"]=min (100.0 ,self .stats ["agility"]+base_stat_gain *0.5 )
        self .stats ["intelligence"]=min (100.0 ,self .stats ["intelligence"]+base_stat_gain *0.3 )
        if xp_boost >0 :
            print (f"Your pet gained extra experience from the adventure!")
        self .needs ["happiness"]=min (100.0 ,self .needs ["happiness"]+(15.0 *success_level ))
        self .needs ["social"]=min (100.0 ,self .needs ["social"]+(10.0 *success_level ))
        print (f"You took {self .name } on an adventure! They had a great time!")
        if found_treasure :
            self .add_to_inventory (found_treasure )
            print (f"Your pet found a {found_treasure ['name']}!")
            for stat ,boost in found_treasure ['stat_boost'].items ():
                if stat in self .stats :
                    self .stats [stat ]=min (100.0 ,self .stats [stat ]+boost )
                    print (f"{stat .capitalize ()} increased by {boost }!")
            if found_treasure .get ('type')=='customization':
                self .unlock_customization (found_treasure )
                print (f"Your pet found a special customization item: {found_treasure ['name']}!")
                print ("It has been added to your unlocked customizations.")
        self .update_mood ()
        self .last_interaction_time =time .time ()
    def customize (self ,category ,item_name ):
        old_item =self .customization .get (category ,"None")
        self .customization [category ]=item_name 
        self .needs ["happiness"]=min (100.0 ,self .needs ["happiness"]+5.0 )
        print (f"You gave {self .name } a new {category }: {item_name }!")
        print (f"They look fabulous! (Replaced {old_item })")
        self .update_mood ()
        self .last_interaction_time =time .time ()
    def add_to_inventory (self ,item ):
        self .inventory .append (item )
    def unlock_customization (self ,item ):
        """Unlock a new customization item for the pet."""
        if item and item ['name']not in self .unlocked_customizations :
            self .unlocked_customizations .append (item ['name'])
    def learn_talent (self ,talent ):
        if self .talent_points >=talent ['cost']:
            self .talent_points -=talent ['cost']
            self .talents .append (talent )
            print (f"{self .name } learned the '{talent ['name']}' talent!")
            return True 
        else :
            print ("Not enough talent points.")
            return False 