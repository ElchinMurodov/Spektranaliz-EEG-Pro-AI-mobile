"""
analyze.py — qurilmadagi (oflayn) EEG tahlil o'rovchisi.

Bu modul `eeg_engine` yadrosini TO'G'RIDAN-TO'G'RI, INTERNETSIZ chaqiradi va
natijani Kivy interfeysi oson ko'rsatadigan oddiy `dict` ko'rinishida qaytaradi.
Server yoki tarmoq umuman talab qilinmaydi — barcha hisoblash telefonning
o'zida bajariladi.

Tahlil yadrosi sof Python: numpy/scipy/pyedflib bo'lmasa ham to'liq ishlaydi
(EDF/BDF ni sof Python parser o'qiydi). Bu mobil paketlash uchun muhim.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from eeg_engine import config, pipeline


# Oksipital/parietal kanallar alfa ritmi uchun eng vakil — PSD grafigi shulardan
# birini tanlaydi.
_PREFERRED_PSD_CHANNELS = ("O1", "O2", "Oz", "Pz", "P3", "P4", "Cz")


def _pick_channel(spec: Dict[str, Any]) -> str:
    for ch in _PREFERRED_PSD_CHANNELS:
        if ch in spec:
            return ch
    return next(iter(spec.keys()))


def _downsample(freqs: List[float], psd: List[float],
                fmax: float = 45.0, max_points: int = 160) -> Dict[str, List[float]]:
    pairs = [(f, p) for f, p in zip(freqs, psd) if f <= fmax]
    if not pairs:
        pairs = list(zip(freqs, psd))
    if len(pairs) > max_points:
        step = len(pairs) / float(max_points)
        pairs = [pairs[int(i * step)] for i in range(max_points)]
    return {
        "freqs": [round(f, 3) for f, _ in pairs],
        "psd": [round(p, 6) for _, p in pairs],
    }


def _num(x):
    return round(x, 4) if isinstance(x, (int, float)) else None


def analyze(path: str, fs: Optional[float] = None, target_fs: Optional[float] = None,
            notch: bool = True, prefer: str = "auto") -> Dict[str, Any]:
    """Bitta EEG faylni (EDF/EDF+/BDF/BDF+/CSV) oflayn tahlil qiladi."""
    objs = pipeline.analyze_objects(
        path, fs=fs, target_fs=target_fs, notch=notch, prefer=prefer)

    rec = objs["rec"]
    spec = objs["spec"]
    feats = objs["features"]
    cls = objs["classification"]
    summary = rec.summary()

    rep_ch = _pick_channel(spec)
    psd = _downsample(spec[rep_ch]["freqs"], spec[rep_ch]["psd"])
    probs = cls["probabilities"]
    ordered = sorted(config.STATES, key=lambda s: probs.get(s, 0.0), reverse=True)

    return {
        "app": {"name": config.APP_NAME, "version": config.APP_VERSION,
                "author": config.AUTHOR},
        "summary": {
            "source_file": rec.meta.get("source_file"),
            "format": summary.get("format"),
            "reader": summary.get("reader"),
            "channels": summary.get("channels"),
            "fs": summary.get("fs"),
            "harmonized_fs": rec.meta.get("harmonized_fs"),
            "duration_sec": round(summary.get("duration_sec", 0.0), 2),
        },
        "result": {
            "state": cls["state"],
            "confidence": round(cls["confidence"], 4),
            "ordered_states": ordered,
            "scores": {k: round(v, 1) for k, v in cls["scores"].items()},
            "probabilities": {k: round(v, 4) for k, v in probs.items()},
            "atypical": cls["atypical"],
        },
        "bands": {
            "delta": round(feats.get("rp_delta", 0.0), 4),
            "theta": round(feats.get("rp_theta", 0.0), 4),
            "alpha": round(feats.get("rp_alpha", 0.0), 4),
            "beta": round(feats.get("rp_beta", 0.0), 4),
            "gamma": round(feats.get("rp_gamma", 0.0), 4),
        },
        "features": {
            "iapf": _num(feats.get("iapf")),
            "dominant_frequency": _num(feats.get("dominant_frequency")),
            "spectral_edge_95": _num(feats.get("spectral_edge_95")),
            "spectral_entropy": _num(feats.get("spectral_entropy")),
            "engagement": _num(feats.get("engagement")),
            "ratio_alpha_beta": _num(feats.get("ratio_alpha_beta")),
            "ratio_theta_beta": _num(feats.get("ratio_theta_beta")),
            "ratio_theta_alpha": _num(feats.get("ratio_theta_alpha")),
            "faa": _num(feats.get("faa")),
            "fmt": _num(feats.get("fmt")),
        },
        "psd": {"channel": rep_ch, **psd},
        "report": objs["report"],
        "disclaimer": config.DISCLAIMER,
    }
