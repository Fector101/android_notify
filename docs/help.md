# Help

## How to Update

When using buildozer and you want to use a new version, buildozer doesn't automatically remove old versions. You'll have to delete the old version in the `.buildozer` folder. These are some commands to help automate the process for Linux, Windows and macOS.

**Linux**

```bash
cd .buildozer && find . -type d -name "android_notify*" -print0 | xargs -0 rm -r && cd ..
```

**Windows (PowerShell)**

If the command prints folder paths containing `android_notify`, replace `Write-Output` with `Remove-Item`:

```powershell
cd .buildozer
Get-ChildItem -Path . -Directory -Filter "android_notify*" | ForEach-Object { Write-Output $_.FullName }
cd ..
```

**Windows (Git Bash)**

```bash
cd .buildozer && find . -type d -name "android_notify*" -print0 | xargs -0 rm -r && cd ..
```

**macOS**

```bash
cd .buildozer && find . -type d -name "android_notify*" -exec rm -r {} + && cd ..
```

## Debugging Tips

- Enable logs during development: `Notification.logs = True`
- Check channel creation with Android's notification settings
- Verify image paths before sending notifications

## Contribution & Reporting Issues

Feel free to submit pull requests for improvements on [GitHub](https://github.com/Fector101/android_notify)!

Or found a bug? Please open an issue on our [Issues page](https://github.com/Fector101/android_notify/issues).

## Credits

- Name: Fabian - fector101@yahoo.com
- GitHub: [Android Notify Repo](https://github.com/Fector101/android_notify)
- Twitter: [FabianDev_](https://twitter.com/intent/user?user_id=1246911115319263233)

This project was thoroughly tested by the [Laner](https://github.com/Fector101/Laner) project - an application for securely transferring files wirelessly between your PC and phone.

Special thanks to the Kivy and Pyjnius communities for their support and contributions.