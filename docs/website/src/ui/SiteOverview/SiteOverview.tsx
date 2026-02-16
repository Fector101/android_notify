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
</> */