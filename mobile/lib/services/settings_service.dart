import 'package:shared_preferences/shared_preferences.dart';

import '../config/app_config.dart';

/// Server manzili kabi foydalanuvchi sozlamalarini saqlaydi/oladi.
class SettingsService {
  static const _keyBaseUrl = 'base_url';

  /// Saqlangan server manzilini qaytaradi (bo'lmasa, standart manzil).
  static Future<String> getBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    final url = prefs.getString(_keyBaseUrl);
    if (url == null || url.trim().isEmpty) return AppConfig.defaultBaseUrl;
    return url.trim();
  }

  /// Server manzilini saqlaydi (oxiridagi '/' belgisi olib tashlanadi).
  static Future<void> setBaseUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    var clean = url.trim();
    while (clean.endsWith('/')) {
      clean = clean.substring(0, clean.length - 1);
    }
    await prefs.setString(_keyBaseUrl, clean);
  }
}
