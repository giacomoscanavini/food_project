import pandas as pd
import numpy as np
import re
import json
import datetime
from dateutil.relativedelta import relativedelta
import os
import matplotlib.pyplot as plt


database_path = "/mnt/c/Users/scana/Dropbox/FoodProject/food_database.csv"
diary_path = "/mnt/c/Users/scana/Dropbox/FoodProject/diary_food/"


def load_food_database(file_path=None):
    df_food = pd.read_csv(file_path)
    # Convert numpy.float64('nan') to np.nan explicitly (redundant but safe for demonstration)
    for col in df_food.columns:
        df_food[col] = df_food[col].apply(lambda x: np.nan if pd.isna(x) else x)
    return df_food


def save_df(df, file_path=None):
    df.to_csv(file_path, index=False)


def generate_dates(start=None, end=None, year=None, month=None):
    """
    Generates a list of dates in the format yyyy-mm-dd between start and end. If year and not month is passed instead, all dates for that year are generated. Similarly if both year and month are passed, all dates in that month are generated

    Parameters:
        start (str): First date to consider, inclusive. Format: 'yyyy-mm-dd'
        end (str): Last date to consider, inclusive. Format: 'yyyy-mm-dd'
        year (int): Year of interest. Format: 2024
        month (int): Month of the year. Format: 11

    Returns:
        list: Contains all generated dates as strings
    """
    date_format = "%Y-%m-%d"
    dates = []

    # Only year is specified
    if year and not month:
        start_date = datetime.datetime(year, 1, 1)
        end_date = start_date + relativedelta(years=1, days=-1)
    # Year and month are both specified
    elif year and month:
        start_date = datetime.datetime(year, month, 1)
        end_date = start_date + relativedelta(months=1, days=-1)
    # Start and end are both specified
    else:
        start_date = datetime.datetime.strptime(start, date_format)
        end_date = datetime.datetime.strptime(end, date_format)

    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime(date_format))
        current_date += datetime.timedelta(days=1)

    return dates


def generate_new_day(path=None, date=None):
    """
    This function creates a new .txt file with the right template in the diary folder with the right template based on today's date

    Parameters:
        path (str): Path to the folder with the diary entries
        date (str): Date to use for the diary entry with format yyyy-mm-dd

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


def find_food(df_food=None, food_name=None, exact=False):
    """
    This function searches the food database to see if there is a match, if so it returns the database entry. This function doesn't reset the index of the filtered pandas.DataFrame

    Parameters:
        df_food (pd.DataFrame): Food database
        food_name (str): String to search in pd.DataFrame
        exact (bool): Determine how strict the search is, whether contained in or exact match

    Returns:
        pd.DataFrame: Filtered pd.DataFrame with string contained in the food name

    """
    if exact:
        mask = df_food["Name"] == food_name
    else:
        mask = df_food["Name"].str.contains(food_name, case=False, na=False)
    return df_food[mask]


# function that imports a diary entry, cretes a dataframe and ?
def diary_entry_to_df(file_name):
    """
    Parses food entries from a text file into a pandas.DataFrame.

    The text file is expected to have a date on the first line, followed by meal sections
    (e.g., breakfast, lunch, snack, dinner, night) and food entries under each section.
    Each food entry is expected to be in the format: "size unit name".

    Parameters:
        file_name (str): The name of the text file to be parsed.

    Returns:
        pd.DataFrame: A DataFrame containing columns for Size, Unit, Name, and Meal.
        str: Date of the diary entry
    """
    # Extract date of diary entry
    date = file_name.split("/")[-1].split(".txt")[0]

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
    return df_diary, date


def recipe_to_df(recipe):
    """
    Parses food entries from a text file into a pandas.DataFrame.

    The text file is expected to have a date on the first line, followed by meal sections
    (e.g., breakfast, lunch, snack, dinner, night) and food entries under each section.
    Each food entry is expected to be in the format: "size unit name".

    Parameters:
        file_name (str): The name of the text file to be parsed.

    Returns:
        pd.DataFrame: A DataFrame containing columns for Size, Unit, Name, and Meal.
        str: Date of the diary entry
    """
    # Initialize an empty list to hold the entries
    entries = []
    current_meal = ""
    lines = recipe.splitlines()
    # Read each line in lines
    for line in lines:
        line = line.strip()

        # Split the line into parts and ensure it has at least three components
        parts = line.split()
        if len(parts) >= 3:
            size = parts[0]  # Size of the food item
            unit = parts[1]  # Unit of measurement
            name = " ".join(parts[2:])  # Name of the food item
            # Append the entry with meal information to the entries list
            entries.append([size, unit, name, current_meal])

    # Create a DataFrame from the list of entries with specified column names
    df_recipe = pd.DataFrame(entries, columns=["Size", "Unit", "Name", "Meal"])
    return df_recipe


def nutrients_to_df(df_diary, df_food, verbose=True):
    """
    This function generates a pandas.DataFrame with all nutrients eaten given a starting pandas.DataFrame of food and quantity eaten

    Parameters:
        df_diary (pd.DataFrame): DataFrame with food eaten and quantities
        df_food (pd.DataFrame): Food database
        verbose (bool): Prints more information

    Returns:
        pd.DataFrame: DataFrame with all food eaten converted to nutrients and scaled according to eaten quantities
    """

    # Initialize output DataFrame
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
        "Meal",
        "Eaten",
        "Scaling",
    ]
    df_nutrients = pd.DataFrame(columns=cols)

    # Initialize output DataFrame entry
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
        "Meal": None,
        "Eaten": None,
        "Scaling": None,
    }

    track_ = [[], [], [], [], []]

    # Loop over eaten food as reported into the diary
    for i in range(df_diary.shape[0]):
        # Store eaten food info
        eaten_size = float(df_diary.loc[i]["Size"])
        eaten_unit = str(df_diary.loc[i]["Unit"])
        eaten_name = str(df_diary.loc[i]["Name"])
        eaten_meal = str(df_diary.loc[i]["Meal"])

        if eaten_meal == "breakfast":
            track_[0].append(eaten_name)
        elif eaten_meal == "lunch":
            track_[1].append(eaten_name)
        elif eaten_meal == "snack":
            track_[2].append(eaten_name)
        elif eaten_meal == "dinner":
            track_[3].append(eaten_name)
        else:
            track_[4].append(eaten_name)

        # print(eaten_size, eaten_unit, eaten_name, eaten_meal)
        # Find entry in food database
        df_dummy = find_food(df_food, eaten_name, exact=True).reset_index(drop=True)
        # Check on the eaten unit to understand if "g" or another unit is reported
        # If eaten : g, use food database Size_g for scaling factor
        if eaten_unit == "g":
            print(eaten_name)
            scale = eaten_size / float(df_dummy.loc[0]["Size_g"])
        # If eaten: not g, check if that unit matches the one in the food database
        else:
            # If it matches, use Size for scaling
            if eaten_unit == str(df_dummy.loc[0]["Size_unit"]):
                print(eaten_name)
                scale = eaten_size / float(df_dummy.loc[0]["Size"])
            # Else, warning error as there is nothing to use for scaling, the entry in the diary must be fixed
            else:
                print(
                    f"WARNING UNIT: eaten = {eaten_unit} vs database = {df_dummy.loc[0]['Size_unit']}"
                )
                continue
        # Fill the output database entry (dictionary) with scaled factors
        dict_nutrients["Name"] = eaten_name
        dict_nutrients["Calories"] = df_dummy.loc[0]["Calories"] * scale
        dict_nutrients["Total_fats"] = df_dummy.loc[0]["Total_fats"] * scale
        dict_nutrients["Saturated_fats"] = df_dummy.loc[0]["Saturated_fats"] * scale
        dict_nutrients["Cholesterol"] = df_dummy.loc[0]["Cholesterol"] * scale
        dict_nutrients["Sodium"] = df_dummy.loc[0]["Sodium"] * scale
        dict_nutrients["Total_carbs"] = df_dummy.loc[0]["Total_carbs"] * scale
        dict_nutrients["Dietary_fibers"] = df_dummy.loc[0]["Dietary_fibers"] * scale
        dict_nutrients["Sugars"] = df_dummy.loc[0]["Sugars"] * scale
        dict_nutrients["Proteins"] = df_dummy.loc[0]["Proteins"] * scale
        dict_nutrients["Meal"] = eaten_meal
        dict_nutrients["Eaten"] = eaten_size
        dict_nutrients["Scaling"] = scale

        # Append to the output database
        df_nutrients.loc[i] = dict_nutrients

    if verbose:
        print(f"Breakfast: {', '.join([x for x in track_[0]])}")
        print(f"Lunch: {', '.join([x for x in track_[1]])}")
        print(f"Snack: {', '.join([x for x in track_[2]])}")
        print(f"Dinner: {', '.join([x for x in track_[3]])}")
        print(f"Night: {', '.join([x for x in track_[4]])}")

    return df_nutrients


# duncion that plots averages of main nutrients
def sum_up_day(df_nutrients, category=None):
    """
    This function evaluates all the nutrients eaten in a day by category

    Parameters:
        df_nutrients (pd.DataFrame): DataFrame with all the food eaten and nutrients in a given diary entry scaled accordingly
        category (str): Category of interest. If None, all categories are returned

    Returns:
        pd.DataFrame: DataFrame with all categories of nutrients summed up
        (or if category is passed)
        float: sum of nutrients in a specific category
    """

    # Sum of each category for the whole day
    df_total = df_nutrients.sum(axis=0)

    if category:
        return df_total[category]
    else:
        return df_total


def recipe_details(recipe, df_food):
    """
    Calculates the total nutrients in a recipe, provided all food is listed in the database.

    Parameters:
        recipe (str): Multiline recipe in a similar format to the diary entries
        df_food (pd.DataFrame): Food database

    Returns:
        pd.DataFrame: Details regarding the input recipe
    """
    df_recipe = recipe_to_df(recipe)
    df_nutrients = nutrients_to_df(df_recipe, df_food, verbose=False)
    return sum_up_day(df_nutrients, category=None)[1:-3]


def plot_pie(df_total, date, ax=None):
    """
    Plot a pie chart with the broken down categories and their percentages for a specific day.

    Parameters:
        df_total (pd.DataFrame): DataFrame with all categories of nutrients summed up
        date (str): Day of the diary entry
        ax (matplotlib.Axis):


    Returns:
        None
    """

    calories = df_total["Calories"]
    total_fats = df_total["Total_fats"]
    saturated_fats = df_total["Saturated_fats"]
    other_fats = total_fats - saturated_fats
    cholesterol = df_total["Cholesterol"]
    sodium = df_total["Sodium"]
    total_carbs = df_total["Total_carbs"]
    dietary_fibers = df_total["Dietary_fibers"]
    sugars = df_total["Sugars"]
    other_carbs = total_carbs - dietary_fibers - sugars
    proteins = df_total["Proteins"]

    values = np.array(
        [
            [dietary_fibers, sugars, other_carbs],
            [saturated_fats, other_fats, 0],
            [proteins, 0, 0],
        ]
    )

    size = 0.3
    # Names for the groups and subgroups
    group_names = ["Carbs", "Fats", "Protein"]
    subgroup_names = ["Fiber", "Sugar", "Other", "Saturated", "Other", "", "", "", ""]
    cmap = plt.colormaps["tab20c"]
    outer_colors = cmap(np.arange(3) * 4)
    inner_colors = cmap([1, 2, 3, 5, 6, 7, 9, 9, 9])

    # Outer pie (Groups)
    outer_labels = [
        f"{name}\n{value:.1f}%"
        for name, value in zip(group_names, 100 * values.sum(axis=1) / values.sum())
    ]
    _, texts = ax.pie(
        values.sum(axis=1),
        radius=1 - size,
        colors=outer_colors,
        labels=outer_labels,
        wedgeprops=dict(width=size, edgecolor="w"),
        labeldistance=0.65,
    )

    # Make the labels better readable
    for text in texts:
        text.set_fontsize(9)

    # Inner pie (Subgroups)
    inner_labels = []
    for i, name in enumerate(subgroup_names):
        if i in [0, 1, 2]:
            total = values.sum(axis=1)[0]
        elif i in [3, 4, 5]:
            total = values.sum(axis=1)[1]
        elif i in [6, 7, 8]:
            total = values.sum(axis=1)[2]

        percent_ = 100 * values.flatten()[i] / total
        if percent_ > 0 and percent_ < 99.9:
            inner_labels.append(f"{name}\n{percent_:.1f}%")
        else:
            inner_labels.append("")

    _, texts = ax.pie(
        values.flatten(),
        radius=1,
        colors=inner_colors,
        labels=inner_labels,
        wedgeprops=dict(width=size, edgecolor="w"),
        labeldistance=1.05,
    )

    # Make the labels better readable
    for text in texts:
        text.set_fontsize(8)

    # ax.set(aspect="equal", title=f"{date}\n{int(calories)} kcal")
    ax.text(
        0.4,
        0.45,
        f"{date}\n {int(calories)} kcal",
        va="bottom",
        ha="left",
        transform=ax.transAxes,
        color="black",
    )


"""
TO DO: 
    - A function that takes in input a list of generated dates, looks for the diary entries and sums up all those days returning a df for each day
    - A funciton that plots a specific category for all those days to sum up  a whole period, maybe mean of that parameter displayed as vertical line among horizontal bars 
    - Save the plot and updates based on month

"""
