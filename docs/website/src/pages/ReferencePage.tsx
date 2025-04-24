import '../assets/css/referencepage.css';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Link } from 'react-router'

const INSTANCE_METHODS = [
	{
		id: 'init',
		signature: `init
	title: str = ''
	message: str = ''
	style: str = 'simple'
	big_picture_path: str = ''
	large_icon_path: str = ''
	progress_current_value: int = 0
	progress_max_value: int = 100
	body: str = ''
	callback: Callable=None
	channel_name: str = ''
	channel_id: str = ''
	app_icon: str = ''
	logs: bool = True
`,
		description: 'Initializes the notification instance.',
		args: [
			{ name: 'title', desc: 'string containing notification title'},
			{ name: 'message', desc: 'string containing notification message'},
			{ name: 'style', desc: "can be ['simple','progress','inbox','big_text','large_icon','big_picture','both_imgs]"},
			{ name: 'big_picture_path', desc: "path or url to big image (for `BIG_PICTURE` style)"},
			{ name: 'large_icon_path', desc: "path or url to image (for `LARGE_ICON` style)"},
			{ name: 'progress_current_value', desc: "integer to set progress bar current value (for `PROGRESS` style)."},
			{ name: 'progress_max_value', desc: "integer for max range for progress value."},
			{ name: 'body', desc: "Detailed text (for `BIG_TEXT` style)."},
			{ name: 'callback', desc: "Function executed on notification tap."},
			{ name: 'channel_name', desc: "Human-readable channel name."},
			{ name: 'channel_id', desc: "Channel identifier (sanitized from name if not provided)."},
			{ name: 'app_icon', desc: 'If not specified, defaults to the app icon. To change it, use a PNG—otherwise it will render as a black box.'},
			{ name: 'logs', desc: 'Enable debug logs when not on Android.'},

		]
	},
	{
		id: 'addButton',
		signature: 'addButton(text, on_release)',
		description: 'Adds an action button to the notification.',
		args: [
			{ name: 'text', desc: 'Label for the button.' },
			{ name: 'on_release', desc: 'Callback invoked when the button is tapped.' }
		]
	},
	{
		id: 'removeButtons',
		signature: 'removeButtons()',
		description: 'Removes all action buttons from the notification.'
	},
	{
		id: 'removeProgressBar',
		signature: 'removeProgressBar(message?, show_on_update?, title?)',
		description:
			'Removes the progress bar and (optionally) updates the title/message.',
		args: [
			{ name: 'message', desc: '(Optional) New message; defaults to last.' },
			{
				name: 'show_on_update',
				desc: 'If true, briefly shows the updated notification. Defaults to true.'
			},
			{ name: 'title', desc: '(Optional) New title; defaults to last.' }
		]
	},
	{
		id: 'send',
		signature: 'send(silent?, persistent?, close_on_click?)',
		description: 'Dispatches the notification.',
		args: [
			{ name: 'silent', desc: 'If true, suppresses the heads-up alert.' },
			{ name: 'persistent', desc: 'If true, the notification survives “Clear All.”' },
			{ name: 'close_on_click', desc: 'If true, tapping the notification dismisses it.' }
		]
	},
	{
		id: 'showInfiniteProgressBar',
		signature: 'showInfiniteProgressBar()',
		description:
			'Shows an indeterminate progress bar. Remove with `removeProgressBar()` or update with `updateProgressBar()`.'
	},
	{
		id: 'updateMessage',
		signature: 'updateMessage(new_message)',
		description: 'Updates the notification message.',
		args: [
			{ name: 'new_message', desc: 'String for the new message.' }
		]
	},

	{
		id: 'addNotificationStyle',
		signature: 'addNotificationStyle(style, already_sent?)',
		description:
			'Applies or updates a notification style (big_text, inbox, images, etc.).',
		args: [
			{
				name: 'style',
				desc:
					"One of ['simple','progress','inbox','big_text','large_icon','big_picture','both_imgs']"
			},
			{
				name: 'already_sent',
				desc: 'If true, re-dispatches the notification so style changes appear immediately.'
			}
		]
	},
	{
		id: 'updateProgressBar',
		signature: 'updateProgressBar(current_value, message?, title?, cooldown?)',
		description:
			'Updates a determinate progress bar (0 – max). Internally throttled to 0.5 s.',
		args: [
			{ name: 'current_value', desc: 'Current progress (number).' },
			{ name: 'message', desc: '(Optional) New message; defaults to last.' },
			{ name: 'title', desc: '(Optional) New title; defaults to last.' },
			{ name: 'cooldown', desc: "Defaults to 0.5secs,buffer time for when changes happen too fast, shouldn't be changed unless tested on specific device" }
		]
	},
	{
		id: 'updateTitle',
		signature: 'updateTitle(new_title)',
		description: 'Updates the notification title.',
		args: [
			{ name: 'new_title', desc: 'String for the new title.' }
		]
	}
];

const HANDLER_METHODS = [
	{
		id: 'getIdentifer',
		signature: 'NotificationHandler.getIdentifer()',
		description:
			'Returns the unique string identifier for the notification or button that opened the app.'
	},
	{
		id: 'bindNotifyListener',
		signature: 'NotificationHandler.bindNotifyListener()',
		description:
			'Binds by Default, Attaches a global listener to notification taps—your callbacks will fire when any notification is tapped.'
	},
	{
		id: 'unbindNotifyListener',
		signature: 'NotificationHandler.unbindNotifyListener()',
		description: 'Removes the listener set by `bindNotifyListener()`.'
	},
	{
		id: 'is_on_android',
		signature: 'NotificationHandler.is_on_android()',
		description:
			'Returns `true` if running on Android, `false` otherwise—useful for platform checks.'
	}
];



const STYLE_ATTRIBUTES = [
	{
		id: 'simple',
		signature: 'NotificationStyles.DEFAULT',
		description: 'contains default style "simple"' 
	},
	{
		id: 'LARGE_ICON',
		signature: 'NotificationStyles.LARGE_ICON',
		description: "contains 'large_icon' value",
	},
	{
		id: 'BIG_PICTURE',
		signature: 'NotificationStyles.BIG_PICTURE',
		description: "contains 'big_picture' value",
	},
	{
		id: 'BOTH_IMGS',
		signature: 'NotificationStyles.BOTH_IMGS',
		description: "contains 'both_imgs' value",
	},
	{
		id: 'PROGRESS',
		signature: 'NotificationStyles.PROGRESS',
		description:
			"contains 'progress' value"
	},
	{
		id: 'INBOX',
		signature: 'NotificationStyles.INBOX',
		description: "contains 'inbox' value",
	},
	{
		id: 'BIG_TEXT',
		signature: 'NotificationStyles.BIG_TEXT',
		description: "contains 'big_text' value",
	},
];

export default function ReferencePage() {
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

			{/* Instance Methods Section */}
			<section id="notification-class" className="space-y-6 page-section" tabIndex={0}>
				<h2 className="text-xl font-bold">Notification Attributes and Methods</h2>
				{INSTANCE_METHODS.map((m) => (
					<div
						key={m.id}
						className="bg-gray-50 p-4 rounded-lg shadow-sm transition"
					>
							<p className={m.id +' ref-code'} >
								{m.signature.replace(/\t/g, '\u00A0\u00A0\u00A0\u00A0')}
								</p>

						<p className="paragraph mb-2 text-gray-700">{m.description}</p>
						{m.args && (
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

			<section id="notificationhandler-class" className="space-y-6 page-section" tabIndex={0}>
				<h2 className="text-xl font-bold">NotificationHandler Methods</h2>
				{HANDLER_METHODS.map((m) => (
					<div
						key={m.id}
						className="bg-gray-50 p-4 rounded-lg shadow-sm hover:shadow-md transition"
					>
						<p className="handler-method">{m.signature}</p>
						<p className="text-gray-700">{m.description}</p>
					</div>
				))}
			</section>

			<section id="notificationstyles-class" className="space-y-6 page-section" tabIndex={0}>
				<h2 className="text-xl font-bold">NotificationStyles attributes for Safely Adding Styles</h2>
				<div className='flex flex-wrap align-items-cen justify-content-cen styles-container'>

				{STYLE_ATTRIBUTES.map((m) => (
					<div
					key={m.id}
					className="bg-gray-50 rounded-lg shadow-sm hover:shadow-md transition"
					>
						<h3 className="style-attr">
							<code>{m.signature}</code>
						</h3>
						<p className="text-gray-700">{m.description}</p>
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
