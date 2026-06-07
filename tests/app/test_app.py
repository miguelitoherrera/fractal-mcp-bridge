# Automated verification tests for explorer UI assets and DOM elements consistency.
import html.parser
import unittest

from fastapi.testclient import TestClient

from fractal_mcp.app.main import app


class ExplorerHTMLParser(html.parser.HTMLParser):
    """Simple parser to extract elements, IDs, and options from HTML for assertions."""

    def __init__(self) -> None:
        super().__init__()
        self.element_ids: set[str] = set()
        self.element_classes: set[str] = set()
        self.fractal_options: list[str] = []
        self._in_fractal_type_select = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)

        # Record element IDs
        if "id" in attrs_dict:
            val = attrs_dict["id"]
            if val is not None:
                self.element_ids.add(val)

        # Record element classes
        if "class" in attrs_dict:
            val = attrs_dict["class"]
            if val is not None:
                for cls in val.split():
                    self.element_classes.add(cls)

        # Check if entering fractal_type select
        if tag == "select" and attrs_dict.get("id") == "fractal_type":
            self._in_fractal_type_select = True

        # Check if inside fractal_type select and reading option
        if tag == "option" and self._in_fractal_type_select:
            if "value" in attrs_dict:
                val = attrs_dict["value"]
                if val is not None:
                    self.fractal_options.append(val)

    def handle_endtag(self, tag: str) -> None:
        if tag == "select":
            self._in_fractal_type_select = False


class TestExplorerUI(unittest.TestCase):
    client: TestClient

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_explorer_html_content_and_dom_elements(self) -> None:
        """Verify index.html is served successfully and contains all DOM elements expected by script.js."""
        # 1. Fetch index.html
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))

        html_content = response.text
        self.assertTrue(len(html_content) > 0)

        # 2. Parse HTML content
        parser = ExplorerHTMLParser()
        parser.feed(html_content)

        # 3. Assert all required DOM IDs expected by script.js are present
        expected_ids = [
            "fractalImg",
            "loader",
            "c-params",
            "newton-params",
            "saveFilename",
            "saveBtn",
            "saveStatus",
            "fractal_type",
            "colormap",
            "iterations",
            "resolution",
            "reverse_colormap",
            "c_real",
            "c_imag",
            "power",
            "precision-val",
            "precision-warning",
            "resetBtn",
            "zoomFactor",
            "hover-coords",
        ]

        for element_id in expected_ids:
            self.assertIn(
                element_id,
                parser.element_ids,
                f"Required DOM ID '{element_id}' is missing from index.html!",
            )

        # 4. Assert classes referenced by CSS / script selector
        self.assertIn(
            "viewer",
            parser.element_classes,
            "Required CSS class 'viewer' is missing from index.html!",
        )

        # 5. Assert options inside fractal_type select element
        expected_options = ["mandelbrot", "julia", "exponential", "sine", "cosine", "newton"]
        for opt in expected_options:
            self.assertIn(
                opt,
                parser.fractal_options,
                f"Fractal option '{opt}' is missing from the fractal_type dropdown!",
            )

    def test_explorer_javascript_served_correctly(self) -> None:
        """Verify script.js is served successfully and contains essential state management logic."""
        response = self.client.get("/script.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("javascript", response.headers.get("content-type", ""))

        js_content = response.text
        self.assertTrue(len(js_content) > 0)

        # Check for core state management structures
        self.assertIn("state =", js_content)
        self.assertIn("fractal_type:", js_content)
        self.assertIn("syncStateFromUI", js_content)
        self.assertIn("resetView", js_content)
        self.assertIn("updateUI", js_content)

        # Check default window boundaries for all fractal types
        # 1. Mandelbrot
        self.assertIn("state.fractal_type === 'mandelbrot'", js_content)
        self.assertIn("state.x_min = -2.0;", js_content)
        self.assertIn("state.x_max = 1.0;", js_content)
        self.assertIn("state.y_min = -1.5;", js_content)
        self.assertIn("state.y_max = 1.5;", js_content)

        # 2. Newton
        self.assertIn("state.fractal_type === 'newton'", js_content)
        self.assertIn("state.x_min = -2.0;", js_content)
        self.assertIn("state.x_max = 2.0;", js_content)
        self.assertIn("state.y_min = -2.0;", js_content)
        self.assertIn("state.y_max = 2.0;", js_content)

        # 3. Exponential
        self.assertIn("state.fractal_type === 'exponential'", js_content)
        self.assertIn("state.x_min = -20.0;", js_content)
        self.assertIn("state.x_max = 20.0;", js_content)
        self.assertIn("state.y_min = -20.0;", js_content)
        self.assertIn("state.y_max = 20.0;", js_content)

        # 4. Sine & Cosine
        self.assertIn("['sine', 'cosine'].includes(state.fractal_type)", js_content)
        self.assertIn("state.x_min = -10.0;", js_content)
        self.assertIn("state.x_max = 10.0;", js_content)
        self.assertIn("state.y_min = -10.0;", js_content)
        self.assertIn("state.y_max = 10.0;", js_content)

        # 4. Fallback default coordinates (e.g. Julia)
        self.assertIn("state.x_min = -2.0;", js_content)
        self.assertIn("state.x_max = 2.0;", js_content)
        self.assertIn("state.y_min = -2.0;", js_content)
        self.assertIn("state.y_max = 2.0;", js_content)

    def test_explorer_styles_served_correctly(self) -> None:
        """Verify styles.css is served successfully."""
        response = self.client.get("/styles.css")
        self.assertEqual(response.status_code, 200)
        self.assertIn("css", response.headers.get("content-type", ""))
        self.assertTrue(len(response.text) > 0)

    def test_fractal_rendering_endpoints(self) -> None:
        """Verify that every fractal type can be successfully rendered with real calculations."""
        # Define test inputs for all supported fractal types
        test_cases: list[dict[str, str | float]] = [
            {"fractal_type": "mandelbrot"},
            {"fractal_type": "julia", "c": "-0.7+0.27j"},
            {"fractal_type": "exponential", "c": "1+0j"},
            {"fractal_type": "sine", "c": "1+0j"},
            {"fractal_type": "cosine", "c": "1+0j"},
            {"fractal_type": "newton", "power": 3.0},
        ]

        # Use a low resolution and max iterations to keep execution extremely fast
        base_params: dict[str, str | int | float | bool] = {
            "x_min": -2.0,
            "x_max": 2.0,
            "y_min": -2.0,
            "y_max": 2.0,
            "max_iterations": 10,
            "resolution": 100,
            "colormap": "Turbo",
            "reverse_colormap": False,
        }

        for case in test_cases:
            params: dict[str, str | int | float | bool] = {**base_params, **case}
            fractal_type = str(case["fractal_type"])
            with self.subTest(fractal_type=fractal_type):
                response = self.client.get("/render", params=params)
                self.assertEqual(response.status_code, 200)
                self.assertIn("image/jpeg", response.headers.get("content-type", ""))
                self.assertTrue(len(response.content) > 0)


if __name__ == "__main__":
    unittest.main()
