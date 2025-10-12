import pandas as pd
import numpy as np
from CW_preprocessing import DataBaseManager as dbm
from Artist import Visualise as vsl

"""
This program fetches and processes data from a database, calculates rankings 
for artists based on popularity, danceability, and other factors, and visualizes 
the results as tables and graphs for a specified year range (1998-2020). It includes 
unctionality for user input validation, weight validation for rankings, penalty 
calculations, and presenting the data in a clear and visually appealing format.

Key Features:
- Validating Year Range: Prompts user to into two values, a start year and end
    year and ensures it is between 1998 and 2020 and that they are not the same
    number.
- Fetching Data: Uses SQL queries to fetch data from the SQLite database about
    popularity, danceability, duration, song count and explicit song count.
- Rank Calculation: Uses song statistics to create a rank value, each given 
    different weightings. Penalties will be given if certain parameters are 
    broken.
- Top 5 Artists: Creates a table of top 5 artists based on this rank value
- Table formatting: Formats and displays a table of the top 5 artists and their
    average rank values, as well as the average for each year within the range.
- Graph Creation: Displays and formats a line graph showing the trends between
    the top 5 artists across the year rang

Usage:
- The user will be prompted to enter a start and end year for analysis.
- The program will fetch artist data for the specified year range from a database.
- It will process the data to calculate penalties, rank values, and generate 
    visualizations.
- The top 5 artists will be displayed in a table and a line graph will show their 
    rank value trends over time.
"""


def get_year_range():
    """
    Prompts user to give a valid start and end year between 1998 and 2020.

    Returns:
        int: year1, start year for the range.
        int: year2, end year for the range.

    Raises:
        ValueError: If input is not an integer.
    """
    while True:
        try:
            year1 = int(
                input("Enter the start year for analysis (1998-2020): "))
            year2 = int(
                input(f"Enter the end year for analysis ({year1}-2020): "))

            if (1998 <= year1 <= 2020) and (1998 <= year2 <= 2020):
                if year1 == year2:
                    print("Start and end year cannot be the same: Try again.")
                elif year1 > year2:
                    year1, year2 = year2, year1
                    print(
                        "Start year is larger than end year and therefore have \
                        been swapped.")
                    return year1, year2
                else:
                    return year1, year2
            else:
                print("Invalid year range: Try again.")

        except ValueError:
            print("ValueError: Input must be an integer, try again.")


def validate_weights(weights, default_weights):
    """
    Validates the weights for the variables given by the user.

    Args:
        weights (dict): Dictionary of variables and weight values used to
            calculate artists' rank value
        default_weights (dict): Default weights for the variables.

    Returns:
        dict: Default weights, if custom weights are chosen then these will
            update the 'default_weight' variable.

    Raises:
        ValueError: If the variable name is not valid, if the weights are not a number,
            or if the weights are not between 0 and 1.
    """
    if weights:
        # Creates a list of invalid names
        invalid_weights = [
            key for key in weights if key not in default_weights]

        if invalid_weights:
            raise ValueError(f"Invalid weight keys: \
                             {', '.join(invalid_weights)}")
        # Checks if the weights are numbers
        if not all(isinstance(value, (float, int)) for value in weights.values()):
            raise ValueError(
                f"All weights must be a numerical value (float or int): {weights}")

        if not all(0 < value < 1 for value in weights.values()):
            raise ValueError("Weights must be between 0 and 1.")

        default_weights.update(weights)
    return default_weights


def validate_columns(data, required_cols):
    """
    Validates column names in the dataframe by comparing them to the
    required columns needed for the rank value equation.

    Args:
        data (Pandas.DataFrame): Dataframe containing column names to be
            validated.
        required_cols (list): List of column name strings which must be
            present for the dataframe to be valid.

    Raises:
        ValueError: If the dataframe is missing any required columns.
    """
    # Creates a list of missing columns
    missing_cols = [col for col in required_cols if col not in data.columns]

    if missing_cols:
        raise ValueError(f"Dataframe is missing the required columns: \
                         {', '.join(missing_cols)}")


def fetch_and_process_data(db, start, end):
    """
    Connects to the database and fetches data from the year range given by the
    user about popularity, danceability, duration, explicit song count, and total 
    song count.

    Args:
        db (str): SQLite database filepath.
        start (int): Start of the year range to fetch the data from.
        end (int): End of the year range to fetch the data from.

    Returns:
        Pandas.DataFrame: Dataframe with neat titles of data from between the 
            selected years.
    """
    # Connecting to the database
    db = dbm(db)

    query = """
    SELECT
        a.ArtistName,
        s.Year,
        AVG(s.Popularity) AS Avg_Pop,
        AVG(s.Danceability) AS Avg_Dan,
        AVG(s.Duration) AS Avg_Dur,
        SUM(CASE
                WHEN s.Explicit = 1
                THEN 1
                ELSE 0
            END) AS Num_Expl,
        COUNT(s.ID) AS Song_Count
    FROM Artist a
    JOIN Song s ON s.ArtistID = a.ID
    WHERE s.Year >= ? AND s.Year <= ?
    GROUP BY a.ArtistName
    ORDER BY Avg_Pop DESC
    ;
    """
    params = (start, end)
    artists = db.query(query, params)

    column_names = ["Name", "Year", "Avg Pop",
                    "Avg Dance", "Avg Dur", "Explicit", "Count"]

    return pd.DataFrame(artists, columns=column_names)


def calculate_penalty(data, weights=None):
    """
    Function to calculate penalties for the Rank Score based on average duration
    and Explicit songs to Song Count ratio.

    Args:
        data (pd.DataFrame): Dataframe with Explicit, Duration, and Count columns.
        weights (dict): Dictionary stating weightings for songs being explicit
            and/or long/short in duration. Defaults to 0.15 for both.

    Returns:
        Pandas.Series: A series containing the overall penalty for each artist.
    """
    default_weights = {"Explicit": 0.15, "Duration": 0.15}
    required_cols = ["Explicit", "Avg Dur", "Count"]

    validate_weights(weights, default_weights)
    validate_columns(data, required_cols=required_cols)

    # Penalty for songs that are explicit
    explicit_pen = 1 - ((data["Explicit"] / data["Count"])
                        * default_weights["Explicit"])
    # Penality for songs that are too long or too short
    duration_pen = 1 - (np.where(
        (data["Avg Dur"] < 120) | (data["Avg Dur"] > 270),
        default_weights["Duration"], 0))
    # Combined penalty - overall score will be multiplied by this number
    return explicit_pen * duration_pen


def calculate_rank(data, penalty, weights=None):
    """
    Calculates a rank score based on song count, popularity, danceability, and
    penalties.

    Args:
        data (Pandas.DataFrame): Dataframe with artist data containing the columns
            ["Count", "Avg Pop", "Avg Dance"].
        penalty (Pandas.Series): Series containing penalties for each song.
        song_weight (float): The weight given to the number of songs released by
            each artist. Defaults to 0.2

    Returns:
        Pandas.Series: A series of rank scores for each song
    """
    default_weights = {"song_weight": 0.2,
                       "pop_weight": 0.6, "dance_weight": 0.4}
    required_cols = ["Count", "Avg Pop", "Avg Dance"]

    validate_columns(data, required_cols)
    weights = validate_weights(weights, default_weights)

    song_multiplier = 1 + (data["Count"] * weights["song_weight"])

    # Equation to calculate the overall rank value for each artist
    rank = ((data["Avg Pop"] * weights["pop_weight"]) +
            ((data["Avg Dance"] * 100) * weights["dance_weight"]) *
            penalty * song_multiplier
            )
    return rank


def top5_prep(data, start, end):
    """
    Preparation of the data to convert the standard dataframe to a more 
    meaningful table, displaying average rank scores across the year range.

    Args:
        data (Pandas.DataFrame): Dataframe containing the Name, Year, and
            variables needed to calculate the rank value for each artist in the 
            year range.
        start (int): Start of the year range.
        end (int): End of the year range.

    Returns:
        Pandas.DataFrame: Dataframe of the Top 5 artists within the year range
            based on their rank value.
    """
    penalty = calculate_penalty(data)
    data["Score"] = calculate_rank(data, penalty)

    # Grouping by artist name and year to gather the average scores
    average_scores = data.groupby(["Name", "Year"], as_index=False)[
        "Score"].mean()

    # Pivoting data to so the years are displayed as columns
    pivot_data = pd.pivot_table(
        average_scores, values="Score", index="Name", columns="Year")

    # List of years in case of any null values for any year
    full_years = list(range(start, end + 1))
    pivot_data = pivot_data.reindex(columns=full_years)

    # Mean rank value for each artist within the year range
    pivot_data["Average"] = pivot_data.mean(skipna=True, axis=1)
    pivot_data = pivot_data.sort_values("Average", ascending=False)

    # Slicing the top 5 highest rank values
    top5_table = pivot_data.reset_index().round(2).head(5)

    # Creating an average row to calculate the mean for each year
    average_row = top5_table.iloc[:, 1:-1].mean(axis=0, skipna=True).round(2)
    average_row["Name"] = "Year Average"
    # Does not show the avergae of the artist averages (bottom right cell)
    average_row["Average"] = " "

    top5_table = pd.concat(
        [top5_table, average_row.to_frame().T], ignore_index=True)

    return top5_table


def format_table(data, start, end):
    """
    Formats and displays table with conditional formatting which highlights the 
    highest score in each year.

    Args: 
        data (Pandas.DataFrame): Dataframe of the top 5 artists within the year
            range.
        start (int): Start of the year range.
        end (int): End of the year range.
    """
    conditions = []

    # Getting the max values for each column
    for col_id, col_name in enumerate(data.columns[1:-1], start=1):
        max_value = data[col_name].max()

        # Displays max values as green
        conditions.append({"columns": [col_id],
                           "condition": lambda x, *args, max_val=max_value: x == max_val,
                           "color": "#d4edda"})
        # Displays NULL values as red
        conditions.append({"columns": [col_id],
                           "condition": lambda x, *args: np.isnan(x),
                           "color": "#f8d7da"})
        # Displays every other cell as white
        conditions.append({"columns": [col_id],
                           "condition": lambda x, *args, max_val=max_value: x != max_val and not np.isnan(x),
                           "color": "white"})

    # Grey columns for presentation
    grey_columns = [{0: "#f2f2f2", data.columns.get_loc("Average"): "#f2f2f2"}]

    # Visualisation class from Artist.py
    vsl(data).create_table(
        title=f"Top 5 Artists between {start}-{end}",
        note="NS = No Songs",
        conditions=conditions,
        col_color=grey_columns,
        row_color=[{len(data): "#cce5ff"}],
        fill_na="NS")


def format_graph(data, start, end):
    """
    Formats and displays line graph of the artists' rank values across the 
    year range

    Args:
        data (Pandas.DataFrame): Dataframe of the top 5 artists within the year
            range.
        start (int): Start of the year range.
        end (int): End of the year range.
    """
    # Reversing the pivot so it is appripriate for visualisation
    top5_long = data.melt(id_vars="Name",
                          value_vars=data.columns[1:-1],
                          var_name="Year",
                          value_name="Rank Value")

    top5_long = top5_long.fillna(0)

    # Visualisation class from Artist.py
    vsl(top5_long).create_line(
        "Year",
        "Rank Value",
        "Name",
        jitter=True,
        title=f"Top 5 Artists between {start}-{end}",
        x_label="Years",
        y_label="Rank Value")


def main():
    """
    Main script to orchestrate the processes.
    """
    try:
        start, end = get_year_range()

        df = fetch_and_process_data(db, start, end)

        top5 = top5_prep(df, start, end)

        format_table(top5, start, end)
        format_graph(top5, start, end)
    except Exception as e:
        raise Exception(f"Unexpected error as occurred: {e}")


if __name__ == "__main__":
    db = "CWDatabase.db"
    main()
