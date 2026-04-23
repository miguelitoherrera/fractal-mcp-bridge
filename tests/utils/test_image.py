import numpy as np
from PIL import Image
import io
from utils.image import grid_to_image_bytes

def test_grid_to_image_bytes_jpeg():
    # Create a dummy 10x10 grid with values representing iterations
    # 0 = inside, other values = escaped
    grid = np.zeros((10, 10), dtype=float)
    grid[0:5, 0:5] = 50.0 # Some escapes
    grid[5:10, 5:10] = 100.0 # Later escapes
    
    max_iter = 100
    
    # Test generating JPEG
    jpeg_bytes = grid_to_image_bytes(
        grid, max_iter, fmt="jpeg", quality=80, colormap="Inferno", reverse=False
    )
    
    assert isinstance(jpeg_bytes, bytes)
    
    # Try reading the bytes back as an image
    img = Image.open(io.BytesIO(jpeg_bytes))
    assert img.format == "JPEG"
    assert img.size == (10, 10)
    assert img.mode == "RGB"

def test_grid_to_image_bytes_png():
    grid = np.ones((5, 5), dtype=float) * 20
    grid[2, 2] = 0.0 # One inside point
    
    png_bytes = grid_to_image_bytes(
        grid, max_iterations=20, fmt="png", quality=100, colormap="Viridis", reverse=True
    )
    
    assert isinstance(png_bytes, bytes)
    
    img = Image.open(io.BytesIO(png_bytes))
    assert img.format == "PNG"
    assert img.size == (5, 5)

def test_grid_to_image_bytes_colormap():
    # Make sure different colormaps produce different bytes
    grid = np.linspace(1, 10, 100).reshape((10, 10))
    
    bytes_inferno = grid_to_image_bytes(grid, 10, "png", 90, colormap="Inferno")
    bytes_viridis = grid_to_image_bytes(grid, 10, "png", 90, colormap="Viridis")
    bytes_reversed = grid_to_image_bytes(grid, 10, "png", 90, colormap="Inferno", reverse=True)
    
    assert bytes_inferno != bytes_viridis
    assert bytes_inferno != bytes_reversed
