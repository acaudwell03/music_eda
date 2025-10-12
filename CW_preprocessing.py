import sqlite3
import pandas as pd

"""
This program is designed to interact with an SQLite database and perform data preprocessing 
for song-related datasets. It imports data from a .csv file, cleans and filters the data, 
and then loads it into an SQLite database with structured tables.

Key Features:
- Data Importing: Import data from a .csv file.
- Data Cleaning: Filters and renames columns to meet specified criteria.
- Database Interaction: 
    - Creates tables in the SQLite database.
    - Inserts data into the tables.
    - Queries the database for specific information.
    - Checks if a value exists in the database.
"""


# Creating a class to deal with database interactions
class DataBaseManager:
    """
    A class for managing interactions with an SQLite database.
    """

    def __init__(self, db_name):
        """
        Establishes connection and cursor to the SQLite database.

        Attributes:
            connection (sqlite3.Connection): Connection for the database.
            cursor (sqlite.Cursor): Cursor to execute SQL queries.
        """
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def create_table(self, query):
        """
        Creates the tables in SQLite3 database.

        Args:
            query (str): Query to create table using standard SQL syntax.
                e.g. 'CREATE TABLE table_name (column1 datatype, column2 datatype, ...);'

        Raises:
            sqlite3.Error: If there is an issue connecting or interacting with the database.
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print(f"Table created successfully.")

        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def insert_data(self, query, data):
        """
        Used to insert data into SQL database.

        Args:
            query (str): Query to insert data into database using standard SQL syntax.
                e.g. '''INSERT INTO table_name (column1, column2, ...)
                        VALUES (value1, value2, ...);'''
            data (list): Data to be transferred into the database.

        Raises:
            ValueError: If table name does not exist in the database.
            sqlite3.Error: If there is an issue connecting or interacting with the database.
        """
        try:
            self.cursor.executemany(query, data)
            self.connection.commit()

        except ValueError as e:
            print(f"Table name does not exist in database: {e}")
        except sqlite3.Error as e:
            print(f"Error connecting or interacting with database: {e}")

    def query(self, query, params=None):
        """
        Communicates with the database for general SQL querying.

        Args:
            query (str): SQL query using standard SQL syntax. 
                e.g. '''SELECT * FROM table WHERE column1 = parameter1'''
            params (str, optional): Parameters that should be met to collect the desired
                data. Default set to None for no explicit parameters.
        Returns:
            tuple: A list or empty list of data collected from the database.

        """
        if params:
            return self.cursor.execute(query, params).fetchall()
        return self.cursor.execute(query).fetchall()

    def check_db(self, value, table, column):
        """
        Searches database for the existance of an object in the database.

        Args:
            table (str): The table in the database to search.
            column (str): The column of the table to search.
            value (str): The value to search for.

        Returns:
            bool: True if value is found, false if not.

        Raises:
            sqlite3.Error: If an error occurrs connecting to the database or 
                query execution
        """
        if isinstance(value, str):
            value = value.replace(" ", "").lower()

        if not table.isidentifier() or not column.isidentifier():
            raise ("Invalid table or column name")

        query = f"""
        SELECT COUNT(*)
        FROM {table}
        WHERE LOWER(REPLACE({column}, " ", "")) LIKE ?
        """
        result = self.cursor.execute(query, (value,)).fetchone()

        return result[0] > 0

    def close(self):
        """
        Closes the connection to the database.
        """
        self.connection.close()


def import_data(file_path):
    """
    Imports and cleans data from a .csv file.

    Args:
        file_path (str): Location of the CSV file.

    Returns:
        Pandas.DataFrame: Data from the .csv file.

    Raises:
        ValueError: If the file submitted is not a .csv format.
        FileNotFoundError: If the location of the file is not correct.
    """
    try:
        if file_path.endswith(".csv"):
            dfSongs = pd.read_csv(file_path)
            return dfSongs

    except ValueError:
        raise ValueError("Unsupported format. Please use a .csv file.")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")


def clean_data(data):
    """
    Cleans and filters data to meet criteria.

    Args:
        data (Pandas.DataFrame): Data frame to be cleaned and filtered.

    Returns:
        Pandas.DataFrame: Cleaned and filtered data.

    Raises:
        KeyError: If column name does not match the dataset
    """
    try:
        # Renaming columns to meet specification
        data.rename(columns={"duration_ms": "duration"}, inplace=True)
        data["duration"] = (data["duration"] / 1000).round()

        # Cleaning data based on criteria
        data = data[
            (data["popularity"] > 50)
            & (data["speechiness"] > 0.33)
            & (data["speechiness"] < 0.66)
            & (data["danceability"] > 0.2)
        ]
        return data

    except KeyError as e:
        raise KeyError(f"KeyError: Column name does not exist: {e}")


def extract_data(data):
    """
    Prepares data to be inserted into database based on specification.

    Args:
        data (pd.DataFrame): Cleaned dataset.

    Returns:
        lists: lists for songs, genre, artist, and song_genre relational tables.

    Raises:
        KeyError: If column name does not match dataset
    """
    # Selecting columns based on crtieria
    try:
        songs_data = data[
            [
                "song",
                "duration",
                "explicit",
                "year",
                "popularity",
                "danceability",
                "speechiness",
                "artist",
            ]
        ].values.tolist()

        # Creating a list of unique genres from the dataset
        genre_data = (
            data["genre"].str.split(
                ",").explode().str.strip().unique().tolist()
        )
        genre_data = [(genre,) for genre in genre_data]

        # Creating a list of unique artists from the dataset
        artist_data = (
            data["artist"].str.split(
                ",").explode().str.strip().unique().tolist()
        )
        artist_data = [(artist,) for artist in artist_data]

        # Creating unique song-genre mappings
        song_genre_data = list(
            set(
                (genre.strip(), song.strip())
                for song, genres in data[["song", "genre"]].values
                for genre in genres.split(",")
            )
        )
        return songs_data, genre_data, artist_data, song_genre_data

    except KeyError as e:
        raise KeyError(f"KeyError: Column name does not exist: {e}")


def main(file_path="songs.csv"):
    """
    Main function which orchestrates the process.

    Args:
        filepath (str): Location of .csv dataset. Defaults to songs.csv file.
    """

    # Retrieving and cleaning data
    dfSongs = import_data(file_path)
    dfSongs = clean_data(dfSongs)

    # Extracting data ready for insertion
    songs_data, genre_data, artist_data, song_genre_data = extract_data(
        dfSongs)

    # Table creation SQL queries as a dictionary
    table_queries = {
        "Song": """
    CREATE TABLE Song (
        ID INTEGER PRIMARY KEY,
        Song VARCHAR(50), 
        Duration INTEGER, 
        Explicit BOOL, 
        Year INTEGER, 
        Popularity INTEGER, 
        Danceability FLOAT, 
        Speechiness FLOAT,
        ArtistID INTEGER,
        FOREIGN KEY (ArtistID) REFERENCES Artist(ID)
        );
    """,
        "Genre": """
    CREATE TABLE Genre (
        ID INTEGER PRIMARY KEY,
        Genre VARCHAR(20)
        );
    """,
        "Artist": """
    CREATE TABLE Artist ( 
        ID INTEGER PRIMARY KEY, 
        ArtistName VARCHAR(20)
        );
    """,
        "Song_genre": """
    CREATE TABLE Song_genre (
        SongID INTEGER,
        GenreID INTEGER,
        FOREIGN KEY (SongID) REFERENCES Song(ID),
        FOREIGN KEY (GenreID) REFERENCES Genre(ID),
        PRIMARY KEY (SongID, GenreID)
        );
    """,
    }

    # Creating tables in the table dictionary
    for table_name, query in table_queries.items():
        print(f"Creating table: {table_name}")
        db.create_table(query)

    # Data insertion queries as a dictionary
    data_queries = {
        "Genre": (
            """
        INSERT INTO Genre (Genre)
        VALUES (?);
        """,
            genre_data,
        ),
        "Artist": (
            """
        INSERT INTO Artist (ArtistName)
        VALUES (?);
        """,
            artist_data,
        ),
        "Song": (
            """
        INSERT INTO Song (
        Song, Duration, Explicit, Year, Popularity, Danceability, Speechiness, ArtistID) 
        SELECT ?, ?, ?, ?, ?, ?, ?, (Select ID FROM Artist WHERE ArtistName = ?);
        """,
            songs_data,
        ),
        "Song_genre": (
            """
        INSERT INTO Song_genre (SongID, GenreID)
        SELECT DISTINCT s.ID, g.ID
        FROM Song s
        JOIN Genre g ON g.Genre = ?
        WHERE s.Song = ? 
        """,
            song_genre_data,
        ),
    }

    # Inserting the data based on the dictionary
    for table_name, (insert_query, data) in data_queries.items():
        db.insert_data(insert_query, data)

    # Closing database connection
    db.close()


# Executing functions
if __name__ == "__main__":
    # Database name in the directory
    db = DataBaseManager("CWDatabase.db")
    main()
