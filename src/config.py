from typing import Final

PAGE_TITLE: Final[str] = "Juntar Arquivos em PDF"
PAGE_ICON: Final[str] = "📄"
PAGE_LAYOUT: Final[str] = "centered"

SUPPORTED_TYPES: Final[list[str]] = [
    "pdf", "png", "jpg", "jpeg", "webp", "bmp", "tiff"
]

OUTPUT_FILENAME: Final[str] = "arquivos_combinados.pdf"

PDF_PAGE_MARGIN: Final[int] = 40
