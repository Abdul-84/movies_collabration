#!/bin/bash

# Create the main project folder if it doesn't exist
mkdir -p ~/Desktop/movies_project

# Navigate into the project folder
cd ~/Desktop/movies_project

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

echo "✅ Created folder structure and base files for movies_project!"

# Assume you already manually placed these into ~/Desktop/movies_project/data/
# - movies_long.csv
# - movies_short.dat

# Optional: Conversion command (if you are starting from .dat manually)
# echo "Converting .dat files to CSV format..."
# awk -F '::' 'BEGIN {OFS=","} {print $1, "\"" $2 "\"", "\"" $3 "\""}' movies.dat > data/movies.csv
# awk -F '::' 'BEGIN {OFS=","} {print $1, $2, $3, $4}' ratings.dat > data/ratings.csv
# awk -F '::' 'BEGIN {OFS=","} {print $1, $2, $3, $4, $5}' users.dat > data/users.csv

# echo "✅ Converted MovieLens .dat files to CSVs!"

echo "✅ Setup complete. Now you can start coding in ~/Desktop/movies_project!"
