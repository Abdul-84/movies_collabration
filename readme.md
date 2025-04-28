Final Project Report: Movie Collaboration Network  --- Date(04-28-2025)

Project Overview

For my final project, I built a Movie Collaboration Network that maps the relationships between actors, directors, and movies.
My goal was to explore how professional relationships in the film industry connect individuals across different projects, and to understand how collaboration patterns might impact success.

By visualizing these networks, users can explore:
	•	Who are the most central people in the industry?
	•	How closely are actors and directors interconnected?
	•	Are there shortcuts between distant collaborators?

⸻

Dataset and APIs Used

I combined APIs and local CSV data to construct the network:
	•	TMDb API: (The Movie Database) – Used for movie metadata, cast, crew, and poster images.
         Link: https://developer.themoviedb.org/docs/getting-started
	•	OMDb API: (Open Movie Database) – Used as a backup for additional movie information.
         Link: https://www.omdbapi.com
	•	MovieLens CSV Files:
         Link: https://grouplens.org/datasets/movielens/latest/
	•	movies_short.dat – A small, fast-loading list for testing.
	•	movies_long.csv – A larger file for deeper analysis.

Data collected includes:
	•	Movie titles and posters
	•	Director and actor names
	•	Collaboration relationships
	•	Movie overviews (where available)

Data is cached locally in a file (movie_cache.json) to improve performance for future runs.

⸻

User Interaction

The program provides a command-line interface with nine options for users to explore the collaboration network:
	1.	Most Frequent Collaborators:
        View the top collaborators for a specific actor or director, including movies they’ve worked on.
	2.	Connection Path Between Two People:
        Find the shortest collaboration path between two individuals across different movies.
	3.	View Collaboration Network for a Movie:
        Visualize all the people connected through a single movie.
	4.	List Top Actors, Directors, or Genres:
        Display the top collaborators based on profession or genre (this option needs refinement).
	5.	Visualize Top 20 Star Collaborators:
        Show an interactive network graph of the top 20 most-connected individuals.
	6.	Search for a Person (Bio & Image):
        Retrieve a short biography and image for an actor or director.
	7.	Export Top 10 Actors by Connections:
        Generate a list of the top actors based on the number of collaborations.
	8.	Detect and Visualize Collaboration Clusters:
        Detect communities within the network and visualize random clusters interactively.
	9.	Exit:
        Safely close the program.

⸻

Findings
	•	Highly collaborative actors and directors form tightly-knit communities.
	•	Some collaborations occur indirectly through shared connections rather than direct work.
	•	Well-known figures typically have larger networks, acting as hubs.
	•	Random collaboration clusters reveal hidden industry relationships.

⸻

Additional Notes
	•	Graphs are generated using NetworkX and visualized with PyVis.
	•	Graphs are automatically saved in the /graphs folder with a timestamped filename.
	•	Movie posters and biographies are fetched live but cached locally to improve load speed.
	•	Some missing data is unavoidable due to incomplete API entries.

⸻

Screenshots, project structure diagrams, and full working code are included in the repository.
