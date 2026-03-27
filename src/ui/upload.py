from typing import Any

import streamlit as st

from src.config import SUPPORTED_TYPES


def render_uploader() -> list[Any]:
    """Renders the file uploader and returns the list of uploaded files."""
    return st.file_uploader(
        "Selecione os arquivos",
        type=SUPPORTED_TYPES,
        accept_multiple_files=True,
        help=f"Formatos aceitos: {', '.join(t.upper() for t in SUPPORTED_TYPES)}",
    )
