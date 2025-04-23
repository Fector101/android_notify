import { CodeBlock } from "../ui/CodeBlock/CodeBlock";
import { ScrollToSection } from "../ScrollAssist";
import '../assets/css/advmethodspage.css'
import { adding_image_code, channel_management_code, getting_identifer, progress_bar_update, title_and_message_update } from "./data/advmethodspage";
import channelimg from '../assets/imgs/channelname.jpg'

export default function AdvancedMethodsPage() {
    return (
        <div className="main-page page adv-methods-page">
            <ScrollToSection />
            <h2 className=" long-title">Updating Notification</h2>
            <section id='updating-notification' className="page-section">

                <hr />
                <p>There Available methods to interact with notification after sending</p>
                <p tabIndex={0} className="paragraph">For Changing <span className="code">title</span> and <span className="code">message</span> after sending:</p>
                <CodeBlock title="Title & Message" code={title_and_message_update} />
                <p tabIndex={0} className="paragraph">For the Progress Bar: </p>
                <ul className="inner-section-2 paragraph">
                    <li>Avoid changing it value in intervals less than 0.5sec</li>
                    <li>And always pass in the new title and message if any to <span className="code">updateProgressBar</span> method</li>
                </ul>
                <span className="paragraph code yellow flex progressbar-warning">Android ignores updates faster than 0.5sec on some devices</span>
                <CodeBlock title="Progress-Bar" code={progress_bar_update} />
                <p tabIndex={0} className="paragraph">For Images:</p>
                <p className="paragraph">To add image after sending set <span className="code">already_sent</span> in <span className="code">addNotificationStyle</span> method to <span className="code">true</span></p>
                <CodeBlock title="Image" code={adding_image_code} />
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
                    <li>In later versions </li>
                </ul>
                <CodeBlock title='Channel Management' code={channel_management_code} img={channelimg} />
            </section>
            <section id="getting-identifer" className="page-section" tabIndex={0}>
                <h2 className="long-title">Getting Identifer</h2>
                <hr />
                <p>If you want to get the Exact Notification Clicked to Open App, you can use NotificationHandler to get unique identifer (str) <span className="code">NotificationHandler.getIdentifer</span></p>
                
                <p>
                    <span className="code warning yellow paragraph block width-max-con">In next version identifer will be changed to id, it'll also be used to reference instance</span>
                </p>
                <CodeBlock title="Identifer" code={getting_identifer} />
            </section>
            {/* <Compo */}
            {/* <h3 className="page-subtitle">Updating Notification</h3>
            <p className="page-text"> You can update a notification after it has been created by using the <code>update</code> method. This method takes an object with the same properties as the original notification, and updates the notification with the new values.</p> */}

        </div>
    )
}