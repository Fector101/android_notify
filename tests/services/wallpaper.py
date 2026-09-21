import os, threading, traceback, time
from jnius import autoclass

from android_notify import Notification
from android_notify.config import get_python_service
from android_notify.core import get_app_root_path

from pythonosc import dispatcher, osc_server

BuildVersion = autoclass("android.os.Build$VERSION")
ServiceInfo = autoclass("android.content.pm.ServiceInfo")


# get and store port for java
def get_service_port():
    try:
        service_port = int(os.environ.get('PYTHON_SERVICE_ARGUMENT', '5006'))
    except (TypeError, ValueError):
        service_port = 5006

    try:
        service_server_store_path = os.path.join(get_app_root_path(), 'port.txt')
        with open(service_server_store_path, "w") as f:
            f.write(str(service_port))
    except Exception as error_write_port:
        print("python service Error writing service port:", error_write_port)
        traceback.print_exc()
    return service_port


# Start foreground service
service = get_python_service()
foreground_type = ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC if BuildVersion.SDK_INT >= 30 else 0

notification = Notification(title="Hey From Service", name="i_have_a_name")
notification.addButton(text="Resume", receiver_name="CarouselReceiver", action="ACTION_RESUME")
notification.addButton(text="Pause", receiver_name="CarouselReceiver", action="ACTION_PAUSE")
notification.addButton(text="Stop", receiver_name="CarouselReceiver", action="ACTION_STOP")

builder = notification.start_building()
service.startForeground(notification.id, builder.build(), foreground_type)
service.setAutoRestartService(True)  # auto-restart if killed

class MyWallpaperReceiver:
    def __init__(self):
        self.live = True
        self.paused = False
        self.lock = threading.Lock()

        threading.Thread(target=self.heart, daemon=True).start()

    def heart(self):
        start = time.time()
        fmt = lambda s: f"{int(s // 3600)}h {int((s % 3600) // 60)}m {int(s % 60)}s"

        while self.live:
            with self.lock:
                paused = self.paused

            if not paused:
                elapsed = time.time() - start
                notification.updateTitle(f"Running for {fmt(elapsed)}")

            time.sleep(1)

    def stop(self, *args):
        self.live = False
        print("python service stop args:", args)
        service.stopSelf()

    def pause(self, *args):
        with self.lock:
            self.paused = True
        print("python service pause data received:", args)
        notification.updateTitle("Carousel Paused")

    def resume(self, *args):
        with self.lock:
            self.paused = False
        print("python service resume data received:", args)
        notification.updateTitle("Carousel Resumed")



myWallpaperReceiver = MyWallpaperReceiver()
myDispatcher = dispatcher.Dispatcher()

myDispatcher.map("/pause", myWallpaperReceiver.pause)
myDispatcher.map("/resume", myWallpaperReceiver.resume)
myDispatcher.map("/stop", myWallpaperReceiver.stop)

server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", get_service_port()), myDispatcher)

try:
    server.serve_forever()
except Exception as e:
    print("python Service Main loop Failed:", e)
    traceback.print_exc()
    # Avoiding process is bad java.lang.SecurityException
