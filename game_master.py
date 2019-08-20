import urllib.request
import json

VERSION_FILE = 'https://raw.githubusercontent.com/pokemongo-dev-contrib/pokemongo-game-master/master/versions/latest-version.txt'
JSON_FILE = 'https://raw.githubusercontent.com/pokemongo-dev-contrib/pokemongo-game-master/master/versions/latest/GAME_MASTER.json'

def update():
    with open('version.txt') as f:
        try:
            local_version = int(f.readline())
        except ValueError:
            local_version = 0

    print('Checking latest GAME_MASTER versions (Local version: {0})...'.format(local_version))

    latest_version = int(urllib.request.urlopen(VERSION_FILE).read())

    if latest_version <= local_version:
        print('Local version is the latest version, no update needed.')
        return

    print('Found newer version of GAME_MASTER file (Latest: {0}).'.format(latest_version))

    print('Downloading latest version of GAME_MASTER file...')
    latest = urllib.request.urlopen(JSON_FILE).read()

    with open('data.json', 'w') as f:
        f.write(latest.decode())
    with open('version.txt', 'w') as f:
        f.write(str(latest_version))

    print('GAME_MASTER file successfully updated.')


def get_json():
    update()

    with open('data.json') as data_file:
        data = json.load(data_file)
    return data