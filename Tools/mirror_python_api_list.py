"""Mirror the curated list of Python API classes.

The full reference holds 11,675 pages and the documentation server answers roughly one per nine
seconds, so copying it all would take about a day. The curated list in python_api_classes.py
covers the editor scripting surface this project uses, and takes a few minutes.

Safe to re-run: pages already on disk are left alone, so an interrupted run resumes.

    python Tools/mirror_python_api_list.py
"""

import html as html_module
import os
import re
import time
import urllib.error
import urllib.request

from python_api_classes import CLASSES

OUT_DIR = "C:/Users/tk/Desktop/lingxujie/Docs/PythonAPI"
BASE = "https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/"
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
            time.sleep(1.2 * (attempt + 1))
    raise last if last else RuntimeError("unknown failure")


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
    body = html_module.unescape(body).replace("\u00b6", "")
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n\s*\n\s*\n+", "\n\n", body)
    return body.strip()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    wanted = []
    for name in CLASSES:
        if name not in wanted:
            wanted.append(name)

    print("curated list: %d classes" % len(wanted), flush=True)
    saved = skipped = failed = 0
    failures = []
    started = time.time()

    for position, name in enumerate(wanted, 1):
        target = os.path.join(OUT_DIR, name + ".txt")
        if os.path.exists(target) and os.path.getsize(target) > 200:
            skipped += 1
            continue

        url = BASE + name + ".html"
        try:
            raw = fetch(url)
        except Exception as error:  # noqa: BLE001
            failed += 1
            failures.append("%s: %s" % (name, str(error)[:70]))
            print("  FAIL %s" % name, flush=True)
            continue

        text = strip_html(raw)
        if len(text) < 120:
            failed += 1
            failures.append("%s: empty page" % name)
            print("  EMPTY %s" % name, flush=True)
            continue

        header = "# unreal.%s  (UE 5.8 Python API)\n\nSource: %s\n\n" % (name, url)
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(header + text)
        saved += 1
        print("  [%d/%d] %s" % (position, len(wanted), name), flush=True)

    with open(os.path.join(OUT_DIR, "MANIFEST.txt"), "w", encoding="utf-8") as handle:
        handle.write("curated classes requested: %d\n" % len(wanted))
        handle.write("saved: %d\nskipped: %d\nfailed: %d\n" % (saved, skipped, failed))
        if failures:
            handle.write("\nfailures:\n")
            for line in failures:
                handle.write("  %s\n" % line)

    print("DONE saved %d skipped %d failed %d in %.0fs"
          % (saved, skipped, failed, time.time() - started), flush=True)


if __name__ == "__main__":
    main()
