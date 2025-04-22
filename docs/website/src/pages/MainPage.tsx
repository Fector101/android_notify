import '../assets/css/mainpage.css'
import {
    dracula
    // ,dark, xonokai,vscDarkPlus
} from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Prism } from 'react-syntax-highlighter'
import { Check, ChevronRight, Copy } from 'lucide-react';
import {
    // a11yDark, github, githubGist, 
    gradientDark
} from 'react-syntax-highlighter/dist/esm/styles/hljs';
// import { vsDark } from 'react-syntax-highlighter/dist/cjs/styles/prism';
// import { Prism as Prism } from 'react-syntax-highlighter';
import { useState, useEffect } from 'react';
import { Link } from 'react-router'
import { copyText } from '../assets/js/helper';
import { code, installation_code_buildozer, installation_code_pip } from './data/mainpage';
import { ScrollToSection } from '../ScrollAssist';

export default function MainPage() {
    let style = gradientDark
    style = dracula



    const [fontSize, setFontSize] = useState<string>(getFontSize());

    function getFontSize(): string {
      return window.innerWidth < 500 ? '13px' : '16px';
    }
  
    useEffect(() => {
      const handleResize = () => setFontSize(getFontSize());
  
      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }, []);





    function copyAction(txt: string, e: React.MouseEvent<HTMLButtonElement, MouseEvent>) {
        let element = e.target as HTMLElement | null| undefined
        element=element?.closest('button')
        console.log(element)
        
        element?.querySelector('.copy-icon')?.classList.add('display-none')
        element?.querySelector('.check-icon')?.classList.remove('display-none')
        // setTimeout(() => {
        //     element?.querySelector('.copy-icon')?.classList.remove('display-none')
        //     element?.querySelector('.check-icon')?.classList.add('display-none')
        // },500)
        copyText(txt)

    }

    // const [sudoku_list, setSudokuList] = useState<(number | '')[][]>()
    // const [sudoku_puzzle, setSudokuPuzzle] = useState<(number | '')[][]>()

    // const [input_value,setInputValue] = useState(1)

    // useEffect(() => {
    // }, [])
    return (
        <div className="page main-page flex fd-column">
            <ScrollToSection/>
            <section id='introduction'>
                <h2>Introduction</h2>
                <hr />
                <p className='reader'>Android-Notify simplifies the process of creating and managing android notifications with <span className='code green'>Python</span>.</p>

                <p className='paragraph reader'>It built using pyjnius to interact with Android's native Java Classes and APIs.</p>
                <p className='paragraph'>The goal is handling all the Java for you -- letting you focus on your notification content with `Python` rather than the platform's implementation details
                    and eliminate the use of third-party services where not required.
                </p>
                <p className='paragraph'>Android-Notify has two dependencies: Kivy, Pyjnius</p>
            </section>

            <section id='features'>
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

            <section id='installation'>

                <h2>Installation</h2>
                <hr />
                <div className='inner-section-1'>
                    <h3 className='sub-header'>Buildozer</h3>
                    <p>In your `buildozer.spec` file include the following:</p>
                    <div className='code-block'>
                        <button onClick={(e) => copyAction(installation_code_buildozer, e)}>
                            <Copy className='copy-icon' />
                            <Check className='check-icon display-none' />
                        </button>
                        <Prism language="ini" style={style} customStyle={{ fontSize: fontSize }}>
                            {installation_code_buildozer}
                        </Prism>
                    </div>
                    <h3 className='sub-header'>PIP</h3>
                    <p className='paragraph'>You Can also install Via PIP for testing purposes</p>
                    <div className='code-block'>
                        <button onClick={(e) => copyAction(installation_code_pip, e)}>
                            <Copy className='copy-icon' />
                            <Check className='check-icon display-none' />
                        </button>
                        <Prism language="bash" style={style} customStyle={{ fontSize: fontSize }}>
                            {installation_code_pip}
                        </Prism>

                    </div>
                </div>
            </section>


            <section id='basic-usage'>

                <h2>Basic Usage</h2>
                <hr />
                <div className='inner-section-1'>
                    <p>You can easily create and send notifications with just a few lines of code.</p>
                    <p>Below is a simple example of how to create a basic notification:</p>
                    <div className='code-block'>
                        <button onClick={(e) => copyAction(code, e)}>
                            <Copy className='copy-icon' />
                            <Check className='check-icon display-none' />
                        </button>
                        <Prism language="python" style={style}  customStyle={{ fontSize: fontSize }}>
                            {code}
                        </Prism>
                    </div>

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
