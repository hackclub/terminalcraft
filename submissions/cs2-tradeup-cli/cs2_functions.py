def calculate_exterior(floatValue):
    if floatValue < 0.07:
        return "FN"
    if floatValue < 0.15:
        return "MW"
    if floatValue < 0.38:
        return "FT"
    if floatValue < 0.45:
        return "WW"
    
    return "BS"

