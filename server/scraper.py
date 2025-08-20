# scraper.py
import requests
from bs4 import BeautifulSoup
import json
import sys

BASE_URLS = {
        "normal": "https://gall.dcinside.com/mgallery/board/lists/?id=sff",
        "hotdeal": "https://gall.dcinside.com/mgallery/board/lists/?id=sff&sort_type=N&search_head=100&page=1"
}
HEADERS = {"User-Agent": "Mozilla/5.0 (Window NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
INVALID_ICON_CLASSES = {"icon_survey", "icon_notice", "icon_ad"}

def scrape(mode="normal"):
    url = BASE_URLS.get(mode, BASE_URLS["normal"])
    print(url)
    res = requests.get(url, headers=HEADERS)
    # print(res.status_code)
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select("tr.ub-content")
    # print(f"[INFO] 수집 대상 게시글 수 :{len(rows)}")

    result = []
    for idx, row in enumerate(rows):
        # print(idx, row)
        tag_elem = row.select_one("td.gall_subject")
        if tag_elem == "SFFSFF후기": tag_elem = "후기"
        title_elem = row.select_one("td.gall_tit a")
        if len(title_elem) > 16: title_elem = title_elem[:17]
        date_elem = row.select_one("td.gall_date")
        icon_elem = row.select_one("td.gall_tit em[class^=icon_]")
        # print(idx, title_elem)
        if not title_elem or not date_elem:
            continue
        
        icon_classes = set(icon_elem.get("class", []))
        if icon_classes & INVALID_ICON_CLASSES:
            continue

        result.append({
            "tag": tag_elem.text.strip(),
            "title": title_elem.text.strip(),
            "date": date_elem['title'] if date_elem.has_attr('title') else date_elem.text.strip()
        })

        if len(result) >= 5:
            break
    # print(result)
    # return
    with open(f"data/data_{mode}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "normal"
    print(mode)
    scrape(mode)