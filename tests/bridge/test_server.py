import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import base64
from fractal_mcp.bridge.server import mcp
from fractal_mcp.renderer import FractalResult, DEFAULT_COLORMAP

class TestBridgeServer(unittest.IsolatedAsyncioTestCase):
    async def test_generate_mandelbrot_image(self):
        with patch("fractal_mcp.bridge.server.render_fractal") as mock_render:
            mock_render.return_value = FractalResult(
                image_bytes=b"fake_image_data",
                mean_escape=5.0,
                grid_shape=(10, 10)
            )
            
            # Call the tool via FastMCP
            result = await mcp.call_tool("generate_mandelbrot_image", {
                "x_min": -2.0, "x_max": 1.0, "y_min": -1.5, "y_max": 1.5,
                "resolution": 10, "max_iterations": 10
            })
            
            res_dict = result
            if hasattr(result, "content"):
                import json
                res_dict = json.loads(result.content[0].text)

            self.assertEqual(res_dict["colormap"], DEFAULT_COLORMAP)
            self.assertEqual(res_dict["type"], "file")
            
            # Expected: mandelbrot_x-0.5000_y0.0000_turbo.jpg
            expected_filename = f"mandelbrot_x-0.5000_y0.0000_{DEFAULT_COLORMAP.lower()}.jpg"
            self.assertEqual(res_dict["filename"], expected_filename)
            
            # Verify the data was base64 encoded correctly
            decoded_data = base64.b64decode(res_dict["data"])
            self.assertEqual(decoded_data, b"fake_image_data")
            mock_render.assert_called_once()

    async def test_generate_julia_image(self):
        with patch("fractal_mcp.bridge.server.render_fractal") as mock_render:
            mock_render.return_value = FractalResult(
                image_bytes=b"fake_image_data",
                mean_escape=5.0,
                grid_shape=(10, 10)
            )
            
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
            self.assertIn("julia_", res_dict["filename"])
            self.assertEqual(res_dict["shape"], [10, 10])
            mock_render.assert_called_once()

if __name__ == "__main__":
    unittest.main()
