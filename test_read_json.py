import json
import random

file = "threats_config.json"


with open(file, "r") as f:
    data = json.load(f)
    print(type(data))
    
    rand_item = random.sample(data["distances"].items(), 1)[0]
    rand = random.sample(rand_item[1], 1)[0]
    print(f"Item {rand_item[0]}: {rand}")