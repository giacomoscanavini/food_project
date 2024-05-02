import json
from datetime import date


def format_meal_data(meal_string):
    meals = {}
    current_meal = None
    lines = meal_string.strip().split("\n")
    for line in lines:
        if line.lower() in ["breakfast", "lunch", "snack", "dinner", "night"]:
            current_meal = line.lower()
            meals[current_meal] = []
        else:
            try:
                quantity, unit, *food = line.split()
                food_name = " ".join(food)
                meals[current_meal].append(
                    {"name": food_name, "size": float(quantity), "unit": unit}
                )
            except ValueError:
                print(f"Error processing line: {line}")
    return meals


def add_daily_food(date, meal_data_string):
    data = load_data("/mnt/c/Users/scana/Dropbox/food_log.json")
    meals = format_meal_data(meal_data_string)
    data.append({"date": date, **meals})
    save_data(data, "/mnt/c/Users/scana/Dropbox/food_log.json")


def load_data(filepath):
    try:
        with open(filepath, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                print(
                    "JSON data is not properly formatted, starting with an empty list."
                )
                data = []  # Initialize as an empty list
    except FileNotFoundError:
        print("File not found, starting with an empty list.")
        data = []  # Initialize as an empty list
    return data


def save_data(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


# Example of how you would use this function
"""
meals_input = '''
breakfast
1 unit banana
100 g greek yogurt
120 g milk whole
lunch
100 g pasta
20 g tomato
snack
130 g greek yogurt vanilla
1 unit egg
dinner
100 g beef steak
50 g mushroom
'''

add_daily_food(str(date.today()), meals_input)
"""
