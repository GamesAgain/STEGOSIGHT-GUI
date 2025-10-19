from .analyze_tab_style import ANALYZE_TAB_STYLE
from .base_theme import BASE_THEME, create_palette
from .embed_tab_style import EMBED_TAB_STYLE
from .extract_tab_style import EXTRACT_TAB_STYLE


def build_stylesheet() -> str:
    return "\n".join(
        filter(
            None,
            [BASE_THEME.strip(), EMBED_TAB_STYLE.strip(), EXTRACT_TAB_STYLE.strip(), ANALYZE_TAB_STYLE.strip()],
        )
    )


__all__ = ["build_stylesheet", "create_palette"]
