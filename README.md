# Spektranaliz EEG Pro AI — Mobil (Android / iOS)

**Sportchining Elektroensefalografik (EEG) signallarini spektral tahlil qilish** —
mobil ilova (Android va iOS).

Ushbu loyiha ish stoli dasturi
[Spektranaliz-EEG-Pro-AI](https://github.com/ElchinMurodov/Spektranaliz-EEG-Pro-AI)
ning **bir xil tahlil yadrosini** (`eeg_engine`) qayta ishlatadi va uni telefon
uchun **klient-server** arxitekturasida taqdim etadi.

> **Versiya:** 3.0.0 · **Muallif:** Murodov Elchin O'ktamovich

---

## Arxitektura

```
┌──────────────────────────┐      HTTPS / REST (JSON)      ┌──────────────────────────┐
│   Flutter ilova          │  ── EEG fayl (EDF/BDF/CSV) ─▶ │   FastAPI backend        │
│   (Android + iOS)        │                               │   + eeg_engine (yadro)   │
│   - fayl tanlash         │  ◀── tahlil natijasi (JSON) ─ │   DSP · Welch PSD ·       │
│   - holat, ritm, PSD,    │                               │   belgilar · klassif.    │
│     hisobot              │                               └──────────────────────────┘
└──────────────────────────┘
```

**Nega klient-server?**
- Og'ir hisoblashlar (FFT, Welch PSD, belgilar, klassifikatsiya) serverda — telefon
  resurslari tejaladi, eski qurilmalarda ham ishlaydi.
- Bitta backend Android **va** iOS ga bir xil natijani beradi (izchillik).
- Tahlil yadrosi (`eeg_engine`) ish stoli versiyasi bilan **aynan bir xil** —
  natijalar mos keladi (dissertatsiya uchun muhim).

---

## Tuzilma

```
Spektranaliz-EEG-Pro-AI-mobile/
├── backend/                 # FastAPI server (Python)
│   ├── app/
│   │   ├── main.py          # REST endpointlar
│   │   └── analysis.py      # eeg_engine -> mobil JSON
│   ├── eeg_engine/          # tahlil yadrosi (ish stolidan, sof Python)
│   ├── requirements.txt
│   └── README.md            # backendni ishga tushirish
└── mobile/                  # Flutter ilova (Android + iOS)
    ├── lib/
    │   ├── main.dart
    │   ├── config/          # sozlamalar (server manzili)
    │   ├── models/          # JSON model klasslari
    │   ├── services/        # API va sozlama xizmatlari
    │   ├── screens/         # asosiy · natija · sozlamalar
    │   ├── widgets/         # diagrammalar (ritm, PSD), holat ro'yxati
    │   └── theme/
    ├── pubspec.yaml
    └── SETUP.md             # Android/iOS yig'ish bo'yicha ko'rsatmalar
```

---

## Tezkor boshlash

### 1. Backend (server)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Batafsil: [`backend/README.md`](backend/README.md).

### 2. Mobil ilova
```bash
cd mobile
flutter create . --org com.elchinmurodov --project-name spektranaliz_eeg_pro_ai --platforms=android,ios
flutter pub get
flutter run
```
Internet ruxsati va HTTP sozlamalari: [`mobile/SETUP.md`](mobile/SETUP.md).

Ilovada **Sozlamalar** orqali server manzilini kiriting va "Ulanishni tekshirish"
tugmasi bilan tasdiqlang.

---

## Imkoniyatlar
- EEG fayl tanlash: **EDF / EDF+ / BDF / BDF+ / CSV**
- 8 funksional holatni aniqlash: Normal, Fokus, Charchoq, Uyquga moyillik,
  Uyqusizlik, Qo'zg'alish/Xayojonlanish, Stress, Meditativ
- Ritmlar bo'yicha nisbiy quvvat diagrammasi (Delta, Theta, Alpha, Beta, Gamma)
- Quvvat spektral zichligi (PSD) egri chizig'i (Welch usuli)
- Spektral belgilar: iAPF, FAA, FMT, engagement, dominant chastota, spektral
  chegara, entropiya, nisbatlar
- To'liq matnli hisobot (nusxalash mumkin)
- Atipik naqsh ogohlantirishlari

---

## Maxfiylik va muhim eslatma
- EEG — **shaxsiy/tibbiy ma'lumot**. Ishlab chiqarishda HTTPS, autentifikatsiya
  va ma'lumotni anonimlashtirishni qo'shing. Backend yuklangan faylni tahlildan
  so'ng **darhol o'chiradi**.
- Natija **TIBBIY TASHXIS EMAS** — u faqat EEG signalining funksional holat
  ko'rsatkichlarini (spektral indekslarni) ifodalaydi. Yakuniy talqin malakali
  mutaxassis (nevrolog/EEG shifokori) tomonidan amalga oshiriladi.
