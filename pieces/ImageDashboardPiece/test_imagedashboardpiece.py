from domino.testing import piece_dry_run
from domino.testing.utils import skip_envs
from pathlib import Path
from PIL import Image
from io import BytesIO
import base64


# Build a tiny valid PNG in memory so the test needs no bundled asset
_buf = BytesIO()
Image.new("RGB", (4, 4), (120, 180, 90)).save(_buf, format="PNG")
sample_b64 = base64.b64encode(_buf.getvalue()).decode("utf-8")


def _run(results):
    return piece_dry_run(
        piece_name="ImageDashboardPiece",
        input_data=dict(results=results),
    )


def test_dashboard_output_path():
    out = _run([
        {"url": "https://example.com/a.png", "status": "success", "filtered_image": sample_b64, "error": None},
        {"url": "https://example.com/b.png", "status": "failed", "filtered_image": None, "error": "HTTP request error: 404"},
    ])
    assert out["dashboard_file_path"].endswith("dashboard.html")


@skip_envs('github')
def test_dashboard_html_contents():
    out = _run([
        {"url": "https://example.com/a.png", "status": "success", "filtered_image": sample_b64, "error": None},
        {"url": "https://example.com/b.png", "status": "failed", "filtered_image": None, "error": "HTTP request error: 404"},
    ])
    html_text = Path(out["dashboard_file_path"]).read_text(encoding="utf-8")

    # success entry is embedded as an inline image
    assert "data:image/png;base64," in html_text
    assert "https://example.com/a.png" in html_text
    assert 'download="a_filtered.png"' in html_text

    # failed entry shows its error, no image
    assert "HTTP request error: 404" in html_text
    assert "1 succeeded" in html_text
    assert "1 failed" in html_text
