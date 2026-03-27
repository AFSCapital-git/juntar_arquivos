from typing import Any

import streamlit as st


class FileListManager:
    """Manages the ordered list of uploaded files in session state."""

    SESSION_KEY = "file_order"

    def sync(self, uploaded_files: list[Any]) -> tuple[list[str], dict[str, Any]]:
        """Syncs session state with the current upload and returns (order, file_map)."""
        file_map: dict[str, Any] = {f.name: f for f in uploaded_files}
        incoming_names = list(file_map.keys())

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

    def render(self, order: list[str], file_map: dict[str, Any]) -> None:
        """Renders the reorder UI with ▲ ▼ buttons."""
        st.subheader("Ordem dos arquivos")
        st.caption("Use ▲ / ▼ para ajustar a sequência antes de gerar o PDF.")

        for i, name in enumerate(order):
            col_idx, col_name, col_up, col_down = st.columns([0.5, 6, 0.75, 0.75])

            col_idx.markdown(f"**{i + 1}.**")
            col_name.write(f"{name}  `{file_map[name].size / 1024:.1f} KB`")

            if col_up.button("▲", key=f"up_{i}", disabled=(i == 0)):
                order[i - 1], order[i] = order[i], order[i - 1]
                st.rerun()

            if col_down.button("▼", key=f"down_{i}", disabled=(i == len(order) - 1)):
                order[i + 1], order[i] = order[i], order[i + 1]
                st.rerun()
