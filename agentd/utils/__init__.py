import io
import json
import os
import re
import uuid

import dotenv
import markdown2
from weasyprint import CSS, HTML

from .cloud_storage import GCPStorage

dotenv.load_dotenv()


def extract_json_from_text(text):
    """
    Extracts the largest valid JSON object or array in a noisy string.
    """

    cleaned_text = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()

    start = None
    stack = []
    for i, c in enumerate(cleaned_text):
        if c == "{" or c == "[":
            if start is None:
                start = i
            stack.append(c)
        elif c == "}" or c == "]":
            if not stack:
                continue
            opening = stack.pop()
            if (opening == "{" and c != "}") or (opening == "[" and c != "]"):
                continue  # malformed
            if not stack:
                json_str = cleaned_text[start : i + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    start = None  # reset if failed

    raise ValueError("No valid JSON found in text.")


def json_to_markdown(data, indent=0):
    """
    Convert JSON (dict or list) to Markdown string.

    Args:
        data (dict or list): The JSON data.
        indent (int): Current indentation level (internal use).

    Returns:
        str: Markdown representation.
    """
    md_lines = []
    prefix = "  " * indent

    if isinstance(data, dict):
        for key, value in data.items():
            key = key.replace("_", " ").title()  # format key for better readability
            if isinstance(value, (dict, list)):
                md_lines.append(f"{prefix}- **{key}**:")
                md_lines.append(json_to_markdown(value, indent + 1))
            else:
                md_lines.append(f"{prefix}- **{key}**: {value}")
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            if isinstance(item, (dict, list)):
                md_lines.append(f"{prefix}- Item {idx + 1}:")
                md_lines.append(json_to_markdown(item, indent + 1))
            else:
                md_lines.append(f"{prefix}- `{item}`")
    else:
        # primitive value
        md_lines.append(f"{prefix}- `{data}`")

    return "\n\n".join(md_lines)


def get_cloud_storage():
    """
    Returns an instance of the Default Cloud Storage implementation.
    This function is a wrapper so it can independant of the specific cloud storage implementation used.
    """
    return GCPStorage()


def get_generated_directory():
    """
    Returns the path to the generated directory.
    """
    from pathlib import Path

    return str(Path(__file__).resolve().parents[2] / "generated")


def _save_to_file(file_path: str, pdf_bytes: io.BytesIO):
    """Saves the PDF bytes to a local file."""
    if not file_path.endswith(".pdf"):
        file_path += ".pdf"
    with open(file_path, "wb") as f:
        f.write(pdf_bytes.read())
    print(f"Saved locally as {file_path}")
    return file_path


def _save_to_cloud(local_file_path: str, remote_file_dir: str = "pdfs") -> str:
    """Uploads a file to Cloud Storage and returns the public URL."""
    remote_file_path = os.path.join(remote_file_dir, os.path.basename(local_file_path))
    print(f"Uploading PDF to cloud storage at {remote_file_path}...")
    get_cloud_storage().upload_file(
        local_path=local_file_path, remote_path=remote_file_path
    )
    print("PDF uploaded to cloud storage.")
    print("Generating public URL for the PDF...")
    public_url = get_cloud_storage().get_file_url(remote_file_path)
    print(f"Public URL for the PDF: {public_url}")

    return public_url


def create_and_upload_pdf(
    markdown_content: str,
    pdf_title: str,
    local_dir: str = os.path.join(get_generated_directory(), "pdfs"),
    remote_dir: str = "pdfs",
) -> str:
    """
    Generates a PDF from Markdown content, uploads it to Cloud Storage,
    and returns the public URL.

    Args:
        markdown_content: A string containing the full Markdown content of the PDF.
        pdf_title: The title of the PDF, used for the filename.

    Returns:
        str: The public URL of the uploaded PDF.
    """
    try:
        pdf_bytes = io.BytesIO()
        html_content = markdown2.markdown(markdown_content)
        HTML(string=html_content).write_pdf(
            pdf_bytes,
            stylesheets=[
                CSS(
                    string="""
            body { font-family: Arial, sans-serif; margin: 0.5in; }
            h1, h2, h3 { color: #333; }
            img { max-width: 100%; height: auto; display: block; margin: 0 auto; }
            .section { margin-bottom: 1em; }
        """
                )
            ],
        )
        pdf_bytes.seek(0)

        file_name = (
            pdf_title.replace(" ", "_").lower() + "_" + str(uuid.uuid1())[:6] + ".pdf"
        )
        os.makedirs(local_dir, exist_ok=True)
        file_path = os.path.join(local_dir, file_name)

        # Save locally
        _save_to_file(file_path, pdf_bytes)

        # Upload to cloud
        public_url = _save_to_cloud(file_path, remote_file_dir=remote_dir)

        print(f"PDF uploaded to: {public_url}")
        return public_url

    except Exception as e:
        print(f"Error generating or uploading PDF: {e}")
        return ""


# create the generated directory if it doesn't exist
os.makedirs(get_generated_directory(), exist_ok=True)

if __name__ == "__main__":
    gen_dir = get_generated_directory()
    print(f"Generated directory: {gen_dir}")
