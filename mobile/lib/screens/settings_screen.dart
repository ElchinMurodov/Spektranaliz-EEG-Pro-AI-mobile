import 'package:flutter/material.dart';

import '../config/app_config.dart';
import '../services/api_service.dart';
import '../services/settings_service.dart';
import '../theme/app_theme.dart';
import '../widgets/app_background.dart';

/// Server manzilini sozlash va ulanishni tekshirish ekrani.
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _controller = TextEditingController();
  bool _checking = false;
  String? _status;
  bool? _ok;

  @override
  void initState() {
    super.initState();
    SettingsService.getBaseUrl().then((url) {
      setState(() => _controller.text = url);
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    await SettingsService.setBaseUrl(_controller.text);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Server manzili saqlandi.')),
      );
    }
  }

  Future<void> _testConnection() async {
    setState(() {
      _checking = true;
      _status = null;
      _ok = null;
    });
    await SettingsService.setBaseUrl(_controller.text);
    final api = ApiService(_controller.text.trim());
    final ok = await api.checkHealth();
    if (!mounted) return;
    setState(() {
      _checking = false;
      _ok = ok;
      _status = ok
          ? "Ulanish muvaffaqiyatli — server javob bermoqda."
          : "Serverga ulanib bo'lmadi. Manzil, port va tarmoqni tekshiring.";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(title: const Text('Sozlamalar')),
      body: AppBackground(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
          const Text(
            'Backend server manzili',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _controller,
            keyboardType: TextInputType.url,
            autocorrect: false,
            decoration: InputDecoration(
              hintText: AppConfig.defaultBaseUrl,
              border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12)),
              prefixIcon: const Icon(Icons.dns_outlined),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _checking ? null : _testConnection,
                  icon: _checking
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.wifi_tethering),
                  label: const Text('Ulanishni tekshirish'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: FilledButton.icon(
                  onPressed: _save,
                  icon: const Icon(Icons.save_outlined),
                  label: const Text('Saqlash'),
                ),
              ),
            ],
          ),
          if (_status != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: (_ok == true ? Colors.green : Colors.red)
                    .withOpacity(0.08),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Icon(_ok == true ? Icons.check_circle : Icons.error_outline,
                      color: _ok == true ? Colors.green : Colors.red),
                  const SizedBox(width: 10),
                  Expanded(child: Text(_status!)),
                ],
              ),
            ),
          ],
          const SizedBox(height: 24),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text('Maslahat',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  Text(
                    '• Android emulyatori: http://10.0.2.2:8000\n'
                    '• iOS simulyatori: http://localhost:8000\n'
                    '• Haqiqiy qurilma: kompyuteringizning lokal IP manzili, '
                    'masalan http://192.168.1.50:8000 (bitta Wi-Fi tarmog\'ida).',
                    style: TextStyle(color: AppTheme.muted, height: 1.5),
                  ),
                ],
              ),
            ),
          ),
        ],
        ),
      ),
    );
  }
}
