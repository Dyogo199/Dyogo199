#!/usr/bin/env python3
"""Generate self-hosted GitHub profile statistics SVG cards.

The script uses only the GitHub REST API and the Python standard library.
It intentionally avoids third-party card services so profile rendering does not
depend on an external deployment.

If PROFILE_STATS_TOKEN is configured and authenticates as GITHUB_USERNAME, the
script can include private repositories visible to that token. Otherwise it
falls back to public repository data using GITHUB_TOKEN.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

API_BASE = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
USERNAME = os.getenv("GITHUB_USERNAME", "Dyogo199")
TOKEN = os.getenv("PROFILE_STATS_TOKEN") or os.getenv("GITHUB_TOKEN", "")
OUTPUT_DIR = Path(os.getenv("PROFILE_STATS_OUTPUT", "profile"))

BG = "#0D1117"
BORDER = "#30363D"
TITLE = "#00BFBF"
TEXT = "#C9D1D9"
MUTED = "#8B949E"
ACCENT = "#00BFBF"

LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "Java": "#B07219",
    "Kotlin": "#A97BFF",
    "C": "#555555",
    "C++": "#F34B7D",
    "C#": "#178600",
    "JavaScript": "#F1E05A",
    "TypeScript": "#3178C6",
    "HTML": "#E34C26",
    "CSS": "#563D7C",
    "Rust": "#DEA584",
    "Shell": "#89E051",
    "Dockerfile": "#384D54",
    "Jupyter Notebook": "#DA5B0B",
    "VHDL": "#ADB2CB",
    "Verilog": "#B2B7F8",
}


def request_json(path: str, *, retries: int = 3) -> Any:
    url = path if path.startswith("http") else f"{API_BASE}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-stats",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:1000]
            last_error = RuntimeError(
                f"GitHub API request failed: HTTP {exc.code} for {url}\n{body}"
            )
            if exc.code not in {429, 500, 502, 503, 504} or attempt == retries:
                raise last_error from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt == retries:
                raise RuntimeError(f"GitHub API request failed for {url}: {exc}") from exc

        time.sleep(2 ** (attempt - 1))

    raise RuntimeError(str(last_error))


def paginated(path: str) -> list[dict[str, Any]]:
    separator = "&" if "?" in path else "?"
    page = 1
    items: list[dict[str, Any]] = []
    while True:
        batch = request_json(f"{path}{separator}per_page=100&page={page}")
        if not isinstance(batch, list):
            raise RuntimeError(f"Expected a list from GitHub API for {path}")
        items.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return items


def authenticated_as_target() -> bool:
    if not TOKEN:
        return False
    try:
        viewer = request_json("/user", retries=1)
    except Exception as exc:  # GITHUB_TOKEN normally identifies an app/bot.
        print(f"Token identity check skipped: {exc}", file=sys.stderr)
        return False
    return str(viewer.get("login", "")).lower() == USERNAME.lower()


def load_repositories() -> tuple[list[dict[str, Any]], bool]:
    include_private = authenticated_as_target()
    if include_private:
        repos = paginated("/user/repos?visibility=all&affiliation=owner&sort=full_name")
        repos = [r for r in repos if str(r.get("owner", {}).get("login", "")).lower() == USERNAME.lower()]
    else:
        encoded = urllib.parse.quote(USERNAME, safe="")
        repos = paginated(f"/users/{encoded}/repos?type=owner&sort=full_name")

    # Archived repositories remain part of the account but are excluded from the
    # language portfolio because they no longer represent active work.
    return repos, include_private


def language_totals(repos: list[dict[str, Any]]) -> Counter[str]:
    totals: Counter[str] = Counter()
    for repo in repos:
        if repo.get("fork") or repo.get("archived"):
            continue
        full_name = repo.get("full_name")
        languages_url = repo.get("languages_url")
        if not full_name or not languages_url:
            continue
        try:
            languages = request_json(str(languages_url))
        except Exception as exc:
            print(f"Warning: unable to read languages for {full_name}: {exc}", file=sys.stderr)
            continue
        if isinstance(languages, dict):
            for language, byte_count in languages.items():
                if isinstance(byte_count, int) and byte_count > 0:
                    totals[str(language)] += byte_count
    return totals


def svg_header(width: int, height: int, title: str, subtitle: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
        "<style>",
        "text{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif}",
        ".title{font-size:18px;font-weight:700}",
        ".label{font-size:13px;font-weight:600}",
        ".value{font-size:18px;font-weight:700}",
        ".muted{font-size:11px}",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="8" fill="{BG}" stroke="{BORDER}"/>',
        f'<text x="24" y="34" class="title" fill="{TITLE}">{escape(title)}</text>',
        f'<text x="24" y="53" class="muted" fill="{MUTED}">{escape(subtitle)}</text>',
    ]


def render_stats(repos: list[dict[str, Any]], include_private: bool) -> str:
    profile = request_json(f"/users/{urllib.parse.quote(USERNAME, safe='')}")
    owned = [r for r in repos if not r.get("fork")]
    stars = sum(int(r.get("stargazers_count", 0) or 0) for r in owned)
    forks = sum(int(r.get("forks_count", 0) or 0) for r in owned)
    followers = int(profile.get("followers", 0) or 0)
    repo_count = len(repos) if include_private else int(profile.get("public_repos", len(repos)) or len(repos))

    subtitle = "GitHub REST API · private repositories included" if include_private else "GitHub REST API · public repository data"
    lines = svg_header(495, 190, f"{USERNAME}'s GitHub Stats", subtitle)

    metrics = [
        ("Repositories", repo_count, 24, 92),
        ("Total Stars", stars, 260, 92),
        ("Total Forks", forks, 24, 142),
        ("Followers", followers, 260, 142),
    ]
    for label, value, x, y in metrics:
        lines.append(f'<circle cx="{x+6}" cy="{y-4}" r="4" fill="{ACCENT}"/>')
        lines.append(f'<text x="{x+18}" y="{y}" class="label" fill="{TEXT}">{escape(label)}</text>')
        lines.append(f'<text x="{x+18}" y="{y+23}" class="value" fill="{TITLE}">{value:,}</text>')

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_languages(totals: Counter[str], include_private: bool) -> str:
    top = totals.most_common(8)
    total_bytes = sum(totals.values())
    subtitle = "GitHub Linguist data · private repositories included" if include_private else "GitHub Linguist data · public non-fork repositories"
    height = 92 + max(len(top), 1) * 27
    lines = svg_header(495, height, "Most Used Languages", subtitle)

    if not top or total_bytes <= 0:
        lines.append(f'<text x="24" y="88" class="label" fill="{TEXT}">No language data available.</text>')
        lines.append("</svg>")
        return "\n".join(lines) + "\n"

    for index, (language, byte_count) in enumerate(top):
        percentage = (byte_count / total_bytes) * 100
        y = 83 + index * 27
        color = LANGUAGE_COLORS.get(language, ACCENT)
        bar_width = max(2.0, 260.0 * percentage / 100.0)
        lines.append(f'<circle cx="28" cy="{y-4}" r="5" fill="{color}"/>')
        lines.append(f'<text x="41" y="{y}" class="label" fill="{TEXT}">{escape(language)}</text>')
        lines.append(f'<text x="448" y="{y}" text-anchor="end" class="label" fill="{MUTED}">{percentage:.1f}%</text>')
        lines.append(f'<rect x="180" y="{y-9}" width="260" height="5" rx="2.5" fill="{BORDER}"/>')
        lines.append(f'<rect x="180" y="{y-9}" width="{bar_width:.1f}" height="5" rx="2.5" fill="{color}"/>')

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def main() -> int:
    repos, include_private = load_repositories()
    print(f"Loaded {len(repos)} repositories for {USERNAME} (private included: {include_private}).")

    totals = language_totals(repos)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    stats_path = OUTPUT_DIR / "stats.svg"
    langs_path = OUTPUT_DIR / "top-langs.svg"
    stats_path.write_text(render_stats(repos, include_private), encoding="utf-8")
    langs_path.write_text(render_languages(totals, include_private), encoding="utf-8")

    print(f"Generated {stats_path}")
    print(f"Generated {langs_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
