import { Iversion, NotificationMethods, IReferencePage } from "../../assets/js/mytypes";
import { reference_page as v158 } from "./1.58";
import { reference_page as v159 } from "./1.59";
import { reference_page as v160 } from "./1.60";

/*
|--------------------------------------------------------------------------
| ORDER OF VERSIONS  🔥
|--------------------------------------------------------------------------
| When a new version comes:
| 1. import the file above
| 2. add it to this list
| DONE.
*/
export const VERSION_ORDER: Iversion[] = ["1.58", "1.59", "1.60"];



/* ------------------------------------------------ */
/* MERGE HELPERS */
/* ------------------------------------------------ */

const mergeMethods = (
  base: NotificationMethods = {},
  incoming: NotificationMethods = {}
) => {
  const result: NotificationMethods = { ...base };

  for (const key in incoming) {
    const prev = result[key];
    const next = incoming[key];

    if (!prev) {
      result[key] = next;
      continue;
    }

    // Merge args intelligently: maintain prev args and update/add from next
    let mergedArgs = prev.args || [];
    if (next.args) {
      const argMap = new Map(mergedArgs.map(arg => [arg.name, arg]));
      // Update existing or add new args from next version
      next.args.forEach(arg => {
        argMap.set(arg.name, arg);
      });
      mergedArgs = Array.from(argMap.values());
    }

    result[key] = {
      signature: next.signature ?? prev.signature,
      description: next.description ?? prev.description,
      args: mergedArgs.length > 0 ? mergedArgs : undefined,
    };
  }

  return result;
};

const mergeArrayById = <T extends { id: string }>(
  a: T[] = [],
  b: T[] = []
) => {
  const map = new Map<string, T>();

  a.forEach((i) => map.set(i.id, i));
  b.forEach((i) => map.set(i.id, { ...map.get(i.id), ...i }));

  return Array.from(map.values());
};



/* ------------------------------------------------ */
/* RAW VERSION DATA */
/* ------------------------------------------------ */

const RAW_VERSION_MAP: Record<Iversion, IReferencePage> = {
  "1.58": v158,
  "1.59": v159,
  "1.60": v160,
};



/* ------------------------------------------------ */
/* BUILD FINAL MAP WITH INHERITANCE */
/* ------------------------------------------------ */

export const VERSION_MAP: Record<Iversion, IReferencePage> = {} as any;

for (let i = 0; i < VERSION_ORDER.length; i++) {
  const version = VERSION_ORDER[i];

  let methods: NotificationMethods = {};
  let handlers: any[] = [];
  let styles: any = {};

  for (let j = 0; j <= i; j++) {
    const v = VERSION_ORDER[j];
    const ref = RAW_VERSION_MAP[v];

    methods = mergeMethods(methods, ref.NOTIFICATION_METHODS);
    handlers = mergeArrayById(handlers, ref.HANDLER_METHODS || []);
    styles = { ...styles, ...(ref.STYLE_ATTRIBUTES || {}) };
  }

  VERSION_MAP[version] = {
    NOTIFICATION_METHODS: methods,
    HANDLER_METHODS: handlers,
    STYLE_ATTRIBUTES: styles,
  };
}
