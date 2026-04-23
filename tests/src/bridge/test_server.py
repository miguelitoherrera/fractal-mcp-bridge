import unittest
import base64
from bridge.server import generate_mandelbrot_image, generate_julia_image

class TestServer(unittest.TestCase):
    def test_generate_mandelbrot_image(self):
        # Small resolution for fast testing
        result = generate_mandelbrot_image(
            x_min=-2.0, x_max=1.0, y_min=-1.5, y_max=1.5,
            resolution=100, max_iterations=50
        )
        
        self.assertEqual(result["type"], "file")
        self.assertTrue(result["filename"].startswith("mandelbrot_"))
        self.assertEqual(result["mime_type"], "image/jpeg")
        self.assertTrue(len(result["data"]) > 0)
        # Verify base64 data
        base64.b64decode(result["data"])
        self.assertIn("mean_escape", result)
        self.assertEqual(result["shape"], [100, 100])

    def test_generate_julia_image(self):
        # Small resolution for fast testing
        result = generate_julia_image(
            x_min=-1.5, x_max=1.5, y_min=-1.5, y_max=1.5,
            c_real=-0.7, c_imag=0.27015,
            resolution=100, max_iterations=50
        )
        
        self.assertEqual(result["type"], "file")
        self.assertTrue(result["filename"].startswith("julia_"))
        self.assertEqual(result["mime_type"], "image/jpeg")
        self.assertTrue(len(result["data"]) > 0)
        # Verify base64 data
        base64.b64decode(result["data"])
        self.assertIn("mean_escape", result)
        self.assertEqual(result["shape"], [100, 100])

if __name__ == '__main__':
    unittest.main()
