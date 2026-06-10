# Mobil ilovani yig'ish (Android va iOS)

Bu papkada Flutter ilovasining **manba kodi** (`lib/`, `pubspec.yaml`, `test/`)
tayyor. Platforma papkalari (`android/`, `ios/`) repozitoriyga kiritilmagan —
ularni bir buyruq bilan hosil qilasiz. Bu standart Flutter amaliyoti.

## 0. Talablar
- [Flutter SDK](https://docs.flutter.dev/get-started/install) (3.x), `flutter doctor` muammosiz
- Android uchun: Android Studio + SDK
- iOS uchun: macOS + Xcode (iOS faqat macOS da yig'iladi)

## 1. Platforma papkalarini hosil qilish
`mobile/` ichida quyidagini ishga tushiring. `flutter create` **mavjud**
fayllarni (bizning `lib/`, `pubspec.yaml`) o'chirmaydi, faqat yetishmayotgan
platforma papkalarini qo'shadi:

```bash
cd mobile
flutter create . --org com.elchinmurodov --project-name spektranaliz_eeg_pro_ai --platforms=android,ios
flutter pub get
```

## 2. Internet ruxsati va HTTP (mahalliy server uchun)

Mahalliy backend `http://` (shifrlanmagan) bo'lgani uchun ikkala platformada
ham ruxsat qo'shish kerak. Ishlab chiqarishda (production) HTTPS ishlating.

### Android — `android/app/src/main/AndroidManifest.xml`
`<manifest>` ichiga (eng yuqoriga) INTERNET ruxsatini, `<application>` tegiga
esa `usesCleartextTraffic` ni qo'shing:

```xml
<manifest ...>
    <uses-permission android:name="android.permission.INTERNET"/>
    <application
        android:usesCleartextTraffic="true"
        ... >
```

### iOS — `ios/Runner/Info.plist`
`<dict>` ichiga quyidagini qo'shing (mahalliy HTTP ga ruxsat):

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

> `file_picker` paketi qo'shimcha ruxsat talab qilmaydi (tizim fayl tanlagichidan
> foydalanadi).

## 3. Ishga tushirish

Avval backendni ishga tushiring (`../backend/README.md` ga qarang), so'ng:

```bash
flutter run
```

Ilovada **Sozlamalar** (yuqori o'ngdagi tishli belgi) orqali server manzilini
kiriting:
- Android emulyatori: `http://10.0.2.2:8000`
- iOS simulyatori: `http://localhost:8000`
- Haqiqiy qurilma: kompyuteringizning lokal IP (masalan `http://192.168.1.50:8000`)

"Ulanishni tekshirish" tugmasi bilan aloqani tasdiqlang.

## 4. Relizga yig'ish

```bash
flutter build apk --release        # Android APK
flutter build appbundle --release  # Google Play uchun .aab
flutter build ios --release        # iOS (macOS + Xcode kerak)
```
