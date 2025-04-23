import {
    Bell, Github, Menu,
    X
    // Sun
} from 'lucide-react'
import './header.css'
import { Link, useLocation } from 'react-router'
// import { useState } from 'react'
import { toTitleCase } from '../../assets/js/helper';
import pages_dict from '../../pages/data/general';
import { useRef, useState } from 'react';

// type PagesDict = {
//     [key: string]: { title: string; description: string } | undefined;
// };

// const typedPagesDict: PagesDict = pages_dict;


export default function Header() {
    // const [search,setSearch]=useState('')
    const location = useLocation();
    let description = pages_dict[location.pathname.slice(1)]?.description || '';
    description = description ? ' - ' + description : '';
    const isMobileView = useRef(window.innerWidth < 770)
    const [isOpen,setIsOpen] =useState(()=>!isMobileView.current)

    function toggleSideBar() {
        const side_bar_ele = document.getElementById('site-overview')
        const main_page = document.getElementsByClassName('main-page')?.[0] as HTMLElement
        
        if (side_bar_ele && main_page) {
            side_bar_ele.style.transform = `translateX(-${isMobileView.current ? 0 : 100}%)`
            // main_page.style.margin='0 auto'
            main_page.classList.toggle('page-toggler')
            isMobileView.current = !isMobileView.current
            setIsOpen(state=>!state)
        }
    }


    return (
        <header className='flex align-items-cen width100per'>
            <Link to='/'>
                <Bell className='brand' />
            </Link>
            <Link to='/versions' className='version-no'>v1.58</Link>
            <p className='page-title'>{location.pathname.slice(1).split('-').map(toTitleCase).join(' ')}{description || ''}</p>
            {/* <input value={search} onChange={(e)=>setSearch(e.target.value)}/> */}
            <nav className="flex margin-left-auto icon-nav">
                <Link className='btn-link' to="https://github.com/Fector101/android_notify"> <Github /> </Link>
                <button onClick={toggleSideBar} className='btn-link menu-btn'>
                    {isOpen?<X/>:<Menu />}
                </button>
                {/* <button> <MoonIcon /> </button> */}
            </nav>
        </header>
    )
}