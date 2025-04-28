#!/bin/bash

# Create the main project folder if it doesn't exist
mkdir -p ~/Desktop/movie_len

# Navigate into the project folder
cd ~/Desktop/movie_len

# Create subfolders
mkdir -p api
mkdir -p data

# Create empty Python scripts with NEW names
touch api/tmdb_fetcher.py
touch api/omdb_fetcher.py
touch api/api_unified_fetcher.py
touch build_movie_network.py
touch analyze_movie_network.py
touch run_movie_app.py

# Create requirements.txt
cat <<EOL > requirements.txt
networkx
pyvis
pandas
requests
matplotlib
EOL

# Create empty README
touch README.md

# Assume you already manually placed these into ~/Desktop/movie_len/
# - movies.dat
# - ratings.dat
# - users.dat

# Convert the .dat files to .csv properly
echo "Converting MovieLens .dat files to CSV format..."

# Convert the .dat files into .csv
awk -F '::' 'BEGIN {OFS=","} {print $1, "\"" $2 "\"", "\"" $3 "\""}' movies.dat > data/movies.csv
awk -F '::' 'BEGIN {OFS=","} {print $1, $2, $3, $4}' ratings.dat > data/ratings.csv
awk -F '::' 'BEGIN {OFS=","} {print $1, $2, $3, $4, $5}' users.dat > data/users.csv

# Clean up
rm movies.dat ratings.dat users.dat
# Cleanup unnecessary .dat files after conversion (optional)
rm movies.dat ratings.dat users.dat

echo "✅ Project movie_len is fully setup in ~/Desktop/movie_len!"
