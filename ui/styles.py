from ui.themes.dark import stylesheet as dark_theme
from ui.themes.light import stylesheet as light_theme


def load_styles(theme="dark"):

    themes = {
        "dark": dark_theme,
        "light": light_theme,
    }

    return themes.get(theme, dark_theme)()
