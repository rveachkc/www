#!/usr/bin/env python3
"""One-shot import of a WordPress WXR export into Jekyll _posts/.

Usage:
    python3 -m venv scripts/.venv
    scripts/.venv/bin/pip install markdownify pyyaml
    scripts/.venv/bin/python scripts/wp_import.py ryanveachcom.WordPress.*.xml

Published posts become _posts/YYYY-MM-DD-slug.md. Images referenced by posts
(or used as featured images) are downloaded from the live site into
assets/images/YYYY/MM/ and links are rewritten to point there.
"""

import argparse
import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import yaml
from markdownify import markdownify

NS = {
    "wp": "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
}
SITE = "https://ryanveach.com"
UPLOADS = SITE + "/wp-content/uploads/"
REPO = Path(__file__).resolve().parent.parent
IMAGE_DIR = REPO / "assets" / "images"

BLOCK_RE = re.compile(r"<!-- (/?)wp:([a-z0-9/-]+)(\s+\{.*?\})?\s*(/?)-->", re.S)


# ---------------------------------------------------------------------------
# Gutenberg block parsing
# ---------------------------------------------------------------------------

class Block:
    def __init__(self, name, inner_html="", children=None):
        self.name = name
        self.inner_html = inner_html  # full HTML of the block, comments stripped
        self.children = children or []


def parse_blocks(content):
    """Parse top-level Gutenberg blocks; returns a list of Block (name None = freeform HTML)."""
    blocks, pos = [], 0
    while True:
        m = BLOCK_RE.search(content, pos)
        if not m:
            break
        if content[pos:m.start()].strip():
            blocks.append(Block(None, content[pos:m.start()]))
        closing, name, _, selfclose = m.groups()
        if closing:
            raise ValueError(f"unexpected closing block {name} at {m.start()}")
        if selfclose:
            blocks.append(Block(name))
            pos = m.end()
            continue
        # find the matching close, accounting for nesting of the same name
        depth, scan = 1, m.end()
        while depth:
            n = BLOCK_RE.search(content, scan)
            if not n:
                raise ValueError(f"unclosed block {name}")
            if n.group(2) == name and not n.group(4):
                depth += -1 if n.group(1) else 1
            scan = n.end()
        inner = content[m.end():n.start()]
        blocks.append(Block(name, BLOCK_RE.sub("", inner), parse_blocks(inner)))
        pos = n.end()
    if content[pos:].strip():
        blocks.append(Block(None, content[pos:]))
    return blocks


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------

class Converter:
    def __init__(self, attachments):
        self.attachments = attachments  # set of relative upload paths, e.g. 2020/01/foo.png
        self.images = set()  # relative upload paths to download

    def local_image(self, url):
        """Map a wp-content/uploads URL to a local /assets/images path (full-size original)."""
        url = html.unescape(url)
        if not url.startswith(UPLOADS):
            return url
        rel = url[len(UPLOADS):]
        full = re.sub(r"-\d+x\d+(\.\w+)$", r"\1", rel)
        if full in self.attachments:
            rel = full
        self.images.add(rel)
        return "/assets/images/" + rel

    def figure(self, img_html, caption=None, klass=None):
        src = re.search(r'src="([^"]+)"', img_html).group(1)
        alt = re.search(r'alt="([^"]*)"', img_html)
        alt = html.unescape(alt.group(1)) if alt else ""
        out = [f'<figure{f" class={chr(34)}{klass}{chr(34)}" if klass else ""}>',
               f'  <img src="{self.local_image(src)}" alt="{html.escape(alt)}">']
        if caption:
            out.append(f"  <figcaption>{self.rewrite_links(caption.strip())}</figcaption>")
        out.append("</figure>")
        return "\n".join(out)

    def rewrite_links(self, text):
        text = re.sub(re.escape(UPLOADS) + r'[^"\s)]+', lambda m: self.local_image(m.group(0)), text)
        return re.sub(re.escape(SITE) + r"(/[^\"\s)]*)", r"\1", text)

    def html_to_md(self, fragment):
        fragment = fragment.replace("\\", "\\\\")  # literal backslashes in prose
        md = markdownify(fragment, heading_style="ATX", bullets="-", escape_underscores=False,
                         escape_asterisks=False)
        return self.rewrite_links(md).strip()

    def code(self, pre_html):
        lang = re.search(r'(?:lang="|language-)([\w+-]+)', pre_html)
        body = re.sub(r"</?(pre|code)[^>]*>", "", pre_html)
        body = html.unescape(re.sub(r"<br\s*/?>", "\n", body)).strip("\n")
        fence = f"```{lang.group(1) if lang else ''}\n{body}\n```"
        if "{{" in body or "{%" in body:
            fence = "{% raw %}\n" + fence + "\n{% endraw %}"
        return fence

    def block(self, b, featured=None):
        h = b.inner_html.strip()
        if b.name in ("core/code", "code", "preformatted", "core/preformatted"):
            return self.code(h)
        if b.name == "html":
            return self.rewrite_links(h)
        if b.name == "verse":
            return self.html_to_md(re.sub(r"</?pre[^>]*>", "", h))
        if b.name == "image":
            cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", h, re.S)
            return self.figure(re.search(r"<img[^>]+>", h).group(0), cap and cap.group(1))
        if b.name == "gallery":
            figs = re.findall(r"<li[^>]*>(.*?)</li>", h, re.S)
            out = []
            for f in figs:
                cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", f, re.S)
                out.append(self.figure(re.search(r"<img[^>]+>", f).group(0), cap and cap.group(1)))
            return "\n\n".join(out)
        if b.name == "cover":
            url = re.search(r"background-image:url\(([^)]+)\)", h).group(1)
            if featured and self.local_image(url) == featured:
                return ""  # already shown as the post header
            return self.figure(f'<img src="{url}" alt="">')
        if b.name == "media-text":
            img = re.search(r"<img[^>]+>", h).group(0)
            right = "has-media-on-the-right" in h
            fig = self.figure(img, klass="media-text " + ("align-right" if right else "align-left"))
            # freeform children are the media figure itself, already rendered above
            text = "\n\n".join(filter(None, (self.block(c) for c in b.children if c.name)))
            return fig + "\n\n" + text
        if b.name == "group" or (b.children and b.name not in ("list", "heading", "paragraph")):
            return "\n\n".join(filter(None, (self.block(c, featured) for c in b.children)))
        if b.name == "separator":
            return "---"
        if b.name == "paragraph" and not re.sub(r"<[^>]+>", "", h).strip():
            return ""
        md = self.html_to_md(h)
        if b.name == "paragraph":
            # "2. foo" in a paragraph would become a list that kramdown renumbers from 1
            md = re.sub(r"^(\d+)\. ", r"\1\\. ", md)
        return md

    def convert(self, content, featured=None):
        parts = [self.block(b, featured) for b in parse_blocks(content)]
        return "\n\n".join(p for p in parts if p.strip()) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def text(item, path):
    el = item.find(path, NS)
    return el.text if el is not None and el.text else ""


def postmeta(item, key):
    for pm in item.findall("wp:postmeta", NS):
        if text(pm, "wp:meta_key") == key:
            return text(pm, "wp:meta_value")
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export", help="WordPress WXR export file")
    ap.add_argument("--no-download", action="store_true", help="skip downloading images")
    args = ap.parse_args()

    items = list(ET.parse(args.export).getroot().iter("item"))
    attachments = {}  # post_id -> relative upload path
    for it in items:
        if text(it, "wp:post_type") == "attachment":
            attachments[text(it, "wp:post_id")] = postmeta(it, "_wp_attached_file")
    conv = Converter(set(attachments.values()))

    posts_dir = REPO / "_posts"
    posts_dir.mkdir(exist_ok=True)
    for it in items:
        ptype, status = text(it, "wp:post_type"), text(it, "wp:status")
        if ptype not in ("post", "page"):
            continue
        if ptype != "post" or status != "publish":
            print(f"skipping {ptype} ({status}): {text(it, 'title') or '(untitled)'}", file=sys.stderr)
            continue

        slug = text(it, "wp:post_name")
        local = datetime.strptime(text(it, "wp:post_date"), "%Y-%m-%d %H:%M:%S")
        gmt = datetime.strptime(text(it, "wp:post_date_gmt"), "%Y-%m-%d %H:%M:%S")
        offset = int((local - gmt).total_seconds() // 60)
        tz = f"{'+' if offset >= 0 else '-'}{abs(offset) // 60:02d}{abs(offset) % 60:02d}"

        fm = {
            "title": html.unescape(text(it, "title")),
            "date": f"{local:%Y-%m-%d %H:%M:%S} {tz}",
            "categories": [c.text for c in it.findall("category") if c.get("domain") == "category"],
            "tags": [c.text for c in it.findall("category") if c.get("domain") == "post_tag"],
        }
        excerpt = text(it, "excerpt:encoded").strip()
        if excerpt:
            fm["excerpt"] = html.unescape(excerpt)

        featured = None
        thumb = postmeta(it, "_thumbnail_id")
        if thumb and thumb in attachments:
            featured = conv.local_image(UPLOADS + attachments[thumb])
            fm["header"] = {"overlay_image": featured, "overlay_filter": 0.5, "teaser": featured}

        body = conv.convert(text(it, "content:encoded"), featured)
        out = posts_dir / f"{local:%Y-%m-%d}-{slug}.md"
        out.write_text("---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n\n" + body)
        print(f"wrote {out.relative_to(REPO)}")

    if args.no_download:
        return
    for rel in sorted(conv.images):
        dest = IMAGE_DIR / rel
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading {rel}")
        req = urllib.request.Request(UPLOADS + rel, headers={"User-Agent": "wp_import"})
        with urllib.request.urlopen(req) as resp:
            dest.write_bytes(resp.read())


if __name__ == "__main__":
    main()
