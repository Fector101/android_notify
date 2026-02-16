import "../assets/css/referencepage.css";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { nanoid } from "nanoid";
import { Link } from "react-router";
import { InlineCode } from "../ui/CodeBlock/CodeBlock";
import { Iversion, NotificationMethods } from "../assets/js/mytypes";
import { isLegacyVersion } from "../assets/js/helper";

import { VERSION_MAP } from "./versions-data/index";
import { ScrollToSection } from "../ui/ScrollAssist";

function MethodCard({method, fallback }: { method: any; fallback?: string }) {
  const class_name = fallback? fallback+" ref-code": "ref-code"
  return (<div className="bg-gray-50 p-4 rounded-lg shadow-sm transition">
    <p className={class_name}>{method.signature || fallback}</p>
    <p className="paragraph mb-2 text-gray-700">{method.description}</p>

    {method.args && method.args.length > 0 && (
      <dl className="pl-4 space-y-1">
        {method.args.map(({ name, desc }: { name: string; desc: string }) => (
          <div key={nanoid()}>
            <dt>{name}</dt>
            <dd>{desc}</dd>
          </div>
        ))}
      </dl>
    )}
  </div>
);
}
export default function ReferencePage({ version }: { version: Iversion }) {
  const data = VERSION_MAP[version];
  const NOTIFICATION_METHODS: NotificationMethods =
    data?.NOTIFICATION_METHODS || {};

  return (
    <div className="page main-page reference-page">
      <ScrollToSection/>
      <h2>Reference</h2>
      <hr />

      {/* Table of Contents */}
      <nav className="border-l-4 border-blue-600 pl-4">
        <h2 className="font-semibold mb-2">Contents</h2>
        <ul className="inner-section-2 space-y-1 text-sm">
          <li>
            <a href="#notification-class" className="text-blue-600 hover:underline">
              Notification Attributes and Methods
            </a>
          </li>
          <li>
            <a
              href="#notificationhandler-class"
              className="text-blue-600 hover:underline"
            >
              NotificationHandler Methods
            </a>
          </li>
          <li>
            <a href="#notificationstyles-class" className="text-blue-600 hover:underline">
              NotificationStyles
            </a>
          </li>
        </ul>
      </nav>

      {/* v1.59 helper note */}
      {version === "1.59" && (
        <section className="side-note">
          <h2>For v1.59</h2>
          <p className="paragraph">
            Methods were introduced to free up <InlineCode code="__init__" /> kwargs
            and replace direct style usage.
          </p>
        </section>
      )}

      {/* Notification Methods */}
      <section
        id="notification-class"
        className="space-y-6 page-section"
        tabIndex={0}
      >
        <h2 className="text-xl font-bold">
          Notification Attributes and Methods
        </h2>

        {Object.entries(NOTIFICATION_METHODS).map(([key, m]) => (
          <MethodCard key={key} method={m} fallback={key}/>
          
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
          <MethodCard key={nanoid()} method={m} />
        ))}
      </section>

      {/* Styles */}
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
              Style attributes were converted into helper methods like{" "}
              <InlineCode code="setSmallIcon" />,{" "}
              <InlineCode code="setLargeIcon" />,{" "}
              <InlineCode code="setBigPicture" />,{" "}
              <InlineCode code="setBigText" />, and{" "}
              <InlineCode code="updateProgressBar" />.
            </p>
          </>
        )}

        <div className="flex flex-wrap align-items-cen justify-content-cen styles-container">
          {data?.STYLE_ATTRIBUTES &&
            Object.entries(data.STYLE_ATTRIBUTES).map(([key, m]) => (
              <div
                key={nanoid()}
                className="bg-gray-50 rounded-lg shadow-sm hover:shadow-md transition"
              >
                <h3 className="style-attr">
                  <code>{m.signature || key}</code>
                </h3>
                <p className="text-gray-700 new-line-active">
                  {m.description}
                </p>
              </div>
            ))}
        </div>
      </section>

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
