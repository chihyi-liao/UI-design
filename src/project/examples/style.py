Red = "#ff0000"
Green = "#00ff00"
White = "#ffffff"
Gold = "#FFD306"

FONTS_SANS_SERIF = (
    "font.sans-serif",
    [
        "WenQuanYi Zen Hei",
        "Microsoft JhengHei",
        "Noto Sans CJK",
        "DejaVu Sans",
        "Arial",
    ],
)


def default_style():
    return dict(
        style_name="twstock",
        base_mpf_style="mike",
        base_mpl_style="dark_background",
        marketcolors={
            "candle": {"up": Red, "down": Green},
            "edge": {"up": Red, "down": Green},
            "wick": {"up": Red, "down": Green},
            "ohlc": {"up": Red, "down": Green},
            "volume": {"up": Red, "down": Green},
            "vcedge": {"up": Red, "down": Green},
            "vcdopcod": False,  # Volume Color Depends On Price Change On Day
            "alpha": 1.0,
        },
        mavcolors=["#ec009c", "#78ff8f", "#fcf120"],
        y_on_right=False,
        gridcolor=None,
        gridstyle=None,
        facecolor=None,
        scale_padding=0,
        rc=[
            ("axes.edgecolor", "white"),
            ("axes.linewidth", 1.5),
            ("axes.labelsize", "large"),
            ("axes.labelweight", "semibold"),
            ("axes.grid", True),
            ("axes.grid.axis", "both"),
            ("axes.grid.which", "major"),
            ("grid.alpha", 0.5),
            ("grid.color", "#b0b0b0"),
            ("grid.linestyle", "--"),
            ("grid.linewidth", 0.8),
            ("figure.titlesize", "x-large"),
            ("figure.titleweight", "semibold"),
            ("figure.facecolor", "#0a0a0a"),
            ("patch.linewidth", 1.0),
            ("lines.linewidth", 1.0),
            ("font.family", "sans-serif"),
            FONTS_SANS_SERIF,
            ("font.weight", "medium"),
            ("font.size", 8),
            ("axes.unicode_minus", False),
        ],
    )
