import 'package:flutter/material.dart';

import '../services/auth_service.dart';

/// Placeholder shown after login. Replace the body with the real map / search
/// screen; keep the logout button wired to [onLogout].
class HomeScreen extends StatelessWidget {
  final AppUser user;
  final VoidCallback onLogout;

  const HomeScreen({super.key, required this.user, required this.onLogout});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Roam Delhi NCR'),
        actions: [
          IconButton(
            tooltip: 'Log out',
            icon: const Icon(Icons.logout),
            onPressed: onLogout,
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Welcome, ${user.name}!',
                style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 8),
            Text(user.email),
          ],
        ),
      ),
    );
  }
}
