import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../models/analysis_result.dart';
import '../theme/app_theme.dart';
import '../widgets/band_bar_chart.dart';
import '../widgets/psd_chart.dart';
import '../widgets/state_probability_list.dart';

/// Tahlil natijasini tablarda ko'rsatadi: Umumiy · Ritmlar · Spektr · Hisobot.
class ResultScreen extends StatelessWidget {
  final AnalysisResult result;

  const ResultScreen({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 4,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Tahlil natijasi'),
          bottom: const TabBar(
            isScrollable: true,
            indicatorColor: Colors.white,
            tabs: [
              Tab(text: 'Umumiy'),
              Tab(text: 'Ritmlar'),
              Tab(text: 'Spektr (PSD)'),
              Tab(text: 'Hisobot'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _OverviewTab(result: result),
            _BandsTab(result: result),
            _SpectrumTab(result: result),
            _ReportTab(result: result),
          ],
        ),
      ),
    );
  }
}

class _OverviewTab extends StatelessWidget {
  final AnalysisResult result;
  const _OverviewTab({required this.result});

  @override
  Widget build(BuildContext context) {
    final r = result.result;
    final s = result.summary;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _resultCard(r),
        const SizedBox(height: 16),
        _sectionTitle('Holatlar bo\'yicha ehtimollik'),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: StateProbabilityList(
              orderedStates: r.orderedStates,
              probabilities: r.probabilities,
              topState: r.state,
            ),
          ),
        ),
        if (r.atypical.isNotEmpty) ...[
          const SizedBox(height: 16),
          _atypicalCard(r.atypical),
        ],
        const SizedBox(height: 16),
        _sectionTitle('Yozuv ma\'lumotlari'),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                _infoRow('Fayl', s.sourceFile ?? '—'),
                _infoRow('Format', s.format ?? '—'),
                _infoRow('Kanallar soni', s.channels.toString()),
                _infoRow('Namuna chastotasi',
                    s.fs != null ? '${s.fs} Hz' : 'turlicha'),
                if (s.harmonizedFs != null)
                  _infoRow('Harmonizatsiya', '${s.harmonizedFs} Hz'),
                _infoRow('Davomiyligi',
                    '${s.durationSec.toStringAsFixed(1)} s'),
                _infoRow("O'qish usuli", s.reader ?? '—'),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        _disclaimer(result.disclaimer),
      ],
    );
  }

  Widget _resultCard(ClassificationResult r) {
    final color = AppTheme.confidenceColor(r.confidence);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppTheme.primary, AppTheme.accent],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        children: [
          const Text('YAKUNIY BAHOLANGAN HOLAT',
              style: TextStyle(color: Colors.white70, fontSize: 12, letterSpacing: 1)),
          const SizedBox(height: 8),
          Text(
            r.state,
            textAlign: TextAlign.center,
            style: const TextStyle(
                color: Colors.white,
                fontSize: 26,
                fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 14),
          Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              'Ishonch: ${(r.confidence * 100).toStringAsFixed(1)}%',
              style: TextStyle(color: color, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  Widget _atypicalCard(List<String> reasons) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.orange.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.orange.withOpacity(0.4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: Colors.orange),
              SizedBox(width: 8),
              Text('Atipik naqsh belgilari',
                  style: TextStyle(fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 8),
          ...reasons.map((r) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text('• $r', style: const TextStyle(height: 1.4)),
              )),
          const SizedBox(height: 4),
          const Text('=> Mutaxassis (nevrolog) ko\'rigi tavsiya etiladi.',
              style: TextStyle(fontStyle: FontStyle.italic, fontSize: 12)),
        ],
      ),
    );
  }
}

class _BandsTab extends StatelessWidget {
  final AnalysisResult result;
  const _BandsTab({required this.result});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _sectionTitle('Ritmlar bo\'yicha nisbiy quvvat'),
        Card(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(8, 20, 16, 12),
            child: BandBarChart(bands: result.bands),
          ),
        ),
        const SizedBox(height: 16),
        _sectionTitle('Spektral belgilar (features)'),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(children: _featureRows(result.features)),
          ),
        ),
      ],
    );
  }

  List<Widget> _featureRows(Map<String, double?> f) {
    const labels = {
      'iapf': 'iAPF (individual alfa cho\'qqisi), Hz',
      'dominant_frequency': 'Dominant chastota (PSD), Hz',
      'fft_dominant_frequency': 'Dominant chastota (FFT), Hz',
      'spectral_edge_95': 'Spektral chegara (edge 95%), Hz',
      'spectral_entropy': 'Spektral entropiya',
      'engagement': 'Engagement (jalb) indeksi',
      'ratio_alpha_beta': 'Alpha/Beta nisbati',
      'ratio_theta_beta': 'Theta/Beta nisbati',
      'ratio_theta_alpha': 'Theta/Alpha nisbati',
      'ratio_beta_alpha': 'Beta/Alpha nisbati',
      'faa': 'Frontal alfa asimmetriyasi (FAA)',
      'fmt': 'Frontal-median teta (FMT)',
    };
    return labels.entries.map((e) {
      final v = f[e.key];
      return _infoRow(
          e.value, v == null ? '—' : v.toStringAsFixed(3));
    }).toList();
  }
}

class _SpectrumTab extends StatelessWidget {
  final AnalysisResult result;
  const _SpectrumTab({required this.result});

  @override
  Widget build(BuildContext context) {
    final psd = result.psd;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _sectionTitle('Quvvat spektral zichligi (PSD)'),
        Text('Vakil kanal: ${psd.channel} — Welch usuli',
            style: const TextStyle(color: AppTheme.muted, fontSize: 13)),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(10, 18, 16, 10),
            child: PsdChart(
                freqs: psd.freqs, psd: psd.psd, channel: psd.channel),
          ),
        ),
        const SizedBox(height: 12),
        const Text(
          'PSD egri chizig\'i signal quvvatining chastotalar bo\'yicha '
          'taqsimotini ko\'rsatadi. Cho\'qqilar dominant ritmlarga mos keladi.',
          style: TextStyle(color: AppTheme.muted, height: 1.5, fontSize: 13),
        ),
      ],
    );
  }
}

class _ReportTab extends StatelessWidget {
  final AnalysisResult result;
  const _ReportTab({required this.result});

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: SelectableText(
            result.report,
            style: const TextStyle(
                fontFamily: 'monospace', fontSize: 11.5, height: 1.45),
          ),
        ),
        Positioned(
          right: 16,
          bottom: 16,
          child: FloatingActionButton.small(
            backgroundColor: AppTheme.accent,
            onPressed: () {
              Clipboard.setData(ClipboardData(text: result.report));
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Hisobot nusxalandi.')),
              );
            },
            child: const Icon(Icons.copy, color: Colors.white),
          ),
        ),
      ],
    );
  }
}

// --- umumiy yordamchi vidjetlar ---

Widget _sectionTitle(String text) => Padding(
      padding: const EdgeInsets.only(bottom: 10, left: 4),
      child: Text(text,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
    );

Widget _infoRow(String label, String value) => Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 5,
            child: Text(label,
                style: const TextStyle(color: AppTheme.muted, fontSize: 13)),
          ),
          Expanded(
            flex: 4,
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: const TextStyle(
                  fontWeight: FontWeight.w600, fontSize: 13),
            ),
          ),
        ],
      ),
    );

Widget _disclaimer(String text) => Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.amber.withOpacity(0.12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.amber.withOpacity(0.4)),
      ),
      child: Row(
        children: [
          const Icon(Icons.info_outline, color: Colors.amber, size: 22),
          const SizedBox(width: 10),
          Expanded(
            child: Text(text,
                style: const TextStyle(fontSize: 12, height: 1.4)),
          ),
        ],
      ),
    );
