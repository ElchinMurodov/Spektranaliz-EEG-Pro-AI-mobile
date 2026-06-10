import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// Quvvat spektral zichligi (PSD) egri chizig'ini chizadi (chastota bo'yicha).
class PsdChart extends StatelessWidget {
  final List<double> freqs;
  final List<double> psd;
  final String channel;

  const PsdChart({
    super.key,
    required this.freqs,
    required this.psd,
    required this.channel,
  });

  @override
  Widget build(BuildContext context) {
    if (freqs.isEmpty || psd.isEmpty) {
      return const Padding(
        padding: EdgeInsets.all(24),
        child: Text("PSD ma'lumoti mavjud emas."),
      );
    }

    final spots = <FlSpot>[
      for (var i = 0; i < freqs.length && i < psd.length; i++)
        FlSpot(freqs[i], psd[i]),
    ];
    final maxY = psd.reduce((a, b) => a > b ? a : b);
    final maxX = freqs.last;

    return AspectRatio(
      aspectRatio: 1.5,
      child: LineChart(
        LineChartData(
          minX: 0,
          maxX: maxX,
          minY: 0,
          maxY: maxY * 1.1 + 1e-9,
          lineTouchData: const LineTouchData(enabled: false),
          gridData: FlGridData(
            show: true,
            drawVerticalLine: true,
            getDrawingHorizontalLine: (_) =>
                FlLine(color: Colors.grey.withOpacity(0.12), strokeWidth: 1),
            getDrawingVerticalLine: (_) =>
                FlLine(color: Colors.grey.withOpacity(0.12), strokeWidth: 1),
          ),
          titlesData: FlTitlesData(
            leftTitles:
                const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles:
                const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles:
                const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: AxisTitles(
              axisNameWidget: const Text('Chastota (Hz)',
                  style: TextStyle(fontSize: 11, color: AppTheme.muted)),
              sideTitles: SideTitles(
                showTitles: true,
                interval: 10,
                getTitlesWidget: (value, _) => Text(
                  value.toInt().toString(),
                  style: const TextStyle(fontSize: 10, color: AppTheme.muted),
                ),
              ),
            ),
          ),
          borderData: FlBorderData(
            show: true,
            border: Border.all(color: Colors.grey.withOpacity(0.2)),
          ),
          lineBarsData: [
            LineChartBarData(
              spots: spots,
              isCurved: true,
              barWidth: 2,
              color: AppTheme.accent,
              dotData: const FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                color: AppTheme.accent.withOpacity(0.12),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
