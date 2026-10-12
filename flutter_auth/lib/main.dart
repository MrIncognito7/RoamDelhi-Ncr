import 'package:flutter/material.dart';

import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'services/auth_service.dart';

void main() => runApp(const RoamApp());

class RoamApp extends StatelessWidget {
  const RoamApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Roam Delhi NCR',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.teal,
        useMaterial3: true,
      ),
      home: const AuthGate(),
    );
  }
}

/// Decides what to show: spinner while checking the saved token, then either
/// the home screen (logged in) or the login screen.
class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  bool _checking = true;
  AppUser? _user;

  @override
  void initState() {
    super.initState();
    _restore();
  }

  Future<void> _restore() async {
    AppUser? user;
    try {
      user = await AuthService.instance.restoreSession();
    } on AuthException {
      user = null; // server unreachable: show login, token stays saved
    }
    if (!mounted) return;
    setState(() {
      _user = user;
      _checking = false;
    });
  }

  Future<void> _logout() async {
    await AuthService.instance.logout();
    if (!mounted) return;
    setState(() => _user = null);
  }

  @override
  Widget build(BuildContext context) {
    if (_checking) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final user = _user;
    if (user == null) {
      return LoginScreen(onAuthenticated: (u) => setState(() => _user = u));
    }
    return HomeScreen(user: user, onLogout: _logout);
  }
}
