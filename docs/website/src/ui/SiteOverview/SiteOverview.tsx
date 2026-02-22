import { Link, useLocation } from "react-router";
import { ChevronDown, ChevronUp } from "lucide-react";
import "./siteoverview.css";
import { useEffect, useState } from "react";

interface ISiteOverviewData {
    title: string;
    route: string;
    sections: {
        [key: string]: string;
    };
}

function DropDown({
    title,
    sections,
    hash,
    route,
}: {
    route: string;
    title: string;
    sections: string[];
    hash: string;
}) {
    const [opened, setOpened] = useState(false);

    function togglePreview() {
        setOpened((old) => !old);
    }

    // auto open if hash belongs here
    useEffect(() => {
        const match = sections.some((each) => {
            const h =
                "#" + each.trim().toLowerCase().replace(/ /g, "-");
            return h === hash;
        });

        if (match) setOpened(true);
    }, [hash, sections]);

    return (
        <div className="dropdown flex fd-column align-items-cen justify-content-cen no-text-select">
            <div className="header flex align-items-cen width100per space-between">
                <p>{title}</p>

                <button
                    onClick={togglePreview}
                    className="flex align-items-cen justify-content-cen"
                >
                    {opened ? <ChevronUp /> : <ChevronDown />}
                </button>
            </div>

            <ol
                className="content width100per flex fd-column"
                style={{ height: opened ? "auto" : "0px" }}
            >
                {sections.length ? (
                    sections.map((each) => {
                        const hash_ =
                            "#" + each.trim().toLowerCase().replace(/ /g, "-");

                        const active = hash === hash_;

                        return (
                            <li key={each}>
                                <Link
                                    className={active ? "active" : ""}
                                    to={route + hash_}
                                    tabIndex={opened ? 0 : -1}
                                >
                                    {each}
                                </Link>
                            </li>
                        );
                    })
                ) : (
                    <li>No Content</li>
                )}
            </ol>
        </div>
    );
}

export default function SiteOverview() {
    const location = useLocation();
    const [hash, setHash] = useState(location.hash);

    // Update active hash based on scroll position using Intersection Observer
    useEffect(() => {
        // Only observe sections in the main content area (not sidebar)
        const mainContent = document.querySelector('main.flex.fd-column');
        if (!mainContent) return;

        const sections = mainContent.querySelectorAll('[id]');
        let visibleSections = new Map<string, number>();

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    const id = '#' + entry.target.id;
                    // Skip if it's the site-overview sidebar
                    if (entry.target.id === 'site-overview') return;
                    
                    if (entry.isIntersecting) {
                        visibleSections.set(id, entry.intersectionRatio);
                    } else {
                        visibleSections.delete(id);
                    }
                });

                // Update hash to the most visible section
                if (visibleSections.size > 0) {
                    const mostVisible = Array.from(visibleSections.entries()).sort(
                        (a, b) => b[1] - a[1]
                    )[0][0];
                    
                    setHash(mostVisible);
                    window.history.replaceState(null, '', mostVisible);
                }
            },
            // { threshold: [0.1, 0.5, 1.0], rootMargin: '-50px 0px -50% 0px' }
             { threshold: [0, 0.1, 0.25, 0.5], rootMargin: '-20px 0px -20px 0px' }
        );

        sections.forEach((section) => {
            if (section.id && section.id !== 'site-overview') {
                observer.observe(section);
            }
        });

        return () => observer.disconnect();
    }, []);

    const data: ISiteOverviewData[] = [
        {
            title: "Getting Started",
            route: "/getting-started",
            sections: {
                Introduction: "introduction",
                Features: "features",
                Installation: "installation",
                "Basic Usage": "basic-usage",
            },
        },
        {
            title: "Components",
            route: "/components",
            sections: {
                Images: "images",
                Buttons: "buttons",
                "Progress Bars": "progress-bars",
                Texts: "texts",
            },
        },
        {
            title: "Advanced Methods",
            route: "/advanced-methods",
            sections: {
                "Updating Notification": "updating-notification",
                "Adding Image": "adding-image",
                "Channel Management": "channel-management",
                "Getting Identifer": "getting-identifer",
            },
        },
        {
            title: "Reference",
            route: "/reference",
            sections: {
                "Notification Class": "notification-class",
                "NotificationHandler Class": "notificationhandler-class",
                "NotificationStyles Class": "notificationstyles-class",
            },
        },
        {
            title: "Help",
            route: "/help",
            sections: {
                "How to update": "how-to-update",
                "Debugging Tips": "debugging-tips",
                "Contributing-Issues": "contributing-issues",
                "Support Project": "support-project",
                Credits: "credits",
            },
        },
    ];

    // update active hash when route changes
    useEffect(() => {
        setHash(location.hash);
    }, [location]);
    return (
        <div id="site-overview">
            {data.map((each) => (
                <DropDown
                    key={each.title}
                    hash={hash}
                    title={each.title}
                    route={each.route}
                    sections={Object.keys(each.sections)}
                />
            ))}
        </div>
    );
}
