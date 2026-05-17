# Tests for the FastMCP bridge server and tools.
import unittest
from unittest.mock import patch

from fractal_mcp.bridge.server import mcp


@patch("fractal_mcp.bridge.server.Path.write_bytes")
@patch("fractal_mcp.bridge.server.render_fractal")
class TestBridgeServer(unittest.IsolatedAsyncioTestCase):
    async def test_generate_mandelbrot_image(self, mock_render, mock_write):
        mock_render.return_value = b"fake_image_data"

        # Call the tool via FastMCP
        result = await mcp.call_tool(
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
            import json

            res_dict = json.loads(result.content[0].text)

        self.assertEqual(res_dict["type"], "file")
        self.assertEqual(res_dict["colormap"], "Turbo")

        # Expected: images/mandelbrot_x-0.5000_y0.0000_turbo.jpg
        expected_filename = "mandelbrot_x-0.5000_y0.0000_turbo.jpg"
        self.assertEqual(res_dict["path"], f"images/{expected_filename}")

        mock_render.assert_called_once()
        mock_write.assert_called_once_with(b"fake_image_data")

    async def test_generate_julia_image(self, mock_render, mock_write):
        mock_render.return_value = b"fake_image_data"

        result = await mcp.call_tool(
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
            import json

            res_dict = json.loads(result.content[0].text)

        self.assertEqual(res_dict["type"], "file")
        self.assertIn("images/julia_", res_dict["path"])

        mock_render.assert_called_once()
        mock_write.assert_called_once_with(b"fake_image_data")

    async def test_generate_exponential_image(self, mock_render, mock_write):
        mock_render.return_value = b"fake_image_data"

        result = await mcp.call_tool(
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
            import json

            res_dict = json.loads(result.content[0].text)

        self.assertEqual(res_dict["type"], "file")
        self.assertIn("images/exponential_", res_dict["path"])

        mock_render.assert_called_once()
        mock_write.assert_called_once_with(b"fake_image_data")


if __name__ == "__main__":
    unittest.main()
