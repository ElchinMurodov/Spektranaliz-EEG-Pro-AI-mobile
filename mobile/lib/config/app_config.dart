/// Ilova darajasidagi doimiy sozlamalar.
class AppConfig {
  AppConfig._();

  static const String appName = 'Spektranaliz EEG Pro AI';
  static const String appVersion = '3.0.0';
  static const String author = "Murodov Elchin O'ktamovich";

  /// Backend serverning standart manzili. Foydalanuvchi sozlamalarda
  /// o'zgartirishi mumkin (masalan kompyuterning lokal IP manzili).
  ///
  /// Eslatma: Android emulyatorida hostdagi serverga `10.0.2.2` orqali
  /// murojaat qilinadi; iOS simulyatorida `localhost` ishlaydi.
  static const String defaultBaseUrl = 'http://10.0.2.2:8000';

  /// Tanlash mumkin bo'lgan fayl kengaytmalari.
  static const List<String> allowedExtensions = ['edf', 'bdf', 'csv'];

  /// So'rovlar uchun kutish vaqti.
  static const Duration requestTimeout = Duration(seconds: 120);
}
