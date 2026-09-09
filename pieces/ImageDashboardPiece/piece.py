from domino.base_piece import BasePiece
from .models import InputModel, OutputModel
from pathlib import Path
from urllib.parse import urlparse
from html import escape


_STYLE = """
  body { font-family: system-ui, -apple-system, sans-serif; margin: 24px; background: #fafafa; color: #222; }
  h1 { font-size: 20px; margin: 0 0 4px; }
  .summary { color: #555; margin-bottom: 20px; font-size: 13px; }
  .grid { display: flex; flex-wrap: wrap; gap: 16px; }
  .card { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 12px; width: 280px; }
  .card img { width: 100%; height: auto; border-radius: 4px; display: block; }
  .card.failed { border-color: #e0b4b4; background: #fff6f6; }
  .meta { margin-top: 8px; font-size: 12px; word-break: break-all; }
  .url { display: block; color: #333; }
  .error { display: block; color: #b00020; margin-top: 4px; }
  .download { display: inline-block; margin-top: 6px; color: #0366d6; text-decoration: none; }
"""


def _download_name(url: str, index: int) -> str:
    stem = Path(urlparse(url).path).stem
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in stem)
    return f"{safe or f'image_{index}'}_filtered.png"


def _render_card(entry, index: int) -> str:
    url_html = escape(entry.url)
    if entry.status == "success" and entry.filtered_image:
        src = f"data:image/png;base64,{entry.filtered_image}"
        return (
            '<div class="card">'
            f'<img src="{src}" alt="{url_html}" />'
            '<div class="meta">'
            f'<span class="url">{url_html}</span>'
            f'<a class="download" href="{src}" download="{_download_name(entry.url, index)}">Download</a>'
            '</div></div>'
        )
    return (
        '<div class="card failed"><div class="meta">'
        f'<span class="url">{url_html}</span>'
        f'<span class="error">{escape(entry.error or "Unknown error")}</span>'
        '</div></div>'
    )


def _page(total: int, succeeded: int, failed: int, cards_html: str) -> str:
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{_STYLE}</style></head><body>"
        "<h1>Image Filter Results</h1>"
        f"<p class='summary'>{total} image(s) &middot; {succeeded} succeeded &middot; {failed} failed</p>"
        f"<div class='grid'>{cards_html}</div>"
        "</body></html>"
    )


class ImageDashboardPiece(BasePiece):

    def piece_function(self, input_data: InputModel):
        entries = input_data.results
        succeeded = sum(1 for e in entries if e.status == "success")
        failed = len(entries) - succeeded

        cards_html = "".join(_render_card(e, i) for i, e in enumerate(entries))
        if not cards_html:
            cards_html = "<p>No results received.</p>"

        html_doc = _page(len(entries), succeeded, failed, cards_html)

        dashboard_path = Path(self.results_path) / "dashboard.html"
        dashboard_path.write_text(html_doc, encoding="utf-8")

        self.logger.info(
            f"Dashboard written for {len(entries)} entry(ies): {succeeded} succeeded, {failed} failed."
        )

        self.display_result = {
            "file_type": "html",
            "file_path": str(dashboard_path),
        }

        return OutputModel(dashboard_file_path=str(dashboard_path))
