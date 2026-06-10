"""
charts.py — Kivy canvas asosidagi oddiy diagramma vidjetlari.

Hech qanday qo'shimcha grafik kutubxona (matplotlib va h.k.) talab qilinmaydi —
bu mobil paketlashni yengillashtiradi va ilovani kichik saqlaydi. Barcha chizish
to'g'ridan-to'g'ri Kivy `canvas` orqali amalga oshiriladi.

  - BandBarChart : 5 ritm bo'yicha nisbiy quvvat (ustunli diagramma)
  - PsdChart     : Quvvat spektral zichligi (PSD) egri chizig'i
"""

from __future__ import annotations

from typing import Dict, List

from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.widget import Widget


# EEG ritmlari uchun ranglar (RGBA, 0..1)
BAND_COLORS = {
    "delta": (0.557, 0.267, 0.678, 1),
    "theta": (0.161, 0.502, 0.725, 1),
    "alpha": (0.153, 0.682, 0.376, 1),
    "beta": (0.902, 0.494, 0.133, 1),
    "gamma": (0.753, 0.224, 0.169, 1),
}
BAND_ORDER = ["delta", "theta", "alpha", "beta", "gamma"]
BAND_LABELS = {
    "delta": "Delta", "theta": "Theta", "alpha": "Alpha",
    "beta": "Beta", "gamma": "Gamma",
}

_AXIS = (0.42, 0.45, 0.5, 1)
_GRID = (0.85, 0.87, 0.9, 1)
_ACCENT = (0.18, 0.525, 0.871, 1)


def _text_texture(text, font_size=13, bold=False, color=(0.1, 0.13, 0.19, 1)):
    label = CoreLabel(text=text, font_size=font_size, bold=bold, color=color)
    label.refresh()
    return label.texture


class BandBarChart(Widget):
    """5 ta ritm bo'yicha nisbiy quvvatni ustunli diagrammada chizadi."""

    def __init__(self, bands: Dict[str, float], **kwargs):
        super().__init__(**kwargs)
        self.bands = bands or {}
        self.bind(pos=self._redraw, size=self._redraw)

    def set_data(self, bands: Dict[str, float]):
        self.bands = bands or {}
        self._redraw()

    def _redraw(self, *_):
        self.canvas.clear()
        if not self.bands:
            return
        pad_l, pad_b, pad_t, pad_r = 44, 34, 16, 12
        x0 = self.x + pad_l
        y0 = self.y + pad_b
        w = self.width - pad_l - pad_r
        h = self.height - pad_b - pad_t
        if w <= 0 or h <= 0:
            return

        max_val = max(self.bands.values()) if self.bands else 1.0
        top = max(max_val * 1.2, 0.1)
        n = len(BAND_ORDER)
        slot = w / n
        bar_w = slot * 0.55

        with self.canvas:
            # Y o'qi panjarasi va belgilari (0%, 50%, 100% nisbatan top ga)
            for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
                gy = y0 + h * frac
                Color(*_GRID)
                Line(points=[x0, gy, x0 + w, gy], width=1)
                tex = _text_texture("%d%%" % int(top * frac * 100), font_size=11,
                                    color=_AXIS)
                Color(1, 1, 1, 1)
                Rectangle(texture=tex, pos=(self.x + 4, gy - tex.height / 2),
                          size=tex.size)

            # Ustunlar
            for i, name in enumerate(BAND_ORDER):
                val = self.bands.get(name, 0.0)
                bar_h = (val / top) * h if top else 0
                bx = x0 + i * slot + (slot - bar_w) / 2
                Color(*BAND_COLORS[name])
                Rectangle(pos=(bx, y0), size=(bar_w, bar_h))

                # Ustun ustidagi qiymat
                vtex = _text_texture("%.0f%%" % (val * 100), font_size=11, bold=True)
                Color(1, 1, 1, 1)
                Rectangle(texture=vtex,
                          pos=(bx + bar_w / 2 - vtex.width / 2, y0 + bar_h + 3),
                          size=vtex.size)

                # Pastdagi ritm nomi
                ltex = _text_texture(BAND_LABELS[name], font_size=12, bold=True)
                Color(1, 1, 1, 1)
                Rectangle(texture=ltex,
                          pos=(bx + bar_w / 2 - ltex.width / 2, self.y + 8),
                          size=ltex.size)


class PsdChart(Widget):
    """Quvvat spektral zichligi (PSD) egri chizig'ini chizadi."""

    def __init__(self, freqs: List[float], psd: List[float], **kwargs):
        super().__init__(**kwargs)
        self.freqs = freqs or []
        self.psd = psd or []
        self.bind(pos=self._redraw, size=self._redraw)

    def set_data(self, freqs: List[float], psd: List[float]):
        self.freqs = freqs or []
        self.psd = psd or []
        self._redraw()

    def _redraw(self, *_):
        self.canvas.clear()
        if len(self.freqs) < 2 or len(self.psd) < 2:
            return
        pad_l, pad_b, pad_t, pad_r = 12, 32, 14, 12
        x0 = self.x + pad_l
        y0 = self.y + pad_b
        w = self.width - pad_l - pad_r
        h = self.height - pad_b - pad_t
        if w <= 0 or h <= 0:
            return

        fmax = self.freqs[-1] if self.freqs[-1] > 0 else 1.0
        pmax = max(self.psd) if max(self.psd) > 0 else 1.0
        n = min(len(self.freqs), len(self.psd))

        pts = []
        for i in range(n):
            px = x0 + (self.freqs[i] / fmax) * w
            py = y0 + (self.psd[i] / pmax) * h
            pts.extend([px, py])

        with self.canvas:
            # Ramka va vertikal panjara (har 10 Hz)
            Color(*_GRID)
            Line(rectangle=[x0, y0, w, h], width=1)
            f = 10.0
            while f < fmax:
                gx = x0 + (f / fmax) * w
                Color(*_GRID)
                Line(points=[gx, y0, gx, y0 + h], width=1)
                tex = _text_texture("%d" % int(f), font_size=10, color=_AXIS)
                Color(1, 1, 1, 1)
                Rectangle(texture=tex, pos=(gx - tex.width / 2, self.y + 8),
                          size=tex.size)
                f += 10.0

            # PSD egri chizig'i
            Color(*_ACCENT)
            Line(points=pts, width=1.5)

            # X o'qi nomi
            xt = _text_texture("Chastota (Hz)", font_size=11, color=_AXIS)
            Color(1, 1, 1, 1)
            Rectangle(texture=xt, pos=(x0 + w / 2 - xt.width / 2, self.y - 2),
                      size=xt.size)
