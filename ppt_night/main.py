# guess_the_sound_fullscreen.py  – with Title screen “Guess the Meow?”

import pygame
import sys
import random
from pathlib import Path

# ---------- CONFIG -----------------------------------------------------
SOUND_DIR  = Path(__file__).with_name("sounds")   # ./sounds/ next to script
FONT_SIZE  = 52
TITLE_FONT = 72
BG_COLOR   = (30, 30, 30)
TEXT_COLOR = (240, 240, 240)
BTN_COLOR  = (70, 70, 70)
BTN_HOVER  = (110, 110, 110)
BTN_SIZE   = (200, 60)    # width, height (Back / Replay)
BTN_SPACING = 40
BTN_BOTTOM_MARGIN = 40
# ----------------------------------------------------------------------

def load_sounds(folder: Path):
    clips = [f for f in folder.iterdir() if f.suffix.lower() == ".ogg"]
    if not clips:
        raise FileNotFoundError(f"No .ogg files found inside {folder}")
    random.shuffle(clips)
    return clips

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Guess the Meow?")
    win_w, win_h = screen.get_size()

    font        = pygame.font.SysFont(None, FONT_SIZE)
    title_font  = pygame.font.SysFont(None, TITLE_FONT)
    sounds      = load_sounds(SOUND_DIR)
    total       = len(sounds)

    # ---------- STATE --------------------------------------------------
    phase = "title"   # "title" → "guess" → "reveal"
    idx   = -1
    current_channel = None

    # ---------- Buttons ------------------------------------------------
    btn_w, btn_h = BTN_SIZE
    total_width  = 2 * btn_w + BTN_SPACING
    start_x      = (win_w - total_width) // 2

    back_rect   = pygame.Rect(start_x,                     win_h - btn_h - BTN_BOTTOM_MARGIN, btn_w, btn_h)
    replay_rect = pygame.Rect(start_x + btn_w + BTN_SPACING, win_h - btn_h - BTN_BOTTOM_MARGIN, btn_w, btn_h)

    # ---------- Helper functions --------------------------------------
    def play_clip(index: int):
        if 0 <= index < total:
            snd = pygame.mixer.Sound(sounds[index])
            return snd.play()
        return None

    def replay_current():
        nonlocal current_channel
        if 0 <= idx < total:
            pygame.mixer.stop()
            current_channel = play_clip(idx)

    def play_next():
        nonlocal idx, current_channel
        if idx + 1 >= total:
            return False
        idx += 1
        pygame.mixer.stop()
        current_channel = play_clip(idx)
        return True

    def play_previous():
        nonlocal idx, current_channel
        if idx <= 0:
            return False
        idx -= 1
        pygame.mixer.stop()
        current_channel = play_clip(idx)
        return True

    # ---------- Main loop ---------------------------------------------
    clock, running = pygame.time.Clock(), True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        # ---- EVENTS ---------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if phase == "title":
                    phase = "guess"           # start the game
                    continue

                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if phase == "guess" and idx >= total - 1:
                        phase = "reveal"
                        idx   = -1
                        pygame.mixer.stop()
                    play_next()
                elif event.key == pygame.K_r:
                    replay_current()
                elif event.key in (pygame.K_b, pygame.K_LEFT):
                    play_previous()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if phase == "title":
                    phase = "guess"           # click also starts the game
                else:
                    if back_rect.collidepoint(event.pos):
                        play_previous()
                    elif replay_rect.collidepoint(event.pos):
                        replay_current()

        # ---- DRAW ----------------------------------------------------
        screen.fill(BG_COLOR)

        if phase == "title":
            title_surf = title_font.render("Sweet Princes (plus a few extras) Guess the Meow", True, TEXT_COLOR)
            prompt_surf = font.render("Press any key to begin", True, TEXT_COLOR)
            screen.blit(title_surf, title_surf.get_rect(center=(win_w//2, win_h//2 - 40)))
            screen.blit(prompt_surf, prompt_surf.get_rect(center=(win_w//2, win_h//2 + 40)))

        else:
            # status line
            if phase == "guess":
                if idx < 0:
                    msg = f"Guess Round – SPACE to play clip 1 of {total}"
                elif idx < total:
                    msg = f"Guess Round – clip {idx+1}/{total}."
                else:
                    msg = "Switching to reveal…"
            else:  # reveal
                if idx < 0:
                    msg = "Reveal Round – SPACE to replay clip 1 with answer"
                elif idx < total:
                    answer = sounds[idx].stem
                    msg = f"Answer: {answer}  ({idx+1}/{total})"
                else:
                    msg = "All answers revealed! Press ESC to quit."

            text_surf = font.render(msg, True, TEXT_COLOR)
            screen.blit(text_surf, text_surf.get_rect(center=(win_w//2, win_h//2)))

            # Back button
            back_color = BTN_HOVER if back_rect.collidepoint(mouse_pos) else BTN_COLOR
            pygame.draw.rect(screen, back_color, back_rect, border_radius=12)
            back_label = font.render("Back (B)", True, TEXT_COLOR)
            screen.blit(back_label, back_label.get_rect(center=back_rect.center))

            # Replay button
            rep_color = BTN_HOVER if replay_rect.collidepoint(mouse_pos) else BTN_COLOR
            pygame.draw.rect(screen, rep_color, replay_rect, border_radius=12)
            rep_label = font.render("Replay (R)", True, TEXT_COLOR)
            screen.blit(rep_label, rep_label.get_rect(center=replay_rect.center))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
