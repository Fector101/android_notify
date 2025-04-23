import { CodeBlock } from "../ui/CodeBlock/CodeBlock";
import { ScrollToSection } from "../ScrollAssist";
import '../assets/css/advmethodspage.css'
import { adding_image_code, progress_bar_update, title_and_message_update } from "./data/advmethodspage";

export default function AdvancedMethodsPage() {
    return (
        <div className="main-page page adv-methods-page">
            <ScrollToSection />
            <h2 className="page-title long-title">Updating Notification</h2>
            <section id='updating-notification'>

                <hr />
                <p>There Available methods to interact with notification after sending</p>
                <p className="paragraph">For Changing <span className="code">title</span> and <span className="code">message</span> after sending:</p>
                <CodeBlock title="Title & Message" code={title_and_message_update} />
                <p className="paragraph">For the Progress Bar: </p>
                <ul className="inner-section-2 paragraph">
                    <li>Avoid changing it value in intervals less than 0.5sec</li>
                    <li>And always pass in the new title and message if any to <span className="code">updateProgressBar</span> method</li>
                </ul>
                <span className="paragraph code yellow flex progressbar-warning">Android ignores updates faster than 0.5sec on some devices</span>
                <CodeBlock title="Progress-Bar" code={progress_bar_update} />
                <p className="paragraph">For Images:</p>
                <p className="paragraph">To add image after sending set <span className="code">already_sent</span> in <span className="code">addNotificationStyle</span> method to <span className="code">true</span></p>
                <CodeBlock title="Image" code={adding_image_code}/>
                {/* <Compo */}
                {/* <h3 className="page-subtitle">Updating Notification</h3>
            <p className="page-text"> You can update a notification after it has been created by using the <code>update</code> method. This method takes an object with the same properties as the original notification, and updates the notification with the new values.</p> */}

            </section>
        </div>
    )
}