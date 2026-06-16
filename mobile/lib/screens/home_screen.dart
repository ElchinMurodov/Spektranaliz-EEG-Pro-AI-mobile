import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../config/app_config.dart';
import '../services/api_service.dart';
import '../services/settings_service.dart';
import '../theme/app_theme.dart';
import '../widgets/app_background.dart';
import 'result_screen.dart';
import 'settings_screen.dart';

/// Asosiy ekran: EEG fayl tanlash va tahlilni boshlash.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  PlatformFile? _picked;
  bool _loading = false;
  bool _notch = true;

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: AppConfig.allowedExtensions,
      withData: false,
    );
    if (result != null && result.files.isNotEmpty) {
      setState(() => _picked = result.files.first);
    }
  }

  Future<void> _analyze() async {
    final file = _picked;
    if (file == null || file.path == null) return;

    setState(() => _loading = true);
    final baseUrl = await SettingsService.getBaseUrl();
    final api = ApiService(baseUrl);

    try {
      final result = await api.analyzeFile(
        filePath: file.path!,
        fileName: file.name,
        notch: _notch,
      );
      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => ResultScreen(result: result)),
      );
    } catch (e) {
      if (!mounted) return;
      _showError(e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _showError(String message) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Xatolik'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Yopish'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        title: const Text(AppConfig.appName),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            tooltip: 'Sozlamalar',
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const SettingsScreen()),
            ),
          ),
        ],
      ),
      body: AppBackground(
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _header(),
            const SizedBox(height: 20),
            _filePickerCard(),
            const SizedBox(height: 16),
            _optionsCard(),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: (_picked == null || _loading) ? null : _analyze,
              icon: _loading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.analytics_outlined),
              label: Text(_loading ? 'Tahlil qilinmoqda...' : 'Natijani olish'),
            ),
            const SizedBox(height: 24),
            _disclaimer(),
          ],
        ),
      ),
    );
  }

  Widget _header() {
    return Column(
      children: [
        // Ish stoli dasturi bilan bir xil logotip
        Container(
          padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 12),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.7),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Image.asset(
            'assets/images/logo.png',
            height: 64,
            fit: BoxFit.contain,
            // Logo yuklanmasa, eski belgicha ko'rinadi
            errorBuilder: (_, __, ___) => const Icon(
                Icons.monitor_heart_outlined,
                color: AppTheme.primary,
                size: 48),
          ),
        ),
        const SizedBox(height: 14),
        const Text(
          'Sportchining EEG signallarini\nspektral tahlil qilish',
          textAlign: TextAlign.center,
          style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.bold,
              height: 1.35,
              color: AppTheme.ink),
        ),
        const SizedBox(height: 4),
        Text('Versiya ${AppConfig.appVersion}',
            style: const TextStyle(color: AppTheme.muted, fontSize: 12)),
      ],
    );
  }

  Widget _filePickerCard() {
    final file = _picked;
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: _pickFile,
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              Icon(
                file == null ? Icons.upload_file_outlined : Icons.description,
                size: 40,
                color: AppTheme.accent,
              ),
              const SizedBox(height: 12),
              Text(
                file == null ? 'EEG faylni tanlang' : file.name,
                textAlign: TextAlign.center,
                style: const TextStyle(
                    fontSize: 15, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 4),
              Text(
                file == null
                    ? 'EDF · EDF+ · BDF · BDF+ · CSV'
                    : '${(file.size / 1024).toStringAsFixed(1)} KB — boshqa fayl tanlash uchun bosing',
                style: const TextStyle(color: AppTheme.muted, fontSize: 12),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _optionsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8),
        child: SwitchListTile(
          value: _notch,
          onChanged: (v) => setState(() => _notch = v),
          title: const Text('50/60 Hz tarmoq filtri (notch)'),
          subtitle: const Text("Elektr tarmog'i shovqinini bostiradi"),
          activeColor: AppTheme.accent,
        ),
      ),
    );
  }

  Widget _disclaimer() {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.amber.withOpacity(0.12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.amber.withOpacity(0.4)),
      ),
      child: const Row(
        children: [
          Icon(Icons.info_outline, color: Colors.amber, size: 22),
          SizedBox(width: 10),
          Expanded(
            child: Text(
              'Natija TIBBIY TASHXIS EMAS. U faqat EEG signalining funksional '
              'holat ko\'rsatkichlarini ifodalaydi.',
              style: TextStyle(fontSize: 12, height: 1.4),
            ),
          ),
        ],
      ),
    );
  }
}
