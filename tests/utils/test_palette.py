import numpy as np
from utils.palette import load_bokeh_palette, _hex_to_rgb_array

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
