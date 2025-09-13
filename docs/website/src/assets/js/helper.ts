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

export {
    returnClass,
    randInt,
    toHHMMSS,
    toTitleCase,
    formatDate,
    range
};
