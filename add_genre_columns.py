import csv

# Read the CSV file and collect all genres
all_genres = set()
rows = []
with open('data/movies_1900_2023.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='|')
    for row in reader:
        rows.append(row)
        if row['genres']:
            genres = [g.strip() for g in row['genres'].split(',')]
            all_genres.update(genres)

# Sort genres for consistent column order
sorted_genres = sorted(all_genres)

# Define new fieldnames
original_fields = ['title', 'year', 'extract', 'cast', 'genres', 'href', 'thumbnail', 'thumbnail_height', 'thumbnail_width']
fieldnames = original_fields + sorted_genres

# Process each row to add genre columns
for row in rows:
    movie_genres = set()
    if row['genres']:
        movie_genres = set(g.strip() for g in row['genres'].split(','))
    
    for genre in sorted_genres:
        row[genre] = '1' if genre in movie_genres else '0'

# Write the updated CSV
with open('data/movies_1900_2023.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='|')
    writer.writeheader()
    writer.writerows(rows)

print(f'Added {len(sorted_genres)} genre columns')
print(f'Total columns: {len(fieldnames)}')
