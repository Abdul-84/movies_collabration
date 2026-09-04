# Movie Collaboration Network

A Python network-analysis project that maps how actors, directors, and movies connect through shared work. The project builds a weighted collaboration graph, lets users explore relationships from the command line, and exports visual network graphs for easier discovery.

<p>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3" />
  <img src="https://img.shields.io/badge/NetworkX-Graph%20Analysis-1f6feb?style=for-the-badge" alt="NetworkX graph analysis" />
  <img src="https://img.shields.io/badge/PyVis-Interactive%20Graphs-238636?style=for-the-badge" alt="PyVis interactive graphs" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-8a63d2?style=for-the-badge" alt="GPL-3.0 license" />
</p>

![Collaboration network preview](Collaboration%20Network.png)

## Why This Project Exists

Movie credits contain a lot of hidden structure. Two actors may be directly connected by one movie, or indirectly connected through a chain of shared collaborators. This project turns that information into a graph so those patterns are easier to inspect.

The project explores questions such as:

- Which actors and directors are highly connected?
- Who collaborates repeatedly across different movies?
- What is the shortest collaboration path between two people?
- Which communities appear naturally inside the movie network?

## Features

- Build a collaboration graph from selected movie IDs.
- Add actors, directors, and movie metadata from TMDb and OMDb-style sources.
- Find the most frequent collaborators for a selected person.
- Find shortest collaboration paths between two people, including the movies that connect them.
- Visualize the network for a single movie.
- Export top actors by number of connections.
- Detect collaboration communities and export interactive PyVis graph views.
- Cache metadata locally so repeated runs are faster.

## Screenshots

### Full Collaboration Network

![Full collaboration network](Collaboration%20Network.png)

### Random Collaboration Community

![Random collaboration community](Random%20Collaboration%20Community.png)

## Tech Stack

- Python
- NetworkX
- PyVis
- pandas
- requests
- matplotlib
- TMDb API
- OMDb API

## Project Structure

```text
.
├── api/                    # API helpers for TMDb and OMDb metadata
├── data/                   # Local movie data used by the project
├── analysis.py             # Graph analysis helpers
├── build_graph.py          # Collaboration graph builder
├── main.py                 # Command-line interface and visualization flow
├── requirements.txt        # Python dependencies
├── top_actors.txt          # Example exported output
└── people_in_graph.txt     # Example generated people list
```

## Setup

1. Clone the repository.

```bash
git clone https://github.com/Abdul-84/movies_collabration.git
cd movies_collabration
```

2. Create and activate a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Configure API keys.

Create local environment variables before running the app. Do not commit real API keys.

```bash
export TMDB_API_KEY="your_tmdb_api_key"
export OMDB_API_KEY="your_omdb_api_key"
```

You can use `.env.example` as a reference for the required names.

5. Run the project.

```bash
python main.py
```

## Menu Options

When the program starts, it opens a command-line menu for exploring the graph:

1. View the most frequent collaborators for a person.
2. Find a connection path between two people.
3. View the collaboration network for a movie.
4. List top actors, directors, or genres.
5. Visualize the top star collaborators.
6. Search for a person biography and image.
7. Export the top actors by number of connections.
8. Detect and visualize collaboration clusters.
9. Exit the program.

## Notes

- Some movie records may be incomplete depending on API coverage.
- Generated graph files and cache files are local run artifacts.
- API keys should be stored locally as environment variables.
- If keys were committed previously, rotate them in the provider dashboards before continuing development.

## License

This project is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE) for details.
