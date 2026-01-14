from PyQt6.QtGui import QColor

class ThemeManager:
    """
    Manages application themes.
    Generates 50 variations of Cyberpunk accents.
    """
    def __init__(self):
        self.themes = self._generate_themes()
        self.current_theme_index = 0

    def _generate_themes(self):
        """
        Generates 50 themes.
        Base is Dark mode (Off Black).
        Accents shift through the HSL spectrum.
        Default (Index 0) is Dark Yellow.
        """
        base_bg = "#121212" # Off Black
        themes = []

        # Theme 0: User requested Dark Yellow
        themes.append({
            "name": "Cyber Yellow (Default)",
            "accent": "#FFD700", # Gold/Dark Yellow
            "bg": base_bg
        })

        # Generate 49 others by shifting Hue
        for i in range(1, 50):
            # Hue 0-360. 
            hue = (i * (360 / 50)) % 360
            color = QColor.fromHslF(hue/360.0, 1.0, 0.5)
            themes.append({
                "name": f"Cyber Variant {i}",
                "accent": color.name(),
                "bg": base_bg
            })
            
        return themes

    def get_current_theme(self):
        return self.themes[self.current_theme_index]

    def set_theme(self, index):
        if 0 <= index < len(self.themes):
            self.current_theme_index = index

    def next_theme(self):
        self.current_theme_index = (self.current_theme_index + 1) % len(self.themes)
        return self.get_current_theme()
