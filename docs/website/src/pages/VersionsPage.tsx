import { useState } from 'react';
import { nanoid } from 'nanoid'
import { ChevronDown, ChevronUp } from 'lucide-react';
import { ScrollToSection } from '../ui/ScrollAssist';
import './../assets/css/versionspage.css'

interface IDropDown {
    version: number;
    sections: { msg: React.ReactNode; type: 'good' | 'warning' | 'bad' | '' }[];
    setVersion: React.Dispatch<React.SetStateAction<number>>
}

function DropDown({ version, sections, setVersion }: IDropDown) {
    const [opened, setOpened] = useState(false)
    const warnings = sections.filter(each => each.type === 'warning')
    const critical_list = sections.filter(each => each.type === 'bad')
    const features_list = sections.filter(each => each.type === 'good')
    function togglePreview() {
        setOpened(old => !old)
    }
    function switchToDocs() {
        setVersion(version)
    }
    return (
        <div className="dropdown flex fd-column align-items-cen justify-content-cen">
            <div className="header flex align-items-cen width100per flex-wrap">
                <p>
                    {'version-' + (version == 1.6? "1.60": version)}
                </p>
                <div className='flex margin-left-auto'>
                    {warnings.length > 0 && <span className="warning ver-badge flex align-items-cen justify-content-cen">{warnings.length}</span>}
                    {critical_list.length > 0 && <span className="bad ver-badge flex align-items-cen justify-content-cen" >{critical_list.length}</span>}
                    {features_list.length > 0 && <span className="good ver-badge flex align-items-cen justify-content-cen" >{features_list.length}</span>}
                </div>
                <div className='flex'>

                    <button onClick={switchToDocs} className='switch-to-docs-btn'>Switch to Docs</button>
                    <button onClick={togglePreview} className="flex align-items-cen justify-content-cen">
                        {opened ? <ChevronUp /> : <ChevronDown />}
                    </button>
                </div>
            </div>
            <ol className="content width100per flex fd-column" style={{ height: opened ? 'auto' : '0px' }}>
                {
                    sections.length ?
                        sections.map(({ msg, type }) => {
                            return <li key={nanoid()} className={type} style={{ listStyleType: ['good', 'warning', 'bad'].includes(type) ? 'initial' : 'none' }}>
                                <p>
                                    {msg}
                                </p>
                            </li>
                        })
                        :
                        <li>
                            No Content
                        </li>
                }
            </ol>
        </div>
    )

}
export default function VersionsPage({ setVersion }: { setVersion: React.Dispatch<React.SetStateAction<number>> }) {


    return (
        <div className="page main-page versions-page flex fd-column">
            <ScrollToSection />
            <section className="page-section rules">
                <p className="good">Version's marked with green have new features or API</p>
                {/* <p>Yellow marker  while For older issue had an <p className="warning">issue with an advanced method</p></p> */}
                <p className='warning'>For Yellow marker:</p>
                <ul className='inner-section-2'>
                    <li className='inner-section-1'>for newer version means has API change</li>
                    <li className='inner-section-1'>for older version issue with an advanced method</li>
                </ul>
                <p className="bad">Any Version marked red had a critical issue</p>
                <hr />
            </section>
            <section className="versions">
                <DropDown
  setVersion={setVersion}
  version={1.6}
  sections={[
    { msg: 'Improvements', type: '' },

    { msg: 'Interactions in Service: A way to pass in BroadCast Reciver and Actions to Buttons', type: 'good' },

    { msg: <>Usage without gradle dependencies: new branch <span className="code green-shade">without-androidx</span> was created, allowing usage in Pyroid3 and Flet apps. Install via <span className="code green-shade">__version__.dev0</span>.</>, type: 'good' },

    { msg: 'Flet support: Beta support for Flet Python apps.', type: 'good' },

    { msg: 'Better Logging: replaced prints with Python logger, allowing log levels.', type: 'good' },

    { msg: 'Modularization: split package into smaller task-based structure for easier management.', type: 'good' },


    { msg: <>Class: <span className="code">Notification</span></>, type: '' },

    { msg: 'New Arguments', type: '' },
    { msg: <><span className="code">addButton</span> - receiver_name, action</>, type: 'good' },
    { msg: <><span className="code">createChannel</span> - vibrate, res_sound_name</>, type: 'good' },
    { msg: <><span className="code">setBigText</span> - title, summary</>, type: 'good' },

    { msg: 'New Methods', type: '' },
    { msg: <><span className="code">setColor</span> - color, changes app icon color using hex code.</>, type: 'good' },
    { msg: <><span className="code">setSubText</span> - text, Adds small text near the title.</>, type: 'good' },
    { msg: <><span className="code">setWhen</span> - secs_ago, to change the time the notification was created.</>, type: 'good' },
    { msg: <><span className="code">channelExists</span> - channel_id, to check if said channel exists.</>, type: 'good' },
    { msg: <><span className="code">doChannelsExist</span> - ids, returns those that do not exist.</>, type: 'good' },
    { msg: <><span className="code">setData</span> - attach a dictionary of data for later use.</>, type: 'good' },
    { msg: <><span className="code">fVibrate</span> - force vibration even if disabled in device settings.</>, type: 'good' },
    { msg: <><span className="code">fill_args</span> - fills notification args without sending.</>, type: 'good' },

    { msg: 'Support for devices less than Android 8', type: 'good' },
    { msg: <><span className="code">setVibrate</span> - pattern, defaults to a single vibration.</>, type: 'good' },
    { msg: <><span className="code">setSound</span> - res_sound_name, changes the default notification sound.</>, type: 'good' },


    { msg: <>Class: <span className="code">NotificationHandler</span></>, type: '' },

    { msg: 'New Arguments', type: '' },
    { msg: <><span className="code">get_name</span> - on_start must be True when called from App.on_start().</>, type: 'good' },

    { msg: 'New Property', type: '' },
    { msg: <><span className="code">data_object</span> - access data added via Notification.setData.</>, type: 'good' },
  ]}
/>
                <DropDown setVersion={setVersion} version={1.59} sections={[
                    { msg: 'Add new features', type: '' },
                    { msg: <>Added a way to access Old Notification instance with <span className="code">Notification().id</span> </>, type: 'good' },
                    { msg: <>methods to cancel a certain or all Notifications<span className="code">Notification().cancel()</span>, <span className="code">Notification.cancelAll</span>, For if old instance not available and need to cancel one use id with <span className="code">Notification.cancel(_id)</span></>, type: 'good' },
                    { msg: <>When setting a new component after <span className="code">Notification().send</span>  use <span className="code">Notification().refresh</span> </>, type: 'good' },
                    { msg: <>Instead of only requesting in init created <span className="code">NotificationHandler.asks_permission</span> and <span className="code">NotificationHandler.has_permission</span> </>, type: 'good' },
                    { msg: 'Add methods working to free up __init__ kwargs [parsing out `style` attribute]', type: '' },
                    { msg: <><span className="code">setSmallIcon</span> == <span className="code yellow-shade">Notification(...,app_icon="...") </span></>, type: 'good' },
                    { msg: <><span className="code">setLargeIcon</span> == <span className="code yellow-shade">Notification(...,large_icon_path="...",style=NotificationStyles.LARGE_ICON)</span></>, type: 'good' },
                    { msg: <><span className="code">setBigPicture</span> == <span className="code yellow-shade">Notification(...,body="...",style=NotificationStyles.BIG_PICTURE)</span></>, type: 'good' },
                    { msg: <><span className="code">setBigText</span> == <span className="code yellow-shade">Notification(...,big_picture_path="...",style=NotificationStyles.BIG_TEXT)</span></>, type: 'good' },
                    { msg: <>For creating channels <span className="code">Notification.createChannel(name, id, desc</span> </>, type: 'good' },
                    { msg: <>For deleting channels <span className="code">Notification.deleteAllChannel()</span> and <span className="code">Notification.deleteChannel(channel_id)</span> </>, type: 'good' },
                    { msg: 'Changed ', type: '' },
                    { msg: '`Notification.identifer` to `Notification.name`', type: 'warning' },
                    { msg: '`NotificationHandler.getIdentifer` to `NotificationHandler.get_name`', type: 'warning' },
                ]} />
                <DropDown setVersion={setVersion} version={1.58} sections={[
                    { msg: '`showInfiniteProgressBar` Had no guard block when not on android', type: 'warning' },
                    { msg: '`NotificationHandler.getIdentifer` always returned value even when app not opened from notification', type: 'bad' },
                ]} />
            </section>

        </div>
    )
}


// import { nanoid } from "nanoid";
// import React from "react";

// interface ReleaseItem {
//   msg: React.ReactNode;
//   type: "good" | "warning" | "bad" | "";
// }

// interface ReleaseProps {
//   version: number;
//   sections: ReleaseItem[];
//   setVersion: React.Dispatch<React.SetStateAction<number>>;
// }

// // Helper to group sections
// function groupSections(sections: ReleaseItem[]) {
//   return {
//     good: sections.filter(s => s.type === "good"),
//     warning: sections.filter(s => s.type === "warning"),
//     bad: sections.filter(s => s.type === "bad"),
//     neutral: sections.filter(s => s.type === ""),
//   };
// }

// // Single Release Card
// function Release({ version, sections, setVersion }: ReleaseProps) {
//   const { good, warning, bad, neutral } = groupSections(sections);

//   return (
//     <article className="relative border-l-4 border-blue-500 pl-6 mb-12">
//       {/* Version Header */}
//       <div className="flex items-center justify-between mb-4">
//         <h2 className="text-2xl font-bold text-white">
//           Version {version === 1.6 ? "1.60" : version}
//         </h2>
//         <button
//           onClick={() => setVersion(version)}
//           className="text-sm text-blue-400 hover:underline"
//         >
//           View Docs →
//         </button>
//       </div>

//       <div className="space-y-6 text-sm">
//         {good.length > 0 && (
//           <div>
//             <h3 className="text-green-400 font-semibold mb-2">Added</h3>
//             <ul className="space-y-2 text-zinc-300 list-disc list-inside">
//               {good.map(item => (
//                 <li key={nanoid()}>{item.msg}</li>
//               ))}
//             </ul>
//           </div>
//         )}

//         {warning.length > 0 && (
//           <div>
//             <h3 className="text-yellow-400 font-semibold mb-2">Changed</h3>
//             <ul className="space-y-2 text-zinc-300 list-disc list-inside">
//               {warning.map(item => (
//                 <li key={nanoid()}>{item.msg}</li>
//               ))}
//             </ul>
//           </div>
//         )}

//         {bad.length > 0 && (
//           <div>
//             <h3 className="text-red-400 font-semibold mb-2">Fixed / Critical</h3>
//             <ul className="space-y-2 text-zinc-300 list-disc list-inside">
//               {bad.map(item => (
//                 <li key={nanoid()}>{item.msg}</li>
//               ))}
//             </ul>
//           </div>
//         )}

//         {neutral.length > 0 && (
//           <div>
//             <h3 className="text-zinc-500 font-semibold mb-2">Notes</h3>
//             <ul className="space-y-2 text-zinc-400 list-disc list-inside">
//               {neutral.map(item => (
//                 <li key={nanoid()}>{item.msg}</li>
//               ))}
//             </ul>
//           </div>
//         )}
//       </div>
//     </article>
//   );
// }

// // Main Page
// export default function VersionsPage({
//   setVersion,
// }: {
//   setVersion: React.Dispatch<React.SetStateAction<number>>;
// }) {
//   return (
//     <div className="max-w-3xl mx-auto px-5 py-16">
//       <h1 className="text-4xl font-bold mb-3 text-white">Changelog</h1>
//       <p className="text-zinc-400 mb-12">
//         Track new features, improvements, and fixes in each version.
//       </p>

//       <section className="space-y-12">
//         {/* v1.60 */}
//         <Release
//           version={1.6}
//           setVersion={setVersion}
//           sections={[
//             { msg: "Interactions in Service: pass receivers and button actions.", type: "good" },
//             {
//               msg: (
//                 <>
//                   Usage without gradle via <span className="code text-green-400">without-androidx</span>.
//                 </>
//               ),
//               type: "good",
//             },
//             { msg: "Flet support (beta).", type: "good" },
//             { msg: "Better logging with Python logger instead of prints.", type: "good" },
//             { msg: "Modularization: split package into smaller task-based structure.", type: "good" },
//             { msg: "New Arguments in Notification class: addButton, createChannel, setBigText", type: "" },
//             { msg: "New Methods in Notification: setColor, setSubText, setWhen, channelExists, doChannelsExist, setData, fVibrate, fill_args", type: "" },
//             { msg: "Support for devices less than Android 8.", type: "good" },
//             { msg: "New Arguments in NotificationHandler: get_name", type: "" },
//             { msg: "New Property: data_object", type: "" },
//           ]}
//         />

//         {/* v1.59 */}
//         <Release
//           version={1.59}
//           setVersion={setVersion}
//           sections={[
//             { msg: "Add new features", type: "good" },
//             {
//               msg: (
//                 <>
//                   Added a way to access Old Notification instance with{" "}
//                   <span className="code text-green-400">Notification().id</span>
//                 </>
//               ),
//               type: "good",
//             },
//             { msg: "Methods to cancel a certain or all notifications.", type: "good" },
//             { msg: "Changed Notification.identifier → Notification.name", type: "warning" },
//             { msg: "Changed NotificationHandler.getIdentifier → NotificationHandler.get_name", type: "warning" },
//           ]}
//         />

//         {/* v1.58 */}
//         <Release
//           version={1.58}
//           setVersion={setVersion}
//           sections={[
//             { msg: "`showInfiniteProgressBar` had no guard block when not on android", type: "warning" },
//             { msg: "`NotificationHandler.getIdentifier` always returned value even when app not opened from notification", type: "bad" },
//           ]}
//         />
//       </section>
//     </div>
//   );
// }
