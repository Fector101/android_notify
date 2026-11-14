package org.android_notify.music;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.media.session.MediaSession;
import android.util.Log;
import android.view.KeyEvent;

/**
 * Java bridge for Android-Notify's MediaNotification.
 *
 * It receives MediaSession transport control events (play/pause/seek/next/prev)
 * from the notification, lock screen and Quick Settings, and forwards them to a
 * Python {@code MediaSessionListener} implemented via pyjnius.
 *
 * The class intentionally lives in the fixed package {@code org.android_notify.music}
 * so it can be shipped pre-compiled as a Maven artifact — users never have to
 * copy or edit this file.
 */
public class MediaSessionCallback extends MediaSession.Callback {

    private static final String TAG = "MediaSessionCallback";

    public interface MediaSessionListener {
        void onPlay();
        void onPause();
        void onSeekTo(long pos);
        void onSkipToNext();
        void onSkipToPrevious();
    }

    private MediaSessionListener listener;

    public MediaSessionCallback(MediaSessionListener listener) {
        this.listener = listener;
    }

    @Override
    public void onPlay() {
        if (listener != null) {
            listener.onPlay();
        }
    }

    @Override
    public void onPause() {
        if (listener != null) {
            listener.onPause();
        }
    }

    @Override
    public void onSeekTo(long pos) {
        if (listener != null) {
            listener.onSeekTo(pos);
        }
    }

    @Override
    public void onSkipToNext() {
        if (listener != null) {
            listener.onSkipToNext();
        }
    }

    @Override
    public void onSkipToPrevious() {
        if (listener != null) {
            listener.onSkipToPrevious();
        }
    }

    /**
     * Receives media-notification action PendingIntents and forwards them to
     * the same Python listener as the MediaSession callback.
     */
    public static final class MediaButtonReceiver extends BroadcastReceiver {

        private static volatile MediaSessionListener activeListener;

        public static void setListener(MediaSessionListener listener) {
            activeListener = listener;
        }

        @Override
        public void onReceive(Context context, Intent intent) {
            if (!Intent.ACTION_MEDIA_BUTTON.equals(intent.getAction())) {
                return;
            }

            KeyEvent event = intent.getParcelableExtra(Intent.EXTRA_KEY_EVENT);
            if (event == null || event.getAction() != KeyEvent.ACTION_DOWN) {
                return;
            }

            MediaSessionListener listener = activeListener;
            if (listener == null) {
                Log.w(TAG, "Ignoring media button; no active media-session listener");
                return;
            }

            switch (event.getKeyCode()) {
                case KeyEvent.KEYCODE_MEDIA_PLAY:
                    listener.onPlay();
                    break;
                case KeyEvent.KEYCODE_MEDIA_PAUSE:
                case KeyEvent.KEYCODE_MEDIA_STOP:
                    listener.onPause();
                    break;
                case KeyEvent.KEYCODE_MEDIA_NEXT:
                    listener.onSkipToNext();
                    break;
                case KeyEvent.KEYCODE_MEDIA_PREVIOUS:
                    listener.onSkipToPrevious();
                    break;
                default:
                    Log.w(TAG, "Ignoring unsupported media key: " + event.getKeyCode());
            }
        }
    }
}