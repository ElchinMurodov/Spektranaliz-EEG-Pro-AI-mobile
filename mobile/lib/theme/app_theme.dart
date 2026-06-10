import 'package:flutter/material.dart';

/// Ilovaning rang sxemasi va mavzusi (akademik, toza ko'rinish).
class AppTheme {
  AppTheme._();

  static const Color primary = Color(0xFF1B3A6B); // chuqur ko'k
  static const Color accent = Color(0xFF2E86DE); // yorqin ko'k
  static const Color bg = Color(0xFFF4F6FA);
  static const Color card = Colors.white;
  static const Color ink = Color(0xFF1A2230);
  static const Color muted = Color(0xFF6B7280);

  /// EEG ritmlari uchun ranglar (diagrammalar bir xil ranglardan foydalanadi).
  static const Map<String, Color> bandColors = {
    'delta': Color(0xFF8E44AD),
    'theta': Color(0xFF2980B9),
    'alpha': Color(0xFF27AE60),
    'beta': Color(0xFFE67E22),
    'gamma': Color(0xFFC0392B),
  };

  static const Map<String, String> bandLabels = {
    'delta': 'Delta',
    'theta': 'Theta',
    'alpha': 'Alpha',
    'beta': 'Beta',
    'gamma': 'Gamma',
  };

  static Color confidenceColor(double confidence) {
    if (confidence >= 0.75) return const Color(0xFF27AE60);
    if (confidence >= 0.5) return const Color(0xFFE67E22);
    return const Color(0xFFC0392B);
  }

  static ThemeData get light {
    final base = ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary,
        primary: primary,
        secondary: accent,
        surface: card,
      ),
      scaffoldBackgroundColor: bg,
    );
    return base.copyWith(
      appBarTheme: const AppBarTheme(
        backgroundColor: primary,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: accent,
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle:
              const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
      ),
    );
  }
}
