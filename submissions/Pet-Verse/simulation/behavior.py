import random 
import time 
class BehaviorEngine :
    def __init__ (self ):
        self .behavior_cooldown =60 
        self .last_behavior_change ={}
    def update_behavior (self ,pet ,current_phase ="Day"):
        if pet .name not in self .last_behavior_change :
            self .last_behavior_change [pet .name ]=time .time ()
        current_time =time .time ()
        time_since_last_change =current_time -self .last_behavior_change [pet .name ]
        time_since_interaction =current_time -pet .last_interaction_time 
        if time_since_last_change >=self .behavior_cooldown or pet .mood in ["sad","angry","sick"]:
            self ._change_behavior (pet ,time_since_interaction ,current_phase )
            self .last_behavior_change [pet .name ]=current_time 
    def _change_behavior (self ,pet ,time_since_interaction ,current_phase ):
        if current_phase =="Night"and pet .needs ["energy"]<70 :
            behaviors =["sleeping"]
        elif current_phase =="Morning":
            behaviors =["eating","exploring"]
        elif pet .needs ["hunger"]>70 :
            behaviors =["eating","mischievous","bored"]
        elif pet .needs ["energy"]<30 :
            behaviors =["sleeping","bored"]
        elif pet .needs ["happiness"]<30 :
            behaviors =["bored","mischievous"]
        elif pet .needs ["social"]<30 and time_since_interaction >300 :
            behaviors =["bored","mischievous","exploring"]
        else :
            behaviors =["playing","exploring","sleeping","eating"]
        if random .random ()<0.2 :
            pet .current_behavior =random .choice (pet .behaviors )
        else :
            pet .current_behavior =random .choice (behaviors )
        self ._apply_behavior_effects (pet )
    def _apply_behavior_effects (self ,pet ):
        if pet .current_behavior =="playing":
            pet .needs ["energy"]=max (0.0 ,pet .needs ["energy"]-5.0 )
            pet .needs ["happiness"]=min (100.0 ,pet .needs ["happiness"]+3.0 )
        elif pet .current_behavior =="sleeping":
            pet .needs ["energy"]=min (100.0 ,pet .needs ["energy"]+10.0 )
        elif pet .current_behavior =="eating":
            pet .needs ["hunger"]=max (0.0 ,pet .needs ["hunger"]-8.0 )
        elif pet .current_behavior =="exploring":
            pet .needs ["energy"]=max (0.0 ,pet .needs ["energy"]-3.0 )
            pet .needs ["happiness"]=min (100.0 ,pet .needs ["happiness"]+2.0 )
            pet .needs ["hunger"]=min (100.0 ,pet .needs ["hunger"]+2.0 )
        elif pet .current_behavior =="mischievous":
            pet .needs ["happiness"]=min (100.0 ,pet .needs ["happiness"]+5.0 )
            pet .needs ["hygiene"]=max (0.0 ,pet .needs ["hygiene"]-5.0 )