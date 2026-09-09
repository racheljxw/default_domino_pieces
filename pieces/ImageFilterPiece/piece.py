from domino.base_piece import BasePiece
from .models import InputModel, OutputModel, FilterResult
from PIL import Image
from io import BytesIO
import numpy as np
import base64


filter_masks = {
    'sepia': ((0.393, 0.769, 0.189), (0.349, 0.686, 0.168), (0.272, 0.534, 0.131)),
    'black_and_white': ((0.333, 0.333, 0.333), (0.333, 0.333, 0.333), (0.333, 0.333, 0.333)),
    'brightness': ((1.4, 0, 0), (0, 1.4, 0), (0, 0, 1.4)),
    'darkness': ((0.6, 0, 0), (0, 0.6, 0), (0, 0, 0.6)),
    'contrast': ((1.2, 0.6, 0.6), (0.6, 1.2, 0.6), (0.6, 0.6, 1.2)),
    'red': ((1.6, 0, 0), (0, 1, 0), (0, 0, 1)),
    'green': ((1, 0, 0), (0, 1.6, 0), (0, 0, 1)),
    'blue': ((1, 0, 0), (0, 1, 0), (0, 0, 1.6)),
    'cool': ((0.9, 0, 0), (0, 1.1, 0), (0, 0, 1.3)),
    'warm': ((1.2, 0, 0), (0, 0.9, 0), (0, 0, 0.8)),
}


class ImageFilterPiece(BasePiece):

    def piece_function(self, input_data: InputModel):

        all_filters = list()
        if input_data.sepia:
            all_filters.append('sepia')
        if input_data.black_and_white:
            all_filters.append('black_and_white')
        if input_data.brightness:
            all_filters.append('brightness')
        if input_data.darkness:
            all_filters.append('darkness')
        if input_data.contrast:
            all_filters.append('contrast')
        if input_data.red:
            all_filters.append('red')
        if input_data.green:
            all_filters.append('green')
        if input_data.blue:
            all_filters.append('blue')
        if input_data.cool:
            all_filters.append('cool')
        if input_data.warm:
            all_filters.append('warm')

        self.logger.info(f"Applying filters: {', '.join(all_filters) if all_filters else '(none)'}")

        results = []
        for entry in input_data.results:
            # Gate on upstream status: only try to filter images the fetch Piece got successfully.
            if entry.status != "success" or not entry.base64_content:
                results.append(FilterResult(
                    url=entry.url,
                    status="failed",
                    error=entry.error or "No image content from upstream.",
                ))
                continue

            try:
                filtered_image = self._filter_image(entry.base64_content, all_filters)
                results.append(FilterResult(
                    url=entry.url,
                    status="success",
                    filtered_image=filtered_image,
                ))
            except Exception as e:
                self.logger.info(f"Filtering failed for {entry.url}: {e}")
                results.append(FilterResult(
                    url=entry.url,
                    status="failed",
                    error=str(e),
                ))

        n_failed = sum(1 for r in results if r.status == "failed")
        self.logger.info(f"Filtered {len(results)} image(s): {len(results) - n_failed} succeeded, {n_failed} failed.")

        # Preview the first successfully filtered image in the Domino GUI.
        first_success = next((r for r in results if r.status == "success"), None)
        if first_success is not None:
            self.logger.info(f"Previewing filtered image for {first_success.url}")
            self.display_result = {
                "file_type": "png",
                "base64_content": first_success.filtered_image,
            }

        return OutputModel(results=results)

    def _filter_image(self, base64_content: str, filter_names: list) -> str:
        # Decode the base64 string into a PIL image
        try:
            decoded_data = base64.b64decode(base64_content)
            image = Image.open(BytesIO(decoded_data))
            image.verify()
            image = Image.open(BytesIO(decoded_data))
        except Exception:
            raise ValueError("Input content is not a valid base64 encoded image.")

        # Convert Image to NumPy array
        np_image = np.array(image, dtype=float)

        # Apply filters
        for filter_name in filter_names:
            np_mask = np.array(filter_masks[filter_name], dtype=float)
            for y in range(np_image.shape[0]):
                for x in range(np_image.shape[1]):
                    rgb = np_image[y, x, :3]
                    new_rgb = np.dot(np_mask, rgb)
                    np_image[y, x, :3] = new_rgb
            # Clip values to be in valid range
            np_image = np.clip(np_image, 0, 255)

        # Convert back to uint8 and PIL image
        np_image = np_image.astype(np.uint8)
        modified_image = Image.fromarray(np_image)

        # Encode as base64 PNG string
        buffered = BytesIO()
        modified_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
