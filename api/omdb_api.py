import requests

### This module fetches movie and person metadata from TMDb and OMDb APIs.
### API keys for TMDb and OMDb
### These keys are used to fetch movie and person metadata.
### Make sure to keep them secure and not expose them in public repositories.
### OMDb API key: http://www.omdbapi.com/apikey.aspx
OMDB_API_KEY = "19760cdd"


def get_movie_metadata(title_or_id):
    try:
        base_url = "http://www.omdbapi.com/"
        params = {
            "apikey": OMDB_API_KEY,
            "t": title_or_id,
            "plot": "short",
            "r": "json",
        }
        response = requests.get(base_url, params=params, timeout=5)
        data = response.json()

        if data.get("Response", "False") == "True":
            plot = data.get("Plot", "No plot found.")
            poster = data.get("Poster", None)
            if poster == "N/A":
                poster = None
            return {"plot": plot, "poster": poster}
        else:
            return {"plot": "No plot found.", "poster": None}

    except Exception as e:
        print(f"Error fetching from OMDb: {e}")
        return {"plot": "Error retrieving metadata", "poster": None}
