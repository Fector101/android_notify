import '../assets/css/referencepage.css';

const INSTANCE_METHODS = [
  {
    id: 'init',
    signature: 'init({ app_icon })',
    description: 'Initializes the notification instance.',
    args: [
      {
        name: 'app_icon',
        desc: 'If not specified, defaults to the app icon. To change it, use a PNG—otherwise it will render as a black box.'
      }
    ]
  },
  {
    id: 'send',
    signature: 'send({ silent, persistent, close_on_click })',
    description: 'Dispatches the notification.',
    args: [
      { name: 'silent', desc: 'If true, suppresses the heads-up alert.' },
      { name: 'persistent', desc: 'If true, the notification survives “Clear All.”' },
      { name: 'close_on_click', desc: 'If true, tapping the notification dismisses it.' }
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
    id: 'updateTitle',
    signature: 'updateTitle(new_title)',
    description: 'Updates the notification title.',
    args: [
      { name: 'new_title', desc: 'String for the new title.' }
    ]
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
    id: 'showInfiniteProgressBar',
    signature: 'showInfiniteProgressBar()',
    description:
      'Shows an indeterminate progress bar. Remove with `removeProgressBar()` or update with `updateProgressBar()`.'
  },
  {
    id: 'updateProgressBar',
    signature: 'updateProgressBar(current_value, message?, title?)',
    description:
      'Updates a determinate progress bar (0–max). Internally throttled to 0.5 s.',
    args: [
      { name: 'current_value', desc: 'Current progress (number).' },
      { name: 'message', desc: '(Optional) New message; defaults to last.' },
      { name: 'title', desc: '(Optional) New title; defaults to last.' }
    ]
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
      'Attaches a global listener to notification taps—your callbacks will fire when any notification is tapped.'
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

export default function ReferencePage() {
  return (
    <div className="page main-page">

      {/* Page Title */}
      <h1 className="text-2xl font-bold">android-notify Reference</h1>

      {/* Table of Contents */}
      <nav className="border-l-4 border-blue-600 pl-4">
        <h2 className="font-semibold mb-2">Contents</h2>
        <ul className="space-y-1 text-sm">
          <li>
            <a href="#instance-methods" className="text-blue-600 hover:underline">
              Instance Methods
            </a>
          </li>
          <li>
            <a href="#handler-methods" className="text-blue-600 hover:underline">
              NotificationHandler Methods
            </a>
          </li>
        </ul>
      </nav>

      {/* Instance Methods Section */}
      <section id="instance-methods" className="space-y-6">
        <h2 className="text-xl font-bold">Instance Methods</h2>
        {INSTANCE_METHODS.map((m) => (
          <div
            key={m.id}
            className="bg-gray-50 p-4 rounded-lg shadow-sm hover:shadow-md transition"
          >
            <h3 className="text-lg font-semibold mb-1">
              <code>{m.signature}</code>
            </h3>
            <p className="mb-2 text-gray-700">{m.description}</p>
            {m.args && (
              <dl className="pl-4 space-y-1">
                {m.args.map(({ name, desc }) => (
                  <div key={name}>
                    <dt className="font-medium">{name}</dt>
                    <dd className="ml-4">{desc}</dd>
                  </div>
                ))}
              </dl>
            )}
          </div>
        ))}
      </section>

      <section id="handler-methods" className="space-y-6">
        <h2 className="text-xl font-bold">NotificationHandler Methods</h2>
        {HANDLER_METHODS.map((m) => (
          <div
            key={m.id}
            className="bg-gray-50 p-4 rounded-lg shadow-sm hover:shadow-md transition"
          >
            <h3 className="text-lg font-semibold mb-1">
              <code>{m.signature}</code>
            </h3>
            <p className="text-gray-700">{m.description}</p>
          </div>
        ))}
      </section>

    </div>
  );
}
