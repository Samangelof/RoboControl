WINDOW_ACTIVITY_SCRIPT = """
// Активность окна
let windowActive = true;

window.addEventListener('blur', () => {
    windowActive = false;
    console.log('Window is inactive');
});

window.addEventListener('focus', () => {
    windowActive = true;
    console.log('Window is active');
});

window.isWindowActive = () => windowActive;
"""