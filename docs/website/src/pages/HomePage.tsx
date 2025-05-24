import { Link } from 'react-router'
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { ScrollToSection } from '../ui/ScrollAssist'
// import { CodeBlock } from '../ui/CodeBlock/CodeBlock';
import "../assets/css/home-page.css"
export default function HomePage() {
    return (
        <div className="page main-page home-page">
            <ScrollToSection />
            <section className="page-section flex fd-column" id='installation'>
                <h1 className='huge'>1.59</h1>
                <p>Release Notes</p>
                <hr />
                <p className="paragraph">This release includes several improvements, features and a bug fix to enhance the performance and stability of the library.</p>
                <h3 className='paragraph'>Improvements</h3>
                <span className='code width100per flex paragraph'></span>

                <p className="paragraph">- Freeing up __init__ kwargs, Created some new methods:</p>
                <ul className='inner-section-2 paragraph'>
                    <li><span className="code green-shade">setSmallIcon</span> == <span className="code yellow-shade">Notification(...,app_icon="...") </span></li>
                    <li><span className="code green-shade">setLargeIcon</span> == <span className="code yellow-shade">Notification(...,large_icon_path="...",style=NotificationStyles.LARGE_ICON)</span></li>
                    <li><span className="code green-shade">setBigPicture</span> == <span className="code yellow-shade">Notification(...,body="...",style=NotificationStyles.BIG_PICTURE)</span></li>
                    <li><span className="code green-shade">setBigText</span> == <span className="code yellow-shade">Notification(...,big_picture_path="...",style=NotificationStyles.BIG_TEXT)</span></li>
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
                <p className="paragraph">- Fixed a bug where .getIdentifer returned value even when app wasn't opened by notification.</p>
                <h3 className='paragraph'>Changes</h3>
                <p className="paragraph">- Changed .getIdentifer to .get_name</p>
                {/* Copilot Shit */}
                {/*
                <p className="paragraph">- Improved the handling of notification channels for better compatibility with Android 13 and above.</p>
                <p className="paragraph">- Added support for custom icons in notifications.</p>
                <p className="paragraph">- Updated the documentation to provide clearer examples and usage instructions.</p>
                <p className="paragraph">- Optimized the library for better performance and reduced memory usage.</p>
                <p className="paragraph">- Fixed various minor bugs and issues reported by users.</p>
                <p className="paragraph">- Added new features to enhance the user experience.</p>
                <p className="paragraph">- Improved the overall stability and reliability of the library.</p>
                <p className="paragraph">- Updated dependencies to the latest versions.</p>
                <p className="paragraph">- Added new features to enhance the user experience.</p> */}
                {/* <p className="paragraph">- Improved the overall stability and reliability of the library.</p> */}
                {/* <p className="paragraph margin-left-auto auto-width">Happy coding!</p> */}
            </section>
            {/* <section className="page-section" id='home'> */}
                {/* <h2>Home</h2>
                <hr />
                <p className="paragraph">Welcome to the Android Notify documentation! This guide will help you understand how to use the library effectively.</p>
                <p className="paragraph">Android Notify is a Python library that allows you to generate notifications in your Android devices. It provides a simple and efficient way to create and manage notifications, making it easier for developers to enhance their applications with notification features.</p>
                <p className="paragraph">This documentation covers everything from installation to advanced usage, including examples and best practices. Whether you're a beginner or an experienced developer, you'll find valuable information here.</p>
                <p className="paragraph">If you have any questions or need further assistance, feel free to reach out to the community or the library maintainers.</p> */}
            {/* </section> */}


            <span className='flex next-page-btns-box space-between'>
                <Link className='next-page-btn' to='/extras'>
                    <ChevronLeft />
                    <span>
                        <p className='next-txt'>Previous</p>
                        <p className='page-name'>extras</p>
                    </span>
                </Link>
                <Link className='next-page-btn' to='/getting-started'>
                    {/* <Link className='next-page-btn' to='/event-handling'> */}
                    <span>
                        <p className='next-txt'>Next</p>
                        <p className='page-name'>Getting Started</p>
                        {/* <p className='page-name'>Event Handling</p> */}
                    </span>
                    <ChevronRight />
                </Link>
            </span>

        </div>
    )
}