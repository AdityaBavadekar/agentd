import io
import json
import os
import re
import uuid

import dotenv
import markdown2
from weasyprint import CSS, HTML

from .cloud_storage import GCPStorage
from .link_utils import (
    extract_all_urls,
    extract_and_replace_urls,
    resolve_redirect,
    restore_urls_from_placeholders,
)
from .links_injector_agent import LinkInjectorAgent

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


_PDF_CSS = """
<style>
body { font-family: sans-serif; margin: 0; padding: 0; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #aaa; padding: 8px; }
th { background: #f2f2f2; }
code { background: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
pre { background: #f4f4f4; padding: 10px; border-radius: 4px; }
img { border-radius: 18px; }

@page {
  @bottom-center {
    content: "Page " counter(page) " of  " counter(pages) " ";
    font-size: 10px;
    color: #555;
  }
}
.footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 30px;
  color: #555;
  font-weight: 600;
  font-size: 12px;
  text-align: center;
  padding-top: 5px;
}
</style>
"""


def create_and_upload_pdf(
    markdown_content: str,
    pdf_title: str,
    local_dir: str = "pdfs",
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
    local_dir = os.path.join(get_generated_directory(), local_dir)
    os.makedirs(local_dir, exist_ok=True)
    try:
        import markdown

        final_html = _PDF_CSS + markdown.markdown(
            markdown_content,
            extensions=["tables", "fenced_code", "codehilite"],
        )
        html_doc = HTML(string=final_html)

        file_name = (
            pdf_title.replace(" ", "_").lower() + "_" + str(uuid.uuid1())[:8] + ".pdf"
        )
        file_path = os.path.join(local_dir, file_name)

        # [FOR TESTING] save markdown content to a file
        with open(os.path.join(local_dir, f"{file_name[:-4]}_markdown.md"), "w") as f:
            f.write(markdown_content)

        # Save locally
        html_doc.write_pdf(file_path)
        # _save_to_file(file_path, pdf_bytes)

        # Upload to cloud
        public_url = _save_to_cloud(file_path, remote_file_dir=remote_dir)

        print(f"PDF uploaded to: {public_url}")
        return public_url

    except Exception as e:
        print(f"Error generating or uploading PDF: {e}")
        return ""


# create the generated directory if it doesn't exist
os.makedirs(get_generated_directory(), exist_ok=True)
