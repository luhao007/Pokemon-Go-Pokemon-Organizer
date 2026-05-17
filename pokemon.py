import os
from typing import Any, Iterable

import game_master
import requests
from tqdm import tqdm


def write_csv(path: str, header: list[str], data: list[str]):
    with open(os.path.join(os.getcwd(), path), "w", encoding="utf-8") as fi:
        fi.write(",".join(header))
        fi.write("\n")
        fi.write("\n".join(data))


def get_pokemon_images(pokemons: Iterable[int]):
    if not os.path.exists("image"):
        os.mkdir("image")
    if not os.path.exists("image/small"):
        os.mkdir("image/small")
    if not os.path.exists("image/full"):
        os.mkdir("image/full")
    if not os.path.exists("image/128"):
        os.mkdir("image/128")

    local_paths = ["image/small/{id}.png", "image/full/{id}.png", "image/128/{id}.png"]
    paths = [
        "https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/detail/{id:03d}.png",
        "https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/{id:03d}.png",
        "https://resource.pokemon-home.com/battledata/img/pokei128/icon{id:04d}_f00_s0.png",
    ]

    for local_path, path in zip(local_paths, paths):
        needs_to_download = [
            id for id in pokemons if not os.path.exists(local_path.format(id=id))
        ]

        if needs_to_download:
            print(f"Downloading {len(needs_to_download)} pokemon images...")

            for id in tqdm(needs_to_download, desc="Downloading images"):
                with open(local_path.format(id=id), "wb") as f:
                    res = requests.get(path.format(id=int(id)))
                    f.write(res.content)

            print("Downloading done.")


def handle_pokemon(data: game_master.GAME_MASTER_TYPE):
    pokemons: dict[int, dict[str, Any]] = {}
    gender_info: dict[int, dict[str, int]] = {}
    for template in data:
        if "pokemonSettings" in template["data"]:
            pokemonId = int(template["templateId"][1:5])
            pokemon: dict[str, Any] = template["data"]["pokemonSettings"]
            if pokemonId not in pokemons:
                stats: dict[str, int] = pokemon["stats"]
                encounter: dict[str, int] = pokemon["encounter"]
                thridMove: dict[str, int] = pokemon.get("thirdMove", {})
                pokemons[pokemonId] = {
                    "Name": pokemon["pokemonId"],
                    "Form": [str(pokemon["form"])] if "form" in pokemon else [],
                    "Base Stamina": stats.get("baseStamina", 0),
                    "Base Attack": stats.get("baseAttack", 0),
                    "Base Defense": stats.get("baseDefense", 0),
                    "Type1": pokemon["type"],
                    "Type2": pokemon.get("type2", "POKEMON_TYPE_NONE"),
                    "Base Capture Rate": encounter.get("baseCaptureRate", 0),
                    "Base Flee Rate": encounter.get("baseFleeRate", 0),
                    "Height (m)": pokemon.get("pokedexHeightM", 0),
                    "Height SD": pokemon.get("heightStdDev", 0),
                    "Weight (kg)": pokemon.get("pokedexWeightKg", 0),
                    "Weight SD": pokemon.get("weightStdDev", 0),
                    "Candy To Evolve": pokemon.get("candyToEvolve", 0),
                    "Buddy Candy Distance (km)": pokemon["kmBuddyDistance"],
                    "Model Height": pokemon.get("modelHeight", 0),
                    "Buddy Size": pokemon.get("buddySize", "BUDDY_NORMAL"),
                    "Quick Moves": pokemon.get("quickMoves", []),
                    "Cinematic Moves": pokemon.get("cinematicMoves", []),
                    "Class": pokemon.get("pokemonClass", "NONE"),
                    "Family": pokemon.get("familyId", "NONE"),
                    "Stardust To Unlock Move": thridMove.get("stardustToUnlock", 0),
                    "Candy To Unlock Move": thridMove.get("candyToUnlock", 0),
                    "isTransferable": pokemon.get("isTransferable", False),
                    "isDeployable": pokemon.get("isDeployable", False),
                    "isTradable": pokemon.get("isTradable", False),
                }
            elif "form" in pokemon:
                pokemons[pokemonId].setdefault("Form", []).append(str(pokemon["form"]))

            for evolution in pokemon.get("evolutionBranch", []):
                if "evolution" in evolution or "temporaryEvolution" in evolution:
                    evolve = evolution.get(
                        "evolution", evolution.get("temporaryEvolution")
                    )
                    form = pokemon.get("form", f'{pokemon["pokemonId"]}_NORMAL')
                    pokemons[pokemonId].setdefault("Evolutions", []).append(
                        [form, evolution]
                    )
        elif "genderSettings" in template["data"]:
            # Spawn setting
            pokemonId = int(template["templateId"][7:11])
            if pokemonId not in gender_info:
                gender = template["data"]["genderSettings"]["gender"]
                gender_info[pokemonId] = {
                    "Male Percent": gender.get("malePercent", 0),
                    "Female Percent": gender.get("femalePercent", 0),
                    "Genderless Percent": gender.get("genderlessPercent", 0),
                }

    for pid, gender_data in gender_info.items():
        if pid in pokemons:
            pokemons[pid].update(gender_data)

    pokemon_columns = [
        "ID",
        "Name",
        "Form",
        "Base Stamina",
        "Base Attack",
        "Base Defense",
        "Type1",
        "Type2",
        "Base Capture Rate",
        "Base Flee Rate",
        "Height (m)",
        "Height SD",
        "Weight (kg)",
        "Weight SD",
        "Candy To Evolve",
        "Buddy Candy Distance (km)",
        "Model Height",
        "Buddy Size",
        "Class",
        "Family",
        "Male Percent",
        "Female Percent",
        "Genderless Percent",
        "Stardust To Unlock Move",
        "Candy To Unlock Move",
        "isTransferable",
        "isDeployable",
        "isTradable",
    ]
    move_columns = ["ID", "Name", "Quick Move", "Cinematic Move"]
    evolution_columns = ["ID", "Name", "Form", "Evolution", "Candy"]
    pokemon_rows: list[str] = []
    move_rows: list[str] = []
    evolution_rows: list[str] = []
    for pokemonId, pokemon in pokemons.items():
        pokemon["Form"] = "/".join(pokemon["Form"])
        row = f"{pokemonId},"
        row += ",".join([str(pokemon[col]) for col in pokemon_columns[1:]])
        pokemon_rows.append(row)

        for quick_move in pokemon["Quick Moves"]:
            for cinematic_move in pokemon["Cinematic Moves"]:
                move_rows.append(
                    ",".join(
                        [
                            str(pokemonId),
                            str(pokemon["Name"]),
                            quick_move,
                            str(cinematic_move),
                        ]
                    )
                )

        for form, evolve in pokemon.get("Evolutions", []):
            if "evolution" in evolve:
                row = [
                    pokemonId,
                    pokemon["Name"],
                    form,
                    evolve["evolution"],
                    evolve.get("candyCost", 0),
                ]
            else:
                row = [
                    pokemonId,
                    pokemon["Name"],
                    form,
                    evolve["temporaryEvolution"],
                    0,
                ]
            evolution_row = ",".join([str(i) for i in row])
            if evolution_row not in evolution_rows:
                evolution_rows.append(evolution_row)

    get_pokemon_images(pokemons.keys())

    write_csv("pokemon.csv", pokemon_columns, pokemon_rows)
    write_csv("pokemon_moves.csv", move_columns, move_rows)
    write_csv("evolution.csv", evolution_columns, evolution_rows)

    print("Done handling Pokemons.")


def handle_move(data: game_master.GAME_MASTER_TYPE):
    quick_columns = [
        "ID",
        "Name",
        "Pokemon Type",
        "Power",
        "Energy Gain",
        "Stamina Loss",
        "Duration (ms)",
        "Window Start (ms)",
        "Window End (ms)",
        "Accuracy",
        "Critical",
    ]
    cinematic_columns = quick_columns.copy()
    cinematic_columns[4] = "Energy Used"
    quick_rows: list[str] = []
    cinematic_rows: list[str] = []
    for template in data:
        if "moveSettings" in template["data"]:
            move = template["data"]["moveSettings"]
            if len(template["templateId"].split("_")[0]) != 5:
                # placeholder data wihtout id
                continue
            row = [
                int(template["templateId"][1:5]),
                move["movementId"],
                move["pokemonType"],
                move.get("power", 0),
                move.get("energyDelta", 0),
                move.get("staminaLossScalar", 0),
                move["durationMs"],
                move.get("damageWindowStartMs", 0),
                move.get("damageWindowEndMs", 0),
                move["accuracyChance"],
                move.get("criticalChance", 0),
            ]

            if "FAST" in str(move["movementId"]):
                quick_rows.append(",".join([str(i) for i in row]))
            else:
                row[4] = abs(row[4])
                cinematic_rows.append(",".join([str(i) for i in row]))

    write_csv("quick_moves.csv", quick_columns, quick_rows)
    write_csv("cinematic_moves.csv", cinematic_columns, cinematic_rows)

    print("Done handling moves.")


def main():
    data = game_master.get_json()

    print("Processing GAME_MASTER data...")

    handle_pokemon(data)
    handle_move(data)

    print("All finished.")


if __name__ == "__main__":
    main()
