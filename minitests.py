import uuid
from datetime import datetime
import json
from utility import get_characters
import random
#with open ("playable_characters.json","r") as f:
#    data = json.load(f)
#    print(len(data["playable_characters"]))
print(type(uuid.uuid4().time))

print(uuid.uuid4())
print(not None)

chat_box_name = "room1"

group_name = "chat_%s" % chat_box_name

print(group_name)



datetime_string = "2024-07-02T20:18:41.569Z"

# Parse the datetime string into a datetime object
datetime_obj = datetime.fromisoformat(datetime_string[:-1])

# Extract the date and time components
date = datetime_obj.date()
time = datetime_obj.time()

print("Date:", date)
print("Time:", time)

for i in range(1,6):
    print(i)


list1 = [{"key1":2},{"key2":3}]
list2 = [{"key3":4},{"key4":5}]

list3 = list1+list2
print(list3)

dic1 = {"key":"value"}
dic1.update({"key2":"value2"})
print(dic1)

uuid_num = uuid.uuid4()
test = f"room_{uuid_num}" 
print(test+" finis")

empty_list = []

print(len(empty_list))

num = "0"
num = int(num)
my_bool = bool(num)
print(my_bool)

import datetime
time_now = datetime.datetime.now()
print(time_now.time().strftime("%H"))
print(time_now.date().day)

test_time = datetime.datetime(2024, 8, 19, 14, 30)
diff = time_now - test_time
print(time_now,test_time)
print("diff: ",diff)
print((diff.seconds%3600)//60)


rank_list = ["E","D","C","B","A"]

loser_rank = "A"
winner_rank = "E"


def rank_index(rank):
    for i in range(len(rank_list)):
        if rank == rank_list[i]:
            index = i

    return index

points = 0
rank_diff = rank_index(loser_rank) - rank_index(winner_rank)

if rank_diff > 0:
    points +=1
    match rank_diff:
        case 1:
            points += 2
        case 2:
            points += 3
        case 3:
            points += 4
        case 4:
            points += 5 
        case _:
            pass               

print(points)

time_now = datetime.datetime.now()
#time_now.day += 30
print(time_now)
    




for i in range(5):
    print("i:",i)

battles = []

fighters = ["a","b","c","d","e","f","g","h"]
registered_fighters = []

refrees = [10,11,12]
registered_refrees = []

# while len(registered_fighters) != len(fighters):
#     #fighters[random.randint(0,len(fighters)-1)]
#     random.shuffle(fighters)
#     random.shuffle(refrees)
#     fighter1 = fighters[0]
#     fighter2 = fighters[1]

#     refree = refrees[0]
    
#     if fighter1 in registered_fighters or fighter2 in registered_fighters:
#         continue
    
#     if (refree in registered_refrees and len(refrees) == len(registered_refrees)) or (refree not in registered_refrees and len(refrees) != len(registered_refrees)):
#         registered_fighters.append(fighter1)
#         registered_fighters.append(fighter2)
#         registered_refrees.append(refree)
#         battles.append(
#         {
#             "fighter1":fighter1,
#             'fighter2': fighter2,
#             'refree':refree
#         }
#     )
#     else:
#         continue
    

# print(registered_fighters)
# print(battles)


rounds = 3
# rounds_battles = {
   
# }
# for i in range(rounds):
#     #get battles for that round in the tournament
#     battles = [
#        {"fighter1": 'a', "fighter2":'b'},
#         {"fighter1": 'c', "fighter2":'d'}
#         ]
#     if len(battles) > 0:
#         rounds_battles[i] = battles
    



# print(rounds_battles[1])    


test_json = {
    'a':'b'
}
try:
    print(test_json['c'])
except:
    print('Error')
        



families = [
    {
    'name': 'a',
    'points':27,
},
{
    'name': 'b',
    'points':20,
},
{
    'name': 'e',
    'points':60,
},
{
    'name': 'x',
    'points':40,
}
] 

sorted_families = sorted(families, key = lambda family: family['points'],reverse=True)

print(sorted_families)

def get_ranking(name):
    for i in range(len(sorted_families)):
        if name == sorted_families[i]['name']:
            ranking = i + 1
            if ranking == 1:
                return f'{ranking}st'
            elif ranking == 2:
                return f'{ranking}nd'
            elif ranking == 3:
                return f'{ranking}rd'
            else:
                return f'{ranking}th'
    return ""
print(families[0])
print(get_ranking('b'))        

from cryptography.fernet import Fernet

fernet  = Fernet('8ABUvgzWftJMEoZ0ghhUpun9YN3GAv-qHQTImmbcPjs=')

def encrypt_message(message:str):
    # Convert the message to bytes
    message_bytes = message.encode()

    #encrypt the message
    encrypted_message = fernet.encrypt(message_bytes)
    return encrypted_message

def decrypt_message(encrypted_message):
    #decrypt message
    decrypted_message = fernet.decrypt(encrypted_message)
    return decrypted_message.decode()

my_message = "Hello world message"
encrypted_message = encrypt_message(my_message)
print(encrypted_message)
print(decrypt_message(encrypted_message))

from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import time
# from requests_html import HTMLSession

def get_anime_memes(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/"
    driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(5)

    html = driver.page_source
    #response = requests.get(url)
    # session = HTMLSession()
    # response = session.get(url)
    # response.html.render(wait = 5)
    soup = BeautifulSoup(html, 'html.parser')

    memes = []
    # for post in soup.find_all('div', class_='Post'):
    #     image_url = post.find('img', class_='preview')['src']
    #     title = post.find('h3', class_='Post-title').text
    #     memes.append({'image_url':image_url, 'title':title})
    for img in soup.find_all('img', {'class':'preview-img'}):
        image_url = img['src']
        memes.append(image_url)
        if len(memes) > 5:
            break


    return memes

#memes = get_anime_memes('animemes')

# for meme in memes:
#     # print(f'Image: {meme['image_url']}')
#     # print(f'Title:{meme['title']}')
#     print("meme:",meme)    


def generate_referall_code(username):
    num1 = random.randint(1,100)
    num2 = random.randint(100,150)
    num3 = random.randint(30,70)
    num4 = random.randint(190,210)
    num5 = random.randint(9,20)
    #str1 = random.ra
    num5 = (num1+num2+num3+num4) % num5
    code = f'{username}-{num1}{num2}{num3}{num4}-{num5}'
    
    link = f'https://chronics.com/users/register/{code}'
    return link

# print(generate_referall_code("Hradolf"))
dic1 = {
    0: 'red'
}
import socket

def get_website_ip(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.error as e:
        return str(e)

# Example usage
domain = 'mboaflix.com'
ip = get_website_ip(domain)
print(f"The IP address of {domain} is {ip}")

import string
import secrets

key = "".join(random.choices(string.ascii_letters + string.digits, k=16))
print(key)

biggest = 0
for it in [10,56,447,89]:
    if it > biggest:
        biggest = it

print(biggest)
count = [1 for x in [1,2,3]]
print(sum(count))

print(uuid.uuid1())