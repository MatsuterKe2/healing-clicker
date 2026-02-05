"""
UI部品（ボタン、スライダー、アップグレードパネル等）
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame

from settings import ACHIEVEMENTS, AFFECTION, CHARACTERS, COLORS, UPGRADES

if TYPE_CHECKING:
    from character_manager import CharacterManager
    from player import Player


class Button:
    """汎用ボタンクラス"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int] | None = None,
        hover_color: tuple[int, int, int] | None = None,
        text_color: tuple[int, int, int] | None = None,
        border_radius: int = 10,
    ) -> None:
        """初期化"""
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.text: str = text
        self.font: pygame.font.Font = font
        self.color: tuple[int, int, int] = color or COLORS["primary"]
        self.hover_color: tuple[int, int, int] = hover_color or COLORS["secondary"]
        self.text_color: tuple[int, int, int] = text_color or COLORS["text"]
        self.border_radius: int = border_radius
        self.is_hovered: bool = False
        self.is_enabled: bool = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理 - クリックされたらTrueを返す"""
        if not self.is_enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        """描画"""
        # 背景色選択
        bg_color: tuple[int, int, int]
        if not self.is_enabled:
            bg_color = COLORS["text_light"]
        elif self.is_hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.color

        # 背景描画
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=self.border_radius)

        # 枠線
        pygame.draw.rect(surface, COLORS["text"], self.rect, 2, border_radius=self.border_radius)

        # テキスト描画
        text_surface: pygame.Surface = self.font.render(self.text, True, self.text_color)
        text_rect: pygame.Rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def set_enabled(self, enabled: bool) -> None:
        """有効/無効を設定"""
        self.is_enabled = enabled


class Slider:
    """スライダーUIクラス"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        min_val: float = 0.0,
        max_val: float = 1.0,
        initial_val: float = 0.5,
        label: str = "",
    ) -> None:
        """初期化"""
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.min_val: float = min_val
        self.max_val: float = max_val
        self.value: float = initial_val
        self.label: str = label
        self.is_dragging: bool = False
        self.knob_radius: int = height

    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理 - 値が変更されたらTrueを返す"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                knob_x: int = self._get_knob_x()
                knob_rect: pygame.Rect = pygame.Rect(
                    knob_x - self.knob_radius,
                    self.rect.y - self.knob_radius // 2,
                    self.knob_radius * 2,
                    self.knob_radius * 2
                )
                if knob_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                    self.is_dragging = True
                    self._update_value(event.pos[0])
                    return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self._update_value(event.pos[0])
                return True
        return False

    def _get_knob_x(self) -> int:
        """つまみのX座標を取得"""
        ratio: float = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + ratio * self.rect.width)

    def _update_value(self, mouse_x: int) -> None:
        """マウスX座標から値を更新"""
        ratio: float = (mouse_x - self.rect.x) / self.rect.width
        ratio = max(0.0, min(1.0, ratio))
        self.value = self.min_val + ratio * (self.max_val - self.min_val)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """描画"""
        # ラベル描画
        if self.label:
            label_surface: pygame.Surface = font.render(self.label, True, COLORS["text"])
            surface.blit(label_surface, (self.rect.x, self.rect.y - 25))

        # トラック描画
        pygame.draw.rect(surface, COLORS["text_light"], self.rect, border_radius=5)

        # 塗りつぶし部分
        filled_width: int = int(self.rect.width * (self.value - self.min_val) / (self.max_val - self.min_val))
        filled_rect: pygame.Rect = pygame.Rect(self.rect.x, self.rect.y, filled_width, self.rect.height)
        pygame.draw.rect(surface, COLORS["primary"], filled_rect, border_radius=5)

        # つまみ描画
        knob_x: int = self._get_knob_x()
        pygame.draw.circle(
            surface,
            COLORS["white"],
            (knob_x, self.rect.centery),
            self.knob_radius
        )
        pygame.draw.circle(
            surface,
            COLORS["text"],
            (knob_x, self.rect.centery),
            self.knob_radius,
            2
        )

        # 値表示
        value_text: str = f"{int(self.value * 100)}%"
        value_surface: pygame.Surface = font.render(value_text, True, COLORS["text"])
        surface.blit(value_surface, (self.rect.right + 10, self.rect.y - 5))

    def get_value(self) -> float:
        """現在の値を取得"""
        return self.value

    def set_value(self, value: float) -> None:
        """値を設定"""
        self.value = max(self.min_val, min(self.max_val, value))


class UpgradePanel:
    """アップグレードパネルクラス"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        fonts: dict[str, pygame.font.Font],
    ) -> None:
        """初期化"""
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.fonts: dict[str, pygame.font.Font] = fonts
        self.buttons: dict[str, UpgradeButton] = {}
        self.scroll_offset: int = 0
        self._create_buttons()

    def _create_buttons(self) -> None:
        """アップグレードボタンを作成"""
        button_height: int = 80
        padding: int = 10
        y_offset: int = self.rect.y + padding

        for upgrade_id, upgrade in UPGRADES.items():
            button: UpgradeButton = UpgradeButton(
                self.rect.x + padding,
                y_offset,
                self.rect.width - padding * 2,
                button_height,
                upgrade_id,
                upgrade,
                self.fonts
            )
            self.buttons[upgrade_id] = button
            y_offset += button_height + padding

    def handle_event(self, event: pygame.event.Event, player: Player) -> str | None:
        """イベント処理 - 購入されたアップグレードIDを返す"""
        for upgrade_id, button in self.buttons.items():
            button.update_state(player)
            if button.handle_event(event):
                if player.can_afford_upgrade(upgrade_id):
                    return upgrade_id
        return None

    def draw(self, surface: pygame.Surface, player: Player) -> None:
        """描画"""
        # パネル背景
        panel_surface: pygame.Surface = pygame.Surface(
            (self.rect.width, self.rect.height), pygame.SRCALPHA
        )
        pygame.draw.rect(
            panel_surface,
            (*COLORS["white"], 200),
            (0, 0, self.rect.width, self.rect.height),
            border_radius=15
        )
        surface.blit(panel_surface, self.rect.topleft)

        # タイトル
        title_font: pygame.font.Font = self.fonts["medium"]
        title_text: pygame.Surface = title_font.render("アップグレード", True, COLORS["text"])
        surface.blit(title_text, (self.rect.x + 20, self.rect.y + 10))

        # ボタン描画
        for upgrade_id, button in self.buttons.items():
            button.update_state(player)
            button.draw(surface, player)


class UpgradeButton:
    """アップグレードボタン"""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        upgrade_id: str,
        upgrade: dict[str, Any],
        fonts: dict[str, pygame.font.Font],
    ) -> None:
        """初期化"""
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.upgrade_id: str = upgrade_id
        self.upgrade: dict[str, Any] = upgrade
        self.fonts: dict[str, pygame.font.Font] = fonts
        self.is_hovered: bool = False
        self.can_afford: bool = False

    def update_state(self, player: Player) -> None:
        """状態を更新"""
        self.can_afford = player.can_afford_upgrade(self.upgrade_id)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface, player: Player) -> None:
        """描画"""
        # 背景色
        bg_color: tuple[int, int, int]
        if self.can_afford:
            if self.is_hovered:
                bg_color = COLORS["success"]
            else:
                bg_color = COLORS["primary"]
        else:
            bg_color = COLORS["text_light"]

        # 背景描画
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)

        # 名前
        name_font: pygame.font.Font = self.fonts["small"]
        name_text: pygame.Surface = name_font.render(self.upgrade["name"], True, COLORS["text"])
        surface.blit(name_text, (self.rect.x + 10, self.rect.y + 8))

        # レベル
        level: int = player.upgrade_levels[self.upgrade_id]
        max_level: int | str = self.upgrade.get("max_level", "---")
        level_text: pygame.Surface = name_font.render(f"Lv.{level}/{max_level}", True, COLORS["text"])
        surface.blit(level_text, (self.rect.right - 70, self.rect.y + 8))

        # 説明
        desc_font: pygame.font.Font = self.fonts["small"]
        desc_text: pygame.Surface = desc_font.render(
            self.upgrade["description"], True, COLORS["text_light"]
        )
        surface.blit(desc_text, (self.rect.x + 10, self.rect.y + 32))

        # コスト
        cost: int = player.get_upgrade_cost(self.upgrade_id)
        cost_color: tuple[int, int, int] = COLORS["gold"] if self.can_afford else COLORS["warning"]
        cost_text: pygame.Surface = name_font.render(f"Cost: {cost:,}", True, cost_color)
        surface.blit(cost_text, (self.rect.x + 10, self.rect.y + 55))


class SettingsPanel:
    """設定パネル"""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        fonts: dict[str, pygame.font.Font],
    ) -> None:
        """初期化"""
        self.width: int = 400
        self.height: int = 300
        self.x: int = (screen_width - self.width) // 2
        self.y: int = (screen_height - self.height) // 2
        self.rect: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.fonts: dict[str, pygame.font.Font] = fonts
        self.is_visible: bool = False

        # スライダー
        self.bgm_slider: Slider = Slider(
            self.x + 30, self.y + 80, 250, 15,
            0.0, 1.0, 0.5, "BGM音量"
        )
        self.sfx_slider: Slider = Slider(
            self.x + 30, self.y + 150, 250, 15,
            0.0, 1.0, 0.7, "効果音音量"
        )

        # 閉じるボタン
        self.close_button: Button = Button(
            self.x + self.width // 2 - 60,
            self.y + self.height - 60,
            120, 40,
            "閉じる",
            fonts["small"]
        )

    def show(self) -> None:
        """表示"""
        self.is_visible = True

    def hide(self) -> None:
        """非表示"""
        self.is_visible = False

    def handle_event(self, event: pygame.event.Event) -> dict[str, Any] | None:
        """イベント処理 - 設定変更を返す"""
        if not self.is_visible:
            return None

        result: dict[str, Any] = {}

        if self.bgm_slider.handle_event(event):
            result["bgm_volume"] = self.bgm_slider.get_value()

        if self.sfx_slider.handle_event(event):
            result["sfx_volume"] = self.sfx_slider.get_value()

        if self.close_button.handle_event(event):
            self.hide()
            result["closed"] = True

        return result if result else None

    def draw(self, surface: pygame.Surface) -> None:
        """描画"""
        if not self.is_visible:
            return

        # 背景オーバーレイ
        overlay: pygame.Surface = pygame.Surface(
            (surface.get_width(), surface.get_height()), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))

        # パネル背景
        pygame.draw.rect(surface, COLORS["white"], self.rect, border_radius=15)
        pygame.draw.rect(surface, COLORS["text"], self.rect, 3, border_radius=15)

        # タイトル
        title_font: pygame.font.Font = self.fonts["large"]
        title_text: pygame.Surface = title_font.render("設定", True, COLORS["text"])
        title_rect: pygame.Rect = title_text.get_rect(centerx=self.rect.centerx, y=self.y + 20)
        surface.blit(title_text, title_rect)

        # スライダー
        self.bgm_slider.draw(surface, self.fonts["small"])
        self.sfx_slider.draw(surface, self.fonts["small"])

        # 閉じるボタン
        self.close_button.draw(surface)

    def set_volumes(self, bgm: float, sfx: float) -> None:
        """音量値を設定"""
        self.bgm_slider.set_value(bgm)
        self.sfx_slider.set_value(sfx)

    def get_volumes(self) -> tuple[float, float]:
        """音量値を取得"""
        return self.bgm_slider.get_value(), self.sfx_slider.get_value()


# ==================================================================
# キャラ切替パネル
# ==================================================================
class CharacterSelectPanel:
    """キャラクター選択パネル"""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        fonts: dict[str, pygame.font.Font],
    ) -> None:
        self.width: int = 500
        self.height: int = 420
        self.x: int = (screen_width - self.width) // 2
        self.y: int = (screen_height - self.height) // 2
        self.rect: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.fonts: dict[str, pygame.font.Font] = fonts
        self.is_visible: bool = False
        self.close_button: Button = Button(
            self.x + self.width // 2 - 60,
            self.y + self.height - 55,
            120, 40, "閉じる", fonts["small"],
        )

    def show(self) -> None:
        self.is_visible = True

    def hide(self) -> None:
        self.is_visible = False

    def handle_event(
        self, event: pygame.event.Event, char_mgr: CharacterManager
    ) -> str | None:
        """クリックされたキャラIDを返す。閉じるなら None"""
        if not self.is_visible:
            return None
        if self.close_button.handle_event(event):
            self.hide()
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, (cid, info) in enumerate(CHARACTERS.items()):
                card = self._card_rect(i)
                if card.collidepoint(event.pos) and cid in char_mgr.unlocked:
                    self.hide()
                    return cid
        return None

    def _card_rect(self, index: int) -> pygame.Rect:
        cols = 2
        card_w, card_h = 210, 140
        pad = 20
        col = index % cols
        row = index // cols
        cx = self.x + 30 + col * (card_w + pad)
        cy = self.y + 55 + row * (card_h + pad)
        return pygame.Rect(cx, cy, card_w, card_h)

    def draw(self, surface: pygame.Surface, char_mgr: CharacterManager) -> None:
        if not self.is_visible:
            return
        # オーバーレイ
        overlay = pygame.Surface(
            (surface.get_width(), surface.get_height()), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))
        # パネル背景
        pygame.draw.rect(surface, COLORS["white"], self.rect, border_radius=15)
        pygame.draw.rect(surface, COLORS["text"], self.rect, 3, border_radius=15)
        # タイトル
        title = self.fonts["large"].render("キャラクター", True, COLORS["text"])
        tr = title.get_rect(centerx=self.rect.centerx, y=self.y + 12)
        surface.blit(title, tr)
        # カード
        for i, (cid, info) in enumerate(CHARACTERS.items()):
            card = self._card_rect(i)
            unlocked = cid in char_mgr.unlocked
            is_current = cid == char_mgr.current_id
            if unlocked:
                bg = COLORS["primary"] if is_current else COLORS["accent"]
            else:
                bg = COLORS["text_light"]
            pygame.draw.rect(surface, bg, card, border_radius=10)
            pygame.draw.rect(surface, COLORS["text"], card, 2, border_radius=10)
            if unlocked:
                name_s = self.fonts["medium"].render(info["name"], True, COLORS["text"])
                surface.blit(name_s, (card.x + 10, card.y + 10))
                theme_s = self.fonts["small"].render(info["theme"], True, COLORS["text_light"])
                surface.blit(theme_s, (card.x + 10, card.y + 40))
                # 好感度
                aff = char_mgr.get_affection(cid)
                aff_lvl = char_mgr.get_affection_level_info(cid)
                aff_text = f"好感度: {aff:.0f} ({aff_lvl['name']})"
                aff_s = self.fonts["small"].render(aff_text, True, COLORS["text"])
                surface.blit(aff_s, (card.x + 10, card.y + 65))
                if is_current:
                    sel = self.fonts["small"].render("選択中", True, (255, 100, 100))
                    surface.blit(sel, (card.x + 10, card.y + 110))
            else:
                # シルエット + ヒント
                q = self.fonts["xlarge"].render("？", True, COLORS["white"])
                qr = q.get_rect(center=(card.centerx, card.y + 45))
                surface.blit(q, qr)
                cond = info["unlock_condition"]
                if cond:
                    hint = self._condition_hint(cond)
                    h_s = self.fonts["small"].render(hint, True, COLORS["text_light"])
                    surface.blit(h_s, (card.x + 10, card.y + 95))
        self.close_button.draw(surface)

    @staticmethod
    def _condition_hint(cond: dict[str, Any]) -> str:
        t, v = cond["type"], cond["value"]
        if t == "total_points":
            return f"累計 {v:,} pt 獲得で解放"
        if t == "total_clicks":
            return f"累計 {v:,} 回クリックで解放"
        if t == "achievements":
            return f"実績 {v} 個達成で解放"
        return "条件を満たすと解放"


# ==================================================================
# 好感度バー
# ==================================================================
class AffectionBar:
    """キャラ下に表示する好感度バー"""

    def __init__(self, fonts: dict[str, pygame.font.Font]) -> None:
        self.fonts = fonts

    def draw(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        char_mgr: CharacterManager,
    ) -> None:
        aff = char_mgr.get_affection()
        info = char_mgr.get_affection_level_info()
        bar_w, bar_h = 160, 12
        bx = x - bar_w // 2
        by = y
        # ハートアイコン(テキスト)
        heart = self.fonts["small"].render("♥", True, (255, 100, 130))
        surface.blit(heart, (bx - 22, by - 4))
        # バー背景
        pygame.draw.rect(surface, COLORS["text_light"], (bx, by, bar_w, bar_h), border_radius=6)
        # バー塗り
        fill_w = int(bar_w * aff / AFFECTION["max"])
        if fill_w > 0:
            pygame.draw.rect(surface, (255, 130, 160), (bx, by, fill_w, bar_h), border_radius=6)
        # レベル名
        lvl_s = self.fonts["small"].render(info["name"], True, COLORS["text"])
        surface.blit(lvl_s, (bx + bar_w + 8, by - 4))


# ==================================================================
# 実績パネル
# ==================================================================
class AchievementPanel:
    """実績一覧パネル"""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        fonts: dict[str, pygame.font.Font],
    ) -> None:
        self.width: int = 550
        self.height: int = 520
        self.x: int = (screen_width - self.width) // 2
        self.y: int = (screen_height - self.height) // 2
        self.rect: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.fonts: dict[str, pygame.font.Font] = fonts
        self.is_visible: bool = False
        self.scroll_offset: int = 0
        self.close_button: Button = Button(
            self.x + self.width // 2 - 60,
            self.y + self.height - 55,
            120, 40, "閉じる", fonts["small"],
        )

    def show(self) -> None:
        self.is_visible = True
        self.scroll_offset = 0

    def hide(self) -> None:
        self.is_visible = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.is_visible:
            return
        if self.close_button.handle_event(event):
            self.hide()
            return
        # スクロール
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * 30
            self.scroll_offset = max(0, self.scroll_offset)

    def draw(
        self,
        surface: pygame.Surface,
        unlocked_ids: list[str],
        player: Player,
        char_mgr: CharacterManager,
    ) -> None:
        if not self.is_visible:
            return
        # オーバーレイ
        overlay = pygame.Surface(
            (surface.get_width(), surface.get_height()), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))
        # パネル
        pygame.draw.rect(surface, COLORS["white"], self.rect, border_radius=15)
        pygame.draw.rect(surface, COLORS["text"], self.rect, 3, border_radius=15)
        # タイトル
        total = len(ACHIEVEMENTS)
        done = len(unlocked_ids)
        title = self.fonts["large"].render(f"実績  {done}/{total}", True, COLORS["text"])
        tr = title.get_rect(centerx=self.rect.centerx, y=self.y + 12)
        surface.blit(title, tr)
        # クリッピング領域
        list_area = pygame.Rect(self.x + 10, self.y + 55, self.width - 20, self.height - 120)
        surface.set_clip(list_area)
        row_h = 52
        iy = list_area.y - self.scroll_offset
        for aid, info in ACHIEVEMENTS.items():
            if iy + row_h < list_area.y:
                iy += row_h
                continue
            if iy > list_area.bottom:
                break
            achieved = aid in unlocked_ids
            # 行背景
            row_rect = pygame.Rect(list_area.x, iy, list_area.width, row_h - 4)
            bg = COLORS["accent"] if achieved else (*COLORS["text_light"], 80)
            pygame.draw.rect(surface, bg, row_rect, border_radius=8)
            # チェック / グレー
            mark = "✓" if achieved else "○"
            mark_c = COLORS["success"] if achieved else COLORS["text_light"]
            ms = self.fonts["medium"].render(mark, True, mark_c)
            surface.blit(ms, (row_rect.x + 8, iy + 4))
            # 名前
            name_c = COLORS["text"] if achieved else COLORS["text_light"]
            ns = self.fonts["small"].render(info["name"], True, name_c)
            surface.blit(ns, (row_rect.x + 40, iy + 4))
            # 報酬
            rw = self.fonts["small"].render(f"+{info['reward']:,}pt", True, COLORS["gold"])
            surface.blit(rw, (row_rect.right - 80, iy + 4))
            # 進捗バー (未達成)
            if not achieved:
                prog = self._get_progress(aid, info, player, char_mgr)
                if prog is not None:
                    bar_w = 160
                    bar_rect = pygame.Rect(row_rect.x + 40, iy + 28, bar_w, 8)
                    pygame.draw.rect(surface, COLORS["white"], bar_rect, border_radius=4)
                    fw = int(bar_w * min(1.0, prog))
                    if fw > 0:
                        pygame.draw.rect(
                            surface, COLORS["primary"],
                            (bar_rect.x, bar_rect.y, fw, 8), border_radius=4,
                        )
            iy += row_h
        # クリップ解除
        surface.set_clip(None)
        self.close_button.draw(surface)

    def _get_progress(
        self, aid: str, info: dict[str, Any], player: Player, char_mgr: CharacterManager
    ) -> float | None:
        cond = info["condition"]
        t, v = cond["type"], cond["value"]
        if t == "total_clicks":
            return player.total_clicks / v
        if t == "total_points":
            return player.total_points_earned / v
        if t == "total_upgrades":
            return sum(player.upgrade_levels.values()) / v
        if t == "max_affection":
            return char_mgr.get_max_affection() / v
        return None


# ==================================================================
# トースト通知
# ==================================================================
class ToastNotification:
    """画面上部からスライドインするトースト"""

    def __init__(self, fonts: dict[str, pygame.font.Font]) -> None:
        self.fonts = fonts
        self._queue: list[dict[str, Any]] = []
        self._current: dict[str, Any] | None = None
        self._timer: float = 0.0
        self._show_duration: float = 3.0
        self._slide_duration: float = 0.3

    def push(self, text: str, color: tuple[int, int, int] | None = None) -> None:
        self._queue.append({"text": text, "color": color or COLORS["gold"]})

    def update(self, dt: float) -> None:
        if self._current is None:
            if self._queue:
                self._current = self._queue.pop(0)
                self._timer = 0.0
            return
        self._timer += dt
        if self._timer >= self._show_duration + self._slide_duration:
            self._current = None

    def draw(self, surface: pygame.Surface) -> None:
        if self._current is None:
            return
        t = self._timer
        # スライドイン
        if t < self._slide_duration:
            ratio = t / self._slide_duration
            y = int(-50 + 60 * ratio)
        elif t < self._show_duration:
            y = 10
        else:
            ratio = (t - self._show_duration) / self._slide_duration
            y = int(10 - 60 * ratio)
        banner_w = 450
        bx = (surface.get_width() - banner_w) // 2
        banner = pygame.Rect(bx, y, banner_w, 44)
        pygame.draw.rect(surface, (*COLORS["white"], 230), banner, border_radius=12)
        pygame.draw.rect(surface, self._current["color"], banner, 2, border_radius=12)
        ts = self.fonts["medium"].render(self._current["text"], True, self._current["color"])
        tr = ts.get_rect(center=banner.center)
        surface.blit(ts, tr)
