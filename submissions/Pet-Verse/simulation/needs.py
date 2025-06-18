import copy 
class NeedsEngine :
    def __init__ (self ):
        self .decay_rates ={
        "hunger":0.05 ,
        "energy":0.03 ,
        "hygiene":0.02 ,
        "happiness":0.04 ,
        "social":0.03 
        }
    def update_needs (self ,pet ,elapsed_time ,weather =None ,current_phase =None ,placed_furniture =None ,housing_system =None ):
        events =[]
        modified_rates =copy .deepcopy (self .decay_rates )
        if weather :
            if weather =="Cold"or weather =="Hot":
                modified_rates ["energy"]*=1.5 
            elif weather =="Rainy":
                modified_rates ["happiness"]*=1.5 
            elif weather =="Sunny":
                modified_rates ["happiness"]*=0.7 
        if current_phase =="Night":
            if pet .current_behavior =="sleeping":
                modified_rates ["energy"]*=0.5 
            if any (t ['name']=='Night Owl'for t in pet .talents ):
                talent =next ((t for t in pet .talents if t ['name']=='Night Owl'),None )
                if talent :
                    modified_rates ["energy"]*=(1 -talent ['effect']['value'])
                    events .append (f"Night Owl talent reduced {pet .name }'s energy decay.")
        if placed_furniture :
            for item in placed_furniture :
                effect =item .get ('effect')
                if not effect :continue 
                if effect ['type']=='energy_recovery'and pet .current_behavior =="sleeping":
                    modified_rates ["energy"]*=(1 -effect ['value'])
                    events .append (f"{item ['name']} is reducing {pet .name }'s energy decay.")
                elif effect ['type']=='happiness_boost':
                    modified_rates ["happiness"]*=(1 -effect ['value'])
                    events .append (f"{item ['name']} is reducing {pet .name }'s happiness decay.")
                elif effect ['type']=='hunger_reduction':
                    modified_rates ["hunger"]*=(1 -effect ['value'])
                    events .append (f"{item ['name']} is reducing {pet .name }'s hunger increase.")
        if any (t ['name']=='Naturalist'for t in pet .talents )and housing_system :
            garden =housing_system .rooms .get ("Garden",{})
            if garden and garden .get ("furniture"):
                talent =next ((t for t in pet .talents if t ['name']=='Naturalist'),None )
                if talent :
                    modified_rates ["happiness"]*=(1 -talent ['effect']['value'])
                    events .append (f"Naturalist talent reduced {pet .name }'s happiness decay in the Garden.")
        for need ,decay_rate in modified_rates .items ():
            if need =="hunger":
                pet .needs [need ]=min (100.0 ,pet .needs [need ]+(decay_rate *elapsed_time ))
            else :
                pet .needs [need ]=max (0.0 ,pet .needs [need ]-(decay_rate *elapsed_time ))
        pet .check_death ()
        return events 