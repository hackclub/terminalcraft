import random 
import time 
class WeatherSystem :
    def __init__ (self ):
        self .weather_types =[
        {"name":"Sunny","effects":{"happiness":5.0 ,"energy":3.0 }},
        {"name":"Rainy","effects":{"happiness":-2.0 ,"energy":-1.0 ,"hygiene":-3.0 }},
        {"name":"Cloudy","effects":{"happiness":-1.0 }},
        {"name":"Stormy","effects":{"happiness":-4.0 ,"energy":-3.0 ,"social":-2.0 }},
        {"name":"Snowy","effects":{"energy":-2.0 ,"happiness":2.0 }},
        {"name":"Windy","effects":{"happiness":-1.0 ,"hygiene":-1.0 }}
        ]
        self .current_weather =self .weather_types [0 ]
        self .last_weather_change =time .time ()
        self .weather_duration =random .randint (3600 ,7200 )
    def update_weather (self ):
        current_time =time .time ()
        if current_time -self .last_weather_change >self .weather_duration :
            old_weather =self .current_weather 
            while self .current_weather ==old_weather :
                self .current_weather =random .choice (self .weather_types )
            self .last_weather_change =current_time 
            self .weather_duration =random .randint (3600 ,7200 )
            return True 
        return False 
    def apply_weather_effects (self ,pet ,resistance =0.0 ):
        for need ,effect in self .current_weather ["effects"].items ():
            if need in pet .needs :
                applied_effect =effect *0.05 
                if applied_effect <0 :
                    applied_effect *=(1.0 -resistance )
                pet .needs [need ]=max (0.0 ,min (100.0 ,pet .needs [need ]+applied_effect ))
        if hasattr (pet ,'species'):
            if pet .species =="Dragon"and self .current_weather ["name"]=="Sunny":
                pet .needs ["energy"]=min (100.0 ,pet .needs ["energy"]+0.2 )
            elif pet .species =="Aquatic"and self .current_weather ["name"]=="Rainy":
                pet .needs ["happiness"]=min (100.0 ,pet .needs ["happiness"]+0.3 )
                pet .needs ["hygiene"]=min (100.0 ,pet .needs ["hygiene"]+0.2 )
            elif pet .species =="Arctic"and self .current_weather ["name"]=="Snowy":
                pet .needs ["happiness"]=min (100.0 ,pet .needs ["happiness"]+0.3 )
                pet .needs ["energy"]=min (100.0 ,pet .needs ["energy"]+0.2 )
    def get_weather_description (self ):
        weather_name =self .current_weather ["name"]
        descriptions ={
        "Sunny":"The sun is shining brightly in a clear blue sky.",
        "Rainy":"Rain is falling steadily from gray clouds overhead.",
        "Cloudy":"The sky is covered with fluffy gray clouds.",
        "Stormy":"Thunder rumbles as lightning flashes across the dark sky.",
        "Snowy":"Delicate snowflakes are falling gently from the sky.",
        "Windy":"A strong breeze is blowing, rustling the leaves."
        }
        return descriptions .get (weather_name ,f"The weather is {weather_name }.")
    def get_weather_name (self ):
        return self .current_weather ["name"]