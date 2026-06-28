"""
generate_player_card.py

Auto-generates a FIFA-Ultimate-Team-style PNG for any player using real
stats from the database. Tries a freely-licensed Wikipedia photo first
(Wikimedia Commons images are tagged with reuse licenses), falling back
to a generated initials avatar so the project never depends on
unlicensed scraped images.
"""

import os
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import create_engine
from dotenv import load_dotenv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

load_dotenv()

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "data" / "player_cards"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_CANDIDATES_BOLD = ["arialbd.ttf", "C:/Windows/Fonts/arialbd.ttf"]
FONT_CANDIDATES_REGULAR = ["arial.ttf", "C:/Windows/Fonts/arial.ttf"]

GOLD = (255, 215, 0)
NAVY_TOP = (20, 34, 68)
NAVY_BOTTOM = (3, 6, 14)


def load_font(candidates, size):
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def get_engine():
    host = os.getenv("HOST_POSTGRES_HOST", "localhost")
    port = os.getenv("HOST_POSTGRES_PORT", "5432")
    db = os.getenv("HOST_POSTGRES_DB", "worldcup2026")
    user = os.getenv("HOST_POSTGRES_USER", "postgres")
    password = os.getenv("HOST_POSTGRES_PASSWORD", "")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")


def get_player_stats(engine, player_name):
    query = """
        SELECT p.full_name, g.is_penalty, m.tournament_id, m.stage
        FROM players p
        JOIN match_goals g ON p.player_id = g.player_id
        JOIN matches m ON g.match_id = m.match_id
        WHERE p.full_name ILIKE %(name)s
    """
    return pd.read_sql(query, engine, params={"name": f"%{player_name}%"})


def get_player_nationality(engine, player_name):
    query = """
        SELECT t.team_name
        FROM players p
        LEFT JOIN teams t ON p.nationality_team_id = t.team_id
        WHERE p.full_name ILIKE %(name)s
        LIMIT 1
    """
    df = pd.read_sql(query, engine, params={"name": f"%{player_name}%"})
    if not df.empty and pd.notna(df["team_name"].iloc[0]):
        return df["team_name"].iloc[0]
    return None


def compute_metrics(df):
    total_goals = len(df)
    tournaments_played = df["tournament_id"].nunique()
    penalty_goals = int(df["is_penalty"].sum())
    knockout_keywords = ["final", "semi", "quarter", "round of", "knockout"]
    is_knockout = df["stage"].fillna("").str.lower().apply(
        lambda s: any(k in s for k in knockout_keywords)
    )
    knockout_goals = int(is_knockout.sum())
    goals_per_tournament = round(total_goals / tournaments_played, 1) if tournaments_played else 0

    return {
        "Total Goals": total_goals,
        "Tournaments": tournaments_played,
        "Goals / Tourney": goals_per_tournament,
        "Knockout Goals": knockout_goals,
        "Penalties": penalty_goals,
    }


def compute_rating(metrics):
    """A flavor 'ALL-TIME RATING' (40-99 scale), like a FUT card overall."""
    raw = (
        40
        + metrics["Total Goals"] * 2.2
        + metrics["Tournaments"] * 3
        + metrics["Knockout Goals"] * 2.5
    )
    return int(min(99, raw))


def fetch_player_photo(player_name, size=180):
    headers = {"User-Agent": "WorldCup2026Pipeline/1.0 (educational portfolio project)"}
    try:
        resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "titles": player_name,
                "prop": "pageimages",
                "format": "json",
                "pithumbsize": size * 2,
            },
            headers=headers,
            timeout=5,
        )
        pages = resp.json().get("query", {}).get("pages", {})
        for page in pages.values():
            thumb = page.get("thumbnail", {}).get("source")
            if thumb:
                img_resp = requests.get(thumb, headers=headers, timeout=5)
                return Image.open(BytesIO(img_resp.content)).convert("RGBA")
    except Exception as e:
        print(f"  (No Wikipedia photo found for {player_name}: {e})")
    return None


def draw_initials_avatar(name, size=180):
    initials = "".join([w[0] for w in name.split()[:2]]).upper()
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 0, size, size), fill=(30, 60, 114, 255))
    font = load_font(FONT_CANDIDATES_BOLD, size // 2)
    bbox = draw.textbbox((0, 0), initials, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - w) / 2, (size - h) / 2 - bbox[1]), initials, font=font, fill="white")
    return img


def circular_crop(img, size):
    img = img.resize((size, size))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size))
    out.paste(img, (0, 0), mask)
    return out


def draw_vertical_gradient(size, top_color, bottom_color):
    w, h = size
    base = Image.new("RGB", (w, h), top_color)
    draw = ImageDraw.Draw(base)
    for y in range(h):
        t = y / h
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return base


def add_diamond_pattern(card, spacing=42, color=(255, 215, 0, 14)):
    w, h = card.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x in range(-h, w + h, spacing):
        draw.line([(x, 0), (x + h, h)], fill=color, width=1)
        draw.line([(x, h), (x + h, 0)], fill=color, width=1)
    return Image.alpha_composite(card.convert("RGBA"), overlay)


def add_shine(card):
    w, h = card.size
    shine = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    band_w, band_h = int(w * 0.45), h * 2
    band = Image.new("RGBA", (band_w, band_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(band)
    for x in range(band_w):
        t = x / band_w
        alpha = int(70 * np.exp(-((t - 0.5) ** 2) / 0.015))
        draw.line([(x, 0), (x, band_h)], fill=(255, 255, 255, alpha))
    band = band.rotate(18, expand=True)
    shine.paste(band, (int(w * 0.45), -int(h * 0.35)), band)
    return Image.alpha_composite(card.convert("RGBA"), shine)


def draw_radar(metrics, save_path):
    labels = list(metrics.keys())
    values = list(metrics.values())
    max_val = max(values) if max(values) > 0 else 1
    norm_values = [v / max_val for v in values]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    norm_values += norm_values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4.6, 4.6), subplot_kw=dict(polar=True))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    ax.set_ylim(0, 1.08)
    ax.set_yticks([])
    ax.grid(color="white", alpha=0.25, linewidth=0.8)
    ax.spines['polar'].set_color((1, 1, 1, 0.35))

    ax.plot(angles, norm_values, color="#FFD700", linewidth=2.5)
    ax.fill(angles, norm_values, color="#FFD700", alpha=0.35)
    ax.plot(angles, norm_values, "o", color="#FFD700", markersize=6, zorder=5)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color="white", size=11, fontweight="bold")
    ax.tick_params(axis='x', pad=16)

    plt.savefig(save_path, transparent=True, dpi=150, bbox_inches="tight", pad_inches=0.4)
    plt.close()


def draw_text_with_shadow(draw, position, text, font, fill, anchor=None, shadow_color=(0, 0, 0)):
    x, y = position
    draw.text((x + 2, y + 2), text, font=font, fill=shadow_color, anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)


def generate_card(player_name):
    engine = get_engine()
    df = get_player_stats(engine, player_name)
    if df.empty:
        print(f"No data found for '{player_name}'")
        return

    full_name = df["full_name"].iloc[0]
    nationality = get_player_nationality(engine, player_name)
    metrics = compute_metrics(df)
    rating = compute_rating(metrics)

    card_w, card_h = 640, 1020
    card = draw_vertical_gradient((card_w, card_h), NAVY_TOP, NAVY_BOTTOM)
    card = add_diamond_pattern(card)

    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle([8, 8, card_w - 9, card_h - 9], radius=28, outline=GOLD, width=5)
    draw.rounded_rectangle([20, 20, card_w - 21, card_h - 21], radius=20, outline=(255, 255, 255, 90), width=1)

    rating_font = load_font(FONT_CANDIDATES_BOLD, 54)
    rating_label_font = load_font(FONT_CANDIDATES_BOLD, 13)
    star_font = load_font(FONT_CANDIDATES_REGULAR, 18)
    badge_font = load_font(FONT_CANDIDATES_BOLD, 14)
    title_font = load_font(FONT_CANDIDATES_BOLD, 36)
    nation_font = load_font(FONT_CANDIDATES_REGULAR, 15)
    stat_label_font = load_font(FONT_CANDIDATES_REGULAR, 17)
    stat_value_font = load_font(FONT_CANDIDATES_BOLD, 19)
    footer_font = load_font(FONT_CANDIDATES_REGULAR, 13)

    cx = card_w / 2

    # --- Rating corner badge (top-left, classic FUT placement) ---
    draw_text_with_shadow(draw, (55, 60), str(rating), rating_font, GOLD, anchor="mm")
    draw.text((55, 98), "ALL-TIME", font=rating_label_font, fill=(220, 220, 230), anchor="mm")
    draw.text((55, 115), "RATING", font=rating_label_font, fill=(220, 220, 230), anchor="mm")
    stars_filled = max(1, min(5, round(rating / 20)))
    star_str = "\u2605" * stars_filled + "\u2606" * (5 - stars_filled)
    draw.text((55, 140), star_str, font=star_font, fill=GOLD, anchor="mm")

    draw.text((cx, 50), "FIFA WORLD CUP  \u2022  ALL-TIME LEGENDS", font=badge_font, fill=GOLD, anchor="mm")
    draw_text_with_shadow(draw, (cx, 98), full_name, title_font, "white", anchor="mm")
    if nationality:
        draw.text((cx, 128), nationality.upper(), font=nation_font, fill=(200, 200, 215), anchor="mm")
    draw.line([(cx - 110, 148), (cx + 110, 148)], fill=GOLD, width=2)

    # --- Avatar with gold ring ---
    avatar_size = 170
    ring_size = avatar_size + 16
    ring_top = 165
    ring = Image.new("RGBA", (ring_size, ring_size), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, ring_size, ring_size), outline=GOLD, width=6)
    card.paste(ring, (int(cx - ring_size / 2), ring_top), ring)

    photo = fetch_player_photo(full_name, size=avatar_size)
    avatar = circular_crop(photo, avatar_size) if photo else draw_initials_avatar(full_name, size=avatar_size)
    card.paste(avatar, (int(cx - avatar_size / 2), ring_top + 8), avatar)

    # --- Radar chart ---
    radar_path = OUTPUT_DIR / "_radar_temp.png"
    draw_radar(metrics, radar_path)
    radar_img = Image.open(radar_path).convert("RGBA")
    radar_w = 400
    radar_h = int(radar_img.height * (radar_w / radar_img.width))
    radar_img = radar_img.resize((radar_w, radar_h))
    radar_top = ring_top + ring_size + 8
    card.paste(radar_img, (int(cx - radar_w / 2), radar_top), radar_img)
    os.remove(radar_path)

    # --- Stats rows ---
    stats_top = radar_top + radar_h - 5
    inner_left, inner_right = 95, card_w - 95
    row_height = 34
    draw.line([(inner_left, stats_top), (inner_right, stats_top)], fill=(255, 255, 255, 60), width=1)

    y = stats_top + 16
    for label, value in metrics.items():
        draw.text((inner_left, y), label, font=stat_label_font, fill=(210, 210, 220), anchor="lm")
        draw.text((inner_right, y), str(value), font=stat_value_font, fill=GOLD, anchor="rm")
        y += row_height
        draw.line([(inner_left, y - 8), (inner_right, y - 8)], fill=(255, 255, 255, 25), width=1)

    footer_y = card_h - 45
    draw.line([(cx - 90, footer_y - 15), (cx + 90, footer_y - 15)], fill=GOLD, width=1)
    draw.text((cx, footer_y), "#WorldCup2026  \u2022  Auto-Generated Player Card",
              font=footer_font, fill=(170, 170, 180), anchor="mm")

    card = add_shine(card)

    safe_name = full_name.replace(" ", "_")
    out_path = OUTPUT_DIR / f"{safe_name}_card.png"
    card.convert("RGB").save(out_path)
    print(f"Card saved to {out_path}")
    return out_path


if __name__ == "__main__":
    generate_card("Lionel Messi")