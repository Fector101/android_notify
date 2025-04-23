import { Link } from 'react-router'
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { ScrollToSection } from '../ui/ScrollAssist'

export default function ExtrasPage() {
    return (
        <div className="page main-page">
            <ScrollToSection />
            <section className="page-section" id="debugging-tips">
                <h2>Debugging Tips</h2>
                <hr />
                <ul className="inner-section-2">
                    <li> Enable logs during development: Notification.logs = True </li>
                    <li>Check channel creation with Android's notification settings </li>
                    <li> Verify image paths before sending notifications </li>
                </ul>

            </section>
            <section className="screen-height200px page-section flex fd-column justify-content-cen" id="contributing-issues">
                <h2>Contribution || Reporting Issues</h2>
                <hr />
                <p>Feel free to submit pull requests for improvements! on <Link to='https://github.com/Fector101/android_notify'>Github</Link></p>
                <p>Or Found a bug? Please open an issue on our GitHub Issues page.</p>
            </section>

            <section id='credits' className='page-section screen-height200px flex fd-column justify-content-cen'>
                <h2>Credits</h2>
                <hr />
                <ul className='inner-section-2'>
                    <li>Name: Fabian - fector101@yahoo.com</li>
                    <li>GitHub: <Link to='https://github.com/Fector101/android_notify'>Android Notify Repo</Link></li>
                    <li>Twitter: <Link to='https://twitter.com/intent/user?user_id=1246911115319263233'>FabianDev_</Link></li>
                </ul>
                {/* <p className='paragraph'>For feedback or contributions, feel free to reach out!</p> */}
                <p className='paragraph'>This Project was thoroughly Tested by the <Link to='https://github.com/Fector101/Laner'>Laner</Link> Project - A application for Securely Transfering Files Wirelessly between your PC and Phone.</p>
                <p>Special thanks to the Kivy and Pyjnius communities for their support and contributions.</p>
            </section>
            <section id='support-project' className='page-section screen-height200px flex fd-column justify-content-cen'>

                <h2>☕ Support</h2>
                <hr />
                <p>If you find this project helpful, consider buying me a <Link to="https://www.buymeacoffee.com/fector101">coffee!</Link> 😊 Or Giving it a star on 🌟 <Link to='https://github.com/Fector101/android_notify'>GitHub.</Link></p>
                <p>Your support helps maintain and improve the project.</p>

            </section>
            {/* Remember to check Android's notification documentation for best practices and guidelines regarding notification frequency and content. */}
            <span className='flex next-page-btns-box space-between'>
                <Link className='next-page-btn' to='/reference'>
                    <ChevronLeft />
                    <span>
                        <p className='next-txt'>Previous</p>
                        <p className='page-name'>Reference</p>
                    </span>
                </Link>
                <Link className='next-page-btn' to='/getting-Zstarted'>
                    {/* <Link className='next-page-btn' to='/event-handling'> */}
                    <span>
                        <p className='next-txt'>Next</p>
                        <p className='page-name'>Getting Started</p>
                        {/* <p className='page-name'>Event Handling</p> */}
                    </span>
                    <ChevronRight />
                </Link>

            </span>

        </div>
    )
}