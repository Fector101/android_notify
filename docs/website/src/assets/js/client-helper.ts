/**
 * Determines if the current device is a touch device.
 * @returns {boolean}
 */
function isTouchDevice(): boolean {
    return "ontouchstart" in window || navigator.maxTouchPoints > 0;
}

// For Scroll Disabling/Enabling
const __keys: Record<number, number> = { 37: 1, 38: 1, 39: 1, 40: 1 };
function preventDefault(e: Event): void {
    e.preventDefault();
}

function preventDefaultForScrollKeys(e: KeyboardEvent): boolean {
    if (__keys[e.keyCode]) {
        preventDefault(e);
        return false;
    }
    return true;
}

let supportPassive = false;
// Test for passive event listener support
try {
    const options = Object.defineProperty({}, "passive", {
        get: function (this) {
            supportPassive = true;
            return true;
        },
    });

    window.addEventListener(
        "test",
        () => {},
        options as AddEventListenerOptions
    );
    window.removeEventListener("test", () => {}, options);
} catch (e) {
    console.log(e);
    // Browser does not support passive events
}

const wheelOpt: AddEventListenerOptions | boolean = supportPassive
    ? { passive: false }
    : false;
const wheelEvent: string =
    "onwheel" in document.createElement("div") ? "wheel" : "mousewheel";

function disableScroll(): void {
    window.addEventListener("DOMMouseScroll", preventDefault, false); // older
    window.addEventListener(wheelEvent, preventDefault, wheelOpt);
    window.addEventListener("touchmove", preventDefault, wheelOpt); // For mobile
    window.addEventListener("keydown", preventDefaultForScrollKeys, false);
}

async function enableScroll(): Promise<void> {
    window.removeEventListener("DOMMouseScroll", preventDefault, false);
    window.removeEventListener(wheelEvent, preventDefault, wheelOpt);
    window.removeEventListener("touchmove", preventDefault, wheelOpt);
    window.removeEventListener("keydown", preventDefaultForScrollKeys, false);
}

function copyText(text:string) {
    // alert(navigator.clipboard)
    navigator.clipboard.writeText(text)
        .then(() => {
            // console.log('Text copied to clipboard!');
            // alert('Text copied to clipboard!');
        })
        .catch(err => {
            // alert('Failed to copy: err');
            console.error('Failed to copy: ', err);
        });
}

export {
    copyText,
    isTouchDevice,
    disableScroll,
    enableScroll,
};
