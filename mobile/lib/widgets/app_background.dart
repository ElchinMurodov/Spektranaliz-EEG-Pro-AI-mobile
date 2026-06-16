import 'package:flutter/material.dart';

/// Ish stoli dasturidagidek EEG-spektr fonini ekran ortiga joylaydi.
///
/// Fon rasmi butun ekranni qoplaydi (cover), ustiga esa yengil oqartiruvchi
/// qatlam (overlay) qo'yiladi — shunda kartalar va matn o'qilishi qulay bo'ladi.
class AppBackground extends StatelessWidget {
  final Widget child;

  /// Fon ustidagi oqartiruvchi qatlam shaffofligi (0..1). Kattaroq qiymat —
  /// fon yumshoqroq (oqishroq) ko'rinadi.
  final double overlayOpacity;

  const AppBackground({
    super.key,
    required this.child,
    this.overlayOpacity = 0.86,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        // 1-qatlam: EEG-spektr foni (ish stoli dasturi bilan bir xil rasm)
        Image.asset(
          'assets/images/background.jpg',
          fit: BoxFit.cover,
          // Rasm yuklanmasa, ilova ishlamay qolmasin — bo'sh konteyner
          errorBuilder: (_, __, ___) => const SizedBox.shrink(),
        ),
        // 2-qatlam: oqartiruvchi qatlam (kontent o'qilishi uchun)
        Container(color: Colors.white.withOpacity(overlayOpacity)),
        // 3-qatlam: asosiy kontent
        child,
      ],
    );
  }
}
