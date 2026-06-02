import requests

import logging
import time
from cache import get_cache, set_cache
TIMEOUT = 5
MAX_RETRIES = 3
BACKOFF_FACTOR = 2






def safe_get(url: str):
    #  Check cache first
    cached = get_cache(url)
    if cached:
        logging.info("Cache hit")
        return cached

    delay = 1

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            res = requests.get(url, timeout=TIMEOUT)

            if res.status_code == 403:
                logging.warning(f"Attempt {attempt}: Rate limited")
                time.sleep(delay)
                delay *= BACKOFF_FACTOR
                continue

            res.raise_for_status()

            # 💾 Store in cache
            set_cache(url, res)

            return res

        except requests.exceptions.Timeout:
            logging.warning(f"Attempt {attempt}: Timeout")

        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt}: Failed {str(e)}")

        time.sleep(delay)
        delay *= BACKOFF_FACTOR

    logging.error("All retries failed")
    return None

def read_github_repo(repo_url: str):
    cache_key = f"readme:{repo_url}"

    cached = get_cache(cache_key)
    if cached:
        logging.info("README cache hit")
        return cached

    try:
        parts = repo_url.replace("https://github.com/", "").split("/")

        if len(parts) < 2:
            return "No README found"

        owner, repo = parts[0], parts[1]

        url = f"https://api.github.com/repos/{owner}/{repo}/readme"

        res = safe_get(url)

        if not res:
            return "No README found"

        try:
            import base64
            readme = base64.b64decode(res.json()["content"]).decode("utf-8")

            # 💾 cache processed result
            set_cache(cache_key, readme)

            return readme

        except Exception:
            return "No README found"

    except Exception:
        return "No README found"

def get_repo_metadata(repo_url: str):
    try:
        parts = repo_url.replace("https://github.com/", "").split("/")
        owner, repo = parts[0], parts[1]

        url = f"https://api.github.com/repos/{owner}/{repo}"
        res = requests.get(url)

        if res.status_code == 200:
            data = res.json()
            return {
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "language": data.get("language", "unknown")
            }
    except:
        pass

    return {"stars": 0, "forks": 0, "language": "unknown"}


def readme_quality_score(readme: str):
    score = 0
    if len(readme) > 500:
        score += 1
    if "##" in readme:
        score += 1
    if "```" in readme:
        score += 1
    return score


def extract_title(readme):
    for line in readme.split("\n"):
        if line.startswith("#"):
            return line.replace("#", "").strip()
    return "Untitled Project"

import re

def extract_summary(readme):
    if not readme:
        return "No summary available"

    # remove markdown headers
    text = re.sub(r"^#+\s*", "", readme, flags=re.MULTILINE)

    # remove bullet points
    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip() and not line.strip().startswith(("-", "*"))
    ]

    text = " ".join(lines)

    # split into sentences (simple but effective)
    sentences = re.split(r"(?<=[.!?])\s+", text)

    summary = []
    length = 0
    MAX_LEN = 400

    for s in sentences:
        if length + len(s) > MAX_LEN:
            break
        summary.append(s)
        length += len(s)

    return " ".join(summary).strip()

def extract_tags(readme):
    words = re.findall(r'\b[a-zA-Z]{4,}\b', readme.lower())

    stopwords = {
        "this","that","with","from","have","will",
        "your","about","using","project","https","http","www","com","lesson"
    }

    keywords = [w for w in words if w not in stopwords]

    freq = {}
    for w in keywords:
        freq[w] = freq.get(w, 0) + 1

    return sorted(freq, key=freq.get, reverse=True)[:5]

