// State management
console.log("Script v2 loaded - Auto-render disabled for numeric inputs. Press Enter to render.");
let state = {
    fractal_type: 'mandelbrot',
    x_min: -2.0,
    x_max: 1.0,
    y_min: -1.5,
    y_max: 1.5,
    iterations: 200,
    colormap: 'Turbo',
    reverse_colormap: false,
    c_real: -0.7,
    c_imag: 0.27,
    power: 3.0,
    resolution: 1600
};

const fractalImg = document.getElementById('fractalImg');
const loader = document.getElementById('loader');
const cParams = document.getElementById('c-params');
const newtonParams = document.getElementById('newton-params');
const saveFilenameInput = document.getElementById('saveFilename');
const saveBtn = document.getElementById('saveBtn');
const saveStatus = document.getElementById('saveStatus');

/**
 * Sync the internal 'state' object with values from the UI.
 */
function syncStateFromUI() {
    state.fractal_type = document.getElementById('fractal_type').value;
    state.colormap = document.getElementById('colormap').value;
    state.iterations = parseInt(document.getElementById('iterations').value) || 200;
    state.resolution = parseInt(document.getElementById('resolution').value) || 1600;
    state.reverse_colormap = document.getElementById('reverse_colormap').checked;
    state.c_real = parseFloat(document.getElementById('c_real').value) || 0;
    state.c_imag = parseFloat(document.getElementById('c_imag').value) || 0;
    state.power = parseFloat(document.getElementById('power').value) || 3.0;

    cParams.style.display = (['julia', 'exponential', 'sine', 'cosine'].includes(state.fractal_type)) ? 'flex' : 'none';
    newtonParams.style.display = (state.fractal_type === 'newton') ? 'flex' : 'none';
    
    // Update Precision Indicator
    const xRange = state.x_max - state.x_min;
    const precisionPower = Math.floor(Math.log10(xRange));
    document.getElementById('precision-val').innerHTML = `10<sup>${precisionPower}</sup>`;
    
    // IEEE 754 double precision limit is around 10^-15 to 10^-16
    const warning = document.getElementById('precision-warning');
    if (precisionPower <= -14) {
        warning.style.display = 'inline';
    } else {
        warning.style.display = 'none';
    }

    console.log("UI Synced:", state);
}

/**
 * Fetch a suggested filename from the backend.
 */
async function suggestFilename() {
    const paramsObj = {
        fractal_type: state.fractal_type,
        x_min: state.x_min.toFixed(6),
        x_max: state.x_max.toFixed(6),
        y_min: state.y_min.toFixed(6),
        y_max: state.y_max.toFixed(6),
        colormap: state.colormap,
        reverse_colormap: state.reverse_colormap ? 'true' : 'false'
    };

    if (['julia', 'exponential', 'sine', 'cosine'].includes(state.fractal_type)) {
        paramsObj.c = `${state.c_real}${state.c_imag >= 0 ? '+' : ''}${state.c_imag}j`;
    } else if (state.fractal_type === 'newton') {
        paramsObj.power = state.power;
    }

    const params = new URLSearchParams(paramsObj);
    try {
        const response = await fetch(`/suggest-filename?${params.toString()}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        saveFilenameInput.value = data.filename;
        console.log("Filename suggested by API:", data.filename);
    } catch (err) {
        console.error("Failed to suggest filename:", err);
    }
}

/**
 * Update the image and filename.
 */
async function updateUI(renderImage = true) {
    syncStateFromUI();

    if (renderImage) {
        loader.classList.add('active');
        const paramsObj = {
            fractal_type: state.fractal_type,
            x_min: state.x_min,
            x_max: state.x_max,
            y_min: state.y_min,
            y_max: state.y_max,
            max_iterations: state.iterations,
            colormap: state.colormap,
            reverse_colormap: state.reverse_colormap ? 'true' : 'false',
            resolution: state.resolution,
            _t: Date.now()
        };

        if (['julia', 'exponential', 'sine', 'cosine'].includes(state.fractal_type)) {
            paramsObj.c = `${state.c_real}${state.c_imag >= 0 ? '+' : ''}${state.c_imag}j`;
        } else if (state.fractal_type === 'newton') {
            paramsObj.power = state.power;
        }

        const params = new URLSearchParams(paramsObj);
        const url = `/render?${params.toString()}`;

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            // Extract filename from header (primary sync)
            const suggestedFilename = response.headers.get("X-Suggested-Filename") || response.headers.get("x-suggested-filename");
            if (suggestedFilename) {
                saveFilenameInput.value = suggestedFilename;
                console.log("Filename synced from render header:", suggestedFilename);
            }

            const blob = await response.blob();
            const objectURL = URL.createObjectURL(blob);
            if (fractalImg.src.startsWith('blob:')) {
                URL.revokeObjectURL(fractalImg.src);
            }
            fractalImg.src = objectURL;
        } catch (err) {
            console.error("Render failed:", err);
            loader.classList.remove('active');
            // If render fails, try to at least get a filename suggestion
            await suggestFilename();
        }
    } else {
        await suggestFilename();
    }

    saveStatus.textContent = "";
}

/**
 * Reset the view to defaults based on the current fractal type.
 */
function resetView() {
    if (state.fractal_type === 'mandelbrot') {
        state.x_min = -2.0;
        state.x_max = 1.0;
        state.y_min = -1.5;
        state.y_max = 1.5;
    } else if (state.fractal_type === 'newton') {
        state.x_min = -2.0;
        state.x_max = 2.0;
        state.y_min = -2.0;
        state.y_max = 2.0;
    } else {
        state.x_min = -2.0;
        state.x_max = 2.0;
        state.y_min = -2.0;
        state.y_max = 2.0;
    }

    state.iterations = 200;
    state.resolution = 1600;
    state.reverse_colormap = false;

    document.getElementById('iterations').value = 200;
    document.getElementById('resolution').value = 1600;
    document.getElementById('reverse_colormap').checked = false;

    updateUI(true);
}

// Image load handler
fractalImg.onload = () => {
    loader.classList.remove('active');
};

const hoverCoords = document.getElementById('hover-coords');
const viewer = document.querySelector('.viewer');

viewer.addEventListener('mousemove', (e) => {
    const imgRect = fractalImg.getBoundingClientRect();
    
    if (e.clientX >= imgRect.left && e.clientX <= imgRect.right &&
        e.clientY >= imgRect.top && e.clientY <= imgRect.bottom) {
        
        const px = (e.clientX - imgRect.left) / imgRect.width;
        const py = (e.clientY - imgRect.top) / imgRect.height;

        const xCoord = state.x_min + px * (state.x_max - state.x_min);
        const yCoord = state.y_max - py * (state.y_max - state.y_min);

        hoverCoords.textContent = `${xCoord.toFixed(10)}, ${yCoord.toFixed(10)}`;
        hoverCoords.style.display = 'block';
        
        const viewerRect = viewer.getBoundingClientRect();
        hoverCoords.style.left = `${e.clientX - viewerRect.left}px`;
        hoverCoords.style.top = `${e.clientY - viewerRect.top}px`;
    } else {
        hoverCoords.style.display = 'none';
    }
});

viewer.addEventListener('mouseleave', () => {
    hoverCoords.style.display = 'none';
});

// Zoom on click
fractalImg.onclick = (e) => {
    const rect = fractalImg.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width;
    const py = (e.clientY - rect.top) / rect.height;

    const clickX = state.x_min + px * (state.x_max - state.x_min);
    const clickY = state.y_max - py * (state.y_max - state.y_min);

    const zoom = parseFloat(document.getElementById('zoomFactor').value) || 2;

    const width = (state.x_max - state.x_min) / zoom;
    const height = (state.y_max - state.y_min) / zoom;

    state.x_min = clickX - width / 2;
    state.x_max = clickX + width / 2;
    state.y_min = clickY - height / 2;
    state.y_max = clickY + height / 2;

    updateUI(true);
};

// Save image handler
saveBtn.onclick = async () => {
    saveStatus.textContent = "Saving to server...";
    saveStatus.style.color = "#3498db";

    const payload = {
        ...state,
        max_iterations: state.iterations,
        filename: saveFilenameInput.value
    };

    if (['julia', 'exponential', 'sine', 'cosine'].includes(state.fractal_type)) {
        payload.c = `${state.c_real}${state.c_imag >= 0 ? '+' : ''}${state.c_imag}j`;
    } else if (state.fractal_type === 'newton') {
        payload.power = state.power;
    }

    try {
        const response = await fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (data.status === 'success') {
            saveStatus.textContent = `Successfully saved: ${data.filename}`;
            saveStatus.style.color = "#2ecc71";
        } else {
            saveStatus.textContent = "Error: " + (data.detail || "Failed to save");
            saveStatus.style.color = "#e74c3c";
        }
    } catch (err) {
        saveStatus.textContent = "Network error while saving.";
        saveStatus.style.color = "#e74c3c";
        console.error(err);
    }
};

// Event Listeners
document.getElementById('resetBtn').onclick = resetView;

// Listen for changes on "instant" controls (selects and checkboxes)
['fractal_type', 'colormap', 'reverse_colormap'].forEach(id => {
    const el = document.getElementById(id);
    el.addEventListener('change', () => {
        if (id === 'fractal_type') {
            syncStateFromUI();
            resetView();
        } else {
            updateUI(true);
        }
    });
});

// Keydown listener for numeric inputs (Enter key triggers render)
['iterations', 'resolution', 'c_real', 'c_imag', 'power'].forEach(id => {
    document.getElementById(id).addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            updateUI(true);
        }
    });
});

// Initial load
syncStateFromUI();
updateUI(true);
