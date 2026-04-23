import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open

from src.interactive_server import app

client = TestClient(app)

@patch("src.interactive_server.mandelbrot_set")
@patch("src.interactive_server.grid_to_image_bytes")
def test_render_mandelbrot(mock_grid_to_image, mock_mandelbrot):
    # Mocking the grid to be a simple 2D list and image bytes
    mock_mandelbrot.return_value = [[0, 0], [0, 0]]
    mock_grid_to_image.return_value = b"fake_image_data"
    
    response = client.get("/render?type=mandelbrot&resolution=10&max_iterations=50")
    
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
    
    response = client.get("/render?type=julia&c_real=-0.4&c_imag=0.6&resolution=10&max_iterations=50")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content == b"fake_image_data"
    
    mock_julia.assert_called_once_with(-2.0, 1.0, -1.5, 1.5, complex(-0.4, 0.6), 10, 10, 50)
    mock_grid_to_image.assert_called_once_with(
        [[0, 0], [0, 0]], 50, fmt="jpeg", quality=95, colormap="Inferno", reverse=False
    )

def test_render_invalid_type():
    response = client.get("/render?type=invalid_type")
    # FastAPI returns 422 Unprocessable Entity when query param validation fails
    assert response.status_code == 422

@patch("builtins.open", new_callable=mock_open, read_data="<html><body>Test</body></html>")
def test_read_index(mock_file):
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "<html><body>Test</body></html>"
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    mock_file.assert_called_once_with("static/index.html", "r")
