// import { Link } from "react-router";
import { ChevronDown, ChevronUp } from 'lucide-react';
import {nanoid }from 'nanoid'

import { ScrollToSection } from '../ui/ScrollAssist';
// import { ChevronLeft, ChevronRight } from 'lucide-react';
// import { Link } from 'react-router'
import './../assets/css/versionspage.css'
// import btnsImg from './../assets/imgs/btns.jpg'
// import progressbarImg from './../assets/imgs/progress.jpg'

// import { CodeBlock } from '../ui/CodeBlock/CodeBlock';
import {
    useEffect,
    //  useEffect,
      useState } from 'react';

// const [sudoku_puzzle, setSudokuPuzzle] = useState<(number | '')[][]>()
{/* <React.SetStateAction<string>></React.SetStateAction> */ }
function DropDown({ title, sections }: { title: string; sections: { msg: React.ReactNode; type: 'good' | 'warning' | 'bad' | '' }[] }) {
    const [opened, setOpened] = useState(false)
    const warnings = sections.filter(each => each.type === 'warning')
    const critical_list = sections.filter(each => each.type === 'bad')
    const features_list = sections.filter(each => each.type === 'good')
    function togglePreview() {
        setOpened(old => !old)
    }

    // useEffect(() => {
    //     sections.forEach(each_section => {
    //         const hash_ = '#' + each_section.trim().toLocaleLowerCase().replace(/ /g, '-')
    //         if (hash === hash_) setOpened(true)
    //     })
    // }, [hash, sections])
    return (
        <div className="dropdown flex fd-column align-items-cen justify-content-cen no-text-select">
            <div className="header flex align-items-cen width100per space-between">
                <p>
                    {title}
                </p>
                {warnings.length > 0 && <span className="warning ver-badge flex align-items-cen justify-content-cen">{warnings.length}</span>}
                {critical_list.length > 0 && <span className="bad ver-badge flex align-items-cen justify-content-cen" >{critical_list.length}</span>}
                {features_list.length > 0 && <span className="good ver-badge flex align-items-cen justify-content-cen" >{features_list.length}</span>}
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
                            return <li key={nanoid()} className={type} style={{listStyleType: ['good', 'warning', 'bad'].includes(type) ? 'initial' : 'none' }}>
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
export default function VersionsPage({ setVersion }: { setVersion: React.Dispatch<React.SetStateAction<string>> }) {
    
    useEffect(() => {
        setVersion('1.58')
    }, [setVersion])

    return (
        <div className="page main-page versions-page flex fd-column">
            <ScrollToSection />
            <section className="page-section rules">
                <p className="good">Version's marked with green have new features or API</p>
                <p className="warning">Yellow marker means has API change or had an issue with an advanced method</p>
                <p className="bad">Any Version marked red had a critical serious</p>
                <hr />
            </section>
            <section className="versions">
                <DropDown title='version-1.59' sections={[
                    { msg: 'Add new features', type: '' },
                    { msg: <>methods to cancel certain and all Notifications<span className="code">Notification.cancel()</span>, <span className="code">Notification.cancelAll</span></>, type: 'good' },
                    { msg: <>Added a way to access Old Notification instance with <span className="code">Notification.id</span> </>, type: 'good' },
                    { msg: 'Add methods working to free up __init__ kwargs [parsing out `style` attribute]', type: '' },
                    { msg: <><span className="code">setSmallIcon</span> == <span className="code yellow-shade">Notification(...,app_icon="...") </span></>, type: 'good' },
                    { msg: <><span className="code">setLargeIcon</span> == <span className="code yellow-shade">Notification(...,large_icon_path="...",style=NotificationStyles.LARGE_ICON)</span></>, type: 'good' },
                    { msg: <><span className="code">setBigPicture</span> == <span className="code yellow-shade">Notification(...,body="...",style=NotificationStyles.BIG_PICTURE)</span></>, type: 'good' },
                    { msg: <><span className="code">setBigText</span> == <span className="code yellow-shade">Notification(...,big_picture_path="...",style=NotificationStyles.BIG_TEXT)</span></>, type: 'good' },
                    { msg: 'Changed ', type: '' },
                    { msg: '`Notification.identifer` to `Notification.name`', type: 'warning' },
                    { msg: '`NotificationHandler.get_id` to `NotificationHandler.get_name`', type: 'warning' },
                ]} />
                <DropDown title='version-1.58' sections={[
                    { msg: '`showInfiniteProgressBar` Had no guard block when not on android', type: 'warning' },
                ]} />
            </section>

        </div>
    )
}