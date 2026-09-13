#!/usr/bin/env python3
"""
Static site builder for a minimal DevOps/Platform engineer portfolio.

Content lives in content/*.md (and content/projects/*.md) as plain
Markdown + simple `key: value` front matter. Run this after editing
any content file:

    python3 build.py

Output is written to the repo root (index.html + resume.html),
which is what GitHub Pages serves directly from this branch. No other build step is needed.
"""
import re
import shutil
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
OUTPUT = ROOT / "_site"  # uploaded as the Pages artifact by the GitHub Actions workflow

md = markdown.Markdown(extensions=["extra", "sane_lists"])


def render_md(text: str) -> str:
    md.reset()
    return md.convert(text.strip())


def load_profile() -> dict:
    return yaml.safe_load((CONTENT / "profile.yml").read_text())


def load_simple_md(name: str) -> str:
    return render_md((CONTENT / name).read_text())


def split_sections(text: str) -> list[tuple[str, str]]:
    """Split a markdown file into (## Heading, body) sections."""
    parts = re.split(r"^##\s+(.+)$", text, flags=re.MULTILINE)
    sections = []
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1].strip()
        sections.append((heading, body))
    return sections


def parse_front_matter_block(block: str) -> tuple[dict, str]:
    """Parse a `key: value` header followed by `---` then a markdown body."""
    header, _, body = block.partition("\n---\n")
    meta = {}
    for line in header.strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, body.strip()


def load_experience() -> list[dict]:
    raw = (CONTENT / "experience.md").read_text()
    jobs = []
    for block in raw.split("\n===\n"):
        meta, body = parse_front_matter_block(block)
        meta["bullets_html"] = render_md(body)
        jobs.append(meta)
    return jobs


def load_projects() -> list[dict]:
    projects = []
    for path in sorted((CONTENT / "projects").glob("*.md")):
        meta, body = parse_front_matter_block(path.read_text())
        meta["tags"] = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
        meta["description_html"] = render_md(body)
        projects.append(meta)
    return projects


def load_skill_groups() -> list[dict]:
    text = (CONTENT / "skills.md").read_text()
    return [{"category": h, "skills": [i.strip() for i in b.split(",")]} for h, b in split_sections(text)]


def load_credentials() -> dict:
    text = (CONTENT / "credentials.md").read_text()
    sections = dict(split_sections(text))
    return {
        "certifications": render_md(sections.get("Certifications", "")),
        "education": render_md(sections.get("Education", "")),
    }


def build():
    profile = load_profile()
    about_html = load_simple_md("about.md")
    skills = load_skill_groups()
    experience = load_experience()
    projects = load_projects()
    credentials = load_credentials()

    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), trim_blocks=True, lstrip_blocks=True)
    context = {
        "profile": profile,
        "about_html": about_html,
        "skills": skills,
        "experience": experience,
        "projects": projects,
        "credentials": credentials,
    }

    OUTPUT.mkdir(exist_ok=True)

    for template_name, out_name in [("index.html.j2", "index.html"), ("resume.html.j2", "resume.html")]:
        html = env.get_template(template_name).render(**context)
        (OUTPUT / out_name).write_text(html)

    dest_assets = OUTPUT / "assets"
    if dest_assets.exists():
        shutil.rmtree(dest_assets)
    shutil.copytree(ROOT / "assets", dest_assets)

    (OUTPUT / ".nojekyll").touch()

    print(f"Built site at repo root {OUTPUT}/ ({len(projects)} projects, {len(experience)} roles)")


if __name__ == "__main__":
    build()
