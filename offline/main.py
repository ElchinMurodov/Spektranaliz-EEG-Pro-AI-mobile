"""
main.py — Spektranaliz EEG Pro AI (TO'LIQ OFLAYN, Kivy).

Bu Android/iOS ilovasi EEG faylni TELEFONNING O'ZIDA, INTERNETSIZ tahlil qiladi.
Server, tarmoq yoki internet umuman talab qilinmaydi — ma'lumot qurilmadan
chiqmaydi (maxfiylik uchun muhim). Tahlil yadrosi (`eeg_engine`) sof Python.

Ishga tushirish (ish stolida sinash uchun):
    pip install kivy
    python main.py

Android (.apk) / iOS uchun yig'ish: README.md ga qarang.
"""

from __future__ import annotations

import os
import threading
import traceback

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.utils import get_color_from_hex, platform

from analyze import analyze
from charts import BandBarChart, PsdChart

# --- ranglar ---
PRIMARY = get_color_from_hex("#1B3A6B")
ACCENT = get_color_from_hex("#2E86DE")
BG = get_color_from_hex("#F4F6FA")
INK = get_color_from_hex("#1A2230")
MUTED = get_color_from_hex("#6B7280")

ALLOWED = (".edf", ".bdf", ".csv")

# --- grafik resurslar (ish stoli dasturi bilan bir xil dizayn) ---
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
LOGO_PATH = os.path.join(ASSETS, "logo.png")
LOGO_DARK_PATH = os.path.join(ASSETS, "logo_dark.png")
ICON_PATH = os.path.join(ASSETS, "icon.png")
BACKGROUND_PATH = os.path.join(ASSETS, "background.jpg")


def confidence_color(c: float):
    if c >= 0.75:
        return get_color_from_hex("#27AE60")
    if c >= 0.5:
        return get_color_from_hex("#E67E22")
    return get_color_from_hex("#C0392B")


def _bg(widget, rgba):
    """Vidjet orqa foniga rang beradi (canvas.before)."""
    from kivy.graphics import Color, Rectangle
    with widget.canvas.before:
        Color(*rgba)
        rect = Rectangle(pos=widget.pos, size=widget.size)

    def _update(*_):
        rect.pos = widget.pos
        rect.size = widget.size

    widget.bind(pos=_update, size=_update)
    return rect


def _bg_image(widget, source, overlay=(1, 1, 1, 0.86)):
    """Vidjet ortiga EEG-spektr fonini joylaydi va ustiga yengil oqartiruvchi
    qatlam qo'yadi (kontent o'qilishi uchun). Ish stoli dasturidagi fon dizayni."""
    from kivy.graphics import Color, Rectangle
    if not os.path.exists(source):
        # Fon rasmi topilmasa — oddiy tekis rangga qaytamiz
        return _bg(widget, BG)
    with widget.canvas.before:
        Color(1, 1, 1, 1)
        img_rect = Rectangle(source=source, pos=widget.pos, size=widget.size)
        Color(*overlay)
        ov_rect = Rectangle(pos=widget.pos, size=widget.size)

    def _update(*_):
        img_rect.pos = widget.pos
        img_rect.size = widget.size
        ov_rect.pos = widget.pos
        ov_rect.size = widget.size

    widget.bind(pos=_update, size=_update)
    return img_rect


class Card(BoxLayout):
    """Oq fonli, ichki bo'shliqli oddiy karta."""

    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", dp(14))
        kwargs.setdefault("spacing", dp(6))
        kwargs.setdefault("size_hint_y", None)
        super().__init__(**kwargs)
        _bg(self, (1, 1, 1, 1))
        self.bind(minimum_height=self.setter("height"))


def info_row(label: str, value: str) -> BoxLayout:
    row = BoxLayout(size_hint_y=None, height=dp(26), spacing=dp(8))
    lab = Label(text=label, color=MUTED, font_size="13sp", halign="left",
                valign="middle", size_hint_x=0.6)
    val = Label(text=str(value), color=INK, font_size="13sp", bold=True,
                halign="right", valign="middle", size_hint_x=0.4)
    lab.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
    val.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
    row.add_widget(lab)
    row.add_widget(val)
    return row


class SpektranalizApp(App):
    title = "Spektranaliz EEG Pro AI"
    # Ilova/oyna ikonkasi (ish stoli dasturi ikonkasi bilan bir xil)
    icon = ICON_PATH

    def build(self):
        Window.clearcolor = BG
        self.selected_path = None
        self.selected_name = None

        root = BoxLayout(orientation="vertical")
        # EEG-spektr foni (ish stoli dasturidagidek), ustida yengil oqartiruvchi qatlam
        _bg_image(root, BACKGROUND_PATH)

        # --- yuqori panel (AppBar): logotip + nom ---
        bar = BoxLayout(size_hint_y=None, height=dp(56), padding=(dp(12), dp(6)),
                        spacing=dp(10))
        _bg(bar, PRIMARY)
        if os.path.exists(LOGO_DARK_PATH):
            bar.add_widget(KivyImage(source=LOGO_DARK_PATH, size_hint_x=None,
                                     width=dp(132), allow_stretch=True,
                                     keep_ratio=True))
        else:
            bar.add_widget(Label(text="[b]Spektranaliz EEG Pro AI[/b]",
                                 markup=True, color=(1, 1, 1, 1),
                                 font_size="18sp", halign="left",
                                 valign="middle"))
        bar.add_widget(Label())  # bo'sh joy (logotipни chapga suradi)
        root.add_widget(bar)

        # --- asosiy kontent (ScrollView) ---
        self.scroll = ScrollView()
        self.container = BoxLayout(orientation="vertical", padding=dp(16),
                                   spacing=dp(14), size_hint_y=None)
        self.container.bind(minimum_height=self.container.setter("height"))
        self.scroll.add_widget(self.container)
        root.add_widget(self.scroll)

        self._build_home()
        return root

    # ---------------- ASOSIY (HOME) ----------------

    def _build_home(self):
        self.container.clear_widgets()

        intro = Card()
        # Logotip (ish stoli dasturi bilan bir xil) — oq karta ustida
        if os.path.exists(LOGO_PATH):
            intro.add_widget(KivyImage(source=LOGO_PATH, size_hint_y=None,
                                       height=dp(72), allow_stretch=True,
                                       keep_ratio=True))
        intro.add_widget(Label(
            text="Sportchining EEG signallarini spektral tahlil qilish",
            color=INK, font_size="16sp", bold=True, halign="center",
            valign="middle", size_hint_y=None, height=dp(48),
            text_size=(Window.width - dp(60), None)))
        intro.add_widget(Label(text="To'liq oflayn — internet talab qilinmaydi",
                               color=MUTED, font_size="12sp", size_hint_y=None,
                               height=dp(20)))
        self.container.add_widget(intro)

        # Fayl tanlash kartasi
        pick_card = Card()
        self.file_label = Label(
            text="EEG faylni tanlang\n[size=12][color=6B7280]EDF · EDF+ · BDF · BDF+ · CSV[/color][/size]",
            markup=True, color=INK, font_size="15sp", halign="center",
            valign="middle", size_hint_y=None, height=dp(52))
        self.file_label.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        pick_card.add_widget(self.file_label)
        pick_btn = Button(text="Fayl tanlash", size_hint_y=None, height=dp(48),
                          background_normal="", background_color=ACCENT,
                          color=(1, 1, 1, 1), font_size="15sp", bold=True)
        pick_btn.bind(on_release=lambda *_: self._open_chooser())
        pick_card.add_widget(pick_btn)
        self.container.add_widget(pick_card)

        # Tahlil tugmasi
        self.analyze_btn = Button(text="Natijani olish", size_hint_y=None,
                                  height=dp(52), background_normal="",
                                  background_color=PRIMARY, color=(1, 1, 1, 1),
                                  font_size="16sp", bold=True, disabled=True)
        self.analyze_btn.bind(on_release=lambda *_: self._run_analysis())
        self.container.add_widget(self.analyze_btn)

        self.status = Label(text="", color=MUTED, font_size="13sp",
                            size_hint_y=None, height=dp(24))
        self.container.add_widget(self.status)

        # Ogohlantirish
        warn = Card()
        _bg(warn, get_color_from_hex("#FFF7E6"))
        warn.add_widget(Label(
            text="[b]Eslatma:[/b] Natija TIBBIY TASHXIS EMAS. U faqat EEG "
                 "signalining funksional holat ko'rsatkichlarini ifodalaydi.",
            markup=True, color=INK, font_size="12sp", halign="left",
            valign="middle", size_hint_y=None, height=dp(60),
            text_size=(Window.width - dp(60), None)))
        self.container.add_widget(warn)

    # ---------------- FAYL TANLASH ----------------

    def _open_chooser(self):
        # 1) Mobil qurilmada plyer (tizim fayl tanlagichi) bo'lsa — undan foydalanamiz
        try:
            from plyer import filechooser
            filechooser.open_file(on_selection=self._on_native_selection,
                                  filters=[["EEG", "*.edf", "*.bdf", "*.csv"]])
            return
        except Exception:
            pass
        # 2) Aks holda Kivy ichki fayl tanlagichi (popup)
        self._open_kivy_chooser()

    def _on_native_selection(self, selection):
        if selection:
            self._set_file(selection[0])

    def _open_kivy_chooser(self):
        start = "/sdcard" if platform == "android" else "~"
        import os
        start = os.path.expanduser(start)
        if not os.path.isdir(start):
            start = os.path.expanduser("~")

        box = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        chooser = FileChooserListView(path=start,
                                      filters=["*.edf", "*.bdf", "*.csv",
                                               "*.EDF", "*.BDF", "*.CSV"])
        box.add_widget(chooser)
        btns = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        cancel = Button(text="Bekor qilish")
        ok = Button(text="Tanlash", background_normal="", background_color=ACCENT,
                    color=(1, 1, 1, 1), bold=True)
        btns.add_widget(cancel)
        btns.add_widget(ok)
        box.add_widget(btns)

        popup = Popup(title="EEG faylni tanlang", content=box,
                      size_hint=(0.95, 0.9))
        cancel.bind(on_release=popup.dismiss)

        def _choose(*_):
            if chooser.selection:
                self._set_file(chooser.selection[0])
                popup.dismiss()

        ok.bind(on_release=_choose)
        popup.open()

    def _set_file(self, path):
        import os
        self.selected_path = path
        self.selected_name = os.path.basename(path)
        self.file_label.text = (
            "[b]%s[/b]\n[size=12][color=6B7280]Tahlilga tayyor[/color][/size]"
            % self.selected_name)
        self.analyze_btn.disabled = False
        self.status.text = ""

    # ---------------- TAHLIL ----------------

    def _run_analysis(self):
        if not self.selected_path:
            return
        self.analyze_btn.disabled = True
        self.analyze_btn.text = "Tahlil qilinmoqda..."
        self.status.text = "Iltimos kuting — signal qayta ishlanmoqda."
        # Og'ir hisoblashni alohida oqimda bajaramiz (UI qotib qolmasin)
        threading.Thread(target=self._analyze_worker, daemon=True).start()

    def _analyze_worker(self):
        try:
            result = analyze(self.selected_path)
            result["summary"]["source_file"] = self.selected_name
            Clock.schedule_once(lambda *_: self._show_result(result), 0)
        except Exception as exc:
            # Python 3'da 'exc' except blokidan keyin o'chadi — shu sababli
            # qiymatlarni lambda chaqirilishidan oldin mahalliy o'zgaruvchiga olamiz.
            msg = str(exc)
            tb = traceback.format_exc()
            Clock.schedule_once(lambda *_: self._show_error(msg, tb), 0)

    def _show_error(self, msg, tb=""):
        self.analyze_btn.disabled = False
        self.analyze_btn.text = "Natijani olish"
        self.status.text = ""
        box = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        box.add_widget(Label(text="Tahlil xatosi:\n%s" % msg, color=INK,
                             halign="center", valign="middle"))
        close = Button(text="Yopish", size_hint_y=None, height=dp(44))
        box.add_widget(close)
        popup = Popup(title="Xatolik", content=box, size_hint=(0.9, 0.5))
        close.bind(on_release=popup.dismiss)
        popup.open()

    # ---------------- NATIJA EKRANI ----------------

    def _show_result(self, result):
        self.analyze_btn.disabled = False
        self.analyze_btn.text = "Natijani olish"
        self.status.text = ""

        self.container.clear_widgets()
        self.scroll.scroll_y = 1

        # Orqaga tugmasi
        back = Button(text="< Orqaga (yangi fayl)", size_hint_y=None,
                      height=dp(40), background_normal="",
                      background_color=MUTED, color=(1, 1, 1, 1))
        back.bind(on_release=lambda *_: self._build_home())
        self.container.add_widget(back)

        panel = TabbedPanel(do_default_tab=False, size_hint_y=None,
                            height=dp(560), tab_width=dp(90))
        panel.add_widget(self._tab_overview(result))
        panel.add_widget(self._tab_bands(result))
        panel.add_widget(self._tab_spectrum(result))
        panel.add_widget(self._tab_report(result))
        self.container.add_widget(panel)

    def _scroll_section(self, build_fn):
        sv = ScrollView()
        col = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(12),
                        size_hint_y=None)
        col.bind(minimum_height=col.setter("height"))
        build_fn(col)
        sv.add_widget(col)
        return sv

    def _tab_overview(self, result):
        item = TabbedPanelItem(text="Umumiy")
        r = result["result"]
        s = result["summary"]

        def build(col):
            # Yakuniy holat kartasi
            hero = Card()
            _bg(hero, PRIMARY)
            hero.add_widget(Label(text="YAKUNIY BAHOLANGAN HOLAT",
                                 color=(1, 1, 1, 0.7), font_size="11sp",
                                 size_hint_y=None, height=dp(20)))
            hero.add_widget(Label(text="[b]%s[/b]" % r["state"], markup=True,
                                 color=(1, 1, 1, 1), font_size="24sp",
                                 size_hint_y=None, height=dp(40)))
            conf = r["confidence"] * 100
            hero.add_widget(Label(text="Ishonch: %.1f%%" % conf,
                                 color=confidence_color(r["confidence"]),
                                 bold=True, font_size="14sp",
                                 size_hint_y=None, height=dp(26)))
            col.add_widget(hero)

            # Holatlar ehtimolligi
            col.add_widget(Label(text="[b]Holatlar bo'yicha ehtimollik[/b]",
                                markup=True, color=INK, font_size="15sp",
                                halign="left", size_hint_y=None, height=dp(24),
                                text_size=(Window.width - dp(56), None)))
            probs_card = Card()
            for st in r["ordered_states"]:
                p = r["probabilities"].get(st, 0.0)
                probs_card.add_widget(self._prob_row(st, p, st == r["state"]))
            col.add_widget(probs_card)

            # Atipik belgilar
            if r["atypical"]:
                warn = Card()
                _bg(warn, get_color_from_hex("#FDEBD0"))
                warn.add_widget(Label(text="[b]Atipik naqsh belgilari[/b]",
                                     markup=True, color=INK, font_size="14sp",
                                     size_hint_y=None, height=dp(22)))
                for a in r["atypical"]:
                    lab = Label(text="• %s" % a, color=INK, font_size="12sp",
                                halign="left", valign="top", size_hint_y=None,
                                text_size=(Window.width - dp(72), None))
                    lab.bind(texture_size=lambda w, v: setattr(w, "height", v[1]))
                    warn.add_widget(lab)
                col.add_widget(warn)

            # Yozuv ma'lumotlari
            col.add_widget(Label(text="[b]Yozuv ma'lumotlari[/b]", markup=True,
                                color=INK, font_size="15sp", halign="left",
                                size_hint_y=None, height=dp(24),
                                text_size=(Window.width - dp(56), None)))
            meta = Card()
            meta.add_widget(info_row("Fayl", s.get("source_file") or "—"))
            meta.add_widget(info_row("Format", s.get("format") or "—"))
            meta.add_widget(info_row("Kanallar soni", s.get("channels")))
            meta.add_widget(info_row(
                "Namuna chastotasi",
                "%s Hz" % s.get("fs") if s.get("fs") else "turlicha"))
            meta.add_widget(info_row("Davomiyligi",
                                     "%.1f s" % s.get("duration_sec", 0.0)))
            col.add_widget(meta)

        item.add_widget(self._scroll_section(build))
        return item

    def _prob_row(self, state, prob, is_top):
        from kivy.graphics import Color, Rectangle
        wrap = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(40),
                         spacing=dp(3))
        top = BoxLayout(size_hint_y=None, height=dp(20))
        name = Label(text=state, color=PRIMARY if is_top else INK,
                     bold=is_top, font_size="13sp", halign="left", valign="middle")
        pct = Label(text="%.1f%%" % (prob * 100),
                    color=PRIMARY if is_top else MUTED, bold=is_top,
                    font_size="13sp", halign="right", valign="middle")
        name.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        pct.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        top.add_widget(name)
        top.add_widget(pct)
        wrap.add_widget(top)

        track = BoxLayout(size_hint_y=None, height=dp(8))
        with track.canvas.before:
            Color(0.88, 0.89, 0.92, 1)
            bg_rect = Rectangle(pos=track.pos, size=track.size)
            Color(*(ACCENT if is_top else (MUTED[0], MUTED[1], MUTED[2], 0.55)))
            fg_rect = Rectangle(pos=track.pos, size=(0, dp(8)))

        def _upd(*_):
            bg_rect.pos = track.pos
            bg_rect.size = track.size
            fg_rect.pos = track.pos
            fg_rect.size = (track.width * max(0.0, min(1.0, prob)), track.height)

        track.bind(pos=_upd, size=_upd)
        wrap.add_widget(track)
        return wrap

    def _tab_bands(self, result):
        item = TabbedPanelItem(text="Ritmlar")

        def build(col):
            col.add_widget(Label(text="[b]Ritmlar bo'yicha nisbiy quvvat[/b]",
                                markup=True, color=INK, font_size="15sp",
                                halign="left", size_hint_y=None, height=dp(24),
                                text_size=(Window.width - dp(56), None)))
            chart_card = Card(height=dp(240), size_hint_y=None)
            chart = BandBarChart(bands=result["bands"], size_hint_y=None,
                                 height=dp(210))
            chart_card.add_widget(chart)
            col.add_widget(chart_card)

            col.add_widget(Label(text="[b]Spektral belgilar[/b]", markup=True,
                                color=INK, font_size="15sp", halign="left",
                                size_hint_y=None, height=dp(24),
                                text_size=(Window.width - dp(56), None)))
            labels = {
                "iapf": "iAPF (alfa cho'qqisi), Hz",
                "dominant_frequency": "Dominant chastota, Hz",
                "spectral_edge_95": "Spektral chegara (95%), Hz",
                "spectral_entropy": "Spektral entropiya",
                "engagement": "Engagement indeksi",
                "ratio_alpha_beta": "Alpha/Beta nisbati",
                "ratio_theta_beta": "Theta/Beta nisbati",
                "ratio_theta_alpha": "Theta/Alpha nisbati",
                "faa": "Frontal alfa asimmetriyasi (FAA)",
                "fmt": "Frontal-median teta (FMT)",
            }
            feat_card = Card()
            for key, lab in labels.items():
                v = result["features"].get(key)
                feat_card.add_widget(info_row(
                    lab, "—" if v is None else "%.3f" % v))
            col.add_widget(feat_card)

        item.add_widget(self._scroll_section(build))
        return item

    def _tab_spectrum(self, result):
        item = TabbedPanelItem(text="Spektr")
        psd = result["psd"]

        def build(col):
            col.add_widget(Label(
                text="[b]Quvvat spektral zichligi (PSD)[/b]\n"
                     "[size=12][color=6B7280]Vakil kanal: %s — Welch usuli[/color][/size]"
                     % psd.get("channel", "—"),
                markup=True, color=INK, font_size="15sp", halign="left",
                size_hint_y=None, height=dp(44),
                text_size=(Window.width - dp(56), None)))
            chart_card = Card(height=dp(280), size_hint_y=None)
            chart = PsdChart(freqs=psd.get("freqs", []), psd=psd.get("psd", []),
                             size_hint_y=None, height=dp(250))
            chart_card.add_widget(chart)
            col.add_widget(chart_card)
            note = Label(
                text="PSD egri chizig'i signal quvvatining chastotalar bo'yicha "
                     "taqsimotini ko'rsatadi. Cho'qqilar dominant ritmlarga mos keladi.",
                color=MUTED, font_size="12sp", halign="left", valign="top",
                size_hint_y=None, text_size=(Window.width - dp(56), None))
            note.bind(texture_size=lambda w, v: setattr(w, "height", v[1]))
            col.add_widget(note)

        item.add_widget(self._scroll_section(build))
        return item

    def _tab_report(self, result):
        item = TabbedPanelItem(text="Hisobot")
        sv = ScrollView()
        lab = Label(text=result["report"], color=INK, font_size="11.5sp",
                    font_name="RobotoMono-Regular" if self._mono_available() else "Roboto",
                    halign="left", valign="top", size_hint_y=None, padding=(dp(12), dp(12)))

        def _resize(*_):
            lab.text_size = (self.scroll.width - dp(24), None)
            lab.height = lab.texture_size[1] + dp(24)

        lab.bind(texture_size=_resize)
        Clock.schedule_once(_resize, 0)
        sv.add_widget(lab)
        item.add_widget(sv)
        return item

    @staticmethod
    def _mono_available():
        try:
            from kivy.core.text import LabelBase
            return "RobotoMono-Regular" in LabelBase._fonts
        except Exception:
            return False


if __name__ == "__main__":
    # Android'da fayllarni o'qish uchun ruxsat so'rash
    if platform == "android":
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ])
        except Exception:
            pass
    SpektranalizApp().run()
