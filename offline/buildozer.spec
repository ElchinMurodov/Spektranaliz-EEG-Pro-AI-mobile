[app]

# Ilova nomi va paketi
title = Spektranaliz EEG Pro AI
package.name = spektranalizeeg
package.domain = com.elchinmurodov

# Manba kodi shu papkada (offline/)
source.dir = .
source.include_exts = py,png,jpg,svg,ico,kv,edf,bdf,csv,txt
# eeg_engine paketi va asosiy modullar avtomatik kiritiladi (source.dir butun papka)

version = 3.0.0

# --- Talablar ---
# eeg_engine SOF PYTHON: numpy/scipy/pyedflib SHART EMAS (sof Python EDF/BDF
# parser ishlatiladi). Bu .apk ni yengil va ishonchli yig'ishni ta'minlaydi.
# Tezlik kerak bo'lsa requirements ga numpy ni qo'shish mumkin (recipe mavjud).
requirements = python3,kivy,plyer

orientation = portrait
fullscreen = 0

# --- Android ---
# Fayllarni o'qish uchun ruxsatlar
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = 1

# Ikona va boshlang'ich ekran (presplash) — ish stoli dasturi grafikasi
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png
android.presplash_color = #1B3A6B

[buildozer]

log_level = 2
warn_on_root = 1
