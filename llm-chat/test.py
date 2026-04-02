import argparse
import base64
import json
import subprocess
import tempfile
from pathlib import Path

from openai import OpenAI

client = OpenAI(base_url="http://localhost:8080/v1", api_key="unused")

SCHEMA = {
    "type": "object",
    "properties": {
        "year": {"type": "integer"},
        "month": {"type": "integer"},
        "day": {"type": "integer"},
        "description": {"type": "string"},
    },
    "required": ["year", "month", "day", "description"],
    "additionalProperties": False,
}


def pdf_to_images(pdf_path: str) -> list[str]:
    tmp = tempfile.mkdtemp()
    subprocess.run(
        ["pdftoppm", pdf_path, f"{tmp}/page", "-png"],
        check=True,
    )
    pages = sorted(Path(tmp).glob("page-*.png"))
    encoded = []
    for page in pages:
        encoded.append(base64.b64encode(page.read_bytes()).decode())
    return encoded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", help="Path to the PDF file")
    args = parser.parse_args()

    images = pdf_to_images(args.pdf)

    content = []
    for img in images:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{img}"},
        })
    content.append({
        "type": "text",
        "text": "Extract the date referenced in this document. For the description, write a descriptive title for this file — not too concise, but enough information that someone browsing a folder of documents could understand what it is at a glance. Should be no more than 4 to 7 words",
    })

    response = client.chat.completions.create(
        model="gemma-4-E4B",
        messages=[{"role": "user", "content": content}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "document_info", "strict": True, "schema": SCHEMA},
        },
    )

    result = json.loads(response.choices[0].message.content)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
