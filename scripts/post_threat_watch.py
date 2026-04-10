#!/usr/bin/env python3
"""
ThreatWatch Pipeline Script
Receives generated threat intel content and:
1. Posts embed to Discord webhook
2. Injects new blog post card into blog.html
3. Commits and pushes to GitHub (triggers Cloudflare deploy)

Usage:
  python post_threat_watch.py --title "Title" --excerpt "Short excerpt" --body "Full body text" --source-url "https://..." --tags "tag1,tag2"
"""

import argparse
import json
import requests
import subprocess
import re
from datetime import datetime
from pathlib import Path

WEBHOOK_URL = "https://discord.com/api/webhooks/1492269233378431230/IsL_tpchWdbYDoCoNCZIhJVkrcSU8zUzvlfYAAulxvyl_X8QtU6s6gfisbNArLxwv0BV"
BLOG_HTML = Path(__file__).parent.parent / "blog.html"
REPO_ROOT = Path(__file__).parent.parent

def post_to_discord(title, excerpt, source_url, tags, date_str):
    tag_str = " ".join(f"`{t}`" for t in tags)
    payload = {
        "username": "ThreatWatch",
        "embeds": [{
            "title": title,
            "description": excerpt,
            "url": source_url,
            "color": 0x00e5c0,
            "fields": [
                {"name": "Tags", "value": tag_str, "inline": True},
                {"name": "Date", "value": date_str, "inline": True}
            ],
            "footer": {
                "text": "packetpursuit.net/blog | recon | exploit && defend | repeat >> theGrind.log"
            }
        }]
    }
    resp = requests.post(WEBHOOK_URL, json=payload)
    if resp.status_code == 204:
        print(f"Discord: posted successfully")
    else:
        print(f"Discord: error {resp.status_code} - {resp.text}")

def inject_blog_post(title, excerpt, body, tags, date_str):
    html = BLOG_HTML.read_text(encoding="utf-8")
    tag_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
    body_escaped = body.replace('"', '&quot;').replace("'", "&#39;")

    new_card = f"""
                <div class="post-card threat-watch-auto">
                    <div class="post-meta">{date_str}</div>
                    <h3 class="post-title">{title}</h3>
                    <div class="post-tags">{tag_html}</div>
                    <p class="post-excerpt">{excerpt}</p>
                    <div class="post-body" style="display:none;">{body}</div>
                    <a href="#" class="read-more" onclick="togglePost(this); return false;">read more &rarr;</a>
                </div>"""

    # Inject after the threat-watch-posts opening comment marker
    marker = "<!-- THREAT-WATCH-POSTS-START -->"
    if marker in html:
        html = html.replace(marker, marker + new_card)
    else:
        print("WARNING: marker not found in blog.html — post not injected")
        return False

    BLOG_HTML.write_text(html, encoding="utf-8")
    print(f"Blog: post injected into blog.html")
    return True

def git_push(title):
    try:
        subprocess.run(["git", "add", "blog.html"], cwd=REPO_ROOT, check=True)
        subprocess.run(["git", "commit", "-m", f"feat(threatwatch): {title[:60]}"], cwd=REPO_ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_ROOT, check=True)
        print("Git: pushed successfully — Cloudflare will deploy in ~60s")
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--excerpt", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--source-url", default="https://packetpursuit.net/blog")
    parser.add_argument("--tags", default="Threat Intel,Cybersecurity")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",")]
    date_str = datetime.now().strftime("%B %d, %Y")

    post_to_discord(args.title, args.excerpt, args.source_url, tags, date_str)
    injected = inject_blog_post(args.title, args.excerpt, args.body, tags, date_str)
    if injected:
        git_push(args.title)

if __name__ == "__main__":
    main()
