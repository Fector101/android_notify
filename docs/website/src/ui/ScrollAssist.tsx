"use client"
import { useEffect, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";

const ScrollToTop: React.FC = () => {
    const pathname = usePathname();
    useEffect(() => {
        if (typeof window !== 'undefined') {
            window.scrollTo(0, 0)
        }
    }, [pathname]);
    return null;
};

const ScrollToSection = () => {
    const searchParams = useSearchParams();
    const hash = searchParams.get('hash');
    const [scroll_top, setScrollToTop] = useState<React.ReactNode>(null);
    useEffect(() => {
        if (hash && typeof document !== 'undefined') {
            const section = document.querySelector(hash) as HTMLElement;
            // console.log(hash,section)
            if (section) {
                const headerHeight = 70
                if (typeof window !== 'undefined') {
                    window.scrollTo({
                        top: section.offsetTop - headerHeight,
                        behavior: "smooth",
                    });
                }
            }
        }else{
            console.log('else....')
            setScrollToTop(<ScrollToTop/>)
        }
    }, [hash]);

    return scroll_top
};

export { ScrollToSection };
