
from bs4 import BeautifulSoup
from pathlib import Path
import argparse
import re
import json


def get_indent_level(field_cell):
    style = field_cell.get("style", "")
    match = re.search(r"padding-left:\s*(\d+)px", style)

    if not match:
        return 0

    return int(match.group(1)) // 25


def extract_required(field_cell):
    if field_cell.select_one(".red"):
        return True

    if field_cell.select_one(".green"):
        return False

    return None


def extract_api_metadata(article):
    name_element = (
        article.select_one("h4#h4APIName")
        or article.select_one("h4.h4-name")
    )

    action_element = article.select_one(".action-url")

    if action_element is None:
        raise ValueError("Could not find API action details")

    description_element = action_element.find_next_sibling("div")
    method_element = action_element.select_one("p:nth-of-type(1) code")
    endpoint_element = action_element.select_one("p:nth-of-type(2) code")

    return {
        "name": (
            name_element.get("value")
            or name_element.get_text(strip=True)
            if name_element else None
        ),
        "http_method": (
            method_element.get_text(strip=True)
            if method_element else None
        ),
        "endpoint": (
            endpoint_element.get_text(strip=True)
            if endpoint_element else None
        ),
        "description": (
            description_element.get_text(" ", strip=True)
            if description_element else None
        ),
    }


def extract_fields(table):
    fields = []

    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td", recursive=False)

        if len(cells) < 2:
            continue

        field_cell, description_cell = cells

        name_element = (
            field_cell.select_one(".field-src")
            or field_cell.find("p")
        )

        type_element = field_cell.find(
            "span",
            style=lambda value: value and "italic" in value
        )

        fields.append({
            "name": (
                name_element.get_text(strip=True)
                if name_element else None
            ),
            "type": (
                type_element.get_text(strip=True)
                if type_element else None
            ),
            "required": extract_required(field_cell),
            "description": description_cell.get_text(" ", strip=True),
            "indent_level": get_indent_level(field_cell),
        })

    return fields


def build_nested_fields(fields):
    root = []
    stack = []

    for field in fields:
        level = field["indent_level"]

        node = {
            "name": field["name"],
            "type": field["type"],
            "required": field["required"],
            "description": field["description"],
            "children": []
        }

        while stack and stack[-1]["level"] >= level:
            stack.pop()

        if stack:
            stack[-1]["node"]["children"].append(node)
        else:
            root.append(node)

        stack.append({
            "level": level,
            "node": node
        })

    return root


def extract_sample(article, selector):
    element = article.select_one(selector)

    if element is None:
        return None

    raw_text = element.get_text("", strip=False).strip()

    # Find the JSON object or array.
    start_positions = [
        pos for pos in (
            raw_text.find("{"),
            raw_text.find("["),
        )
        if pos != -1
    ]

    if not start_positions:
        return None

    start = min(start_positions)

    opening = raw_text[start]
    closing = "}" if opening == "{" else "]"

    end = raw_text.rfind(closing)

    if end == -1:
        return None

    json_text = raw_text[start:end + 1]

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in sample {selector}: {error}"
        ) from error

def parse_corecard_html(input_path):
    soup = BeautifulSoup(
        input_path.read_text(encoding="utf-8"),
        "html.parser"
    )

    article = soup.select_one("main#center article")

    if article is None:
        raise ValueError(
            f"Could not find API article in {input_path}"
        )

    tables = article.find_all("table")

    if not tables:
        raise ValueError(
            f"Could not find request fields table in {input_path}"
        )

    metadata = extract_api_metadata(article)

    request_fields = [
        {
            key: value
            for key, value in field.items()
            if key != "indent_level"
        }
        for field in extract_fields(tables[0])
    ]

    response_fields = (
        build_nested_fields(extract_fields(tables[1]))
        if len(tables) >= 2 else None
    )

    return {
        "metadata": metadata,
        "request_fields": request_fields,
        "response_fields": response_fields,
        "sample_request": extract_sample(article, ".pre-req"),
        "sample_response": extract_sample(article, ".pre-res"),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Parse CoreCard API HTML documentation"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input HTML file not found: {input_path}"
        )

    result = parse_corecard_html(input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(result, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"API: {result['metadata']['name']}")
    print(f"Request fields: {len(result['request_fields'])}")
    print(f"Normalized API document saved to: {output_path}")


if __name__ == "__main__":
    main()
