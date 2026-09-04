import os

import requests

TMDB_BASE_URL = "https://api.themoviedb.org/3/movie"
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/person"
TMDB_PERSON_URL = "https://api.themoviedb.org/3/person"


def _get_tmdb_api_key():
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        print("TMDB_API_KEY is not set. Add it to your environment before running TMDb requests.")
    return api_key


def _format_request_error(error):
    response = getattr(error, "response", None)
    if response is not None:
        reason = response.reason or "HTTP error"
        return f"{response.status_code} {reason}"

    request = getattr(error, "request", None)
    if request is not None and request.url:
        safe_url = request.url.split("?", 1)[0]
        return f"{error.__class__.__name__} while requesting {safe_url}"

    return error.__class__.__name__


def get_movie_credits(movie_id):
    api_key = _get_tmdb_api_key()
    if not api_key:
        return None

    url = f"{TMDB_BASE_URL}/{movie_id}/credits"
    params = {"api_key": api_key}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching movie credits: {_format_request_error(e)}")
        return None


def get_movie_details(movie_id):
    api_key = _get_tmdb_api_key()
    if not api_key:
        return None

    url = f"{TMDB_BASE_URL}/{movie_id}"
    params = {"api_key": api_key}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching movie details: {_format_request_error(e)}")
        return None


def get_person_metadata(name):
    api_key = _get_tmdb_api_key()
    if not api_key:
        return None

    search_params = {"api_key": api_key, "query": name}
    try:
        search_resp = requests.get(TMDB_SEARCH_URL, params=search_params, timeout=10)
        search_resp.raise_for_status()
        search_data = search_resp.json()

        if not search_data.get("results"):
            return None

        person_id = search_data["results"][0]["id"]

        details_resp = requests.get(
            f"{TMDB_PERSON_URL}/{person_id}",
            params={"api_key": api_key},
            timeout=10,
        )
        details_resp.raise_for_status()
        data = details_resp.json()

        profile_path = data.get("profile_path")
        return {
            "bio": data.get("biography", "No bio available."),
            "image": f"https://image.tmdb.org/t/p/w200{profile_path}" if profile_path else None,
        }

    except requests.RequestException as e:
        print(f"Error fetching person metadata: {_format_request_error(e)}")
        return None
