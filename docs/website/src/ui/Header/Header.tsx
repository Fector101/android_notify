import {
    Bell, Github, Menu,
    X
    // Sun
} from 'lucide-react'
import './header.css'
import { Link, useLocation } from 'react-router'
// import { useState } from 'react'
import { toTitleCase } from '../../assets/js/helper';
import pages_dict from '../../pages/versions-data/general';
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
    const [isOpen, setIsOpen] = useState(() => !isMobileView.current)
    const [oldSideWidth, setOldSideBarWidth] = useState(300)

    function toggleSideBar() {
        const side_bar_ele = document.getElementById('site-overview')
        const main_page = document.getElementsByClassName('main-page')?.[0] as HTMLElement
        if (side_bar_ele) {
            // side_bar_ele.style.transform = `translateX(-${isMobileView.current ? 0 : 100}%)`
            if(isOpen){
                setOldSideBarWidth(side_bar_ele.getBoundingClientRect().width)
                side_bar_ele.style.width = '0'
                side_bar_ele.style.minWidth = '0'
            }else{
                side_bar_ele.style.width =  oldSideWidth+'px'
                side_bar_ele.style.minWidth = oldSideWidth+'px'
            }
            // side_bar_ele.style.width = 0

        } if (main_page) {
            // main_page.classList.toggle('page-toggler')
        }
        isMobileView.current = !isMobileView.current
        setIsOpen(state => !state)
    }

    return (
        <header className='flex align-items-cen width100per'>
            <Link to='/getting-started'>
                <Bell className='brand' />
            </Link>
            <Link to='/versions' className='version-no'>v1.58</Link>
            <p className='page-title'>{location.pathname.slice(1).split('-').map(toTitleCase).join(' ')}{description || ''}</p>
            {/* <input value={search} onChange={(e)=>setSearch(e.target.value)}/> */}
            <nav className="flex margin-left-auto icon-nav">
                <Link target='_blank' rel='noopener noreferrer' className='btn-link' to="https://github.com/Fector101/android_notify"> <Github /> </Link>
                <button onClick={toggleSideBar} className='btn-link menu-btn'>
                    {isOpen ? <X /> : <Menu />}
                </button>
                {/* <button> <MoonIcon /> </button> */}
            </nav>
        </header>
    )
}