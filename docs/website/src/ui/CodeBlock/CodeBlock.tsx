"use client";
import { useState, useEffect } from "react";
import { Prism } from 'react-syntax-highlighter'
import { dracula } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './codeblock.css'
import { Check, Copy } from "lucide-react";
import { copyText } from '../../assets/js/client-helper';
import Image, { StaticImageData } from "next/image";

export function CodeBlock({ title, img, code, lang = 'python' }: { title?: string, img?: string | StaticImageData, code: string; lang?: string;}) {

    const [fontSize, setFontSize] = useState<string>('16px');

    useEffect(() => {
        const getFontSize = () => {
            return window.innerWidth < 500 ? '12px' : '16px';
        }

        setFontSize(getFontSize());

        const handleResize = () => setFontSize(getFontSize());

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);



    function copyAction(txt: string, e: React.MouseEvent<HTMLButtonElement, MouseEvent>) {
        let element = e.target as HTMLElement | null | undefined
        element = element?.closest('button')
        console.log(element)

        element?.querySelector('.copy-icon')?.classList.add('display-none')
        element?.querySelector('.check-icon')?.classList.remove('display-none')
        copyText(txt)

    }
    return (
        <div className='code-block flex fd-column width100per' tabIndex={0}>
            <button onClick={(e) => copyAction(code, e)}>
                <Copy className='copy-icon' />
                <Check className='check-icon display-none' />
            </button>
            {title &&
                <div className="header">
                    <h3>{title}</h3>
                </div>
            }
            <div className='flex content'>

                <Prism language={lang} style={dracula} customStyle={{ margin: 0, padding: '20px', borderRadius: 0, fontSize: fontSize, overflowX: 'auto' }}>
                    {code}
                </Prism>
                {img && <Image src={img} alt={title || 'demo'} />}
            </div>
        </div>

    )
}

