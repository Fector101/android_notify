import { useEffect, useState } from 'react';
import {
    dracula
} from 'react-syntax-highlighter/dist/esm/styles/prism';
// import {
//     gradientDark
// } from 'react-syntax-highlighter/dist/esm/styles/hljs';
// import { code } from "./data/mainpage";
import { Prism } from 'react-syntax-highlighter'
import { ScrollToSection } from '../ScrollAssist';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Link } from 'react-router'
import './../assets/css/componentspage.css'
import bigPicImg from './../assets/imgs/bigpicturenoti.jpg'
import btnsImg from './../assets/imgs/btns.jpg'
import progressbarImg from './../assets/imgs/progress.jpg'
import largeIconImg from './../assets/imgs/largeicon.jpg'
import inboxImg from '../assets/imgs/inboxnoti.jpg'
import { bigimgcode, bigtextcode, buttons_code, inboxcode, largeiconcode, progressbarcode } from './data/componentspage';


function ComponentPreview({ title, img, code }: { title: string, img: string, code: string }) {

    const [fontSize, setFontSize] = useState<string>(getFontSize());

    function getFontSize(): string {
        return window.innerWidth < 500 ? '13px' : '16px';
    }

    useEffect(() => {
        const handleResize = () => setFontSize(getFontSize());

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);


    return (
        <div className='component-preview flex fd-column'>
            <div className="header">
                <h3>{title}</h3>
            </div>
            <div className='flex content'>

                <Prism language="python" style={dracula} customStyle={{ margin: 0, padding: '20px', borderRadius: 0, fontSize: fontSize, overflowX: 'auto' }}>
                    {code}
                </Prism>
                <img src={img} />
            </div>
        </div>

    )
}


export default function ComponentsPage() {
    // const style = dracula
    return (
        <div className="page main-page components-page">
            <ScrollToSection />
            <section id="images">
                <h2>Images</h2>
                <hr />
                <div className="inner-section-1">
                    <p>You can enhance your notifications by adding images, Images can be local or online</p>
                    <p className='paragraph'>For Local Images:
                        <ul>
                            <li>Images should be in the <span className="code">apps</span> folder</li>
                        </ul>
                    </p>

                    <p className='paragraph'>For Online Images:
                        <ul>
                            <li>you'll have to specify this requirement in your <span className="code">buildozer.spec</span> file:<br /><span className="code">android.permissions = INTERNET</span></li>
                            <li>Paths should start with <span className="code">http://</span> or <span className="code">https://</span> </li>
                        </ul>
                    </p>
                    <br />

                    <p>
                        You can display:
                    </p>
                    <ul>
                        <li>A large image (Big Picture Style)</li>
                        <li>A small image (Large Icon Style)</li>
                        <li>Both large and small images together</li>
                        <li>Custom notification icons (override the default app icon)</li>
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
                    <div>
                        <ComponentPreview title='Big Picture Style' img={bigPicImg} code={bigimgcode} />
                        <ComponentPreview title='Large Icon Style' img={largeIconImg} code={largeiconcode} />
                        <h3 className='paragraph'>Changing Default Notification Icon</h3>
                        <p className='paragraph'>When you initailze Notification instance you can pass in file path to <span className="code">app_icon</span> </p>
                        <p className='paragraph'>Must use <span className="code yellow"> PNG format</span> Or Image Will display as a Black Box</p>
                        <ComponentPreview title='Large Icon Style' img={largeIconImg} code={largeiconcode} />

                    </div>
                </div>
            </section>

            <section id="buttons">
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
                <ComponentPreview title='Button Example' img={btnsImg} code={buttons_code} />
                <p className='paragraph inner-section-1'>For more on functions and callbacks check out the <Link to='/advanced#functions'>Advanced</Link> section</p>
            </section>


            <section id="progress-bars">
                <h2>Progress Bars</h2>
                <hr />
                <div className="inner-section-1">
                    <p>
                        Also supports notifications with progress indicators — useful for showing download status, task completion.
                    </p>
                    <ul>
                        <li>Update progress in real-time with <code>updateProgressBar()</code></li>
                        <li>Show an infinite progress animation with <code>showInfiniteProgressBar()</code></li>
                        <li>Cleanly remove the progress bar with <code>removeProgressBar()</code></li>
                    </ul>
                    <p>
                        You can customize the displayed message and title while the progress bar updates.
                    </p>
                </div>
                <ComponentPreview title='Progress Bar Style' img={progressbarImg} code={progressbarcode} />
            </section>


            <section id="texts">
                <h2>Texts</h2>
                <hr />
                <h3>Multi-Line Text </h3>
                <div className="paragraph inner-section-1">
                    <p>
                        Simply Adds new line where <span className='code'>\n</span> is signified in message. [will auto detect in other versions]
                    </p>
                    {/* <ul>
                        <li>Use <code>\\n</code> to add new lines in the message</li>
                        <li>Use <code>\\t</code> to add tabs in the message</li>
                        <li>Use <code>\\r</code> to add carriage returns in the message</li>
                        </ul> */}
                </div>
                <ComponentPreview title='Inbox Style' img={inboxImg} code={inboxcode} />
                <h3 className='paragraph'>Big Text Style</h3>
                <p className='paragraph'>When using big_text style <span className="code">message</span> acts as sub-title, Then when notification drop down button is pressed <span className="code">body</span> is revealed</p>
                <ComponentPreview title='Big Text Style' code={bigtextcode} img='' />
            </section>

            <span className='flex next-page-btns-box space-between'>
                <Link className='next-page-btn' to='/getting-started'>
                    <ChevronLeft />
                    <span>
                        <p className='next-txt'>Previous</p>
                        <p className='page-name'>Getting Started</p>
                    </span>
                </Link>
                <Link className='next-page-btn' to='/event-handling'>
                    <span>
                        <p className='next-txt'>Next</p>
                        <p className='page-name'>Event Handling</p>
                    </span>
                    <ChevronRight />
                </Link>

            </span>

        </div>
    )
}