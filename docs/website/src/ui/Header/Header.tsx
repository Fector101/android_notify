import { Bell, Github, Sun } from 'lucide-react'
import './header.css'
import { Link, useLocation } from 'react-router'
// import { useState } from 'react'
import { toTitleCase } from '../../assets/js/helper';
import pages_dict from '../../pages/data/general';

// type PagesDict = {
//     [key: string]: { title: string; description: string } | undefined;
// };

// const typedPagesDict: PagesDict = pages_dict;


export default function Header() {
    // const [search,setSearch]=useState('')
    const location = useLocation();
    let description = pages_dict[location.pathname.slice(1)]?.description || '';
    description = description? ' - ' + description : '';
    return (
        <header className='flex align-items-cen width100per'>
            <Bell className='brand' />
            <Link to='/versions' className='version-no'>v1.58</Link>
            <p className='page-title'>{location.pathname.slice(1).split('-').map(toTitleCase).join(' ')}{description || ''}</p>
            {/* <input value={search} onChange={(e)=>setSearch(e.target.value)}/> */}
            <nav className="flex margin-left-auto icon-nav">
                <Link className='btn-link' to="https://github.com/Fector101/android_notify"> <Github /> </Link>
                <button className='btn-link'> <Sun /> </button>
                {/* <button> <MoonIcon /> </button> */}
            </nav>
        </header>
    )
}