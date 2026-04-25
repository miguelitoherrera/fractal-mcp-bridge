import numpy as np
from PIL import Image
import io
from utils.image import grid_to_image_bytes, load_bokeh_palette, _hex_to_rgb_array

def test_grid_to_image_bytes_jpeg():
    # Create a dummy 10x10 grid with values representing iterations
    # 0 = escaped immediately (far exterior), other values represent slower escapes
    # max_iterations represents points that never escaped (core)
    grid = np.zeros((10, 10), dtype=float)
    grid[0:5, 0:5] = 50.0 # Some escapes
    grid[5:10, 5:10] = 100.0 # Never escaped (core)
    
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
    grid = np.ones((5, 5), dtype=float) * 10
    grid[2, 2] = 0.0 # Escaped immediately
    
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

def test_hex_to_rgb_array():
    hex_colors = ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF"]
    expected = np.array([
        [0, 0, 0],
        [255, 255, 255],
        [255, 0, 0],
        [0, 255, 0],
        [0, 0, 255]
    ], dtype=np.uint8)
    
    result = _hex_to_rgb_array(hex_colors)
    np.testing.assert_array_equal(result, expected)

def test_load_bokeh_palette_existing_256():
    # Viridis is natively a 256 color palette
    palette = load_bokeh_palette("Viridis")
    assert palette.shape == (256, 3)
    assert palette.dtype == np.uint8

def test_load_bokeh_palette_missing_fallback():
    # Should fallback to Inferno256
    palette_missing = load_bokeh_palette("NonExistentPalette123")
    palette_inferno = load_bokeh_palette("Inferno")
    
    assert palette_missing.shape == (256, 3)
    np.testing.assert_array_equal(palette_missing, palette_inferno)

def test_load_bokeh_palette_interpolate():
    # Pastel1 only has 9 colors, so it should be interpolated up to 256
    palette = load_bokeh_palette("Pastel1")
    assert palette.shape == (256, 3)
    assert palette.dtype == np.uint8

def test_load_bokeh_palette_case_insensitive():
    # Should work even if we pass lowercase when bokeh uses Capitalized
    palette_lower = load_bokeh_palette("viridis")
    palette_capital = load_bokeh_palette("Viridis")
    
    np.testing.assert_array_equal(palette_lower, palette_capital)