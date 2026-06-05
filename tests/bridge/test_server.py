# Tests for the FastMCP bridge server and tools.
import json
import unittest
from typing import Any
from unittest.mock import MagicMock, patch

from fractal_mcp.bridge.server import mcp
from fractal_mcp.renderer import IMAGES_DIR


@patch("pathlib.Path.write_bytes")
@patch("fractal_mcp.bridge.server.render_fractal")
class TestBridgeServer(unittest.IsolatedAsyncioTestCase):
    async def test_generate_mandelbrot_image(self, mock_render: MagicMock, mock_write: MagicMock) -> None:
        mock_render.return_value = b"fake_image_data"

        # Call the tool via FastMCP
        result: Any = await mcp.call_tool(
            "generate_mandelbrot_image",
            {
                "x_min": -2.0,
                "x_max": 1.0,
                "y_min": -1.5,
                "y_max": 1.5,
                "resolution": 10,
                "max_iterations": 10,
                "colormap": "Turbo",
                "reverse_colormap": False,
            },
        )

        res_dict = result
        if hasattr(result, "content"):
            content_item = result.content[0]
            if hasattr(content_item, "text"):
                res_dict = json.loads(content_item.text)

        self.assertEqual(res_dict["type"], "file")
        self.assertEqual(res_dict["colormap"], "Turbo")

        # Expected: images/mandelbrot_x-0.5000_y0.0000_res10_iter10_turbo.jpg
        expected_filename = "mandelbrot_x-0.5000_y0.0000_res10_iter10_turbo.jpg"
        self.assertEqual(res_dict["path"], str(IMAGES_DIR / expected_filename))

        mock_render.assert_called_once()
        mock_write.assert_called_once_with(b"fake_image_data")

    async def test_generate_julia_image(self, mock_render: MagicMock, mock_write: MagicMock) -> None:
        mock_render.return_value = b"fake_image_data"

        result: Any = await mcp.call_tool(
            "generate_julia_image",
            {
                "x_min": -2.0,
                "x_max": 2.0,
                "y_min": -2.0,
                "y_max": 2.0,
                "c": "0+0j",
                "resolution": 10,
                "max_iterations": 10,
                "colormap": "Turbo",
                "reverse_colormap": False,
            },
        )

        res_dict = result
        if hasattr(result, "content"):
            content_item = result.content[0]
            if hasattr(content_item, "text"):
                res_dict = json.loads(content_item.text)

        self.assertEqual(res_dict["type"], "file")
        self.assertIn("images/julia_", res_dict["path"])

        mock_render.assert_called_once()
        mock_write.assert_called_once_with(b"fake_image_data")

    async def test_generate_exponential_image(self, mock_render: MagicMock, mock_write: MagicMock) -> None:
        mock_render.return_value = b"fake_image_data"

        result: Any = await mcp.call_tool(
            "generate_exponential_image",
            {
                "x_min": -2.0,
                "x_max": 2.0,
                "y_min": -2.0,
                "y_max": 2.0,
                "c": "1+0j",
                "resolution": 10,
                "max_iterations": 10,
                "colormap": "Turbo",
                "reverse_colormap": False,
            },
        )

        res_dict = result
        if hasattr(result, "content"):
            content_item = result.content[0]
            if hasattr(content_item, "text"):
                res_dict = json.loads(content_item.text)

        self.assertEqual(res_dict["type"], "file")
        self.assertIn("images/exponential_", res_dict["path"])

        mock_render.assert_called_once()
        mock_write.assert_called_once_with(b"fake_image_data")

    async def test_generate_sine_image(self, mock_render: MagicMock, mock_write: MagicMock) -> None:
        mock_render.return_value = b"fake_image_data"

        result: Any = await mcp.call_tool(
            "generate_sine_image",
            {
                "x_min": -2.0,
                "x_max": 2.0,
                "y_min": -2.0,
                "y_max": 2.0,
                "c": "1+0j",
                "resolution": 10,
                "max_iterations": 10,
                "colormap": "Turbo",
                "reverse_colormap": False,
            },
        )

        res_dict = result
        if hasattr(result, "content"):
            content_item = result.content[0]
            if hasattr(content_item, "text"):
                res_dict = json.loads(content_item.text)

        self.assertEqual(res_dict["type"], "file")
        self.assertIn("images/sine_", res_dict["path"])

        mock_render.assert_called_once()
        mock_write.assert_called_once_with(b"fake_image_data")

    async def test_generate_cosine_image(self, mock_render: MagicMock, mock_write: MagicMock) -> None:
        mock_render.return_value = b"fake_image_data"

        result: Any = await mcp.call_tool(
            "generate_cosine_image",
            {
                "x_min": -2.0,
                "x_max": 2.0,
                "y_min": -2.0,
                "y_max": 2.0,
                "c": "1+0j",
                "resolution": 10,
                "max_iterations": 10,
                "colormap": "Turbo",
                "reverse_colormap": False,
            },
        )

        res_dict = result
        if hasattr(result, "content"):
            content_item = result.content[0]
            if hasattr(content_item, "text"):
                res_dict = json.loads(content_item.text)

        self.assertEqual(res_dict["type"], "file")
        self.assertIn("images/cosine_", res_dict["path"])

        mock_render.assert_called_once()
        mock_write.assert_called_once_with(b"fake_image_data")

    async def test_generate_newton_image(self, mock_render: MagicMock, mock_write: MagicMock) -> None:
        mock_render.return_value = b"fake_image_data"

        result: Any = await mcp.call_tool(
            "generate_newton_image",
            {
                "x_min": -2.0,
                "x_max": 2.0,
                "y_min": -2.0,
                "y_max": 2.0,
                "power": 3.0,
                "resolution": 10,
                "max_iterations": 10,
                "colormap": "Turbo",
                "reverse_colormap": False,
            },
        )

        res_dict = result
        if hasattr(result, "content"):
            content_item = result.content[0]
            if hasattr(content_item, "text"):
                res_dict = json.loads(content_item.text)

        self.assertEqual(res_dict["type"], "file")
        self.assertIn("images/newton_", res_dict["path"])

        mock_render.assert_called_once()
        mock_write.assert_called_once_with(b"fake_image_data")


if __name__ == "__main__":
    unittest.main()
