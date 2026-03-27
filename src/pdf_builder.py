import io
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from src.config import PDF_PAGE_MARGIN


@dataclass
class BuildResult:
    pdf_bytes: bytes
    total_pages: int
    errors: list[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


class ImageConverter:
    """Converts a raster image to a single A4 PDF page."""

    def __init__(self, margin: int = PDF_PAGE_MARGIN) -> None:
        self._margin = margin

    def to_pdf_bytes(self, image_bytes: bytes) -> bytes:
        img = self._normalise_image(Image.open(io.BytesIO(image_bytes)))
        x, y, draw_w, draw_h = self._fit_to_page(img)

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        c.drawImage(
            ImageReader(img),
            x, y,
            width=draw_w,
            height=draw_h,
            preserveAspectRatio=True,
        )
        c.save()
        buf.seek(0)
        return buf.read()

    def _normalise_image(self, img: Image.Image) -> Image.Image:
        if img.mode in ("RGBA", "P", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
            return background
        if img.mode != "RGB":
            return img.convert("RGB")
        return img

    def _fit_to_page(self, img: Image.Image) -> tuple[float, float, float, float]:
        page_w, page_h = A4
        max_w = page_w - 2 * self._margin
        max_h = page_h - 2 * self._margin

        img_w, img_h = img.size
        scale = min(max_w / img_w, max_h / img_h)
        draw_w, draw_h = img_w * scale, img_h * scale
        x = (page_w - draw_w) / 2
        y = (page_h - draw_h) / 2
        return x, y, draw_w, draw_h


class PdfBuilder:
    """Merges a sequence of files (images and PDFs) into a single PDF."""

    IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "tiff"}

    def __init__(self) -> None:
        self._converter = ImageConverter()

    def build(
        self,
        file_map: dict[str, bytes],
        order: list[str],
        progress_callback=None,
    ) -> BuildResult:
        writer = PdfWriter()
        errors: list[str] = []
        total = len(order)

        for idx, name in enumerate(order):
            ext = Path(name).suffix.lower().lstrip(".")
            file_bytes = file_map[name]

            try:
                if ext == "pdf":
                    self._append_pdf(writer, file_bytes)
                elif ext in self.IMAGE_EXTENSIONS:
                    self._append_image(writer, file_bytes)
                else:
                    errors.append(f"{name}: formato não suportado")
            except Exception as exc:
                errors.append(f"{name}: {exc}")

            if progress_callback:
                progress_callback(idx + 1, total, name)

        output_buf = io.BytesIO()
        writer.write(output_buf)
        output_buf.seek(0)

        return BuildResult(
            pdf_bytes=output_buf.read(),
            total_pages=len(writer.pages),
            errors=errors,
        )

    def _append_pdf(self, writer: PdfWriter, file_bytes: bytes) -> None:
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            writer.add_page(page)

    def _append_image(self, writer: PdfWriter, file_bytes: bytes) -> None:
        pdf_bytes = self._converter.to_pdf_bytes(file_bytes)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer.add_page(reader.pages[0])
