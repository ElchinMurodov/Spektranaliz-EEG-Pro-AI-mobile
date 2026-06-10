import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';
import '../models/analysis_result.dart';

/// Backend bilan ishlash istisnosi (tushunarli xabar bilan).
class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}

/// FastAPI backend bilan aloqa qiluvchi xizmat.
class ApiService {
  final String baseUrl;

  ApiService(this.baseUrl);

  Uri _uri(String path) => Uri.parse('$baseUrl$path');

  /// Server ishlayotganini tekshiradi (`GET /health`).
  Future<bool> checkHealth() async {
    try {
      final resp = await http
          .get(_uri('/health'))
          .timeout(const Duration(seconds: 10));
      if (resp.statusCode != 200) return false;
      final body = jsonDecode(resp.body) as Map<String, dynamic>;
      return body['status'] == 'ok';
    } catch (_) {
      return false;
    }
  }

  /// EEG faylni serverga yuborib, tahlil natijasini oladi (`POST /api/analyze`).
  ///
  /// [filePath] — qurilmadagi fayl yo'li.
  /// [fileName] — asl fayl nomi (server javobida ko'rsatiladi).
  Future<AnalysisResult> analyzeFile({
    required String filePath,
    required String fileName,
    double? fs,
    double? targetFs,
    bool notch = true,
    String reader = 'auto',
  }) async {
    final request = http.MultipartRequest('POST', _uri('/api/analyze'));
    request.files
        .add(await http.MultipartFile.fromPath('file', filePath, filename: fileName));
    request.fields['notch'] = notch.toString();
    request.fields['reader'] = reader;
    if (fs != null) request.fields['fs'] = fs.toString();
    if (targetFs != null) request.fields['target_fs'] = targetFs.toString();

    http.StreamedResponse streamed;
    try {
      streamed = await request.send().timeout(AppConfig.requestTimeout);
    } catch (e) {
      throw ApiException(
          "Serverga ulanib bo'lmadi. Manzil va tarmoqni tekshiring.\n($e)");
    }

    final resp = await http.Response.fromStream(streamed);
    if (resp.statusCode == 200) {
      final json = jsonDecode(utf8.decode(resp.bodyBytes)) as Map<String, dynamic>;
      return AnalysisResult.fromJson(json);
    }

    // Xato xabarini serverdan ajratib olamiz
    String detail;
    try {
      final body = jsonDecode(utf8.decode(resp.bodyBytes));
      detail = (body is Map && body['detail'] != null)
          ? body['detail'].toString()
          : resp.body;
    } catch (_) {
      detail = resp.body;
    }
    throw ApiException('Xato (${resp.statusCode}): $detail');
  }

  /// HTML hisobot manzilini qaytaradi (WebView/brauzer uchun — kelajakda).
  String htmlReportUrl() => '$baseUrl/api/report/html';
}
