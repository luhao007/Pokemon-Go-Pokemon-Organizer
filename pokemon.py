import json
import os
import logging
import game_master

def handle_pokemon(data):
    pokemon_columns = ['ID', 'Name', 'Form', 'Base Stamina', 'Base Attack', 'Base Defence',
                       'Type1', 'Type2', 'Base Capture Rate', 'Base Flee Rate',
                       'Height (m)', 'Height SD', 'Weight (kg)', 'Weight SD',
                       'Candy To Evolve', 'Buddy Candy Distance (km)', 'Model Height', 'Buddy Size']
    move_columns = ['ID', 'Name', 'Quick Move', 'Cinematic Move']
    evolution_columns = ['ID', 'Name', 'Evolution', 'Candy']
    pokemon_rows = []
    move_rows = []
    evolution_rows = []
    for template in data['itemTemplates']:
        if 'pokemonSettings' in template:
            pokemonId = str(int(template['templateId'][1:5]))
            settings = template['pokemonSettings']
            row = [pokemonId, settings['pokemonId'], settings.get('form', ''), settings['stats']['baseStamina'], settings['stats']['baseAttack'], settings['stats']['baseDefense'],
                   settings['type'], settings.get('type2', 'POKEMON_TYPE_NONE'), settings['encounter'].get('baseCaptureRate', 0), settings['encounter'].get('baseFleeRate', 0),
                   settings['pokedexHeightM'], settings['heightStdDev'], settings['pokedexWeightKg'], settings['weightStdDev'], settings.get('candyToEvolve', 0), settings['kmBuddyDistance'],
                   settings['modelHeight'], settings.get('buddySize', 'BUDDY_NORMAL')]
            pokemon_rows.append(','.join([str(i) for i in row]))

            for quick_move in settings['quickMoves']:
                for cinematic_move in settings['cinematicMoves']:
                    row = [pokemonId, settings['pokemonId'], quick_move, cinematic_move]
                    move_rows.append(','.join([str(i) for i in row]))

            for evolve in settings.get('evolutionBranch', []):
                row = [pokemonId, settings['pokemonId'], evolve.get('evolution', ''), evolve.get('candyCost', 0)]
                evolution_rows.append(','.join([str(i) for i in row]))

    file_pokemon = open('{}\pokemon.csv'.format(os.getcwd()), 'w')
    file_pokemon.write(','.join(pokemon_columns))
    file_pokemon.write('\n')
    file_pokemon.write('\n'.join(pokemon_rows))
    file_pokemon.close()

    file_moves = open('{}\pokemon_moves.csv'.format(os.getcwd()), 'w')
    file_moves.write(','.join(move_columns))
    file_moves.write('\n')
    file_moves.write('\n'.join(move_rows))
    file_moves.close()

    file_evolution = open('{}\evolution.csv'.format(os.getcwd()), 'w')
    file_evolution.write(','.join(evolution_columns))
    file_evolution.write('\n')
    file_evolution.write('\n'.join(evolution_rows))
    file_evolution.close()

    logging.info('Done handling Pokemons')


def handle_move(data):
    columns = ['ID', 'Name', 'Pokemon Type', 'Power', 'Energy Gain',
               'Stamina Loss', 'Duration (ms)', 'Window Start (ms)', 'Window End (ms)']
    quick_rows = []
    cinematic_rows = []
    for template in data['itemTemplates']:
        if 'moveSettings' in template:
            settings = template['moveSettings']
            row = [int(template['templateId'][1:5]), settings['movementId'], settings['pokemonType'], settings.get('power', 0), settings.get('energyDelta', 0),
                   settings.get('staminaLossScalar', 0), settings['durationMs'], settings['damageWindowStartMs'], settings['damageWindowEndMs']]

            if 'FAST' in settings['movementId']:
                quick_rows.append(','.join([str(i) for i in row]))
            else:
                row[4] = abs(row[4])
                cinematic_rows.append(','.join([str(i) for i in row]))

    file_quick = open('{}\quick_moves.csv'.format(os.getcwd()), 'w')
    file_quick.write(','.join(columns))
    file_quick.write('\n')
    file_quick.write('\n'.join(quick_rows))
    file_quick.close()

    file_cinematic = open('{}\cinematic_moves.csv'.format(os.getcwd()), 'w')
    file_cinematic.write(','.join(columns))
    file_cinematic.write('\n')
    file_cinematic.write('\n'.join(cinematic_rows))
    file_cinematic.close()

    logging.info('Done handling moves')


def main():
    data = game_master.get_json()

    print('Processing GAME_MASTER data...')

    handle_pokemon(data)
    handle_move(data)

    print('Done')


if __name__ == '__main__':
    main()
