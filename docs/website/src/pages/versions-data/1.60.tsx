// TODO : add a gif for big-text notification
// FIXME : type loerm ipsum typos
const subtextcode = `notification = Notification(
    title="Downloading...",
    message="70% downloaded",
    progress_max_value=100
)
notification.setSubText("19 secs left")

notification.setColor("#00FF00")
notification.updateProgressBar(70)
notification.send()`
const an_colored_basic_small = `<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">

    <TextView
        android:id="@+id/title"
        android:layout_width="wrap_content"
        android:layout_height="0dp"
        android:layout_weight="1"
    />

</LinearLayout>`
const an_colored_basic_large =`<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">

    <TextView
        android:id="@+id/title"
        android:layout_width="wrap_content"
        android:layout_height="0dp"
        android:layout_weight="1"

    />

    <TextView
        android:id="@+id/message"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="4dp"
    />

</LinearLayout>`
const colored_text_code = `Notification(title="Title Color", message="Testing Color",title_color="red").send()`

const component_page = {
    sub_text_code: subtextcode,
    an_colored_basic_small,
    an_colored_basic_large,
    colored_text_code
}

export { component_page}