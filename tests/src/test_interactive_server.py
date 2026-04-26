from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.interactive_server import app

client = TestClient(app)

@patch("src.interactive_server.mandelbrot_set")
@patch("src.interactive_server.grid_to_image_bytes")
def test_render_mandelbrot(mock_grid_to_image, mock_mandelbrot):
    # Mocking the grid to be a simple 2D list and image bytes
    mock_mandelbrot.return_value = [[0, 0], [0, 0]]
    mock_grid_to_image.return_value = b"fake_image_data"

    response = client.get("/render?fractal_type=mandelbrot&resolution=10&max_iterations=50")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content == b"fake_image_data"

    mock_mandelbrot.assert_called_once_with(-2.0, 1.0, -1.5, 1.5, 10, 10, 50)
    mock_grid_to_image.assert_called_once_with(
        [[0, 0], [0, 0]], 50, fmt="jpeg", quality=95, colormap="Inferno", reverse=False
    )

@patch("src.interactive_server.julia_set")
@patch("src.interactive_server.grid_to_image_bytes")
def test_render_julia(mock_grid_to_image, mock_julia):
    mock_julia.return_value = [[0, 0], [0, 0]]
    mock_grid_to_image.return_value = b"fake_image_data"

    response = client.get("/render?fractal_type=julia&c_real=-0.4&c_imag=0.6&resolution=10&max_iterations=50")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content == b"fake_image_data"

    mock_julia.assert_called_once_with(-2.0, 1.0, -1.5, 1.5, complex(-0.4, 0.6), 10, 10, 50)
    mock_grid_to_image.assert_called_once_with(
        [[0, 0], [0, 0]], 50, fmt="jpeg", quality=95, colormap="Inferno", reverse=False
    )

def test_render_invalid_type():
    response = client.get("/render?fractal_type=invalid_type")
    # FastAPI returns 422 Unprocessable Entity when query param validation fails
    assert response.status_code == 422

def test_read_index():
    # Use a real file check or mock appropriately.
    # Since we use FileResponse, we can mock the underlying starlette behavior or just ensure the file exists.
    # For 100% coverage of the 'index' function, we just need to call it.
    with patch("src.interactive_server.FileResponse") as mock_fr:
        mock_fr.return_value = MagicMock()
        response = client.get("/")
        assert response.status_code == 200
        mock_fr.assert_called_once_with("static/index.html")

@patch("src.interactive_server.mandelbrot_set")
@patch("src.interactive_server.grid_to_image_bytes")
@patch.object(Path, "write_bytes")
def test_save_mandelbrot(mock_write_bytes, mock_grid_to_image, mock_mandelbrot):
    mock_mandelbrot.return_value = [[0, 0], [0, 0]]
    mock_grid_to_image.return_value = b"fake_image_data"

    payload = {
        "fractal_type": "mandelbrot",
        "x_min": -2.0, "x_max": 1.0, "y_min": -1.5, "y_max": 1.5,
        "max_iterations": 50, "resolution": 10,
        "colormap": "Inferno", "reverse_colormap": False,
        "c_real": 0.0, "c_imag": 0.0,
        "filename": "test_mandelbrot.jpg"
    }

    response = client.post("/save", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_write_bytes.assert_called_once_with(b"fake_image_data")

@patch("src.interactive_server.julia_set")
@patch("src.interactive_server.grid_to_image_bytes")
@patch.object(Path, "write_bytes")
def test_save_julia(mock_write_bytes, mock_grid_to_image, mock_julia):
    mock_julia.return_value = [[0, 0], [0, 0]]
    mock_grid_to_image.return_value = b"fake_image_data"

    payload = {
        "fractal_type": "julia",
        "x_min": -2.0, "x_max": 2.0, "y_min": -2.0, "y_max": 2.0,
        "max_iterations": 50, "resolution": 10,
        "colormap": "Inferno", "reverse_colormap": False,
        "c_real": -0.4, "c_imag": 0.6,
        "filename": "test_julia"
    }

    response = client.post("/save", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["filename"] == "test_julia.jpg"
    mock_write_bytes.assert_called_once_with(b"fake_image_data")
