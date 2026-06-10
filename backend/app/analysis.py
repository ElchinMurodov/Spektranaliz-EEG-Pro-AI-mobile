"""
analysis.py — `eeg_engine` yadrosini mobil ilova uchun qulay JSON natijaga o'raydi.

Asosiy g'oya: ish stoli dasturidagi BIR XIL tahlil yadrosini (DSP, Welch PSD,
belgilar, qoidaviy klassifikatsiya) qayta ishlatamiz. Bu modul faqat natijani
telefon ilovasi oson o'qiydigan, ixcham JSON ko'rinishiga keltiradi:

  - umumiy yozuv ma'lumotlari (summary)
  - yakuniy holat + ishonch
  - holatlar bo'yicha ballar va ehtimolliklar (diagramma uchun)
  - 5 ritm bo'yicha nisbiy quvvat (ustunli diagramma uchun)
  - asosiy spektral belgilar (iAPF, FAA, FMT, engagement, ...)
  - vakil kanal uchun PSD egri chizig'i (kamaytirilgan nuqtalar — grafik uchun)
  - to'liq matnli hisobot (report)
  - atipik naqsh ogohlantirishlari va majburiy DISCLAIMER

Tahlil yadrosi SOF PYTHON da ishlaydi; numpy/scipy/pyedflib bo'lsa avtomatik
tezlashadi, bo'lmasa ham to'liq ishlaydi.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from eeg_engine import config, pipeline


# 10-20 tizimida orqa (oksipital/parietal) kanallar alfa ritmi uchun eng vakil
# hisoblanadi — PSD grafigi uchun shulardan birini tanlaymiz.
_PREFERRED_PSD_CHANNELS = ("O1", "O2", "Oz", "Pz", "P3", "P4", "Cz")


def _pick_representative_channel(spec: Dict[str, Any]) -> str:
    for ch in _PREFERRED_PSD_CHANNELS:
        if ch in spec:
            return ch
    return next(iter(spec.keys()))


def _downsample_psd(freqs: List[float], psd: List[float],
                    fmax: float = 45.0, max_points: int = 180) -> Dict[str, List[float]]:
    """PSD ni grafik uchun [0, fmax] Hz oralig'ida va <= max_points nuqtaga keltiradi."""
    pairs = [(f, p) for f, p in zip(freqs, psd) if f <= fmax]
    if not pairs:
        pairs = list(zip(freqs, psd))
    if len(pairs) > max_points:
        step = len(pairs) / float(max_points)
        idx = [int(i * step) for i in range(max_points)]
        pairs = [pairs[i] for i in idx]
    return {
        "freqs": [round(f, 3) for f, _ in pairs],
        "psd": [round(p, 6) for _, p in pairs],
    }


def _round_map(d: Dict[str, float], n: int = 4) -> Dict[str, float]:
    return {k: (round(v, n) if isinstance(v, (int, float)) else v) for k, v in d.items()}


def _selected_features(f: Dict[str, Any]) -> Dict[str, Any]:
    """Mobil ekranda ko'rsatish uchun asosiy belgilarni tanlaydi."""
    def num(x):
        return round(x, 4) if isinstance(x, (int, float)) else None

    return {
        "iapf": num(f.get("iapf")),
        "dominant_frequency": num(f.get("dominant_frequency")),
        "fft_dominant_frequency": num(f.get("fft_dominant_frequency")),
        "spectral_edge_95": num(f.get("spectral_edge_95")),
        "spectral_entropy": num(f.get("spectral_entropy")),
        "engagement": num(f.get("engagement")),
        "ratio_alpha_beta": num(f.get("ratio_alpha_beta")),
        "ratio_theta_beta": num(f.get("ratio_theta_beta")),
        "ratio_theta_alpha": num(f.get("ratio_theta_alpha")),
        "ratio_beta_alpha": num(f.get("ratio_beta_alpha")),
        "faa": num(f.get("faa")),
        "fmt": num(f.get("fmt")),
    }


def _relative_bands(f: Dict[str, Any]) -> Dict[str, float]:
    """5 ritm bo'yicha nisbiy quvvat (0..1) — ustunli diagramma uchun."""
    return {
        "delta": round(f.get("rp_delta", 0.0), 4),
        "theta": round(f.get("rp_theta", 0.0), 4),
        "alpha": round(f.get("rp_alpha", 0.0), 4),
        "beta": round(f.get("rp_beta", 0.0), 4),
        "gamma": round(f.get("rp_gamma", 0.0), 4),
    }


def analyze(path: str, fs: Optional[float] = None, target_fs: Optional[float] = None,
            notch: bool = True, prefer: str = "auto") -> Dict[str, Any]:
    """
    Bitta EEG faylni (EDF/EDF+/BDF/BDF+/CSV) tahlil qiladi va mobil ilova uchun
    JSON-ga moslangan dict qaytaradi.
    """
    objs = pipeline.analyze_objects(
        path, fs=fs, target_fs=target_fs, notch=notch, prefer=prefer)

    rec = objs["rec"]
    spec = objs["spec"]
    feats = objs["features"]
    cls = objs["classification"]

    summary = rec.summary()
    rep_ch = _pick_representative_channel(spec)
    psd = _downsample_psd(spec[rep_ch]["freqs"], spec[rep_ch]["psd"])

    # Holatlar tartibi: ehtimollik bo'yicha kamayuvchi
    probs = cls["probabilities"]
    ordered_states = sorted(config.STATES, key=lambda s: probs.get(s, 0.0), reverse=True)

    return {
        "app": {"name": config.APP_NAME, "version": config.APP_VERSION,
                "author": config.AUTHOR},
        "summary": {
            "source_file": rec.meta.get("source_file"),
            "format": summary.get("format"),
            "reader": summary.get("reader"),
            "channels": summary.get("channels"),
            "channel_names": summary.get("channel_names"),
            "fs": summary.get("fs"),
            "harmonized_fs": rec.meta.get("harmonized_fs"),
            "duration_sec": round(summary.get("duration_sec", 0.0), 2),
            "calibrated": objs["calibrated"],
        },
        "result": {
            "state": cls["state"],
            "confidence": round(cls["confidence"], 4),
            "ordered_states": ordered_states,
            "scores": _round_map(cls["scores"], 1),
            "probabilities": _round_map(probs, 4),
            "atypical": cls["atypical"],
        },
        "bands": _relative_bands(feats),
        "features": _selected_features(feats),
        "psd": {"channel": rep_ch, **psd},
        "report": objs["report"],
        "disclaimer": config.DISCLAIMER,
    }
