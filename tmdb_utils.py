import os

import requests
from dotenv import load_dotenv

# Load environment variables.
load_dotenv('.env.local')


def fetch_movie_images(movie_id: int, languages: list[str] | None = None) -> dict[str, any] | None:
    """
    Fetch images for a specific movie from TMDB.

    Args:
        movie_id (int): The unique identifier for the movie on TMDB.
        languages (List[str], optional): List of languages to include in the image results.
            Defaults to None.

    Returns:
        dict[str, any] | None: A dictionary containing image data if the request is successful,
        otherwise None if the request fails.
    """
    if languages:
        # Construct the language query parameter.
        language_param = "%2C".join(languages)  # Join languages with URL-encoded comma.
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/images?include_image_language={language_param}"
    else:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/images"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('TMDB_API_TOKEN')}"
    }

    try:
        print(f"Fetching images for movie with id {movie_id}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching images for movie ID {movie_id}: {e}")
        return None


def download_image(file_path: str, output_path: str) -> None:
    """
    Download an image from TMDB to a specified local file path.

    Args:
        file_path (str): The relative path of the image file on TMDB.
        output_path (str): The local path where the image will be saved.

    Returns:
        None
    """
    base_url = "https://image.tmdb.org/t/p/original"
    image_url = f"{base_url}{file_path}"

    try:
        response = requests.get(image_url)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
    except requests.RequestException as e:
        print(f"Error downloading image from {image_url} to {output_path}: {e}")