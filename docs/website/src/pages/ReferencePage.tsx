import '../assets/css/referencepage.css';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { nanoid } from 'nanoid';
import { useEffect, useState } from 'react';
import { Link } from 'react-router'
import { Iversion } from '../assets/js/mytypes';
import { isLegacyVersion } from '../assets/js/helper';

type arg = { name: string; desc: string }
type object_list = {
	id: string;
	signature: string;
	description: string;
	args: arg[]
}
interface IReferencePage {
	NOTIFICATION_METHODS: object_list[];
	HANDLER_METHODS: object_list[];
	STYLE_ATTRIBUTES: object_list[];
}
export default function ReferencePage({ version }: { version: Iversion }) {
	const [data, setData] = useState<IReferencePage>()

	async function changeVersionData(version: Iversion) {

		const data = await import(`./versions-data/${version}.tsx`);
		setData(data.reference_page)
	}
	useEffect(() => {
		changeVersionData(version)
	}, [version])
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
			{version > 1.58 &&
				<section className='side-note'>
					<h2>For v1.59</h2>
					<p className='paragraph'>Add methods working to free up __init__ kwargs [parsing out `style` attribute] </p>
					<div className='paragraph'>
						<span className="cod paragraph">setSmallIcon</span> == <span className="code yellow-shade">Notification(..., app_icon="...") </span><br /><br />
						<span>setLargeIcon</span> == <span className="code yellow-shade">Notification(..., large_icon_path="...", style=NotificationStyles.LARGE_ICON)</span><br /><br />
						<span>setBigPicture</span> == <span className="code yellow-shade">Notification(..., big_picture_path="...",style=NotificationStyles.BIG_PICTURE)</span><br /><br />
						<span>setBigText</span> == <span className="code yellow-shade">Notification(..., body="...", style=NotificationStyles.BIG_TEXT)</span><br />
					</div>
				</section>}
			{/* Instance Methods Section */}
			<section id="notification-class" className="space-y-6 page-section" tabIndex={0}>
				<h2 className="text-xl font-bold">Notification Attributes and Methods</h2>
				{data?.NOTIFICATION_METHODS.map((m) => (
					<div
						key={nanoid()}
						className="bg-gray-50 p-4 rounded-lg shadow-sm transition"
					>
						<p className={m.id + ' ref-code'} >
							{m.signature.replace(/\t/g, '\u00A0\u00A0\u00A0\u00A0')}
						</p>

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

			<section id="notificationhandler-class" className="space-y-6 page-section" tabIndex={0}>
				<h2 className="text-xl font-bold">NotificationHandler Methods</h2>
				{data?.HANDLER_METHODS.map((m) => (
					<div
						key={nanoid()}
						className="bg-gray-50 p-4 rounded-lg shadow-sm hover:shadow-md transition"
					>
						<p className="handler-method">{m.signature}</p>
						<p className="text-gray-700">{m.description}</p>
					</div>
				))}
			</section>

			<section id="notificationstyles-class" className="space-y-6 page-section" tabIndex={0}>
				{isLegacyVersion(version) ?
					<h2 className="text-xl font-bold">NotificationStyles attributes for Safely Adding Styles</h2>
					:
					<>
						<h2 className="text-xl font-bold">NotificationStyles</h2>
						<p className="paragraph">
							All NotificationStyles attributes are deprecated in v1.59.3, but they're still available for backward compatibility.
							You can use the <span className="code yellow-shade">style</span> attribute in the Notification class to set styles.</p>
						<p>For example:</p>
						<p>Notification.setLargeIcon('profile.png') replaced</p>
						<p className="paragraph inner-section-2">
							<span className="code yellow-shade">Notification(..., large_icon_path="profile.png", style=NotificationStyles.LARGE_ICON)</span>
						</p>
						<p className="paragraph">
							You can also use the <span className="code yellow-shade">setLargeIcon</span>, <span className="code yellow-shade">setBigPicture</span>, <span className="code yellow-shade">setBigText</span> and <span className="code yellow-shade">setLines</span> methods to set the respective styles of <span className="code">NotificationStyles.LARGE_ICON</span>, <span className="code">NotificationStyles.BIG_PICTURE</span>, 
							<span className="code">NotificationStyles.BIG_TEXT</span> and <span className="code">NotificationStyles.INBOX</span>.
						</p>
					</>
				}
				<div className='flex flex-wrap align-items-cen justify-content-cen styles-container'>

					{data?.STYLE_ATTRIBUTES.map((m) => (
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

			<span className='flex next-page-btns-box space-between'>
				<Link className='next-page-btn' to='/advanced-methods'>
					<ChevronLeft />
					<span>
						<p className='next-txt'>Previous</p>
						<p className='page-name'>Advanced Methods</p>
					</span>
				</Link>
				<Link className='next-page-btn' to='/extras'>
					<span>
						<p className='next-txt'>Next</p>
						<p className='page-name'>Extras</p>
					</span>
					<ChevronRight />
				</Link>

			</span>
		</div>
	);
}
