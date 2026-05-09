import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from fractal_mcp.bridge.server import mcp
from fractal_mcp.renderer import DEFAULT_COLORMAP

class TestBridgeServer(unittest.IsolatedAsyncioTestCase):
    async def test_generate_mandelbrot_image(self):
        with patch("fractal_mcp.bridge.server.render_fractal") as mock_render, \
             patch("fractal_mcp.bridge.server.Path.write_bytes") as mock_write:
            mock_render.return_value = b"fake_image_data"
            
            # Call the tool via FastMCP
            result = await mcp.call_tool("generate_mandelbrot_image", {
                "x_min": -2.0, "x_max": 1.0, "y_min": -1.5, "y_max": 1.5,
                "resolution": 10, "max_iterations": 10
            })
            
            res_dict = result
            if hasattr(result, "content"):
                import json
                res_dict = json.loads(result.content[0].text)

            self.assertEqual(res_dict["type"], "file")
            self.assertEqual(res_dict["colormap"], DEFAULT_COLORMAP)
            self.assertEqual(res_dict["mime_type"], "image/jpeg")
            
            # Expected: images/mandelbrot_x-0.5000_y0.0000_turbo.jpg
            expected_filename = f"mandelbrot_x-0.5000_y0.0000_{DEFAULT_COLORMAP.lower()}.jpg"
            self.assertEqual(res_dict["path"], f"images/{expected_filename}")
            
            mock_render.assert_called_once()
            mock_write.assert_called_once_with(b"fake_image_data")

    async def test_generate_mandelbrot_image_custom_filename(self):
        with patch("fractal_mcp.bridge.server.render_fractal") as mock_render, \
             patch("fractal_mcp.bridge.server.Path.write_bytes") as mock_write:
            mock_render.return_value = b"fake_image_data"
            
            # Call with a filename that HAS NO extension
            result = await mcp.call_tool("generate_mandelbrot_image", {
                "x_min": -2.0, "x_max": 1.0, "y_min": -1.5, "y_max": 1.5,
                "filename": "my_fractal"
            })
            
            res_dict = result
            if hasattr(result, "content"):
                import json
                res_dict = json.loads(result.content[0].text)

            self.assertEqual(res_dict["path"], "images/my_fractal.jpg")
            mock_write.assert_called_once_with(b"fake_image_data")

    async def test_generate_julia_image(self):
        with patch("fractal_mcp.bridge.server.render_fractal") as mock_render, \
             patch("fractal_mcp.bridge.server.Path.write_bytes") as mock_write:
            mock_render.return_value = b"fake_image_data"
            
            result = await mcp.call_tool("generate_julia_image", {
                "x_min": -2.0, "x_max": 2.0, "y_min": -2.0, "y_max": 2.0,
                "julia_c": "0+0j",
                "resolution": 10, "max_iterations": 10
            })
            
            res_dict = result
            if hasattr(result, "content"):
                import json
                res_dict = json.loads(result.content[0].text)

            self.assertEqual(res_dict["type"], "file")
            self.assertIn("images/julia_", res_dict["path"])
            
            mock_render.assert_called_once()
            mock_write.assert_called_once_with(b"fake_image_data")

    async def test_generate_julia_image_custom_filename(self):
        with patch("fractal_mcp.bridge.server.render_fractal") as mock_render, \
             patch("fractal_mcp.bridge.server.Path.write_bytes") as mock_write:
            mock_render.return_value = b"fake_image_data"
            
            result = await mcp.call_tool("generate_julia_image", {
                "x_min": -2.0, "x_max": 2.0, "y_min": -2.0, "y_max": 2.0,
                "julia_c": "0+0j",
                "filename": "julia_custom"
            })
            
            res_dict = result
            if hasattr(result, "content"):
                import json
                res_dict = json.loads(result.content[0].text)

            self.assertEqual(res_dict["path"], "images/julia_custom.jpg")
            mock_write.assert_called_once_with(b"fake_image_data")


if __name__ == "__main__":
    unittest.main()
