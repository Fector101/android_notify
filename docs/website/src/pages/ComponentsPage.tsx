// import { useEffect, useState } from 'react';
// import {dracula} from 'react-syntax-highlighter/dist/esm/styles/prism';
// import {
//     gradientDark
// } from 'react-syntax-highlighter/dist/esm/styles/hljs';
// import { code } from "./data/mainpage";
// import { Prism } from 'react-syntax-highlighter'
import { ScrollToSection } from '../ui/ScrollAssist';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Link } from 'react-router'
import './../assets/css/componentspage.css'
import bigPicImg from './../assets/imgs/bigpicturenoti.jpg'
import btnsImg from './../assets/imgs/btns.jpg'
import progressbarImg from './../assets/imgs/progress.jpg'
import largeIconImg from './../assets/imgs/largeicon.jpg'
import inboxImg from '../assets/imgs/inboxnoti.jpg'
import customIconImg from "../assets/imgs/custom_icon.jpg"
import onlineBigPicImg from "../assets/imgs/online-img.jpg"
// import { appiconcode, bigimgcode, bigtextcode, buttons_code, inboxcode, largeiconcode, progressbarcode } from './versions-data/componentspage';

import { CodeBlock } from '../ui/CodeBlock/CodeBlock';
import { useEffect, useState } from 'react';
import { Iversion } from '../assets/js/mytypes';
import { isLegacyVersion } from '../assets/js/helper';


interface IComponentPage {
    big_picture_code: string;
    large_icon_code: string;
    how_to_add_both_imgs: JSX.Element;
    small_icon_code: string;
    buttons_code: string;
    progressbar_code: string;
    inbox_style_code: string;
    big_text_style_code: string
}

export default function ComponentsPage({ version }: { version: Iversion }) {
    const [data, setData] = useState<IComponentPage>()

    async function changeVersionData(version: Iversion) {

        const data = await import(`./versions-data/${version}.tsx`);
        setData(data.component_page)
        // data.default; // if exported as default
    }
    useEffect(() => {
        changeVersionData(version)
    }, [version])
    // const style = dracula
    return (
        <div className="page main-page components-page">
            <ScrollToSection />

            <section tabIndex={0} className="page-section" id="images">
                <h2>Images</h2>
                <hr />
                <div className="inner-section-1">
                    <p>You can enhance your notifications by adding images, Images can be local or online</p>
                    <p className='paragraph'>For Local Images:</p>
                    <ul>
                        <li>Images should be in the <span className="code">app</span> folder</li>
                    </ul>

                    <p className='paragraph'>For Online Images:</p>
                    <ul>
                        <li>you'll have to specify this requirement in your <span className="code">buildozer.spec</span> file:<br /><span className="code">android.permissions = INTERNET</span></li>
                        <li>Paths should start with <span className="code">http://</span> or <span className="code">https://</span> </li>
                    </ul>
                    <br />

                    <p>You can display:</p>
                    <ul>
                        <li>A large image (Big Picture Style)</li>
                        <li>A small image (Large Icon Style)</li>
                        <li>Both large and small images together</li>
                        <li>Custom notification icons (change the default app icon)</li>
                    </ul>
                    {/* <p className='paragraph'>
                        This gives you full control over how your notifications look on Android.
                    </p> */}
                    {/* <p>
                        You can use the <code>setLargeIcon()</code> method to set a large image, and the <code>setSmallIcon()</code> method to set a small image.
                        <br /><br />
                        You can also use the <code>setCustomIcon()</code> method to set a custom notification icon.
                        <br /><br />
                        The <code>setStyle()</code> method allows you to set the style of the notification.
                        <br /><br />
                        The <code>setStyle()</code> method takes a <code>style</code> parameter, which can be one of the following:
                    </p> */}
                    <CodeBlock title='Big Picture Style' img={bigPicImg} code={data?.big_picture_code || ''} />
                    <CodeBlock title='Large Icon Style' img={largeIconImg} code={data?.large_icon_code || ''} />
                    {data?.how_to_add_both_imgs || <></>}
                    {/* {data?.how_to_add_both_imgs} */}
                    {/* <p className="paragraph">For Both Images pass in <span className="code">NotificationStyles.BOTH_IMGS</span> as argument to <span className="code">style</span> and provide both paths</p> */}
                    <h3 className='app-icon-h3 sub-header'>Changing Default Notification Icon [Android 6+]</h3>
                    {isLegacyVersion(version) ?
                        <p className='paragraph'>When you initialize Notification instance you can pass in file path to <span className="code">app_icon</span> </p>
                        : <p className='paragraph'>Use <span className="code">.setSmallIcon(path)</span> to set custom notification icon</p>
                    }
                    <p className='paragraph'>Must use <span className="code yellow"> PNG format</span> Or Image Will display as a Black Box.</p>
                    <CodeBlock title='Custom Icon' img={customIconImg} code={data?.small_icon_code || ''} />
                    {
                        isLegacyVersion(version) ?
                            <CodeBlock code={`Notification(
    title="Using Online Image",
    message="Pass image URL as path to setBigImage",
    style=NotificationStyles.BIG_PICTURE,
    big_picture_path="https://www.python.org/static/img/python-logo.png")`} title='Online Image' img={onlineBigPicImg} />

                            :
                            <CodeBlock code={`Notification(
    title="Using Online Image",
    message="Pass image URL as path to setBigImage"
).setBigPicture("https://www.python.org/static/img/python-logo.png")`} title='Online Image' img={onlineBigPicImg} />

                    }
                    <p className='paragraph inner-section-1'>For about Images see <Link to='/advanced-methods#updating-notification'>advanced methods</Link> section</p>
                </div>
            </section>

            <section tabIndex={0} className="page-section" id="buttons">
                <h2>Buttons</h2>
                <hr />
                <div className="inner-section-1">
                    <p>
                        Allowing users to trigger specific Functions.
                    </p>
                    <ul className='paragraph inner-section-1'>
                        <li>Handle user clicks with the provided callback function</li>
                        <li>Add one or more buttons using <span className='code'>addButton(text, callback)</span></li>
                        <li>Easily remove buttons with <span className='code'>removeButtons()</span></li>
                    </ul>
                    <p className='paragraph'>
                        This makes your notifications more dynamic and interactive.
                    </p>
                </div>
                <CodeBlock title='Button Example' img={btnsImg} code={data?.buttons_code || ''} />
                <p className='paragraph inner-section-1'>For more on functions and callbacks see the <Link to='/advanced#functions'>Advanced</Link> section</p>
            </section>

            <section tabIndex={0} className="page-section" id="progress-bars">
                <h2>Progress Bars</h2>
                <hr />
                <div className="inner-section-1">
                    <p>
                        Notifications with progress indicators are useful for showing download status, pending actions,task completion.
                    </p>
                    <ul>
                        <li>Update progress in real-time with <span className='code'>updateProgressBar()</span></li>
                        <li>Show an infinite progress animation with <span className='code'>showInfiniteProgressBar()</span></li>
                        <li>Cleanly remove the progress bar with <span className='code'>removeProgressBar()</span></li>
                    </ul>
                    <p>
                        You can customize the displayed message and title while the progress bar updates.
                    </p>
                </div>
                <CodeBlock title='Progress Bar Style' img={progressbarImg} code={data?.progressbar_code || ''} />
            </section>


            <section tabIndex={0} className="page-section" id="texts">
                <h2>Texts</h2>
                <hr />
                <h3>Multi-Line Text </h3>
                <div className="paragraph inner-section-1">
                    <p>
                        Simply Adds new line where <span className='code'>\n</span> is signified in message, Then specify <span className="code">style='inbox'</span> [will auto detect in other versions]</p>
                    {/* <ul>
                        <li>Use <code>\\n</code> to add new lines in the message</li>
                        <li>Use <code>\\t</code> to add tabs in the message</li>
                        <li>Use <code>\\r</code> to add carriage returns in the message</li>
                        </ul> */}
                </div>
                <CodeBlock title='Inbox Style' img={inboxImg} code={data?.inbox_style_code || ''} />
                <h3 className='paragraph'>Big Text Style</h3>
                <p className='paragraph'>When using big_text style <span className="code">message</span> acts as sub-title, Then when notification drop down button is pressed <span className="code">body</span> is revealed</p>
                <CodeBlock title='Big Text Style' code={data?.big_text_style_code || ''} img='' />
            </section>

            <span className='flex next-page-btns-box space-between'>
                <Link className='next-page-btn' to='/getting-started'>
                    <ChevronLeft />
                    <span>
                        <p className='next-txt'>Previous</p>
                        <p className='page-name'>Getting Started</p>
                    </span>
                </Link>
                <Link className='next-page-btn' to='/advanced-methods'>
                    {/* <Link className='next-page-btn' to='/event-handling'> */}
                    <span>
                        <p className='next-txt'>Next</p>
                        <p className='page-name'>Advanced Methods</p>
                        {/* <p className='page-name'>Event Handling</p> */}
                    </span>
                    <ChevronRight />
                </Link>

            </span>

        </div>
    )
}