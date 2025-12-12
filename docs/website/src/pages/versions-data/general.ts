interface IPageDict {
    [key: string]: { title: string; description: string } | undefined;
}
const pages_dict: IPageDict = {
    "getting-started": {
        title: "Getting Started",
        description:''
            // "Learn how to set up and use the Android-notify library in your projects.",
    },
    components: {
        title: "Components",
        description:
            "Explore the various components.",
            // "Explore the various components available in the Android-notify library.",
    },
    // 'general': {
    //     'title': 'General',
    //     'description': 'Learn about the general features and functionalities of the Android-notify library.',
    // },
    // 'notifications': {
    //     'title': 'Notifications',
    //     'description': 'Discover how to create and manage notifications using the Android-notify library.',
    // },
    // 'progress-bars': {
    //     'title': 'Progress Bars',
    //     'description': 'Learn how to implement progress bars in your notifications using the Android-notify library.',
    // },
    // 'content': (
    //     <div className='page-content'>
};

export {pages_dict};
