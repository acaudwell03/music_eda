# Music_Exploration
This project was completed during my MSc Data Science degree. It involves taking a dataset from Kaggle about songs from 1998-2020 and creating functions to make changes, explore, and visualise different elementes of the dataset.

Files include:
* **Top5.py**: Fetches and processes data from a database, calculates rankings 
for artists based on popularity, danceability, and other factors, and visualizes 
the results as tables and graphs for a specified year range (1998-2020)
* **menu.ipynb**: Provides an interactive interface to explore music data from an SQLite database. Users can check if the database exists, then fetch data on music genres, artists, and top 5 artists over selected years
* **Genres.py**: Retrieves and visualises genre-related music statistics from an SQLite database 
for a user-specified year between 1998 and 2020
* **Artist.py**: Fetches, processes, and visualizes data related to an artist's music genre popularity
and compares it with overall genre popularity
* **CW_preprocessing.py**: Designed to interact with an SQLite database and perform data preprocessing 
for song-related datasets
* **CWDatabase.db**: SQLite3 database to store song data
* **songs.csv**: Initial dataste from Kaggle.com
