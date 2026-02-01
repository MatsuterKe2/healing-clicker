"""
癒し系クリッカーゲーム - エントリーポイント
"""

from __future__ import annotations

import sys

import pygame

from settings import COLORS, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE


def main() -> None:
    """メイン関数"""
    # Pygame初期化
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error as e:
        print(f"オーディオ初期化をスキップ: {e}")

    # ウィンドウ設定
    screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)

    # クロック設定
    clock: pygame.time.Clock = pygame.time.Clock()

    # ゲームインスタンス作成
    from game import Game
    game: Game = Game(screen)

    # メインゲームループ
    running: bool = True
    while running:
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)

        # 更新
        dt: float = clock.tick(FPS) / 1000.0  # 秒に変換
        game.update(dt)

        # 描画
        screen.fill(COLORS["background"])
        game.draw(screen)
        pygame.display.flip()

    # 終了処理
    game.cleanup()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
