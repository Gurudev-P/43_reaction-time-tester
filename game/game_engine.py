import pygame
from .round import Round

WHITE = (255, 255, 255)
GRAY = (90, 90, 90)
GREEN = (40, 180, 90)
BLUE = (50, 90, 170)
RED = (190, 60, 60)
DARK = (35, 35, 35)

class GameEngine:
    DIFFICULTIES = {
        "Easy": (5, 1500, 3500),
        "Medium": (7, 1000, 3000),
        "Hard": (10, 700, 2000),
    }

    def __init__(self, width, height, rounds_total=7, min_wait_ms=1000, max_wait_ms=3000):
        self.width = width
        self.height = height
        self.rounds_total = rounds_total
        self.min_wait_ms = min_wait_ms
        self.max_wait_ms = max_wait_ms
        self.difficulty = "Medium"

        self.round = Round(self.min_wait_ms, self.max_wait_ms)
        self.reaction_times = []
        self.false_starts = 0
        self.rounds_completed = 0

        self.result_shown_at = None
        self.result_pause_ms = 800
        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 46)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.game_over = False
        self.mode = "playing"

    def handle_event(self, event):
        if self.game_over:
            return

        is_click = event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", 1) == 1
        is_space = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE

        if self.mode == "results":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self._start_session("Easy")
                elif event.key == pygame.K_2:
                    self._start_session("Medium")
                elif event.key == pygame.K_3:
                    self._start_session("Hard")
            return

        if (is_click or is_space) and self.round.state in ("waiting", "go"):
            reaction_ms = self.round.register_input()
            self.result_shown_at = pygame.time.get_ticks()

            if self.round.state == "false_start":
                self.false_starts += 1
                self.rounds_completed += 1
            elif self.round.state == "result" and reaction_ms is not None:
                self.reaction_times.append(reaction_ms)
                self.rounds_completed += 1

    def update(self):
        if self.game_over:
            return

        self.round.update()

        if self.round.state in ("result", "false_start"):
            now = pygame.time.get_ticks()
            if self.result_shown_at is not None and now - self.result_shown_at >= self.result_pause_ms:
                self._start_next_round()

    def _start_session(self, difficulty):
        self.difficulty = difficulty
        self.rounds_total, self.min_wait_ms, self.max_wait_ms = self.DIFFICULTIES[difficulty]
        self.reaction_times = []
        self.false_starts = 0
        self.rounds_completed = 0
        self.game_over = False
        self.mode = "playing"
        self.result_shown_at = None
        self.round = Round(self.min_wait_ms, self.max_wait_ms)

    def _start_next_round(self):
        if self.rounds_completed >= self.rounds_total:
            self.game_over = True
            self.mode = "results"
            return
        self.round = Round(self.min_wait_ms, self.max_wait_ms)

    def average_reaction_ms(self):
        if not self.reaction_times:
            return 0
        return round(sum(self.reaction_times) / len(self.reaction_times))

    def render(self, screen):
        if self.mode == "results":
            self._render_results(screen)
            return

        if self.round.state == "waiting":
            bg, message = GRAY, "Wait for green..."
        elif self.round.state == "go":
            bg, message = GREEN, "Click now!"
        elif self.round.state == "false_start":
            bg, message = RED, "FALSE START!"
        else:
            bg, message = BLUE, f"{self.round.reaction_ms} ms"

        screen.fill(bg)

        text_surf = self.big_font.render(message, True, WHITE)
        text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
        screen.blit(text_surf, text_rect)

        round_text = self.font.render(
            f"{self.difficulty} - Round {min(self.rounds_completed + 1, self.rounds_total)}/{self.rounds_total}",
            True, WHITE
        )
        screen.blit(round_text, (10, 10))

        avg_text = self.font.render(
            f"Avg: {self.average_reaction_ms()} ms", True, WHITE
        )
        screen.blit(avg_text, (self.width - 240, 10))

        false_text = self.font.render(
            f"False starts: {self.false_starts}", True, WHITE
        )
        screen.blit(false_text, (10, 48))

    def _render_results(self, screen):
        screen.fill(DARK)

        title = self.big_font.render("SESSION COMPLETE", True, WHITE)
        screen.blit(title, title.get_rect(center=(self.width // 2, 45)))

        lines = [
            f"Difficulty: {self.difficulty}",
            f"Average valid reaction: {self.average_reaction_ms()} ms",
            f"False starts: {self.false_starts}",
            "",
            "Reaction times:",
        ]

        y = 100
        for line in lines:
            surf = self.font.render(line, True, WHITE)
            screen.blit(surf, (40, y))
            y += 36

        if self.reaction_times:
            for index, value in enumerate(self.reaction_times, start=1):
                surf = self.font.render(f"Round {index}: {value} ms", True, WHITE)
                x = 55 + ((index - 1) % 2) * 270
                row = (index - 1) // 2
                screen.blit(surf, (x, y + row * 34))
            y += ((len(self.reaction_times) + 1) // 2) * 34 + 20
        else:
            surf = self.small_font.render("No valid reaction times recorded.", True, WHITE)
            screen.blit(surf, (40, y))
            y += 30

        menu = [
            "1 = Easy (5 rounds, 1.5-3.5s wait)",
            "2 = Medium (7 rounds, 1.0-3.0s wait)",
            "3 = Hard (10 rounds, 0.7-2.0s wait)",
            "Close the window to exit.",
        ]

        y = max(y + 10, 300)
        for line in menu:
            surf = self.small_font.render(line, True, WHITE)
            screen.blit(surf, (40, y))
            y += 28
