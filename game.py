"""
ゲームメインロジック
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import pygame

from achievement_manager import AchievementManager
from animations import AnimationManager
from character_manager import CharacterManager
from event_manager import EventManager
from player import Player
from save_manager import SaveManager
from settings import (
    AFFECTION,
    AUTO_SAVE_INTERVAL,
    CHARACTER,
    COLORS,
    FONT_SIZES,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    UI_LAYOUT,
)
from sound_manager import SoundManager
from ui import (
    AchievementPanel,
    AffectionBar,
    Button,
    CharacterSelectPanel,
    SettingsPanel,
    ToastNotification,
    UpgradePanel,
)


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
        self.char_mgr: CharacterManager = CharacterManager()
        self.achievement_mgr: AchievementManager = AchievementManager()
        self.event_mgr: EventManager = EventManager()

        # UI初期化
        self._init_ui()

        # キャラクター
        self.character_rect: pygame.Rect = pygame.Rect(
            CHARACTER["position"][0],
            CHARACTER["position"][1],
            CHARACTER["size"][0],
            CHARACTER["size"][1],
        )
        self._refresh_character_image()

        # ゲーム状態
        self.auto_save_timer: float = 0.0
        self.auto_earn_accumulator: float = 0.0
        self.settings_open: bool = False

        # セーブデータ読み込み
        self._load_game()

        # サウンド読み込み
        self._load_sounds()

        # デイリーログインチェック
        self._check_daily_login()

    def _load_fonts(self) -> dict[str, pygame.font.Font]:
        """フォントを読み込み"""
        fonts: dict[str, pygame.font.Font] = {}
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
            self.fonts,
        )

        # 設定ボタン
        settings_pos: tuple[int, int] = UI_LAYOUT["settings_button"]
        self.settings_button: Button = Button(
            settings_pos[0] - 40, settings_pos[1] - 15,
            80, 30, "[設定]", self.fonts["small"],
            COLORS["secondary"], COLORS["primary"],
        )

        # キャラ切替ボタン
        self.char_button: Button = Button(
            settings_pos[0] - 140, settings_pos[1] - 15,
            80, 30, "[キャラ]", self.fonts["small"],
            COLORS["accent"], COLORS["primary"],
        )

        # 実績ボタン
        self.achievement_button: Button = Button(
            settings_pos[0] - 240, settings_pos[1] - 15,
            80, 30, "[実績]", self.fonts["small"],
            COLORS["success"], COLORS["primary"],
        )

        # パネル類
        self.settings_panel: SettingsPanel = SettingsPanel(
            SCREEN_WIDTH, SCREEN_HEIGHT, self.fonts,
        )
        self.char_select_panel: CharacterSelectPanel = CharacterSelectPanel(
            SCREEN_WIDTH, SCREEN_HEIGHT, self.fonts,
        )
        self.achievement_panel: AchievementPanel = AchievementPanel(
            SCREEN_WIDTH, SCREEN_HEIGHT, self.fonts,
        )

        # 好感度バー
        self.affection_bar: AffectionBar = AffectionBar(self.fonts)

        # トースト通知
        self.toast: ToastNotification = ToastNotification(self.fonts)

    def _refresh_character_image(self) -> None:
        """現在のキャラクターで画像を再生成"""
        self.character_image: pygame.Surface = self.char_mgr.create_character_surface(
            CHARACTER["size"]
        )

    def _load_sounds(self) -> None:
        """サウンドを読み込み"""
        self.sound_manager.load_all_sounds()
        bgm_path: str = "assets/music/bgm.wav"
        if self.sound_manager.load_bgm(bgm_path):
            self.sound_manager.play_bgm()

    def _load_game(self) -> None:
        """ゲームデータを読み込み"""
        data: dict[str, Any] | None = self.save_manager.load()
        if data:
            if "player" in data:
                self.player.from_dict(data["player"])
            if "characters" in data:
                self.char_mgr.from_dict(data["characters"])
            if "achievements" in data:
                self.achievement_mgr.from_dict(data["achievements"])
            if "events" in data:
                self.event_mgr.from_dict(data["events"])
            if "settings" in data:
                settings: dict[str, Any] = data["settings"]
                self.sound_manager.set_bgm_volume(settings.get("bgm_volume", 0.5))
                self.sound_manager.set_sfx_volume(settings.get("sfx_volume", 0.7))
                self.settings_panel.set_volumes(
                    settings.get("bgm_volume", 0.5),
                    settings.get("sfx_volume", 0.7),
                )
            # オフライン収益
            if "last_played" in data:
                offline_earnings: float = self.save_manager.calculate_offline_earnings(
                    self.player, data["last_played"]
                )
                if offline_earnings > 0:
                    self.player.add_points(offline_earnings)
                    self.achievement_mgr.mark_offline()
                    self.animation_manager.add_popup(
                        f"お帰りなさい！ +{int(offline_earnings):,}pt",
                        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                        self.fonts["large"], COLORS["gold"],
                    )
        # キャラ画像を最新状態で再生成
        self._refresh_character_image()

    def _save_game(self) -> None:
        """ゲームデータを保存"""
        settings: dict[str, float] = {
            "bgm_volume": self.sound_manager.get_bgm_volume(),
            "sfx_volume": self.sound_manager.get_sfx_volume(),
        }
        extra: dict[str, Any] = {
            "characters": self.char_mgr.to_dict(),
            "achievements": self.achievement_mgr.to_dict(),
            "events": self.event_mgr.to_dict(),
        }
        self.save_manager.save(self.player, settings, extra)

    def _check_daily_login(self) -> None:
        """デイリーログイン好感度"""
        data = self.save_manager.load()
        today = datetime.now().strftime("%Y-%m-%d")
        last_login = ""
        if data:
            last_login = data.get("daily_login", "")
        if last_login != today:
            self.char_mgr.add_affection(AFFECTION["gains"]["daily_login"])
            self.toast.push("デイリーボーナス！好感度UP")

    # ------------------------------------------------------------------
    # イベント処理
    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        """イベント処理"""
        # モーダルパネルが開いている場合
        if self.settings_panel.is_visible:
            result: dict[str, Any] | None = self.settings_panel.handle_event(event)
            if result:
                if "bgm_volume" in result:
                    self.sound_manager.set_bgm_volume(result["bgm_volume"])
                if "sfx_volume" in result:
                    self.sound_manager.set_sfx_volume(result["sfx_volume"])
            return

        if self.char_select_panel.is_visible:
            selected = self.char_select_panel.handle_event(event, self.char_mgr)
            if selected:
                self.char_mgr.switch_character(selected)
                self._refresh_character_image()
            return

        if self.achievement_panel.is_visible:
            self.achievement_panel.handle_event(event)
            return

        # ヘッダーボタン
        if self.settings_button.handle_event(event):
            self.settings_panel.show()
            return
        if self.char_button.handle_event(event):
            self.char_select_panel.show()
            return
        if self.achievement_button.handle_event(event):
            self.achievement_panel.show()
            return

        # イベントアラートクリック
        if self.event_mgr.showing_alert:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.event_mgr.dismiss_alert()
                return

        # イベント中のターゲットクリック
        if self.event_mgr.current_event is not None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.event_mgr.handle_click(event.pos):
                    self.sound_manager.play_sound("click")
                    self.animation_manager.add_particles(event.pos[0], event.pos[1], 8)
                    return

        # アップグレードパネル (イベント中は操作不可)
        if self.event_mgr.current_event is None:
            upgrade_id: str | None = self.upgrade_panel.handle_event(event, self.player)
            if upgrade_id:
                if self.player.purchase_upgrade(upgrade_id):
                    self.sound_manager.play_sound("upgrade")
                    self.char_mgr.add_affection(AFFECTION["gains"]["upgrade"])
                    self.animation_manager.add_particles(
                        self.character_rect.centerx,
                        self.character_rect.centery, 15,
                    )
                    self._check_achievements()
                return

        # キャラクタークリック
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.character_rect.collidepoint(event.pos):
                    self._on_character_click(event.pos)

    def _on_character_click(self, pos: tuple[int, int]) -> None:
        """キャラクタークリック時の処理"""
        multiplier = self.event_mgr.get_click_multiplier()
        points, lucky = self.player.click(multiplier)

        # 好感度
        self.char_mgr.add_affection(AFFECTION["gains"]["click"])

        # ラッキー実績
        if lucky:
            self.achievement_mgr.mark_lucky()

        # サウンド
        self.sound_manager.play_sound("click")

        # アニメーション
        self.animation_manager.trigger_click()

        # 好感度レベルに応じたエフェクト
        aff_level = self.char_mgr.get_affection_level()
        popup_color = COLORS["gold"]
        if multiplier > 1:
            popup_color = (255, 100, 100)
        self.animation_manager.add_popup(
            f"+{points}", pos[0], pos[1] - 30,
            self.fonts["medium"], popup_color,
        )

        if aff_level >= 2:
            # ハートパーティクル
            self.animation_manager.add_particles(pos[0], pos[1], 5)
        if aff_level >= 3:
            self.animation_manager.add_particles(pos[0], pos[1] - 20, 8)

        # ボーナス時
        base_power = self.player.get_click_power() * multiplier
        if points > base_power:
            self.sound_manager.play_sound("bonus")
            self.animation_manager.add_particles(pos[0], pos[1], 20)

        # キャラ画像更新 (表情変化の反映)
        self._refresh_character_image()
        self._check_achievements()

    # ------------------------------------------------------------------
    # 更新
    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        """更新"""
        # アニメーション更新
        self.animation_manager.update(dt)

        # キャラアイドルアニメーション
        self.char_mgr.update_idle(dt)

        # トースト通知
        self.toast.update(dt)

        # 自動収益
        auto_rate: float = self.player.get_auto_rate()
        if auto_rate > 0:
            self.auto_earn_accumulator += auto_rate * dt
            if self.auto_earn_accumulator >= 1.0:
                earned: int = int(self.auto_earn_accumulator)
                self.player.add_points(earned)
                self.auto_earn_accumulator -= earned

        # ランダムイベント更新
        event_result = self.event_mgr.update(dt)
        if event_result is not None:
            self._on_event_finished(event_result)

        # キャラ解放チェック
        newly_unlocked = self.char_mgr.check_unlocks(
            self.player, self.achievement_mgr.count()
        )
        for cid in newly_unlocked:
            from settings import CHARACTERS
            name = CHARACTERS[cid]["name"]
            self.toast.push(f"新キャラ解放！ {name}")

        # オートセーブ
        self.auto_save_timer += dt
        if self.auto_save_timer >= AUTO_SAVE_INTERVAL:
            self._save_game()
            self.auto_save_timer = 0.0

    def _on_event_finished(self, result: dict[str, Any]) -> None:
        """イベント完了時処理"""
        self.achievement_mgr.mark_event()
        if result["success"]:
            self.char_mgr.add_affection(AFFECTION["gains"]["event_success"])
            ev_type = result["type"]
            reward = 0
            if ev_type == "gold_rush":
                self.toast.push("ゴールドラッシュ終了！")
            elif ev_type == "shooting_star":
                reward = self.player.get_click_power() * 50
                self.toast.push(f"流れ星 +{reward:,}pt！")
            elif ev_type == "flower_field":
                reward = self.player.get_click_power() * 30
                self.toast.push(f"お花畑 +{reward:,}pt！")
            elif ev_type == "rainbow_visitor":
                self.char_mgr.add_affection(3.0)
                self.toast.push("虹の訪問者 好感度大幅UP！")
            if reward > 0:
                self.player.add_points(reward)
        else:
            self.toast.push("イベント失敗...")
        self._check_achievements()

    def _check_achievements(self) -> None:
        """実績チェックと通知"""
        newly = self.achievement_mgr.check_all(self.player, self.char_mgr)
        for ach in newly:
            self.player.add_points(ach["reward"])
            self.toast.push(f"実績達成！ {ach['name']} +{ach['reward']:,}pt")
            self.sound_manager.play_sound("upgrade")

    # ------------------------------------------------------------------
    # 描画
    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface) -> None:
        """描画"""
        # キャラクター描画
        self._draw_character(screen)

        # 好感度バー
        self.affection_bar.draw(
            screen,
            self.character_rect.centerx,
            self.character_rect.bottom + 10,
            self.char_mgr,
        )

        # ポイント表示
        self._draw_points(screen)

        # ステータス表示
        self._draw_stats(screen)

        # アップグレードパネル
        self.upgrade_panel.draw(screen, self.player)

        # ヘッダーボタン
        self.settings_button.draw(screen)
        self.char_button.draw(screen)
        self.achievement_button.draw(screen)

        # ランダムイベント
        self.event_mgr.draw(screen, self.fonts)

        # アニメーション
        self.animation_manager.draw(screen)

        # トースト通知
        self.toast.draw(screen)

        # モーダルパネル（最前面）
        self.settings_panel.draw(screen)
        self.char_select_panel.draw(screen, self.char_mgr)
        self.achievement_panel.draw(
            screen,
            self.achievement_mgr.unlocked,
            self.player,
            self.char_mgr,
        )

    def _draw_character(self, screen: pygame.Surface) -> None:
        """キャラクター描画"""
        scale_x, scale_y = self.animation_manager.get_click_scale()
        idle_y = self.char_mgr.get_idle_offset_y()

        img = self.character_image
        if scale_x != 1.0 or scale_y != 1.0:
            scaled_size: tuple[int, int] = (
                int(CHARACTER["size"][0] * scale_x),
                int(CHARACTER["size"][1] * scale_y),
            )
            img = pygame.transform.scale(self.character_image, scaled_size)
            rect: pygame.Rect = img.get_rect(
                center=(self.character_rect.centerx, self.character_rect.centery + int(idle_y))
            )
            screen.blit(img, rect)
        else:
            screen.blit(
                img,
                (self.character_rect.x, self.character_rect.y + int(idle_y)),
            )

    def _draw_points(self, screen: pygame.Surface) -> None:
        """ポイント表示"""
        pos: tuple[int, int] = UI_LAYOUT["points_display"]
        bg_rect: pygame.Rect = pygame.Rect(pos[0] - 150, pos[1] - 30, 300, 70)
        pygame.draw.rect(screen, (*COLORS["white"], 200), bg_rect, border_radius=15)

        points_text: str = f"{int(self.player.points):,}"
        points_surface: pygame.Surface = self.fonts["xlarge"].render(
            points_text, True, COLORS["text"]
        )
        points_rect: pygame.Rect = points_surface.get_rect(center=(pos[0], pos[1]))
        screen.blit(points_surface, points_rect)

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
