#!/bin/bash

# cleanup_project.sh
# A safe cleanup script for your movies_project folder

# Delete __pycache__ folders
find . type d -name "__pycache__" -exec rm -r {} +

# Delete temp files
rm -f tempCodeRunnerFile.py

# Delete unwanted HTML outputs
rm -f collaboration_network.html
rm -f person_info.html
rm -f __pychache__/*

# Remove lib/ folder if you confirm it's not needed
rm -rf lib

# (Optional) Remove heavy old datasets if not needed
# Uncomment the lines below if you want
# rm -rf ml-1m
# rm -rf ml-32m

# Remove any extra backup scripts if duplicated
rm -f requirement.sh

# Re-confirm
echo "✅ Cleanup completed successfully! Your project folder is clean."

# Reminder
echo "👉 Reminder: Only the essential folders remain: api/, data/, main.py, build_graph.py, analysis.py, requirements.txt, setup_movie.sh, and README.md."

