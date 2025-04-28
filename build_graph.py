import networkx as nx
from api.tmdb_api import get_movie_credits, get_movie_details

def build_collab_graph(movie_ids):
    G = nx.Graph()

    for movie_id in movie_ids:
        credits = get_movie_credits(movie_id)
        movie_details = get_movie_details(movie_id)

        if not credits or not movie_details:
            print(f"Skipping movie ID {movie_id} due to missing data.")
            continue

        genres = movie_details.get("genres", [])
        genre_names = [g["name"] for g in genres]
        movie_title = movie_details.get("title", f"Movie {movie_id}")
        release_year = movie_details.get("release_date", "")[:4]
        revenue = movie_details.get("revenue", 0)
        movie_label = f"{movie_title} ({release_year}, ${revenue:,})"

        people = []

        for person in credits.get("cast", []):
            people.append({**person, "job": "actor"})

        for person in credits.get("crew", []):
            if person.get("job") == "Director":
                people.append({**person, "job": "director"})

        G.add_node(movie_label, job="movie", genres=genre_names)

        for i, person1 in enumerate(people):
            name1 = person1.get("name")
            job1 = person1.get("job", "")
            G.add_node(name1, job=job1)

            for person2 in people[i+1:]:
                name2 = person2.get("name")
                if G.has_edge(name1, name2):
                    G[name1][name2]['weight'] += 1
                    G[name1][name2]['movies'].append(movie_label)
                else:
                    G.add_edge(name1, name2, weight=1, movies=[movie_label])

    return G
