package org.android_notify.music;

import android.media.session.MediaSession;

/**
 * Java bridge for Android-Notify's MusicNotification.
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
}