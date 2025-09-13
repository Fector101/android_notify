"use client"
import {  ChevronRight } from 'lucide-react';
import Link from 'next/link'
import dynamic from 'next/dynamic'
import '../../assets/css/mainpage.css'
import { mainpage } from '../../versions-data';

const CodeBlock = dynamic(() => import('../../ui/CodeBlock/CodeBlock').then(mod => mod.CodeBlock), { ssr: false });

export default function MainPage() {
    return (
        <div className="page main-page flex fd-column">
            <section className="page-section" id='introduction'>
                <h2>Introduction</h2>
                <hr />
                <p className='reader'>Android-Notify simplifies the process of creating and managing android notifications with <span className='code green'>Python</span>.</p>

                <p className='paragraph reader'>It&apos;s built using pyjnius to interact with Android&apos;s native Java Classes and APIs.</p>
                <p className='paragraph'>
The goal of android-notify is to handle all the Java for you, allowing you to focus on your notification content using Python, without worrying about platform-specific implementation details. It also eliminates the need for unnecessary third-party APIs or online services.
                </p>
                <p className='paragraph'>Android-Notify has two dependencies: Kivy, Pyjnius</p>
            </section>

            <section className="page-section" id='features'>
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
            </section>

            <section className="page-section" id='installation'>
                <h2>Installation</h2>
                <hr />
                <div className='inner-section-1'>
                    <h3 className='sub-header'>Buildozer</h3>
                    <p>In your `buildozer.spec` file include the following:</p>
                    <CodeBlock code={mainpage.installation_code_buildozer} lang='ini' />
                    <h3 className='sub-header'>PIP</h3>
                    <p className='paragraph'>You Can also install Via PIP for testing purposes</p>
                    <CodeBlock code={mainpage.installation_code_pip} lang='bash' />

                </div>
            </section>


            <section className="page-section" id='basic-usage'>

                <h2>Basic Usage</h2>
                <hr />
                <div className='inner-section-1'>
                    <p>You can easily create and send notifications with just a few lines of code.</p>
                    <p>Below is a simple example of how to create a basic notification:</p>
                    <CodeBlock code={mainpage.code} />


                </div>
            </section>

            <Link className='next-page-btn' href='/components'>
                <span>
                    <p className='next-txt'>Next</p>
                    <p className='page-name'>Components</p>
                </span>
                <ChevronRight />
            </Link>

        </div>
    )
}
