import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Link } from 'react-router'
import { CodeBlock } from "../ui/CodeBlock/CodeBlock";
import { ScrollToSection } from "../ui/ScrollAssist";
import '../assets/css/advmethodspage.css'
// import { adding_image_code, channel_management_code, getting_identifer, progress_bar_update, title_and_message_update } from "./versions-data/advmethodspage";
import channelimg from '../assets/imgs/channelname.jpg'
import { useEffect, useState } from 'react';
import { Iversion } from '../assets/js/mytypes';
import { isLegacyVersion } from '../assets/js/helper';


interface IAdvancedMethodsPage {
    title_and_message_update_code: string;
    progress_bar_update_code: string;
    adding_image_code: string;
    channel_management_code: string;
    getting_identifier_code: string;
}

export default function AdvancedMethodsPage({ version }: { version: Iversion }) {
    const [data, setData] = useState<IAdvancedMethodsPage>()

    async function changeVersionData(version: Iversion) {

        const v1 = await import(`./versions-data/1.58.tsx`);
        const v2 = await import(`./versions-data/1.59.tsx`);
        const data = await import(`./versions-data/${version}.tsx`);
        setData({...v1.advanced_methods_page,...v2.advanced_methods_page,...data.advanced_methods_page})
    }
    useEffect(() => {
        changeVersionData(version)
    }, [version])
    return (
        <div className="main-page page adv-methods-page">
            <ScrollToSection />
            <section id='updating-notification' className="page-section">
                <h2 className=" long-title">Updating Notification</h2>
                <hr />
                <p>There Available methods to interact with notification after sending</p>
                <h3 className="underline text-xl mt-[10px] mb-[0]">For Texts:</h3>
                <p tabIndex={0} className="paragraph">For Changing <span className="code">title</span> and <span className="code">message</span> after sending:</p>
                <CodeBlock title="Title & Message" code={data?.title_and_message_update_code || ''} />
                <h3 className="underline text-xl mt-[10px] mb-[0]">For Progress Bars:</h3>
                <ul className="inner-section-2 paragraph">
                    <li>Avoid changing it value in intervals less than 0.5sec</li>
                    <li>And always pass in the new title and message if any to <span className="code">updateProgressBar</span> method</li>
                </ul>
                <span className="paragraph code yellow flex progressbar-warning">Android ignores updates faster than 0.5sec on some devices</span>
                <CodeBlock title="Progress-Bar" code={data?.progress_bar_update_code || ''} />
            </section>

            <section id='adding-image' className="page-section">
                <h3 className="underline text-xl mt-[10px] mb-[0]">For Images:</h3>
                {/* <p tabIndex={0} className="paragraph">For Images:</p> */}
                <p className="paragraph">To add image after sending
                {isLegacyVersion(version) ?
                    <>
                        <span> set </span>
                        <span className="code">already_sent</span> in <span className="code">addNotificationStyle</span> method to <span className="code">true</span>
                    </>
                    :
                    <>
                    <span> use </span>
                    <span className="code">setLargeIcon</span> or <span className="code">setBigPicture</span> then <span className="code">.refresh</span> 
                    </>
                }
                </p>
                <CodeBlock title="Image" code={data?.adding_image_code || ''} />
            </section>

            <section id="channel-management" className="page-section" tabIndex={0}>

                <h2 className="long-title">Channel Management</h2>
                <hr />
                <p className="paragraph">From Android 8.0 above channels are required, android-notify use <span className="code">Default Channel</span> if no channel specified.</p>
                <p className="paragraph">You can customize the channel name and ID:</p>
                <ul className="inner-section-2 paragraph">
                    <li>If not specified <span className="code">channel_id</span> will be auto generated from <span className="code">channel_name</span></li>
                    <li className="inner-section-2">Using this format <span className="code">.lower().replace(' ', '_')</span> </li>
                    <li>Custom Channel Name's Gives User ability to turn on/off specific notifications</li>
                </ul>
                <CodeBlock title='Channel Management' code={data?.channel_management_code || ''} img={channelimg} />
            </section>

            <section id="getting-identifer" className="page-section" tabIndex={0}>
                <h2 className="long-title">Getting Identifer</h2>
                <hr />
                <p>If you want to get the Exact Notification Clicked to Open App, you can use NotificationHandler to get unique identifer (str) <span className="code">NotificationHandler{isLegacyVersion(version) ? ".getIdentifer" : '.get_name'}</span></p>

                <p>
                    {isLegacyVersion(version) && <span className="code warning yellow paragraph block width-max-con">In next version identifer will be changed to `name` and NotificationHandler.getIdentifer to NotificationHandler.get_name</span>}
                </p>
                <CodeBlock title="Identifer" code={data?.getting_identifier_code || ''} pydroid={data?.getting_identifier_code || ''} />
            </section>


            <span className='flex next-page-btns-box space-between'>
                <Link className='next-page-btn' to='/components'>
                    <ChevronLeft />
                    <span>
                        <p className='next-txt'>Previous</p>
                        <p className='page-name'>Components</p>
                    </span>
                </Link>
                <Link className='next-page-btn' to='/reference'>
                    <span>
                        <p className='next-txt'>Next</p>
                        <p className='page-name'>Reference</p>
                    </span>
                    <ChevronRight />
                </Link>

            </span>
            {/* <Compo */}
            {/* <h3 className="page-subtitle">Updating Notification</h3>
            <p className="page-text"> You can update a notification after it has been created by using the <code>update</code> method. This method takes an object with the same properties as the original notification, and updates the notification with the new values.</p> */}

        </div>
    )
}