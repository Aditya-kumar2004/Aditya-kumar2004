import os
import re
import requests
import json
from datetime import datetime

GITHUB_USERNAME = "Aditya-kumar2004"
GITHUB_TOKEN = os.environ.get("GH_TOKEN", "")

LANGUAGE_COLORS = {
    "JavaScript": "#f1e05a",
    "TypeScript": "#2b7489",
    "Python": "#3572A5",
    "Java": "#b07219",
    "C++": "#f34b7d",
    "PHP": "#4F5D95",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Shell": "#89e051",
    "Jupyter Notebook": "#DA5B0B",
}

LANGUAGE_ICONS = {
    "JavaScript": "js",
    "TypeScript": "typescript",
    "Python": "python",
    "Java": "java",
    "C++": "cpp",
    "PHP": "php",
    "HTML": "html",
    "CSS": "css",
    "Shell": "bash",
    "Jupyter Notebook": "jupyter",
}

TOPIC_EMOJI = {
    "react": "⚛️",
    "django": "🐍",
    "node": "🟢",
    "api": "🔌",
    "machine-learning": "🤖",
    "ai": "🧠",
    "fullstack": "🌐",
    "game": "🎮",
    "database": "🗄️",
    "blockchain": "⛓️",
    "mobile": "📱",
    "web": "🌍",
    "laravel": "🔴",
    "nextjs": "▲",
    "mongodb": "🍃",
    "postgresql": "🐘",
    "docker": "🐳",
    "graphql": "◈",
}


def get_repos():
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
    params = {
        "sort": "updated",
        "direction": "desc",
        "per_page": 100,
        "type": "owner",
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error fetching repos: {response.status_code}")
        print(response.text)
        return []

    repos = response.json()
    # Filter out forked repos and the profile repo itself
    filtered = [
        r for r in repos
        if not r.get("fork", False)
        and r["name"] != GITHUB_USERNAME
        and not r.get("private", False)
    ]
    return filtered


def get_lang_badge(language):
    if not language:
        return ""
    color = LANGUAGE_COLORS.get(language, "#858585")
    color_hex = color.replace("#", "")
    return f"![{language}](https://img.shields.io/badge/{language.replace('+', '%2B').replace(' ', '%20')}-{color_hex}?style=flat-square&logo={LANGUAGE_ICONS.get(language, 'code')}&logoColor=white)"


def get_topic_emojis(topics):
    emojis = []
    for topic in topics[:3]:
        for key, emoji in TOPIC_EMOJI.items():
            if key in topic.lower():
                emojis.append(emoji)
                break
    return " ".join(emojis) if emojis else "💻"


def format_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%b %Y")


def stars_badge(count):
    if count == 0:
        return ""
    return f"![Stars](https://img.shields.io/badge/⭐%20{count}-stars-yellow?style=flat-square)"


def forks_badge(count):
    if count == 0:
        return ""
    return f"![Forks](https://img.shields.io/badge/🍴%20{count}-forks-blue?style=flat-square)"


def generate_project_cards(repos):
    if not repos:
        return "> No public repositories found yet. Stay tuned! 🚧"

    cards = []
    cards.append('<div align="center">')
    cards.append("")
    cards.append(
        "| 🗂️ Project | 📝 Description | 🛠️ Stack | 📅 Updated |"
    )
    cards.append(
        "|-----------|---------------|----------|------------|"
    )

    for repo in repos:
        name = repo["name"]
        desc = repo.get("description") or "No description provided."
        # Truncate long descriptions
        if len(desc) > 80:
            desc = desc[:77] + "..."
        url = repo["html_url"]
        language = repo.get("language", "")
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        updated = format_date(repo["updated_at"])
        topics = repo.get("topics", [])
        homepage = repo.get("homepage", "")

        # Build name cell with emoji
        emoji = get_topic_emojis(topics)
        name_cell = f"{emoji} [**{name}**]({url})"
        if homepage:
            name_cell += f" · [🔗 Live]({homepage})"

        # Stars/forks inline
        meta = []
        if stars:
            meta.append(f"⭐ {stars}")
        if forks:
            meta.append(f"🍴 {forks}")
        if meta:
            name_cell += f"<br/>`{'  '.join(meta)}`"

        # Language badge
        lang_cell = get_lang_badge(language) if language else "`–`"

        cards.append(
            f"| {name_cell} | {desc} | {lang_cell} | `{updated}` |"
        )

    cards.append("")
    cards.append("</div>")
    cards.append("")
    cards.append(
        f"> 🤖 *Auto-generated on {datetime.utcnow().strftime('%d %B %Y at %H:%M UTC')} · {len(repos)} public repos*"
    )

    return "\n".join(cards)


def update_readme(content):
    readme_path = "README.md"
    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()

    pattern = r"<!-- PROJECTS:START -->.*?<!-- PROJECTS:END -->"
    replacement = f"<!-- PROJECTS:START -->\n{content}\n<!-- PROJECTS:END -->"
    new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_readme)

    print("✅ README.md updated successfully!")


def main():
    print(f"🔍 Fetching repos for {GITHUB_USERNAME}...")
    repos = get_repos()
    print(f"📦 Found {len(repos)} public repos")

    cards = generate_project_cards(repos)
    update_readme(cards)


if __name__ == "__main__":
    main()
