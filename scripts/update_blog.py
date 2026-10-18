"""네이버 블로그 RSS를 읽어 assets/blog.json 을 만듭니다. (GitHub Actions에서 주기적으로 실행)"""
import json, re, html, urllib.request
from email.utils import parsedate_to_datetime

BLOGS = [
    {"id": "main", "name": "삼성스마트신경과 대표 블로그", "url": "https://blog.naver.com/smartdr2", "rss": "https://rss.blog.naver.com/smartdr2.xml", "count": 3},
    {"id": "busan", "name": "삼성스마트신경과 부산점", "url": "https://blog.naver.com/smartneuro3", "rss": "https://rss.blog.naver.com/smartneuro3.xml", "count": 6},
    {"id": "director", "name": "원장 블로그", "url": "https://blog.naver.com/smart_neuro", "rss": "https://rss.blog.naver.com/smart_neuro.xml", "count": 3},
    {"id": "sleep", "name": "부산점 수면센터", "url": "https://blog.naver.com/smartneuro2", "rss": "https://rss.blog.naver.com/smartneuro2.xml", "count": 3},
]


def text(s):
    s = re.sub(r"<!\[CDATA\[|\]\]>", "", s or "")
    return html.unescape(re.sub(r"<[^>]+>", " ", html.unescape(s))).strip()


def tag(item, name):
    m = re.search(rf"<{name}>(.*?)</{name}>", item, re.S)
    return m.group(1) if m else ""


out = {"blogs": []}
for b in BLOGS:
    req = urllib.request.Request(b["rss"], headers={"User-Agent": "Mozilla/5.0"})
    xml = urllib.request.urlopen(req, timeout=20).read().decode("utf-8")
    posts = []
    for item in re.findall(r"<item>(.*?)</item>", xml, re.S)[: b["count"]]:
        desc = html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", tag(item, "description")))
        img = re.search(r'src="(https://blogthumb[^"]+)"', desc)
        link = text(tag(item, "link")).split("?")[0]
        summary = re.sub(r"\s+", " ", text(desc))[:90]
        try:
            date = parsedate_to_datetime(text(tag(item, "pubDate"))).strftime("%Y.%m.%d")
        except Exception:
            date = ""
        posts.append({"title": text(tag(item, "title")), "link": link, "date": date, "summary": summary,
                      "thumb": img.group(1) if img else ""})
    out["blogs"].append({k: b[k] for k in ("id", "name", "url")} | {"posts": posts})

with open("assets/blog.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("updated", [(b["id"], len(b["posts"])) for b in out["blogs"]])
