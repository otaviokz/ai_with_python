import csv
import sqlite3

# Read the CSV file
rows = []
with open('data/movies_1900_2023.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='|')
    fieldnames = reader.fieldnames
    for row in reader:
        rows.append(row)

# Get genre column names (all columns except the base ones)
base_columns = ['title', 'year', 'extract', 'cast', 'href', 'thumbnail', 'thumbnail_height', 'thumbnail_width']
genre_columns = [f for f in fieldnames if f not in base_columns]

# Extract unique artists
all_artists = set()
for row in rows:
    if row['cast']:
        artists = [a.strip() for a in row['cast'].split(',')]
        all_artists.update(artists)

all_artists = sorted(all_artists)
genres_list = sorted(genre_columns)

print(f'Found {len(all_artists)} unique artists')
print(f'Found {len(genres_list)} genres')

# Create SQLite database
conn = sqlite3.connect('data/movies.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        year INTEGER,
        extract TEXT,
        href TEXT,
        thumbnail TEXT,
        thumbnail_height INTEGER,
        thumbnail_width INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS artists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS genres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS movie_artists (
        movie_id INTEGER,
        artist_id INTEGER,
        FOREIGN KEY (movie_id) REFERENCES movies(id),
        FOREIGN KEY (artist_id) REFERENCES artists(id),
        PRIMARY KEY (movie_id, artist_id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS movie_genres (
        movie_id INTEGER,
        genre_id INTEGER,
        FOREIGN KEY (movie_id) REFERENCES movies(id),
        FOREIGN KEY (genre_id) REFERENCES genres(id),
        PRIMARY KEY (movie_id, genre_id)
    )
''')

# Insert artists
for artist in all_artists:
    cursor.execute('INSERT OR IGNORE INTO artists (name) VALUES (?)', (artist,))

# Insert genres
for genre in genres_list:
    cursor.execute('INSERT OR IGNORE INTO genres (name) VALUES (?)', (genre,))

# Create artist and genre name to id mappings
cursor.execute('SELECT id, name FROM artists')
artist_map = {name: id for id, name in cursor.fetchall()}

cursor.execute('SELECT id, name FROM genres')
genre_map = {name: id for id, name in cursor.fetchall()}

# Insert movies and relationships
for row in rows:
    # Insert movie
    cursor.execute('''
        INSERT INTO movies (title, year, extract, href, thumbnail, thumbnail_height, thumbnail_width)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        row['title'],
        int(row['year']) if row['year'] else None,
        row.get('extract', ''),
        row.get('href', ''),
        row.get('thumbnail', ''),
        int(row['thumbnail_height']) if row.get('thumbnail_height') else None,
        int(row['thumbnail_width']) if row.get('thumbnail_width') else None
    ))
    
    movie_id = cursor.lastrowid
    
    # Link artists
    if row['cast']:
        artists = [a.strip() for a in row['cast'].split(',')]
        for artist in artists:
            if artist in artist_map:
                cursor.execute('INSERT OR IGNORE INTO movie_artists (movie_id, artist_id) VALUES (?, ?)',
                             (movie_id, artist_map[artist]))
    
    # Link genres
    for genre in genre_columns:
        if row[genre] == '1':
            cursor.execute('INSERT OR IGNORE INTO movie_genres (movie_id, genre_id) VALUES (?, ?)',
                         (movie_id, genre_map[genre]))

conn.commit()

# Print statistics
cursor.execute('SELECT COUNT(*) FROM movies')
movie_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM artists')
artist_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM genres')
genre_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM movie_artists')
movie_artist_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM movie_genres')
movie_genre_count = cursor.fetchone()[0]

print(f'\nDatabase created successfully!')
print(f'Movies: {movie_count}')
print(f'Artists: {artist_count}')
print(f'Genres: {genre_count}')
print(f'Movie-Artist relationships: {movie_artist_count}')
print(f'Movie-Genre relationships: {movie_genre_count}')

conn.close()
