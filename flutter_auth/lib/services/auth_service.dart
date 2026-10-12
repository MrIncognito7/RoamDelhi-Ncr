import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import '../config.dart';

/// Error with a message that is safe to show directly to the user.
class AuthException implements Exception {
  final String message;
  AuthException(this.message);

  @override
  String toString() => message;
}

class AppUser {
  final int id;
  final String name;
  final String email;

  const AppUser({required this.id, required this.name, required this.email});

  factory AppUser.fromJson(Map<String, dynamic> json) => AppUser(
        id: json['id'] as int,
        name: json['name'] as String,
        email: json['email'] as String,
      );
}

/// Talks to the FastAPI /register, /login and /me endpoints and keeps the
/// JWT in the Android Keystore (flutter_secure_storage), not in plain prefs.
class AuthService {
  AuthService._();
  static final AuthService instance = AuthService._();

  static const _tokenKey = 'access_token';
  static const _timeout = Duration(seconds: 15);

  final _storage = const FlutterSecureStorage();

  // ---------- public API ----------

  Future<AppUser> register({
    required String name,
    required String email,
    required String password,
  }) async {
    final data = await _postAuth('/register', {
      'name': name.trim(),
      'email': email.trim(),
      'password': password,
    });
    return _saveSession(data);
  }

  Future<AppUser> login({
    required String email,
    required String password,
  }) async {
    final data = await _postAuth('/login', {
      'email': email.trim(),
      'password': password,
    });
    return _saveSession(data);
  }

  /// Returns the logged-in user if a saved token is still valid, else null.
  /// Throws [AuthException] only when the server can't be reached (the saved
  /// token is kept in that case, so the user isn't logged out by bad Wi-Fi).
  Future<AppUser?> restoreSession() async {
    final token = await _storage.read(key: _tokenKey);
    if (token == null) return null;

    final response = await _send(
      () => http
          .get(Uri.parse('$apiBaseUrl/me'),
              headers: {'Authorization': 'Bearer $token'})
          .timeout(_timeout),
    );

    if (response.statusCode == 200) {
      return AppUser.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    }
    if (response.statusCode == 401) {
      await _storage.delete(key: _tokenKey); // expired or invalid
      return null;
    }
    throw AuthException('Server error (${response.statusCode}). Try again.');
  }

  Future<void> logout() => _storage.delete(key: _tokenKey);

  /// Use this for future authenticated calls (trips, expenses...).
  Future<Map<String, String>> authHeaders() async {
    final token = await _storage.read(key: _tokenKey);
    return {if (token != null) 'Authorization': 'Bearer $token'};
  }

  // ---------- internals ----------

  Future<Map<String, dynamic>> _postAuth(
      String path, Map<String, dynamic> body) async {
    final response = await _send(
      () => http
          .post(
            Uri.parse('$apiBaseUrl$path'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(body),
          )
          .timeout(_timeout),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }
    throw AuthException(_errorMessage(response));
  }

  Future<AppUser> _saveSession(Map<String, dynamic> data) async {
    await _storage.write(key: _tokenKey, value: data['access_token'] as String);
    return AppUser.fromJson(data['user'] as Map<String, dynamic>);
  }

  /// Runs a request and turns network failures into friendly messages.
  Future<http.Response> _send(Future<http.Response> Function() request) async {
    try {
      return await request();
    } on TimeoutException {
      throw AuthException('The server took too long to respond. Try again.');
    } on SocketException {
      throw AuthException(
          "Can't reach the server. Check your connection and that the API is running.");
    } on http.ClientException {
      throw AuthException("Can't reach the server. Check your connection.");
    }
  }

  /// FastAPI sends {"detail": "text"} for 400/401 and
  /// {"detail": [{"msg": ...}, ...]} for 422 validation errors.
  String _errorMessage(http.Response response) {
    try {
      final detail = (jsonDecode(response.body) as Map<String, dynamic>)['detail'];
      if (detail is String) return detail;
      if (detail is List && detail.isNotEmpty) {
        final msg = (detail.first as Map<String, dynamic>)['msg'] as String? ?? '';
        return msg.replaceFirst('Value error, ', '');
      }
    } catch (_) {
      // fall through to the generic message
    }
    return 'Something went wrong (${response.statusCode}). Try again.';
  }
}
