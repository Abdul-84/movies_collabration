import difflib
import json
import os
import re
import requests
import networkx as nx
from collections import defaultdict

def find_most_frequent_collaborators(G, person):
    if person not in G:
        suggestions = difflib.get_close_matches(person, G.nodes(), n=3, cutoff=0.5)
        if suggestions:
            return f"{person} not found. Did you mean: {', '.join(suggestions)}?"
        return f"{person} not found in the network."

    collaborators = [(neighbor, G[person][neighbor]) for neighbor in G.neighbors(person)]
    sorted_collabs = sorted(collaborators, key=lambda x: x[1]['weight'], reverse=True)[:5]
    output = [f"Top collaborators for {person}:\n"]

    for name, data in sorted_collabs:
        output.append(f"{name}")
        unique_movies = {}
        for movie in data.get("movies", []):
            unique_movies[movie] = unique_movies.get(movie, 0) + 1
        for movie, count in unique_movies.items():
            movie_display = f"{movie} (x{count})" if count > 1 else movie
            output.append(f"  ├── {movie_display}")
        output.append(f"  ↳ Total collaborations: {data['weight']}")

    return "\n".join(output)

def find_shortest_path_with_movies(G, source, target):
    try:
        path = nx.shortest_path(G, source=source, target=target)
        output = []
        for i in range(len(path) - 1):
            movies = G[path[i]][path[i+1]].get('movies', [])
            output.append(f"{path[i]} → {path[i+1]} (via {', '.join(movies)})")
        return "\n".join(output)
    except nx.NetworkXNoPath:
        return f"No path between {source} and {target}."
    except nx.NodeNotFound as e:
        return str(e)

def get_top_central_people(G, n=5):
    centrality = nx.degree_centrality(G)
    top_people = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:n]
    return "Top Central Figures:\n" + "\n".join([f"{person}: {score:.4f}" for person, score in top_people])

def get_movie_subgraph(G, movie_title_fragment):
    movie_title_fragment = movie_title_fragment.lower()
    nodes_to_include = set()
    for u, v, data in G.edges(data=True):
        for movie in data.get('movies', []):
            if movie_title_fragment in movie.lower():
                nodes_to_include.update([u, v])
    return G.subgraph(nodes_to_include).copy()

def detect_communities(G):
    from networkx.algorithms.community import greedy_modularity_communities
    communities = list(greedy_modularity_communities(G))
    result = []
    for i, comm in enumerate(communities[:5]):
        sample = list(comm)[:5]
        result.append(f"Community {i+1}: {', '.join(sample)}...")
    return "\n".join(result)

def list_all_people(G):
    with open("people_in_graph.txt", "w", encoding="utf-8") as f:
        for person in sorted(G.nodes()):
            role = G.nodes[person].get("job", "Unknown")
            bio = G.nodes[person].get("bio", "No bio available")
            snippet = bio if len(bio) <= 120 else bio[:117] + "..."
            f.write(f"{person} — {role} | {snippet}\n")
    return f"Saved list of people to 'people_in_graph.txt' with {len(G.nodes())} names."
