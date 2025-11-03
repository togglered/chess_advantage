import asyncio
from bs4 import BeautifulSoup
from stockfish import Stockfish
from datetime import datetime
import traceback
import time
import chess
import re
from playwright.async_api import async_playwright

from pieces import PIECES

CHARS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']


def parse_color(soup: BeautifulSoup):
    players = soup.find_all(class_='player-component')
    if len(players) < 2:
        return chess.WHITE  # default fallback

    player_div = players[1]
    color_digit = player_div.find("wc-captured-pieces").get('player-color')
    if color_digit and int(color_digit) == 1:
        return chess.WHITE
    return chess.BLACK


def transform_position(position: str):
    horizontal_index = CHARS.index(position[0].upper()) + 1
    vertical_index = int(position[1])
    return f"{horizontal_index}{vertical_index}"


async def highlight_tile(page, tiles: str):
    from_tile = tiles[0:2].upper()
    to_tile = tiles[2:4].upper()

    from_position = transform_position(from_tile)
    to_position = transform_position(to_tile)

    js_code = f"""
    (() => {{
        const board = document.getElementById("board-single");
        if (!board) return;

        const existing = board.querySelectorAll(".best-move");

        if (existing.length >= 2) {{
            existing[0].className = 'highlight square-{from_position} best-move';
            existing[0].style.backgroundColor = 'red';
            existing[0].style.opacity = 0.3;

            existing[1].className = 'highlight square-{to_position} best-move';
            existing[1].style.backgroundColor = 'red';
            existing[1].style.opacity = 0.3;
        }} else {{
            const from_div = document.createElement('div');
            from_div.classList.add('highlight', 'square-{from_position}', 'best-move');
            from_div.style.backgroundColor = 'red';
            from_div.style.opacity = 0.3;
            board.appendChild(from_div);

            const to_div = document.createElement('div');
            to_div.classList.add('highlight', 'square-{to_position}', 'best-move');
            to_div.style.backgroundColor = 'red';
            to_div.style.opacity = 0.3;
            board.appendChild(to_div);
        }}
    }})();
    """

    await page.evaluate(js_code)


def parse_board(html: str):
    board = chess.Board(None)

    soup = BeautifulSoup(html, 'html.parser')
    for horizontal_index in range(1, 9):
        for vertical_index in range(1, 9):
            squares = soup.find_all(class_=f"square-{horizontal_index}{vertical_index}")
            for square in squares:
                piece_classes = square.get("class", [])
                if "piece" not in piece_classes:
                    continue

                position = (vertical_index - 1) * 8 + horizontal_index - 1

                for piece_class in piece_classes:
                    if piece_class in PIECES:
                        board.set_piece_at(position, PIECES[piece_class])
                        break

    color = parse_color(soup)
    board.turn = color
    return board


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        await page.goto("https://www.chess.com/")

        url_pattern = re.compile(r"^https://www\.chess\.com/.+$")

        while True:
            try:
                stockfish = Stockfish(path="stockfish_engine/stockfish-windows-x86-64-avx2.exe")
                
                url = page.url
                if not url_pattern.match(url):
                    await asyncio.sleep(5)
                    continue

                html = await page.content()
                board = parse_board(html)
                fen = board.fen()
                stockfish.set_fen_position(fen)

                best_move = stockfish.get_best_move()
                if best_move:
                    await highlight_tile(page, best_move)

                await asyncio.sleep(0.5)

            except Exception as e:
                print("Error:", e)
                traceback.print_exc()
                await asyncio.sleep(1)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
