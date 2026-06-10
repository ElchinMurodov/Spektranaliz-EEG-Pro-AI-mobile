import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// 5 ta EEG ritmi bo'yicha nisbiy quvvatni ustunli diagrammada ko'rsatadi.
class BandBarChart extends StatelessWidget {
  final Map<String, double> bands; // delta..gamma -> 0..1

  const BandBarChart({super.key, required this.bands});

  @override
  Widget build(BuildContext context) {
    const order = ['delta', 'theta', 'alpha', 'beta', 'gamma'];
    final maxVal = bands.values.isEmpty
        ? 1.0
        : bands.values.reduce((a, b) => a > b ? a : b);
    final top = (maxVal * 1.25).clamp(0.1, 1.0);

    return AspectRatio(
      aspectRatio: 1.6,
      child: BarChart(
        BarChartData(
          alignment: BarChartAlignment.spaceAround,
          maxY: top,
          barTouchData: BarTouchData(
            touchTooltipData: BarTouchTooltipData(
              getTooltipItem: (group, _, rod, __) {
                final name = order[group.x];
                return BarTooltipItem(
                  '${AppTheme.bandLabels[name]}\n${(rod.toY * 100).toStringAsFixed(1)}%',
                  const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                );
              },
            ),
          ),
          titlesData: FlTitlesData(
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 36,
                getTitlesWidget: (value, _) => Text(
                  '${(value * 100).toInt()}%',
                  style: const TextStyle(fontSize: 10, color: AppTheme.muted),
                ),
              ),
            ),
            rightTitles:
                const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles:
                const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, _) {
                  final i = value.toInt();
                  if (i < 0 || i >= order.length) return const SizedBox();
                  return Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: Text(
                      AppTheme.bandLabels[order[i]] ?? order[i],
                      style: const TextStyle(
                          fontSize: 11, fontWeight: FontWeight.w600),
                    ),
                  );
                },
              ),
            ),
          ),
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            getDrawingHorizontalLine: (_) =>
                FlLine(color: Colors.grey.withOpacity(0.15), strokeWidth: 1),
          ),
          borderData: FlBorderData(show: false),
          barGroups: [
            for (var i = 0; i < order.length; i++)
              BarChartGroupData(
                x: i,
                barRods: [
                  BarChartRodData(
                    toY: bands[order[i]] ?? 0.0,
                    color: AppTheme.bandColors[order[i]],
                    width: 24,
                    borderRadius: const BorderRadius.vertical(
                        top: Radius.circular(6)),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
