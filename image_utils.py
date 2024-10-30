from PIL import Image, ImageFont, ImageDraw


def center_position(final_poster_width: float, obj_bbox: tuple[float, float, float, float]) -> float:
    """
    Calculate the horizontal center position for an object bbox within a specified width.

    Args:
        final_poster_width (float): The width of the poster image.
        obj_bbox (tuple[float, float, float, float]): The bounding box of the object (left, top, right, bottom).

    Returns:
        float: The x-coordinate to center the object within the final poster width.
    """
    obj_width = obj_bbox[2] - obj_bbox[0]
    return (final_poster_width - obj_width) // 2


def add_bboxes(
        bbox1: tuple[float, float, float, float],
        bbox2: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    """
    Combine two bounding boxes and return the resulting bounding box.

    Args:
        bbox1 (tuple[float, float, float, float]): The first bounding box (left, top, right, bottom).
        bbox2 (tuple[float, float, float, float]): The second bounding box (left, top, right, bottom).

    Returns:
        tuple[float, float, float, float]: A new bounding box that encompasses both input bounding boxes.
    """
    left = min(bbox1[0], bbox2[0])
    top = min(bbox1[1], bbox2[1])
    right = max(bbox1[2], bbox2[2])
    bottom = max(bbox1[3], bbox2[3])

    return left, top, right, bottom


def get_adaptive_font(text: str, font_path: str, max_width: int,
                      initial_font_size: int = 244) -> ImageFont.FreeTypeFont:
    """
    Determine the largest font size that allows the text to fit within a given width.

    Args:
        text (str): The text to be rendered.
        font_path (str): The path to the font file.
        max_width (int): The maximum width the text should fit within.
        initial_font_size (int): The starting font size to test (default is 244).

    Returns:
        ImageFont.FreeTypeFont: A font object with the appropriate size to fit within max_width.
    """
    # Start with the initial font size.
    font_size = initial_font_size
    font = ImageFont.truetype(font_path, font_size)

    # Create a temporary draw object to measure text width.
    with Image.new("RGBA", (1, 1)) as temp_image:
        draw = ImageDraw.Draw(temp_image)

        # Reduce font size until the text width is within the max width.
        while draw.textbbox((0, 0), text, font=font)[2] > max_width and font_size > 10:  # Avoid too small fonts.
            font_size -= 1
            font = ImageFont.truetype(font_path, font_size)

    return font


def smart_resize(image_path: str, target_size: tuple[int, int]) -> Image:
    """
    Resize an image to fit within a target size, preserving the aspect ratio and centering the result.

    Args:
        image_path (str): Path to the image file.
        target_size (tuple[int, int]): The target (width, height) for the resized image.

    Returns:
        Image: The resized image centered on a canvas of target_size with a transparent background.
    """
    # Load the image.
    image = Image.open(image_path).convert("RGBA")

    # Calculate the scale factors for both dimensions.
    scale_width = target_size[0] / image.width
    scale_height = target_size[1] / image.height

    # Use the maximum scale factor to ensure the image fills the target size.
    scale = max(scale_width, scale_height)

    # Calculate new dimensions based on the scale factor.
    new_width = int(image.width * scale)
    new_height = int(image.height * scale)

    # Resize the image with aspect ratio preserved.
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create a blank canvas with the target size.
    canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))

    # Calculate the position to paste the resized image to be centered.
    x_offset = (target_size[0] - new_width) // 2
    y_offset = (target_size[1] - new_height) // 2

    # Paste the resized image onto the canvas.
    canvas.paste(resized_image, (x_offset, y_offset))

    return canvas


def create_image_poster(
        title_text: str,
        poster_image_path: str,
        output_image_path: str,
        blur_image_path: str) -> None:
    """
    Create a movie poster with a title and blur effect.

    Args:
        title_text (str): Title text for the movie poster.
        poster_image_path (str): Path to the main poster image.
        output_image_path (str): Path where the final poster image will be saved.
        blur_image_path (str): Path to the image used for the blur effect.

    Returns:
        None
    """

    # Load and resize images.
    target_size = (2400, 2940)
    poster = smart_resize(poster_image_path, target_size)
    blur = Image.open(blur_image_path).resize((2400, 2940)).convert("RGBA")

    # Calculate the offset for the blur to end near the center of the poster.
    poster_height = poster.height
    blur_height = blur.height
    offset_y: int = int(poster_height // 1.2 - blur_height)

    # Create a blank image to hold the modified blur with offset.
    blur_with_offset = Image.new("RGBA", poster.size, (0, 0, 0, 0))

    # Paste the blur image onto the blank canvas at the calculated offset.
    blur_with_offset.paste(blur, (0, -offset_y))

    # Composite the poster with the blur effect starting from the specified offset.
    final_poster = Image.alpha_composite(poster, blur_with_offset)

    # Prepare to draw on the final image.
    draw = ImageDraw.Draw(final_poster)

    # Define maximum width for the title.
    max_title_width = poster.width - 200  # leave some padding.

    # Load fonts.
    title_font = get_adaptive_font(title_text, "Gloock/Gloock-Regular.ttf", max_title_width)
    gloock_font = ImageFont.truetype("Gloock/Gloock-Regular.ttf", 126)
    charmonman_font = ImageFont.truetype("Charmonman/Charmonman-Bold.ttf", 126)
    small_font = ImageFont.truetype("Gloock/Gloock-Regular.ttf", 44)

    # Define text.
    cine: str = "ciné"
    fil: str = "fil"
    room_info: str = "salle J160"
    day_info: str = "mardi 20h30"

    # Get text bounding boxes for centering.
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    cine_bbox = draw.textbbox((0, 0), cine, font=gloock_font)
    fil_bbox = draw.textbbox((0, 0), fil, font=charmonman_font)
    room_bbox = draw.textbbox((0, 0), room_info, font=small_font)
    day_bbox = draw.textbbox((0, 0), day_info, font=small_font)

    # Calculate positions.
    title_position = (center_position(final_poster.width, title_bbox), final_poster.height - (final_poster.height // 4))

    cine_width = cine_bbox[2] - cine_bbox[0]
    fil_width = fil_bbox[2] - fil_bbox[0]
    cinefil_width = cine_width + fil_width
    cine_height = cine_bbox[3] - cine_bbox[1]
    fil_height = fil_bbox[3] - fil_bbox[1]
    cinefil_height = cine_height + fil_height

    cinefil_bbox = add_bboxes(cine_bbox, fil_bbox)
    cinefil_start_position = center_position(final_poster.width, cinefil_bbox)

    cine_position = (cinefil_start_position,
                     final_poster.height - 450 + (cine_height // 4))
    fil_position = (
        cinefil_start_position + cine_bbox[2], final_poster.height - 450)

    room_position = (cine_position[0] + room_bbox[2] + (cinefil_width // 1.3), cine_position[1] + (cinefil_height // 4))
    day_position = (cine_position[0] - day_bbox[2] - (cinefil_width // 3), cine_position[1] + (cinefil_height // 4))

    # Draw text on the poster.
    draw.text(title_position, title_text, font=title_font, fill="white")
    draw.text(cine_position, cine, font=gloock_font, fill="white")
    draw.text(fil_position, fil, font=charmonman_font, fill="white")
    draw.text(room_position, room_info, font=small_font, fill="white")
    draw.text(day_position, day_info, font=small_font, fill="white")

    # Save the final poster.
    final_poster.save(output_image_path, format='PNG')
