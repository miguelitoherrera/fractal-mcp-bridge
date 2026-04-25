// State management
let state = {
    type: 'mandelbrot',
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

function updateStateFromUI() {
    const oldType = state.type;
    state.type = document.getElementById('type').value;
    state.colormap = document.getElementById('colormap').value;
    state.iterations = parseInt(document.getElementById('iterations').value);
    state.resolution = parseInt(document.getElementById('resolution').value);
    state.reverse_colormap = document.getElementById('reverse_colormap').checked;
    state.c_real = parseFloat(document.getElementById('c_real').value);
    state.c_imag = parseFloat(document.getElementById('c_imag').value);
    
    juliaParams.style.display = state.type === 'julia' ? 'flex' : 'none';

    // If type changed, reset to type-specific defaults
    if (oldType !== state.type) {
        resetView();
    }
}

function render() {
    loader.classList.add('active');
    
    const params = new URLSearchParams({
        type: state.type,
        x_min: state.x_min,
        x_max: state.x_max,
        y_min: state.y_min,
        y_max: state.y_max,
        max_iterations: state.iterations,
        colormap: state.colormap,
        reverse_colormap: state.reverse_colormap,
        resolution: state.resolution,
        c_real: state.c_real,
        c_imag: state.c_imag
    });

    const url = `/render?${params.toString()}`;
    fractalImg.src = url;
    
    coordsDisplay.textContent = `X: [${state.x_min.toFixed(6)}, ${state.x_max.toFixed(6)}] Y: [${state.y_min.toFixed(6)}, ${state.y_max.toFixed(6)}]`;
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
    if (state.type === 'mandelbrot') {
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

document.getElementById('updateBtn').onclick = () => {
    updateStateFromUI();
    render();
};

document.getElementById('resetBtn').onclick = resetView;

document.getElementById('type').onchange = updateStateFromUI;
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