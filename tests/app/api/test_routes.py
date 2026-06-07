# Tests for the explorer API routes.
import unittest
import urllib.parse
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fractal_mcp.app.api.routes import clear_render_cache, router
from fractal_mcp.app.main import value_error_handler
from fractal_mcp.renderer import IMAGES_DIR, parse_complex

# Testing Constants (formerly from renderer.py)
RESOLUTION = 1600
MAX_ITERATIONS = 200
DEFAULT_COLORMAP = "Turbo"
DEFAULT_JULIA_C = -0.7 + 0.27j
X_MIN = -2.0
X_MAX = 1.0
Y_MIN = -1.5
Y_MAX = 1.5


@patch.object(Path, "write_bytes")
@patch("fractal_mcp.app.api.routes.render_fractal")
class TestExplorerAPI(unittest.TestCase):
    client: TestClient

    def setUp(self) -> None:
        app = FastAPI()
        app.include_router(router)
        clear_render_cache()

        app.add_exception_handler(ValueError, value_error_handler)
        self.client = TestClient(app)

    def _get_default_params(self, **kwargs: Any) -> str:
        defaults = {
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": DEFAULT_COLORMAP,
            "reverse_colormap": False,
        }
        defaults.update(kwargs)

        return urllib.parse.urlencode(defaults)

    def test_router_render_cases(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        test_cases: list[dict[str, Any]] = [
            {"fractal_type": "mandelbrot", "expected": b"render_data"},
            {"fractal_type": "julia", "c": "-0.7+0.27j", "expected": b"julia_data"},
            {"fractal_type": "exponential", "c": "1+0j", "expected": b"expo_data"},
            {"fractal_type": "sine", "c": "1+0j", "expected": b"sine_data"},
            {"fractal_type": "cosine", "c": "1+0j", "expected": b"cosine_data"},
            {"fractal_type": "newton", "power": 3.0, "expected": b"newton_data"},
        ]
        for case in test_cases:
            with self.subTest(fractal_type=case["fractal_type"]):
                mock_render.reset_mock()
                mock_render.return_value = case["expected"]

                kwargs = {k: v for k, v in case.items() if k != "expected"}
                params = self._get_default_params(**kwargs)
                response = self.client.get(f"/render?{params}")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, case["expected"])
                self.assertIn("X-Suggested-Filename", response.headers)
                self.assertTrue(response.headers["X-Suggested-Filename"].endswith(".jpg"))
                mock_render.assert_called_once()

    def test_router_save_success_cases(self, mock_render: MagicMock, mock_write: MagicMock) -> None:
        mock_render.return_value = b"save_data"
        test_cases: list[dict[str, Any]] = [
            {"fractal_type": "mandelbrot", "filename": "m_save", "expected_file": "m_save.jpg"},
            {"fractal_type": "julia", "c": "-0.7 + 0.27j", "filename": "j_save", "expected_file": "j_save.jpg"},
            {"fractal_type": "exponential", "c": "1+0j", "filename": "e_save", "expected_file": "e_save.jpg"},
            {"fractal_type": "sine", "c": "1+0j", "filename": "s_save", "expected_file": "s_save.jpg"},
            {"fractal_type": "cosine", "c": "1+0j", "filename": "c_save", "expected_file": "c_save.jpg"},
            {"fractal_type": "newton", "power": 3.0, "filename": "n_save", "expected_file": "n_save.jpg"},
        ]
        for case in test_cases:
            with self.subTest(case=case):
                mock_render.reset_mock()
                mock_write.reset_mock()

                payload = {
                    "x_min": X_MIN,
                    "x_max": X_MAX,
                    "y_min": Y_MIN,
                    "y_max": Y_MAX,
                    "max_iterations": 200,
                    "resolution": 1600,
                    "colormap": "Turbo",
                    "reverse_colormap": False,
                    **{k: v for k, v in case.items() if k != "expected_file"},
                }
                response = self.client.post("/save", json=payload)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["filename"], case["expected_file"])
                mock_write.assert_called_once_with(b"save_data")
                mock_render.assert_called_once()

    def test_router_save_path_traversal_sanitization(self, mock_render: MagicMock, mock_write: MagicMock) -> None:
        mock_render.return_value = b"save_data"
        payload = {
            "fractal_type": "mandelbrot",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": "Turbo",
            "reverse_colormap": False,
            "filename": "../../../traversal_test.jpg",
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "traversal_test.jpg")
        mock_write.assert_called_once_with(b"save_data")
        mock_render.assert_called_once()

    def test_router_save_invalid_cases(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        test_cases: list[dict[str, Any]] = [
            # Missing filename
            {
                "fractal_type": "mandelbrot",
                "x_min": X_MIN,
                "x_max": X_MAX,
                "y_min": Y_MIN,
                "y_max": Y_MAX,
                "max_iterations": 200,
                "resolution": 1600,
                "colormap": "Turbo",
                "reverse_colormap": False,
            },
            # Invalid complex number string
            {"fractal_type": "julia", "c": "not-a-number", "resolution": 123, "filename": "test"},
            # Missing julia c
            {
                "fractal_type": "julia",
                "filename": "missing_c",
                "x_min": X_MIN,
                "x_max": X_MAX,
                "y_min": Y_MIN,
                "y_max": Y_MAX,
                "max_iterations": 200,
                "resolution": 1600,
                "colormap": "Turbo",
                "reverse_colormap": False,
            },
            # Explicit None julia c
            {
                "fractal_type": "julia",
                "c": None,
                "filename": "none_c",
                "x_min": X_MIN,
                "x_max": X_MAX,
                "y_min": Y_MIN,
                "y_max": Y_MAX,
                "max_iterations": 200,
                "resolution": 1600,
                "colormap": "Turbo",
                "reverse_colormap": False,
            },
            # Invalid coordinates value error
            {
                "fractal_type": "mandelbrot",
                "filename": "invalid_coords",
                "x_min": 1.0,
                "x_max": -1.0,
                "y_min": Y_MIN,
                "y_max": Y_MAX,
                "max_iterations": 200,
                "resolution": 1600,
                "colormap": "Turbo",
                "reverse_colormap": False,
            },
        ]
        for case in test_cases:
            with self.subTest(case=case):
                response = self.client.post("/save", json=case)
                self.assertEqual(response.status_code, 422)

    def test_router_suggest_filename_cases(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        test_cases: list[dict[str, Any]] = [
            {
                "params": {"fractal_type": "julia", "c": "-0.123+0.745j", "reverse_colormap": False},
                "not_in": "reversed",
                "ends_with": "turbo.jpg",
            },
            {
                "params": {"fractal_type": "julia", "c": "-0.7+0.27j"},
                "in": "julia_c-0.700_0.270",
            },
            {
                "params": {"fractal_type": "newton", "power": 3.5},
                "in": "newton_p3.5",
            },
        ]
        for case in test_cases:
            with self.subTest(params=case["params"]):
                params = self._get_default_params(**case["params"])
                response = self.client.get(f"/suggest-filename?{params}")
                self.assertEqual(response.status_code, 200)
                filename = response.json()["filename"]
                if "not_in" in case:
                    self.assertNotIn(case["not_in"], filename)
                if "ends_with" in case:
                    self.assertTrue(filename.endswith(case["ends_with"]))
                if "in" in case:
                    self.assertIn(case["in"], filename)

    def test_render_cache_hit(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"cached_data"
        params = self._get_default_params(fractal_type="mandelbrot", resolution=100)
        # First render to populate cache
        self.client.get(f"/render?{params}")
        # Second render with same params should hit cache
        response = self.client.get(f"/render?{params}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"cached_data")
        # Should only be called ONCE
        mock_render.assert_called_once()

    def test_render_unsupported_fractal(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        # Now returns 400 because ValueError is handled
        params = self._get_default_params(fractal_type="invalid")
        response = self.client.get(f"/render?{params}")
        self.assertEqual(response.status_code, 400)

    def test_save_cache_hit(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"cached_data"
        # 1. Render once to populate cache
        params = self._get_default_params(fractal_type="mandelbrot", resolution=100)
        self.client.get(f"/render?{params}")

        # 2. Save with same params should hit cache
        payload = {
            "fractal_type": "mandelbrot",
            "resolution": 100,
            "filename": "cache_hit_save",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "colormap": DEFAULT_COLORMAP,
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "cache_hit_save.jpg")
        self.assertEqual(response.json()["path"], str(IMAGES_DIR / "cache_hit_save.jpg"))
        # Should only be called ONCE (during the initial render)
        mock_render.assert_called_once()

    def test_render_invalid_coords_value_error(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        params = self._get_default_params(fractal_type="mandelbrot", x_min=1.0, x_max=-1.0)
        response = self.client.get(f"/render?{params}")
        # ValueError is caught by the exception handler in main.py, returning 400
        self.assertEqual(response.status_code, 400)
        self.assertIn("x_min must be strictly less than x_max", response.json()["detail"])

    def test_save_invalid_coords_value_error(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        payload = {
            "fractal_type": "mandelbrot",
            "filename": "invalid_coords",
            "x_min": 1.0,
            "x_max": -1.0,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": "Turbo",
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_router_save_path_traversal(self, mock_render: MagicMock, mock_write: MagicMock) -> None:
        """Verify that directory traversal filename sequences are safely sanitized before saving."""
        mock_render.return_value = b"save_data"

        payload = {
            "fractal_type": "mandelbrot",
            "filename": "../../../path_traversal_test.jpg",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 1600,
            "colormap": "Turbo",
            "reverse_colormap": False,
        }

        written_paths = []

        def spy_write_bytes(self_path: Path, data: bytes) -> int:
            written_paths.append(self_path)
            # Call mock_write to preserve the call stats
            mock_write(data)
            return len(data)

        with patch.object(Path, "write_bytes", spy_write_bytes):
            response = self.client.post("/save", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "path_traversal_test.jpg")

        # Verify that write_bytes was called on the correct sanitized Path
        self.assertEqual(len(written_paths), 1)
        self.assertEqual(written_paths[0], IMAGES_DIR / "path_traversal_test.jpg")

    def test_save_invalid_filename(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        for bad_filename in ("", ".", ".."):
            payload = {
                "fractal_type": "mandelbrot",
                "filename": bad_filename,
                "x_min": X_MIN,
                "x_max": X_MAX,
                "y_min": Y_MIN,
                "y_max": Y_MAX,
                "max_iterations": 200,
                "resolution": 1600,
                "colormap": "Turbo",
                "reverse_colormap": False,
            }
            response = self.client.post("/save", json=payload)
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid filename", response.json()["detail"])

    def test_list_colormaps_route(self, *mocks: Any) -> None:
        response = self.client.get("/colormaps")
        self.assertEqual(response.status_code, 200)
        colormaps = response.json()
        self.assertIn("Turbo", colormaps)
        self.assertIn("Viridis", colormaps)

    def test_save_jpeg_extension(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"jpeg_data"
        payload = {
            "fractal_type": "mandelbrot",
            "filename": "test_image.jpeg",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 100,
            "colormap": DEFAULT_COLORMAP,
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["filename"], "test_image.jpeg")

    def test_render_cache_miss_on_different_params(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"some_data"
        params_a = self._get_default_params(fractal_type="mandelbrot", resolution=100)
        params_b = self._get_default_params(fractal_type="mandelbrot", resolution=200)
        self.client.get(f"/render?{params_a}")
        self.client.get(f"/render?{params_b}")
        self.assertEqual(mock_render.call_count, 2)

    def test_save_populates_render_cache(self, mock_render: MagicMock, _mock_write: MagicMock) -> None:
        mock_render.return_value = b"cached_data"
        payload = {
            "fractal_type": "mandelbrot",
            "resolution": 100,
            "filename": "save_populate",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "colormap": DEFAULT_COLORMAP,
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 200)

        params = self._get_default_params(fractal_type="mandelbrot", resolution=100)
        render_response = self.client.get(f"/render?{params}")
        self.assertEqual(render_response.status_code, 200)
        self.assertEqual(render_response.content, b"cached_data")
        mock_render.assert_called_once()

    def test_save_invalid_filename_whitespace_only(self, _mock_render: MagicMock, _mock_write: MagicMock) -> None:
        payload = {
            "fractal_type": "mandelbrot",
            "filename": "   ",
            "x_min": X_MIN,
            "x_max": X_MAX,
            "y_min": Y_MIN,
            "y_max": Y_MAX,
            "max_iterations": 200,
            "resolution": 100,
            "colormap": DEFAULT_COLORMAP,
            "reverse_colormap": False,
        }
        response = self.client.post("/save", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid filename", response.json()["detail"])

    def test_parse_complex_direct(self, *mocks: Any) -> None:
        self.assertEqual(parse_complex(complex(1, 2)), complex(1, 2))
        self.assertEqual(parse_complex("-0.7+0.27j"), complex(-0.7, 0.27))
        self.assertEqual(parse_complex("-0.7+0.27i"), complex(-0.7, 0.27))
        self.assertEqual(parse_complex("-0.7+0.27I"), complex(-0.7, 0.27))
        self.assertEqual(parse_complex("-0.7 + 0.27j"), complex(-0.7, 0.27))
        self.assertEqual(parse_complex("  -0.7   +   0.27j  "), complex(-0.7, 0.27))
        with self.assertRaisesRegex(ValueError, r"complex\(\) arg is a malformed string"):
            parse_complex("invalid")


if __name__ == "__main__":
    unittest.main()
