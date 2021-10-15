import os
import game_master


def write_csv(path, header, data):
    with open(os.path.join(os.getcwd(), path), 'w', encoding='utf-8') as fi:
        fi.write(','.join(header))
        fi.write('\n')
        fi.write('\n'.join(data))


def handle_pokemon(data):
    pokemons = {}
    for template in data['template']:
        if 'pokemon' in template['data']:
            pokemonId = str(int(template['templateId'][1:5]))
            pokemon = template['data']['pokemon']
            if pokemonId not in pokemons:
                pokemons[pokemonId] = {
                    'Name': pokemon['uniqueId'],
                    'Form': [pokemon['form']] if 'form' in pokemon else [],
                    'Base Stamina': pokemon['stats'].get('baseStamina', 0),
                    'Base Attack': pokemon['stats'].get('baseAttack', 0),
                    'Base Defence': pokemon['stats'].get('baseDefense', 0),
                    'Type1': pokemon['type1'],
                    'Type2': pokemon.get('type2', 'POKEMON_TYPE_NONE'),
                    'Base Capture Rate': pokemon['encounter'].get('baseCaptureRate', 0),
                    'Base Flee Rate': pokemon['encounter'].get('baseFleeRate', 0),
                    'Height (m)': pokemon.get('pokedexHeightM', 0),
                    'Height SD': pokemon.get('heightStdDev', 0),
                    'Weight (kg)': pokemon.get('pokedexWeightKg', 0),
                    'Weight SD': pokemon.get('weightStdDev', 0),
                    'Candy To Evolve': pokemon.get('candyToEvolve', 0),
                    'Buddy Candy Distance (km)': pokemon['kmBuddyDistance'],
                    'Model Height': pokemon['modelHeight'],
                    'Buddy Size': pokemon.get('buddySize', 'BUDDY_NORMAL'),
                    'Quick Moves': pokemon.get('quickMoves', []),
                    'Cinematic Moves': pokemon.get('cinematicMoves', []),
                }
            elif 'form' in pokemon:
                pokemons[pokemonId].setdefault('Form', []).append(pokemon['form'])

            if 'Evolutions' not in pokemons[pokemonId]:
                if template['data']['templateId'].split('_')[-1] not in ('SHADOW', 'PURIFIED'):
                    pokemons[pokemonId]['Evolutions'] = pokemon.get('evolutionBranch', [])

    pokemon_columns = ['ID', 'Name', 'Form', 'Base Stamina', 'Base Attack', 'Base Defence',
                       'Type1', 'Type2', 'Base Capture Rate', 'Base Flee Rate',
                       'Height (m)', 'Height SD', 'Weight (kg)', 'Weight SD',
                       'Candy To Evolve', 'Buddy Candy Distance (km)', 'Model Height', 'Buddy Size']
    move_columns = ['ID', 'Name', 'Quick Move', 'Cinematic Move']
    evolution_columns = ['ID', 'Name', 'Evolution', 'Candy']
    pokemon_rows = []
    move_rows = []
    evolution_rows = []
    for pokemonId, pokemon in pokemons.items():
        row = f'{pokemonId},'
        row += ','.join([str(pokemon[col]) for col in pokemon_columns[1:]])
        pokemon_rows.append(row)

        for quick_move in pokemon['Quick Moves']:
            for cinematic_move in pokemon['Cinematic Moves']:
                move_rows.append(','.join([pokemonId, pokemon['Name'], quick_move, cinematic_move]))

        for evolve in pokemon.get('Evolutions', []):
            if 'evolution' in evolve:
                row = [pokemonId, pokemon['Name'], evolve['evolution'], evolve['candyCost']]
            else:
                row = [pokemonId, pokemon['Name'], evolve['temporaryEvolution'], 0]
            evolution_rows.append(','.join([str(i) for i in row]))

    write_csv('pokemon.csv', pokemon_columns, pokemon_rows)
    write_csv('pokemon_moves.csv', move_columns, move_rows)
    write_csv('evolution.csv', evolution_columns, evolution_rows)

    print('Done handling Pokemons.')


def handle_move(data):
    columns = ['ID', 'Name', 'Pokemon Type', 'Power', 'Energy Gain',
               'Stamina Loss', 'Duration (ms)', 'Window Start (ms)', 'Window End (ms)']
    quick_rows = []
    cinematic_rows = []
    for template in data['template']:
        if 'move' in template['data']:
            move = template['data']['move']
            row = [int(template['templateId'][1:5]), move['uniqueId'], move['type'],
                   move.get('power', 0), move.get('energyDelta', 0),
                   move.get('staminaLossScalar', 0), move['durationMs'], move['damageWindowStartMs'], move['damageWindowEndMs']]

            if 'FAST' in move['uniqueId']:
                quick_rows.append(','.join([str(i) for i in row]))
            else:
                row[4] = abs(row[4])
                cinematic_rows.append(','.join([str(i) for i in row]))

    write_csv('quick_moves.csv', columns, quick_rows)
    write_csv('cinematic_moves.csv', columns, cinematic_rows)

    print('Done handling moves.')


def main():
    data = game_master.get_json()

    print('Processing GAME_MASTER data...')

    handle_pokemon(data)
    handle_move(data)

    print('All finished.')


if __name__ == '__main__':
    main()
