import os
import game_master


def write_csv(path, header, data):
    with open(os.path.join(os.getcwd(), path), 'w', encoding='utf-8') as fi:
        fi.write(','.join(header))
        fi.write('\n')
        fi.write('\n'.join(data))


def handle_pokemon(data):
    pokemons = {}
    for template in data:
        if 'pokemonSettings' in template['data']:
            pokemonId = str(int(template['templateId'][1:5]))
            pokemon = template['data']['pokemonSettings']
            if pokemonId not in pokemons:
                pokemons[pokemonId] = {
                    'Name': pokemon['pokemonId'],
                    'Form': [str(pokemon['form'])] if 'form' in pokemon else [],
                    'Base Stamina': pokemon['stats'].get('baseStamina', 0),
                    'Base Attack': pokemon['stats'].get('baseAttack', 0),
                    'Base Defence': pokemon['stats'].get('baseDefense', 0),
                    'Type1': pokemon['type'],
                    'Type2': pokemon.get('type2', 'POKEMON_TYPE_NONE'),
                    'Base Capture Rate': pokemon['encounter'].get('baseCaptureRate', 0),
                    'Base Flee Rate': pokemon['encounter'].get('baseFleeRate', 0),
                    'Height (m)': pokemon.get('pokedexHeightM', 0),
                    'Height SD': pokemon.get('heightStdDev', 0),
                    'Weight (kg)': pokemon.get('pokedexWeightKg', 0),
                    'Weight SD': pokemon.get('weightStdDev', 0),
                    'Candy To Evolve': pokemon.get('candyToEvolve', 0),
                    'Buddy Candy Distance (km)': pokemon['kmBuddyDistance'],
                    'Model Height': pokemon.get('modelHeight', 0),
                    'Buddy Size': pokemon.get('buddySize', 'BUDDY_NORMAL'),
                    'Quick Moves': pokemon.get('quickMoves', []),
                    'Cinematic Moves': pokemon.get('cinematicMoves', []),
                }
            elif 'form' in pokemon:
                pokemons[pokemonId].setdefault('Form', []).append(str(pokemon['form']))

            for evolution in pokemon.get('evolutionBranch', []):
                if 'evolution' in evolution or 'temporaryEvolution' in evolution:
                    evolve = evolution.get('evolution', evolution.get('temporaryEvolution'))
                    form = pokemon.get('form', f'{pokemon["pokemonId"]}_NORMAL')
                    pokemons[pokemonId].setdefault('Evolutions', {})[form] = evolution

    pokemon_columns = ['ID', 'Name', 'Form', 'Base Stamina', 'Base Attack', 'Base Defence',
                       'Type1', 'Type2', 'Base Capture Rate', 'Base Flee Rate',
                       'Height (m)', 'Height SD', 'Weight (kg)', 'Weight SD',
                       'Candy To Evolve', 'Buddy Candy Distance (km)', 'Model Height', 'Buddy Size']
    move_columns = ['ID', 'Name', 'Quick Move', 'Cinematic Move']
    evolution_columns = ['ID', 'Name', 'Form', 'Evolution', 'Candy']
    pokemon_rows = []
    move_rows = []
    evolution_rows = []
    for pokemonId, pokemon in pokemons.items():
        pokemon['Form'] = '/'.join(pokemon['Form'])
        row = f'{pokemonId},'
        row += ','.join([str(pokemon[col]) for col in pokemon_columns[1:]])
        pokemon_rows.append(row)

        for quick_move in pokemon['Quick Moves']:
            for cinematic_move in pokemon['Cinematic Moves']:
                move_rows.append(','.join([pokemonId, pokemon['Name'], quick_move, cinematic_move]))

        for form, evolve in pokemon.get('Evolutions', {}).items():
            if 'evolution' in evolve:
                row = [pokemonId, pokemon['Name'], form, evolve['evolution'], evolve.get('candyCost', 0)]
            else:
                row = [pokemonId, pokemon['Name'], form, evolve['temporaryEvolution'], 0]
            evolution_rows.append(','.join([str(i) for i in row]))

    write_csv('pokemon.csv', pokemon_columns, pokemon_rows)
    write_csv('pokemon_moves.csv', move_columns, move_rows)
    write_csv('evolution.csv', evolution_columns, evolution_rows)

    print('Done handling Pokemons.')


def handle_move(data):
    quick_columns = ['ID', 'Name', 'Pokemon Type', 'Power', 'Energy Gain',
                     'Stamina Loss', 'Duration (ms)', 'Window Start (ms)', 'Window End (ms)',
                     'Accuracy', 'Critical']
    cinematic_columns = quick_columns.copy()
    cinematic_columns[4] = 'Energy Used'
    quick_rows = []
    cinematic_rows = []
    for template in data:
        if 'moveSettings' in template['data']:
            move = template['data']['moveSettings']
            row = [int(template['templateId'][1:5]), move['movementId'], move['pokemonType'],
                   move.get('power', 0), move.get('energyDelta', 0),
                   move.get('staminaLossScalar', 0), move['durationMs'], move['damageWindowStartMs'],
                   move['damageWindowEndMs'], move['accuracyChance'], move.get('criticalChance', 0)]

            if 'FAST' in str(move['movementId']):
                quick_rows.append(','.join([str(i) for i in row]))
            else:
                row[4] = abs(row[4])
                cinematic_rows.append(','.join([str(i) for i in row]))

    write_csv('quick_moves.csv', quick_columns, quick_rows)
    write_csv('cinematic_moves.csv', cinematic_columns, cinematic_rows)

    print('Done handling moves.')


def main():
    data = game_master.get_json()

    print('Processing GAME_MASTER data...')

    handle_pokemon(data)
    handle_move(data)

    print('All finished.')


if __name__ == '__main__':
    main()
