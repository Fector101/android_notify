import "../assets/css/referencepage.css";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router";
import { Iversion } from "../assets/js/mytypes";
import { isLegacyVersion } from "../assets/js/helper";
import { InlineCode } from "../ui/CodeBlock/CodeBlock";

/* -------------------------------- */
/* 🔥 IMPORT ALL VERSION DATA HERE  */
/* -------------------------------- */

import { reference_page as v158 } from "./versions-data/1.58";
import { reference_page as v159 } from "./versions-data/1.59";
import { reference_page as v160 } from "./versions-data/1.60";

const VERSION_MAP = {
  "1.58": v158,
  "1.59": v159,
  "1.60": v160,
};

/* -------------------------------- */

type arg = { name: string; desc: string };

type object_list = {
  id: string;
  signature: string;
  description: string;
  args?: arg[];
};

export type NotificationMethods = Record<
  string,
  {
    signature?: string;
    description?: string;
    args?: arg[];
  }
>;

interface IReferencePage {
  NOTIFICATION_METHODS: NotificationMethods;
  HANDLER_METHODS: object_list[];
  STYLE_ATTRIBUTES?: object_list[];
}

/* -------------------------------- */
/* VERSION ORDER                    */
/* -------------------------------- */

const VERSION_ORDER: Iversion[] = ["1.58", "1.59", "1.60"];

/* -------------------------------- */
/* MERGE HELPERS                    */
/* -------------------------------- */

// remove duplicates by arg name
const dedupeArgs = (arr: arg[] = []) => {
  const map = new Map<string, arg>();
  arr.forEach((a) => map.set(a.name, a));
  return Array.from(map.values());
};

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

    result[key] = {
      signature: next.signature ?? prev.signature,
      description: next.description ?? prev.description,
      args: dedupeArgs([...(prev.args || []), ...(next.args || [])]),
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

/* -------------------------------- */

const MethodCard = ({ method }: { method: any }) => (
  <div className="bg-gray-50 p-4 rounded-lg shadow-sm transition">
    <p className="ref-code">{method.signature}</p>
    <p className="paragraph mb-2 text-gray-700">{method.description}</p>

    {method.args?.length > 0 && (
      <dl className="pl-4 space-y-1">
        {method.args.map(({ name, desc }: any) => (
          <div key={name}>
            <dt>{name}</dt>
            <dd>{desc}</dd>
          </div>
        ))}
      </dl>
    )}
  </div>
);

/* -------------------------------- */

export default function ReferencePage({ version }: { version: Iversion }) {
  const [data, setData] = useState<IReferencePage>();
  const [NOTIFICATION_METHODS, setNOTIFICATION_METHODS] =
    useState<NotificationMethods>();

  useEffect(() => {
    const index = VERSION_ORDER.indexOf(version);
    if (index === -1) return;

    let mergedMethods: NotificationMethods = {};
    let mergedHandlers: object_list[] = [];
    let mergedStyles: object_list[] = [];
    let latest: IReferencePage | undefined;

    for (let i = 0; i <= index; i++) {
      const ref = VERSION_MAP[VERSION_ORDER[i]];

      mergedMethods = mergeMethods(mergedMethods, ref.NOTIFICATION_METHODS);
      mergedHandlers = mergeArrayById(
        mergedHandlers,
        ref.HANDLER_METHODS || []
      );
      mergedStyles = mergeArrayById(
        mergedStyles,
        ref.STYLE_ATTRIBUTES || []
      );

      latest = ref;
    }

    setNOTIFICATION_METHODS(mergedMethods);

    setData({
      ...latest!,
      NOTIFICATION_METHODS: mergedMethods,
      HANDLER_METHODS: mergedHandlers,
      STYLE_ATTRIBUTES: mergedStyles,
    });
  }, [version]);

  return (
    <div className="page main-page reference-page">
      <h2>Reference</h2>
      <hr />

      {/* Notification Methods */}
      <section
        id="notification-class"
        className="space-y-6 page-section"
        tabIndex={0}
      >
        <h2 className="text-xl font-bold">
          Notification Attributes and Methods
        </h2>

        {Object.entries(NOTIFICATION_METHODS || {}).map(([key, m]) => (
          <div
            key={key}
            className="bg-gray-50 p-4 rounded-lg shadow-sm transition"
          >
            <p className="ref-code">{m.signature || key}</p>
            <p className="paragraph mb-2 text-gray-700">{m.description}</p>

            {m.args?.length > 0 && (
              <dl className="pl-4 space-y-1">
                {m.args.map(({ name, desc }) => (
                  <div key={name}>
                    <dt>{name}</dt>
                    <dd>{desc}</dd>
                  </div>
                ))}
              </dl>
            )}
          </div>
        ))}
      </section>

      {/* Handler Methods */}
      <section
        id="notificationhandler-class"
        className="space-y-6 page-section"
        tabIndex={0}
      >
        <h2 className="text-xl font-bold">NotificationHandler Methods</h2>

        {data?.HANDLER_METHODS?.map((m) => (
          <MethodCard key={m.id} method={m} />
        ))}
      </section>

      {/* Styles */}
      {["1.58", "1.59", "1.60"].includes(version) && (
        <section
          id="notificationstyles-class"
          className="space-y-6 page-section"
          tabIndex={0}
        >
          {isLegacyVersion(version) ? (
            <h2 className="text-xl font-bold">
              NotificationStyles attributes for Safely Adding Styles
            </h2>
          ) : (
            <>
              <h2 className="text-xl font-bold">NotificationStyles</h2>
              <p className="paragraph">
                All NotificationStyles attributes are deprecated in v1.59.3.
              </p>
              <p>
                The new methods are <InlineCode code="setSmallIcon" />,{" "}
                <InlineCode code="setLargeIcon" />,{" "}
                <InlineCode code="setBigPicture" />,{" "}
                <InlineCode code="setBigText" /> and{" "}
                <InlineCode code="updateProgressBar" />.
              </p>
            </>
          )}

          <div className="flex flex-wrap align-items-cen justify-content-cen styles-container">
            {data?.STYLE_ATTRIBUTES?.map((m) => (
              <div
                key={m.id}
                className="bg-gray-50 rounded-lg shadow-sm hover:shadow-md transition"
              >
                <h3 className="style-attr">
                  <code>{m.signature}</code>
                </h3>
                <p className="text-gray-700 new-line-active">
                  {m.description}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Navigation */}
      <span className="flex next-page-btns-box space-between">
        <Link className="next-page-btn" to="/advanced-methods">
          <ChevronLeft />
          <span>
            <p className="next-txt">Previous</p>
            <p className="page-name">Advanced Methods</p>
          </span>
        </Link>

        <Link className="next-page-btn" to="/help">
          <span>
            <p className="next-txt">Next</p>
            <p className="page-name">Help</p>
          </span>
          <ChevronRight />
        </Link>
      </span>
    </div>
  );
}
