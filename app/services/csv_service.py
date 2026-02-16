import csv
from io import StringIO


def parse_links_csv(content: bytes) -> list[str]:
    text = content.decode("utf-8", errors="ignore")
    reader = csv.reader(StringIO(text))
    links = []
    for row in reader:
        if not row:
            continue
        link = row[0].strip()
        if link and not link.lower().startswith("http"):
            continue
        if link:
            links.append(link)
    return links
