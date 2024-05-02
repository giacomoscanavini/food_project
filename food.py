import pandas as pd
import numpy as np
import re
import json

dictionary_path = "/mnt/c/Users/scana/Dropbox/FoodProject/food_dictionary.json"
database_path = "/mnt/c/Users/scana/Dropbox/FoodProject/food_database.csv"


def load_food_dictionary(file_path=dictionary_path):
    with open(file_path, "r") as file:
        food_dictionary = json.load(file)
    return food_dictionary


def load_food_database(file_path=database_path):
    df = pd.read_csv(file_path)
    # Convert numpy.float64('nan') to np.nan explicitly (redundant but safe for demonstration)
    for col in df.columns:
        df[col] = df[col].apply(lambda x: np.nan if pd.isna(x) else x)
    return df


def extract_nutritional_values(df, text, food_dict, file_path=dictionary_path):
    entries = {
        "Name": None,
        "Category": None,
        "Size": None,
        "Size_unit": None,
        "Size_g": None,
        "Calories": None,
        "Total Fat": None,
        "Saturated fat": None,
        "Cholesterol": None,
        "Sodium": None,
        "Potassium": None,
        "Total Carbohydrate": None,
        "Dietary fiber": None,
        "Sugar": None,
        "Protein": None,
    }

    for entry in entries.keys():

        # entry = entry.lower()

        if entry == "Name":
            name = input("Enter Food: ").lower()
            if name in np.array(df.Name):
                print(f">_ {name} already in database!")
                print(df[df.Name == name])
                return df
            else:
                entries[entry] = name

        elif entry == "Category":
            entries[entry] = get_food_category(entries["Name"], food_dict, file_path)

        elif entry == "Size":
            size = input(
                f"Does {entries['Name']} have a convenient size? [y/n]"
            ).lower()
            if size == "y":
                size = input(f"Convenient size: [e.g. 1 cup, 1 tbs, 1 unit]").lower()
                size = size.split()
                entries[entry] = size[0]
                entries["Size_unit"] = size[1]
            else:
                entries[entry] = np.nan
                entries["Size_unit"] = "g"

        elif entry == "Size_unit":
            pass

        elif entry == "Size_g":
            input_ = input(
                f"How many grams of {entries['Name']} are these values for: 100 g ? [y/n]"
            ).lower()
            if input_ == None or input_ == "y" or input_ == "":
                entries[entry] = 100
            else:
                entries[entry] = float(input_)
        else:
            entries[entry] = find_values(entry, text)
    # Convert dictionary to DataFrame
    new_row = pd.DataFrame([entries])
    # Append to the existing DataFrame
    df = pd.concat([df, new_row], ignore_index=True)

    save_df(df)
    return df


def save_df(df, file_path=database_path):
    df.to_csv(file_path, index=False)


def get_food_category(food_name, food_dict, file_path):
    # Check if the food name is in the dictionary and return the category
    if food_name in food_dict:
        return food_dict[food_name]
    else:
        category = input(
            "Enter Category [dairy, meat, fish, produce, carbs, other]: "
        ).lower()
        food_dict[food_name] = category
        save_entry_to_database(file_path, entry=food_name, category=category)
        return category


def find_values(entry, text):
    # Convert entire text to lowercase to simplify matching
    text = text.lower()

    # Dictionary to handle label variations
    label_variations = {
        "total fat": r"total fats?",
        "saturated fat": r"saturated fats?",
        "cholesterol": r"cholesterol",
        "sodium": r"sodium",
        "potassium": r"potassium",
        "total carbohydrate": r"total (carbohydrate|carbs|carbo|carbohydrates)",
        "dietary fiber": r"dietary fibers?",
        "sugar": r"sugars?",  # Matches both 'sugar' and 'sugars'
        "protein": r"proteins?",
    }

    # Use regex pattern from dictionary or use the entry itself if not found
    regex_entry = label_variations.get(entry.lower(), entry.lower())
    pattern = rf"\b{regex_entry}\s+([\d\.]+)"
    match = re.search(pattern, text)

    if match:
        return float(match.group(1))
    else:
        return 0.0


def save_entry_to_database(file_path, entry, category):
    # Read the existing data from the file
    with open(file_path, "r") as file:
        food_database = json.load(file)
    # Add a new entry to the dictionary
    food_database[entry] = category
    # Write the updated dictionary back to the file
    with open(file_path, "w") as file:
        json.dump(food_database, file, indent=4)  # 'indent=4' for pretty-printing
    print(f">_ Adding {entry}:{category} to the dictionary!")


def calculate_values(df, food):
    value = food.split()[0]
    unit = food.split()[1]
    name = " ".join(food.split()[2:])

    value = float(value)
    unit = unit.lower()
    name = name.lower()

    if unit == "g":
        size = float(df.loc[df["Name"] == name, "Size_g"].values[0])
    else:
        size = float(df.loc[df["Name"] == name, "Size"].values[0])

    cal = df.loc[df["Name"] == name, "Calories"].values[0]
    fat = df.loc[df["Name"] == name, "Total Fat"].values[0]
    carb = df.loc[df["Name"] == name, "Total Carbohydrate"].values[0]
    prot = df.loc[df["Name"] == name, "Protein"].values[0]

    scaling = value / size

    def scale_num(num):
        return num * scaling

    return scale_num(cal), scale_num(fat), scale_num(carb), scale_num(prot)


def find_food(df, food):
    # return df.loc[df["Name"] == food]
    # return df.loc[df["Name"].str.startswith(food)]
    return df.loc[df["Name"].str.contains(food, case=False, na=False)]
