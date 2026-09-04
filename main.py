import html
import os
import platform
import random
import re
import subprocess

import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
from pyvis.network import Network

from api.tmdb_api import get_person_metadata
from analysis import find_most_frequent_collaborators
from build_graph import build_collab_graph


def open_generated_file(path):
    if os.getenv("MOVIE_GRAPH_OPEN") == "0":
        return

    system = platform.system()
    if system == "Darwin":
        subprocess.run(["open", path], check=False)
    elif system == "Windows":
        os.startfile(path)
    elif system == "Linux":
        subprocess.run(["xdg-open", path], check=False)


def clean_text(value, fallback="Not available"):
    text = str(value or "").replace("\n", " ").strip()
    return text or fallback


def truncate_text(value, limit=280):
    text = clean_text(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def tmdb_image_url(path, size="w342"):
    if not path:
        return None
    if str(path).startswith("http"):
        return path
    return f"https://image.tmdb.org/t/p/{size}{path}"


def money(value):
    try:
        amount = int(value or 0)
    except (TypeError, ValueError):
        return "Not available"
    return f"${amount:,}" if amount > 0 else "Not available"


def is_person_node(data):
    return data.get("job") in {"actor", "director"}


def find_people(G, query, exact=False):
    query = query.strip().lower()
    if not query:
        return []
    return [
        name
        for name, data in G.nodes(data=True)
        if is_person_node(data)
        and (name.lower() == query if exact else query in name.lower())
    ]


def select_person_from_matches(matches):
    if len(matches) == 1:
        print(f"Using only match: {matches[0]}")
        return matches[0]

    print("\nFound matching people:")
    for idx, person in enumerate(matches, 1):
        print(f"{idx}. {person}")

    selected = input("\nSelect person number or name: ").strip()
    if selected.isdigit() and 1 <= int(selected) <= len(matches):
        return matches[int(selected) - 1]

    selected_lower = selected.lower()
    exact_matches = [person for person in matches if person.lower() == selected_lower]
    if len(exact_matches) == 1:
        return exact_matches[0]

    partial_matches = [
        person for person in matches if selected_lower and selected_lower in person.lower()
    ]
    if len(partial_matches) == 1:
        return partial_matches[0]

    if len(partial_matches) > 1:
        print("That name matches multiple people. Please enter the number shown.")
    else:
        print("Invalid selection.")
    return None


def prompt_for_person(G, prompt):
    query = input(prompt).strip()
    matches = find_people(G, query)
    if not matches:
        print(f"No matching people found for '{query}'.")
        return None
    return select_person_from_matches(matches)


def detail_card(title, subtitle, image_url, rows, body):
    safe_title = html.escape(clean_text(title), quote=True)
    safe_subtitle = html.escape(clean_text(subtitle, ""), quote=True)
    safe_body = html.escape(truncate_text(body), quote=True)
    image = (
        f'<img class="detail-image" src="{html.escape(image_url, quote=True)}" alt="{safe_title}">'
        if image_url
        else '<div class="detail-image detail-image-empty">No image</div>'
    )
    rows_html = "".join(
        f"<div><span>{html.escape(label)}</span><strong>{html.escape(clean_text(value))}</strong></div>"
        for label, value in rows
    )
    return f"""
    <article class="node-detail-card">
      <div class="detail-top">
        {image}
        <div>
          <p>{safe_subtitle}</p>
          <h2>{safe_title}</h2>
        </div>
      </div>
      <div class="detail-meta">{rows_html}</div>
      <p class="detail-body">{safe_body}</p>
    </article>
    """


def person_info_html(display_name, meta):
    meta = meta or {}
    person_name = clean_text(meta.get("name") or display_name.title(), "Unknown Person")
    department = clean_text(meta.get("known_for_department"), "Person")
    bio = clean_text(meta.get("bio"), "No biography available in TMDb.")
    image_url = meta.get("image")
    image_html = (
        f'<img class="person-image" src="{html.escape(image_url, quote=True)}" alt="{html.escape(person_name, quote=True)}">'
        if image_url
        else '<div class="person-image person-image-empty">No image available</div>'
    )
    known_for = meta.get("known_for") or []
    known_for_html = (
        "".join(f"<li>{html.escape(title)}</li>" for title in known_for)
        if known_for
        else "<li>Not available</li>"
    )
    fields = [
        ("Known for", department),
        ("Birthday", meta.get("birthday")),
        ("Place of birth", meta.get("place_of_birth")),
        ("TMDb ID", meta.get("id")),
        ("Popularity", meta.get("popularity")),
        ("Homepage", meta.get("homepage")),
    ]
    rows_html = "".join(
        f"<div><span>{html.escape(label)}</span><strong>{html.escape(clean_text(value))}</strong></div>"
        for label, value in fields
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(person_name)} - Person Info</title>
  <style>
    body {{
      margin: 0;
      background: #f6f7f9;
      color: #17202a;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .person-page {{
      max-width: 920px;
      margin: 0 auto;
      padding: 40px 22px;
    }}
    .person-card {{
      display: grid;
      grid-template-columns: 220px minmax(0, 1fr);
      gap: 28px;
      background: #ffffff;
      border: 1px solid #d8dee4;
      border-radius: 8px;
      padding: 24px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
    }}
    .person-image {{
      width: 220px;
      height: 330px;
      object-fit: cover;
      border-radius: 8px;
      border: 1px solid #d8dee4;
      background: #e5e7eb;
    }}
    .person-image-empty {{
      display: flex;
      align-items: center;
      justify-content: center;
      color: #64748b;
      font-weight: 700;
      text-align: center;
    }}
    h1 {{
      margin: 0;
      font-size: 32px;
      line-height: 1.1;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin: 6px 0 22px;
      color: #64748b;
      font-size: 14px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .meta {{
      display: grid;
      gap: 8px;
      margin-bottom: 22px;
    }}
    .meta div {{
      display: flex;
      justify-content: space-between;
      gap: 18px;
      padding-bottom: 8px;
      border-bottom: 1px solid #edf2f7;
      font-size: 14px;
    }}
    .meta span {{
      color: #64748b;
    }}
    .meta strong {{
      color: #17202a;
      font-weight: 600;
      text-align: right;
      overflow-wrap: anywhere;
    }}
    h2 {{
      margin: 0 0 10px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    p {{
      margin: 0 0 22px;
      color: #334155;
      line-height: 1.55;
    }}
    ul {{
      margin: 0;
      padding-left: 18px;
      color: #334155;
      line-height: 1.6;
    }}
    @media (max-width: 720px) {{
      .person-card {{
        grid-template-columns: 1fr;
      }}
      .person-image {{
        width: 180px;
        height: 270px;
      }}
    }}
  </style>
</head>
<body>
  <main class="person-page">
    <section class="person-card">
      <div>{image_html}</div>
      <div>
        <h1>{html.escape(person_name)}</h1>
        <p class="subtitle">{html.escape(department)}</p>
        <div class="meta">{rows_html}</div>
        <h2>Biography</h2>
        <p>{html.escape(bio)}</p>
        <h2>Known For</h2>
        <ul>{known_for_html}</ul>
      </div>
    </section>
  </main>
</body>
</html>
"""


def enhance_graph_html(html_content, page_title, node_count, edge_count):
    safe_title = html.escape(page_title, quote=True)
    html_content = re.sub(
        r"\s*<center>\s*<h1>.*?</h1>\s*</center>\s*",
        "\n",
        html_content,
        flags=re.DOTALL,
    )
    html_content = re.sub(
        r"\s*<title>.*?</title>\s*",
        "\n",
        html_content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )
    html_content = html_content.replace(
        "<head>",
        f"<head>\n        <title>{safe_title}</title>",
        1,
    )
    html_content = html_content.replace(
        '<style type="text/css">',
        f'''<style type="text/css">
             html, body {{
                 width: 100%;
                 height: 100%;
                 margin: 0;
                 overflow: hidden;
                 background: #f6f7f9;
                 color: #17202a;
                 font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
             }}

             .app-header {{
                 height: 76px;
                 display: flex;
                 align-items: center;
                 justify-content: space-between;
                 gap: 16px;
                 padding: 14px 22px;
                 background: #ffffff;
                 border-bottom: 1px solid #d8dee4;
                 box-sizing: border-box;
             }}

             .app-header h1 {{
                 margin: 0;
                 font-size: 24px;
                 line-height: 1.15;
                 font-weight: 700;
                 letter-spacing: 0;
             }}

             .app-header p {{
                 margin: 4px 0 0;
                 color: #5f6b7a;
                 font-size: 13px;
             }}

             .summary-pills {{
                 display: flex;
                 flex-wrap: wrap;
                 justify-content: flex-end;
                 gap: 8px;
                 font-size: 12px;
                 color: #334155;
             }}

             .summary-pills span {{
                 padding: 6px 10px;
                 border: 1px solid #d8dee4;
                 border-radius: 999px;
                 background: #f8fafc;
                 white-space: nowrap;
             }}

             .graph-page {{
                 display: grid;
                 grid-template-columns: minmax(0, 1fr) 340px;
                 height: calc(100vh - 76px);
             }}

             .network-panel {{
                 min-width: 0;
                 min-height: 0;
             }}

             .card {{
                 height: 100% !important;
                 border: 0 !important;
                 border-radius: 0 !important;
                 background: transparent !important;
             }}

             .card-body {{
                 padding: 0 !important;
             }}

             #mynetwork {{
                 width: 100% !important;
                 height: 100% !important;
                 border: 0 !important;
                 float: none !important;
             }}

             .details-panel {{
                 min-width: 0;
                 overflow: auto;
                 padding: 18px;
                 background: #ffffff;
                 border-left: 1px solid #d8dee4;
                 box-sizing: border-box;
             }}

             .node-detail-card {{
                 display: flex;
                 flex-direction: column;
                 gap: 16px;
             }}

             .detail-top {{
                 display: grid;
                 grid-template-columns: 96px minmax(0, 1fr);
                 gap: 14px;
                 align-items: center;
             }}

             .detail-top h2 {{
                 margin: 0;
                 font-size: 20px;
                 line-height: 1.2;
                 letter-spacing: 0;
             }}

             .detail-top p {{
                 margin: 0 0 6px;
                 color: #64748b;
                 font-size: 12px;
                 font-weight: 700;
                 text-transform: uppercase;
             }}

             .detail-image {{
                 width: 96px;
                 height: 128px;
                 object-fit: cover;
                 border-radius: 8px;
                 background: #e5e7eb;
                 border: 1px solid #d8dee4;
             }}

             .detail-image-empty {{
                 display: flex;
                 align-items: center;
                 justify-content: center;
                 color: #64748b;
                 font-size: 12px;
                 text-align: center;
             }}

             .detail-meta {{
                 display: grid;
                 grid-template-columns: 1fr;
                 gap: 8px;
             }}

             .detail-meta div {{
                 display: flex;
                 justify-content: space-between;
                 gap: 12px;
                 padding-bottom: 8px;
                 border-bottom: 1px solid #edf2f7;
                 font-size: 13px;
             }}

             .detail-meta span {{
                 color: #64748b;
             }}

             .detail-meta strong {{
                 color: #17202a;
                 font-weight: 600;
                 text-align: right;
             }}

             .detail-body {{
                 margin: 0;
                 color: #334155;
                 font-size: 14px;
                 line-height: 1.5;
             }}

             .vis-tooltip {{
                 display: none !important;
             }}

             @media (max-width: 900px) {{
                 body {{
                     overflow: auto;
                 }}

                 .app-header {{
                     height: auto;
                     align-items: flex-start;
                     flex-direction: column;
                 }}

                 .summary-pills {{
                     justify-content: flex-start;
                 }}

                 .graph-page {{
                     grid-template-columns: 1fr;
                     grid-template-rows: 70vh auto;
                     height: auto;
                 }}

                 .details-panel {{
                     border-left: 0;
                     border-top: 1px solid #d8dee4;
                 }}
             }}
''',
        1,
    )
    html_content = html_content.replace(
        "<body>",
        f'''<body>
        <header class="app-header">
          <div>
            <h1>{safe_title}</h1>
            <p>Actor, director, and movie relationships from TMDb data</p>
          </div>
          <div class="summary-pills">
            <span>{node_count} nodes</span>
            <span>{edge_count} connections</span>
          </div>
        </header>
        <main class="graph-page">
          <section class="network-panel">''',
        1,
    )
    html_content = html_content.replace(
        '<script type="text/javascript">',
        '''</section>
          <aside id="details-panel" class="details-panel"></aside>
        </main>

        <script type="text/javascript">''',
        1,
    )
    html_content = html_content.replace(
        "network = new vis.Network(container, data, options);",
        """network = new vis.Network(container, data, options);

                  function escapeHtml(value) {
                      return String(value || "")
                          .replace(/&/g, "&amp;")
                          .replace(/</g, "&lt;")
                          .replace(/>/g, "&gt;")
                          .replace(/"/g, "&quot;")
                          .replace(/'/g, "&#039;");
                  }

                  function nodeName(nodeId) {
                      var node = nodes.get(nodeId);
                      return node ? node.label || node.id : nodeId;
                  }

                  function renderNodeDetails(nodeId) {
                      var panel = document.getElementById("details-panel");
                      var node = nodes.get(nodeId);
                      if (!panel || !node) {
                          return;
                      }
                      panel.innerHTML = node.detail_html || "<article class='node-detail-card'><h2>Node details</h2></article>";
                  }

                  function renderEdgeDetails(edgeId) {
                      var panel = document.getElementById("details-panel");
                      var edge = edges.get(edgeId);
                      if (!panel || !edge) {
                          return;
                      }
                      panel.innerHTML = "<article class='node-detail-card'><div class='detail-top'><div><p>Connection</p><h2>"
                          + escapeHtml(nodeName(edge.from)) + " to " + escapeHtml(nodeName(edge.to))
                          + "</h2></div></div><p class='detail-body'>"
                          + escapeHtml(edge.title || "No movie details available.") + "</p></article>";
                  }

                  network.on("selectNode", function(params) {
                      if (params.nodes.length) {
                          renderNodeDetails(params.nodes[0]);
                      }
                  });

                  network.on("hoverNode", function(params) {
                      renderNodeDetails(params.node);
                  });

                  network.on("selectEdge", function(params) {
                      if (params.edges.length) {
                          renderEdgeDetails(params.edges[0]);
                      }
                  });

                  var initialNode = nodes.get()[0];
                  if (initialNode) {
                      renderNodeDetails(initialNode.id);
                  }""",
        1,
    )
    return html_content

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

    person_cache = {}

# To Display the collaboration network visually
    def visualize_graph(G, custom_title=None):
        if G.number_of_nodes() > 50:
            print(
                f" Large graph with {G.number_of_nodes()} nodes. Filtering top 50 most connected..."
            )
            top_nodes = sorted(G.nodes, key=lambda x: G.degree(x), reverse=True)[:50]
            G = G.subgraph(top_nodes).copy()

        page_title = custom_title or "Movie Collaboration Network"
        net = Network(height="100vh", width="100%", bgcolor="white", font_color="black")
        net.heading = page_title
        net.barnes_hut()
        net.set_options("""
        {
          "interaction": {
            "hover": true,
            "tooltipDelay": 250
          },
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
            label = clean_text(data.get("movie_title") if role == "movie" else node)
            group = role if role in ["actor", "director", "movie"] else "other"
            title = clean_text(node)

            if role == "movie":
                poster = tmdb_image_url(data.get("poster_path"))
                detail_html = detail_card(
                    title=label,
                    subtitle="Movie",
                    image_url=poster,
                    rows=[
                        ("Year", data.get("release_year")),
                        ("Revenue", money(data.get("revenue"))),
                        ("Genres", ", ".join(data.get("genres", [])) or "Not available"),
                        ("Connections", G.degree(node)),
                    ],
                    body=data.get("overview"),
                )
                node_options = {
                    "label": label,
                    "group": group,
                    "title": title,
                    "detail_html": detail_html,
                    "size": 24,
                }
                if poster:
                    node_options.update({"shape": "image", "image": poster})
                net.add_node(node, **node_options)

            elif role in ["actor", "director"]:
                if label in person_cache:
                    person_meta = person_cache[label]
                else:
                    person_meta = get_person_metadata(label)
                    person_cache[label] = person_meta

                if person_meta:
                    bio = person_meta.get("bio", "No bio available.")
                    image = person_meta.get("image")
                    if not image:
                        image = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/200px-No_image_available.svg.png"
                    detail_html = detail_card(
                        title=label,
                        subtitle=role.title(),
                        image_url=image,
                        rows=[
                            ("Role", role.title()),
                            ("Connections", G.degree(node)),
                        ],
                        body=bio,
                    )
                    net.add_node(
                        node,
                        label=label,
                        shape="circularImage",
                        image=image,
                        group=group,
                        title=title,
                        detail_html=detail_html,
                        size=22,
                    )
                else:
                    detail_html = detail_card(
                        title=label,
                        subtitle=role.title(),
                        image_url=None,
                        rows=[
                            ("Role", role.title()),
                            ("Connections", G.degree(node)),
                        ],
                        body="No biography available.",
                    )
                    net.add_node(
                        node,
                        label=label,
                        group=group,
                        title=title,
                        detail_html=detail_html,
                        size=18,
                    )
            else:
                detail_html = detail_card(
                    title=label,
                    subtitle=role.title(),
                    image_url=None,
                    rows=[("Connections", G.degree(node))],
                    body="No details available.",
                )
                net.add_node(
                    node,
                    label=label,
                    group=group,
                    title=title,
                    detail_html=detail_html,
                    size=16,
                )

        for u, v, data in G.edges(data=True):
            movie_titles = ", ".join(data.get("movies", []))
            net.add_edge(u, v, title=movie_titles)

        path = os.path.abspath("collaboration_network.html")
        net.write_html(path)
        with open(path, "r", encoding="utf-8") as f:
            graph_html = f.read()
        graph_html = enhance_graph_html(
            graph_html,
            page_title=page_title,
            node_count=G.number_of_nodes(),
            edge_count=G.number_of_edges(),
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(graph_html)
        open_generated_file(path)
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
            selected_person = prompt_for_person(G, "Enter person's name: ")
            if selected_person:
                print(find_most_frequent_collaborators(G, selected_person))
                subgraph = G.subgraph(
                    [selected_person] + list(G.neighbors(selected_person))
                )
                visualize_graph(
                    subgraph, custom_title=f"Collaborators for {selected_person}"
                )

        elif choice == "2":
            source_person = prompt_for_person(G, "Start person: ")
            target_person = prompt_for_person(G, "End person: ") if source_person else None
            if source_person and target_person:
                try:
                    path = nx.shortest_path(
                        G, source=source_person, target=target_person
                    )
                    print("Connection Path Found:")
                    for idx, node in enumerate(path):
                        print(f"{idx + 1}. {node}")
                    subgraph = G.subgraph(path)
                    visualize_graph(
                        subgraph,
                        custom_title=(
                            f"Connection Path: {source_person} to {target_person}"
                        ),
                    )
                except nx.NetworkXNoPath:
                    print("No connection found.")

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
                movie_title = G.nodes[selected_movie].get("movie_title", selected_movie)
                visualize_graph(subgraph, custom_title=movie_title)
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
            visualize_graph(G_sub, custom_title="Top 20 Star Collaborators")

        elif choice == "6":
            name = input("Enter person's name: ").strip()
            matched_names = [
                n
                for n, d in G.nodes(data=True)
                if n.lower() == name.lower() and d.get("job") in {"actor", "director"}
            ]
            display_name = matched_names[0] if matched_names else name
            meta = get_person_metadata(display_name)
            html_content = person_info_html(display_name, meta)
            with open("person_info.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("Bio and image saved as 'person_info.html'!")
            open_generated_file(os.path.abspath("person_info.html"))

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
