import urllib.request
import json

VERSION_FILE = 'https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/timestamp.txt'
JSON_FILE = 'https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json'

def update():
    with open('version.txt', encoding='utf-8') as f:
        try:
            local_version = int(f.readline())
        except ValueError:
            local_version = 0

    print(f'Checking latest GAME_MASTER versions (Local version: {local_version})...')

    with urllib.request.urlopen(VERSION_FILE) as f:
        latest_version = int(f.read())

    if latest_version <= local_version:
        print('Local version is the latest version, no update needed.')
        return

    print(f'Found newer version of GAME_MASTER file (Latest: {latest_version}).')

    print('Downloading latest version of GAME_MASTER file...')
    with urllib.request.urlopen(JSON_FILE) as f:
        latest = f.read()

    with open('data.json', 'w', encoding='utf-8') as f:
        f.write(latest.decode())
    with open('version.txt', 'w', encoding='utf-8') as f:
        f.write(str(latest_version))

    print('GAME_MASTER file successfully updated.')


def get_json():
    update()

    with open('data.json', encoding='utf-8') as data_file:
        data = json.load(data_file)
    return data