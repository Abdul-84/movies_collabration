import requests

TMDB_API_KEY = "5b4c9c706c4358243fb2945530eaddb4"
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie"
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/person"
TMDB_PERSON_URL = "https://api.themoviedb.org/3/person"

def get_movie_credits(movie_id):
    url = f"{TMDB_BASE_URL}/{movie_id}/credits"
    params = {"api_key": TMDB_API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching movie credits: {e}")
        return None

def get_movie_details(movie_id):
    url = f"{TMDB_BASE_URL}/{movie_id}"
    params = {"api_key": TMDB_API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching movie details: {e}")
        return None

def get_person_metadata(name):
    """
    Fetches bio and profile image for a person (actor or director) from TMDb.

    :param name: str, Name of the person
    :return: dict with 'bio' and 'image' keys, or None if not found
    """
    search_params = {"api_key": TMDB_API_KEY, "query": name}
    try:
        search_resp = requests.get(TMDB_SEARCH_URL, params=search_params)
        search_resp.raise_for_status()
        search_data = search_resp.json()

        if not search_data.get("results"):
            return None

        person_id = search_data["results"][0]["id"]

        details_resp = requests.get(f"{TMDB_PERSON_URL}/{person_id}", params={"api_key": TMDB_API_KEY})
        details_resp.raise_for_status()
        data = details_resp.json()

        return {
            "bio": data.get("biography", "No bio available."),
            "image": f"https://image.tmdb.org/t/p/w200{data.get('profile_path')}" if data.get("profile_path") else None
        }

    except requests.RequestException as e:
        print(f"Error fetching person metadata: {e}")
        return None