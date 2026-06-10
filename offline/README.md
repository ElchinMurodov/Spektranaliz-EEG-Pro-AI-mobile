# Spektranaliz EEG Pro AI — To'liq OFLAYN (Android / iOS)

EEG faylni **telefonning o'zida, internetsiz** spektral tahlil qiluvchi mobil
ilova. Server, tarmoq yoki internet **umuman talab qilinmaydi** — ma'lumot
qurilmadan chiqmaydi (maxfiylik uchun muhim afzallik).

Texnologiya: **[Kivy](https://kivy.org)** (Python). Tahlil yadrosi (`eeg_engine`)
ish stoli dasturi bilan **aynan bir xil** va **sof Python**da — shu sababli uni
to'g'ridan-to'g'ri qurilmaga paketlash mumkin.

> **Versiya:** 3.0.0 · **Muallif:** Murodov Elchin O'ktamovich

---

## Online (server) variantdan farqi

| | Online (`../mobile`) | **Oflayn (bu papka)** |
|---|---|---|
| Internet | Kerak (FastAPI server) | **Kerak emas** |
| Hisoblash | Serverda | **Telefonda** |
| Maxfiylik | Ma'lumot serverga boradi | **Ma'lumot qurilmadan chiqmaydi** |
| Texnologiya | Flutter + FastAPI | Kivy (sof Python) |

---

## Tuzilma
```
offline/
├── main.py             # Kivy ilova (UI + mantiq)
├── analyze.py          # eeg_engine -> ekran uchun dict (oflayn)
├── charts.py           # canvas asosidagi diagrammalar (ritm, PSD)
├── eeg_engine/         # tahlil yadrosi (sof Python, ish stoli bilan bir xil)
├── buildozer.spec      # Android (.apk/.aab) yig'ish konfiguratsiyasi
├── requirements-dev.txt# ish stolida sinash uchun
└── README.md
```

## 1. Ish stolida sinash (Linux/macOS/Windows)
```bash
cd offline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python main.py
```
"Fayl tanlash" → EEG fayl (EDF/BDF/CSV) → "Natijani olish".

## 2. Android (.apk / .aab) — Buildozer

Buildozer **Linux** (yoki WSL2 / macOS) da ishlaydi.

```bash
pip install buildozer cython
sudo apt-get install -y openjdk-17-jdk autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev

cd offline
buildozer android debug          # natija: bin/*.apk
# Do'kon uchun (imzolangan .aab):
# buildozer android release
```
APK ni telefonga o'tkazib o'rnating. Birinchi yig'ish uzoq davom etadi
(SDK/NDK yuklanadi).

> **Eslatma:** `buildozer.spec` da `requirements = python3,kivy,plyer`. `eeg_engine`
> sof Python bo'lgani uchun `numpy/scipy` **shart emas** — bu yig'ishni yengil va
> ishonchli qiladi. Tezlik kerak bo'lsa `numpy` ni qo'shing.

## 2b. ⭐ Avtomatik .apk — GitHub Actions (kompyuterga hech narsa o'rnatmasdan)

Repozitoriyda `.github/workflows/build-apk.yml` workflow'i bor. U `.apk` ni
**GitHub serverlarida avtomatik yig'adi** — sizning kompyuteringizda Buildozer,
Android SDK/NDK o'rnatish shart emas.

**Qanday ishlatish:**
1. GitHub'da repozitoriyning **Actions** bo'limiga o'ting.
2. **"Build Android APK (offline)"** workflow'ini tanlang → **Run workflow**
   (yoki `offline/` papkasiga har qanday o'zgarish `main` ga push qilinsa, o'zi ishga tushadi).
3. Yig'ish tugagach (~15-30 daqiqa), o'sha ish sahifasining pastidagi
   **Artifacts → `Spektranaliz-EEG-Pro-AI-apk`** ni yuklab oling. Ichida `.apk` bor.
4. `.apk` ni Android telefoniga o'tkazib o'rnating ("Noma'lum manbalar" ruxsatini yoqing).

**Reliz (Release) bilan:** `v` bilan boshlanadigan teg push qilsangiz (masalan
`v3.0.0`), `.apk` avtomatik **GitHub Release** ga biriktiriladi:
```bash
git tag v3.0.0
git push origin v3.0.0
```

## 3. iOS (.ipa) — kivy-ios

iOS faqat **macOS + Xcode** da yig'iladi.

```bash
pip install kivy-ios
toolchain build python3 kivy
toolchain create Spektranaliz /path/to/offline
open Spektranaliz-ios/Spektranaliz.xcodeproj
```
So'ng Xcode da o'z Apple Developer hisobingiz bilan imzolab, qurilmaga yoki
App Store Connect ga yuboring. `plyer` iOS fayl tanlagichini qo'llab-quvvatlaydi.

## Maxfiylik va eslatma
- Bu variantda EEG ma'lumoti **qurilmadan chiqmaydi** — maxfiylik bo'yicha eng
  kuchli yechim.
- Natija **TIBBIY TASHXIS EMAS** — u faqat EEG signalining funksional holat
  ko'rsatkichlarini ifodalaydi. Yakuniy talqin malakali mutaxassis tomonidan
  amalga oshiriladi.
