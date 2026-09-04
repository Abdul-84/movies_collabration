#!/bin/bash

PROJECT_DIR="/Volumes/sd/GitHub_ Repository/movies_collabration"

# Create the main project folder if it doesn't exist
mkdir -p "$PROJECT_DIR"

# Navigate into the project folder
cd "$PROJECT_DIR" || exit 1

# Create subfolders
mkdir -p api
mkdir -p data
mkdir -p lib
mkdir -p graphs

# Create empty Python scripts with proper names
touch api/tmdb_api.py
touch api/omdb_api.py
touch api/api_metadata_fetcher.py
touch build_graph.py
touch main.py
touch analysis.py

# Create requirements.txt
cat <<EOL > requirements.txt
networkx
pyvis
pandas
requests
matplotlib
EOL

# Create setup scripts
touch setup_movie.sh
touch cleanup.sh

# Create empty README
touch README.md

# Optional: Create people and top actors text files
touch people_in_graph.txt
touch top_actors.txt

echo "✅ Created folder structure and base files in $PROJECT_DIR!"

# Assume you already manually placed these into $PROJECT_DIR/data/
# - movies_long.csv
# - movies_short.dat

# Optional: Conversion command (if you are starting from .dat manually)
# echo "Converting .dat files to CSV format..."
# awk -F '::' 'BEGIN {OFS=","} {print $1, "\"" $2 "\"", "\"" $3 "\""}' movies.dat > data/movies.csv
# awk -F '::' 'BEGIN {OFS=","} {print $1, $2, $3, $4}' ratings.dat > data/ratings.csv
# awk -F '::' 'BEGIN {OFS=","} {print $1, $2, $3, $4, $5}' users.dat > data/users.csv

# echo "✅ Converted MovieLens .dat files to CSVs!"

echo "✅ Setup complete. Now you can start coding in $PROJECT_DIR!"
