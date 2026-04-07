import sys
import random
import pygame

from game.settings   import NATIVE_W, NATIVE_H, DISPLAY_W, DISPLAY_H, FPS, ORANGE, RED, YELLOW, MELEE_RANGE, BLACK
import game.draw  as draw
import game.audio as audio
from game.background import draw_bg
from game.hud        import init_fonts, draw_hud, draw_game_over, draw_wave_banner, draw_cycle_banner
from game.player     import Player
from game.enemy      import Enemy
from game.particle   import Particle
from game.slash      import Slash
from game.pickup     import Pickup


def spawn_side() -> float:
    return float(random.choice([20, NATIVE_W - 50]))


def run_game() -> None:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    screen = pygame.display.set_mode((DISPLAY_W, DISPLAY_H))
    pygame.display.set_caption("Iron Slug")
    clock = pygame.time.Clock()

    # letterbox: compute scale to fit NATIVE canvas inside DISPLAY keeping aspect ratio
    scale    = min(DISPLAY_W / NATIVE_W, DISPLAY_H / NATIVE_H)
    scaled_w = int(NATIVE_W * scale)
    scaled_h = int(NATIVE_H * scale)
    blit_x   = (DISPLAY_W - scaled_w) // 2
    blit_y   = (DISPLAY_H - scaled_h) // 2

    # game_surf is at display resolution — no further scaling needed (always crisp)
    game_surf = pygame.Surface((scaled_w, scaled_h))

    draw.setup(scale)    # all draw.* calls use this scale
    init_fonts(scale)    # fonts sized proportionally
    audio.init()
    audio.play_music()

    player    = Player()
    enemies:   list[Enemy]    = []
    bullets:   list           = []
    particles: list[Particle] = []
    slashes:   list[Slash]    = []
    pickups:   list[Pickup]   = []

    score         = 0
    lives         = 3
    wave          = 1
    to_spawn      = 5
    spawn_timer   = 0
    wave_banner   = 0
    cycle_banner  = 0
    game_over     = False

    # weapon pickup spawn
    pickup_timer = random.randint(900, 1500)
    MAX_PICKUPS  = 2
    WEAPON_POOL  = ['ak47', 'flamethrower']

    # ── difficulty helpers ────────────────────────────────────────────────────
    def current_cycle(w: int) -> int:
        return (w - 1) // 3 + 1

    def wave_in_cycle(w: int) -> int:
        return (w - 1) % 3 + 1

    def wave_spawn_interval(w: int) -> int:
        wic = wave_in_cycle(w)
        return max(30, 90 - (wic - 1) * 8)       # resets every cycle

    def wave_enemy_count(w: int) -> int:
        wic = wave_in_cycle(w)
        return min(5 + (wic - 1) * 2, 12)        # resets every cycle

    def enemy_speed(w: int) -> float:
        c = current_cycle(w)
        return round(1.8 + (c - 1) * 0.5, 2)     # +0.5 per cycle

    def enemy_bullet_dmg(w: int) -> int:
        c = current_cycle(w)
        return 10 + (c - 1) * 6                  # +6 per cycle

    def enemy_melee_dmg(w: int) -> int:
        c = current_cycle(w)
        return 25 + (c - 1) * 10                 # +10 per cycle

    def _player_hit(dmg: int) -> None:
        nonlocal lives, game_over
        if player.take_damage(dmg):
            if player.health <= 0:
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    player.reset()
                    player.invincible = 120

    running = True
    while running:
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if game_over:
                    if ev.key == pygame.K_r:
                        run_game(); return
                    if ev.key == pygame.K_q:
                        pygame.quit(); sys.exit()

        pressed      = pygame.key.get_pressed()
        live_enemies = [e for e in enemies if not e.dead]

        # ── UPDATE ────────────────────────────────────────────────────────────
        if not game_over:
            player.update(pressed)

            # ── player attack ─────────────────────────────────────────────────
            if pressed[pygame.K_LSHIFT] or pressed[pygame.K_RSHIFT]:
                player_cx = player.x + player.W / 2
                nearest   = min(
                    (e for e in enemies if not e.dead),
                    key=lambda e: abs((e.x + e.W / 2) - player_cx),
                    default=None,
                )
                in_melee = (nearest is not None and
                            abs((nearest.x + nearest.W / 2) - player_cx) <= MELEE_RANGE)

                if in_melee:
                    if player.try_melee():
                        audio.play_slash()
                        nearest.hit(40)
                        slashes.append(Slash(player_cx + player.facing * 25,
                                            player.y + 25, player.facing))
                        for _ in range(8):
                            particles.append(Particle(nearest.x + nearest.W / 2,
                                                      nearest.y + nearest.H / 2, RED))
                        if nearest.dead:
                            score += 100 * wave
                else:
                    _weapon_fired = player.weapon
                    new_bullets = player.try_shoot()
                    if new_bullets:
                        audio.play_shoot(_weapon_fired)
                        bullets.extend(new_bullets)
                        mx = (player.x + player.W) if player.facing == 1 else player.x
                        b_color = new_bullets[0].color
                        for _ in range(4):
                            particles.append(Particle(mx, player.y + 20, b_color))

            # ── pickup collision ───────────────────────────────────────────────
            for pk in pickups[:]:
                pk.update()
                if pk.rect().colliderect(player.rect()):
                    player.equip(pk.weapon)
                    pickups.remove(pk)

            # ── enemies ───────────────────────────────────────────────────────
            for e in enemies[:]:
                e.update(player.x + player.W / 2, enemies)

                if e.try_melee():
                    slashes.append(Slash(e.x + e.W / 2, e.y + e.H / 3, -e.facing))
                    for _ in range(6):
                        particles.append(Particle(player.x + player.W / 2,
                                                  player.y + player.H / 2, RED))
                    _player_hit(e.melee_damage)
                else:
                    b = e.try_ranged()
                    if b:
                        bullets.append(b)

                if e.dead and e.death_timer > 28:
                    enemies.remove(e)

            # ── bullets & collisions ───────────────────────────────────────────
            for b in bullets[:]:
                b.update()
                if not b.alive:
                    bullets.remove(b); continue

                if b.owner == 'player':
                    for e in enemies:
                        if not e.dead and b.rect().colliderect(e.rect()):
                            e.hit(b.damage)
                            b.alive = False
                            for _ in range(6):
                                particles.append(Particle(b.x, b.y, ORANGE))
                            if e.dead:
                                score += 100 * wave
                            break
                else:
                    if b.rect().colliderect(player.rect()):
                        for _ in range(5):
                            particles.append(Particle(b.x, b.y, RED))
                        b.alive = False
                        _player_hit(b.damage)

            # ── slashes ───────────────────────────────────────────────────────
            for s in slashes[:]:
                s.update()
                if not s.alive:
                    slashes.remove(s)

            # ── particles ─────────────────────────────────────────────────────
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)

            # ── weapon pickup spawn ────────────────────────────────────────────
            pickup_timer -= 1
            if pickup_timer <= 0:
                pickup_timer = random.randint(900, 1500)
                if len(pickups) < MAX_PICKUPS:
                    wx     = random.randint(80, NATIVE_W - 80)
                    weapon = random.choice(WEAPON_POOL)
                    pickups.append(Pickup(wx, weapon))

            # ── wave management ───────────────────────────────────────────────
            if not live_enemies and to_spawn == 0:
                prev_cycle   = current_cycle(wave)
                wave        += 1
                to_spawn     = wave_enemy_count(wave)
                spawn_timer  = 0
                wave_banner  = 50
                if current_cycle(wave) > prev_cycle:
                    cycle_banner = 90   # longer display for cycle-up

            if to_spawn > 0:
                spawn_timer -= 1
                if spawn_timer <= 0:
                    enemies.append(Enemy(
                        spawn_side(),
                        speed        = enemy_speed(wave),
                        bullet_damage= enemy_bullet_dmg(wave),
                        melee_damage = enemy_melee_dmg(wave),
                    ))
                    to_spawn    -= 1
                    spawn_timer  = wave_spawn_interval(wave)

            if cycle_banner > 0:
                cycle_banner -= 1

            if wave_banner > 0:
                wave_banner -= 1

        # ── DRAW ──────────────────────────────────────────────────────────────
        draw_bg(game_surf)

        for pk in pickups:  pk.draw(game_surf)
        for p in particles: p.draw(game_surf)
        for b in bullets:   b.draw(game_surf)
        for s in slashes:   s.draw(game_surf)
        for e in enemies:   e.draw(game_surf)
        if not game_over:
            player.draw(game_surf)

        draw_hud(game_surf, player, score, lives, wave, len(live_enemies) + to_spawn)
        draw_wave_banner(game_surf, wave, wave_banner)
        draw_cycle_banner(game_surf, current_cycle(wave), cycle_banner)

        if game_over:
            draw_game_over(game_surf, score)

        # blit game surface onto display with letterbox bars
        screen.fill(BLACK)
        screen.blit(game_surf, (blit_x, blit_y))
        pygame.display.flip()


if __name__ == '__main__':
    run_game()
