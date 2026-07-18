from ui.styles import load_styles


def test_light_theme_stylesheet_contains_brand_colors():
    stylesheet = load_styles("light")

    assert "#3B82F6" in stylesheet
    assert "#F8FAFC" in stylesheet
    assert "#0F172A" in stylesheet
