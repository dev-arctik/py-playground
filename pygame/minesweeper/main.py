# Original repo: dev-arctik/python-minesweeper
# Merged from: cell.py, board.py, ui/renderer.py, game.py, main.py
import pygame
import pygame.font
import os
import random
import time
import asyncio


# --- Cell (from cell.py) ---

class Cell:
    def __init__(self):
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0

    def reveal(self):
        if not self.is_flagged:
            self.is_revealed = True
            return True
        return False

    def toggle_flag(self):
        if not self.is_revealed:
            self.is_flagged = not self.is_flagged
            return True
        return False

    def place_mine(self):
        self.is_mine = True

    def increment_adjacent(self):
        self.adjacent_mines += 1

    def __str__(self):
        if self.is_flagged:
            return "F"
        if not self.is_revealed:
            return "■"
        if self.is_mine:
            return "X"
        if self.adjacent_mines == 0:
            return " "
        return str(self.adjacent_mines)


# --- Board (from board.py) — uses plain lists instead of numpy ---

class Board:
    def __init__(self, width, height, num_mines):
        self.width = width
        self.height = height
        self.num_mines = min(num_mines, width * height - 1)
        self.first_move_made = False
        self.game_over = False
        self.win = False
        # Plain list of lists instead of np.array (avoids numpy dependency)
        self.grid = [[Cell() for _ in range(width)] for _ in range(height)]

    def place_mines(self, first_x, first_y):
        """Place mines randomly, ensuring first clicked cell and neighbors are safe."""
        positions = [(x, y) for x in range(self.width) for y in range(self.height)]

        # Build safe zone around first click
        safe_positions = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = first_x + dx, first_y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    safe_positions.append((nx, ny))

        mine_candidates = [pos for pos in positions if pos not in safe_positions]
        mine_positions = random.sample(mine_candidates, self.num_mines)

        for x, y in mine_positions:
            self.grid[y][x].place_mine()
            # Update neighbor counts
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and not (dx == 0 and dy == 0):
                        self.grid[ny][nx].increment_adjacent()

    def reveal_cell(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False

        if not self.first_move_made:
            self.place_mines(x, y)
            self.first_move_made = True

        cell = self.grid[y][x]
        if cell.is_revealed or cell.is_flagged:
            return False

        cell.reveal()

        if cell.is_mine:
            self.game_over = True
            return True

        # Flood-fill empty cells
        if cell.adjacent_mines == 0:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and not (dx == 0 and dy == 0):
                        self.reveal_cell(nx, ny)

        self.check_win()
        return True

    def toggle_flag(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.grid[y][x].toggle_flag()

    def chord(self, x, y):
        """Reveal all unflagged neighbors if flag count matches the cell's number."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False

        cell = self.grid[y][x]
        if not cell.is_revealed or cell.is_mine or cell.adjacent_mines == 0:
            return False

        adjacent_flags = 0
        adjacent_cells = []

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and not (dx == 0 and dy == 0):
                    adj = self.grid[ny][nx]
                    if adj.is_flagged:
                        adjacent_flags += 1
                    else:
                        adjacent_cells.append((nx, ny))

        if adjacent_flags == cell.adjacent_mines:
            # Check for incorrect flags — triggers game over
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and not (dx == 0 and dy == 0):
                        adj = self.grid[ny][nx]
                        if adj.is_flagged and not adj.is_mine:
                            adj.is_flagged = False
                            adj.reveal()
                            self.game_over = True
                            return True

            for nx, ny in adjacent_cells:
                self.reveal_cell(nx, ny)
            return True

        return False

    def check_win(self):
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if not cell.is_mine and not cell.is_revealed:
                    return False
        self.win = True
        return True

    def get_visible_board(self):
        return [[str(self.grid[y][x]) for x in range(self.width)] for y in range(self.height)]


# --- GameRenderer (from ui/renderer.py) ---

class GameRenderer:
    GRID_COLOR = (128, 128, 128)
    CELL_COLOR = (200, 200, 200)
    REVEALED_COLOR = (180, 180, 180)

    # Number colors (1=blue, 2=green, 3=red, etc.)
    NUMBER_COLORS = {
        1: (0, 0, 255), 2: (0, 128, 0), 3: (255, 0, 0), 4: (0, 0, 128),
        5: (128, 0, 0), 6: (0, 128, 128), 7: (0, 0, 0), 8: (128, 128, 128),
    }

    def __init__(self, width, height, cell_size=30, stats_height=40):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.stats_height = stats_height
        self.screen_width = width * cell_size
        self.screen_height = height * cell_size + stats_height

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Minesweeper")

        # Replaced SysFont('Arial', ...) — no system fonts in browser
        self.font = pygame.font.Font(None, cell_size // 2)
        self.stats_font = pygame.font.Font(None, 18)

        self.load_images()

    def load_images(self):
        # Asset paths updated: ui/assets/ → assets/ (flat structure for browser)
        bomb_path = os.path.join('assets', 'bomb.png')
        flag_path = os.path.join('assets', 'flag.png')

        target_size = int(self.cell_size * 0.8)

        if os.path.exists(bomb_path):
            self.bomb_img = pygame.transform.scale(pygame.image.load(bomb_path), (target_size, target_size))
        else:
            self.bomb_img = None

        if os.path.exists(flag_path):
            self.flag_img = pygame.transform.scale(pygame.image.load(flag_path), (target_size, target_size))
        else:
            self.flag_img = None

    def draw_board(self, board_state, game_over=False, win=False):
        # Fill the board area (not the stats bar)
        board_area = pygame.Rect(0, self.stats_height, self.screen_width, self.height * self.cell_size)
        self.screen.fill((255, 255, 255), board_area)

        for y in range(self.height):
            for x in range(self.width):
                cell = board_state[y][x]
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size + self.stats_height,
                    self.cell_size,
                    self.cell_size,
                )

                if cell == "■":
                    pygame.draw.rect(self.screen, self.CELL_COLOR, rect)
                elif cell == "F":
                    pygame.draw.rect(self.screen, self.CELL_COLOR, rect)
                    if self.flag_img:
                        self.screen.blit(self.flag_img, self.flag_img.get_rect(center=rect.center))
                    else:
                        # Fallback: orange square
                        flag_rect = pygame.Rect(
                            x * self.cell_size + self.cell_size // 4,
                            y * self.cell_size + self.stats_height + self.cell_size // 4,
                            self.cell_size // 2, self.cell_size // 2,
                        )
                        pygame.draw.rect(self.screen, (255, 165, 0), flag_rect)
                elif cell == "X":
                    pygame.draw.rect(self.screen, self.REVEALED_COLOR, rect)
                    if self.bomb_img:
                        self.screen.blit(self.bomb_img, self.bomb_img.get_rect(center=rect.center))
                    else:
                        # Fallback: red circle
                        cx = x * self.cell_size + self.cell_size // 2
                        cy = y * self.cell_size + self.stats_height + self.cell_size // 2
                        pygame.draw.circle(self.screen, (255, 0, 0), (cx, cy), self.cell_size // 3)
                else:
                    pygame.draw.rect(self.screen, self.REVEALED_COLOR, rect)
                    if cell != " ":
                        num = int(cell)
                        color = self.NUMBER_COLORS.get(num, (0, 0, 0))
                        text = self.font.render(cell, True, color)
                        self.screen.blit(text, text.get_rect(center=(
                            x * self.cell_size + self.cell_size // 2,
                            y * self.cell_size + self.stats_height + self.cell_size // 2,
                        )))

                # Cell border
                pygame.draw.rect(self.screen, self.GRID_COLOR, rect, 1)

        # Game over / win overlay
        if game_over or win:
            overlay = pygame.Surface((self.screen_width, self.height * self.cell_size), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 128))
            self.screen.blit(overlay, (0, self.stats_height))

            message = "Game Over! Click to restart." if game_over else "You Win! Click to restart."
            # Replaced SysFont('Arial', 32) — no system fonts in browser
            text = pygame.font.Font(None, 32).render(message, True, (0, 0, 0))
            self.screen.blit(text, text.get_rect(center=(
                self.screen_width // 2,
                self.stats_height + (self.height * self.cell_size) // 2,
            )))

    def draw_stats(self, mines_remaining, flags_used, game_time):
        stats_rect = pygame.Rect(0, 0, self.screen_width, self.stats_height)
        pygame.draw.rect(self.screen, (220, 220, 220), stats_rect)
        pygame.draw.line(self.screen, (180, 180, 180),
                         (0, self.stats_height), (self.screen_width, self.stats_height), 2)

        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"

        mines_text = self.stats_font.render(f"Mines: {mines_remaining}", True, (0, 0, 0))
        flags_text = self.stats_font.render(f"Flags: {flags_used}", True, (0, 0, 0))
        time_text = self.stats_font.render(f"Time: {time_str}", True, (0, 0, 0))

        padding = 20
        self.screen.blit(mines_text, mines_text.get_rect(midleft=(padding, self.stats_height // 2)))
        self.screen.blit(flags_text, flags_text.get_rect(center=(self.screen_width // 2, self.stats_height // 2)))
        self.screen.blit(time_text, time_text.get_rect(midright=(self.screen_width - padding, self.stats_height // 2)))

    def get_cell_at_pos(self, pos):
        x, y = pos
        board_x = x // self.cell_size
        board_y = (y - self.stats_height) // self.cell_size
        if 0 <= board_x < self.width and 0 <= board_y < self.height:
            return board_x, board_y
        return None


# --- MinesweeperGame (from game.py) ---

class MinesweeperGame:
    def __init__(self, width=10, height=10, num_mines=10):
        self.board = Board(width, height, num_mines)
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.game_over = False
        self.win = False
        self.flags_used = 0

    def new_game(self):
        self.board = Board(self.width, self.height, self.num_mines)
        self.game_over = False
        self.win = False
        self.flags_used = 0

    def reveal_cell(self, x, y):
        if self.game_over or self.win:
            return False
        result = self.board.reveal_cell(x, y)
        self.game_over = self.board.game_over
        self.win = self.board.win
        return result

    def toggle_flag(self, x, y):
        if self.game_over or self.win:
            return False
        result = self.board.toggle_flag(x, y)
        if result:
            cell = self.board.grid[y][x]
            if cell.is_flagged:
                self.flags_used += 1
            else:
                self.flags_used -= 1
        return result

    def chord(self, x, y):
        if self.game_over or self.win:
            return False
        result = self.board.chord(x, y)
        self.game_over = self.board.game_over
        self.win = self.board.win
        return result

    def get_board_state(self):
        return self.board.get_visible_board()

    def is_game_over(self):
        return self.game_over

    def is_win(self):
        return self.win

    def get_flags_remaining(self):
        return self.num_mines - self.flags_used


# --- Main loop (from main.py) ---

async def main():
    # Game parameters
    width = 10
    height = 10
    num_mines = 15
    cell_size = 40

    game = MinesweeperGame(width, height, num_mines)
    renderer = GameRenderer(width, height, cell_size)

    start_time = time.time()
    game_time = 0
    last_time_update = 0
    timer_paused = False
    need_board_update = True

    running = True
    while running:
        current_time = time.time()

        # Update timer once per second while game is active
        if not timer_paused and int(current_time - start_time) > last_time_update:
            game_time = current_time - start_time
            last_time_update = int(game_time)
            renderer.draw_stats(game.get_flags_remaining(), game.flags_used, game_time)
            pygame.display.update(pygame.Rect(0, 0, renderer.screen_width, renderer.stats_height))

        # Pause timer on game end
        if (game.is_game_over() or game.is_win()) and not timer_paused:
            timer_paused = True
            renderer.draw_stats(game.get_flags_remaining(), game.flags_used, game_time)
            pygame.display.update(pygame.Rect(0, 0, renderer.screen_width, renderer.stats_height))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                cell_pos = renderer.get_cell_at_pos(pos)

                if cell_pos:
                    x, y = cell_pos

                    # Left click — reveal cell, chord, or restart
                    if event.button == 1:
                        if game.is_game_over() or game.is_win():
                            game.new_game()
                            start_time = time.time()
                            game_time = 0
                            last_time_update = 0
                            timer_paused = False
                        else:
                            board_state = game.get_board_state()
                            try:
                                cell_value = board_state[y][x]
                                # Click on a revealed number → chord
                                if cell_value not in ["■", "F", "X", " "]:
                                    game.chord(x, y)
                                else:
                                    game.reveal_cell(x, y)
                            except (IndexError, ValueError):
                                game.reveal_cell(x, y)
                        need_board_update = True

                    # Right click — toggle flag
                    elif event.button == 3:
                        if not (game.is_game_over() or game.is_win()):
                            game.toggle_flag(x, y)
                            need_board_update = True
                            renderer.draw_stats(game.get_flags_remaining(), game.flags_used, game_time)
                            pygame.display.update(pygame.Rect(0, 0, renderer.screen_width, renderer.stats_height))

        # Redraw board only when state changes
        if need_board_update:
            if game.is_game_over():
                # Reveal all mines on game over
                for y in range(game.height):
                    for x in range(game.width):
                        cell = game.board.grid[y][x]
                        if cell.is_mine:
                            cell.is_revealed = True

            renderer.draw_board(game.get_board_state(), game.is_game_over(), game.is_win())
            pygame.display.update(pygame.Rect(
                0, renderer.stats_height,
                renderer.screen_width, renderer.height * renderer.cell_size,
            ))
            need_board_update = False

        # 30 FPS — sufficient for turn-based game
        await asyncio.sleep(1 / 30)


# Dual-mode: browser (Pyodide has running loop) vs local
try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())
    pygame.quit()
