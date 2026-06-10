import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// Funksional holatlarni ehtimollik (ishonch %) bo'yicha ro'yxat ko'rinishida
/// chiziqli indikatorlar bilan ko'rsatadi.
class StateProbabilityList extends StatelessWidget {
  final List<String> orderedStates;
  final Map<String, double> probabilities; // 0..1
  final String topState;

  const StateProbabilityList({
    super.key,
    required this.orderedStates,
    required this.probabilities,
    required this.topState,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        for (final state in orderedStates)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: _row(state, probabilities[state] ?? 0.0, state == topState),
          ),
      ],
    );
  }

  Widget _row(String state, double prob, bool isTop) {
    final pct = prob * 100;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                state,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: isTop ? FontWeight.bold : FontWeight.w500,
                  color: isTop ? AppTheme.primary : AppTheme.ink,
                ),
              ),
            ),
            Text(
              '${pct.toStringAsFixed(1)}%',
              style: TextStyle(
                fontSize: 13,
                fontWeight: isTop ? FontWeight.bold : FontWeight.w500,
                color: isTop ? AppTheme.primary : AppTheme.muted,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(6),
          child: LinearProgressIndicator(
            value: prob.clamp(0.0, 1.0),
            minHeight: 8,
            backgroundColor: Colors.grey.withOpacity(0.15),
            valueColor: AlwaysStoppedAnimation(
              isTop ? AppTheme.accent : AppTheme.muted.withOpacity(0.55),
            ),
          ),
        ),
      ],
    );
  }
}
