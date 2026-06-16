import markdown
import bleach
from urllib.parse import urlparse
import re

MAX_MD_SIZE = 200_000  # V1.3.3 - prevent abuse (ajusta ao teu caso)

ALLOWED_TAGS = [
    "p", "b", "i", "strong", "em",
    "ul", "ol", "li",
    "h1", "h2", "h3",
    "code", "pre",
    "br", "hr",
    "blockquote",
    "a"
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel", "target"],
    "code": [],
    "pre": [],
}

ALLOWED_SCHEMES = {"http", "https"}


def sanitize_href(attrs, new=False):
    href = (attrs.get("href") or "").strip()

    if not href:
        attrs["href"] = "#"
        return attrs

    href = href.lower()

    # remove null bytes / weird encoding tricks
    if "\x00" in href or "%00" in href:
        attrs["href"] = "#"
        return attrs

    parsed = urlparse(href)

    # scheme enforcement
    if parsed.scheme and parsed.scheme not in ALLOWED_SCHEMES:
        attrs["href"] = "#"
        return attrs

    # block dangerous schemes explicitly
    if href.startswith(("javascript:", "data:", "vbscript:", "file:")):
        attrs["href"] = "#"
        return attrs

    attrs["rel"] = "noopener noreferrer"
    attrs["target"] = "_blank"

    return attrs


def render_safe_markdown(md_text: str) -> str:

    # V1.3.3 - hard limit (anti DoS)
    if not md_text:
        return ""

    md_text = md_text.strip()

    if len(md_text) > MAX_MD_SIZE:
        raise ValueError("Markdown too large")

    # markdown -> HTML
    html = markdown.markdown(
        md_text,
        extensions=["fenced_code", "tables"]
    )

    # V1.3.5 - sanitize HTML output
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_SCHEMES,
        strip=True,
        strip_comments=True
    )

    # link hardening
    clean_html = bleach.linkify(
        clean_html,
        callbacks=[sanitize_href],
        skip_tags=["pre", "code"]
    )

    return clean_html