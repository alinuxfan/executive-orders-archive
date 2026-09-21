import json
import os
import time
from pathlib import Path
import urllib.request

ROOT_DIR = Path(__file__).resolve().parent.parent
PORTRAITS_DIR = ROOT_DIR / "public" / "portraits"
PORTRAITS_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "ExecutiveOrdersPortraits/1.0 (Educational Project; mailto:contact@executiveorders.io)"
}

# Mapping of custom wiki article titles if needed
WIKI_OVERRIDES = {
    "donald-trump": "Donald_Trump",
    "william-henry-harrison": "William_Henry_Harrison",
    "franklin-d-roosevelt": "Franklin_D._Roosevelt",
    "harry-s-truman": "Harry_S._Truman",
    "dwight-d-eisenhower": "Dwight_D._Eisenhower",
    "john-f-kennedy": "John_F._Kennedy",
    "lyndon-b-johnson": "Lyndon_B._Johnson",
    "richard-nixon": "Richard_Nixon",
    "gerald-ford": "Gerald_Ford",
    "jimmy-carter": "Jimmy_Carter",
    "ronald-reagan": "Ronald_Reagan",
    "george-h-w-bush": "George_H._W._Bush",
    "bill-clinton": "Bill_Clinton",
    "george-w-bush": "George_W._Bush",
    "barack-obama": "Barack_Obama",
    "joe-biden": "Joe_Biden"
}

def download_all_portraits():
    with open(ROOT_DIR / "data" / "presidents.json", "r") as f:
        presidents = json.load(f)

    for p in presidents:
        slug = p["slug"]
        out_path = PORTRAITS_DIR / f"{slug}.jpg"
        if out_path.exists() and out_path.stat().st_size > 1000:
            print(f"Portrait already exists for {p['name']}")
            continue

        wiki_title = WIKI_OVERRIDES.get(slug, p["name"].replace(" ", "_"))
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_title}"
        
        try:
            req = urllib.request.Request(api_url, headers=HEADERS)
            with urllib.request.urlopen(req) as resp:
                data = json.load(resp)
            
            thumb_url = data.get("thumbnail", {}).get("source")
            if not thumb_url:
                print(f"No thumbnail found for {p['name']}")
                continue

            img_req = urllib.request.Request(thumb_url, headers=HEADERS)
            with urllib.request.urlopen(img_req) as img_resp:
                img_data = img_resp.read()

            with open(out_path, "wb") as f:
                f.write(img_data)

            print(f"Downloaded portrait for {p['name']} -> {out_path.name} ({len(img_data)} bytes)")
            time.sleep(0.2)
        except Exception as e:
            print(f"Failed to download portrait for {p['name']} ({wiki_title}): {e}")

if __name__ == "__main__":
    download_all_portraits()
