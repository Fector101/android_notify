import '../assets/css/referencepage.css';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { nanoid } from 'nanoid';
import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { Iversion } from '../assets/js/mytypes';
import { isLegacyVersion } from '../assets/js/helper';

type arg = { name: string; desc: string };

type object_list = {
	id: string;
	signature: string;
	description: string;
	args?: arg[];
};

interface IReferencePage {
	NOTIFICATION_METHODS: NotificationMethods;
	HANDLER_METHODS: object_list[];
	STYLE_ATTRIBUTES?: object_list[];
}

type MethodArg = {
	name: string;
	desc: string;
};

type Method = {
	signature?: string;
	description?: string;
	args?: MethodArg[];
};

export type NotificationMethods = Record<string, Method>;



/* ------------------------------------------------ */
/* VERSION ORDER  (🔥 only thing you update later) */
/* ------------------------------------------------ */

const VERSION_ORDER: Iversion[] = ['1.58', '1.59', '1.60'];



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

		result[key] = {
			signature: next.signature ?? prev.signature,
			description: next.description ?? prev.description,
			args: [...(prev.args || []), ...(next.args || [])],
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
/* COMPONENT */
/* ------------------------------------------------ */




const MethodCard = ({ method, fallback }: { method: any; fallback?: string }) => (
	<div className="bg-gray-50 p-4 rounded-lg shadow-sm transition">
		<p className="ref-code">{method.signature || fallback}</p>
		<p className="paragraph mb-2 text-gray-700">{method.description}</p>

		{method.args && method.args.length > 0 && (
			<dl className="pl-4 space-y-1">
				{method.args.map(({ name, desc }: any) => (
					<div key={nanoid()}>
						<dt>{name}</dt>
						<dd>{desc}</dd>
					</div>
				))}
			</dl>
		)}
	</div>
);

export default function ReferencePage({ version }: { version: Iversion }) {
	const [data, setData] = useState<IReferencePage>();
	const [NOTIFICATION_METHODS, setNOTIFICATION_METHODS] =
		useState<NotificationMethods>();

	async function changeVersionData(version: Iversion) {
		const index = VERSION_ORDER.indexOf(version);
		if (index === -1) return;

		let mergedRef: IReferencePage | undefined;
		let mergedMethods: NotificationMethods = {};
		let mergedHandlers: object_list[] = [];
		let mergedStyles: object_list[] = [];

		for (let i = 0; i <= index; i++) {
			const v = await import(`./versions-data/${VERSION_ORDER[i]}.tsx`);
			const ref = v.reference_page;

			mergedMethods = mergeMethods(mergedMethods, ref.NOTIFICATION_METHODS);
			mergedHandlers = mergeArrayById(
				mergedHandlers,
				ref.HANDLER_METHODS || []
			);
			mergedStyles = mergeArrayById(
				mergedStyles,
				ref.STYLE_ATTRIBUTES || []
			);

			mergedRef = ref;
		}

		setNOTIFICATION_METHODS(mergedMethods);

		setData({
			...mergedRef!,
			NOTIFICATION_METHODS: mergedMethods,
			HANDLER_METHODS: mergedHandlers,
			STYLE_ATTRIBUTES: mergedStyles,
		});
	}

	useEffect(() => {
		changeVersionData(version);
	}, [version]);

	return (
		<div className="page main-page reference-page">
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
						<a href="#notificationhandler-class" className="text-blue-600 hover:underline">
							NotificationHandler Methods
						</a>
					</li>
					<li>
						<a href="#notificationstyles-class" className="text-blue-600 hover:underline">
							NotificationStyles Methods
						</a>
					</li>
				</ul>
			</nav>

			{version === '1.59' && (
				<section className="side-note">
					<h2>For v1.59</h2>
					<p className="paragraph">
						Add methods working to free up __init__ kwargs [parsing out `style`
						attribute]
					</p>
					<div className="paragraph">
						<span className="cod paragraph">setSmallIcon</span> ==
						<span className="code yellow-shade">
							{' '}
							Notification(..., app_icon="...")
						</span>
						<br />
						<br />
						<span>setLargeIcon</span> ==
						<span className="code yellow-shade">
							{' '}
							Notification(..., large_icon_path="...",
							style=NotificationStyles.LARGE_ICON)
						</span>
						<br />
						<br />
						<span>setBigPicture</span> ==
						<span className="code yellow-shade">
							{' '}
							Notification(..., big_picture_path="...",
							style=NotificationStyles.BIG_PICTURE)
						</span>
						<br />
						<br />
						<span>setBigText</span> ==
						<span className="code yellow-shade">
							{' '}
							Notification(..., body="...",
							style=NotificationStyles.BIG_TEXT)
						</span>
					</div>
				</section>
			)}

			{/* Notification Methods */}
			<section id="notification-class" className="space-y-6 page-section" tabIndex={0}>
				<h2 className="text-xl font-bold">
					Notification Attributes and Methods
				</h2>

				{Object.entries(NOTIFICATION_METHODS || {}).map(([key, m]) => (
					<div
						key={nanoid()}
						className="bg-gray-50 p-4 rounded-lg shadow-sm transition"
					>
						<p className={key + ' ref-code'}>{m.signature || key}</p>

						<p className="paragraph mb-2 text-gray-700">{m.description}</p>

						{m.args && (
							<dl className="pl-4 space-y-1">
								{m.args.map(({ name, desc }) => (
									<div key={nanoid()}>
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
					<MethodCard key={nanoid()} method={m} />
				))}

			</section>

			{/* Styles */}
{["1.58", "1.59"].includes(version) ? (
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
          All NotificationStyles attributes are deprecated in v1.59.3, but
          they're still available for backward compatibility. You can use the{" "}
          <span className="code yellow-shade">style</span> attribute in the
          Notification class to set styles.
        </p>
      </>
    )}

    <div className="flex flex-wrap align-items-cen justify-content-cen styles-container">
      {data?.STYLE_ATTRIBUTES?.map((m) => (
        <div
          key={nanoid()}
          className="bg-gray-50 rounded-lg shadow-sm hover:shadow-md transition"
        >
          <h3 className="style-attr">
            <code>{m.signature}</code>
          </h3>
          <p className="text-gray-700 new-line-active">{m.description}</p>
        </div>
      ))}
    </div>
  </section>
) : (
  <></>
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
