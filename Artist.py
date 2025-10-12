import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from CW_preprocessing import DataBaseManager as dbm
"""
This program fetches, processes, and visualizes data related to an artist's music genre popularity
and compares it with overall genre popularity. The artist's popularity is retrieved from an SQLite 
database, which is then used to create a formatted table and bar graph for visualization.

Key Features:
- Validating User Input: Prompts the user for a valid artist name and ensures it is not empty.
- Fetching Data: Queries the SQLite database for the selected artist’s genre-based popularity data 
    and compares it with the overall popularity of those genres.
- Table Creation: Generates a styled table that displays the artist's genre popularity data, 
    highlighting cells where the artist's popularity is greater than the overall popularity.
- Graph Creation: Creates a bar graph comparing the artist's popularity with the overall genre 
    popularity, with separate bars for each genre.

Usage:
- Run the script.
- Enter in an artist name.
- If valid and data exists in the database, a table and bar graph will be
    displayed one after the other.
"""


class Visualise:
    """
    A class for creating visualisations.
    """

    def __init__(self, data):
        """
        Initialises the Visualise class with a dataset

        Parameters:
            data (Pandas.DataFrame): Data frame to be visualised into the selected
                figure.
        """
        self.data = data

    def create_table(self,
                     title=None,
                     note=None,
                     conditions=None,
                     col_color=None,
                     row_color=None,
                     fill_na="NA",
                     figsize=(14, 6)):
        """
        Creates and displays a table with the selected data with customisable
        formatting and styling.

        Args:
            title (str, optional): Title displayed above the table. Defaults to
                None
            note (str, optional): Text displayed below the table for additional 
                information about the data. Defaults to None
            conditions (list[dict], optional): A list of dictionaries to specify the 
                cell formatting conditions. Each dictionary must include:    
                    - 'columns' (list[int]): Indices of columns to apply the conditions.
                    - 'condition_func' (callable): Function that defines the condition.
                        Should return a boolean value.
                        Example: 'lambda x: x > 10'
                    - 'color' (str): Color to change the cells if the condition is met.
                Defaults to None.
            col_color (list[dict], optional): Dictionary containing the column name 
                or index to change paired with the desired hex code or written color.
                Example: '[{0: 'grey', 1: #ffcccb}]'. Defaults to None
            row_color (list[dict], optional): Dictionary containing the row name 
                or index to change paired with the desired hex code or written color.
                Example: '[{0: 'grey', 1: #ffcccb}]'. Defaults to None.
            fill_na (any, optional): Value to replace any NA or missing values.
                Defaults to NA.
            figsize (tuple, optional): Size of the figure (width, height). 
                Defaults to (14, 6)

        Raises:
            ValueError: If any values are missing or invalid.
            TypeError: If any argument is of an incorrect type.

        """
        try:
            fig, ax = plt.subplots(figsize=figsize)
            # Takes axis off to only show the table
            ax.axis("off")
            table_data = self.data.fillna(
                fill_na).values if fill_na else self.data.values

            table = ax.table(cellText=table_data,
                             colLabels=self.data.columns,
                             loc="center",
                             cellLoc="center",
                             colColours=[[0.9, 0.93, 0.95, 1]] * self.data.shape[1])

            table.scale(1, 1.5)
            table.auto_set_font_size(True)

            # Details for the size and placement for a custom note
            if note:
                ax.text(0.8, 0.25, f"Note: {note}", fontsize=9)

            # Customises the header row to make it stand out
            for (row, col), cell in table.get_celld().items():
                if row == 0:  # Header row
                    # Bold font with dark blue text
                    cell.set_text_props(weight="bold", color="#004085")
                    cell.set_facecolor("#cce5ff")
                    cell.set_edgecolor("lightgrey")
                else:
                    cell.set_edgecolor("lightgrey")

            # checking if the conditions argument is a list
            if conditions and not isinstance(conditions, list):
                raise ValueError("Conditions must be a list of dictionaries")

            if conditions:
                # Goes through all the conditions in the list[dict]
                for condition in conditions:
                    # Defaults to no columns if no column is provided
                    columns = condition.get("columns", [])
                    # Defaults to 'False' if not function is provided
                    condition_func = condition.get(
                        "condition", lambda *args: False)
                    # Defaults to white if no color is provided
                    color = condition.get("color", "white")

                    # Goes through each row to apply the conditions
                    for row_id in range(len(self.data)):
                        # List of values for each row
                        row_values = self.data.iloc[row_id, :].values
                        for col_id in columns:
                            # Passes through every row value and applies condition
                            if condition_func(row_values[col_id], *row_values):
                                table[(row_id + 1, col_id)
                                      ].set_facecolor(color)

            # Checks if col_color is a list of dictionaries
            if col_color and isinstance(col_color, list) \
                    and all(isinstance(item, dict) for item in col_color):
                for col_dict in col_color:  # Goes through each dictionary
                    for col_id, color in col_dict.items():
                        for row_id in range(len(self.data)):
                            table[(row_id + 1, col_id)].set_facecolor(color)

            # Checks if row_color is a list of dictionaries
            if row_color and isinstance(row_color, list) \
                    and all(isinstance(item, dict) for item in row_color):
                for row_dict in row_color:  # Goes through each dictionary
                    for row_id, color in row_dict.items():
                        for col_id in range(len(self.data.columns)):
                            table[(row_id, col_id)].set_facecolor(
                                color)
                            table[(row_id, col_id)].set_text_props(
                                weight="bold")

            if title:
                ax.set_title(title, weight="bold", fontsize=14)

            plt.tight_layout()
            plt.show()

        except (ValueError, TypeError) as e:
            print(f"An error has occurred while creating table: {e}")

    def create_bar(self,
                   x_value,
                   y1_value,
                   y2_value=None,
                   ax=None,
                   title=None,
                   x_label=None,
                   y1_label=None,
                   y2_label=None,
                   figsize=(14, 6)):
        """
        Creates and displays a bar graph to visualise a dataset with customisable 
        formatting.

        Args:
            x_axis (str): Variable to be used on the x-axis.
            y1_value (str): Variable to be used on the y-axis
            y2_value (str, optional): Additional Variable on the y-axis which will
                display as a grouped bar graph. Defaults to None.
            ax (Matplotlib.axes, optional): A Matplotlib axes object for
                embedding the table into a subplot, if needed. Defaults to None.
            title (str, optional): Title to be displayed above the graph. 
                Defaults to None.
            x_label (str, optional): Label for the x-axis. Defaults to None.
            y1_label (str, optional): Label for the first y-axis variable.
                Defaults to None.
            y2_label (str, optional): Label for the second y-axis variable.
                Defaults to None.
            figsize (tuple, optional): Size of the figure (width, height). 
                Defaults to (14, 6)

        Raises:
            ValueError: If any values are missing or invalid.
            TypeError: If any argument is of an incorrect type.

        """
        try:
            plt.style.use("seaborn-v0_8-colorblind")
            # Doesnt plot the figure if it is for a subplot
            fig, ax = plt.subplots(
                figsize=figsize) if ax is None else (None, ax)

            x = self.data[x_value]
            y1 = self.data[y1_value]
            y2 = self.data[y2_value] if y2_value else None

            # Creates an array of integers for bar placement on the x-axis
            x_position = np.arange(len(x))
            bar_width = 0.4

            # If the user has a second y-axis variable
            if y2 is not None:

                # Dynamic min and max values based on the data with 5% cushion
                ymin = (min(y1[y1 > 0].min(), y2[y2 > 0].min()) * 0.95)
                ymax = max(y1.max(), y2.max()) * 1.05

                # Plotting the first variable
                ax.bar(x_position, y1, bar_width, label=y1_label)
                # Plotting the second variable next to the first
                ax.bar(
                    x_position + bar_width, y2, bar_width, label=y2_label,
                )

                # Sets ticks in the middle of the two bars
                ax.set_xticks(x_position + bar_width / 2)
                ax.set_xticklabels(x, rotation=60, fontsize=10)
                ax.set_ylim(ymin, ymax)

                ax.legend(loc="upper left", bbox_to_anchor=(0, 1), fontsize=8)

            else:
                ymin = y1.min() * 0.95
                ymax = y1.max() * 1.05

                ax.bar(x_position, y1, bar_width, label=y1)

                ax.set_xticks(x_position)
                ax.set_xticklabels(x, rotation=60, fontsize=10)
                ax.set_ylim(ymin, ymax)

            if title:
                ax.set_title(title, weight="bold", fontsize=16)

            if x_label:
                ax.set_xlabel(x_label, fontsize=14)

            if y1_label:
                ax.set_ylabel(y1_label, fontsize=14)

            # Displays figure if no axis is given
            if fig:
                plt.tight_layout()
                plt.show()

        except (ValueError, TypeError) as e:
            print(f"An error has occurred while creating bar graph: {e}")

    def create_line(self,
                    x_value,
                    y_value,
                    group_name=None,
                    x_label=None,
                    y_label=None,
                    title=None,
                    jitter=0.001,
                    ax=None,
                    figsize=(14, 6)):
        """
        Creates and displays a line graph from the dataset with customisable 
        formatting.

        Args:
            x_value (str): Variable name to be displayed across the x-axis.
            y_value (str): Varianle name to be displayed across the y-axis.
            group_name (str): Grouped variable to show multiple lines on
                the graph. Defaults to None.
            x_label (str): Label for the x-axis. Defaults to None.
            y_label (str): Label for the y-axus. Defaults to None.
            title (str): Title to be displayed above the graph.
                Defaults to None.
            jitter (float): Amount of movement to add to points to reduce
                overlap. Must be between 0 and 1. Defaults to 0.001.
        """
        try:
            plt.style.use("seaborn-v0_8-colorblind")
            # Doesnt plot the figure if it is for a subplot
            fig, ax = plt.subplots(
                figsize=figsize) if ax is None else (None, ax)

            if group_name:
                # Plots individual lines for each case in the group
                for member in self.data[group_name].unique():
                    member_data = self.data[self.data[group_name] == member]

                    y_values = member_data[y_value].values
                    # Jitters the y_axis for better seperation
                    jitter_y = y_values + \
                        np.random.uniform(-jitter, jitter,
                                          size=len(member_data))
                    # Plots the new jittered y-values
                    plt.plot(
                        member_data[x_value],
                        jitter_y,
                        label=member,
                        marker="o"
                    )
                    plt.legend(title=group_name, fontsize=12)
            else:
                # Jitters the y_axis for better seperation
                jitter_y = self.data[y_value] + \
                    np.random.uniform(-jitter, jitter, size=len(self.data))
                # Plots the new jittered y-values
                plt.plot(self.data[x_value], jitter_y,
                         marker="o")

            if title:
                plt.title(title, weight="bold", fontsize=16)

            if x_label:
                plt.xlabel(x_label, fontsize=14)

            if y_label:
                plt.ylabel(y_label, fontsize=14)

            # Dynamic limits for x and y-axis
            x_min = self.data[x_value].min()
            x_max = self.data[x_value].max()

            y_min = (self.data[y_value]).min() * 0.95
            y_max = (self.data[y_value]).max() * 1.05

            plt.xticks(np.arange(int(x_min), int(x_max) + 1), rotation=45)
            plt.ylim(y_min, y_max)
            plt.grid(False)

            # Displays figure if no axis is given
            if fig:
                plt.tight_layout()
                plt.show()
        except (ValueError, TypeError) as e:
            print(f"An error has occurred while creating line graph: {e}")

    def create_pie(self,
                   values,
                   labels,
                   figsize=(10, 6),
                   title=None,
                   ax=None):
        """
        Creates a pie chart based on the data given with customisable labels.

        Args:
            values (str): Dependent varaible name to be shown.
            labels (str): Independent variable name of the group.
            figsize (tuple, optional): Size of the figure (width, height). Defaults
                to (14, 6)
            title (str, optional): Title to display above the graph.
            ax (Matplotlib.axes, optional): A Matplotlib axes object for
                embedding the table into a subplot, if needed. Defaults to None.
        """
        plt.style.use("seaborn-v0_8-colorblind")
        fig, ax = plt.subplots(figsize=figsize) if ax is None else (None, ax)

        ax.pie(x=self.data[values], labels=self.data[labels])

        if title:
            ax.set_title(title, weight="bold", fontsize=16)

        plt.grid(False)

        # Displays figure if no axis is given
        if fig:
            plt.tight_layout()
            plt.show()


def valid_artist():
    """
    Prompts user to enter an artist; does not accept empty strings.

    Returns:
        str: A valid artist chosen by the user.
    """
    artist = str(input("Enter an artist you would like to analyse\n")).strip()
    if artist:
        return artist

    print("String cannot be empty. Please try again")
    return valid_artist()


def fetch_artist_data(db, artist):
    """
    Takes the selected artist and fetches genre-popularity data from the SQLite 
    database, along with the average overall genre-popularity.

    Args:
        db (str): SQLite database filepath with artist data.
        artist (str): Valid artist name to fetch data about.

    Returns:
        Pandas.DataFrame: A neat dataframe containing genres, artist popularity, and
            overall popularity from the chosen artist

    Raises:
        Exception: If any unexpected errors occur while executing any functions.
    """
    # Using DatabaseManager class
    db = dbm(db)
    # Converts artist name to a standard format for ease of searching
    artist = artist.lower().replace(" ", "")
    # Checks database to see if the name exists
    if db.check_db(value=artist, table="Artist", column="ArtistName"):
        try:
            sql_query = """
                SELECT
                    g.Genre,
                    AVG(CASE
                            WHEN LOWER(REPLACE(a.ArtistName, " ", "")) LIKE ?
                            THEN s.Popularity
                            ELSE NULL
                        END) AS Artist_Popularity,
                    AVG(s.Popularity) AS Overall_Popularity
                FROM Song s
                JOIN Artist a ON s.ArtistID = a.ID
                JOIN Song_genre sg ON s.ID = sg.SongID
                JOIN Genre g ON sg.GenreID = g.ID
                GROUP BY g.Genre
                ORDER BY Overall_Popularity ASC;
                """

            results = db.query(sql_query, params=(artist,))

            # Tidies the dataframe to make visualisation easier
            df = pd.DataFrame(results, columns=["Genre",
                                                "Artist Popularity",
                                                "Overall Popularity"])
            df["Genre"] = df["Genre"].str.title()
            # Replaces NAs with 0 and rounding to 2 d.p.
            df = df.fillna(0).round(2)

            return df

        except Exception as e:
            raise Exception(f"An unexpected error has occurred: {e}")

        finally:
            # Closing database connection
            db.close()
    else:
        print(f"{artist} cannot be found in the database.")


def format_table(df, artist):
    """
    Formats and displays a table of the fetched data, highlighting cells where
    'Artist Popularity' > 'Overall Popularity'.

    Args:
        df (Pandas.DataFrame): Tidied dataframe containing 'Genre', 'Artist
            Popularity', and 'Overall Popularity'.
        artist (str): Name of artist selected by the user.
    """
    # Conditional formatting to highlight when 'Artist Popularity' is larger than
    # 'Overall Popularity'
    conditions = [
        {
            "columns": [1],  # Column index for 'Artist Popularity'
            # Function to compare Artist and Overall Popularity
            "condition": lambda x, *row: x > row[2],
            "color": "#d4edda"  # Changes color to green if 'Artist' > 'Overall'
        },
        {
            "columns": [1],
            "condition": lambda x, *row: x < row[2],
            "color": "#f8d7da"  # Changes color to red if 'Overall' > 'Artist'
        }
    ]
    # Grey background for the 'Artist' column
    col_color = [{0: "#f2f2f2"}]

    Visualise(df).create_table(
        conditions=conditions, col_color=col_color,
        title=f"{artist.title()} Popularity vs Overall Popularity")


def format_graph(df, artist):
    """
    Formats and displays a bar graph comparing 'Artist Popularity' and 
    'Overall Popularity' per 'Genre'.

    Args:
        df (Pandas.DataFrame): Tidied dataframe containing 'Genre', 'Artist
            Popularity', and 'Overall Popularity'.
        artist (str): Name of artist selected by the user.
    """
    Visualise(df).create_bar(x_value="Genre",
                             y1_value="Overall Popularity",
                             y2_value="Artist Popularity",
                             x_label="Genres",
                             y1_label="Average Popularity",
                             y2_label="Artist",
                             title=f"{artist.title()} Popularity vs Overall Popularity")


def main():
    """
    Main function to orchestrate processes.
    """
    artist = valid_artist()

    df = fetch_artist_data(db, artist)

    if df.empty:
        raise ValueError(f"No data has been found for {artist}.")

    format_table(df, artist)
    format_graph(df, artist)


if __name__ == "__main__":
    db = "CWDatabase.db"
    main()
