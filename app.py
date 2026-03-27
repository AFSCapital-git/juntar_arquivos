import io
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image
from pypdf import PdfWriter, PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


SUPPORTED_TYPES = ["pdf", "png", "jpg", "jpeg", "webp", "bmp", "tiff"]

st.set_page_config(
    page_title="Juntar Arquivos em PDF",
    page_icon="📄",
    layout="centered",
)

st.title("📄 Juntar Arquivos em PDF")
st.markdown(
    "Faça upload de imagens e/ou PDFs. "
    "Os arquivos serão combinados **na ordem em que aparecem** e exportados como um único PDF."
)

uploaded_files = st.file_uploader(
    "Selecione os arquivos",
    type=SUPPORTED_TYPES,
    accept_multiple_files=True,
    help="Formatos aceitos: PDF, PNG, JPG, JPEG, WEBP, BMP, TIFF",
)

if uploaded_files:
    st.subheader("Arquivos carregados")

    # Allow reordering via drag-and-drop description; show list with index
    for i, f in enumerate(uploaded_files, start=1):
        st.write(f"**{i}.** {f.name}  `{f.size / 1024:.1f} KB`")

    st.divider()

    if st.button("⬇️ Gerar PDF combinado", type="primary", use_container_width=True):
        writer = PdfWriter()

        progress = st.progress(0, text="Processando arquivos…")

        def image_bytes_to_pdf_page(image_bytes: bytes, filename: str) -> bytes:
            """Converts an image to a PDF page (A4, image fits inside keeping aspect ratio)."""
            img = Image.open(io.BytesIO(image_bytes))

            # Convert palette/RGBA to RGB for JPEG compatibility inside PDF
            if img.mode in ("RGBA", "P", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            page_w, page_h = A4  # 595 x 842 pt
            margin = 40
            max_w = page_w - 2 * margin
            max_h = page_h - 2 * margin

            img_w, img_h = img.size
            scale = min(max_w / img_w, max_h / img_h)
            draw_w = img_w * scale
            draw_h = img_h * scale
            x = (page_w - draw_w) / 2
            y = (page_h - draw_h) / 2

            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=A4)
            c.drawImage(
                ImageReader(img),
                x, y, width=draw_w, height=draw_h,
                preserveAspectRatio=True,
            )
            c.save()
            buf.seek(0)
            return buf.read()

        total = len(uploaded_files)
        errors = []

        for idx, uploaded_file in enumerate(uploaded_files):
            file_bytes = uploaded_file.read()
            ext = Path(uploaded_file.name).suffix.lower().lstrip(".")

            try:
                if ext == "pdf":
                    reader = PdfReader(io.BytesIO(file_bytes))
                    for page in reader.pages:
                        writer.add_page(page)
                else:
                    pdf_bytes = image_bytes_to_pdf_page(file_bytes, uploaded_file.name)
                    reader = PdfReader(io.BytesIO(pdf_bytes))
                    writer.add_page(reader.pages[0])
            except Exception as exc:
                errors.append(f"{uploaded_file.name}: {exc}")

            progress.progress((idx + 1) / total, text=f"Processando {idx + 1}/{total}…")

        if errors:
            st.error("Alguns arquivos não puderam ser processados:\n" + "\n".join(errors))

        output_buf = io.BytesIO()
        writer.write(output_buf)
        output_buf.seek(0)

        progress.empty()
        st.success(f"PDF gerado com sucesso! Total de páginas: **{len(writer.pages)}**")

        st.download_button(
            label="💾 Baixar PDF combinado",
            data=output_buf,
            file_name="arquivos_combinados.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
else:
    st.info("Faça upload de pelo menos um arquivo para começar.")
