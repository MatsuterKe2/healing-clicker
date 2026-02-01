"""
ゲームメインロジック
"""

from __future__ import annotations

import os
from typing import Any

import pygame

from animations import AnimationManager
from player import Player
from save_manager import SaveManager
from settings import (
    AUTO_SAVE_INTERVAL,
    CHARACTER,
    COLORS,
    FONT_SIZES,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    UI_LAYOUT,
)
from sound_manager import SoundManager
from ui import Button, SettingsPanel, UpgradePanel


class Game:
    """ゲームメインクラス"""

    def __init__(self, screen: pygame.Surface) -> None:
        """初期化"""
        self.screen: pygame.Surface = screen
        self.running: bool = True

        # フォント初期化
        self.fonts: dict[str, pygame.font.Font] = self._load_fonts()

        # コンポーネント初期化
        self.player: Player = Player()
        self.save_manager: SaveManager = SaveManager()
        self.sound_manager: SoundManager = SoundManager()
        self.animation_manager: AnimationManager = AnimationManager()

        # UI初期化
        self._init_ui()

        # キャラクター
        self.character_rect: pygame.Rect = pygame.Rect(
            CHARACTER["position"][0],
            CHARACTER["position"][1],
            CHARACTER["size"][0],
            CHARACTER["size"][1]
        )
        self.character_image: pygame.Surface = self._create_placeholder_character()

        # ゲーム状態
        self.auto_save_timer: float = 0.0
        self.auto_earn_accumulator: float = 0.0
        self.settings_open: bool = False

        # セーブデータ読み込み
        self._load_game()

        # サウンド読み込み
        self._load_sounds()

    def _load_fonts(self) -> dict[str, pygame.font.Font]:
        """フォントを読み込み"""
        fonts: dict[str, pygame.font.Font] = {}

        # システムフォントまたはカスタムフォントを試す
        font_paths: list[str] = [
            "assets/fonts/NotoSansCJKjp-Regular.otf",
            "assets/fonts/NotoSansJP-Regular.ttf",
            "assets/fonts/mplus-1p-regular.ttf",
        ]

        font_path: str | None = None
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                break

        for size_name, size in FONT_SIZES.items():
            try:
                if font_path:
                    fonts[size_name] = pygame.font.Font(font_path, size)
                else:
                    # フォールバック: システムフォント
                    fonts[size_name] = pygame.font.SysFont(
                        "notosanscjkjp,meiryoui,msgothic", size
                    )
            except Exception:
                fonts[size_name] = pygame.font.Font(None, size)

        return fonts

    def _init_ui(self) -> None:
        """UI初期化"""
        # アップグレードパネル
        panel: dict[str, int] = UI_LAYOUT["upgrade_panel"]
        self.upgrade_panel: UpgradePanel = UpgradePanel(
            panel["x"], panel["y"],
            panel["width"], panel["height"],
            self.fonts
        )

        # 設定ボタン
        settings_pos: tuple[int, int] = UI_LAYOUT["settings_button"]
        self.settings_button: Button = Button(
            settings_pos[0] - 40, settings_pos[1] - 15,
            80, 30,
            "[設定]",
            self.fonts["small"],
            COLORS["secondary"],
            COLORS["primary"]
        )

        # 設定パネル
        self.settings_panel: SettingsPanel = SettingsPanel(
            SCREEN_WIDTH, SCREEN_HEIGHT, self.fonts
        )

    def _create_placeholder_character(self) -> pygame.Surface:
        """プレースホルダーキャラクター画像を作成"""
        # 画像ファイルを試す
        image_path: str = "assets/images/character.png"
        if os.path.exists(image_path):
            try:
                img: pygame.Surface = pygame.image.load(image_path)
                return pygame.transform.scale(img, CHARACTER["size"])
            except Exception:
                pass

        # フォールバック: 簡易的な丸いキャラクター
        size: tuple[int, int] = CHARACTER["size"]
        surface: pygame.Surface = pygame.Surface(size, pygame.SRCALPHA)

        # 体 (大きな円)
        pygame.draw.circle(
            surface, COLORS["primary"],
            (size[0] // 2, size[1] // 2), size[0] // 2 - 10
        )

        # 顔の輪郭
        pygame.draw.circle(
            surface, COLORS["accent"],
            (size[0] // 2, size[1] // 2 - 20), size[0] // 3
        )

        # 目
        eye_y: int = size[1] // 2 - 30
        pygame.draw.circle(surface, COLORS["black"], (size[0] // 2 - 25, eye_y), 8)
        pygame.draw.circle(surface, COLORS["black"], (size[0] // 2 + 25, eye_y), 8)
        pygame.draw.circle(surface, COLORS["white"], (size[0] // 2 - 23, eye_y - 2), 3)
        pygame.draw.circle(surface, COLORS["white"], (size[0] // 2 + 27, eye_y - 2), 3)

        # 頬 (ピンクの円)
        pygame.draw.circle(surface, (255, 200, 200), (size[0] // 2 - 40, eye_y + 20), 12)
        pygame.draw.circle(surface, (255, 200, 200), (size[0] // 2 + 40, eye_y + 20), 12)

        # 口 (にっこり)
        pygame.draw.arc(
            surface, COLORS["text"],
            (size[0] // 2 - 20, eye_y + 10, 40, 30),
            3.14, 0, 3
        )

        return surface

    def _load_sounds(self) -> None:
        """サウンドを読み込み"""
        self.sound_manager.load_all_sounds()

        # BGM読み込み
        bgm_path: str = "assets/music/bgm.wav"
        if self.sound_manager.load_bgm(bgm_path):
            self.sound_manager.play_bgm()

    def _load_game(self) -> None:
        """ゲームデータを読み込み"""
        data: dict[str, Any] | None = self.save_manager.load()
        if data:
            # プレイヤーデータ復元
            if "player" in data:
                self.player.from_dict(data["player"])

            # 設定復元
            if "settings" in data:
                settings: dict[str, Any] = data["settings"]
                self.sound_manager.set_bgm_volume(settings.get("bgm_volume", 0.5))
                self.sound_manager.set_sfx_volume(settings.get("sfx_volume", 0.7))
                self.settings_panel.set_volumes(
                    settings.get("bgm_volume", 0.5),
                    settings.get("sfx_volume", 0.7)
                )

            # オフライン収益計算
            if "last_played" in data:
                offline_earnings: float = self.save_manager.calculate_offline_earnings(
                    self.player, data["last_played"]
                )
                if offline_earnings > 0:
                    self.player.add_points(offline_earnings)
                    # オフライン収益通知用ポップアップ
                    self.animation_manager.add_popup(
                        f"お帰りなさい！ +{int(offline_earnings):,}pt",
                        SCREEN_WIDTH // 2,
                        SCREEN_HEIGHT // 2,
                        self.fonts["large"],
                        COLORS["gold"]
                    )

    def _save_game(self) -> None:
        """ゲームデータを保存"""
        settings: dict[str, float] = {
            "bgm_volume": self.sound_manager.get_bgm_volume(),
            "sfx_volume": self.sound_manager.get_sfx_volume(),
        }
        self.save_manager.save(self.player, settings)

    def handle_event(self, event: pygame.event.Event) -> None:
        """イベント処理"""
        # 設定パネルが開いている場合
        if self.settings_panel.is_visible:
            result: dict[str, Any] | None = self.settings_panel.handle_event(event)
            if result:
                if "bgm_volume" in result:
                    self.sound_manager.set_bgm_volume(result["bgm_volume"])
                if "sfx_volume" in result:
                    self.sound_manager.set_sfx_volume(result["sfx_volume"])
            return

        # 設定ボタン
        if self.settings_button.handle_event(event):
            self.settings_panel.show()
            return

        # アップグレードパネル
        upgrade_id: str | None = self.upgrade_panel.handle_event(event, self.player)
        if upgrade_id:
            if self.player.purchase_upgrade(upgrade_id):
                self.sound_manager.play_sound("upgrade")
                # 購入エフェクト
                self.animation_manager.add_particles(
                    self.character_rect.centerx,
                    self.character_rect.centery,
                    15
                )
            return

        # キャラクタークリック
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                if self.character_rect.collidepoint(event.pos):
                    self._on_character_click(event.pos)

    def _on_character_click(self, pos: tuple[int, int]) -> None:
        """キャラクタークリック時の処理"""
        # ポイント獲得
        points: int = self.player.click()

        # サウンド
        self.sound_manager.play_sound("click")

        # アニメーション
        self.animation_manager.trigger_click()
        self.animation_manager.add_popup(
            f"+{points}",
            pos[0],
            pos[1] - 30,
            self.fonts["medium"],
            COLORS["gold"]
        )

        # ボーナス時は追加エフェクト
        if points > self.player.get_click_power():
            self.sound_manager.play_sound("bonus")
            self.animation_manager.add_particles(pos[0], pos[1], 20)

    def update(self, dt: float) -> None:
        """更新"""
        # アニメーション更新
        self.animation_manager.update(dt)

        # 自動収益
        auto_rate: float = self.player.get_auto_rate()
        if auto_rate > 0:
            self.auto_earn_accumulator += auto_rate * dt
            if self.auto_earn_accumulator >= 1.0:
                earned: int = int(self.auto_earn_accumulator)
                self.player.add_points(earned)
                self.auto_earn_accumulator -= earned

        # オートセーブ
        self.auto_save_timer += dt
        if self.auto_save_timer >= AUTO_SAVE_INTERVAL:
            self._save_game()
            self.auto_save_timer = 0.0

    def draw(self, screen: pygame.Surface) -> None:
        """描画"""
        # キャラクター描画
        self._draw_character(screen)

        # ポイント表示
        self._draw_points(screen)

        # ステータス表示
        self._draw_stats(screen)

        # アップグレードパネル
        self.upgrade_panel.draw(screen, self.player)

        # 設定ボタン
        self.settings_button.draw(screen)

        # アニメーション
        self.animation_manager.draw(screen)

        # 設定パネル（最前面）
        self.settings_panel.draw(screen)

    def _draw_character(self, screen: pygame.Surface) -> None:
        """キャラクター描画"""
        scale: float = self.animation_manager.get_click_scale()

        if scale != 1.0:
            # スケーリング
            scaled_size: tuple[int, int] = (
                int(CHARACTER["size"][0] * scale),
                int(CHARACTER["size"][1] * scale)
            )
            scaled_img: pygame.Surface = pygame.transform.scale(
                self.character_image, scaled_size
            )
            # 中心を維持
            rect: pygame.Rect = scaled_img.get_rect(center=self.character_rect.center)
            screen.blit(scaled_img, rect)
        else:
            screen.blit(self.character_image, self.character_rect)

    def _draw_points(self, screen: pygame.Surface) -> None:
        """ポイント表示"""
        pos: tuple[int, int] = UI_LAYOUT["points_display"]

        # 背景
        bg_rect: pygame.Rect = pygame.Rect(pos[0] - 150, pos[1] - 30, 300, 70)
        pygame.draw.rect(screen, (*COLORS["white"], 200), bg_rect, border_radius=15)

        # ポイント数
        points_text: str = f"{int(self.player.points):,}"
        points_surface: pygame.Surface = self.fonts["xlarge"].render(
            points_text, True, COLORS["text"]
        )
        points_rect: pygame.Rect = points_surface.get_rect(center=(pos[0], pos[1]))
        screen.blit(points_surface, points_rect)

        # ラベル
        label_surface: pygame.Surface = self.fonts["small"].render(
            "ポイント", True, COLORS["text_light"]
        )
        label_rect: pygame.Rect = label_surface.get_rect(center=(pos[0], pos[1] + 30))
        screen.blit(label_surface, label_rect)

    def _draw_stats(self, screen: pygame.Surface) -> None:
        """ステータス表示"""
        stats: list[str] = [
            f"クリック: +{self.player.get_click_power()}/回",
            f"自動: +{self.player.get_auto_rate():.1f}/秒",
        ]

        y: int = 150
        for stat in stats:
            text_surface: pygame.Surface = self.fonts["small"].render(
                stat, True, COLORS["text_light"]
            )
            screen.blit(text_surface, (50, y))
            y += 25

    def cleanup(self) -> None:
        """終了処理"""
        self._save_game()
        self.sound_manager.cleanup()
