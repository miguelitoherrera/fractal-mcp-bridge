// State management
let state = {
    fractal_type: 'mandelbrot',
    x_min: -2.0,
    x_max: 1.0,
    y_min: -1.5,
    y_max: 1.5,
    iterations: 200,
    colormap: 'Turbo',
    reverse_colormap: false,
    c_real: -0.74543,
    c_imag: 0.11301,
    resolution: 1600
};

const fractalImg = document.getElementById('fractalImg');
const loader = document.getElementById('loader');
const coordsDisplay = document.getElementById('coordsDisplay');
const juliaParams = document.getElementById('julia-params');
const saveFilenameInput = document.getElementById('saveFilename');
const saveBtn = document.getElementById('saveBtn');
const saveStatus = document.getElementById('saveStatus');

function suggestFilename() {
    const xRange = state.x_max - state.x_min;
    const yRange = state.y_max - state.y_min;
    const xCenter = state.x_min + xRange / 2;
    const yCenter = state.y_min + yRange / 2;
    // zoom level relative to initial view width of 3.0
    const zoom = (3.0 / xRange).toFixed(1);

    let name = `${state.fractal_type}_x${xCenter.toFixed(4)}_y${yCenter.toFixed(4)}_z${zoom}_${state.colormap.toLowerCase()}`;
    if (state.fractal_type === 'julia') {
        name = `julia_c${state.c_real.toFixed(3)}_${state.c_imag.toFixed(3)}_x${xCenter.toFixed(4)}_y${yCenter.toFixed(4)}_${state.colormap.toLowerCase()}`;
    }
    saveFilenameInput.value = name + ".jpg";
}

function updateStateFromUI() {
    const oldType = state.fractal_type;
    state.fractal_type = document.getElementById('fractal_type').value;
    state.colormap = document.getElementById('colormap').value;
    state.iterations = parseInt(document.getElementById('iterations').value);
    state.resolution = parseInt(document.getElementById('resolution').value);
    state.reverse_colormap = document.getElementById('reverse_colormap').checked;
    state.c_real = parseFloat(document.getElementById('c_real').value);
    state.c_imag = parseFloat(document.getElementById('c_imag').value);

    juliaParams.style.display = state.fractal_type === 'julia' ? 'flex' : 'none';

    // If type changed, reset to type-specific defaults
    if (oldType !== state.fractal_type) {
        resetView();
    }
    suggestFilename();
}

function render() {
    loader.classList.add('active');

    const params = new URLSearchParams({
        fractal_type: state.fractal_type,
        x_min: state.x_min,
        x_max: state.x_max,
        y_min: state.y_min,
        y_max: state.y_max,
        max_iterations: state.iterations,
        colormap: state.colormap,
        reverse_colormap: state.reverse_colormap,
        resolution: state.resolution,
        julia_c: `${state.c_real}${state.c_imag >= 0 ? '+' : ''}${state.c_imag}j`
    });

    const url = `/render?${params.toString()}`;
    console.log("Calling API:", url);
    fractalImg.src = url;

    coordsDisplay.textContent = `X: [${state.x_min.toFixed(6)}, ${state.x_max.toFixed(6)}] Y: [${state.y_min.toFixed(6)}, ${state.y_max.toFixed(6)}]`;
    suggestFilename();
    saveStatus.textContent = "";
}

fractalImg.onload = () => {
    loader.classList.remove('active');
};

fractalImg.onclick = (e) => {
    const rect = fractalImg.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width;
    const py = (e.clientY - rect.top) / rect.height;

    // Map click to complex plane
    const clickX = state.x_min + px * (state.x_max - state.x_min);
    const clickY = state.y_min + py * (state.y_max - state.y_min);

    const zoom = parseFloat(document.getElementById('zoomFactor').value);

    // Calculate new width and height
    const width = (state.x_max - state.x_min) / zoom;
    const height = (state.y_max - state.y_min) / zoom;

    // Set new bounds centered on click
    state.x_min = clickX - width / 2;
    state.x_max = clickX + width / 2;
    state.y_min = clickY - height / 2;
    state.y_max = clickY + height / 2;

    render();
};

function resetView() {
    if (state.fractal_type === 'mandelbrot') {
        state.x_min = -2.0;
        state.x_max = 1.0;
        state.y_min = -1.5;
        state.y_max = 1.5;
    } else {
        state.x_min = -2.0;
        state.x_max = 2.0;
        state.y_min = -2.0;
        state.y_max = 2.0;
    }
    state.iterations = 200;
    state.resolution = 1600;
    document.getElementById('iterations').value = 200;
    document.getElementById('resolution').value = 1600;
    render();
}

saveBtn.onclick = async () => {
    saveStatus.textContent = "Saving to server...";
    saveStatus.style.color = "#3498db";

    const payload = {
        ...state,
        max_iterations: state.iterations,
        julia_c: `${state.c_real}${state.c_imag >= 0 ? '+' : ''}${state.c_imag}j`,
        filename: saveFilenameInput.value
    };

    console.log("Calling API: /save", payload);
    try {
        const response = await fetch('/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
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

document.getElementById('updateBtn').onclick = () => {
    updateStateFromUI();
    render();
};

document.getElementById('resetBtn').onclick = resetView;

document.getElementById('fractal_type').onchange = updateStateFromUI;
document.getElementById('colormap').onchange = () => { updateStateFromUI(); render(); };
document.getElementById('reverse_colormap').onchange = () => { updateStateFromUI(); render(); };

const inputs = ['iterations', 'resolution', 'c_real', 'c_imag'];
inputs.forEach(id => {
    document.getElementById(id).addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            updateStateFromUI();
            render();
        }
    });
});

// Initial render
updateStateFromUI();
render();