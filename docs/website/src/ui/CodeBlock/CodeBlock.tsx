import { useState, useEffect } from "react";
import { Prism } from 'react-syntax-highlighter'
import { dracula } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './codeblock.css'
import { Check, Copy } from "lucide-react";
import { copyText } from '../../assets/js/helper';

export function CodeBlock({ title, img = '', code, lang = 'python' }: { title?: string, img?: string, code: string; lang?: string;}) {

    const [fontSize, setFontSize] = useState<string>(getFontSize());

    function getFontSize(): string {
        return window.innerWidth < 500 ? '12px' : '16px';
    }

    useEffect(() => {
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
        // setTimeout(() => {
        //     element?.querySelector('.copy-icon')?.classList.remove('display-none')
        //     element?.querySelector('.check-icon')?.classList.add('display-none')
        // },500)
        copyText(txt)

    }
    return (
        <div className='code-block flex fd-column width100per' tabIndex={0}>
            <button onClick={(e) => copyAction(code, e)}>site-overview
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
                <img src={img} />
            </div>
        </div>

    )
}


// // import React from 'react';
// import Highlight, { defaultProps } from 'prism-react-renderer';
// import useMeasure from 'react-use-measure';
// import copy from 'copy-to-clipboard';
// import { AnimatePresence, motion, MotionConfig } from 'framer-motion';

// import styles from './code-block.module.css';

// const variants = {
//   visible: { opacity: 1, scale: 1 },
//   hidden: { opacity: 0, scale: 0.5 },
// };

// const theme = {
//   plain: {
//     color: 'var(--gray12)',
//     fontSize: 12,
//     fontFamily: 'var(--font-mono)',
//   },
//   styles: [
//     {
//       types: ['comment'],
//       style: {
//         color: 'var(--gray9)',
//       },
//     },
//     {
//       types: ['atrule', 'keyword', 'attr-name', 'selector', 'string'],
//       style: {
//         color: 'var(--gray11)',
//       },
//     },
//     {
//       types: ['punctuation', 'operator'],
//       style: {
//         color: 'var(--gray9)',
//       },
//     },
//     {
//       types: ['class-name', 'function', 'tag'],
//       style: {
//         color: 'var(--gray12)',
//       },
//     },
//   ],
// };

// export const CodeBlock = ({ children, initialHeight = 0 }: { children: string; initialHeight?: number }) => {
//   const [ref, bounds] = useMeasure();
//   const [copying, setCopying] = React.useState<number>(0);

//   const onCopy = React.useCallback(() => {
//     copy(children);
//     setCopying((c) => c + 1);
//     setTimeout(() => {
//       setCopying((c) => c - 1);
//     }, 2000);
//   }, [children]);

//   return (
//     <div className={styles.outerWrapper}>
//       <button className={styles.copyButton} onClick={onCopy} aria-label="Copy code">
//         <MotionConfig transition={{ duration: 0.15 }}>
//           <AnimatePresence initial={false} mode="wait">
//             {copying ? (
//               <motion.div animate="visible" exit="hidden" initial="hidden" key="check" variants={variants}>
//                 <svg
//                   viewBox="0 0 24 24"
//                   width="14"
//                   height="14"
//                   stroke="currentColor"
//                   strokeWidth="1.5"
//                   strokeLinecap="round"
//                   strokeLinejoin="round"
//                   fill="none"
//                   shapeRendering="geometricPrecision"
//                 >
//                   <path d="M20 6L9 17l-5-5"></path>
//                 </svg>
//               </motion.div>
//             ) : (
//               <motion.div animate="visible" exit="hidden" initial="hidden" key="copy" variants={variants}>
//                 <svg
//                   viewBox="0 0 24 24"
//                   width="14"
//                   height="14"
//                   stroke="currentColor"
//                   strokeWidth="1.5"
//                   strokeLinecap="round"
//                   strokeLinejoin="round"
//                   fill="none"
//                   shapeRendering="geometricPrecision"
//                 >
//                   <path d="M8 17.929H6c-1.105 0-2-.912-2-2.036V5.036C4 3.91 4.895 3 6 3h8c1.105 0 2 .911 2 2.036v1.866m-6 .17h8c1.105 0 2 .91 2 2.035v10.857C20 21.09 19.105 22 18 22h-8c-1.105 0-2-.911-2-2.036V9.107c0-1.124.895-2.036 2-2.036z"></path>
//                 </svg>
//               </motion.div>
//             )}
//           </AnimatePresence>
//         </MotionConfig>
//       </button>
//       {/* @ts-ignore */}
//       <Highlight {...defaultProps} theme={theme} code={children} language="jsx">
//         {({ className, tokens, getLineProps, getTokenProps }) => (
//           <motion.pre
//             className={styles.wrapper}
//             animate={{ height: bounds.height || initialHeight }}
//             transition={{ type: 'easeOut', duration: 0.2 }}
//           >
//             <div className={`${className} ${styles.root}`} ref={ref}>
//               <div />
//               {tokens.map((line, i) => {
//                 const { key: lineKey, ...rest } = getLineProps({ line, key: i });
//                 return (
//                   <div key={lineKey} {...rest}>
//                     {line.map((token, key) => {
//                       const { key: tokenKey, ...rest } = getTokenProps({ token, key });
//                       return <span key={tokenKey} {...rest} />;
//                     })}
//                   </div>
//                 );
//               })}
//             </div>
//           </motion.pre>
//         )}
//       </Highlight>
//     </div>
//   );
// };