from api.tmdb_api import get_movie_details, get_person_metadata


def get_movie_metadata(title_or_id):
    try:
        data = get_movie_details(title_or_id)
        if not data:
            return {"plot": "No plot found.", "poster": None}

        plot = data.get("overview", "No plot found.")
        poster_path = data.get("poster_path")
        poster = f"https://image.tmdb.org/t/p/w200{poster_path}" if poster_path else None

        return {"plot": plot, "poster": poster}
    except Exception as e:
        print(f"Error in get_movie_metadata: {e}")
        return {"plot": "Error retrieving metadata", "poster": None}
