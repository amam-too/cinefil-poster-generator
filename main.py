import os

from image_utils import create_image_poster
from tmdb_utils import download_image, fetch_movie_images


def ensure_directories_exist(paths: list[str]) -> None:
    """
    Ensure that all directories in the provided list exist; create them if they do not.

    Args:
        paths (list[str]): A list of directory paths to check and create if necessary.

    Returns:
        None
    """
    for path in paths:
        os.makedirs(path, exist_ok=True)


def create_movie_poster(movie_title: str, images: list[any], label: str, save_original: bool) -> None:
    """
    Helper function to process a list of images (posters or backdrops).

    Args:
        :param save_original: (bool) Whether to save the original poster or not.
        :param label: (str) Label to differentiate posters from backdrops in filenames.
        :param images: (list[any]): A list of images to process.
        :param movie_title: (str) The title of the movie.

    Returns:
        None
    """

    for i, image in enumerate(images):
        image_path = image['file_path']

        # Define paths for original and final images.
        if save_original:
            original_image_path = f"originals/original_{label}_{i + 1}.jpg"
            download_image(image_path, original_image_path)
        else:
            original_image_path = f"posters/temp_{label}_{i + 1}.jpg"
            download_image(image_path, original_image_path)

        # Define output path for final customized poster.
        output_image_path = f"posters/final_movie_{label}_{i + 1}.png"

        print(f"Creating poster {output_image_path}")

        # Create the movie poster with customized styling.
        create_image_poster(
            title_text=movie_title,
            poster_image_path=original_image_path,
            blur_image_path="Blur.png",
            output_image_path=output_image_path
        )

        # Remove the temporary file if not saving the original.
        if not save_original:
            os.remove(original_image_path)


def generate_movie_posters(
        movie_title: str,
        movie_id: int,
        save_original: bool,
        poster_languages: list[str] | None = None) -> None:
    """
    Fetch and process movie posters by downloading, optionally saving originals,
    and creating a customized movie poster for each image.

    Args:
        :param poster_languages: (list[str] | None) List of languages of movie posters.
        :param movie_title: (str) The title of the movie.
        :param movie_id: (int) The unique identifier for the movie on TMDB.
        :param save_original: (bool) Whether to save the original poster images.

    Returns:
        None
    """

    # Ensure necessary directories are created.
    ensure_directories_exist(["originals", "posters"])

    # Fetch images from TMDB.
    movie_images: dict[str, any] = fetch_movie_images(movie_id=movie_id, languages=poster_languages)
    if not movie_images:
        print("Failed to fetch movie images.")
        return

    # Retrieve all posters available for the movie.
    posters: list[any] = movie_images.get('posters', [])
    if not posters:
        print("No posters available for this movie.")
    else:
        print(f"-> Found {len(posters)} posters.")
        create_movie_poster(movie_title=movie_title, images=posters, label="poster", save_original=save_original)

    # Retrieve all backdrops available for the movie.
    backdrops: list[any] = movie_images.get('backdrops', [])
    if not backdrops:
        print("No backdrops available for this movie.")
    else:
        print(f"-> Found {len(backdrops)} backdrops.")
        create_movie_poster(movie_title=movie_title, images=posters, label="backdrop", save_original=save_original)


POSTER_LANGUAGES: list[str] = ["en", "de", "fr", "it", "es", "null"]
MOVIE_TITLE: str = "The Substance"
MOVIE_ID: int = 933260
SAVE_ORIGINAL: bool = False  # Set this to True if you want to save the original posters.

if __name__ == "__main__":
    generate_movie_posters(
        movie_title=MOVIE_TITLE,
        movie_id=MOVIE_ID,
        save_original=SAVE_ORIGINAL,
        poster_languages=POSTER_LANGUAGES)
