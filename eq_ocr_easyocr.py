# services/eq_ocr_easyocr.py
from __future__ import annotations
import io, os, re
from dataclasses import dataclass
from typing import Optional, Union, List
from PIL import Image, ImageOps
import numpy as np
import cv2
import easyocr

@dataclass
class OcrResult:
    text: str
    backend: str = "easyocr"
    confidence: Optional[float] = None

_reader = None

def _get_reader():
    global _reader
    if _reader is not None:
        return _reader
    langs = os.getenv("EASYOCR_LANGS", "en").split(",")
    langs = [l.strip() for l in langs if l.strip()]
    gpu = os.getenv("EASYOCR_GPU", "0") not in ("0", "false", "False", "no", "No")
    _reader = easyocr.Reader(langs, gpu=gpu, verbose=False)
    return _reader

def _load_image_any(img_or_bytes_or_path: Union[bytes, str, Image.Image]) -> Image.Image:
    if isinstance(img_or_bytes_or_path, Image.Image):
        return img_or_bytes_or_path.convert("RGB")
    if isinstance(img_or_bytes_or_path, (bytes, bytearray)):
        return Image.open(io.BytesIO(img_or_bytes_or_path)).convert("RGB")
    with open(str(img_or_bytes_or_path), "rb") as f:
        return Image.open(io.BytesIO(f.read())).convert("RGB")

def _preprocess(pil_img: Image.Image) -> np.ndarray:
    # borda branca para não cortar símbolos nas extremidades
    pil_img = ImageOps.expand(pil_img, border=8, fill="white")
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    # upscale leve melhora OCR em imagens pequenas
    h, w = img.shape[:2]
    scale = 1.5 if max(h, w) < 1200 else 1.0
    if scale != 1.0:
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # contrast stretch + CLAHE
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    gray = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8)).apply(gray)
    # threshold leve (mantém linhas finas)
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                               cv2.THRESH_BINARY, 31, 10)
    return bw

_LATEX_WRAP_RX = re.compile(r"^\s*(\$\$?|\\\[|\\\()?(?P<core>.*?)(\$\$?|\\\]|\\\))?\s*$", re.DOTALL)

def _strip_delims(s: str) -> str:
    m = _LATEX_WRAP_RX.match(s or "")
    return (m.group("core") if m else s).strip()

def _normalize_math_like(text_lines: List[str]) -> str:
    """
    Normalização *leve* para aproximar de notação matemática/LaTeX-friendly.
    EasyOCR não é OCR matemático especializado; a ideia é só limpar ruído.
    """
    t = " ".join([re.sub(r"\s+", " ", x.strip()) for x in text_lines if x.strip()])
    t = _strip_delims(t)

    # correções simples
    t = re.sub(r"sqrt\s*\(\s*([^)]+)\s*\)", r"\\sqrt{\1}", t, flags=re.I)
    t = re.sub(r"\b(sin|cos|tan|log|ln)\s*\(\s*([^)]+)\s*\)", r"\\\1{\2}", t, flags=re.I)
    t = re.sub(r"\^([A-Za-z0-9])", r"^{\1}", t)  # x^2 -> x^{2}
    t = re.sub(r"\(\s*([^()]+)\s*\)\s*/\s*\(\s*([^()]+)\s*\)", r"\\frac{\1}{\2}", t)
    t = re.sub(r"([0-9])\s*[·•]\s*([0-9])", r"\1 \\cdot \2", t)
    # evitar duplicações de barras
    t = re.sub(r"\\\\+", r"\\", t)
    return t.strip()

def easyocr_math_ocr(img_or_bytes_or_path: Union[bytes, str, Image.Image]) -> OcrResult:
    """
    OCR com EasyOCR + pré-processamento.
    Retorna texto “math-like” (não LaTeX puro); seu LLM gera LaTeX nos campos do schema.
    """
    pil = _load_image_any(img_or_bytes_or_path)
    proc = _preprocess(pil)

    reader = _get_reader()
    # detail=1 → (bbox, text, conf). Pegamos linhas com confiança razoável.
    result = reader.readtext(proc, detail=1, paragraph=False)
    if not result:
        return OcrResult(text="", backend="easyocr", confidence=None)

    lines = []
    confs = []
    for (_bbox, text, conf) in result:
        if (text or "").strip():
            lines.append(text)
            try:
                confs.append(float(conf))
            except Exception:
                pass

    norm = _normalize_math_like(lines)
    avg_conf = (sum(confs) / len(confs)) if confs else None
    return OcrResult(text=norm, backend="easyocr", confidence=avg_conf)
