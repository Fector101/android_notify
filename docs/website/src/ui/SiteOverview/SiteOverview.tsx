import { Link, useLocation } from "react-router";

import { ChevronDown } from "lucide-react"
import './siteoverview.css'
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { ScrollToSection } from "../../ScrollAssist";

function DropDown({ title, sections, hash,route}: { route:string;title: string; sections: string[], hash: string }) {
    const [opened, setOpened] = useState(false)
    function togglePreview() {
        setOpened(old => !old)
    }

    useEffect(()=>{
        sections.forEach(each_section=>{
            const hash_ = '#' + each_section.toLocaleLowerCase().replace(/ /g, '-')
            if(hash===hash_)setOpened(true)
        })
    },[hash,sections])
    return (
        <div className="dropdown flex fd-column align-items-cen justify-content-cen no-text-select">
            <div className="header flex align-items-cen width100per space-between">
                <p>
                    {title}
                </p>
                <button onClick={togglePreview} className="flex align-items-cen justify-content-cen">
                    <ChevronDown />
                </button>
            </div>
            <ol className="content width100per flex fd-column" style={{ height: opened ? 'auto' : '0px' }}>
                {
                    sections.length ?
                        sections.map(each_section => {
                            const hash_ = '#' + each_section.toLocaleLowerCase().replace(/ /g, '-')
                            const state = hash == hash_
                            return <li key={each_section}>
                                <Link className={state ? 'active' : ''} to={ route + hash_} tabIndex={opened?0:-1}>
                                    {each_section}
                                </Link>
                            </li>
                        })
                    :
                        <li>
                            No Content
                        </li>
                }
            </ol>
        </div>
    )

}
export default function SiteOverview() {
    const location = useLocation();
    const [hash, setHash] = useState(location.hash)

    useEffect(() => {
        setHash(location.hash)
        toast.success(location.toString())
    }, [location])

    useEffect(() => {
        const sections = document.querySelectorAll("section");
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        const id = `#${entry.target.id}`;
                        setHash(id)
                        history.replaceState(null, "", id);
                    }
                });
            },
            { threshold: 0.7 }  // 50% of the section must be visible
        );

        sections.forEach((section) => observer.observe(section));

        return () => observer.disconnect(); // Cleanup on unmount
    }, [location.pathname]);

    return (
        // <>

            <div className="site-overview">
                <ScrollToSection/>

                <DropDown
                    hash={hash}
                    route='/getting-started'
                    title="Getting Started"
                    sections={[
                        'Introduction',
                        'Features',
                        'Installation',
                        'Basic Usage'
                    ]}
                />
                <DropDown
                    hash={hash}
                    title="Components"
                    route='/components'
                    sections={[
                        'Images',
                        'Buttons',
                        'Progress Bars',
                        'Texts',
                        
                        
                        //'Persistent Notifications'
                    ]}
                />
                <DropDown
                    hash={hash}
                    title="Advance Methods"
                    route='/advance-methods'

                    sections={[
                        'Updating Notification', // 'Adding More Components',
                        // 'Notification Clicks',
                        'Getting Identifer', //TODO version typo
                        'Channel Management',

                    ]}
                />
                <DropDown
                    hash={hash}
                    title="Reference"
                    route='/components'
                    sections={[
                        'Notification Class',
                        'NotificationHandler Class',
                        'Available Methods',
                        'Advanced Parameters'
                    ]}
                />
                <DropDown
                    hash={hash}
                    title="Extras"
                    route='/components'
                    sections={[
                        'FAQ',
                        'Common Errors',
                        'Contributing',
                        'Changelog'
                    ]}
                />
            </div>

            /* comment ./siteoverview.css .site-overview {`position: fixed;`} to see properly
         <div className="site-overview">
    <DropDown 
        hash={hash} 
        title="Getting Started" 
        sections={[
            'Introduction', 
            'Installation', 
            'Basic Usage'
        ]} 
    />
    <DropDown 
        hash={hash} 
        title="Guides" 
        sections={[
            'Notification Options', 
            'Customizing Behavior', 
            'Error Handling'
        ]} 
    />
    <DropDown 
        hash={hash} 
        title="Reference" 
        sections={[
            'Notification Class', 
            'Available Methods', 
            'Examples'
        ]} 
    />
    <DropDown 
        hash={hash} 
        title="Support" 
        sections={[
            'FAQ', 
            'Troubleshooting', 
            'Contributing'
        ]} 
    />
    <DropDown 
        hash={hash} 
        title="About" 
        sections={[
            'What is Android-notify?', 
            'License', 
            'Changelog'
        ]} 
    />
        </div> 
        * </> */
        
    )
}