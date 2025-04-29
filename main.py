# Required imports for API calls, graph construction, and visualization
from api.api_metadata_fetcher import get_movie_metadata, get_person_metadata
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt
import os
from build_graph import build_collab_graph
from analysis import (
    find_most_frequent_collaborators,
    find_shortest_path_with_movies,
    get_movie_subgraph,
)
from collections import Counter
import random
from networkx.algorithms.community import greedy_modularity_communities
from datetime import datetime
import platform
import requests

# Fetches metadata(title, poster, and other information) about a movie using TMDB API, besides handles API calls and exceptions
def get_movie_metadata(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "id": data.get("id"),
                "title": data.get("title"),
                "overview": data.get("overview"),
                "poster_path": data.get("poster_path"),
                "backdrop_path": data.get("backdrop_path"),
                "production_companies": data.get("production_companies", []),
            }
        else:
            print(f"Error fetching movie metadata: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching movie metadata: {e}")
        return None

# Entry point of the program, to show the menu and guides user interaction.
def main():
    print("\n=== Collaboration Network Project ===")
    print("Loading recommended dataset (short list)...")
    dataset_path = "data/movies_short.dat"
    print("Loaded short movie list.")

    movie_ids = list(
        set(
            [
                550,     # Fight Club (1999)
                680,     # Pulp Fiction (1994)
                13,      # Forrest Gump (1994) 
                299536,  # Avengers: Infinity War (2018)
                24428,   # The Avengers (2012)
                99861,
                118340,
                76341,
                76342,
                157336,
                27205,
                1572,
                671,
                122,
                578,
                637,
                603,
                238,
                240,
                278,
                424,
                155,
                272,
                807,
                68718,
                120,
                185,
                122917,
                27206,
            ]
        )
    )
    random.seed(17)
    movie_ids = random.sample(movie_ids, min(15, len(movie_ids)))
    G = build_collab_graph(movie_ids)

    movie_cache = {}
    person_cache = {}
# To check if the poster image URL is working
    def is_valid_image_url(url):
        try:
            response = requests.head(url, timeout=3)
            return response.status_code == 200 and "image" in response.headers.get(
                "Content-Type", ""
            )
        except:
            return False
# To Display the collaboration network visually
    def visualize_graph(G, custom_title=None):
        from pyvis.network import Network
        import os
        if G.number_of_nodes() > 50:
            print(
                f" Large graph with {G.number_of_nodes()} nodes. Filtering top 50 most connected..."
            )
            top_nodes = sorted(G.nodes, key=lambda x: G.degree(x), reverse=True)[:50]
            G = G.subgraph(top_nodes).copy()
        net = Network(height="100vh", width="100%", bgcolor="white", font_color="black")
        if custom_title:
            net.heading = custom_title
        else:
            net.heading = "Collaboration Network"
        net.barnes_hut()
        net.set_options("""
        {
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -30000,
              "centralGravity": 0.3,
              "springLength": 100,
              "springConstant": 0.01,
              "damping": 0.4
            },
            "minVelocity": 0.75
          }
        }
        """)
        for node, data in G.nodes(data=True):
            role = data.get("job", "Unknown")
            label = node
            group = role if role in ["actor", "director", "movie"] else "other"
            title = label
            if role == "movie":
                if label in movie_cache:
                    meta = movie_cache[label]
                else:
                    meta = get_movie_metadata(label)
                    movie_cache[label] = meta
                poster = (
                    f"https://image.tmdb.org/t/p/w500{meta['poster_path']}"
                    if meta and meta.get("poster_path")
                    else None
                )
                backdrop = (
                    f"https://image.tmdb.org/t/p/w780{meta['backdrop_path']}"
                    if meta and meta.get("backdrop_path")
                    else None
                )
                if meta:
                    plot = meta.get("overview", "No plot available.")
                    clean_plot = plot.replace("'", "").replace('"', "")
                    if backdrop:
                        background_style = f"background:url({backdrop}) no-repeat center top; background-size:cover;"
                    else:
                        background_style = "background:#fff;"
                    title = (
                        f"<div style='text-align:left; {background_style} border:1px solid #ccc; padding:10px; width:200px; font-size:11px; "
                        f"box-shadow:2px 2px 5px rgba(0,0,0,0.1); border-radius:8px;'>"
                        f"<img src='{poster}' width='160' style='display:block; margin:auto; border-radius:8px; box-shadow:0 0 3px rgba(0,0,0,0.3);'>"
                        f"<div style='background:rgba(255,255,255,0.85); padding:10px; margin-top:8px;'>"
                        f"<div style='font-weight:bold;'>{label}</div>"
                        f"<div style='font-size:10px;'>{clean_plot[:200]}...</div>"
                        f"</div></div>"
                    )
                    net.add_node(
                        node,
                        label=" ",
                        shape="circularImage"
                        if poster and is_valid_image_url(poster)
                        else "ellipse",
                        image=poster if poster and is_valid_image_url(poster) else None,
                        group=group,
                        title=title,
                    )
                else:
                    net.add_node(node, label=label, group=group, title=title)
            elif role in ["actor", "director"]:
                if label in person_cache:
                    person_meta = person_cache[label]
                else:
                    person_meta = get_person_metadata(label)
                    person_cache[label] = person_meta
                if person_meta:
                    bio = person_meta.get("bio", "No bio available.")
                    image = person_meta.get("image")
                    clean_bio = bio.replace("\n", " ").replace("'", "")
                    if not image or not is_valid_image_url(image):
                        image = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/200px-No_image_available.svg.png"
                    title = (
                        f"<div style='text-align:left; border:1px solid #ccc; padding:6px; width:180px; font-size:11px; background:#f9f9f9; "
                        f"box-shadow:2px 2px 5px rgba(0,0,0,0.1); border-radius:6px;'>"
                        f"<img src='{image}' width='80' style='display:block; margin:5px auto 10px auto; border-radius:50%; box-shadow:0 0 3px rgba(0,0,0,0.3);'><br/>"
                        f"<table style='font-size:11px; width:100%; border-collapse:collapse;'>"
                        f"<tr><td style='padding-right:4px;'><strong>Name:</strong></td><td>{label}</td></tr>"
                        f"<tr><td style='padding-right:4px;'><strong>Bio:</strong></td><td>{clean_bio[:120]}...</td></tr>"
                        f"</table></div>"
                    )
                    net.add_node(
                        node,
                        label=" ",
                        shape="circularImage",
                        image=image,
                        group=group,
                        title=title,
                    )
                else:
                    net.add_node(node, label=label, group=group, title=title)
            else:
                net.add_node(node, label=label, group=group, title=title)
        for u, v, data in G.edges(data=True):
            movie_titles = ", ".join(data.get("movies", []))
            net.add_edge(u, v, title=movie_titles)
        net.html += """
        <div style="position:absolute;top:10px;right:10px;background:white;padding:10px;border:1px solid #ccc;">
          <h4>Legend</h4>
          <table style="font-size:12px;">
            <tr><td style="background-color:lightblue;width:20px;height:20px;"></td><td>Actor</td></tr>
            <tr><td style="background-color:lightgreen;width:20px;height:20px;"></td><td>Director</td></tr>
            <tr><td style="background-color:orange;width:20px;height:20px;"></td><td>Movie</td></tr>
          </table>
          <hr>
          <h4>Top Collaborators for Tom Hanks</h4>
          <ul style="font-size:12px;padding-left:20px;">
            <li><strong>Robin Wright</strong><br/><small>Forrest Gump (1994, $677,387,716) (x2) - Total: 2</small></li>
            <li><strong>Gary Sinise</strong><br/><small>Forrest Gump (1994, $677,387,716) (x2) - Total: 2</small></li>
            <li><strong>Sally Field</strong><br/><small>Forrest Gump (1994, $677,387,716) (x2) - Total: 2</small></li>
            <li><strong>Mykelti Williamson</strong><br/><small>Forrest Gump (1994, $677,387,716) (x2) - Total: 2</small></li>
            <li><strong>Michael Conner Humphreys</strong><br/><small>Forrest Gump (1994, $677,387,716) (x2) - Total: 2</small></li>
          </ul>
        </div>
        """
        path = os.path.abspath("collaboration_network.html")
        net.write_html(path)
        if platform.system() == "Darwin":
            os.system(f"open {path}")
        elif platform.system() == "Windows":
            os.system(f"start {path}")
        elif platform.system() == "Linux":
            os.system(f"xdg-open {path}")
        print(f" Graph written to {path}")

    while True:
        print("\nOptions:")
        print("1. Most Frequent Collaborators")
        print("2. Connection Path Between Two People")
        print("3. View Collaboration Network for a Movie")
        print("4. List Top Actors, Directors, or Genres")
        print("5. Visualize Top 20 Star Collaborators")
        print("6. Search for a Person (Bio & Image)")
        print("7. Export Top 10 Actors by Connections")
        print("8. Detect and Visualize Collaboration Clusters")
        print("9. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            name_input = input("Enter person's name: ").strip().lower()
            matched_people = [n for n in G.nodes if name_input in n.lower()]

            if matched_people:
                print("\nFound matching people:")
                for idx, person in enumerate(matched_people, 1):
                    print(f"{idx}. {person}")

                selected = input("\nSelect person number: ").strip()
                if selected.isdigit() and 1 <= int(selected) <= len(matched_people):
                    selected_person = matched_people[int(selected) - 1]
                    print(find_most_frequent_collaborators(G, selected_person))
                    subgraph = G.subgraph(
                        [selected_person] + list(G.neighbors(selected_person))
                    )
                    visualize_graph(subgraph)
                else:
                    print("Invalid selection.")
            else:
                print(f"No matching people found for '{name_input}'.")

        elif choice == "2":
            source = input("Start person: ").strip().lower()
            target = input("End person: ").strip().lower()
            matched_source = [n for n in G.nodes if n.lower() == source]
            matched_target = [n for n in G.nodes if n.lower() == target]
            if matched_source and matched_target:
                try:
                    path = nx.shortest_path(
                        G, source=matched_source[0], target=matched_target[0]
                    )
                    print("Connection Path Found:")
                    for idx, node in enumerate(path):
                        print(f"{idx + 1}. {node}")
                    subgraph = G.subgraph(path)
                    visualize_graph(subgraph)
                except nx.NetworkXNoPath:
                    print("No connection found.")
            else:
                print("Names not found.")

        elif choice == "3":
            title = input("Enter movie title: ").strip().lower()
            matches = [
                n
                for n, d in G.nodes(data=True)
                if d.get("job", "").lower() == "movie" and title in n.lower()
            ]
            if matches:
                print("Found matches:")
                for idx, m in enumerate(matches, 1):
                    print(f"{idx}. {m}")
                selected = int(input("Select number: ")) - 1
                selected_movie = matches[selected]
                neighbors = list(G.neighbors(selected_movie))
                level_2 = set()
                for neighbor in neighbors:
                    level_2.update(G.neighbors(neighbor))
                all_nodes = set(neighbors) | level_2 | {selected_movie}
                subgraph = G.subgraph(all_nodes)
                visualize_graph(subgraph)
            else:
                print("No movie found.")

        elif choice == "4":
            print(
                "List Options:\n1. Top 5 Movies for an Actor\n2. Top 5 Movies for a Director\n3. Top 5 Movies per Genre by Income"
            )
            list_choice = input("Select an option: ")
            if list_choice == "1":
                actor = input("Enter actor's name: ").strip().lower()
                matched_actor = [
                    n
                    for n in G.nodes
                    if n.lower() == actor and G.nodes[n].get("job", "") == "actor"
                ]
                if matched_actor:
                    neighbors = [
                        n
                        for n in G.neighbors(matched_actor[0])
                        if G.nodes[n].get("job", "") == "movie"
                    ]
                    if neighbors:
                        print(f"Top 5 Movies for {matched_actor[0]}:")
                        for movie in neighbors[:5]:
                            print(f"- {movie}")
                    else:
                        print("No movies found for that actor.")
                else:
                    print("Actor not found.")
            elif list_choice == "2":
                director = input("Enter director's name: ").strip().lower()
                matched_director = [
                    n
                    for n in G.nodes
                    if n.lower() == director and G.nodes[n].get("job", "") == "director"
                ]
                if matched_director:
                    neighbors = [
                        n
                        for n in G.neighbors(matched_director[0])
                        if G.nodes[n].get("job", "") == "movie"
                    ]
                    if neighbors:
                        print(f"Top 5 Movies for {matched_director[0]}:")
                        for movie in neighbors[:5]:
                            print(f"- {movie}")
                    else:
                        print("No movies found for that director.")
                else:
                    print("Director not found.")
            elif list_choice == "3":
                print("Feature not yet implemented.")
            else:
                print("Invalid selection.")

        elif choice == "5":
            actors = [
                n for n, d in G.nodes(data=True) if "actor" in d.get("job", "").lower()
            ]
            directors = [
                n
                for n, d in G.nodes(data=True)
                if d.get("job", "").lower() == "director"
            ]
            top_actors = sorted(actors, key=lambda name: G.degree(name), reverse=True)[
                :20
            ]
            top_directors = sorted(
                directors, key=lambda name: G.degree(name), reverse=True
            )[:20]
            nodes_to_keep = set(top_actors) | set(top_directors)
            for node in list(nodes_to_keep):
                neighbors = G.neighbors(node)
                for nbr in neighbors:
                    if G.nodes[nbr].get("job") == "movie":
                        nodes_to_keep.add(nbr)
            G_sub = G.subgraph(nodes_to_keep)
            visualize_graph(G_sub)

        elif choice == "6":
            name = input("Enter person's name: ").strip().lower()
            matched_names = [n for n in G.nodes if n.lower() == name]
            display_name = matched_names[0] if matched_names else name
            meta = get_person_metadata(display_name)
            bio = meta.get("bio", "No bio available.")
            image = meta.get(
                "image",
                "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/200px-No_image_available.svg.png",
            )
            clean_bio = bio.replace("\n", " ").replace("'", "")
            html_content = f"""
            <html>
            <head><title>Person Info</title></head>
            <body style="font-family:sans-serif;">
              <div style='text-align:center; margin-top:50px;'>
                <h2>{display_name}</h2>
                <img src="{image}" width="200" style="border-radius:10px;"><br><br>
                <div style="width:60%; margin:auto; border:1px solid #ccc; padding:15px; text-align:left;">
                  <p style="font-size:14px;">{clean_bio}</p>
                </div>
              </div>
            </body>
            </html>
            """
            with open("person_info.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("Bio and image saved as 'person_info.html'!")
            if platform.system() == "Darwin":
                os.system(f"open person_info.html")
            elif platform.system() == "Windows":
                os.system(f"start person_info.html")
            elif platform.system() == "Linux":
                os.system(f"xdg-open person_info.html")

        elif choice == "7":
            actors = [
                n for n, d in G.nodes(data=True) if "actor" in d.get("job", "").lower()
            ]
            top_10 = sorted(actors, key=lambda name: G.degree(name), reverse=True)[:10]
            print("Top 10 Actors:")
            for actor in top_10:
                print(actor)

        elif choice == "8":
            communities = list(greedy_modularity_communities(G))
            if communities:
                large_communities = [c for c in communities if len(c) > 2]
                if not large_communities:
                    print("No large communities detected. Showing any available community instead.")
                    selected_community = random.choice(communities)
                else:
                    selected_community = random.choice(large_communities)

                print(f"Randomly selected community with {len(selected_community)} nodes!")
                G_sub = G.subgraph(selected_community)

                net_title = f"Random Collaboration Community - {len(selected_community)} Nodes"
                visualize_graph(G_sub, custom_title=net_title)
            else:
                print("No communities detected.")

        elif choice == "9":
            confirm = input("Are you sure you want to exit? (y/n): ").strip().lower()
            if confirm == "y":
                print("Goodbye!")
                break
        else:
            print("Invalid choice. Please select from the menu.")


if __name__ == "__main__":
    main()
