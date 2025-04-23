import { useEffect, useState } from "react";
import { useLocation } from "react-router";

const ScrollToTop: React.FC = () => {
    const routePath = useLocation();
    const onTop = () => window.scrollTo(0, 0);
    useEffect(onTop, [routePath]);
    return null;
};

const ScrollToSection = () => {
    const { hash } = useLocation();
    const [scroll_top, setScrollToTop] = useState<React.ReactNode>(null);
    useEffect(() => {
        if (hash) {
            const section = document.querySelector(hash) as HTMLElement;
            // console.log(hash,section)
            if (section) {
                const headerHeight = 70
                window.scrollTo({
                    top: section.offsetTop - headerHeight,
                    behavior: "smooth",
                });
            }
        }else{
            console.log('else....')
            setScrollToTop(<ScrollToTop/>)
        }
    }, [hash]);

    return scroll_top
};

export { ScrollToSection };
