# p4a/hook.py
from pathlib import Path
from pythonforandroid.toolchain import ToolchainCL

def after_apk_build(toolchain: ToolchainCL):
    manifest_file = Path(toolchain._dist.dist_dir) / "src" / "main" / "AndroidManifest.xml"
    old_manifest = manifest_file.read_text(encoding="utf-8")

    package = "org.wally.waller"
    service_name="Wallpapercarousel"
    foreground_type="dataSync"
    target = f'android:name="{package}.Service{service_name.capitalize()}"'

    # Inject foregroundServiceType
    pos = old_manifest.find(target)

    if pos != -1:
        end = old_manifest.find("/>", pos)
        old_manifest = (old_manifest[:end] + f'android:foregroundServiceType="{foreground_type}"' + old_manifest[end:])
        print(f"Successfully Added foregroundServiceType to Service{service_name}")

    # Your custom receiver XML
    receiver_name = "CarouselReceiver"
    receiver_xml = f'''
    <receiver android:name="{package}.{receiver_name}"
              android:enabled="true"
              android:exported="false">
        <intent-filter>
            <action android:name="ACTION_RESUME" />
            <action android:name="ACTION_PAUSE" />
            <action android:name="ACTION_STOP" />
        </intent-filter>
    </receiver>
    '''

    # Insert before the closing </application>
    new_manifest = old_manifest.replace('</application>', f'{receiver_xml}\n</application>')

    manifest_file.write_text(new_manifest, encoding="utf-8")

    print(new_manifest)
    if old_manifest != new_manifest:
        print("Receiver added successfully")
    else:
        print("Failed to add receiver")