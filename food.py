import pandas as pd
import numpy as np
import re
import json
import datetime
import os


database_path = "/mnt/c/Users/scana/Dropbox/FoodProject/food_database.csv"
diary_path = "/mnt/c/Users/scana/Dropbox/FoodProject/diary_food/"


def generate_new_day(
    date=None, path="/mnt/c/Users/scana/Dropbox/FoodProject/diary_food/"
):
    """
    This function creates a new .txt file with the right template in the diary folder with the right template based on today's date

    Parameters:
        date (str): Date to use for the diary entry with format yyyy-mm-dd
        path (str): Path to the folder with the diary entries

    Returns:
        None
    """
    if date:
        # Use the given date, must be in yyyy-mm-dd format
        today = date
    else:
        # Get today's date in the specified format
        today = datetime.datetime.now().strftime("%Y-%m-%d")

    # Filename using today's date
    filename = f"{path}{today}.txt"

    # Check if the file already exists
    if not os.path.exists(filename):
        # Create and write to the file if it doesn't exist
        with open(filename, "w") as file:
            file.write(today + "\n")  # Write the date
            file.write("breakfast\n\n")  # Write breakfast
            file.write("lunch\n\n")  # Write lunch
            file.write("snack\n\n")  # Write snack
            file.write("dinner\n\n")  # Write dinner
            file.write("night\n")  # Write night

        print(f"File {filename} created successfully.")
    else:
        print(f"File {filename} already exists.")


# function that search for entries with a specific word, prints nutrients
def find_food(df=None, food_name=None):
    """
    This function searches the food database to see if there is a match, if so it prints the database entry

    Parameters:
        df (pd.DataFrame): Food database
        food_name (str): String to search in pd.DataFrame

    Returns:
        pd.DataFrame: Filtered pd.DataFrame with string contained in the food name

    """

    # for i in range(df_food.Name.shape[0]):
    # if 'cheese' in df_food.Name.loc[i]:
    #    df_food.loc[i]

    mask = df["Name"].isin([food_name])
    return df[mask]


# function that imports a diary entry, cretes a dataframe and ?
def parse_diary_entry(file_name):
    """
    Parses food entries from a text file into a pandas DataFrame.

    The text file is expected to have a date on the first line, followed by meal sections
    (e.g., breakfast, lunch, snack, dinner, night) and food entries under each section.
    Each food entry is expected to be in the format: "size unit name".

    Parameters:
        file_name (str): The name of the text file to be parsed.

    Returns:
        pd.DataFrame: A DataFrame containing columns for Size, Unit, Name, and Meal.
    """
    # Initialize an empty list to hold the entries
    entries = []

    # Open the file for reading
    with open(file_name, "r") as file:
        # Skip the first line (date) and start reading from the second line
        next(file)
        current_meal = None  # Variable to keep track of the current meal category

        # Read each line in the file
        for line in file:
            line = line.strip()
            # Check if the line indicates a meal time, update current_meal
            if any(
                meal in line
                for meal in ["breakfast", "lunch", "snack", "dinner", "night"]
            ):
                current_meal = line
            else:
                # Split the line into parts and ensure it has at least three components
                parts = line.split()
                if len(parts) >= 3:
                    size = parts[0]  # Size of the food item
                    unit = parts[1]  # Unit of measurement
                    name = " ".join(parts[2:])  # Name of the food item
                    # Append the entry with meal information to the entries list
                    entries.append([size, unit, name, current_meal])

    # Create a DataFrame from the list of entries with specified column names
    df_diary = pd.DataFrame(entries, columns=["Size", "Unit", "Name", "Meal"])
    return df_diary


# function that sums up a diary day
def convert_diary_entry_to_nutrients(df_diary, df_database):
    """ """

    cols = [
        "Name",
        "Calories",
        "Total_fats",
        "Saturated_fats",
        "Cholesterol",
        "Sodium",
        "Total_carbs",
        "Dietary_fibers",
        "Sugars",
        "Proteins",
    ]

    df_nutrients = pd.DataFrame(columns=cols)

    dict_nutrients = {
        "Name": None,
        "Calories": None,
        "Total_fats": None,
        "Saturated_fats": None,
        "Cholesterol": None,
        "Sodium": None,
        "Total_carbs": None,
        "Dietary_fibers": None,
        "Sugars": None,
        "Proteins": None,
    }
    for i in range(df_diary.shape[0]):
        eaten_size = df.loc[i]["Size"]
        eaten_unit = df.loc[i]["Unit"]
        eaten_name = df.loc[i]["Name"]
        eaten_meal = df.loc[i]["Meal"]

        mask = df_database["Name"].isin([eaten_name])
        df_dummy = df_database[mask]

        Name = df_dummy["Name"]
        Size = df_dummy["Size"]
        Size_unit = df_dummy["Size_unit"]
        Size_g = df_dummy["Size_g"]
        Calories = df_dummy["Calories"]
        Total_fats = df_dummy["Total_fats"]
        Saturated_fats = df_dummy["Saturated_fats"]
        Cholesterol = df_dummy["Cholesterol"]
        Sodium = df_dummy["Sodium"]
        Total_carbs = df_dummy["Total_carbs"]
        Dietary_fibers = df_dummy["Dietary_fibers"]
        Sugars = df_dummy["Sugars"]
        Proteins = df_dummy["Proteins"]

        # Unit in eaten list is not "g"
        if eaten_unit != "g":
            # Units is the one used in the food database --> Use Size
            if eaten_unit == Size_unit:
                scale = eaten_size / Size
            # No match --> Error
            else:
                print(f"WARNING UNIT: eaten = {eaten_unit} vs database = {Size_unit}")
                continue
        # Unit in eaten list is "g"
        else:
            # Units is the one used in the food database --> Use Size_g
            if eaten_unit == Size_unit:
                scale = eaten_size / Size_g
            # No match --> Error
            else:
                print(f"WARNING UNIT: eaten = {eaten_unit} vs database = {Size_unit}")
                continue

        dict_nutrients = {
            "Name": Name,
            "Calories": Calories * scale,
            "Total_fats": Total_fats * scale,
            "Saturated_fats": Saturated_fats * scale,
            "Cholesterol": Cholesterol * scale,
            "Sodium": Sodium * scale,
            "Total_carbs": Total_carbs * scale,
            "Dietary_fibers": Dietary_fibers * scale,
            "Sugars": Sugars * scale,
            "Proteins": Proteins * scale,
        }

        df_nutrients

        new_row = pd.DataFrame([new_data])
        df = df.append(new_row, ignore_index=True)


# duncion that plots averages of main nutrients
# pie chart?
# pick a date and show nutritional details


def load_food_database(file_path=database_path):
    df = pd.read_csv(file_path)
    # Convert numpy.float64('nan') to np.nan explicitly (redundant but safe for demonstration)
    for col in df.columns:
        df[col] = df[col].apply(lambda x: np.nan if pd.isna(x) else x)
    return df


def save_df(df, file_path=database_path):
    df.to_csv(file_path, index=False)


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

    if unit in ["unit", "tbs", "scoop"]:
        size = float(df.loc[df["Name"] == name, "Size"].values[0])
    else:
        size = float(df.loc[df["Name"] == name, "Size_g"].values[0])

    cal = df.loc[df["Name"] == name, "Calories"].values[0]
    fat = df.loc[df["Name"] == name, "Total Fat"].values[0]
    carb = df.loc[df["Name"] == name, "Total Carbohydrate"].values[0]
    prot = df.loc[df["Name"] == name, "Protein"].values[0]

    scaling = value / size

    def scale_num(num):
        return num * scaling

    return scale_num(cal), scale_num(fat), scale_num(carb), scale_num(prot)


dictionary_path = "/mnt/c/Users/scana/Dropbox/FoodProject/food_dictionary.json"


def load_food_dictionary(file_path=dictionary_path):
    with open(file_path, "r") as file:
        food_dictionary = json.load(file)
    return food_dictionary
