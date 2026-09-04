import os

import requests


def _get_omdb_api_key():
    api_key = os.getenv("OMDB_API_KEY")
    if not api_key:
        print("OMDB_API_KEY is not set. Add it to your environment before running OMDb requests.")
    return api_key


def get_movie_metadata(title_or_id):
    api_key = _get_omdb_api_key()
    if not api_key:
        return {"plot": "OMDB_API_KEY is not set.", "poster": None}

    try:
        base_url = "https://www.omdbapi.com/"
        params = {
            "apikey": api_key,
            "t": title_or_id,
            "plot": "short",
            "r": "json",
        }
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("Response", "False") == "True":
            plot = data.get("Plot", "No plot found.")
            poster = data.get("Poster")
            if poster == "N/A":
                poster = None
            return {"plot": plot, "poster": poster}

        return {"plot": "No plot found.", "poster": None}

    except requests.RequestException as e:
        print(f"Error fetching from OMDb: {e}")
        return {"plot": "Error retrieving metadata", "poster": None}
