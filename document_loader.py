"""Student 1 - multimodal ingestion for UniCourse AI.

PDF/PNG/JPG -> [{'text': str, 'source': str, 'page': int}, ...]

- Searchable PDFs: local native text extraction (PyMuPDF).
- Scanned slides and images: 300-DPI Tesseract OCR, PSM 3 (paragraph-friendly).
- Complex diagrams/formulas: optional vision-model description (external API).

Team contract is unchanged: load_pdf(file_bytes, filename) remains available,
and each record contains only 'text', 'source', and 'page'.
"""
from __future__ import annotations

import base64
import os
import shutil
import warnings
from io import BytesIO
from pathlib import Path
from typing import Iterable

import pymupdf

SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg"}
SUPPORTED_DOCUMENTS = SUPPORTED_IMAGES | {".pdf"}


def _configure_tesseract(pytesseract_module) -> None:
    """Find the executable on Windows even if it is not included in PATH."""
    provided = os.getenv("TESSERACT_CMD")
    if provided:
        pytesseract_module.pytesseract.tesseract_cmd = provided
        return
    if shutil.which("tesseract"):
        return
    if os.name == "nt":
        candidates = [
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Tesseract-OCR" / "tesseract.exe",
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Tesseract-OCR" / "tesseract.exe",
        ]
        for executable in candidates:
            if executable.is_file():
                pytesseract_module.pytesseract.tesseract_cmd = str(executable)
                return


def _extract_ocr(
    page,
    language: str,
    dpi: int,
    tessdata: str | None,
    psm: int = 3,
) -> str:
    """Read an image-only page with 300-DPI Tesseract OCR (PSM 3 by default).

    First uses pytesseract on a rendered page (matches tested quality comparison).
    If unavailable, falls back to the PyMuPDF OCR integration.
    """
    primary_error = None
    try:
        import pytesseract
        from PIL import Image

        _configure_tesseract(pytesseract)
        pix = page.get_pixmap(
            dpi=dpi,
            colorspace=pymupdf.csRGB,
            alpha=False,
        )
        image = Image.open(BytesIO(pix.tobytes("png")))
        config = f"--oem 3 --psm {psm}"
        if tessdata:
            config += f' --tessdata-dir "{tessdata}"'
        return pytesseract.image_to_string(
            image,
            lang=language,
            config=config,
        ).strip()
    except Exception as exc:
        primary_error = exc

    try:
        textpage = page.get_textpage_ocr(
            language=language,
            dpi=dpi,
            full=True,
            tessdata=tessdata,
        )
        return page.get_text("text", textpage=textpage, sort=True).strip()
    except Exception as backup_error:
        raise RuntimeError(
            f"Tesseract OCR failed ({primary_error}); PyMuPDF OCR fallback "
            f"failed ({backup_error}). Verify Tesseract installation and "
            "English language data (eng.traineddata)."
        ) from backup_error


def _describe_visual_page(page, model: str, api_client=None) -> str:
    """Optional AI visual notes; verify all formulas and labels manually."""
    if api_client is None:
        from openai import OpenAI
        api_client = OpenAI()

    png_bytes = page.get_pixmap(dpi=145, alpha=False).tobytes("png")
    encoded = base64.b64encode(png_bytes).decode("ascii")
    prompt = (
        "You are transcribing a university lecture page for document search. "
        "Describe ONLY what can be seen. Concentrate on diagrams, axes and labels, "
        "arrows, charts, tables, relations between boxes, and mathematical formulas "
        "that ordinary OCR might miss. Quote equations exactly when legible. "
        "If a character, value or relationship is unclear, say 'unclear' rather "
        "than guessing. Keep the output factual, under 220 words, in the original "
        "language of the slide. Do not introduce external knowledge."
    )
    response = api_client.responses.create(
        model=model,
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": "data:image/png;base64," + encoded, "detail": "high"},
            ],
        }],
    )
    return (response.output_text or "").strip()


def load_document(
    file_bytes: bytes,
    filename: str,
    use_ocr: bool = True,
    max_pages: int | None = None,
    *,
    ocr_language: str = "eng",
    ocr_dpi: int = 300,
    ocr_psm: int = 3,
    tessdata: str | None = None,
    force_ocr: bool = False,
    use_vision: bool = False,
    vision_model: str = "gpt-4.1-mini",
    vision_pages: Iterable[int] | None = None,
    vision_max_pages: int = 3,
    vision_client=None,
) -> list[dict]:
    """Return 1-based document-page records with only text/source/page keys.

    OCR runs if a page has less than 120 characters of searchable native text,
    or for all selected pages when force_ocr=True. For testing, max_pages limits
    processing cost. AI vision is off by default and transmits page images only
    when explicitly enabled; it may incur charges.
    """
    if not file_bytes:
        return []
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_DOCUMENTS:
        raise ValueError("Supported documents: .pdf, .png, .jpg, .jpeg")
    if max_pages is not None and max_pages < 1:
        raise ValueError("max_pages must be >= 1 or None")
    if not ocr_language:
        raise ValueError("ocr_language cannot be empty")
    if not 72 <= ocr_dpi <= 600:
        raise ValueError("ocr_dpi must be between 72 and 600")
    if not 0 <= ocr_psm <= 13:
        raise ValueError("ocr_psm must be between 0 and 13")
    if vision_max_pages < 0:
        raise ValueError("vision_max_pages must be >= 0")
    if ext != ".pdf" and not use_ocr and not use_vision:
        raise ValueError("Image files require use_ocr=True or use_vision=True")
    if use_vision and vision_client is None and not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Set OPENAI_API_KEY for use_vision=True or pass vision_client")

    try:
        doc = pymupdf.open(stream=file_bytes, filetype=ext.lstrip("."))
    except Exception as exc:
        raise ValueError(f"Unable to open {filename!r} as a valid document") from exc

    chosen_pages = None if vision_pages is None else set(vision_pages)
    records: list[dict] = []
    issues: list[str] = []
    vision_calls = 0

    with doc:
        total = len(doc) if max_pages is None else min(len(doc), max_pages)
        for index in range(total):
            page = doc[index]
            page_number = index + 1
            native = page.get_text("text", sort=True).strip() if ext == ".pdf" else ""
            combined = native

            if use_ocr and (force_ocr or len(native) < 120):
                try:
                    recognized = _extract_ocr(
                        page, ocr_language, ocr_dpi, tessdata, psm=ocr_psm
                    )
                    if recognized and (force_ocr or len(recognized) > len(native)):
                        combined = recognized
                except Exception as exc:
                    issues.append(f"Page {page_number} OCR: {exc}")

            if (
                use_vision
                and vision_calls < vision_max_pages
                and (chosen_pages is None or page_number in chosen_pages)
            ):
                vision_calls += 1
                try:
                    description = _describe_visual_page(page, vision_model, api_client=vision_client)
                    if description:
                        combined = (
                            combined + "\n\n[AI-GENERATED VISUAL NOTES - CHECK ORIGINAL] "
                            + description
                        ).strip()
                except Exception as exc:
                    issues.append(f"Page {page_number} vision: {exc}")

            if combined.strip():
                records.append({
                    "text": combined.strip(),
                    "source": filename,
                    "page": page_number,
                })
            else:
                issues.append(f"Page {page_number}: no extracted content")

    if issues:
        warnings.warn(
            "Some pages may be incomplete: " + "; ".join(issues[:3]),
            RuntimeWarning,
            stacklevel=2,
        )
    if not records:
        raise ValueError(
            "No readable content. Install Tesseract and its language data "
            "(eng.traineddata), or use the optional vision model with permission."
        )
    return records


def load_pdf(
    file_bytes: bytes,
    filename: str,
    use_ocr: bool = True,
    max_pages: int | None = None,
    **kwargs,
) -> list[dict]:
    """Backward-compatible API: load_pdf(pdf_bytes, 'course.pdf')."""
    if Path(filename).suffix.lower() != ".pdf":
        raise ValueError("load_pdf supports only .pdf; use load_document for PNG/JPG")
    return load_document(
        file_bytes,
        filename,
        use_ocr=use_ocr,
        max_pages=max_pages,
        **kwargs,
    )
