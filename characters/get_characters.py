import requests
import json

character_file = "playable_characters.json"
with open(character_file,'r') as c_f:
    stored_characters = json.load(c_f)  

n_of_pages = 72
for i in range(1,n_of_pages+1):
    url = f"https://narutodb.xyz/api/character?page={i}" 
    data = requests.get(url)
    data = data.json()
    characters = data['characters']
    my_characters = []

    for character in characters:
        if 'jutsu' in character:
            if len(character['jutsu'])>=3: #add only characters with more than 3 jutsus  
                my_characters.append(character)

    for idx, character in enumerate(my_characters):
        my_characters[idx] = {
            'id':character['id'],
            'name':character['name'],
            'images':character['images'],
            'jutsu':character['jutsu'],
            #'rank': character['rank'],
            }
        stored_characters["playable_characters"].append(my_characters[idx])
        
    
    #write to json file
  
    with open(character_file,'w') as c_file_obj:
        json.dump(stored_characters,c_file_obj,indent=4)
