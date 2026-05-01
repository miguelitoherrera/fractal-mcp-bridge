from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from pathlib import Path
from src.api.explorer import router, generate_image, FractalParams

# We create a minimal app just to test this specific router in isolation
app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_generate_image_mandelbrot():
    params = FractalParams(
        fractal_type="mandelbrot",
        x_min=-2.0, x_max=1.0, y_min=-1.5, y_max=1.5,
        max_iterations=10, resolution=10,
        colormap="Inferno", reverse_colormap=False,
        c_real=0.0, c_imag=0.0
    )
    with patch("fractal_core.mandelbrot.mandelbrot_set") as mock_mandel, \
         patch("utils.image.grid_to_image_bytes") as mock_img:
        mock_mandel.return_value = []
        mock_img.return_value = b"fake_data"
        
        result = generate_image(params)
        assert result == b"fake_data"
        mock_mandel.assert_called_once()

@patch("fractal_core.mandelbrot.mandelbrot_set")
@patch("utils.image.grid_to_image_bytes")
def test_router_render_mandelbrot(mock_img, mock_mandel):
    mock_mandel.return_value = []
    mock_img.return_value = b"render_data"
    
    response = client.get("/render?fractal_type=mandelbrot")
    assert response.status_code == 200
    assert response.content == b"render_data"

@patch("fractal_core.julia.julia_set")
@patch("utils.image.grid_to_image_bytes")
def test_router_render_julia(mock_img, mock_julia):
    mock_julia.return_value = []
    mock_img.return_value = b"julia_data"
    
    response = client.get("/render?fractal_type=julia")
    assert response.status_code == 200
    assert response.content == b"julia_data"

@patch("fractal_core.mandelbrot.mandelbrot_set")
@patch("utils.image.grid_to_image_bytes")
@patch.object(Path, "write_bytes")
def test_router_save(mock_write, mock_img, mock_mandel):
    mock_mandel.return_value = []
    mock_img.return_value = b"save_data"
    
    payload = {
        "fractal_type": "mandelbrot",
        "x_min": -2.0, "x_max": 1.0, "y_min": -1.5, "y_max": 1.5,
        "max_iterations": 10, "resolution": 10,
        "colormap": "Inferno", "reverse_colormap": False,
        "c_real": 0.0, "c_imag": 0.0,
        "filename": "test.jpg"
    }
    response = client.post("/save", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_write.assert_called_once_with(b"save_data")
