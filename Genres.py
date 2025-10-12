from CW_preprocessing import DataBaseManager as dbm
from Artist import Visualise
import matplotlib.pyplot as plt
import pandas as pd

"""
This program retrieves and visualises genre-related music statistics from an SQLite database 
for a user-specified year between 1998 and 2020. The data includes metrics such as average 
popularity, danceability, and song duration across different music genres. The program provides 
the user with a table and graphical representations (bar and pie charts) of the genre data for 
the selected year.

Key Features:
- Year Validation: Prompts the user to input a valid year between 1998 and 2020.
- Data Fetching: Queries the SQLite database for genre-related statistics, such as the number 
    of songs, average popularity, danceability, and song duration for a given year.
- Table Formatting: Creates a well-formatted table displaying the genre statistics for the 
    selected year.
- Graph Formatting: Generates and displays a side-by-side bar graph (for average song duration) 
    and pie chart (for genre distribution by song count).

Usage:
- Run the script.
- Enter a year between 1998 and 2020 when prompted.
- A table and a bar graph will be displayed one after the other.
"""


def valid_year():
    """
    Prompts user to input a valid year within the range 2998-2020.

    Returns:
        int: A valid year between 1998 and 2020.

    Raises:
        ValueError: If user inputs a non-integer.
    """
    # Loops until valid year has been inputted
    while True:
        try:
            year = int(input("Enter a year between 1998 and 2020:\n"))
            if 1998 <= year <= 2020:
                return year
            print("Year must be between 1998-2020. Try again.")
        except ValueError:
            print("Value Error: must be an integer. Try again")


def fetch_genre_data(db, year):
    """
    Takes the user-chosen year and fetches average popularity, danceability, 
    and duration from the database during the year.

    Args:
        db (str): Filepath to the SQLite3 database.
        year (int): Year to be fetched from the database. 

    Returns:
        Pandas.DataFrame: Dataframe with the following columns:
            - Genre
            - Song Count
            - Average Popularity
            - Average Danceability
            - Average Duration (s)

    Raises:
        Exception: If DatabaseManager encounters an error while interacting with
            the database.
    """
    # Calling DatabaseManager class
    db = dbm(db)
    sql_query = """
            SELECT
                g.Genre,
                COUNT(s.ID) AS Song_Count,
                AVG(s.Popularity) AS Average_Popularity,
                AVG(s.Danceability) AS Average_Danceability,
                AVG(s.Duration) AS Average_Duration_s
            FROM Song s
            JOIN Song_genre sg
                ON s.ID = sg.SongID
            JOIN Genre g
                ON g.ID = sg.GenreID
            WHERE
                s.YEAR = ?
            GROUP BY
                g.Genre
            ORDER BY
                g.Genre ASC;
            """
    # Using query function to fetch the relevent data from the database
    try:
        results = db.query(sql_query, params=(year,))

    except Exception as e:
        raise Exception(
            f"Error occurred while interacting with the database: {e}")

    # Renaming columns
    columns = ["Genre",
               "Song Count",
               "Average Popularity",
               "Average Danceability",
               "Average Duration (s)"]

    # Converting to Pandas.DataFrame
    df = pd.DataFrame(results, columns=columns)
    df["Genre"] = df["Genre"].str.title()

    if df.empty:
        print(
            f"No results found for {year}. Try another year."
        )
        return pd.DataFrame(columns=columns)

    return df.fillna(0).round(2).sort_values("Average Duration (s)", ascending=False)


def format_table(df, year):
    """
    Formats and displays a table of statistics for the use-inputted year.

    Args:
        df (Pandas.DataFrame): Dataset to be formated into a neatly styled table.
        year (int): Year which the data is based on.
    """

    # Calling Visualise class
    vs = Visualise(df)
    vs.create_table(title=f"Genre Statistics for {year}")


def format_graph(df, year):
    """
    Formats and displays a bar graph and pie chart as a subplot with the selected data.

    Args:
        df (Pandas.DataFrame): Data to be visualised into the graphs.
        year (int): User-selected year which the data is based on.
    """

    # Calling Visualise class
    vs = Visualise(df)

    plt.style.use("seaborn-v0_8-colorblind")

    # Creating a subplot to present both graphs
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    vs.create_bar(x_value="Genre",
                  y1_value="Average Duration (s)",
                  x_label="Genres",
                  y1_label="Duration (s)",
                  ax=axes[0],  # To be displayed on the left side of the subplot
                  title=f"Average Song Duration (s) for Genres in {year}")

    vs.create_pie(values="Song Count",
                  labels="Genre",
                  # To be displayed on the right side of the subplot
                  ax=axes[1],
                  title=f"Genre Distribution for {year}")

    # Adjusts subplots so they fit in the figure
    plt.tight_layout()
    plt.show()


def main():
    """
    Main function to orchestrate procedures to fetch, format, and present
    the data.

    Raises:
        Exception: if any unexpected errors occur.
    """
    try:
        year = valid_year()
        df = fetch_genre_data(db, year)

        format_table(df, year)
        format_graph(df, year)

    # Error handling in case an unexpected error
    except Exception as e:
        print("Unexpected error: {}".format(e))


if __name__ == "__main__":
    # Setting db to the filepath of the database
    db = "CWDatabase.db"
    main()
