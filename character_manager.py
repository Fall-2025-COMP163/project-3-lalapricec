"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: Lauren Price

AI Usage: AI assistance was used formatting and understsnding sections of the code.

This module handles character creation, loading, and saving.
"""

import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================

def create_character(name, character_class):
    """
    Create a new character with stats based on class
    
    Valid classes: Warrior, Mage, Rogue, Cleric
    
    Returns: Dictionary with character data including:
            - name, class, level, health, max_health, strength, magic
            - experience, gold, inventory, active_quests, completed_quests
    
    Raises: InvalidCharacterClassError if class is not valid
    """
    valid_classes = ["Warrior", "Mage", "Rogue", "Cleric"]
    if character_class not in valid_classes:
        raise InvalidCharacterClassError(f"Invalid character class: {character_class}")

    # Base stats by class
    if character_class == "Warrior":
        max_health = 120
        strength = 15
        magic = 5
    elif character_class == "Mage":
        max_health = 80
        strength = 8
        magic = 20
    elif character_class == "Rogue":
        max_health = 90
        strength = 12
        magic = 10
    elif character_class == "Cleric":
        max_health = 100
        strength = 10
        magic = 15

    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": max_health,
        "max_health": max_health,
        "strength": strength,
        "magic": magic,
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }

    # Optional: validate before returning
    validate_character_data(character)

    return character


def save_character(character, save_directory="data/save_games"):
    """
    Save character to file
    
    Filename format: {character_name}_save.txt
    
    File format:
    NAME: character_name
    CLASS: class_name
    LEVEL: 1
    HEALTH: 120
    MAX_HEALTH: 120
    STRENGTH: 15
    MAGIC: 5
    EXPERIENCE: 0
    GOLD: 100
    INVENTORY: item1,item2,item3
    ACTIVE_QUESTS: quest1,quest2
    COMPLETED_QUESTS: quest1,quest2
    
    Returns: True if successful
    Raises: PermissionError, IOError (let them propagate or handle)
    """
    # Ensure directory exists
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    filename = f"{character['name']}_save.txt"
    filepath = os.path.join(save_directory, filename)

    # Lists saved as comma-separated values
    inventory_str = ",".join(character.get("inventory", []))
    active_str = ",".join(character.get("active_quests", []))
    completed_str = ",".join(character.get("completed_quests", []))

    # Any file I/O errors will propagate, as allowed in the spec
    with open(filepath, "w") as f:
        f.write(f"NAME: {character['name']}\n")
        f.write(f"CLASS: {character['class']}\n")
        f.write(f"LEVEL: {character['level']}\n")
        f.write(f"HEALTH: {character['health']}\n")
        f.write(f"MAX_HEALTH: {character['max_health']}\n")
        f.write(f"STRENGTH: {character['strength']}\n")
        f.write(f"MAGIC: {character['magic']}\n")
        f.write(f"EXPERIENCE: {character['experience']}\n")
        f.write(f"GOLD: {character['gold']}\n")
        f.write(f"INVENTORY: {inventory_str}\n")
        f.write(f"ACTIVE_QUESTS: {active_str}\n")
        f.write(f"COMPLETED_QUESTS: {completed_str}\n")

    return True


def load_character(character_name, save_directory="data/save_games"):
    """
    Load character from save file
    
    Args:
        character_name: Name of character to load
        save_directory: Directory containing save files
    
    Returns: Character dictionary
    Raises: 
        CharacterNotFoundError if save file doesn't exist
        SaveFileCorruptedError if file exists but can't be read
        InvalidSaveDataError if data format is wrong
    """
    filename = f"{character_name}_save.txt"
    filepath = os.path.join(save_directory, filename)

    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"Character not found: {character_name}")

    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except OSError:
        # File exists but can't be read properly
        raise SaveFileCorruptedError(f"Could not read save file for {character_name}")

    if not lines:
        raise InvalidSaveDataError("Save file is empty")

    raw_data = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Expect "KEY: value"
        if ":" not in line:
            raise InvalidSaveDataError(f"Invalid line format: {line}")
        key, value = line.split(":", 1)
        raw_data[key.strip()] = value.strip()

    # Required keys in the save file (uppercase)
    required_keys = [
        "NAME", "CLASS", "LEVEL", "HEALTH", "MAX_HEALTH",
        "STRENGTH", "MAGIC", "EXPERIENCE", "GOLD",
        "INVENTORY", "ACTIVE_QUESTS", "COMPLETED_QUESTS"
    ]

    for key in required_keys:
        if key not in raw_data:
            raise InvalidSaveDataError(f"Missing field in save file: {key}")

    # Build the character dict, converting types appropriately
    try:
        character = {
            "name": raw_data["NAME"],
            "class": raw_data["CLASS"],
            "level": int(raw_data["LEVEL"]),
            "health": int(raw_data["HEALTH"]),
            "max_health": int(raw_data["MAX_HEALTH"]),
            "strength": int(raw_data["STRENGTH"]),
            "magic": int(raw_data["MAGIC"]),
            "experience": int(raw_data["EXPERIENCE"]),
            "gold": int(raw_data["GOLD"]),
            "inventory": _parse_list_field(raw_data["INVENTORY"]),
            "active_quests": _parse_list_field(raw_data["ACTIVE_QUESTS"]),
            "completed_quests": _parse_list_field(raw_data["COMPLETED_QUESTS"]),
        }
    except (ValueError, TypeError):
        raise InvalidSaveDataError("Invalid numeric value in save data")

    # Validate structure
    validate_character_data(character)

    return character


def _parse_list_field(value):
    """Helper: parse comma-separated string into list."""
    value = value.strip()
    if value == "":
        return []
    return [item.strip() for item in value.split(",")]


def list_saved_characters(save_directory="data/save_games"):
    """
    Get list of all saved character names
    
    Returns: List of character names (without _save.txt extension)
    """
    if not os.path.exists(save_directory):
        return []

    names = []
    for filename in os.listdir(save_directory):
        if filename.endswith("_save.txt"):
            # Remove the "_save.txt" (9 characters)
            name = filename[:-9]
            names.append(name)

    return names


def delete_character(character_name, save_directory="data/save_games"):
    """
    Delete a character's save file
    
    Returns: True if deleted successfully
    Raises: CharacterNotFoundError if character doesn't exist
    """
    filename = f"{character_name}_save.txt"
    filepath = os.path.join(save_directory, filename)

    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"Character not found: {character_name}")

    os.remove(filepath)
    return True

# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    """
    Add experience to character and handle level ups
    
    Level up formula: level_up_xp = current_level * 100
    Example when leveling up:
    - Increase level by 1
    - Increase max_health by 10
    - Increase strength by 2
    - Increase magic by 2
    - Restore health to max_health
    
    Raises: CharacterDeadError if character health is 0
    """
    if character.get("health", 0) <= 0:
        raise CharacterDeadError("Dead characters cannot gain experience")

    if xp_amount < 0:
        xp_amount = 0

    character["experience"] += xp_amount

    # Level up as many times as needed
    leveled_up = True
    while leveled_up:
        leveled_up = False
        level = character["level"]
        required_xp = level * 100
        if character["experience"] >= required_xp:
            character["level"] += 1
            character["max_health"] += 10
            character["strength"] += 2
            character["magic"] += 2
            character["health"] = character["max_health"]
            leveled_up = True


def add_gold(character, amount):
    """
    Add gold to character's inventory
    
    Args:
        character: Character dictionary
        amount: Amount of gold to add (can be negative for spending)
    
    Returns: New gold total
    Raises: ValueError if result would be negative
    """
    current_gold = character.get("gold", 0)
    new_gold = current_gold + amount

    if new_gold < 0:
        raise ValueError("Gold cannot be negative")

    character["gold"] = new_gold
    return new_gold


def heal_character(character, amount):
    """
    Heal character by specified amount
    
    Health cannot exceed max_health
    
    Returns: Actual amount healed
    """
    if amount < 0:
        amount = 0

    current_health = character.get("health", 0)
    max_health = character.get("max_health", 0)

    new_health = current_health + amount
    if new_health > max_health:
        new_health = max_health

    healed = new_health - current_health
    character["health"] = new_health

    return healed


def is_character_dead(character):
    """
    Check if character's health is 0 or below
    
    Returns: True if dead, False if alive
    """
    return character.get("health", 0) <= 0


def revive_character(character):
    """
    Revive a dead character with 50% health
    
    Returns: True if revived
    """
    if not is_character_dead(character):
        return False

    max_health = character.get("max_health", 0)
    half_health = max_health // 2
    if half_health <= 0:
        half_health = 1

    character["health"] = half_health
    return True

# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    """
    Validate that character dictionary has all required fields
    
    Required fields: name, class, level, health, max_health, 
                    strength, magic, experience, gold, inventory,
                    active_quests, completed_quests
    
    Returns: True if valid
    Raises: InvalidSaveDataError if missing fields or invalid types
    """
    required_fields = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]

    for field in required_fields:
        if field not in character:
            raise InvalidSaveDataError(f"Missing field: {field}")

    # Check numeric fields
    numeric_fields = [
        "level", "health", "max_health",
        "strength", "magic", "experience", "gold"
    ]
    for field in numeric_fields:
        if not isinstance(character[field], int):
            raise InvalidSaveDataError(f"Field {field} must be an integer")

    # Check list fields
    list_fields = ["inventory", "active_quests", "completed_quests"]
    for field in list_fields:
        if not isinstance(character[field], list):
            raise InvalidSaveDataError(f"Field {field} must be a list")

    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
    
    # Test character creation
    # try:
    #     char = create_character("TestHero", "Warrior")
    #     print(f"Created: {char['name']} the {char['class']}")
    #     print(f"Stats: HP={char['health']}, STR={char['strength']}, MAG={char['magic']}")
    # except InvalidCharacterClassError as e:
    #     print(f"Invalid class: {e}")
    
    # Test saving
    # try:
    #     save_character(char)
    #     print("Character saved successfully")
    # except Exception as e:
    #     print(f"Save error: {e}")
    
    # Test loading
    # try:
    #     loaded = load_character("TestHero")
    #     print(f"Loaded: {loaded['name']}")
    # except CharacterNotFoundError:
    #     print("Character not found")
    # except SaveFileCorruptedError:
    #     print("Save file corrupted")
