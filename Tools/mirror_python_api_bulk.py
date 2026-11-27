"""Mirror the Unreal Python API reference for this engine version, in bulk.

The index page lists every class the Python API exposes - several thousand of them. Fetching
them one at a time from inside a conversation is far too slow, so this walks the list, saves each
page as text with the navigation stripped, and keeps a manifest of what succeeded. It is safe to
re-run: anything already on disk is skipped.

The whole set is worth keeping because it is generated per release and the 5.8 pages match the
engine installed here, which is not true of tutorials or the manual. What the manual says can
drift by version; a signature cannot.

    python Tools/mirror_python_api_bulk.py            # everything
    python Tools/mirror_python_api_bulk.py --limit 400
"""

import argparse
import html as html_module
import os
import re
import time
import urllib.error
import urllib.request

OUT_DIR = "C:/Users/tk/Desktop/lingxujie/Docs/PythonAPI"
BASE = "https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
RETRIES = 3


def fetch(url, timeout=45):
    last = None
    for attempt in range(RETRIES):
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last = error
            time.sleep(1.5 * (attempt + 1))
    raise last if last else RuntimeError("unknown fetch failure")


def strip_html(raw):
    start = raw.find("<h1")
    if start < 0:
        start = raw.find("<body")
    if start < 0:
        start = 0
    end = raw.find("Table of Contents")
    body = raw[start:end] if end > start else raw[start:]

    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    body = re.sub(r"<style.*?</style>", "", body, flags=re.S)
    body = re.sub(r"<[^>]+>", "", body)
    body = html_module.unescape(body)
    body = body.replace("\u00b6", "")
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n\s*\n\s*\n+", "\n\n", body)
    return body.strip()


def discover_classes():
    """Read the index and pull out every class page link."""
    raw = fetch(BASE)
    names = re.findall(r'href="class/([A-Za-z0-9_]+)\.html"', raw)
    seen = []
    for name in names:
        if name not in seen:
            seen.append(name)
    return seen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    print("reading the index ...", flush=True)
    classes = discover_classes()
    print("index lists %d classes" % len(classes), flush=True)
    if args.limit:
        classes = classes[:args.limit]
        print("limiting to %d" % len(classes), flush=True)

    saved = skipped = failed = 0
    failures = []
    started = time.time()

    for position, name in enumerate(classes, 1):
        target = os.path.join(OUT_DIR, name + ".txt")
        if os.path.exists(target) and os.path.getsize(target) > 200:
            skipped += 1
            continue
        url = BASE + "class/" + name + ".html"
        try:
            raw = fetch(url)
        except Exception as error:  # noqa: BLE001
            failed += 1
            failures.append("%s: %s" % (name, str(error)[:70]))
            continue

        text = strip_html(raw)
        if len(text) < 120:
            failed += 1
            failures.append("%s: page looked empty" % name)
            continue

        header = "# unreal.%s  (UE 5.8 Python API)\n\nSource: %s\n\n" % (name, url)
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(header + text)
        saved += 1

        if position % 50 == 0:
            elapsed = time.time() - started
            print("  %d/%d  saved %d skipped %d failed %d  (%.0fs)"
                  % (position, len(classes), saved, skipped, failed, elapsed), flush=True)

    with open(os.path.join(OUT_DIR, "MANIFEST.txt"), "w", encoding="utf-8") as handle:
        handle.write("classes in index: %d\n" % len(classes))
        handle.write("saved now: %d\nskipped (already present): %d\nfailed: %d\n"
                     % (saved, skipped, failed))
        if failures:
            handle.write("\nfailures:\n")
            for line in failures:
                handle.write("  %s\n" % line)

    print("DONE saved %d skipped %d failed %d in %.0fs"
          % (saved, skipped, failed, time.time() - started), flush=True)


if __name__ == "__main__":
    main()
