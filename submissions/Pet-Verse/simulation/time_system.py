import time 
class TimeSystem :
    def __init__ (self ,cycle_duration_seconds =240 ):
        self .cycle_duration =cycle_duration_seconds 
        self .start_time =time .time ()
        self .current_phase ="Day"
    def update_time (self ):
        elapsed_time =(time .time ()-self .start_time )%self .cycle_duration 
        phase_percentage =elapsed_time /self .cycle_duration 
        if 0 <=phase_percentage <0.25 :
            new_phase ="Morning"
        elif 0.25 <=phase_percentage <0.65 :
            new_phase ="Day"
        elif 0.65 <=phase_percentage <0.90 :
            new_phase ="Evening"
        else :
            new_phase ="Night"
        if new_phase !=self .current_phase :
            self .current_phase =new_phase 
            print (f"\nThe time has changed. It is now {self .current_phase }.")
            return True 
        return False 
    def get_current_phase (self ):
        return self .current_phase 
    def save_data (self ):
        return {
        'start_time':self .start_time ,
        'cycle_duration':self .cycle_duration 
        }
    def load_data (self ,data ):
        self .start_time =data .get ('start_time',time .time ())
        self .cycle_duration =data .get ('cycle_duration',self .cycle_duration )
        self .update_time ()