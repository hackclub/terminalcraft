import statistics
import json
import math

from cs2_functions import calculate_exterior

grades = ['Consumer Grade', 'Industrial Grade', 'Mil-Spec Grade', 'Restricted', 'Classified', 'Covert']




def calculate_tradeup(input_items, input_floats):
    with open('json/skins.json', "r", encoding='utf-8') as f:
        skins = json.loads(f.read())

    with open('json/collections.json', "r", encoding='utf-8') as f:
        collections = json.loads(f.read())

    
    avg_float = statistics.mean(input_floats)

    # Check that all rarities are valid
    if input_items[0] == '': return False, 'missing'
    item_rarity = skins[input_items[0]]['rarity']['name']
    if item_rarity == "Covert":
        return False, 'covert'
    
    for i in input_items:
        if i == '':
            return False, 'missing'
        if skins[i]['rarity']['name'] != item_rarity:
            return False, "rarity"
    
    output_items = {}
    total_items = 0
    next_rarity = grades[grades.index(item_rarity)+1]
    for item in input_items:
        item_collection = skins[item]['collections'][0]['name']
        if not next_rarity in collections[item_collection]:
            continue

        for i in collections[item_collection][next_rarity]:
            total_items += 1
            
            max_float = skins[i]['max_float']
            min_float = skins[i]['min_float']

            item_float = avg_float*(max_float-min_float) + min_float
            item_exterior = calculate_exterior(item_float)
            if not i in output_items:
                output_items[i] = {'count': 0, 'exterior': 0}
                output_items[i]['count'] = 1
                output_items[i]['exterior'] = item_exterior
            else:
                output_items[i]['count'] += 1

    output = []
    for key in output_items:
        chance = output_items[key]['count']/total_items
        # make chance a percentage to 2 DPs
        chance = int(chance*10_000)/100
        name = key
        exterior = output_items[key]['exterior']

        output.append([name, chance, exterior])
    
    return True, output
            

        
        
    