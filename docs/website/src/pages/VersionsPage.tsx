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

function DropDown({ version, sections, setVersion }:IDropDown) {
    const [opened, setOpened] = useState(false)
    const warnings = sections.filter(each => each.type === 'warning')
    const critical_list = sections.filter(each => each.type === 'bad')
    const features_list = sections.filter(each => each.type === 'good')
    function togglePreview() {
        setOpened(old => !old)
    }
    function switchToDocs() {
        // console.log(''+version)
        setVersion(version)
    }
    // useEffect(() => {
    //     sections.forEach(each_section => {
    //         const hash_ = '#' + each_section.trim().toLocaleLowerCase().replace(/ /g, '-')
    //         if (hash === hash_) setOpened(true)
    //     })
    // }, [hash, sections])
    return (
        <div className="dropdown flex fd-column align-items-cen justify-content-cen">
            <div className="header flex align-items-cen width100per space-between">
                <p>
                    {'version-' + version}
                </p>
                {warnings.length > 0 && <span className="warning ver-badge flex align-items-cen justify-content-cen">{warnings.length}</span>}
                {critical_list.length > 0 && <span className="bad ver-badge flex align-items-cen justify-content-cen" >{critical_list.length}</span>}
                {features_list.length > 0 && <span className="good ver-badge flex align-items-cen justify-content-cen" >{features_list.length}</span>}
                <button onClick={switchToDocs} className='switch-to-docs-btn'>Switch to Docs</button>
                <button onClick={togglePreview} className="flex align-items-cen justify-content-cen">
                    {opened ? <ChevronUp /> : <ChevronDown />}
                </button>
            </div>
            <ol className="content width100per flex fd-column" style={{ height: opened ? 'auto' : '0px' }}>
                {
                    sections.length ?
                        sections.map(({ msg, type }) => {
                            // const hash_ = '#' + each_section.toLocaleLowerCase().replace(/ /g, '-')
                            // const state = hash == hash_
                            return <li key={nanoid()} className={type} style={{ listStyleType: ['good', 'warning', 'bad'].includes(type) ? 'initial' : 'none' }}>
                                <p>
                                    {msg}
                                </p>
                                {/* <Link className={state ? 'active' : ''} to={route + hash_} tabIndex={opened ? 0 : -1}>
                                    {each_section}
                                </Link> */}
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
                    { msg: '`NotificationHandler.get_id` to `NotificationHandler.get_name`', type: 'warning' },
                ]} />
                <DropDown setVersion={setVersion} version={1.58} sections={[
                    { msg: '`showInfiniteProgressBar` Had no guard block when not on android', type: 'warning' },
                    { msg: '`NotificationHandler.get_id` always returned value even when app not opened from notification', type: 'bad' },
                ]} />
            </section>

        </div>
    )
}