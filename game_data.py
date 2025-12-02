import os
from custom_exceptions import DataLoadError

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

ITEMS_FILE = os.path.join(DATA_DIR, "items.txt")
QUESTS_FILE = os.path.join(DATA_DIR, "quests.txt")

SAVE_DIR = os.path.join(DATA_DIR, "save_games")
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


def load_items():
    """Load items from items.txt and return a dictionary.

    Expected format per line:
        name,type,power,value
    """

    items = {}

    try:
        with open(ITEMS_FILE, "r") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                parts = line.split(",")

                if len(parts) < 4:
                    raise DataLoadError(f"Invalid item line: {line}")

                name = parts[0].strip()
                item_type = parts[1].strip()
                power_str = parts[2].strip()
                value_str = parts[3].strip()

                try:
                    power = int(power_str)
                    value = int(value_str)
                except ValueError:
                    raise DataLoadError(f"Invalid number in item line: {line}")

                items[name] = {
                    "name": name,
                    "type": item_type,
                    "power": power,
                    "value": value,
                }

    except FileNotFoundError:
        raise DataLoadError(f"Items file not found: {ITEMS_FILE}")

    return items


def load_quests():
    """Load quests from quests.txt and return a dictionary.

    Expected format per line:
        id|name|description|xp|gold
    """

    quests = {}

    try:
        with open(QUESTS_FILE, "r") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                parts = line.split("|")

                if len(parts) < 5:
                    raise DataLoadError(f"Invalid quest line: {line}")

                quest_id = parts[0].strip()
                name = parts[1].strip()
                description = parts[2].strip()
                xp_str = parts[3].strip()
                gold_str = parts[4].strip()

                try:
                    xp = int(xp_str)
                    gold = int(gold_str)
                except ValueError:
                    raise DataLoadError(f"Invalid xp/gold value in line: {line}")

                quests[quest_id] = {
                    "id": quest_id,
                    "name": name,
                    "description": description,
                    "xp": xp,
                    "gold": gold,
                }

    except FileNotFoundError:
        raise DataLoadError(f"Quests file not found: {QUESTS_FILE}")

    return quests


def get_save_file_path(player_name):
    """Return the path where a player's save file should be stored."""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    filename = player_name.replace(" ", "_") + ".sav"
    return os.path.join(SAVE_DIR, filename)
