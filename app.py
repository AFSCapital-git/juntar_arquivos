import streamlit as st

from src.config import OUTPUT_FILENAME, PAGE_ICON, PAGE_LAYOUT, PAGE_TITLE
from src.pdf_builder import PdfBuilder
from src.ui.file_list import FileListManager
from src.ui.upload import render_uploader

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=PAGE_LAYOUT)

st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.markdown(
    "Faça upload de imagens e/ou PDFs. "
    "Use os botões ▲ ▼ para reordenar e exporte tudo em um único PDF."
)

uploaded_files = render_uploader()

manager = FileListManager()

if uploaded_files:
    order, file_map = manager.sync(uploaded_files)
    manager.render(order, file_map)

    st.divider()

    if st.button("⬇️ Gerar PDF combinado", type="primary", use_container_width=True):
        progress_bar = st.progress(0, text="Processando arquivos…")

        def on_progress(current: int, total: int, name: str) -> None:
            progress_bar.progress(current / total, text=f"Processando {current}/{total}…")

        raw_file_map = {name: file_map[name].read() for name in order}

        builder = PdfBuilder()
        result = builder.build(raw_file_map, order, progress_callback=on_progress)

        if result.has_errors:
            st.error("Alguns arquivos não puderam ser processados:\n" + "\n".join(result.errors))

        progress_bar.empty()
        st.success(f"PDF gerado com sucesso! Total de páginas: **{result.total_pages}**")

        st.download_button(
            label="💾 Baixar PDF combinado",
            data=result.pdf_bytes,
            file_name=OUTPUT_FILENAME,
            mime="application/pdf",
            use_container_width=True,
        )
else:
    manager.reset()
    st.info("Faça upload de pelo menos um arquivo para começar.")
