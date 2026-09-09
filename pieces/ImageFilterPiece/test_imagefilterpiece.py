from domino.testing import piece_dry_run
from pathlib import Path
from PIL import Image
from io import BytesIO
import base64


# Open the bundled test image and convert it to a base64 string using Pillow
img_path = str(Path(__file__).parent / "test_image.png")
img = Image.open(img_path)
buffered = BytesIO()
img.save(buffered, format="PNG")
base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")


def test_imagefilterpiece_mixed_upstream_results():
    input_data = dict(
        results=[
            {"url": "https://example.com/a.png", "status": "success", "base64_content": base64_image, "error": None},
            {"url": "https://example.com/b.png", "status": "failed", "base64_content": None, "error": "HTTP request error: 404"},
        ],
        sepia=True,
        blue=True,
    )
    piece_output = piece_dry_run(
        piece_name="ImageFilterPiece",
        input_data=input_data
    )
    results = piece_output['results']
    assert len(results) == 2

    assert results[0]['url'] == "https://example.com/a.png"
    assert results[0]['status'] == "success"
    assert results[0]['filtered_image'] is not None
    assert results[0]['error'] is None

    # Upstream failure is passed through untouched
    assert results[1]['status'] == "failed"
    assert results[1]['filtered_image'] is None
    assert results[1]['error'] == "HTTP request error: 404"


def test_imagefilterpiece_bad_image_isolated():
    input_data = dict(
        results=[
            {"url": "https://example.com/good.png", "status": "success", "base64_content": base64_image, "error": None},
            {"url": "https://example.com/bad.png", "status": "success", "base64_content": "bm90LWFuLWltYWdl", "error": None},
        ],
    )
    piece_output = piece_dry_run(
        piece_name="ImageFilterPiece",
        input_data=input_data
    )
    results = piece_output['results']
    assert len(results) == 2

    # A broken image in one entry does not stop the others
    assert results[0]['status'] == "success"
    assert results[0]['filtered_image'] is not None

    assert results[1]['status'] == "failed"
    assert results[1]['filtered_image'] is None
    assert results[1]['error'] is not None
