"use client"
import { ChevronLeft, ChevronRight } from 'lucide-react';
import Link from 'next/link'
import dynamic from 'next/dynamic'
import '../../assets/css/advmethodspage.css'
import channelimg from '../../assets/imgs/channelname.jpg'
import { useEffect, useState } from 'react';
import { useVersion } from '../VersionContext';
import { versions } from '../../versions-data';

const CodeBlock = dynamic(() => import('../../ui/CodeBlock/CodeBlock').then(mod => mod.CodeBlock), { ssr: false });

interface IAdvancedMethodsPage {
    title_and_message_update_code: string;
    progress_bar_update_code: string;
    adding_image_code: string;
    channel_management_code: string;
    getting_identifier_code: string;
}

export default function AdvancedMethodsPage() {
    const { version } = useVersion();
    const [data, setData] = useState<IAdvancedMethodsPage>()

    useEffect(() => {
        const versionData = versions[String(version) as keyof typeof versions];
        setData(versionData.advanced_methods_page)
    }, [version])
    return (
        <div className="main-page page adv-methods-page">
            <section id='updating-notification' className="page-section">
                <h2 className=" long-title">Updating Notification</h2>
                <hr />
                <p>There Available methods to interact with notification after sending</p>
                <p tabIndex={0} className="paragraph">For Changing <span className="code">title</span> and <span className="code">message</span> after sending:</p>
                <CodeBlock title="Title & Message" code={data?.title_and_message_update_code || ''} />
                <p tabIndex={0} className="paragraph">For the Progress Bar: </p>
                <ul className="inner-section-2 paragraph">
                    <li>Avoid changing it value in intervals less than 0.5sec</li>
                    <li>And always pass in the new title and message if any to <span className="code">updateProgressBar</span> method</li>
                </ul>
                <span className="paragraph code yellow flex progressbar-warning">Android ignores updates faster than 0.5sec on some devices</span>
                <CodeBlock title="Progress-Bar" code={data?.progress_bar_update_code || ''} />
            </section>

            <section id='adding-image' className="page-section">
                <h2 className=" long-title">For Images:</h2>
                <hr />
                {/* <p tabIndex={0} className="paragraph">For Images:</p> */}
                <p className="paragraph">To add image after sending
                    <span> use </span>
                    <span className="code">setLargeIcon</span> or <span className="code">setBigPicture</span> then <span className="code">.refresh</span>
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
                    <li className="inner-section-2">Using this format <span className="code">.lower().replace(&apos; &apos;, &apos;_&apos;)</span> </li>
                    <li>Custom Channel Name&apos;s Gives User ability to turn on/off specific notifications</li>
                </ul>
                <CodeBlock title='Channel Management' code={data?.channel_management_code || ''} img={channelimg} />
            </section>

            <section id="getting-identifer" className="page-section" tabIndex={0}>
                <h2 className="long-title">Getting Identifer</h2>
                <hr />
                <p>If you want to get the Exact Notification Clicked to Open App, you can use NotificationHandler to get unique identifer (str) <span className="code">NotificationHandler.get_name</span></p>

                <CodeBlock title="Identifer" code={data?.getting_identifier_code || ''} />
            </section>


            <span className='flex next-page-btns-box space-between'>
                <Link className='next-page-btn' href='/components'>
                    <ChevronLeft />
                    <span>
                        <p className='next-txt'>Previous</p>
                        <p className='page-name'>Components</p>
                    </span>
                </Link>
                <Link className='next-page-btn' href='/reference'>
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
