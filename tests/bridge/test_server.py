# Tests for the FastMCP bridge server and tools.
import base64
import unittest
from typing import Any
from unittest.mock import MagicMock, patch

from fractal_mcp.bridge.server import mcp


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

        self.assertEqual(len(result.content), 1)
        content_item = result.content[0]
        self.assertEqual(content_item.type, "image")
        self.assertEqual(content_item.mimeType, "image/jpeg")
        self.assertEqual(base64.b64decode(content_item.data), b"fake_image_data")

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

        self.assertEqual(len(result.content), 1)
        content_item = result.content[0]
        self.assertEqual(content_item.type, "image")
        self.assertEqual(content_item.mimeType, "image/jpeg")
        self.assertEqual(base64.b64decode(content_item.data), b"fake_image_data")

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

        self.assertEqual(len(result.content), 1)
        content_item = result.content[0]
        self.assertEqual(content_item.type, "image")
        self.assertEqual(content_item.mimeType, "image/jpeg")
        self.assertEqual(base64.b64decode(content_item.data), b"fake_image_data")

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

        self.assertEqual(len(result.content), 1)
        content_item = result.content[0]
        self.assertEqual(content_item.type, "image")
        self.assertEqual(content_item.mimeType, "image/jpeg")
        self.assertEqual(base64.b64decode(content_item.data), b"fake_image_data")

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

        self.assertEqual(len(result.content), 1)
        content_item = result.content[0]
        self.assertEqual(content_item.type, "image")
        self.assertEqual(content_item.mimeType, "image/jpeg")
        self.assertEqual(base64.b64decode(content_item.data), b"fake_image_data")

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

        self.assertEqual(len(result.content), 1)
        content_item = result.content[0]
        self.assertEqual(content_item.type, "image")
        self.assertEqual(content_item.mimeType, "image/jpeg")
        self.assertEqual(base64.b64decode(content_item.data), b"fake_image_data")

        mock_render.assert_called_once()
        mock_write.assert_called_once_with(b"fake_image_data")


if __name__ == "__main__":
    unittest.main()
