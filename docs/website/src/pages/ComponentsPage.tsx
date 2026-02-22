
import { ScrollToSection } from '../ui/ScrollAssist';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Link } from 'react-router'
import './../assets/css/componentspage.css'
import bigPicImg from './../assets/imgs/bigpicturenoti.jpg'
import btnsImg from './../assets/imgs/btns.jpg'
import largeIconImg from './../assets/imgs/largeicon.jpg'
import inboxImg from '../assets/imgs/inboxnoti.jpg'
import customIconImg from "../assets/imgs/custom_icon.jpg"
import customColorIconImg from "../assets/imgs/custom_color_icon.jpg"
import onlineBigPicImg from "../assets/imgs/online-img.jpg"
import subTextImg from "../assets/imgs/sub-text.jpg"
// import coloredTextImg from "../assets/imgs/colored-texts.jpg"
import progressbarImg from './../assets/imgs/progress.jpg'

import bigTextGif from "../assets/imgs/big_text.gif"
import inboxTextGif from "../assets/imgs/inbox_text.gif"
import progressbarGif from '../assets/imgs/progressbar.gif'

import { CodeBlock, InlineCode } from '../ui/CodeBlock/CodeBlock';
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
    sub_text_code: string
    an_colored_basic_small: string
    an_colored_basic_large: string
    colored_text_code: string
}
type set_version = React.Dispatch<React.SetStateAction<string>>

export default function ComponentsPage({ version, setVersion }: { version: Iversion, setVersion: set_version }) {
    const [data, setData] = useState<IComponentPage>()

    async function changeVersionData(version: Iversion) {
        console.log('vers0+0' + version);

        const v1 = await import(`./versions-data/1.58.tsx`);
        const v2 = await import(`./versions-data/1.59.tsx`);
        const data = await import(`./versions-data/${version}.tsx`);
        setData({ ...v1.component_page, ...v2.component_page, ...data.component_page })
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
                        <li>Image path should be in relative to your <span className="code">main.py</span> </li>
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
                        <li>Also custom app icons and custom colors</li>
                    </ul>
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

                    <p className='paragraph'>You can also set custom color for the icon to match your app theme:</p>
                    <p className='paragraph'>Use <span className="code">.setColor(color)</span> method to set a custom color</p>
                    <p className='paragraph'> You can specify the color using a hex code (e.g., "#FF0000" for red).</p>
                    <p>Strings <span className="code yellow">(red, green, blue)</span> work without hex code.</p>
                    {
                        <CodeBlock code={`from android_notify import Notification
notification = Notification(
    title="Emergency 🚨🚨",
    message="Check out now!"
)
notification.setColor("red") # or "#FF0000"
notification.send()
`} title="Coloured App Icon" img={customColorIconImg} />
                    }

                    {
                        isLegacyVersion(version) ?
                            <CodeBlock code={`from android_notify import Notification
notification = Notification(
    title="Using Online Image",
    message="Pass image URL as path to setBigImage",
    style=NotificationStyles.BIG_PICTURE,
    big_picture_path="https://www.python.org/static/img/python-logo.png")
notification.send()
`} title='Online Image' img={onlineBigPicImg} />

                            :
                            <CodeBlock code={`from android_notify import Notification
notification = Notification(
    title="Using Online Image",
    message="Pass image URL as path to setBigImage"
)
notification.setBigPicture("https://www.python.org/static/img/python-logo.png")
notification.send()`} title='Online Image' img={onlineBigPicImg} />

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
                <p className='paragraph inner-section-1'>For more on functions and callbacks see the <Link to='/advanced-methods#functions'>Advanced</Link> section</p>
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
                <CodeBlock title='Progress Bar Style' img={version == "1.58" ? progressbarImg : progressbarGif} code={data?.progressbar_code || ''} />
            </section>


            <section tabIndex={0} className="page-section" id="texts">
                <h2>Texts</h2>
                <hr />
                <h3>Multi-Line Text </h3>
                <div className="paragraph inner-section-1">
                    {
                        isLegacyVersion(version) ?
                            <>
                                <p>This feature doesn't work properly for v1.58, No way to set message and lines together. </p>
                                <p className='paragraph'>Use <span className='link-design' onClick={() => setVersion("1.59")}>v1.59.3</span> for proper implementation </p>
                            </>
                            :
                            <p>You can use <span className="code">addLine</span> and pass in each line or<br /><span className="code">setLines</span> and pass in list of strings or <br /> Pass in txt separated by <span className="code">\n</span> as arg to <span className="code">lines_txt</span> in instance</p>

                    }

                </div>
                <CodeBlock title='Inbox Style' img={isLegacyVersion(version) ? inboxImg : inboxTextGif} code={data?.inbox_style_code || ''} />

                <h3 className='paragraph'>Big Text Style</h3>
                <p className='paragraph'>When using big_text style <span className="code">message</span> acts as sub-title, Then when notification drop down button is pressed <span className="code">body</span> is revealed</p>
                {version !== "1.58" ? <p className='paragraph'>Use <span className='code'>setBigText</span> to display string</p> : ""}
                <CodeBlock title='Big Text Style' code={data?.big_text_style_code || ''} img={bigTextGif} />

                <h3 className='paragraph'>Sub Text</h3>
                <p className='paragraph'>Sub Text is a smaller text that appears side of app name, often used to provide additional context or information, Like download seconds remaining.</p>
                <p className='paragraph'>Use <span className='code'>setSubText</span> to display string</p>
                <CodeBlock title='Sub Text' code={data?.sub_text_code || '# No available in version: ' + version} img={subTextImg} />

                <h3 className='paragraph'>Colored Texts [dev]</h3>
                <ol>
                    <li className='paragraph'> Create a path named <span>res/layout</span> </li>
                    <li className='paragraph'> Copy these files using exact names


                        <details>
                            <summary><InlineCode code="an_colored_basic_small.xml" /></summary>
                            <CodeBlock code={data?.an_colored_basic_small || '# No available in version: ' + version} lang='xml' />
                        </details>
                        <details>
                            <summary><InlineCode code="an_colored_basic_large.xml" /></summary>
                            <CodeBlock code={data?.an_colored_basic_large || '# No available in version: ' + version} lang='xml' />
                        </details>
                    </li>
                    <li className='paragraph'>
                        In your `buildozer.spec` file add these:
                        <br />
                        <p >- `source.include_exts = xml` and `android.add_resources = res`
                        </p>
                    </li>

                </ol>
                <p className='paragraph'>Use params <InlineCode code='title_color' /> and/or <InlineCode code='message_color' /> with hex color codes to control colors.</p>
                <CodeBlock title='Colored Texts' code={data?.colored_text_code || '# No available in version: ' + version} />

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
