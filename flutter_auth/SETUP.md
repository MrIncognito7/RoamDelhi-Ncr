# Flutter login / register: setup

Copy `lib/` over your Flutter project's `lib/` folder (`~/roam_delhi_ncr/lib`).

## 1. Packages
```bash
cd ~/roam_delhi_ncr
flutter pub add http flutter_secure_storage
```
(If Gradle complains about `minSdkVersion`, set `minSdk = 23` in `android/app/build.gradle(.kts)`.)

## 2. Android manifest: `android/app/src/main/AndroidManifest.xml`
Add the internet permission (above `<application>`), and allow plain `http://` while developing:
```xml
<uses-permission android:name="android.permission.INTERNET"/>

<application
    android:usesCleartextTraffic="true"
    ... >
```
Remove `usesCleartextTraffic` once the API is served over HTTPS.

## 3. Run the backend, then the app
```bash
# in the backend folder (needs .env with SECRET_KEY, see README)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# in the Flutter folder
flutter run                                                    # emulator
flutter run --dart-define=API_BASE_URL=http://192.168.1.5:8000  # real phone (your PC's Wi-Fi IP)
```

## How it fits together
- `main.dart`: `AuthGate` checks for a saved token on startup -> home or login.
- `screens/login_screen.dart`, `screens/register_screen.dart`: the two pages.
- `services/auth_service.dart`: all HTTP + token storage. Use `AuthService.instance.authHeaders()` for future protected calls.
- `screens/home_screen.dart`: placeholder, replace with the map screen.
