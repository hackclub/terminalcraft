def roundf(num, f):
    return round(num*(10**f))/(10**f)

def minmax(lower, value, upper):
    return max(lower, min(value, upper))