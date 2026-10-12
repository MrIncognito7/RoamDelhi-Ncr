/// Where the FastAPI server lives.
///
/// Android emulator -> 10.0.2.2 reaches your computer's localhost (default below).
/// Real phone       -> pass your computer's Wi-Fi IP when running:
///   flutter run --dart-define=API_BASE_URL=http://192.168.1.5:8000
const String apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000',
);
