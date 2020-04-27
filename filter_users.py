import json
from pprint import pprint
import re

tweets_data = "./key_users.json"
user_list = "./ListaKont.txt"
out_path = "./ListaFiltr.txt"

users = []
original_file = []

with open(user_list, "r") as f:
    for line in f.readlines():
        original_file.append(line)
        if re.match('#', line):
            continue
        match = re.search(r"from:\w+", line)
        if match:
            users.append(match.group()[len("from:"):])


with open(tweets_data, 'r') as f:
    tweets_data = json.load(f)


tweets_data = tweets_data['users_tweets']
tweets_data = {user['name']: user for user in tweets_data}


def filter_user(username, tweets_data):
    if username in tweets_data:
        print(f"[OK] {username} has {tweets_data[username]['summary']['total_tweets']} tweets about corona...")
        return True
    else:
        print(f"[NOT GOOD] {username} did not tweet about corona...")
        return False


filtered = set()
for user in users:
    if filter_user(user, tweets_data):
        filtered.add(user)

filtered_file = []
for line in original_file:
    if re.match(r'#', line):
        filtered_file.append(line)
        continue
    match = re.search(r"from:\w+", line)
    if match:
        user = match.group()[len("from:"):]
        if user in filtered:
            filtered_file.append(line)
    else:
        filtered_file.append(line)


with open(out_path, 'w') as f:
    f.writelines(filtered_file)
