from typing import Any

import streamlit as st


class FileListManager:
    """Manages the ordered list of uploaded files in session state."""

    SESSION_KEY = "file_order"
    BYTES_KEY = "file_bytes"
    SIZE_KEY = "file_sizes"

    def sync(self, uploaded_files: list[Any]) -> tuple[list[str], dict[str, Any]]:
        """Syncs session state with the current upload and returns (order, file_map)."""
        if self.BYTES_KEY not in st.session_state:
            st.session_state[self.BYTES_KEY] = {}
        if self.SIZE_KEY not in st.session_state:
            st.session_state[self.SIZE_KEY] = {}

        # Store bytes for any newly uploaded files before a potential rerun discards them
        for f in uploaded_files:
            if f.name not in st.session_state[self.BYTES_KEY]:
                st.session_state[self.BYTES_KEY][f.name] = f.read()
                st.session_state[self.SIZE_KEY][f.name] = f.size

        file_map: dict[str, Any] = st.session_state[self.BYTES_KEY]
        incoming_names = [f.name for f in uploaded_files]

        if self.SESSION_KEY not in st.session_state:
            st.session_state[self.SESSION_KEY] = incoming_names
        else:
            existing = [n for n in st.session_state[self.SESSION_KEY] if n in file_map]
            new_files = [n for n in incoming_names if n not in st.session_state[self.SESSION_KEY]]
            st.session_state[self.SESSION_KEY] = existing + new_files

        return st.session_state[self.SESSION_KEY], file_map

    def reset(self) -> None:
        """Clears the order from session state."""
        st.session_state.pop(self.SESSION_KEY, None)
        st.session_state.pop(self.BYTES_KEY, None)
        st.session_state.pop(self.SIZE_KEY, None)

    def render(self, order: list[str], file_map: dict[str, Any]) -> None:
        """Renders the reorder UI with ▲ ▼ buttons."""
        st.subheader("Ordem dos arquivos")
        st.caption("Use ▲ / ▼ para ajustar a sequência antes de gerar o PDF.")

        for i, name in enumerate(order):
            col_idx, col_name, col_up, col_down = st.columns([0.5, 6, 0.75, 0.75])

            col_idx.markdown(f"**{i + 1}.**")
            size_kb = st.session_state[self.SIZE_KEY].get(name, len(file_map[name])) / 1024
            col_name.write(f"{name}  `{size_kb:.1f} KB`")

            if col_up.button("▲", key=f"up_{i}", disabled=(i == 0)):
                order[i - 1], order[i] = order[i], order[i - 1]
                st.rerun()

            if col_down.button("▼", key=f"down_{i}", disabled=(i == len(order) - 1)):
                order[i + 1], order[i] = order[i], order[i + 1]
                st.rerun()
