import { ChevronRight } from 'lucide-react';
import { Link } from 'react-router'
import { ScrollToSection } from '../ui/ScrollAssist';
import { CodeBlock, InlineCode } from '../ui/CodeBlock/CodeBlock';
import '../assets/css/mainpage.css'
import { code, installation_code_buildozer, installation_code_pip, installation_code_flet, installation_code_buildozer_without_androidx } from './versions-data/mainpage';

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
                <p className="paragraph">Dependencies: Kivy, Pyjnius</p>
            </section>

            <section className="page-section" id="features">
                <h2>Features</h2>
                <hr />

                <ul className="inner-section-1 space-y-[20px]">

                    <details>
                        <summary><strong>Notification Components&Design:</strong></summary>

                        <ul className='space-y-[20px] mt-[10px]'>
                            <ul>
                                <li>Texts (<a href="/components#texts" target="_blank" rel="noopener noreferrer">texts section </a>)</li>
                                <li>Simple text</li>
                                <li>Big text</li>
                                <li>Inbox-style</li>
                                <li>Sub Texts</li>
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
                    </details>
                    <details>

                        <summary><strong>Behaviours/ Runtime Functions:</strong></summary>

                        <ul className='space-y-[10px] mt-[10px]'>
                            <li>Send: normal/silent/persistent/vibrate</li>
                            <li>Update: title, message, images, progress bar</li>
                            <li>Add or Remove Buttons</li>
                            <li>Click handlers and opening app on notification click</li>
                            <li>Custom sound per and vibrate notification</li>
                            <li>Set timestamps</li>
                            <li>Clear single or all notifications</li>

                        </ul>
                    </details>

                    <details>
                        <summary><strong>Channels for </strong>(<a href="https://android-notify.vercel.app/advanced-methods#channel-management" target="_blank" rel="noopener noreferrer">Android 8.0+</a>):</summary>
                        <ul className='space-y-[10px] mt-[10px]'>
                            <li>Create, delete, delete all</li>
                            <li>Set importance, vibration, and sound</li>
                        </ul>
                    </details>

                    <details>
                        <summary><strong>Permissions:</strong></summary>
                        <ul className='space-y-[10px] mt-[10px]'>
                            <li>Ask / check notification permission with callback</li>
                        </ul>
                    </details>


                </ul>

            </section>

            <section className="page-section" id='installation'>
                <h2>Installation</h2>
                <hr />
                <h3 className='my-[20px]'>- With Androidx:</h3>
                <h4 className='ml-[20px]'>Recommended for Newer devices</h4>

                <div className='inner-section-1'>
                    <h3 className='sub-header'>Kivy Apps</h3>
                    <p>In your `buildozer.spec` file include the following:</p>
                    <CodeBlock code={installation_code_buildozer} lang='ini' />

                    <h3 className='my-[20px]'>- Without Androidx:</h3>
                    <p className='my-[20px]'> easy usage without gradle dependencies,
                        android-notify uses android legacy implementations.(Tested up to Android 15)</p>

                    <h3 className='sub-header'>Flet Apps</h3>

                    <p>In your `pyproject.toml` include the following:</p>

                    <CodeBlock code={installation_code_flet} lang='toml' />
                    <h3 className='sub-header'>Kivy Apps</h3>
                    <p className='my-[20px]'>In your `buildozer.spec` include the following:</p>
                    <CodeBlock code={installation_code_buildozer_without_androidx} lang='ini' />

                    <h3 className='sub-header'>Pydroid 3 App</h3>
                    <p className='paragraph'>In pip section where you're asked to insert libary name paste <InlineCode code='android-notify==1.60.10.dev0' /> </p>

                    <h3 className='sub-header'>PIP</h3>
                    <p className='paragraph'>You Can also install Via PIP for IDE IntelliSense and testing purposes</p>
                    <CodeBlock code={installation_code_pip} lang='bash' />

                </div>
            </section>


            <section className="page-section" id='basic-usage'>

                <h2>Basic Usage</h2>
                <hr />
                <div className='inner-section-1'>
                    <p>You can easily create and send notifications with just a few lines of code.</p>
                    <p>Below is a simple example of how to create a basic notification:</p>
                    <CodeBlock code={code} pydroid={`# Testing with "android-notify==1.60.10.dev0" on pydroid
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from android_notify import Notification
from android_notify.core import asks_permission_if_needed


class AndroidNotifyDemoApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Button(
            text="Ask Notification Permission",
            on_release=self.request_permission
        ))
        layout.add_widget(Button(
            text="Send Notification",
            on_release=self.send_notification
        ))
        return layout

    def request_permission(self, *args):
        # Callback for NotificationHandler.asks_permission not Available on Pyroid3
        asks_permission_if_needed(legacy=True)

    def send_notification(self, *args):
        Notification(
            title="Hello from Android Notify",
            message="This is a basic notification."
        ).send()


if __name__ == "__main__":
    AndroidNotifyDemoApp().run()`} />


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
