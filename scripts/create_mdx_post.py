#!/usr/bin/env python3
"""
Create a safe starter MDX blog post file.

Why this belongs in a frontend project:
Frontend teams often keep content in files, especially in Next.js/MDX blogs.
Python is useful as a small automation layer around that content. A script like
this can turn a title into a slug, add frontmatter metadata, and create a
consistent draft file without manually copying/pasting a template each time.

This script is intentionally beginner-friendly:
- It uses only Python's standard library.
- It previews by default, so running it will not write files accidentally.
- It refuses to overwrite an existing post.
- It keeps all generated content in content/blog/, away from the app source.
"""

from __future__ import annotations

import argparse
import re
import textwrap
from datetime import date
from pathlib import Path


# Path(__file__) is the path to this Python file.
# .resolve() turns it into an absolute path.
# .parents[1] means "go up two levels":
#   scripts/create_mdx_post.py -> scripts/ -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# This is where the generated MDX drafts will live.
# The current Pocket template does not read this folder yet. That is okay.
# We are creating the content shape now, then later we can teach Next.js to
# read from this folder and render posts.
BLOG_DIR = PROJECT_ROOT / "content" / "blog"


def create_slug(title: str) -> str:
    """Turn a human title into a URL/file-friendly slug.

    Example:
        "My First Python + Frontend Script!" -> "my-first-python-frontend-script"

    Frontend connection:
        Slugs often become route pieces, like /blog/my-first-post.
    """

    # Lowercase keeps URLs consistent.
    slug = title.lower()

    # Replace anything that is not a letter or number with a dash.
    # The "+" in "Python + Frontend" becomes "-".
    slug = re.sub(r"[^a-z0-9]+", "-", slug)

    # Remove extra dashes from the beginning or end.
    slug = slug.strip("-")

    # If someone enters only symbols, we still return a usable fallback.
    return slug or "untitled-post"


def estimate_reading_time(markdown: str, words_per_minute: int = 200) -> int:
    """Estimate reading time from plain text/markdown.

    This is a common content-site feature. Many blogs show something like
    "4 min read" beside the post date.
    """

    words = re.findall(r"\b\w+\b", markdown)

    # max(..., 1) keeps tiny drafts from showing "0 min read".
    return max(round(len(words) / words_per_minute), 1)


def build_mdx(title: str, description: str) -> str:
    """Build the text that will go inside the .mdx file."""

    today = date.today().isoformat()

    # This starter body is deliberately small. Later, you could add prompts,
    # tags, author fields, canonical URLs, image paths, or draft status.
    body = f"""
    This is a draft post created by a Python utility script.

    Use this space to write the article body in MDX. Because MDX supports
    Markdown plus React components, a frontend blog can later render this file
    as a real page.
    """

    reading_time = estimate_reading_time(body)

    # Frontmatter is the metadata block between the --- lines.
    # Next.js/MDX tooling can read this and use it for blog cards, SEO, sorting,
    # RSS feeds, search indexes, and social previews.
    clean_body = textwrap.dedent(body).strip()

    return f"""\
---
title: "{title}"
description: "{description}"
date: "{today}"
readingTime: "{reading_time} min read"
draft: true
---

# {title}

{clean_body}
"""


def parse_args() -> argparse.Namespace:
    """Define the command-line interface for the script.

    argparse is Python's built-in way to accept options from the terminal.
    """

    parser = argparse.ArgumentParser(
        description="Preview or create a beginner-friendly MDX blog draft.",
    )

    parser.add_argument(
        "title",
        help='Post title, for example: "My First Python Content Script"',
    )

    parser.add_argument(
        "--description",
        default="Draft generated from a small Python content utility.",
        help="Short metadata description for the post.",
    )

    parser.add_argument(
        "--write",
        action="store_true",
        help="Actually create the .mdx file. Without this, the script only previews.",
    )

    return parser.parse_args()


def main() -> None:
    """Run the script from top to bottom.

    Execution flow:
    1. Read the title/options from the terminal.
    2. Convert the title into a slug.
    3. Build the MDX content.
    4. Preview the target file path.
    5. Only write the file if --write was provided.
    """

    args = parse_args()

    slug = create_slug(args.title)
    target_path = BLOG_DIR / f"{slug}.mdx"
    mdx = build_mdx(args.title, args.description)

    print("\nMDX draft generator")
    print("-------------------")
    print(f"Title:      {args.title}")
    print(f"Slug:       {slug}")
    print(f"Target:     {target_path.relative_to(PROJECT_ROOT)}")

    if not args.write:
        print("\nPreview only. No files were changed.")
        print("Run again with --write to create the file.\n")
        print(mdx)
        return

    # mkdir(parents=True) creates content/blog/ if it does not exist yet.
    # exist_ok=True means it is fine if the folder already exists.
    BLOG_DIR.mkdir(parents=True, exist_ok=True)

    if target_path.exists():
        print("\nStopped safely: that file already exists.")
        print("Choose a different title or edit the existing file manually.")
        return

    target_path.write_text(mdx, encoding="utf-8")

    print("\nCreated draft:")
    print(target_path)
    print("\nNext frontend step:")
    print("Later, Next.js can scan content/blog/ and render these MDX files as pages.")


# This means: only run main() when this file is executed directly.
# If another Python file imports this script later, main() will not auto-run.
if __name__ == "__main__":
    main()
