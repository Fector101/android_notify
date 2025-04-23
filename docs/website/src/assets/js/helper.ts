/**
 *  Changes String first letter to Capital Case
 * @param {string} str
 * @returns {string} string in Title Case
 */
const toTitleCase = (str: string): string =>str.slice(0, 1).toUpperCase() + str.slice(1);

/**
 * Computes list to give string with space at front if str_or_list is not undefined
 * @param {string[] | string | undefined} str_or_list - classes set the parent element class.
 * @returns {string} A String
 */
function returnClass(str_or_list?: string | string[]): string {
    if (!str_or_list) return "";
    if (typeof str_or_list === "string") return " " + str_or_list;
    if (Array.isArray(str_or_list)) return " " + str_or_list.join(" ");
    return "";
}

/**
 * Generates a random integer within a specified range.
 * @param {number} start
 * @param {number} end
 * @returns {number} A random Number from given range.
 */
function randInt(start: number = 0, end: number): number {
    const gen = (): number => Math.trunc(Math.random() * end);
    const int_ = gen();
    if (int_ < start) {
        return randInt(start, end);
    }
    return int_;
}

/**
 * Determines if the current device is a touch device.
 * @returns {boolean}
 */
function isTouchDevice(): boolean {
    return "ontouchstart" in window || navigator.maxTouchPoints > 0;
}

/**
 * Converts seconds to HH:MM:SS format.
 * @param {number | string} secs__
 * @returns {string}
 */
function toHHMMSS(secs__: number | string): string {
    const sec_num = parseInt(secs__.toString(), 10);
    const hrs = Math.floor(sec_num / 3600);
    const mins = Math.floor((sec_num - hrs * 3600) / 60);
    const secs = sec_num - hrs * 3600 - mins * 60;
    const format = (arg: number) => arg.toString().padStart(2, "0");

    return `${format(hrs)}:${format(mins)}:${format(secs)}`;
}

/**
 * Extracts the decimal part of a number.
 * @param {number} decimal_number if input is 5.0 output will be 0
 * @returns {number} if input is 5.12 output will be 0.12
 */
export function parseDecimalSide(decimal_number: number): number {
    const decimalStr = decimal_number.toString();
    if (decimalStr.includes(".")) {
        const [, value] = decimalStr.split(".");
        return Number("0." + value);
    }
    return 0;
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

const formatDate = (dateString: string) => {
    if (dateString === "") return "";
    return new Intl.DateTimeFormat("en-GB", {
        day: "numeric",
        month: "short",
        year: "numeric",
    }).format(new Date(dateString));
};
function range(start: number, end: number) {
    return Array.from({ length: end - start + 1 }, (_, i) => start + i);
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
    returnClass,
    randInt,
    toHHMMSS,
    toTitleCase,
    disableScroll,
    enableScroll,
    formatDate,
    range
};
