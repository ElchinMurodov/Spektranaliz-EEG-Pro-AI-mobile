import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:spektranaliz_eeg_pro_ai/main.dart';

void main() {
  testWidgets('Ilova ishga tushadi va asosiy ekran ko\'rinadi',
      (WidgetTester tester) async {
    await tester.pumpWidget(const SpektranalizApp());

    // Asosiy ekrandagi "Natijani olish" tugmasi mavjudligini tekshiramiz.
    expect(find.text('Natijani olish'), findsOneWidget);
    expect(find.byIcon(Icons.settings_outlined), findsOneWidget);
  });
}
