import { useEffect, useState } from 'react';
import { Link } from 'react-router'
import "./footer.css"
/**
 * Footer component for the documentation website.
 * Displays last updated date and links to support the project.
 *
 * @returns {JSX.Element} The footer element.
 */
export default function Footer(): JSX.Element {
    const [date, setDate] = useState('');

    useEffect(() => {
      fetch('/last-updated.txt')
        .then(res => res.text())
        .then(text => setDate(new Date(text).toLocaleString()));
    }, []);
    return (
        <footer className='flex fd-column justify-content-cen text-align-center footer'>
            {/* <h2 className='footer-title'>Laner Documentation</h2>
            <p className='footer-subtitle'>A comprehensive guide to using Laner</p> */}
            {/* <p>Made with ❤️ using <Link to='https://react.dev/'>React</Link> and <Link to='https://vitejs.dev/'>Vite</Link></p> */}
            {/* <p>Documentation hosted on <Link to='https://vercel.com/'>Vercel</Link></p> */}

            <p>Thoroughly Tested and supported by <Link to='https://github.com/Fector101/laner'>Laner</Link> </p>
            <div className='support-links-box flex fd-column justify-content-cen text-align-center'>
            <p>Find this project helpful?</p>
            <p> consider buying me a <Link to='https://www.buymeacoffee.com/fector101' className="buy-me-a-coffee">Coffee ☕️</Link></p>
            <p> Or a star on 🌟<Link to='https://github.com/Fector101/android_notify'>GitHub.</Link></p>
            <p>Your support helps maintain and improve the project.</p>
            </div>
            <p>Last Updated: {date}, © 2023 Fector101</p>
        </footer>
    )
}