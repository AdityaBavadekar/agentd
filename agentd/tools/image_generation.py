"""Tools for generating images using external APIs."""

import os
from datetime import datetime
from io import BytesIO
from typing import Callable

from google import genai
from google.genai import types
from PIL import Image

from agentd.utils import get_cloud_storage, get_generated_directory

SAVE_DIR = get_generated_directory()
SAVE_DIR = os.path.join(SAVE_DIR, "generated_images")
IMAGEN_DISABLED = True
CLOUD_STORAGE_DISABLED = False
CLOUD_STORAGE_IMAGES_DIR = "generated_images"

client = genai.Client()
os.makedirs(SAVE_DIR, exist_ok=True)


def _generate_file_name(prefix: str = "AI", extension: str = "png") -> str:
    """Generates a unique file name based on the current timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"GEN_IMG_{prefix}_{timestamp}.{extension}"


def image_generation_gemini(description: str):
    """Generates an image using the Gemini API based on the provided description."""

    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=description,
        config=types.GenerateContentConfig(
            response_modalities=[
                # NOTE: uncommenting "TEXT" you will get: models/gemini-2.0-flash-preview-image-generation accepts the following combination of response modalities: IMAGE, TEXT
                # so it is best to keep it
                "TEXT",
                "IMAGE",
            ]
        ),
    )
    file_name = _generate_file_name(prefix="GEMINI", extension="png")
    file_path = os.path.join(SAVE_DIR, file_name)

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            image.save(file_path)

    return file_path


def image_generation_imagen(description: str):
    """Generates an image using the Imagen API based on the provided description."""
    # NOTE: Imagen API is only accessible to billed users at this time.

    if IMAGEN_DISABLED:
        raise RuntimeError("Imagen API is currently disabled for this example.")

    response = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=description,
        config=types.GenerateImagesConfig(
            number_of_images=1,
        ),
    )
    file_name = _generate_file_name(prefix="IMAGEN", extension="png")
    file_path = os.path.join(SAVE_DIR, file_name)

    for generated_image in response.generated_images:
        image = Image.open(BytesIO(generated_image.image.image_bytes))
        image.save(file_path)

    return file_path


SELECTED_IMAGE_GENERATION_METHOD: Callable[[str], str] = image_generation_gemini


def generate_image_tool(description: str):
    # wrapper for the image generation function, since the agent should be independent of the specific image generation method used.
    """
    Generates an image using AI based on the provided description.
    Args:
        description (str): The description of the image to be generated.
    Returns:
        str: The file path where the generated image is saved.
    """

    # return "https://picsum.photos/200/300"

    try:
        print("=== GENERATING IMAGE ===")
        image_path = SELECTED_IMAGE_GENERATION_METHOD(description)
        print(f"Image generated and saved at: {image_path}")
        print("=== IMAGE GENERATED ===")

        # using the image_path uploaded the image to the cloud storage
        print("Uploading image to cloud storage...")
        remote_file_path = os.path.join(
            CLOUD_STORAGE_IMAGES_DIR, os.path.basename(image_path)
        )
        get_cloud_storage().upload_file(
            local_path=image_path,
            remote_path=remote_file_path,
        )
        print("Image uploaded to cloud storage.")
        image_url = get_cloud_storage().get_file_url(remote_file_path)

        # add a directory prefix to the image path so that when the image url is used,
        # the DIR prefix is can be replced with the actual project directory path.
        return image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        return "[Image generation failed]"
