/// Backend `/api/analyze` javobini ifodalovchi model klasslari.
///
/// JSON tuzilmasi backenddagi `app/analysis.py` bilan mos keladi.

class AnalysisResult {
  final AppInfo app;
  final RecordingSummary summary;
  final ClassificationResult result;
  final Map<String, double> bands; // delta..gamma -> nisbiy quvvat (0..1)
  final Map<String, double?> features;
  final PsdCurve psd;
  final String report;
  final String disclaimer;

  AnalysisResult({
    required this.app,
    required this.summary,
    required this.result,
    required this.bands,
    required this.features,
    required this.psd,
    required this.report,
    required this.disclaimer,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    final bandsRaw = (json['bands'] as Map?) ?? {};
    final featRaw = (json['features'] as Map?) ?? {};
    return AnalysisResult(
      app: AppInfo.fromJson(_asMap(json['app'])),
      summary: RecordingSummary.fromJson(_asMap(json['summary'])),
      result: ClassificationResult.fromJson(_asMap(json['result'])),
      bands: bandsRaw.map((k, v) => MapEntry(k.toString(), _toDouble(v) ?? 0.0)),
      features: featRaw.map((k, v) => MapEntry(k.toString(), _toDouble(v))),
      psd: PsdCurve.fromJson(_asMap(json['psd'])),
      report: (json['report'] ?? '').toString(),
      disclaimer: (json['disclaimer'] ?? '').toString(),
    );
  }
}

class AppInfo {
  final String name;
  final String version;
  final String author;

  AppInfo({required this.name, required this.version, required this.author});

  factory AppInfo.fromJson(Map<String, dynamic> j) => AppInfo(
        name: (j['name'] ?? '').toString(),
        version: (j['version'] ?? '').toString(),
        author: (j['author'] ?? '').toString(),
      );
}

class RecordingSummary {
  final String? sourceFile;
  final String? format;
  final String? reader;
  final int channels;
  final List<String> channelNames;
  final double? fs;
  final double? harmonizedFs;
  final double durationSec;
  final bool calibrated;

  RecordingSummary({
    this.sourceFile,
    this.format,
    this.reader,
    required this.channels,
    required this.channelNames,
    this.fs,
    this.harmonizedFs,
    required this.durationSec,
    required this.calibrated,
  });

  factory RecordingSummary.fromJson(Map<String, dynamic> j) => RecordingSummary(
        sourceFile: j['source_file']?.toString(),
        format: j['format']?.toString(),
        reader: j['reader']?.toString(),
        channels: (j['channels'] ?? 0) is int
            ? (j['channels'] ?? 0) as int
            : int.tryParse('${j['channels']}') ?? 0,
        channelNames: (j['channel_names'] as List?)
                ?.map((e) => e.toString())
                .toList() ??
            const [],
        fs: _toDouble(j['fs']),
        harmonizedFs: _toDouble(j['harmonized_fs']),
        durationSec: _toDouble(j['duration_sec']) ?? 0.0,
        calibrated: j['calibrated'] == true,
      );
}

class ClassificationResult {
  final String state;
  final double confidence;
  final List<String> orderedStates;
  final Map<String, double> scores;
  final Map<String, double> probabilities;
  final List<String> atypical;

  ClassificationResult({
    required this.state,
    required this.confidence,
    required this.orderedStates,
    required this.scores,
    required this.probabilities,
    required this.atypical,
  });

  factory ClassificationResult.fromJson(Map<String, dynamic> j) {
    final scoresRaw = (j['scores'] as Map?) ?? {};
    final probsRaw = (j['probabilities'] as Map?) ?? {};
    return ClassificationResult(
      state: (j['state'] ?? '—').toString(),
      confidence: _toDouble(j['confidence']) ?? 0.0,
      orderedStates:
          (j['ordered_states'] as List?)?.map((e) => e.toString()).toList() ??
              const [],
      scores: scoresRaw
          .map((k, v) => MapEntry(k.toString(), _toDouble(v) ?? 0.0)),
      probabilities:
          probsRaw.map((k, v) => MapEntry(k.toString(), _toDouble(v) ?? 0.0)),
      atypical:
          (j['atypical'] as List?)?.map((e) => e.toString()).toList() ??
              const [],
    );
  }
}

class PsdCurve {
  final String channel;
  final List<double> freqs;
  final List<double> psd;

  PsdCurve({required this.channel, required this.freqs, required this.psd});

  factory PsdCurve.fromJson(Map<String, dynamic> j) => PsdCurve(
        channel: (j['channel'] ?? '').toString(),
        freqs: (j['freqs'] as List?)?.map((e) => _toDouble(e) ?? 0.0).toList() ??
            const [],
        psd: (j['psd'] as List?)?.map((e) => _toDouble(e) ?? 0.0).toList() ??
            const [],
      );
}

// --- yordamchi funksiyalar ---

Map<String, dynamic> _asMap(dynamic v) =>
    v is Map ? v.map((k, val) => MapEntry(k.toString(), val)) : <String, dynamic>{};

double? _toDouble(dynamic v) {
  if (v == null) return null;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString());
}
