# Spektranaliz EEG Pro AI — Mobil Backend (FastAPI)

Bu backend ish stoli dasturidagi **bir xil** `eeg_engine` tahlil yadrosini REST API
ko'rinishida taqdim etadi. Android/iOS ilovasi EEG faylni yuklaydi, server uni
spektral tahlil qilib, JSON natija (funksional holat, ballar, ritmlar, PSD, hisobot)
qaytaradi.

## O'rnatish va ishga tushirish

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

So'ng brauzerda `http://localhost:8000/docs` — interaktiv API hujjati (Swagger UI).

> **Telefon bilan sinash:** Telefon va kompyuter bitta Wi-Fi da bo'lsin. `--host 0.0.0.0`
> bilan ishga tushiring va mobil ilovada server manzilini kompyuteringizning lokal
> IP manziliga qo'ying (masalan `http://192.168.1.50:8000`).

## Endpointlar

| Metod | Yo'l | Tavsif |
|-------|------|--------|
| `GET` | `/` | Server haqida qisqa ma'lumot |
| `GET` | `/health` | Holat tekshiruvi (ilova ulanishni tekshiradi) |
| `GET` | `/api/states` | Aniqlanadigan 8 holat va ritm diapazonlari |
| `POST` | `/api/analyze` | EEG fayl yuklash → JSON tahlil natijasi |
| `POST` | `/api/report/html` | EEG fayl yuklash → HTML vizual hisobot |

### `POST /api/analyze` — so'rov (multipart/form-data)

| Maydon | Turi | Majburiy | Tavsif |
|--------|------|----------|--------|
| `file` | fayl | ha | EEG fayl (`.edf`, `.bdf`, `.csv`) |
| `fs` | son | yo'q | Namuna chastotasi (faqat CSV uchun), Hz |
| `target_fs` | son | yo'q | Harmonizatsiya chastotasi, Hz |
| `notch` | bool | yo'q | 50/60 Hz tarmoq filtri (standart: `true`) |
| `reader` | matn | yo'q | `auto` \| `pyedflib` \| `mne` \| `pure` |

### Javob (JSON) tuzilmasi (qisqartirilgan)

```json
{
  "app": { "name": "Spektranaliz EEG Pro AI", "version": "3.0.0" },
  "summary": { "format": "EDF", "channels": 19, "fs": 100.0, "duration_sec": 60.0 },
  "result": {
    "state": "Fokus",
    "confidence": 0.91,
    "ordered_states": ["Fokus", "Uyqusizlik", "..."],
    "scores": { "Fokus": 78.4, "...": 0.0 },
    "probabilities": { "Fokus": 0.91, "...": 0.0 },
    "atypical": []
  },
  "bands": { "delta": 0.07, "theta": 0.11, "alpha": 0.12, "beta": 0.64, "gamma": 0.06 },
  "features": { "iapf": 10.0, "engagement": 1.5, "...": 0.0 },
  "psd": { "channel": "O1", "freqs": [0.0, "..."], "psd": [0.0, "..."] },
  "report": "==== EEG SPEKTRAL TAHLIL HISOBOTI ...",
  "disclaimer": "DIQQAT: Ushbu natija TIBBIY TASHXIS EMAS ..."
}
```

## Eslatmalar

- Tahlil yadrosi (`eeg_engine`) **sof Python**da yozilgan va `numpy/scipy/pyedflib`siz
  ham ishlaydi; ular mavjud bo'lsa avtomatik tezlashadi.
- EEG — shaxsiy/tibbiy ma'lumot. Ishlab chiqarishda HTTPS, autentifikatsiya va
  ma'lumotni anonimlashtirishni qo'shing. Yuklangan fayllar tahlildan so'ng darhol
  o'chiriladi (vaqtinchalik faylda saqlanadi).
- Natija **tibbiy tashxis emas** — `disclaimer` maydoniga qarang.
