"""Fill the 'Latest Projects' section of README.md with the user's 2 most recently updated repos."""
import html
import json
import os
import re
import urllib.request

USER = os.environ.get("GH_USER", "Moazamuddin12")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
COUNT = 2
START, END = "<!-- PROJECTS:START -->", "<!-- PROJECTS:END -->"


def fetch_repos():
    url = f"https://api.github.com/users/{USER}/repos?sort=pushed&direction=desc&per_page=30&type=owner"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def build_block(repos):
    cells = []
    for r in repos:
        name = html.escape(r["name"])
        desc = html.escape(r.get("description") or "No description added yet.")
        lang = html.escape(r.get("language") or "Not specified")
        stars = r.get("stargazers_count", 0)
        cells.append(
            f'    <td width="50%" valign="top">\n'
            f'      <h3>📁 <a href="{r["html_url"]}">{name}</a></h3>\n'
            f"      <p>{desc}</p>\n"
            f"      <p><b>Language:</b> {lang} · ⭐ {stars}</p>\n"
            f"    </td>"
        )
    return "<table>\n  <tr>\n" + "\n".join(cells) + "\n  </tr>\n</table>"


def main():
    repos = [
        r for r in fetch_repos()
        if not r["fork"] and r["name"].lower() != USER.lower()
    ][:COUNT]
    if not repos:
        print("No repositories found; leaving README unchanged.")
        return

    with open("README.md", encoding="utf-8") as f:
        text = f.read()

    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        raise SystemExit("Markers not found in README.md")

    new_text = pattern.sub(lambda _: f"{START}\n{build_block(repos)}\n{END}", text)
    if new_text != text:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_text)
        print("README updated.")
    else:
        print("No changes.")


if __name__ == "__main__":
    main()
