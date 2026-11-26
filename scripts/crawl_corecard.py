
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse, parse_qs, parse_qsl, urlencode, urlunparse

import argparse
import json
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from inspect_corecard_fields import parse_corecard_html


BASE_URL = "https://developer.corecard.com/"
REGION_ID = "1"

HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def download_page(url):
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urlopen(request, timeout=30) as response:
        return response.read()


def enforce_usa_region(url):
    """Ensure every discovered CoreCard URL is scoped to USA."""
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query))

    query["regionId"] = REGION_ID

    return urlunparse(
        parsed._replace(query=urlencode(query))
    )


def extract_categories(guide_path, document_type):
    soup = BeautifulSoup(
        guide_path.read_text(encoding="utf-8"),
        "html.parser"
    )

    categories = []
    seen = set()

    for link in soup.select("a[href]"):
        href = link.get("href", "")

        if "type=SubCategory" not in href:
            continue

        if document_type == "webhook":
            if "CoreCardWEBHook" not in href:
                continue
        elif "GuidePage" not in href:
            continue

        url = enforce_usa_region(urljoin(BASE_URL, href))

        if url in seen:
            continue

        seen.add(url)

        category_id = parse_qs(urlparse(url).query).get(
            "id", ["unknown"]
        )[0]

        categories.append({
            "id": category_id,
            "name": link.get_text(" ", strip=True),
            "url": url
        })

    return categories


def extract_document_links(html, document_type):
    soup = BeautifulSoup(html, "html.parser")

    selector = (
        'a[href*="WEBHookPageApiDetail"]'
        if document_type == "webhook"
        else 'a[href*="GuidePageApiDetail"]'
    )

    documents = []
    seen = set()

    for link in soup.select(selector):
        href = link.get("href")

        if not href:
            continue

        url = enforce_usa_region(urljoin(BASE_URL, href))

        if url in seen:
            continue

        seen.add(url)

        document_id = parse_qs(urlparse(url).query).get(
            "id", ["unknown"]
        )[0]

        name = link.get_text(" ", strip=True)

        documents.append({
            "id": document_id,
            "name": name or f"document-{document_id}",
            "url": url
        })

    return documents


def normalize_filename(name):
    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "-",
        name
    ).strip("-").lower()


def crawl_section(
    section,
    guide_path,
    output_dir,
    document_type
):
    if not guide_path.exists():
        print(f"Guide not found: {guide_path}")
        return {
            "discovered": 0,
            "success": 0,
            "failed": 0
        }

    section_dir = output_dir / section
    section_dir.mkdir(parents=True, exist_ok=True)

    categories = extract_categories(
        guide_path,
        document_type
    )

    print(f"\n{'=' * 60}")
    print(f"Section: {section}")
    print(f"Document type: {document_type}")
    print(f"Categories found: {len(categories)}")
    print(f"{'=' * 60}")

    processed_urls = set()

    discovered_count = 0
    success_count = 0
    failed_count = 0

    for category in categories:
        print(
            f"\nCategory: {category['name']} "
            f"(ID: {category['id']})"
        )

        try:
            category_html = download_page(category["url"])
            categories_dir = section_dir / "categories"
            categories_dir.mkdir(parents=True, exist_ok=True)

            category_filename = (
                f"{normalize_filename(category['name'])}-"
                f"{category['id']}.html"
            )

            category_path = categories_dir / category_filename
            category_path.write_bytes(category_html)
        except Exception as error:
            print(f"Failed to download category: {error}")
            failed_count += 1
            continue

        documents = extract_document_links(
            category_html,
            document_type
        )

        print(f"Found {len(documents)} documents")

        for document in documents:
            if document["url"] in processed_urls:
                continue

            processed_urls.add(document["url"])
            discovered_count += 1

            filename = (
                f"{normalize_filename(document['name'])}-"
                f"{document['id']}"
            )

            html_path = section_dir / f"{filename}.html"
            json_path = section_dir / f"{filename}.json"

            try:
                html = download_page(document["url"])
                html_path.write_bytes(html)

                normalized_data = parse_corecard_html(
                    html_path
                )

                normalized_data["source"] = {
                    "vendor": "CoreCard",
                    "document_type": document_type,
                    "section": section,
                    "category": category["name"],
                    "category_id": category["id"],
                    "document_id": document["id"],
                    "region_id": REGION_ID,
                    "region": "USA",
                    "url": document["url"]
                }

                json_path.write_text(
                    json.dumps(
                        normalized_data,
                        indent=4,
                        ensure_ascii=False
                    ),
                    encoding="utf-8"
                )

                success_count += 1

                print(
                    f"  Processed: {document['name']}"
                )

            except Exception as error:
                failed_count += 1

                print(
                    f"  Failed: {document['name']} — {error}"
                )

    result = {
        "discovered": discovered_count,
        "success": success_count,
        "failed": failed_count
    }

    print(f"\n{section} summary")
    print(f"Discovered: {discovered_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Crawl CoreCard USA API and webhook documentation"
    )

    parser.add_argument(
        "--credit-guide",
        default="documents/corecard/apis/credit/guide.html"
    )

    parser.add_argument(
        "--prepaid-debit-guide",
        default="documents/corecard/apis/prepaid-debit/guide.html"
    )

    parser.add_argument(
        "--credit-webhook-guide",
        default="documents/corecard/webhooks/credit/guide.html"
    )

    parser.add_argument(
        "--output-dir",
        default="documents/corecard"
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    results = {}

    results["credit"] = crawl_section(
        "apis/credit",
        Path(args.credit_guide),
        output_dir,
        "api"
    )

    results["prepaid-debit"] = crawl_section(
        "apis/prepaid-debit",
        Path(args.prepaid_debit_guide),
        output_dir,
        "api"
    )

    results["credit-webhooks"] = crawl_section(
        "webhooks/credit",
        Path(args.credit_webhook_guide),
        output_dir,
        "webhook"
    )

    print("\n========== FINAL SUMMARY ==========")

    for section, result in results.items():
        print(
            f"{section}: "
            f"{result['success']}/{result['discovered']} successful, "
            f"{result['failed']} failed"
        )


if __name__ == "__main__":
    main()
