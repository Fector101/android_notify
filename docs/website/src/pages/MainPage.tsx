import { ChevronRight } from 'lucide-react';
import { Link } from 'react-router'
import { ScrollToSection } from '../ui/ScrollAssist';
import { CodeBlock } from '../ui/CodeBlock/CodeBlock';
import '../assets/css/mainpage.css'
import { code, installation_code_buildozer, installation_code_pip } from './versions-data/mainpage';

export default function MainPage() {

    return (
        <div className="page main-page flex fd-column">
            <ScrollToSection />
            <section className="page-section" id="introduction">
                <h2>Introduction</h2>
                <hr />
                <p className="reader">
                    Android-Notify makes creating and managing Android notifications easy with <span className="code green">Python</span>.
                </p>
                <p className="paragraph reader">
                    Built with Pyjnius, it interacts directly with Android’s Java APIs.
                </p>
                <p className="paragraph">
                    It handles all Java details so you can focus on notification content in Python, No extra APIs or services needed.
                </p>
                <p className="paragraph">Dependencies: Kivy, Pyjnius, Flet</p>
            </section>
            <section className="page-section" id="features">
                <h2>Features</h2>
                <hr />

                <ul className="inner-section-1 space-y-[20px]">

                    <li><strong>Notification Styles:</strong></li>

                    <ul className='space-y-[20px]'>
                        <ul>
                            <li>Texts (<a href="/components#texts" target="_blank" rel="noopener noreferrer">texts section </a>)</li>
                            <li>Simple text</li>
                            <li>Big text</li>
                            <li>Inbox-style</li>
                            <li>and Colored texts.</li>
                        </ul>

                        <ul>
                            <li>Images
                                (<a href="/components#images" target="_blank" rel="noopener noreferrer">images section </a>)
                            </li>
                            <li>Large icon</li>
                            <li>Big picture</li>
                            <li>Custom app icons</li>
                            <li>Colored app icons</li>
                        </ul>

                        <ul>
                            <li>Progress bar (<a href="/components#progress-bars" target="_blank" rel="noopener noreferrer">
                                progress bars section</a>)
                            </li>
                            <li> Determinate</li>
                            <li> Indeterminate</li>
                        </ul>

                        <ul>
                            <li>Buttons (<a href="/components#buttons" target="_blank" rel="noopener noreferrer">
                                buttons section</a>)
                            </li>
                            <li> Runtime Functions</li>
                            <li> Broadcast Actions</li>
                            
                        </ul>

                    </ul>

                    <li><strong>Behaviours/ Runtime Functions:</strong></li>
                    <ul>

                        <li>Send: normal/silent/persistent/vibrate</li>
                        <li>Update: title, message, images, progress bar</li>
                        <li>Add or Remove Buttons</li>
                        <li>Custom sound per notification</li>

                    </ul>
                    
                    <li><strong>Utilities:</strong></li>
                    <ul>

                        <li>Set timestamp</li>
                        <li>Clear single or all notifications</li>
                        <li>Refrshing notifications setting new param</li>

                    </ul>
                    

                    <li><strong>Channels </strong>
                    (<a href="https://android-notify.vercel.app/advanced-methods#channel-management" target="_blank" rel="noopener noreferrer">Android 8.0+</a>):
                    </li>
                    <ul>
                        <li>Create, delete, delete all</li>
                        <li>Set importance, vibration, and sound</li>
                    </ul>
                    
                    <li><strong>Permissions & Click Handling:</strong></li>
                    <ul>
                        <li>Ask / check notification permission</li>
                        <li>Click handlers and opening app on notification click</li>
                    </ul>

                </ul>

            </section>



            {/* <section className="page-section" id='features'>
                <h2>Features</h2>
                <hr />
                <ul className='inner-section-1'>
                    <li>Permission request for notifications</li>
                    <li>Allows notification to have a callback function Onclick</li>
                    <li>Supports Images, adding Buttons and Progress-Bar</li>
                    <li>Changing default notification icon</li>
                    <li>Persisting on notification tray </li>
                    <li>Customizable notification channels</li>
                    <li>Opening app on notification click</li>
                </ul>
                <p className='paragraph inner-section-1'>And Many More...</p>
            </section> */}

            <section className="page-section" id='installation'>
                <h2>Installation</h2>
                <hr />
                <div className='inner-section-1'>
                    <h3 className='sub-header'>Buildozer</h3>
                    <p>In your `buildozer.spec` file include the following:</p>
                    <CodeBlock code={installation_code_buildozer} lang='ini' />
                    <h3 className='sub-header'>PIP</h3>
                    <p className='paragraph'>You Can also install Via PIP for testing purposes</p>
                    <CodeBlock code={installation_code_pip} lang='bash' />

                </div>
            </section>


            <section className="page-section" id='basic-usage'>

                <h2>Basic Usage</h2>
                <hr />
                <div className='inner-section-1'>
                    <p>You can easily create and send notifications with just a few lines of code.</p>
                    <p>Below is a simple example of how to create a basic notification:</p>
                    <CodeBlock code={code} />


                </div>
            </section>

            <Link className='next-page-btn' to='/components'>
                <span>
                    <p className='next-txt'>Next</p>
                    <p className='page-name'>Components</p>
                </span>
                <ChevronRight />
            </Link>

        </div>
    )
}
