"""
設定値・定数定義
"""

# ウィンドウ設定
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Healing Clicker"

# 色定義 (RGB)
COLORS = {
    "background": (255, 245, 238),      # セピア風背景
    "primary": (255, 182, 193),          # ライトピンク
    "secondary": (176, 224, 230),        # パウダーブルー
    "accent": (255, 218, 185),           # ピーチ
    "text": (105, 105, 105),             # ダークグレー
    "text_light": (169, 169, 169),       # ライトグレー
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "gold": (255, 215, 0),
    "success": (144, 238, 144),          # ライトグリーン
    "warning": (255, 165, 0),            # オレンジ
}

# フォント設定
FONT_SIZES = {
    "small": 18,
    "medium": 24,
    "large": 36,
    "xlarge": 48,
    "title": 64,
}

# アップグレード設定
UPGRADES = {
    "click_power": {
        "name": "撫でる力",
        "description": "クリックごとのポイントを+1増加",
        "base_cost": 10,
        "cost_multiplier": 1.15,
        "effect_per_level": 1,
    },
    "auto_click": {
        "name": "お手伝い妖精",
        "description": "毎秒自動で+1ポイント獲得",
        "base_cost": 50,
        "cost_multiplier": 1.15,
        "effect_per_level": 1,
    },
    "lucky_bonus": {
        "name": "幸運のお守り",
        "description": "10%の確率でポイント2倍",
        "base_cost": 200,
        "cost_multiplier": 1.20,
        "effect_per_level": 5,  # 5%ずつ確率上昇
        "max_level": 10,
    },
    "golden_touch": {
        "name": "黄金の手",
        "description": "クリックポイントを+5増加",
        "base_cost": 500,
        "cost_multiplier": 1.18,
        "effect_per_level": 5,
    },
    "fairy_army": {
        "name": "妖精軍団",
        "description": "毎秒自動で+10ポイント獲得",
        "base_cost": 2000,
        "cost_multiplier": 1.15,
        "effect_per_level": 10,
    },
}

# アニメーション設定
ANIMATION = {
    "click_scale_duration": 0.18,  # 秒
    "click_squash_portion": 0.35,  # 前半の押し込み割合
    "click_scale_min_y": 0.86,     # ぷにっと縮む縦方向スケール
    "click_scale_max_x": 1.08,     # ぷにっと広がる横方向スケール
    "popup_duration": 1.0,        # 秒
    "popup_rise_distance": 40,    # ピクセル
}

# キャラクター設定
CHARACTER = {
    "size": (200, 200),
    "position": (540, 260),  # 中央やや左
}

# UI配置
UI_LAYOUT = {
    "points_display": (640, 50),
    "upgrade_panel": {
        "x": 900,
        "y": 100,
        "width": 350,
        "height": 500,
    },
    "settings_button": (1220, 30),
}

# セーブ設定
SAVE_FILE = "save_data.json"
AUTO_SAVE_INTERVAL = 30  # 秒

# サウンド設定
DEFAULT_BGM_VOLUME = 0.5
DEFAULT_SFX_VOLUME = 0.7
