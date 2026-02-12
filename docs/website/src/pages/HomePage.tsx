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

                <h1 className='huge'>1.60<span style={{ fontSize: "2rem" }}>.10</span></h1>
                <p>Release Notes</p>
                <hr />
                <p className="paragraph">This release includes several improvements, features and enhances stability of the library.</p>

                <h3 className='paragraph'>Improvements</h3>
                <span className='code width100per flex paragraph'></span>
                <ol>
                    <p className="paragraph">- Interactions in Service: A way to pass in BroadCast Reciver and Actions to Buttons</p>
                    <p className="paragraph" style={{ lineHeight: 1.4 }}>- Usage without gradle dependencies: new branch <span className="code green-shade">without-androidx</span> was created for this singular purpose, allowing to run in pyroid3 mobile app and Flet apps, This Branch can be installed through <span className="code green-shade">__version__.dev0</span></p>
                    <p className="paragraph">- Flet support: Beta support for Flet Python apps.</p>
                    <p className="paragraph">- Better Logging: Instead of prints now using python logger allowing to show and choose logs by levels importance.</p>
                    <p className="paragraph">- Modularization: Spilted package file into simpler structure arranged by specific tasks making it easier to manage.</p>
                    <p className="paragraph"></p>
                </ol>


                <h3 className='paragraph'><span className='code'>Class: Notification</span></h3>

                <h4 className='paragraph'>New Arguments</h4>
                <span className='code width100per flex paragraph'></span>
                <ul className='inner-section-2 paragraph space-y-[8px]'>
                    <li><span className="code">addButton</span> - receiver_name, action</li>
                    <li><span className="code">createChannel</span> - vibrate, res_sound_name</li>
                    <li><span className="code">setBigText</span> - title, summary</li>
                </ul>

                <p className="paragraph"></p>
                <h4 className='paragraph'>New Methods</h4>
                <span className='code width100per flex paragraph'></span>

                <ul className='inner-section-2 paragraph space-y-[8px]'>
                    <li><span className="code">setColor</span> - color, changes app icon color using hex code.</li>
                    <li><span className="code">setSubText</span> - text, Adds small text near the title (e.g. download time remaining)</li>
                    <li><span className="code">setWhen</span> - secs_ago, to change the time the notification was created</li>
                    <li><span className="code">channelExists</span> - channel_id, to check if said channel exists</li>
                    <li><span className="code">doChannelsExist</span> - ids, Accepts a list of channel IDs and returns those that do not exist</li>
                    <li><span className="code">setData</span> - data_object, to Attach a dictionary of data for possible later use</li>
                    <li><span className="code">fVibrate</span> - For when regular notifications vibrate turned off in device settings (useful for Alarms)</li>
                    <li><span className="code">fill_args</span> - Takes same Arguments as send method, it fills notification args without sending.</li>

                </ul>

                <ul className='inner-section-2 paragraph'>
                    <p style={{ lineHeight: 2 }}>- Support for devices less than Android 8</p>
                    <li><span className="code">setVibrate</span> - pattern, defaults to a single vibration</li>
                    <li><span className="code">setSound</span> - res_sound_name, changes the default notification sound</li>
                </ul>

                <h3 className='paragraph'><span className='code'>Class: NotificationHandler</span></h3>

                <h4 className='paragraph'>New Arguments</h4>
                <span className='code width100per flex paragraph'></span>

                <ul className='inner-section-2 paragraph'>
                    <li><span className="code">get_name</span> - on_start, must be True when called from App.on_start()</li>
                </ul>

                <p className="paragraph"></p>
                <h4 className='paragraph'>New Property</h4>
                <span className='code width100per flex paragraph'></span>

                <ul className='inner-section-2 paragraph'>
                    <li><span className="code">data_object</span> - Access data added via Notification.setData.</li>
                </ul>
            </section>




            <details className='version-deatils'>
            <summary className='version-summary-strip'>Version 1.59 release notes</summary>
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
                    <li><span className="code green-shade">setBigPicture</span> == <span className="code yellow-shade">Notification(...,big_picture_path="...",style=NotificationStyles.BIG_PICTURE)</span></li>
                    <li><span className="code green-shade">setBigText</span> == <span className="code yellow-shade">Notification(...,body="...",style=NotificationStyles.BIG_TEXT)</span></li>
                    <li><span className="code green-shade">setLines</span> == <span className="code yellow-shade">Notification(...,lines_txt="...",style=NotificationStyles.INBOX)</span></li>
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
              
            </section>
            </details>
            

            <span className='flex next-page-btns-box space-between'>
                <Link className='next-page-btn' to='/help'>
                    <ChevronLeft />
                    <span>
                        <p className='next-txt'>Previous</p>
                        <p className='page-name'>help</p>
                    </span>
                </Link>
                <Link className='next-page-btn' to='/getting-started'>
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