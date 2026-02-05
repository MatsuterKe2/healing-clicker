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

# キャラクター定義
CHARACTERS = {
    "hana": {
        "name": "ハナ",
        "theme": "花・春",
        "unlock_condition": None,
        "colors": {
            "hair": (180, 130, 220),
            "hair_shadow": (150, 100, 200),
            "ribbon": (255, 150, 180),
            "accent": (255, 218, 185),
        },
    },
    "mizuki": {
        "name": "ミズキ",
        "theme": "水・夏",
        "unlock_condition": {"type": "total_points", "value": 10000},
        "colors": {
            "hair": (100, 180, 255),
            "hair_shadow": (70, 150, 230),
            "ribbon": (150, 220, 255),
            "accent": (200, 235, 255),
        },
    },
    "kaede": {
        "name": "カエデ",
        "theme": "紅葉・秋",
        "unlock_condition": {"type": "total_clicks", "value": 5000},
        "colors": {
            "hair": (220, 120, 60),
            "hair_shadow": (190, 90, 40),
            "ribbon": (255, 180, 50),
            "accent": (255, 230, 180),
        },
    },
    "yuki": {
        "name": "ユキ",
        "theme": "雪・冬",
        "unlock_condition": {"type": "achievements", "value": 10},
        "colors": {
            "hair": (200, 210, 230),
            "hair_shadow": (170, 180, 210),
            "ribbon": (180, 200, 255),
            "accent": (230, 240, 255),
        },
    },
}

# 好感度設定
AFFECTION = {
    "max": 100,
    "levels": [
        {"min": 0, "name": "はじめまして", "expression": "normal"},
        {"min": 20, "name": "仲良し", "expression": "smile"},
        {"min": 40, "name": "親友", "expression": "blush"},
        {"min": 60, "name": "大好き", "expression": "sparkle"},
        {"min": 80, "name": "運命の人", "expression": "rainbow"},
    ],
    "gains": {
        "click": 0.01,
        "upgrade": 0.5,
        "daily_login": 1.0,
        "event_success": 2.0,
    },
}

# 実績定義
ACHIEVEMENTS = {
    "click_10":       {"name": "はじめての一歩",   "condition": {"type": "total_clicks",   "value": 10},      "reward": 100},
    "click_100":      {"name": "なでなでマスター", "condition": {"type": "total_clicks",   "value": 100},     "reward": 500},
    "click_1000":     {"name": "撫で職人",         "condition": {"type": "total_clicks",   "value": 1000},    "reward": 5000},
    "click_10000":    {"name": "伝説の手",         "condition": {"type": "total_clicks",   "value": 10000},   "reward": 50000},
    "points_1000":    {"name": "ちょっとした貯金", "condition": {"type": "total_points",   "value": 1000},    "reward": 200},
    "points_10000":   {"name": "お金持ちへの道",   "condition": {"type": "total_points",   "value": 10000},   "reward": 2000},
    "points_100000":  {"name": "大富豪",           "condition": {"type": "total_points",   "value": 100000},  "reward": 20000},
    "points_1000000": {"name": "億万長者",         "condition": {"type": "total_points",   "value": 1000000}, "reward": 200000},
    "upgrade_first":  {"name": "はじめての強化",   "condition": {"type": "total_upgrades", "value": 1},       "reward": 50},
    "upgrade_10":     {"name": "成長中",           "condition": {"type": "total_upgrades", "value": 10},      "reward": 1000},
    "upgrade_all":    {"name": "コンプリーター",   "condition": {"type": "all_upgrades_lv", "value": 5},      "reward": 10000},
    "affection_20":   {"name": "仲良しさん",       "condition": {"type": "max_affection",  "value": 20},      "reward": 500},
    "affection_50":   {"name": "親友",             "condition": {"type": "max_affection",  "value": 50},      "reward": 5000},
    "affection_100":  {"name": "運命の人",         "condition": {"type": "max_affection",  "value": 100},     "reward": 50000},
    "affection_all":  {"name": "みんな大好き",     "condition": {"type": "all_affection",  "value": 50},      "reward": 100000},
    "lucky_hit":      {"name": "ラッキー！",       "condition": {"type": "first_lucky",    "value": 1},       "reward": 300},
    "offline_return": {"name": "お帰りなさい",     "condition": {"type": "first_offline",  "value": 1},       "reward": 200},
    "event_first":    {"name": "不思議な出来事",   "condition": {"type": "first_event",    "value": 1},       "reward": 500},
}

# ランダムイベント設定
EVENT_CONFIG = {
    "min_interval": 600,
    "max_interval": 1200,
}
