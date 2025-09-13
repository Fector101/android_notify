"use client"
import Link from 'next/link'
import { ChevronLeft, ChevronRight } from 'lucide-react';
import "../assets/css/home-page.css"
export default function HomePage() {
    return (
        <div className="page main-page home-page">
            <section className="page-section flex fd-column" id='installation'>
                <h1 className='huge'>1.59</h1>
                <p>Release Notes</p>
                <hr />
                <p className="paragraph">This release includes several improvements, features and a bug fix to enhance the performance and stability of the library.</p>
                <h3 className='paragraph'>Improvements</h3>
                <span className='code width100per flex paragraph'></span>

                <p className="paragraph">- Freeing up __init__ kwargs, Created some new methods:</p>
                <ul className='inner-section-2 paragraph'>
                    <li><span className="code green-shade">setSmallIcon</span> == <span className="code yellow-shade">Notification(...,app_icon=&quot;...&quot;) </span></li>
                    <li><span className="code green-shade">setLargeIcon</span> == <span className="code yellow-shade">Notification(...,large_icon_path=&quot;...&quot;,style=NotificationStyles.LARGE_ICON)</span></li>
                    <li><span className="code green-shade">setBigPicture</span> == <span className="code yellow-shade">Notification(...,big_picture_path=&quot;...&quot;,style=NotificationStyles.BIG_PICTURE)</span></li>
                    <li><span className="code green-shade">setBigText</span> == <span className="code yellow-shade">Notification(...,body=&quot;...&quot;,style=NotificationStyles.BIG_TEXT)</span></li>
                    <li><span className="code green-shade">setLines</span> == <span className="code yellow-shade">Notification(...,lines_txt=&quot;...&quot;,style=NotificationStyles.INBOX)</span></li>
                </ul>
                <h3 className='paragraph'>New Features</h3>
                <span className='code width100per flex paragraph'></span>
                <p className='auto-width paragraph'>- Created methods to cancel a certain or all Notifications<span className="code">Notification().cancel()</span>, <span className="code">Notification.cancelAll</span> </p>
                <p className='auto-width paragraph-05'>- Created <span className="code">Notification.createChannel(name, id, desc</span> For android Android 8+</p>
                <p className='auto-width paragraph-05'>- Created <span className="code">Notification.deleteAllChannel()</span> and <span className="code">Notification.deleteChannel(channel_id)</span> </p>
                <p className='auto-width paragraph-05'>- Instead of only requesting in init created <span className="code">NotificationHandler.asks_permission</span> and <span className="code">NotificationHandler.has_permission</span> </p>
                <p className='auto-width paragraph-05'>- When setting a new component after <span className="code">Notification().send</span>  use <span className="code">Notification().refresh</span> </p>
                <p className='auto-width paragraph-05'>- Added a way to access Old Notification instance with <span className="code">Notification().id</span> will act as reference key if instance not available</p>
                <h3 className='paragraph'>Fixes</h3>
                <span className='code width100per flex paragraph'></span>
                <p className="paragraph">- Fixed a bug where .getIdentifer returned value even when app wasn&apos;t opened by notification.</p>
                <h3 className='paragraph'>Changes</h3>
                <p className="paragraph">- Changed .getIdentifer to .get_name</p>
                
            </section>


            <span className='flex next-page-btns-box space-between'>
                <Link className='next-page-btn' href='/extras'>
                    <ChevronLeft />
                    <span>
                        <p className='next-txt'>Previous</p>
                        <p className='page-name'>extras</p>
                    </span>
                </Link>
                <Link className='next-page-btn' href='/getting-started'>
                    <span>
                        <p className='next-txt'>Next</p>
                        <p className='page-name'>Getting Started</p>
                        
                    </span>
                    <ChevronRight />
                </Link>
            </span>

        </div>
    )
}