import os
from pathlib import Path

import requests

TMDB_BASE_URL = "https://api.themoviedb.org/3/movie"
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/person"
TMDB_PERSON_URL = "https://api.themoviedb.org/3/person"
_LOCAL_ENV = None


def _load_local_env():
    global _LOCAL_ENV
    if _LOCAL_ENV is not None:
        return _LOCAL_ENV

    values = {}
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip("\"'")

    _LOCAL_ENV = values
    return values


def _get_tmdb_api_key():
    api_key = _load_local_env().get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")
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


def _select_person_result(results, query):
    query = query.strip().lower()
    for result in results:
        if result.get("name", "").strip().lower() == query:
            return result
    return results[0]


def _known_for_titles(items):
    titles = []
    for item in items:
        title = item.get("title") or item.get("name")
        release = item.get("release_date") or item.get("first_air_date") or ""
        year = release[:4]
        if title and year:
            titles.append(f"{title} ({year})")
        elif title:
            titles.append(title)
    return titles


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

        results = search_data.get("results", [])
        if not results:
            return None

        result = _select_person_result(results, name)
        person_id = result["id"]

        details_resp = requests.get(
            f"{TMDB_PERSON_URL}/{person_id}",
            params={"api_key": api_key},
            timeout=10,
        )
        details_resp.raise_for_status()
        data = details_resp.json()

        profile_path = data.get("profile_path")
        return {
            "id": person_id,
            "name": data.get("name") or result.get("name") or name,
            "bio": data.get("biography") or "No biography available in TMDb.",
            "image": f"https://image.tmdb.org/t/p/w200{profile_path}" if profile_path else None,
            "known_for_department": (
                data.get("known_for_department")
                or result.get("known_for_department")
                or "Not available"
            ),
            "birthday": data.get("birthday") or "Not available",
            "deathday": data.get("deathday") or "Not available",
            "place_of_birth": data.get("place_of_birth") or "Not available",
            "popularity": data.get("popularity") or "Not available",
            "homepage": data.get("homepage") or "Not available",
            "known_for": _known_for_titles(result.get("known_for", [])),
        }

    except requests.RequestException as e:
        print(f"Error fetching person metadata: {_format_request_error(e)}")
        return None
