import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import base64
from src.bridge.server import mcp

class TestBridgeServer(unittest.IsolatedAsyncioTestCase):
    async def test_generate_mandelbrot_image(self):
        with patch("src.bridge.server.generate_mandelbrot_grid") as mock_grid, \
             patch("src.bridge.server.grid_to_image_bytes") as mock_img:
            
            mock_grid.return_value = np.zeros((10, 10), dtype=np.uint32)
            mock_img.return_value = b"fake_image_data"
            
            # Call the tool via FastMCP
            result = await mcp.call_tool("generate_mandelbrot_image", {
                "x_min": -2.0, "x_max": 1.0, "y_min": -1.5, "y_max": 1.5,
                "resolution": 10, "max_iterations": 10
            })
            
            # result is a ToolResult. content[0] should be TextContent containing our dict (json-encoded)
            # or the dict itself depending on how FastMCP handles local calls.
            # In current FastMCP versions, call_tool returns the object if it's a dict.
            # However, to be safe and robust, let's verify the key properties we expect.
            
            # If FastMCP returns the dict directly in some contexts:
            res_dict = result
            if hasattr(result, "content"):
                # Handle standard MCP ToolResult wrapper
                import json
                res_dict = json.loads(result.content[0].text)

            self.assertEqual(res_dict["colormap"], "Inferno")
            self.assertEqual(res_dict["type"], "file")
            self.assertIn("mandelbrot_", res_dict["filename"])
            
            # Verify the data was base64 encoded correctly
            decoded_data = base64.b64decode(res_dict["data"])
            self.assertEqual(decoded_data, b"fake_image_data")

    async def test_generate_julia_image(self):
        with patch("src.bridge.server.generate_julia_grid") as mock_grid, \
             patch("src.bridge.server.grid_to_image_bytes") as mock_img:
            
            mock_grid.return_value = np.zeros((10, 10), dtype=np.uint32)
            mock_img.return_value = b"fake_image_data"
            
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

if __name__ == "__main__":
    unittest.main()
