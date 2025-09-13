import React, { useEffect, useState } from 'react';
import Link from 'next/link'
import "./footer.css"
/**
 * Footer component for the documentation website.
 * Displays last updated date and links to support the project.
 *
 * @returns {JSX.Element} The footer element.
 */
export default function Footer() {
    const [date, setDate] = useState('');

    useEffect(() => {
        fetch('/last-updated.txt')
            .then(res => res.text())
            .then(text => setDate(text));
console.log(date)
    }, []);
    return (
        <footer className='flex justify-content-cen text-align-center align-items-cen'>
            {/* <h2 className='footer-title'>Laner Documentation</h2>
            <p className='footer-subtitle'>A comprehensive guide to using Laner</p> */}
            {/* <p>Made with ❤️ using <Link href='https://react.dev/'>React</Link> and <Link href='https://vitejs.dev/'>Vite</Link></p> */}
            {/* <p>Documentation hosted on <Link href='https://vercel.com/'>Vercel</Link></p> */}
            <div className="flex fd-column gap-10">
                <p>Thoroughly Tested and supported by <Link href='https://github.com/Fector101/laner'>Laner</Link> </p>
                <p>Last Updated: 13th Sep, © {new Date().getFullYear()} Fabian</p>
            </div>

            <div className='support-links-box flex fd-column justify-content-cen text-align-center'>
                <p>Find this project helpful?</p>
                <p> consider buying me a <Link href='https://www.buymeacoffee.com/fector101' className="buy-me-a-coffee">Coffee ☕️</Link></p>
                <p> Or a star on 🌟 <Link href='https://github.com/Fector101/android_notify'>GitHub.</Link></p>
                <p>Your support helps maintain and improve the project.</p>
            </div>

        </footer>
    )
}