import requests
## API keys for TMDb and OMDb
# These keys are used to fetch movie and person metadata.
# Make sure to keep them secure and not expose them in public repositories.
# TMDb API key: https://developers.themoviedb.org/3/getting-started/introduction
# OMDb API key: http://www.omdbapi.com/apikey.aspx
# TMDb API key: 5b4c9c706c4358243fb2945530eaddb4
# OMDb API key: 19760cd4

TMDB_API_KEY = "5b4c9c706c4358243fb2945530eaddb4"
OMDB_API_KEY = "19760cd4"

def get_movie_metadata(title_or_id):
    from api.tmdb_api import get_movie_details

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


def get_person_metadata(name):
    try:

        tmdb_search_url = f"https://api.themoviedb.org/3/search/person?query={name}&api_key={TMDB_API_KEY}"
        search_resp = requests.get(tmdb_search_url).json()
        if search_resp.get("results"):
            person = search_resp["results"][0]
            person_id = person["id"]

            details_url = f"https://api.themoviedb.org/3/person/{person_id}?api_key={TMDB_API_KEY}"
            details_resp = requests.get(details_url).json()

            profile_path = details_resp.get("profile_path")
            image_url = f"https://image.tmdb.org/t/p/w200{profile_path}" if profile_path else None
            bio = details_resp.get("biography", "Biography not available.")

            return {
                "bio": bio.strip()[:500] if bio else "Biography not available.",
                "image": image_url
            }
    except Exception as e:
        print(f"[TMDb Person Error] {e}")

    return {"bio": "No biography found.", "image": None}