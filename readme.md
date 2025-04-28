# Movie Collaboration Network – SI 507 Final Project

## 🔍 Project Selection & Motivation (Part A)

**Project:** Movie Collaboration Network  
**Goal:** To explore how professional relationships in the film industry influence success and influence.  
**Motivation:** I want to visualize how actors, directors, and producers are interconnected across movies, and analyze how working with well-connected people affects things like box office success. This network-based approach will help answer:  
- Who are the most central people in the industry?
- Do certain cliques dominate movie collaborations?
- Is there a “shortcut” between distant collaborators?

---

## 📦 Dataset & API Usage (Part B)

**APIs used:**
- [TMDb API](https://developer.themoviedb.org/reference/intro/getting-started)
- Box Office earnings from TMDb (used instead of Box Office Mojo)

**Data Access Proven (see screenshots to attach):**
- Raw TMDb API response for `/movie/{id}` and `/movie/{id}/credits`
- Sample graph output in terminal
- List of all people in the graph saved to `people_in_graph.txt`
- NetworkX graph visualization for specific movie

**Sample File Accessed:**
- `tmdb_api.py`: connects to TMDb API
- `build_graph.py`: constructs the collaboration graph
- `main.py`: handles CLI interface

---

## 🧑‍💻 User Interactions Implemented (Part C)

| Feature | Description |
|--------|-------------|
| 1️⃣ Find most frequent collaborators | Enter a person’s name and see who they worked with the most, with movie titles & counts |
| 2️⃣ Find shortest connection with movies | Compute a collaboration path between two people with movie details |
| 3️⃣ View collaboration network for a movie | Visualize the network of collaborators in a single film |
| 4️⃣ List all people in the graph | Print or filter people by role (actor, director, etc.), supports export |
| ✅ Bonus: Community Detection | Groups of closely collaborating people (in progress) |

---

## 🖼 Screenshot Requirements (Part D.1)

> 📌 Attach these:
- Terminal screenshot showing successful API response in Python
- Graph image or CLI output from “most frequent collaborators”
- View of `people_in_graph.txt` saved file

---

## ❓ Questions for Myself (Part D.2)

1. Should I integrate actual movie genres and show how genre affects collaboration?
2. Do I need to limit my network to only lead cast members?
3. Should I include awards or popularity scores from TMDb as node weights?

---

## 🤔 Instructor Note (Part D.3)

I am confident in my current direction and have no major questions for the instructor right now.

---

## 🧠 Notes

- Data is stored locally; caching is being added
- Final deliverables will include video demo, full project report, and clean repo

---

# analysis.py

def save_collaborators_to_file(G, person):
    if person not in G:
        return f"{person} not found in the graph."

    collaborators = [(neighbor, G[person][neighbor]) for neighbor in G.neighbors(person)]
    sorted_collabs = sorted(collaborators, key=lambda x: x[1]['weight'], reverse=True)[:5]

    output = [f"Top collaborators for {person}:\n"]
    for name, data in sorted_collabs:
        output.append(f"{name}")
        movies = data.get("movies", [])
        for i, movie in enumerate(movies, 1):
            output.append(f"  {i}. {movie}")
        output.append(f"  ↳ Total collaborations: {data['weight']}")

    filename = f"{person.replace(' ', '_')}_collab.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    return f"Saved to {filename}"

---

# main.py

                save = input("Would you like to save this report to a text file? (y/n): ").lower()
                if save == "y":
                    print(save_collaborators_to_file(G, matched[0]))
