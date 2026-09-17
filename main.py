# =========================================================================
# CACTUS TOWER DEFENSE: REMASTERED - ТОЧКА ВХОДА (MAIN CONTROLLER)
# =========================================================================
import os
import sys

# Включаем аппаратную осведомленность о DPI Windows (Per-Monitor DPI Aware v2).
# Это предотвращает размытие DWM на 2K/4K мониторах и при масштабировании 125%/150%.
if sys.platform == "win32":
    try:
        import ctypes
        u32 = ctypes.windll.user32
        u32.SetProcessDpiAwarenessContext.argtypes = [ctypes.c_void_p]
        u32.SetProcessDpiAwarenessContext.restype = ctypes.c_bool
        if not u32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4)):
            raise ValueError("SetProcessDpiAwarenessContext failed")
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

import math
import random
import pygame

# Подключение модулей
from config import *
from game_data import *
from entities import *
from ui_screens import *

class WindowManager:
    """Управление физическим окном ОС (Windows), заголовком, эффектами тряски и системным оповещением."""
    def __init__(self):
        self.win = None
        self.base_pos = None
        self.is_shaking = False
        self.last_title = ""
        try:
            self.win = pygame.Window.from_display_module()
            self.base_pos = self.win.position
        except Exception:
            self.win = None

    def update_shake(self, shake_amount, raw_dt, enabled=True):
        pass  # Тряска физического окна ОС полностью отключена

    def reset_position(self):
        pass

    def set_title(self, title):
        if self.win and title != self.last_title:
            try:
                self.win.title = title
                self.last_title = title
            except Exception:
                pass

    def flash(self):
        if self.win:
            try:
                self.win.flash(pygame.FLASH_BRIEFLY)
            except Exception:
                pass

    def victory_bounce(self):
        pass  # Физическое подпрыгивание окна ОС отключено

def run_game():
    global savedata, screen

    running = True

    STATE_MAIN_MENU = "MAIN_MENU"
    STATE_MAP_SELECT = "MAP_SELECT"
    STATE_UPGRADES = "UPGRADES"
    STATE_ACHIEVEMENTS = "ACHIEVEMENTS"
    STATE_BESTIARY = "BESTIARY"
    STATE_GREENHOUSE = "GREENHOUSE"
    STATE_RELICS = "RELICS"
    STATE_PLAYING = "PLAYING"
    STATE_CREDITS = "CREDITS"
    STATE_SETTINGS = "SETTINGS"

    current_state = STATE_MAIN_MENU
    demo_sim = MenuDemoSimulation()
    settings_source = "main_menu"

    apply_audio_settings(savedata)
    set_graphics_preset(savedata.get("Settings", {}).get("graphics_preset", "normal"))
    screen = set_scale_quality(savedata.get("Settings", {}).get("scale_quality", "sharp"))
    if not is_dark_cacti_unlocked(savedata) and savedata.get("DarkCactuses", 0) > 0:
        savedata["DarkCactuses"] = 0
        save_data(savedata)
    win_mgr = WindowManager()

    game_map = 0
    map_scroll_offset = 0

    path = []
    tower_slots = []
    occupied_slots = []
    towers = []
    enemies = []
    projectiles = []
    effects = []
    item_drops = []
    stellar_drops = item_drops

    active_dig_site = None
    dig_window = None
    dig_session = None
    dig_window_close_timer = 0.0
    dig_mouse_pos = (0, 0)

    active_map_info_modal = None
    active_custom_map_modal = False
    modal_inspect_wave = 1
    bestiary_scroll_y = 0
    is_dragging_bestiary = False
    bestiary_drag_start_y = 0
    bestiary_drag_start_scroll = 0
    bestiary_drag_moved = False
    bestiary_return_state = STATE_MAP_SELECT
    inspected_greenhouse_cactus = None
    credits_scroll_y = 0.0
    credits_source = "game"
    confirming_reset = False
    settings_tab = "general"
    saves_scroll_y = 0
    save_modal_state = None
    active_meteorite = None
    next_meteor_wave = 20
    cactus_drone = None
    orbital_strike_cd = 0.0
    orbital_targeting = False
    rally_targeting_tent = None
    dark_aegis_charges = 0
    flawless_streak = savedata.get("FlawlessWaveStreak", 0)
    lives_at_wave_start = 12

    cacti = 200
    lives = 12
    max_lives = 12
    animated_hp_ratio = 1.0
    hp_catchup_ratio = 1.0
    session_towers_bought = 0
    tree_cam_x = 0
    tree_cam_y = 40
    tree_zoom = 1.0
    selected_tree_node = "oasis_core"
    is_dragging_tree = False
    tree_drag_start = (0, 0)
    tree_drag_cam_start = (0, 0)
    tree_drag_moved = False
    tree_tap_node = None
    wave = 1
    session_start_wave = 1
    ach_scroll_y = 0
    is_dragging_ach = False
    ach_drag_start_y = 0
    ach_drag_start_scroll = 0
    ach_drag_moved = False
    ach_filter_status = "all"
    ach_filter_cat = "all"
    game_over = False
    wave_in_progress = False

    spawn_timer = 0.0
    spawn_delay = 1.2
    enemies_to_spawn = 0
    enemies_spawned = 0
    between_waves_timer = 0.8
    current_wave_queue = []
    upcoming_wave_preview = []
    shake_amount = 0.0

    selected_tower_type = None
    hovered_tower = None
    inspected_tower = None
    last_card_rect = None
    last_btn_rect = None
    last_target_rect = None
    last_sell_rect = None
    last_max_rect = None
    upgrade_mode = False
    is_paused = False
    pause_frozen_frame = None
    pause_click_rects = {}
    r_btn = None
    q_btn = None

    session_kills = 0
    session_cacti = 0
    session_stellar = 0

    speed_levels = [0.2, 1, 2]
    current_speed_index = 1
    game_speed = 1

    bg_time = 0.0
    bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    field_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    hud_fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    battle_ui_fade_alpha = 255.0
    _dock_icon_cache = {}
    _wave_preview_icon_cache = {}
    ambient_particles = AmbientParticleSystem(0)
    map_decor = MapDecorManager(0, path_list[0], tower_slots_list[0])
    slime_splats = []
    _pause_title_surf = massive_font.render('ПАУЗА', True, WHITE)
    _pause_btn_res_txt = font.render('ПРОДОЛЖИТЬ  [P / ESC]', True, WHITE)
    _pause_btn_rst_txt = font.render('ЗАНОВО  [R]', True, WHITE)
    _pause_btn_bst_txt = font.render('БЕСТИАРИЙ  [B]', True, WHITE)
    _pause_btn_mnu_txt = font.render('ВЫБОР КАРТЫ  [ВЫХОД]', True, WHITE)

    def get_wave_cacti_multiplier(wave_num):
        """С 40 по 60 волну выручка обычных кактусов плавно падает в 2 раза (с 1.0 до 0.5)."""
        if wave_num <= 40:
            return 1.0
        elif wave_num >= 60:
            return 0.5
        else:
            return 1.0 - 0.5 * ((wave_num - 40) / 20.0)

    def start_battle_session():
        nonlocal path, tower_slots, occupied_slots, towers, enemies, projectiles, effects, item_drops, stellar_drops
        nonlocal wave, cacti, lives, max_lives, animated_hp_ratio, hp_catchup_ratio, session_towers_bought, game_over, wave_in_progress, between_waves_timer
        nonlocal upgrade_mode, selected_tower_type, inspected_tower, speed_levels, current_speed_index, game_speed
        nonlocal session_kills, session_cacti, session_stellar, is_paused, current_state, pause_frozen_frame
        nonlocal last_card_rect, last_btn_rect, last_target_rect, last_sell_rect, last_max_rect
        nonlocal r_btn, q_btn, pause_click_rects
        nonlocal current_wave_queue, upcoming_wave_preview, shake_amount, ambient_particles, map_decor, slime_splats
        nonlocal active_meteorite, next_meteor_wave, cactus_drone, orbital_strike_cd, orbital_targeting, rally_targeting_tent, dark_aegis_charges, flawless_streak, lives_at_wave_start, session_start_wave
        nonlocal active_dig_site, dig_window, dig_session, dig_window_close_timer, battle_ui_fade_alpha

        pause_frozen_frame = None
        battle_ui_fade_alpha = 0.0
        if active_dig_site:
            active_dig_site = None
        if dig_window:
            try:
                dig_window.destroy()
            except Exception:
                pass
            dig_window = None
            dig_session = None
            dig_window_close_timer = 0.0

        if game_map == 9:
            cfg = savedata.get("CustomMapConfig", {})
            seed_val = int(cfg.get("seed", 777))
            p, s = generate_custom_map_path_and_slots(seed_val)
            path_list[9] = p
            tower_slots_list[9] = s
            MAP_BIOMES_DATA[9]["hp_mult"] = float(cfg.get("hp_mult", 1.5))
            MAP_BIOMES_DATA[9]["spd_mult"] = float(cfg.get("spd_mult", 1.0))
            MAP_BIOMES_DATA[9]["cacti_mult"] = float(cfg.get("cacti_mult", 1.0))
            MAP_BIOMES_DATA[9]["stellar_mult"] = float(cfg.get("stellar_mult", 1.0))
            MAP_BIOMES_DATA[9]["endless"] = bool(cfg.get("endless", True))
            b_idx = int(cfg.get("biome_style", 0)) % 9
            MAP_BIOMES_DATA[9]["bg_col_a"] = MAP_BIOMES_DATA[b_idx]["bg_col_a"]
            MAP_BIOMES_DATA[9]["bg_col_b"] = MAP_BIOMES_DATA[b_idx]["bg_col_b"]
            MAP_BIOMES_DATA[9]["road_col"] = MAP_BIOMES_DATA[b_idx]["road_col"]
            MAP_BIOMES_DATA[9]["road_border"] = MAP_BIOMES_DATA[b_idx]["road_border"]
            MAP_BIOMES_DATA[9]["particle_type"] = MAP_BIOMES_DATA[b_idx]["particle_type"]
            MAP_BIOMES_DATA[9]["soundtrack"] = MAP_SOUNDTRACKS[b_idx][1]

        path = path_list[game_map]
        tower_slots = tower_slots_list[game_map]
        occupied_slots = [False] * len(tower_slots)
        towers = []
        enemies = []
        projectiles = []
        effects = []
        item_drops = []
        stellar_drops = item_drops
        ambient_particles = AmbientParticleSystem(game_map)
        map_decor = MapDecorManager(game_map, path, tower_slots)
        slime_splats = []
        active_meteorite = None

        drone_lvl = savedata["Upgrades"].get("cactus_drone", 0)
        cactus_drone = CactusDrone(drone_lvl) if drone_lvl > 0 else None
        orbital_strike_cd = 0.0
        orbital_targeting = False
        rally_targeting_tent = None
        dark_aegis_charges = savedata["Upgrades"].get("dark_aegis", 0)

        start_wave = savedata.get("SelectedStartWave", 1)
        wave = start_wave
        session_start_wave = start_wave
        gw_lvl = savedata["Upgrades"].get("gravity_well", 0)
        gw_min = max(6, 10 - gw_lvl * 2)
        gw_max = max(9, 15 - gw_lvl * 2)
        next_meteor_wave = max(20 + random.randint(0, 3), start_wave + random.randint(gw_min, gw_max))
        gh_buffs = get_greenhouse_buffs(savedata)
        relic_buffs = get_all_relic_buffs(savedata)
        max_lives = 12 + savedata["Upgrades"].get("base_health", 0) * 3 + gh_buffs.get("base_hp", 0) + relic_buffs.get("base_hp_bonus", 0)
        lives = max_lives
        animated_hp_ratio = 1.0
        hp_catchup_ratio = 1.0
        session_towers_bought = 0
        lives_at_wave_start = lives
        flawless_streak = 0
        cacti = 200 + (start_wave - 1) * 120 + savedata["Upgrades"].get("start_cacti", 0) * 80 + gh_buffs.get("start_gold", 0)
        if game_map == 9:
            cacti = int(savedata.get("CustomMapConfig", {}).get("start_gold", 400))
        elif game_map == 0:
            cacti = int(cacti * 1.10)
        if relic_buffs.get("start_cacti_mult", 0.0) > 0:
            cacti = int(cacti * (1.0 + relic_buffs["start_cacti_mult"]))

        game_over = False
        is_paused = False
        wave_in_progress = False
        wave_rush_lvl = savedata.get("Upgrades", {}).get("wave_rush", 0)
        wave_rush_active = savedata.get("Toggles", {}).get("wave_rush", True)
        if wave_rush_lvl > 0 and wave_rush_active:
            between_waves_timer = [0.8, 0.4, 0.15, 0.0][min(3, wave_rush_lvl)]
        else:
            between_waves_timer = 0.8
        current_wave_queue = []
        upcoming_wave_preview = get_wave_enemies(wave, game_map=game_map, savedata=savedata)
        shake_amount = 0.0
        win_mgr.reset_position()
        upgrade_mode = False
        selected_tower_type = None
        inspected_tower = None
        last_card_rect = None
        last_btn_rect = None
        last_target_rect = None
        last_sell_rect = None
        last_max_rect = None
        r_btn = None
        q_btn = None
        pause_click_rects = {}

        session_kills = 0
        session_cacti = 0
        session_stellar = 0

        speed_upg = savedata["Upgrades"].get("speed_limit", 0)
        speed_levels = [0.2, 1, 2]
        for spd in range(3, 3 + min(8, speed_upg)):
            speed_levels.append(spd)
        current_speed_index = 1
        game_speed = speed_levels[current_speed_index]

        play_soundtrack(MAP_SOUNDTRACKS[game_map][1])
        current_state = STATE_PLAYING

    play_soundtrack(MAP_SOUNDTRACKS[0][1])
    playtime_check_timer = 0.0

    while running:
        raw_dt = clock.tick(FPS) / 1000.0
        raw_dt = min(raw_dt, 0.1)
        bg_time += raw_dt * 1000.0

        # Учёт проведённого времени в текущем сохранении и периодическая проверка достижений
        stats_data = savedata.setdefault("Stats", {})
        stats_data["play_time_seconds"] = stats_data.get("play_time_seconds", 0.0) + raw_dt
        playtime_check_timer += raw_dt
        if playtime_check_timer >= 5.0:
            playtime_check_timer = 0.0
            if check_achievements(savedata):
                save_data(savedata)
                if current_state == STATE_PLAYING:
                    effects.append(FloatingText(SCREEN_WIDTH // 2, 150, "ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!", GOLD))
                    sfx_achievement.play()

        mouse_pos = pygame.mouse.get_pos()

        # Затухание тряски (окна и экрана) глобально для всех состояний игры
        if shake_amount > 0:
            shake_amount = max(0.0, shake_amount - raw_dt * 28.0)

        # Обновление физической тряски окна ОС (Windows)
        win_shake_on = savedata.get("Settings", {}).get("window_shake", True) and not IS_ANDROID
        win_mgr.update_shake(shake_amount, raw_dt, enabled=win_shake_on)

        # Динамический заголовок окна игры
        if current_state == STATE_PLAYING:
            active_boss = next((e for e in enemies if getattr(e, 'is_boss', False) or e.type >= 1000), None)
            if active_boss:
                b_name = "КОРОЛЬ СЛАЙМОВ" if active_boss.type >= 4000 else ("ТЕНЕВОЙ ИСПОЛИН" if active_boss.type >= 3000 else ("СЛИЗНЕБАРОН" if active_boss.type >= 2000 else "ЦАРЬ-СЛИЗЕНЬ"))
                win_mgr.set_title(f"CactusTD Remastered | [БОСС] {b_name}: {int(active_boss.health):,} HP | Волна {wave}")
            elif active_meteorite:
                win_mgr.set_title(f"CactusTD Remastered | [МЕТЕОРИТ] {int(active_meteorite.hp)} HP | Волна {wave}")
            else:
                win_mgr.set_title(f"CactusTD Remastered | Волна {wave} | База: {lives}/{max_lives} HP")
        elif current_state == STATE_MAIN_MENU:
            win_mgr.set_title("CactusTD Remastered | Главное Меню")
        elif current_state == STATE_MAP_SELECT:
            win_mgr.set_title("CactusTD Remastered | Выбор Карты")
        elif current_state == STATE_UPGRADES:
            win_mgr.set_title(f"CactusTD Remastered | Древо Талантов (Звёзды: {savedata.get('StellarCactuses', 0)} | Тёмные: {savedata.get('DarkCactuses', 0)})")
        elif current_state == STATE_GREENHOUSE:
            win_mgr.set_title("CactusTD Remastered | Оранжерея Кактусов")
        elif current_state == STATE_BESTIARY:
            win_mgr.set_title(f"CactusTD Remastered | Бестиарий ({len(savedata.get('BestiaryDiscovered', []))}/10)")
        elif current_state == STATE_ACHIEVEMENTS:
            win_mgr.set_title("CactusTD Remastered | Достижения")
        elif current_state == STATE_SETTINGS:
            win_mgr.set_title("CactusTD Remastered | Настройки")
        elif current_state == STATE_CREDITS:
            win_mgr.set_title("CactusTD Remastered | Титры")

        # =================================================================
        # ЭКРАН 0: ГЛАВНОЕ МЕНЮ
        # =================================================================
        if current_state == STATE_MAIN_MENU:
            demo_sim.update(raw_dt)
            play_btn, set_btn, exit_btn = draw_main_menu_screen(screen, mouse_pos, demo_sim, bg_time=bg_time)

            for event in pygame.event.get():
                if hasattr(event, "pos"):
                    mouse_pos = event.pos
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        current_state = STATE_MAP_SELECT
                        sfx_click.play()
                    elif event.key == pygame.K_o:
                        current_state = STATE_SETTINGS
                        settings_source = "main_menu"
                        sfx_click.play()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if play_btn and play_btn.collidepoint(mouse_pos):
                        current_state = STATE_MAP_SELECT
                        sfx_click.play()
                    elif set_btn and set_btn.collidepoint(mouse_pos):
                        current_state = STATE_SETTINGS
                        settings_source = "main_menu"
                        sfx_click.play()
                    elif exit_btn and exit_btn.collidepoint(mouse_pos):
                        running = False
                        sfx_click.play()
                    else:
                        # Базовая способность: клик по слайму наносит 1 чистый урон и вызывает эффекты
                        clicked_e = None
                        for en in demo_sim.enemies:
                            hit_r = 32 if getattr(en, "is_boss", False) else 22
                            if math.hypot(mouse_pos[0] - en.x, mouse_pos[1] - en.y) <= hit_r:
                                clicked_e = en
                                break
                        if clicked_e:
                            clicked_e.take_damage(1.0, damage_type="pure")
                            demo_sim.effects.append(FloatingText(clicked_e.x, clicked_e.y - 14, "-1", (255, 230, 100)))
                            demo_sim.effects.append(RingEffect(clicked_e.x, clicked_e.y, 16, (255, 215, 60)))
                            for _ in range(4):
                                demo_sim.effects.append(DropSpark(clicked_e.x, clicked_e.y, burst=True))
                            if clicked_e.health <= 0:
                                clicked_e.active = False
                                if clicked_e in demo_sim.enemies:
                                    demo_sim.enemies.remove(clicked_e)
                            sfx_click.play()

            pygame.display.flip()
            continue

        # =================================================================
        # ЭКРАН 1: ВЫБОР КАРТЫ
        # =================================================================
        if current_state == STATE_MAP_SELECT:
            play_soundtrack(MAP_SOUNDTRACKS[game_map][1])

            generate_background(bg_surface, bg_time)
            screen.blit(bg_surface, (0, 0))

            upg_btn, ach_btn, bestiary_btn, settings_btn, map_rects, info_btn_rects, btn_minus, btn_plus, start_btn, l_arr_rect, r_arr_rect, dot_rects, greenhouse_btn, relics_btn, dark_panel_btn, menu_btn = draw_map_selection_screen(
                screen, game_map, map_scroll_offset, savedata, mouse_pos
            )

            modal_close_btn = None
            modal_nav_buttons = []
            custom_close_btn = None
            custom_action_btns = []
            if active_custom_map_modal:
                custom_close_btn, _, custom_action_btns = draw_custom_map_setup_modal(screen, savedata, mouse_pos)
            elif active_map_info_modal is not None:
                modal_close_btn, modal_nav_buttons = draw_map_info_modal(
                    screen, active_map_info_modal, savedata, mouse_pos, modal_inspect_wave
                )

            for event in pygame.event.get():
                if hasattr(event, "pos"):
                    mouse_pos = event.pos
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if active_custom_map_modal:
                        if event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                            active_custom_map_modal = False
                            sfx_click.play()
                        continue

                    if active_map_info_modal is not None:
                        if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_i]:
                            active_map_info_modal = None
                            sfx_click.play()
                        elif event.key in [pygame.K_LEFT, pygame.K_a]:
                            modal_inspect_wave = max(1, modal_inspect_wave - 1)
                            sfx_click.play()
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                            modal_inspect_wave = min(150, modal_inspect_wave + 1)
                            sfx_click.play()
                        continue

                    if event.key == pygame.K_g:
                        if is_greenhouse_unlocked(savedata):
                            current_state = STATE_GREENHOUSE
                            inspected_greenhouse_cactus = None
                            sfx_click.play()
                        else:
                            current_state = STATE_UPGRADES
                            selected_tree_node = "greenhouse_unlock"
                            tree_cam_x = 650
                            tree_cam_y = 350
                            sfx_click.play()
                    elif event.key == pygame.K_r:
                        if savedata.get("Upgrades", {}).get("archaeology_unlock", 0) > 0:
                            current_state = STATE_RELICS
                            sfx_click.play()
                        else:
                            current_state = STATE_UPGRADES
                            selected_tree_node = "archaeology_unlock"
                            tree_cam_x = 800
                            tree_cam_y = 120
                            sfx_click.play()
                    elif event.key == pygame.K_u:
                        current_state = STATE_UPGRADES
                    elif event.key == pygame.K_a:
                        current_state = STATE_ACHIEVEMENTS
                    elif event.key == pygame.K_b:
                        bestiary_return_state = STATE_MAP_SELECT
                        current_state = STATE_BESTIARY
                        bestiary_scroll_y = 0
                        sfx_click.play()
                    elif event.key == pygame.K_o:
                        current_state = STATE_SETTINGS
                        settings_source = "map_select"
                        sfx_click.play()
                    elif event.key == pygame.K_ESCAPE:
                        current_state = STATE_MAIN_MENU
                        sfx_click.play()
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        if map_scroll_offset > 0:
                            map_scroll_offset -= 3
                            sfx_click.play()
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        if map_scroll_offset + 3 < len(MAP_NAMES_LIST):
                            map_scroll_offset += 3
                            sfx_click.play()
                    elif event.key == pygame.K_SPACE:
                        is_ok, _ = is_map_unlocked(game_map, savedata)
                        if is_ok:
                            if game_map == 9:
                                cfg = savedata.get("CustomMapConfig", {})
                                p, s = generate_custom_map_path_and_slots(int(cfg.get("seed", 777)))
                                path_list[9], tower_slots_list[9] = p, s
                            screen = play_start_window_animation(bg_time, game_map=game_map, path=path_list[game_map], tower_slots=tower_slots_list[game_map])
                            start_battle_session()
                        else:
                            laser.play()

                if event.type == pygame.MOUSEWHEEL:
                    if active_custom_map_modal:
                        pass
                    elif active_map_info_modal is not None:
                        if event.y > 0:
                            modal_inspect_wave = max(1, modal_inspect_wave - 1)
                        elif event.y < 0:
                            modal_inspect_wave = min(150, modal_inspect_wave + 1)
                    else:
                        if event.y < 0 and map_scroll_offset + 3 < len(MAP_NAMES_LIST):
                            map_scroll_offset += 3
                            sfx_click.play()
                        elif event.y > 0 and map_scroll_offset > 0:
                            map_scroll_offset -= 3
                            sfx_click.play()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if active_custom_map_modal:
                        cfg = savedata.setdefault("CustomMapConfig", {})
                        if custom_close_btn and custom_close_btn.collidepoint(mouse_pos):
                            active_custom_map_modal = False
                            save_data(savedata)
                            sfx_click.play()
                        else:
                            for btn_rect, cat, val in custom_action_btns:
                                if btn_rect.collidepoint(mouse_pos):
                                    if cat == "seed":
                                        if val == "rand":
                                            cfg["seed"] = random.randint(100, 99999)
                                        else:
                                            cfg["seed"] = max(1, min(999999, int(cfg.get("seed", 777)) + val))
                                    elif cat == "hp_mult":
                                        cfg["hp_mult"] = val
                                    elif cat == "spd_mult":
                                        cfg["spd_mult"] = val
                                    elif cat == "start_gold":
                                        cfg["start_gold"] = val
                                    elif cat == "cacti_mult":
                                        cfg["cacti_mult"] = val
                                    elif cat == "biome_style":
                                        cfg["biome_style"] = val
                                    elif cat == "endless":
                                        cfg["endless"] = val
                                    elif cat == "save_close":
                                        active_custom_map_modal = False
                                    elif cat == "apply_and_play":
                                        is_ok, _ = is_map_unlocked(9, savedata)
                                        if is_ok:
                                            active_custom_map_modal = False
                                            save_data(savedata)
                                            sfx_click.play()
                                            game_map = 9
                                            cfg = savedata.get("CustomMapConfig", {})
                                            p, s = generate_custom_map_path_and_slots(int(cfg.get("seed", 777)))
                                            path_list[9], tower_slots_list[9] = p, s
                                            screen = play_start_window_animation(bg_time, game_map=9, path=path_list[9], tower_slots=tower_slots_list[9])
                                            start_battle_session()
                                        else:
                                            laser.play()
                                        break
                                    save_data(savedata)
                                    sfx_click.play()
                                    break
                        continue

                    if active_map_info_modal is not None:
                        mw, mh = 980, 610
                        mx, my = (SCREEN_WIDTH - mw) // 2, (SCREEN_HEIGHT - mh) // 2
                        m_box = pygame.Rect(mx, my, mw, mh)
                        if modal_close_btn and modal_close_btn.collidepoint(mouse_pos):
                            active_map_info_modal = None
                            sfx_click.play()
                        elif not m_box.collidepoint(mouse_pos):
                            active_map_info_modal = None
                            sfx_click.play()
                        else:
                            for nbtn, action in modal_nav_buttons:
                                if nbtn.collidepoint(mouse_pos):
                                    if action == "-10":
                                        modal_inspect_wave = max(1, modal_inspect_wave - 10)
                                    elif action == "-1":
                                        modal_inspect_wave = max(1, modal_inspect_wave - 1)
                                    elif action == "+1":
                                        modal_inspect_wave = min(150, modal_inspect_wave + 1)
                                    elif action == "+10":
                                        modal_inspect_wave = min(150, modal_inspect_wave + 10)
                                    elif isinstance(action, int):
                                        modal_inspect_wave = action
                                    sfx_click.play()
                                    break
                        continue

                    if greenhouse_btn.collidepoint(mouse_pos):
                        if is_greenhouse_unlocked(savedata):
                            current_state = STATE_GREENHOUSE
                            inspected_greenhouse_cactus = None
                            sfx_click.play()
                        else:
                            current_state = STATE_UPGRADES
                            selected_tree_node = "greenhouse_unlock"
                            tree_cam_x = 650
                            tree_cam_y = 350
                            sfx_click.play()
                    elif relics_btn and relics_btn.collidepoint(mouse_pos):
                        if savedata.get("Upgrades", {}).get("archaeology_unlock", 0) > 0:
                            current_state = STATE_RELICS
                            sfx_click.play()
                        else:
                            current_state = STATE_UPGRADES
                            selected_tree_node = "archaeology_unlock"
                            tree_cam_x = 800
                            tree_cam_y = 120
                            sfx_click.play()
                    elif dark_panel_btn and dark_panel_btn.collidepoint(mouse_pos):
                        current_state = STATE_UPGRADES
                        selected_tree_node = "astral_beacon"
                        tree_cam_x = 0
                        tree_cam_y = 815
                        sfx_click.play()
                    elif upg_btn.collidepoint(mouse_pos):
                        current_state = STATE_UPGRADES
                    elif ach_btn.collidepoint(mouse_pos):
                        current_state = STATE_ACHIEVEMENTS
                    elif bestiary_btn.collidepoint(mouse_pos):
                        bestiary_return_state = STATE_MAP_SELECT
                        current_state = STATE_BESTIARY
                        bestiary_scroll_y = 0
                        sfx_click.play()
                    elif settings_btn.collidepoint(mouse_pos):
                        current_state = STATE_SETTINGS
                        settings_source = "map_select"
                        sfx_click.play()
                    elif menu_btn and menu_btn.collidepoint(mouse_pos):
                        current_state = STATE_MAIN_MENU
                        sfx_click.play()

                    # Клик по инфо-кнопкам [i]
                    info_clicked = False
                    for mid, ibtn in info_btn_rects:
                        if ibtn.collidepoint(mouse_pos):
                            is_ok, _ = is_map_unlocked(mid, savedata)
                            if mid == 9 and is_ok:
                                active_custom_map_modal = True
                            else:
                                active_map_info_modal = mid
                                modal_inspect_wave = savedata.get("SelectedStartWave", 1)
                            sfx_click.play()
                            info_clicked = True
                            break
                    if info_clicked:
                        continue

                    for mid, rect in map_rects:
                        if rect.collidepoint(mouse_pos):
                            game_map = mid
                            play_soundtrack(MAP_SOUNDTRACKS[game_map][1])

                    for p_idx, d_rect in dot_rects:
                        if d_rect.collidepoint(mouse_pos):
                            map_scroll_offset = p_idx * 3
                            sfx_click.play()

                    if l_arr_rect.collidepoint(mouse_pos) and map_scroll_offset > 0:
                        map_scroll_offset -= 3
                        sfx_click.play()
                    if r_arr_rect.collidepoint(mouse_pos) and map_scroll_offset + 3 < len(MAP_NAMES_LIST):
                        map_scroll_offset += 3
                        sfx_click.play()

                    # Кнопки выбора волны
                    wave_step_lvl = savedata["Upgrades"].get("start_wave_step", 0)
                    cur_rec = savedata["LevelsRecords"][game_map]
                    max_allowed = 1 + wave_step_lvl * 5
                    if cur_rec > 1: max_allowed = min(max_allowed, (cur_rec // 5) * 5 + 1)
                    else: max_allowed = 1

                    if btn_minus.collidepoint(mouse_pos):
                        savedata["SelectedStartWave"] = max(1, savedata.get("SelectedStartWave", 1) - 5)
                        save_data(savedata)
                    elif btn_plus.collidepoint(mouse_pos):
                        savedata["SelectedStartWave"] = min(max_allowed, savedata.get("SelectedStartWave", 1) + 5)
                        save_data(savedata)

                    if start_btn.collidepoint(mouse_pos):
                        is_ok, _ = is_map_unlocked(game_map, savedata)
                        if is_ok:
                            if game_map == 9:
                                cfg = savedata.get("CustomMapConfig", {})
                                p, s = generate_custom_map_path_and_slots(int(cfg.get("seed", 777)))
                                path_list[9], tower_slots_list[9] = p, s
                            screen = play_start_window_animation(bg_time, game_map=game_map, path=path_list[game_map], tower_slots=tower_slots_list[game_map])
                            start_battle_session()
                        else:
                            laser.play()

            pygame.display.flip()
            continue

        # =================================================================
        # ЭКРАН 2: ДРЕВО УЛУЧШЕНИЙ
        # =================================================================
        elif current_state == STATE_UPGRADES:
            back_rect, center_rect, buy_btn_rect, toggle_btn_rect, node_rects, dark_bal_rect, zoom_in_rect, zoom_out_rect, zoom_reset_rect = draw_upgrade_tree_screen(
                screen, savedata, mouse_pos, tree_cam_x, tree_cam_y, selected_tree_node, is_dragging_tree, tree_zoom, bg_time=bg_time
            )

            for event in pygame.event.get():
                if hasattr(event, "pos"):
                    mouse_pos = event.pos
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_u]:
                        current_state = STATE_MAP_SELECT
                        sfx_click.play()
                    elif event.key == pygame.K_r:
                        if savedata["Upgrades"].get("archaeology_unlock", 0) > 0:
                            current_state = STATE_RELICS
                            sfx_click.play()
                    elif event.key == pygame.K_g:
                        if savedata["Upgrades"].get("greenhouse_unlock", 0) > 0:
                            current_state = STATE_GREENHOUSE
                            inspected_greenhouse_cactus = None
                            sfx_click.play()
                    elif event.key == pygame.K_c:
                        tree_cam_x = 0
                        tree_cam_y = 40
                        tree_zoom = 1.0
                        sfx_click.play()
                    elif event.key in [pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS]:
                        new_zoom = min(2.2, tree_zoom + 0.15)
                        if new_zoom != tree_zoom:
                            px, py = (SCREEN_WIDTH - 350) / 2, 64 + (SCREEN_HEIGHT - 64 - 30) / 2
                            tree_cam_x += px * (1.0 / tree_zoom - 1.0 / new_zoom)
                            tree_cam_y += py * (1.0 / tree_zoom - 1.0 / new_zoom)
                            tree_zoom = new_zoom
                            sfx_click.play()
                    elif event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]:
                        new_zoom = max(0.45, tree_zoom - 0.15)
                        if new_zoom != tree_zoom:
                            px, py = (SCREEN_WIDTH - 350) / 2, 64 + (SCREEN_HEIGHT - 64 - 30) / 2
                            tree_cam_x += px * (1.0 / tree_zoom - 1.0 / new_zoom)
                            tree_cam_y += py * (1.0 / tree_zoom - 1.0 / new_zoom)
                            tree_zoom = new_zoom
                            sfx_click.play()
                    elif event.key in [pygame.K_0, pygame.K_KP_0]:
                        if tree_zoom != 1.0:
                            px, py = (SCREEN_WIDTH - 350) / 2, 64 + (SCREEN_HEIGHT - 64 - 30) / 2
                            tree_cam_x += px * (1.0 / tree_zoom - 1.0)
                            tree_cam_y += py * (1.0 / tree_zoom - 1.0)
                            tree_zoom = 1.0
                            sfx_click.play()
                    elif event.key == pygame.K_t:
                        sel = UPGRADE_TREE_NODES.get(selected_tree_node, {})
                        if sel.get("toggleable") and savedata["Upgrades"].get(selected_tree_node, 0) > 0:
                            is_active = savedata.get("Toggles", {}).get(selected_tree_node, True)
                            if "Toggles" not in savedata:
                                savedata["Toggles"] = {}
                            savedata["Toggles"][selected_tree_node] = not is_active
                            save_data(savedata)
                            sfx_click.play()
                    elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        if selected_tree_node == "archaeology_unlock" and savedata["Upgrades"].get("archaeology_unlock", 0) > 0:
                            current_state = STATE_RELICS
                            sfx_click.play()
                            continue
                        elif selected_tree_node == "greenhouse_unlock" and savedata["Upgrades"].get("greenhouse_unlock", 0) > 0:
                            current_state = STATE_GREENHOUSE
                            inspected_greenhouse_cactus = None
                            sfx_click.play()
                            continue
                        cur_lvl = savedata["Upgrades"].get(selected_tree_node, 0)
                        unlocked, _ = check_node_requirements(selected_tree_node, savedata)
                        cost, dark_cost, max_lvl = get_upgrade_node_cost(selected_tree_node, cur_lvl)
                        if unlocked and (cost is not None or dark_cost is not None) and cur_lvl < max_lvl:
                            c_st = cost or 0
                            c_dk = dark_cost or 0
                            if savedata.get("StellarCactuses", 0) >= c_st and savedata.get("DarkCactuses", 0) >= c_dk:
                                savedata["StellarCactuses"] = savedata.get("StellarCactuses", 0) - c_st
                                savedata["DarkCactuses"] = savedata.get("DarkCactuses", 0) - c_dk
                                savedata["Upgrades"][selected_tree_node] = cur_lvl + 1
                                save_data(savedata)
                                sfx_upgrade.play()
                            else:
                                laser.play()
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        tree_cam_y = max(-400, tree_cam_y - int(50 / tree_zoom))
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        tree_cam_y = min(2200, tree_cam_y + int(50 / tree_zoom))
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        tree_cam_x = max(-800, tree_cam_x - int(50 / tree_zoom))
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        tree_cam_x = min(1800, tree_cam_x + int(50 / tree_zoom))

                elif event.type == pygame.MOUSEWHEEL:
                    zoom_delta = 0.12 * event.y
                    new_zoom = max(0.45, min(2.2, tree_zoom + zoom_delta))
                    if abs(new_zoom - tree_zoom) > 0.001:
                        if mouse_pos[0] < SCREEN_WIDTH - 350 and 64 <= mouse_pos[1] <= SCREEN_HEIGHT - 30:
                            px, py = mouse_pos[0], mouse_pos[1]
                        else:
                            px, py = (SCREEN_WIDTH - 350) / 2, 64 + (SCREEN_HEIGHT - 64 - 30) / 2
                        tree_cam_x += px * (1.0 / tree_zoom - 1.0 / new_zoom)
                        tree_cam_y += py * (1.0 / tree_zoom - 1.0 / new_zoom)
                        tree_zoom = new_zoom

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                    if back_rect.collidepoint(mouse_pos):
                        current_state = STATE_MAP_SELECT
                        sfx_click.play()
                        continue
                    elif center_rect.collidepoint(mouse_pos):
                        tree_cam_x = 0
                        tree_cam_y = 40
                        tree_zoom = 1.0
                        sfx_click.play()
                        continue
                    elif zoom_in_rect and zoom_in_rect.collidepoint(mouse_pos):
                        new_zoom = min(2.2, tree_zoom + 0.15)
                        if new_zoom != tree_zoom:
                            px, py = (SCREEN_WIDTH - 350) / 2, 64 + (SCREEN_HEIGHT - 64 - 30) / 2
                            tree_cam_x += px * (1.0 / tree_zoom - 1.0 / new_zoom)
                            tree_cam_y += py * (1.0 / tree_zoom - 1.0 / new_zoom)
                            tree_zoom = new_zoom
                            sfx_click.play()
                        continue
                    elif zoom_out_rect and zoom_out_rect.collidepoint(mouse_pos):
                        new_zoom = max(0.45, tree_zoom - 0.15)
                        if new_zoom != tree_zoom:
                            px, py = (SCREEN_WIDTH - 350) / 2, 64 + (SCREEN_HEIGHT - 64 - 30) / 2
                            tree_cam_x += px * (1.0 / tree_zoom - 1.0 / new_zoom)
                            tree_cam_y += py * (1.0 / tree_zoom - 1.0 / new_zoom)
                            tree_zoom = new_zoom
                            sfx_click.play()
                        continue
                    elif zoom_reset_rect and zoom_reset_rect.collidepoint(mouse_pos):
                        if tree_zoom != 1.0:
                            px, py = (SCREEN_WIDTH - 350) / 2, 64 + (SCREEN_HEIGHT - 64 - 30) / 2
                            tree_cam_x += px * (1.0 / tree_zoom - 1.0)
                            tree_cam_y += py * (1.0 / tree_zoom - 1.0)
                            tree_zoom = 1.0
                            sfx_click.play()
                        continue
                    elif dark_bal_rect and dark_bal_rect.collidepoint(mouse_pos):
                        selected_tree_node = "astral_beacon"
                        tree_cam_x = 0
                        tree_cam_y = 815
                        tree_zoom = 1.0
                        sfx_click.play()
                        continue
                    elif toggle_btn_rect and toggle_btn_rect.collidepoint(mouse_pos):
                        is_active = savedata.get("Toggles", {}).get(selected_tree_node, True)
                        if "Toggles" not in savedata:
                            savedata["Toggles"] = {}
                        savedata["Toggles"][selected_tree_node] = not is_active
                        save_data(savedata)
                        sfx_click.play()
                        continue
                    elif buy_btn_rect.collidepoint(mouse_pos):
                        if selected_tree_node == "archaeology_unlock" and savedata["Upgrades"].get("archaeology_unlock", 0) > 0:
                            current_state = STATE_RELICS
                            sfx_click.play()
                            continue
                        elif selected_tree_node == "greenhouse_unlock" and savedata["Upgrades"].get("greenhouse_unlock", 0) > 0:
                            current_state = STATE_GREENHOUSE
                            inspected_greenhouse_cactus = None
                            sfx_click.play()
                            continue
                        cur_lvl = savedata["Upgrades"].get(selected_tree_node, 0)
                        unlocked, _ = check_node_requirements(selected_tree_node, savedata)
                        cost, dark_cost, max_lvl = get_upgrade_node_cost(selected_tree_node, cur_lvl)
                        if unlocked and (cost is not None or dark_cost is not None) and cur_lvl < max_lvl:
                            c_st = cost or 0
                            c_dk = dark_cost or 0
                            if savedata.get("StellarCactuses", 0) >= c_st and savedata.get("DarkCactuses", 0) >= c_dk:
                                savedata["StellarCactuses"] = savedata.get("StellarCactuses", 0) - c_st
                                savedata["DarkCactuses"] = savedata.get("DarkCactuses", 0) - c_dk
                                savedata["Upgrades"][selected_tree_node] = cur_lvl + 1
                                save_data(savedata)
                                sfx_upgrade.play()
                            else:
                                laser.play()
                        continue

                    # Нажатие на холст древа (перемещение или выбор ноды)
                    if mouse_pos[0] < SCREEN_WIDTH - 350 and mouse_pos[1] > 64:
                        is_dragging_tree = True
                        tree_drag_start = mouse_pos
                        tree_drag_cam_start = (tree_cam_x, tree_cam_y)
                        tree_drag_moved = False
                        tree_tap_node = None
                        for nid, nrect in node_rects.items():
                            if nrect.collidepoint(mouse_pos):
                                tree_tap_node = nid
                                break

                elif event.type == pygame.MOUSEBUTTONUP and event.button in (1, 3):
                    if is_dragging_tree:
                        is_dragging_tree = False
                        if not tree_drag_moved:
                            target_nid = tree_tap_node
                            if not target_nid:
                                for nid, nrect in node_rects.items():
                                    if nrect.collidepoint(mouse_pos):
                                        target_nid = nid
                                        break
                            if target_nid:
                                if selected_tree_node == target_nid:
                                    if target_nid == "archaeology_unlock" and savedata["Upgrades"].get(target_nid, 0) > 0:
                                        current_state = STATE_RELICS
                                        sfx_click.play()
                                    elif target_nid == "greenhouse_unlock" and savedata["Upgrades"].get(target_nid, 0) > 0:
                                        current_state = STATE_GREENHOUSE
                                        inspected_greenhouse_cactus = None
                                        sfx_click.play()
                                    else:
                                        cur_lvl = savedata["Upgrades"].get(target_nid, 0)
                                        unlocked, _ = check_node_requirements(target_nid, savedata)
                                        cost, dark_cost, max_lvl = get_upgrade_node_cost(target_nid, cur_lvl)
                                        if unlocked and (cost is not None or dark_cost is not None) and cur_lvl < max_lvl:
                                            c_st = cost or 0
                                            c_dk = dark_cost or 0
                                            if savedata.get("StellarCactuses", 0) >= c_st and savedata.get("DarkCactuses", 0) >= c_dk:
                                                savedata["StellarCactuses"] = savedata.get("StellarCactuses", 0) - c_st
                                                savedata["DarkCactuses"] = savedata.get("DarkCactuses", 0) - c_dk
                                                savedata["Upgrades"][target_nid] = cur_lvl + 1
                                                save_data(savedata)
                                                sfx_upgrade.play()
                                            else:
                                                laser.play()
                                        else:
                                            sfx_click.play()
                                else:
                                    selected_tree_node = target_nid
                                    sfx_click.play()

                elif event.type == pygame.MOUSEMOTION:
                    if is_dragging_tree:
                        dx = mouse_pos[0] - tree_drag_start[0]
                        dy = mouse_pos[1] - tree_drag_start[1]
                        if abs(dx) > 6 or abs(dy) > 6:
                            tree_drag_moved = True
                        tree_cam_x = max(-800, min(1800, tree_drag_cam_start[0] - dx / tree_zoom))
                        tree_cam_y = max(-400, min(2200, tree_drag_cam_start[1] - dy / tree_zoom))

            pygame.display.flip()
            continue

        # =================================================================
        # ЭКРАН 3: ДОСТИЖЕНИЯ И НАГРАДЫ
        # =================================================================
        elif current_state == STATE_ACHIEVEMENTS:
            back_rect, claim_buttons, claim_all_btn, tab_actions, max_ach_scroll = draw_achievements_screen(
                screen, savedata, mouse_pos, ach_scroll_y, filter_status=ach_filter_status, filter_cat=ach_filter_cat, bg_time=bg_time
            )

            for event in pygame.event.get():
                if hasattr(event, "pos"):
                    mouse_pos = event.pos
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_a, pygame.K_SPACE, getattr(pygame, 'K_AC_BACK', -999)]:
                        current_state = STATE_MAP_SELECT
                        sfx_click.play()
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        ach_scroll_y = max(0, ach_scroll_y - 60)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        ach_scroll_y = min(max_ach_scroll, ach_scroll_y + 60)
                    elif event.key == pygame.K_PAGEUP:
                        ach_scroll_y = max(0, ach_scroll_y - 300)
                    elif event.key == pygame.K_PAGEDOWN:
                        ach_scroll_y = min(max_ach_scroll, ach_scroll_y + 300)
                    elif event.key == pygame.K_HOME:
                        ach_scroll_y = 0
                    elif event.key == pygame.K_END:
                        ach_scroll_y = max_ach_scroll

                elif event.type == pygame.MOUSEWHEEL:
                    ach_scroll_y = max(0, min(max_ach_scroll, ach_scroll_y - event.y * 50))

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    is_dragging_ach = True
                    ach_drag_start_y = mouse_pos[1]
                    ach_drag_start_scroll = ach_scroll_y
                    ach_drag_moved = False

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if is_dragging_ach:
                        is_dragging_ach = False
                        if not ach_drag_moved:
                            if back_rect.collidepoint(mouse_pos):
                                current_state = STATE_MAP_SELECT
                                sfx_click.play()

                            # Кнопка «Забрать всё»
                            elif claim_all_btn and claim_all_btn.collidepoint(mouse_pos):
                                total_claimed = 0
                                ach_dict = savedata.setdefault("Achievements", {})
                                for ach in ACHIEVEMENTS_DATA:
                                    aid = ach["id"]
                                    st = ach_dict.get(aid, {})
                                    if st.get("unlocked", False) and not st.get("claimed", False):
                                        st["claimed"] = True
                                        total_claimed += ach["reward"]
                                if total_claimed > 0:
                                    savedata["StellarCactuses"] = savedata.get("StellarCactuses", 0) + total_claimed
                                    sfx_achievement.play()
                                    save_data(savedata)

                            else:
                                tab_hit = False
                                # Переключение статусов (Все, Готовы, В процессе, Выполнены)
                                for s_rect, s_key in tab_actions.get("status", []):
                                    if s_rect.collidepoint(mouse_pos) and ach_filter_status != s_key:
                                        ach_filter_status = s_key
                                        ach_scroll_y = 0
                                        sfx_click.play()
                                        tab_hit = True
                                        break

                                # Переключение категорий (Бой, Башни, Оранжерея, Таланты)
                                if not tab_hit:
                                    for c_rect, c_key in tab_actions.get("cat", []):
                                        if c_rect.collidepoint(mouse_pos) and ach_filter_cat != c_key:
                                            ach_filter_cat = c_key
                                            ach_scroll_y = 0
                                            sfx_click.play()
                                            tab_hit = True
                                            break

                                if not tab_hit:
                                    for aid, b_rect, reward in claim_buttons:
                                        if b_rect.collidepoint(mouse_pos):
                                            savedata.setdefault("Achievements", {})[aid]["claimed"] = True
                                            savedata["StellarCactuses"] = savedata.get("StellarCactuses", 0) + reward
                                            sfx_achievement.play()
                                            save_data(savedata)
                                            break

                elif event.type == pygame.MOUSEMOTION:
                    if is_dragging_ach:
                        dy = mouse_pos[1] - ach_drag_start_y
                        if abs(dy) > 5:
                            ach_drag_moved = True
                        ach_scroll_y = max(0, min(max_ach_scroll, ach_drag_start_scroll - dy))

                # Мобильный свайп пальцем (Android touch events)
                elif event.type == pygame.FINGERDOWN:
                    touch_pos = (int(event.x * SCREEN_WIDTH), int(event.y * SCREEN_HEIGHT))
                    mouse_pos = touch_pos
                    is_dragging_ach = True
                    ach_drag_start_y = touch_pos[1]
                    ach_drag_start_scroll = ach_scroll_y
                    ach_drag_moved = False

                elif event.type == pygame.FINGERMOTION:
                    touch_pos = (int(event.x * SCREEN_WIDTH), int(event.y * SCREEN_HEIGHT))
                    mouse_pos = touch_pos
                    if is_dragging_ach:
                        delta_px = event.dy * SCREEN_HEIGHT * 1.5
                        if abs(delta_px) > 2:
                            ach_drag_moved = True
                        ach_scroll_y = max(0, min(max_ach_scroll, ach_scroll_y - delta_px))

                elif event.type == pygame.FINGERUP:
                    touch_pos = (int(event.x * SCREEN_WIDTH), int(event.y * SCREEN_HEIGHT))
                    mouse_pos = touch_pos
                    if is_dragging_ach:
                        is_dragging_ach = False
                        if not ach_drag_moved:
                            if back_rect.collidepoint(touch_pos):
                                current_state = STATE_MAP_SELECT
                                sfx_click.play()
                            elif claim_all_btn and claim_all_btn.collidepoint(touch_pos):
                                total_claimed = 0
                                ach_dict = savedata.setdefault("Achievements", {})
                                for ach in ACHIEVEMENTS_DATA:
                                    aid = ach["id"]
                                    st = ach_dict.get(aid, {})
                                    if st.get("unlocked", False) and not st.get("claimed", False):
                                        st["claimed"] = True
                                        total_claimed += ach["reward"]
                                if total_claimed > 0:
                                    savedata["StellarCactuses"] = savedata.get("StellarCactuses", 0) + total_claimed
                                    sfx_achievement.play()
                                    save_data(savedata)
                            else:
                                tab_hit = False
                                for s_rect, s_key in tab_actions.get("status", []):
                                    if s_rect.collidepoint(touch_pos) and ach_filter_status != s_key:
                                        ach_filter_status = s_key
                                        ach_scroll_y = 0
                                        sfx_click.play()
                                        tab_hit = True
                                        break
                                if not tab_hit:
                                    for c_rect, c_key in tab_actions.get("cat", []):
                                        if c_rect.collidepoint(touch_pos) and ach_filter_cat != c_key:
                                            ach_filter_cat = c_key
                                            ach_scroll_y = 0
                                            sfx_click.play()
                                            tab_hit = True
                                            break
                                if not tab_hit:
                                    for aid, b_rect, reward in claim_buttons:
                                        if b_rect.collidepoint(touch_pos):
                                            savedata.setdefault("Achievements", {})[aid]["claimed"] = True
                                            savedata["StellarCactuses"] = savedata.get("StellarCactuses", 0) + reward
                                            sfx_achievement.play()
                                            save_data(savedata)
                                            break

            pygame.display.flip()
            continue

        # =================================================================
        # ЭКРАН 2.8: ОРАНЖЕРЕЯ КАКТУСОВ (GREENHOUSE & FLORA COLLECTION)
        # =================================================================
        elif current_state == STATE_GREENHOUSE:
            generate_background(bg_surface, bg_time)
            screen.blit(bg_surface, (0, 0))

            back_btn, upgrade_buttons, card_rects, modal_close_btn, modal_upg_btn = draw_greenhouse_screen(
                screen, savedata, mouse_pos, inspected_greenhouse_cactus, bg_time=bg_time
            )

            for event in pygame.event.get():
                if hasattr(event, "pos"):
                    mouse_pos = event.pos
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if inspected_greenhouse_cactus is not None:
                        if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_g]:
                            inspected_greenhouse_cactus = None
                            sfx_click.play()
                        elif event.key in [pygame.K_RETURN, pygame.K_UP]:
                            success, msg = level_up_greenhouse_cactus(savedata, inspected_greenhouse_cactus)
                            if success:
                                sfx_upgrade.play()
                            else:
                                laser.play()
                        continue

                    if event.key in [pygame.K_ESCAPE, pygame.K_g, pygame.K_SPACE]:
                        current_state = STATE_MAP_SELECT
                        inspected_greenhouse_cactus = None
                        sfx_click.play()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Если открыто модальное окно подробного осмотра
                    if inspected_greenhouse_cactus is not None:
                        mw, mh = 940, 580
                        mx, my = (SCREEN_WIDTH - mw) // 2, (SCREEN_HEIGHT - mh) // 2
                        m_box = pygame.Rect(mx, my, mw, mh)

                        if modal_close_btn and modal_close_btn.collidepoint(mouse_pos):
                            inspected_greenhouse_cactus = None
                            sfx_click.play()
                        elif modal_upg_btn and modal_upg_btn.collidepoint(mouse_pos):
                            success, msg = level_up_greenhouse_cactus(savedata, inspected_greenhouse_cactus)
                            if success:
                                sfx_upgrade.play()
                            else:
                                laser.play()
                        elif not m_box.collidepoint(mouse_pos):
                            inspected_greenhouse_cactus = None
                            sfx_click.play()
                        continue

                    # Нажатие на кнопку НАЗАД
                    if back_btn.collidepoint(mouse_pos):
                        current_state = STATE_MAP_SELECT
                        inspected_greenhouse_cactus = None
                        sfx_click.play()
                        continue

                    # Клик по кнопке улучшения на карточке
                    upg_clicked = False
                    for cid, ubtn in upgrade_buttons:
                        if ubtn.collidepoint(mouse_pos):
                            success, msg = level_up_greenhouse_cactus(savedata, cid)
                            if success:
                                sfx_upgrade.play()
                            else:
                                laser.play()
                            upg_clicked = True
                            break
                    if upg_clicked:
                        continue

                    # Клик по карточке для детального просмотра
                    for cid, crect in card_rects:
                        if crect.collidepoint(mouse_pos):
                            inspected_greenhouse_cactus = cid
                            sfx_click.play()
                            break

            pygame.display.flip()
            continue

        # =================================================================
        # ЭКРАН 2.4: МУЗЕЙ РЕЛИКВИЙ (ARCHAEOLOGY MUSEUM)
        # =================================================================
        elif current_state == STATE_RELICS:
            back_btn, relic_click_rects, pedestal_click_rects = draw_relics_screen(screen, savedata, mouse_pos, bg_time=bg_time)

            for event in pygame.event.get():
                if hasattr(event, "pos"):
                    mouse_pos = event.pos
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_r, pygame.K_SPACE]:
                        current_state = STATE_MAP_SELECT
                        sfx_click.play()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back_btn and back_btn.collidepoint(mouse_pos):
                        current_state = STATE_MAP_SELECT
                        sfx_click.play()
                    else:
                        # Клик по пьедесталам для снятия реликвии
                        ped_clicked = False
                        for s_i, s_rect, eq_rid in pedestal_click_rects:
                            if s_rect.collidepoint(mouse_pos):
                                if eq_rid:
                                    unequip_relic(savedata, eq_rid)
                                    save_data(savedata)
                                    sfx_click.play()
                                ped_clicked = True
                                break

                        if not ped_clicked:
                            # Клик по карточке реликвии для экипировки / снятия
                            relics_dict = savedata.get("Relics", {})
                            for rid, s_rect in relic_click_rects.items():
                                if s_rect.collidepoint(mouse_pos):
                                    if relics_dict.get(rid, {}).get("level", 0) > 0:
                                        equipped = get_equipped_relics(savedata)
                                        if rid in equipped:
                                            unequip_relic(savedata, rid)
                                            sfx_click.play()
                                        else:
                                            success = equip_relic(savedata, rid)
                                            if success:
                                                sfx_click.play()
                                            else:
                                                sfx_sell.play()
                                        save_data(savedata)
                                    break

            pygame.display.flip()
            continue

        # =================================================================
        # ЭКРАН 2.5: СЛОВАРЬ СЛАЙМОВ (BESTIARY)
        # =================================================================
        elif current_state == STATE_BESTIARY:
            back_btn, claim_buttons, max_b_scroll = draw_bestiary_screen(
                screen, savedata, mouse_pos, bestiary_scroll_y, bg_time=bg_time
            )

            for event in pygame.event.get():
                if hasattr(event, "pos"):
                    mouse_pos = event.pos
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_b, pygame.K_SPACE, getattr(pygame, 'K_AC_BACK', -999)]:
                        current_state = bestiary_return_state
                        sfx_click.play()
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        bestiary_scroll_y = max(0, bestiary_scroll_y - 50)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        bestiary_scroll_y = min(max_b_scroll, bestiary_scroll_y + 50)

                elif event.type == pygame.MOUSEWHEEL:
                    bestiary_scroll_y = max(0, min(max_b_scroll, bestiary_scroll_y - event.y * 45))

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    is_dragging_bestiary = True
                    bestiary_drag_start_y = mouse_pos[1]
                    bestiary_drag_start_scroll = bestiary_scroll_y
                    bestiary_drag_moved = False

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if is_dragging_bestiary:
                        is_dragging_bestiary = False
                        if not bestiary_drag_moved:
                            if back_btn.collidepoint(mouse_pos):
                                current_state = bestiary_return_state
                                sfx_click.play()

                            else:
                                for sid, b_rect, r_star, r_dark in claim_buttons:
                                    if b_rect.collidepoint(mouse_pos):
                                        b_claimed = savedata.setdefault("BestiaryClaimed", {})
                                        already_claimed = False
                                        if isinstance(b_claimed, dict):
                                            already_claimed = bool(b_claimed.get(str(sid), False))
                                            if not already_claimed:
                                                b_claimed[str(sid)] = True
                                        elif isinstance(b_claimed, list):
                                            already_claimed = (sid in b_claimed)
                                            if not already_claimed:
                                                b_claimed.append(sid)
                                        else:
                                            savedata["BestiaryClaimed"] = {str(sid): True}

                                        if not already_claimed:
                                            savedata["StellarCactuses"] = savedata.get("StellarCactuses", 0) + r_star
                                            savedata["DarkCactuses"] = savedata.get("DarkCactuses", 0) + r_dark
                                            sfx_achievement.play()
                                            save_data(savedata)
                                        break

                elif event.type == pygame.MOUSEMOTION:
                    if is_dragging_bestiary:
                        dy = mouse_pos[1] - bestiary_drag_start_y
                        if abs(dy) > 5:
                            bestiary_drag_moved = True
                        bestiary_scroll_y = max(0, min(max_b_scroll, bestiary_drag_start_scroll - dy))

                # Мобильный свайп пальцем (Android touch events)
                elif event.type == pygame.FINGERDOWN:
                    touch_pos = (int(event.x * SCREEN_WIDTH), int(event.y * SCREEN_HEIGHT))
                    mouse_pos = touch_pos
                    is_dragging_bestiary = True
                    bestiary_drag_start_y = touch_pos[1]
                    bestiary_drag_start_scroll = bestiary_scroll_y
                    bestiary_drag_moved = False

                elif event.type == pygame.FINGERMOTION:
                    touch_pos = (int(event.x * SCREEN_WIDTH), int(event.y * SCREEN_HEIGHT))
                    mouse_pos = touch_pos
                    if is_dragging_bestiary:
                        delta_px = event.dy * SCREEN_HEIGHT * 1.5
                        if abs(delta_px) > 2:
                            bestiary_drag_moved = True
                        bestiary_scroll_y = max(0, min(max_b_scroll, bestiary_scroll_y - delta_px))

                elif event.type == pygame.FINGERUP:
                    touch_pos = (int(event.x * SCREEN_WIDTH), int(event.y * SCREEN_HEIGHT))
                    mouse_pos = touch_pos
                    if is_dragging_bestiary:
                        is_dragging_bestiary = False
                        if not bestiary_drag_moved:
                            if back_btn.collidepoint(touch_pos):
                                current_state = bestiary_return_state
                                sfx_click.play()
                            else:
                                for sid, b_rect, r_star, r_dark in claim_buttons:
                                    if b_rect.collidepoint(touch_pos):
                                        b_claimed = savedata.setdefault("BestiaryClaimed", {})
                                        already_claimed = False
                                        if isinstance(b_claimed, dict):
                                            already_claimed = bool(b_claimed.get(str(sid), False))
                                            if not already_claimed:
                                                b_claimed[str(sid)] = True
                                        elif isinstance(b_claimed, list):
                                            already_claimed = (sid in b_claimed)
                                            if not already_claimed:
                                                b_claimed.append(sid)
                                        else:
                                            savedata["BestiaryClaimed"] = {str(sid): True}

                                        if not already_claimed:
                                            savedata["StellarCactuses"] = savedata.get("StellarCactuses", 0) + r_star
                                            savedata["DarkCactuses"] = savedata.get("DarkCactuses", 0) + r_dark
                                            sfx_achievement.play()
                                            save_data(savedata)
                                        break

            pygame.display.flip()
            continue

        # =================================================================
        # ЭКРАН 7: ТИТРЫ И ЭПИЛОГ (ПОБЕДА НАД ИСТИННЫМ ПОВЕЛИТЕЛЕМ БЕЗДНЫ)
        # =================================================================
        elif current_state == STATE_CREDITS:
            btn_cont_rect, btn_menu_rect, max_scroll = draw_credits_screen(
                screen, credits_scroll_y, savedata, mouse_pos, source=credits_source
            )

            for event in pygame.event.get():
                if hasattr(event, "pos"):
                    mouse_pos = event.pos
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        if credits_source == "settings":
                            current_state = STATE_SETTINGS
                            play_soundtrack(MAP_SOUNDTRACKS[0][1])
                            sfx_click.play()
                        else:
                            # Титры != конец: продолжаем сессию в бесконечном режиме 101+
                            current_state = STATE_PLAYING
                            play_soundtrack(MAP_SOUNDTRACKS[game_map][1])
                            sfx_click.play()
                    elif event.key == pygame.K_ESCAPE:
                        if credits_source == "settings":
                            current_state = STATE_SETTINGS
                            play_soundtrack(MAP_SOUNDTRACKS[0][1])
                            sfx_click.play()
                        else:
                            current_state = STATE_MAP_SELECT
                            play_soundtrack(MAP_SOUNDTRACKS[game_map][1])
                            save_data(savedata)
                            sfx_click.play()
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        credits_scroll_y = max(0.0, credits_scroll_y - 45)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        credits_scroll_y = min(max_scroll, credits_scroll_y + 45)

                elif event.type == pygame.MOUSEWHEEL:
                    credits_scroll_y = max(0.0, min(max_scroll, credits_scroll_y - event.y * 38))

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                    if btn_cont_rect.collidepoint(mouse_pos):
                        if credits_source == "settings":
                            current_state = STATE_SETTINGS
                            play_soundtrack(MAP_SOUNDTRACKS[0][1])
                            sfx_click.play()
                        else:
                            # Продолжаем оборону с волны 101+ со всеми башнями
                            current_state = STATE_PLAYING
                            play_soundtrack(MAP_SOUNDTRACKS[game_map][1])
                            sfx_click.play()
                    elif btn_menu_rect.collidepoint(mouse_pos):
                        current_state = STATE_MAP_SELECT
                        play_soundtrack(MAP_SOUNDTRACKS[game_map][1])
                        save_data(savedata)
                        sfx_click.play()

            pygame.display.flip()
            continue

        # =================================================================
        # ЭКРАН 8: НАСТРОЙКИ И ОПЦИИ
        # =================================================================
        elif current_state == STATE_SETTINGS:
            generate_background(bg_surface, bg_time)
            screen.blit(bg_surface, (0, 0))

            ui_rects = draw_settings_screen(
                screen, savedata, mouse_pos,
                confirming_reset=confirming_reset,
                current_tab=settings_tab,
                saves_scroll_y=saves_scroll_y,
                modal_state=save_modal_state,
                bg_time=bg_time
            )

            for event in pygame.event.get():
                if hasattr(event, "pos"):
                    mouse_pos = event.pos
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEWHEEL:
                    if settings_tab == "saves" and not save_modal_state and not confirming_reset:
                        max_s = ui_rects.get("max_scroll", 0)
                        saves_scroll_y = max(0, min(saves_scroll_y - event.y * 36, max_s))

                elif event.type == pygame.TEXTINPUT:
                    if save_modal_state and save_modal_state.get("type") == "input":
                        cur_txt = save_modal_state.get("text", "")
                        if len(cur_txt) < 24:
                            save_modal_state["text"] = cur_txt + event.text
                    elif save_modal_state and save_modal_state.get("type") == "import":
                        cur_txt = save_modal_state.get("text", "")
                        save_modal_state["text"] = cur_txt + event.text
                        save_modal_state.pop("error", None)

                elif event.type == pygame.KEYDOWN:
                    # 1. Если активно модальное окно управления слотом
                    if save_modal_state:
                        if event.key == pygame.K_ESCAPE:
                            save_modal_state = None
                            try:
                                pygame.key.stop_text_input()
                            except Exception:
                                pass
                            sfx_click.play()
                        elif save_modal_state.get("type") == "export":
                            if event.key in [pygame.K_c, pygame.K_RETURN, pygame.K_KP_ENTER]:
                                set_clipboard_text(save_modal_state.get("code", ""))
                                sfx_click.play()
                        elif save_modal_state.get("type") == "input":
                            if event.key == pygame.K_BACKSPACE:
                                cur_t = save_modal_state.get("text", "")
                                if cur_t:
                                    save_modal_state["text"] = cur_t[:-1]
                                    sfx_click.play()
                            elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                                mode = save_modal_state.get("mode")
                                val = save_modal_state.get("text", "").strip()
                                if mode == "create":
                                    sid, new_data = create_save_profile(val or "Новое сохранение", make_active=True)
                                    savedata.clear()
                                    savedata.update(new_data)
                                    apply_audio_settings(savedata)
                                    sfx_sprout_collect.play()
                                elif mode == "rename":
                                    tid = save_modal_state.get("target_id")
                                    rename_save_profile(tid, val or "Без названия")
                                    if tid == savedata.get("SaveId"):
                                        savedata["SaveName"] = val or "Без названия"
                                    sfx_sprout_collect.play()
                                save_modal_state = None
                                try:
                                    pygame.key.stop_text_input()
                                except Exception:
                                    pass
                        elif save_modal_state.get("type") == "import":
                            if event.key == pygame.K_BACKSPACE:
                                cur_t = save_modal_state.get("text", "")
                                if cur_t:
                                    save_modal_state["text"] = cur_t[:-1]
                                    save_modal_state.pop("error", None)
                                    sfx_click.play()
                            elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                                clip = get_clipboard_text()
                                if clip:
                                    save_modal_state["text"] = clip
                                    save_modal_state.pop("error", None)
                                    sfx_click.play()
                            elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                                val = save_modal_state.get("text", "").strip()
                                if val:
                                    try:
                                        sid, new_data = import_save_profile(val, as_new_slot=True, make_active=True)
                                        savedata.clear()
                                        savedata.update(new_data)
                                        apply_audio_settings(savedata)
                                        set_graphics_preset(savedata.get("Settings", {}).get("graphics_preset", "normal"))
                                        sfx_sprout_collect.play()
                                        save_modal_state = None
                                        try:
                                            pygame.key.stop_text_input()
                                        except Exception:
                                            pass
                                    except Exception as e:
                                        save_modal_state["error"] = f"Ошибка импорта: {str(e)}"
                                        laser.play()
                                else:
                                    save_modal_state["error"] = "Ключ сохранения пуст!"
                                    laser.play()
                        elif save_modal_state.get("type") == "delete_confirm":
                            if event.key in [pygame.K_RETURN, pygame.K_y, pygame.K_KP_ENTER]:
                                tid = save_modal_state.get("target_id")
                                res = delete_save_profile(tid)
                                if res:
                                    savedata.clear()
                                    savedata.update(res)
                                    apply_audio_settings(savedata)
                                sfx_boss_defeat.play()
                                save_modal_state = None
                        continue

                    # 2. Если активно подтверждение сброса текущего сохранения
                    if confirming_reset:
                        if event.key in [pygame.K_ESCAPE, pygame.K_n]:
                            confirming_reset = False
                            sfx_click.play()
                        elif event.key in [pygame.K_y, pygame.K_RETURN]:
                            savedata.clear()
                            savedata.update(json.loads(json.dumps(DEFAULT_SAVE)))
                            save_data(savedata)
                            apply_audio_settings(savedata)
                            confirming_reset = False
                            sfx_boss_defeat.play()
                        continue

                    # 3. Обычная клавиатурная навигация
                    if event.key in [pygame.K_ESCAPE, pygame.K_o]:
                        current_state = STATE_MAIN_MENU if settings_source == "main_menu" else STATE_MAP_SELECT
                        save_data(savedata)
                        sfx_click.play()
                    elif event.key == pygame.K_TAB:
                        settings_tab = "saves" if settings_tab == "general" else "general"
                        sfx_click.play()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Поддержка колеса мыши для старых версий SDL
                    if event.button in [4, 5] and settings_tab == "saves" and not save_modal_state and not confirming_reset:
                        max_s = ui_rects.get("max_scroll", 0)
                        if event.button == 4:
                            saves_scroll_y = max(0, saves_scroll_y - 36)
                        elif event.button == 5:
                            saves_scroll_y = min(max_s, saves_scroll_y + 36)
                        continue

                    if event.button == 1:
                        # 1. Клик при активном модальном окне слотов
                        if save_modal_state:
                            if ui_rects.get("modal_cancel") and ui_rects["modal_cancel"].collidepoint(mouse_pos):
                                save_modal_state = None
                                try:
                                    pygame.key.stop_text_input()
                                except Exception:
                                    pass
                                sfx_click.play()
                            elif ui_rects.get("modal_copy_code") and ui_rects["modal_copy_code"].collidepoint(mouse_pos):
                                set_clipboard_text(save_modal_state.get("code", ""))
                                sfx_click.play()
                            elif ui_rects.get("modal_paste_code") and ui_rects["modal_paste_code"].collidepoint(mouse_pos):
                                clip = get_clipboard_text()
                                if clip:
                                    save_modal_state["text"] = clip
                                    save_modal_state.pop("error", None)
                                    sfx_click.play()
                            elif ui_rects.get("modal_ok") and ui_rects["modal_ok"].collidepoint(mouse_pos):
                                if save_modal_state.get("type") == "input":
                                    mode = save_modal_state.get("mode")
                                    val = save_modal_state.get("text", "").strip()
                                    if mode == "create":
                                        sid, new_data = create_save_profile(val or "Новое сохранение", make_active=True)
                                        savedata.clear()
                                        savedata.update(new_data)
                                        apply_audio_settings(savedata)
                                        set_graphics_preset(savedata.get("Settings", {}).get("graphics_preset", "normal"))
                                        sfx_sprout_collect.play()
                                    elif mode == "rename":
                                        tid = save_modal_state.get("target_id")
                                        rename_save_profile(tid, val or "Без названия")
                                        if tid == savedata.get("SaveId"):
                                            savedata["SaveName"] = val or "Без названия"
                                        sfx_sprout_collect.play()
                                    save_modal_state = None
                                    try:
                                        pygame.key.stop_text_input()
                                    except Exception:
                                        pass
                                elif save_modal_state.get("type") == "import":
                                    val = save_modal_state.get("text", "").strip()
                                    if val:
                                        try:
                                            sid, new_data = import_save_profile(val, as_new_slot=True, make_active=True)
                                            savedata.clear()
                                            savedata.update(new_data)
                                            apply_audio_settings(savedata)
                                            set_graphics_preset(savedata.get("Settings", {}).get("graphics_preset", "normal"))
                                            sfx_sprout_collect.play()
                                            save_modal_state = None
                                            try:
                                                pygame.key.stop_text_input()
                                            except Exception:
                                                pass
                                        except Exception as e:
                                            save_modal_state["error"] = f"Ошибка импорта: {str(e)}"
                                            laser.play()
                                    else:
                                        save_modal_state["error"] = "Ключ сохранения пуст!"
                                        laser.play()
                                elif save_modal_state.get("type") == "delete_confirm":
                                    tid = save_modal_state.get("target_id")
                                    res = delete_save_profile(tid)
                                    if res:
                                        savedata.clear()
                                        savedata.update(res)
                                        apply_audio_settings(savedata)
                                        set_graphics_preset(savedata.get("Settings", {}).get("graphics_preset", "normal"))
                                    sfx_boss_defeat.play()
                                    save_modal_state = None
                            continue

                        # 2. Клик при активном диалоге сброса
                        if confirming_reset:
                            if ui_rects.get("confirm_yes") and ui_rects["confirm_yes"].collidepoint(mouse_pos):
                                savedata.clear()
                                savedata.update(json.loads(json.dumps(DEFAULT_SAVE)))
                                save_data(savedata)
                                apply_audio_settings(savedata)
                                set_graphics_preset(savedata.get("Settings", {}).get("graphics_preset", "normal"))
                                confirming_reset = False
                                sfx_boss_defeat.play()
                            elif ui_rects.get("confirm_no") and ui_rects["confirm_no"].collidepoint(mouse_pos):
                                confirming_reset = False
                                sfx_click.play()
                            continue

                        # 3. Навигация и переключение вкладок
                        if ui_rects.get("back") and ui_rects["back"].collidepoint(mouse_pos):
                            current_state = STATE_MAIN_MENU if settings_source == "main_menu" else STATE_MAP_SELECT
                            save_data(savedata)
                            sfx_click.play()

                        elif ui_rects.get("tab_general") and ui_rects["tab_general"].collidepoint(mouse_pos):
                            settings_tab = "general"
                            sfx_click.play()

                        elif ui_rects.get("tab_saves") and ui_rects["tab_saves"].collidepoint(mouse_pos):
                            settings_tab = "saves"
                            sfx_click.play()

                        elif ui_rects.get("go_to_saves") and ui_rects["go_to_saves"].collidepoint(mouse_pos):
                            settings_tab = "saves"
                            sfx_click.play()

                        # 4. Вкладка "Параметры игры"
                        elif settings_tab == "general":
                            if ui_rects.get("sfx_minus") and ui_rects["sfx_minus"].collidepoint(mouse_pos):
                                cur_v = savedata.setdefault("Settings", {}).get("sfx_volume", 0.7)
                                savedata["Settings"]["sfx_volume"] = max(0.0, round(cur_v - 0.1, 2))
                                apply_audio_settings(savedata)
                                save_data(savedata)
                                sfx_click.play()

                            elif ui_rects.get("sfx_plus") and ui_rects["sfx_plus"].collidepoint(mouse_pos):
                                cur_v = savedata.setdefault("Settings", {}).get("sfx_volume", 0.7)
                                savedata["Settings"]["sfx_volume"] = min(1.0, round(cur_v + 0.1, 2))
                                apply_audio_settings(savedata)
                                save_data(savedata)
                                sfx_click.play()

                            elif ui_rects.get("music_minus") and ui_rects["music_minus"].collidepoint(mouse_pos):
                                cur_v = savedata.setdefault("Settings", {}).get("music_volume", 0.5)
                                savedata["Settings"]["music_volume"] = max(0.0, round(cur_v - 0.1, 2))
                                apply_audio_settings(savedata)
                                save_data(savedata)
                                sfx_click.play()

                            elif ui_rects.get("music_plus") and ui_rects["music_plus"].collidepoint(mouse_pos):
                                cur_v = savedata.setdefault("Settings", {}).get("music_volume", 0.5)
                                savedata["Settings"]["music_volume"] = min(1.0, round(cur_v + 0.1, 2))
                                apply_audio_settings(savedata)
                                save_data(savedata)
                                sfx_click.play()

                            elif ui_rects.get("preset_normal") and ui_rects["preset_normal"].collidepoint(mouse_pos):
                                savedata.setdefault("Settings", {})["graphics_preset"] = "normal"
                                set_graphics_preset("normal")
                                save_data(savedata)
                                sfx_click.play()

                            elif ui_rects.get("preset_opt") and ui_rects["preset_opt"].collidepoint(mouse_pos):
                                savedata.setdefault("Settings", {})["graphics_preset"] = "optimized"
                                set_graphics_preset("optimized")
                                save_data(savedata)
                                sfx_click.play()

                            elif ui_rects.get("scale_sharp") and ui_rects["scale_sharp"].collidepoint(mouse_pos):
                                savedata.setdefault("Settings", {})["scale_quality"] = "sharp"
                                screen = set_scale_quality("sharp")
                                save_data(savedata)
                                sfx_click.play()

                            elif ui_rects.get("scale_smooth") and ui_rects["scale_smooth"].collidepoint(mouse_pos):
                                savedata.setdefault("Settings", {})["scale_quality"] = "smooth"
                                screen = set_scale_quality("smooth")
                                save_data(savedata)
                                sfx_click.play()

                            elif ui_rects.get("window_shake_toggle") and ui_rects["window_shake_toggle"].collidepoint(mouse_pos):
                                cur_wsh = savedata.setdefault("Settings", {}).get("window_shake", True)
                                savedata["Settings"]["window_shake"] = not cur_wsh
                                save_data(savedata)
                                sfx_click.play()
                                if savedata["Settings"]["window_shake"]:
                                    shake_amount = 12.0
                                else:
                                    shake_amount = 0.0
                                    win_mgr.reset_position()

                            elif ui_rects.get("shake_toggle") and ui_rects["shake_toggle"].collidepoint(mouse_pos):
                                cur_sh = savedata.setdefault("Settings", {}).get("screen_shake", False)
                                savedata["Settings"]["screen_shake"] = not cur_sh
                                save_data(savedata)
                                sfx_click.play()
                                if savedata["Settings"]["screen_shake"]:
                                    shake_amount = 12.0
                                else:
                                    shake_amount = 0.0

                            elif ui_rects.get("dmg_toggle") and ui_rects["dmg_toggle"].collidepoint(mouse_pos):
                                cur_dg = savedata.setdefault("Settings", {}).get("damage_numbers", True)
                                savedata["Settings"]["damage_numbers"] = not cur_dg
                                save_data(savedata)
                                sfx_click.play()

                            elif ui_rects.get("auto_wave_toggle") and ui_rects["auto_wave_toggle"].collidepoint(mouse_pos):
                                cur_aw = savedata.setdefault("Settings", {}).get("auto_wave", False)
                                savedata["Settings"]["auto_wave"] = not cur_aw
                                save_data(savedata)
                                sfx_click.play()

                            elif ui_rects.get("credits") and ui_rects["credits"].collidepoint(mouse_pos):
                                if savedata.get("GameCompleted", False) or savedata.get("CreditsSeen", False):
                                    current_state = STATE_CREDITS
                                    credits_source = "settings"
                                    credits_scroll_y = 0.0
                                    play_soundtrack("star_realm.ogg")
                                    win_mgr.victory_bounce()
                                    sfx_click.play()
                                else:
                                    laser.play()

                            elif ui_rects.get("credits_locked") and ui_rects["credits_locked"].collidepoint(mouse_pos):
                                laser.play()

                            elif ui_rects.get("export_active") and ui_rects["export_active"].collidepoint(mouse_pos):
                                code, fpath = export_save_profile()
                                set_clipboard_text(code)
                                save_modal_state = {
                                    "type": "export",
                                    "code": code,
                                    "file": fpath
                                }
                                sfx_sprout_collect.play()

                            elif ui_rects.get("import_active") and ui_rects["import_active"].collidepoint(mouse_pos):
                                clip = get_clipboard_text()
                                pref_text = clip if (clip.startswith("CTD1_") or clip.startswith("{")) else ""
                                save_modal_state = {
                                    "type": "import",
                                    "text": pref_text
                                }
                                try:
                                    pygame.key.start_text_input()
                                except Exception:
                                    pass
                                sfx_click.play()

                            elif ui_rects.get("reset") and ui_rects["reset"].collidepoint(mouse_pos):
                                confirming_reset = True
                                sfx_click.play()

                        # 5. Вкладка "Файлы сохранений"
                        elif settings_tab == "saves":
                            if ui_rects.get("create_save") and ui_rects["create_save"].collidepoint(mouse_pos):
                                save_modal_state = {
                                    "type": "input",
                                    "mode": "create",
                                    "text": f"Слот #{len(list_save_profiles()) + 1}"
                                }
                                try:
                                    pygame.key.start_text_input()
                                except Exception:
                                    pass
                                sfx_click.play()
                            elif ui_rects.get("import_clipboard") and ui_rects["import_clipboard"].collidepoint(mouse_pos):
                                clip = get_clipboard_text()
                                pref_text = clip if (clip.startswith("CTD1_") or clip.startswith("{")) else ""
                                save_modal_state = {
                                    "type": "import",
                                    "text": pref_text
                                }
                                try:
                                    pygame.key.start_text_input()
                                except Exception:
                                    pass
                                sfx_click.play()
                            else:
                                for sa in ui_rects.get("save_actions", []):
                                    if sa.get("select") and sa["select"].collidepoint(mouse_pos):
                                        new_data = switch_active_save(sa["id"])
                                        savedata.clear()
                                        savedata.update(new_data)
                                        apply_audio_settings(savedata)
                                        set_graphics_preset(savedata.get("Settings", {}).get("graphics_preset", "normal"))
                                        sfx_sprout_collect.play()
                                        break
                                    elif sa.get("rename") and sa["rename"].collidepoint(mouse_pos):
                                        save_modal_state = {
                                            "type": "input",
                                            "mode": "rename",
                                            "target_id": sa["id"],
                                            "text": sa["name"]
                                        }
                                        try:
                                            pygame.key.start_text_input()
                                        except Exception:
                                            pass
                                        sfx_click.play()
                                        break
                                    elif sa.get("duplicate") and sa["duplicate"].collidepoint(mouse_pos):
                                        new_id = duplicate_save_profile(sa["id"])
                                        if new_id:
                                            sfx_sprout_collect.play()
                                        break
                                    elif sa.get("export") and sa["export"].collidepoint(mouse_pos):
                                        code, fpath = export_save_profile(sa["id"])
                                        set_clipboard_text(code)
                                        save_modal_state = {
                                            "type": "export",
                                            "code": code,
                                            "file": fpath
                                        }
                                        sfx_sprout_collect.play()
                                        break
                                    elif sa.get("delete") and sa["delete"].collidepoint(mouse_pos):
                                        save_modal_state = {
                                            "type": "delete_confirm",
                                            "target_id": sa["id"],
                                            "name": sa["name"]
                                        }
                                        sfx_click.play()
                                        break

            pygame.display.flip()
            continue

        # =================================================================
        # ЭКРАН 3: ИГРОВОЙ ПРОЦЕСС
        # =================================================================
        elif current_state == STATE_PLAYING:
            game_dt = (raw_dt * game_speed) if not is_paused else 0.0
            ui_dt = (raw_dt * (1.0 + 0.10 * max(0.0, game_speed - 1.0))) if not is_paused else 0.0
            if not is_paused:
                pause_frozen_frame = None

            # Проверка наведения на башню или на её открытую инфо-карточку
            if not IS_ANDROID:
                new_hovered = None
                if not is_paused:
                    mx, my = mouse_pos[0], mouse_pos[1]
                    for tower in towers:
                        dx = mx - tower.x
                        dy = my - tower.y
                        if dx * dx + dy * dy < 1024:
                            new_hovered = tower
                            break

                if new_hovered:
                    if not rally_targeting_tent:
                        inspected_tower = new_hovered
                elif last_card_rect and last_card_rect.collidepoint(mouse_pos) and not is_paused:
                    # Курсор внутри карточки башни — меню остаётся открытым
                    pass
                elif rally_targeting_tent and not is_paused:
                    # Режим выбора точки сбора — сохраняем выделение палатки
                    inspected_tower = rally_targeting_tent
                else:
                    if not is_paused:
                        inspected_tower = None

            hovered_tower = inspected_tower

            for event in pygame.event.get():
                if hasattr(event, "pos"):
                    mouse_pos = event.pos
                # Мультиоконные события окна раскопок (второе окно ОС)
                if dig_window and getattr(event, 'window', None) == dig_window:
                    if event.type == pygame.WINDOWCLOSE:
                        try:
                            dig_window.destroy()
                        except Exception:
                            pass
                        dig_window = None
                        dig_session = None
                        continue
                    elif event.type == pygame.MOUSEMOTION:
                        dig_mouse_pos = event.pos
                        continue
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        close_btn_rect = pygame.Rect(95, 410, 170, 38)
                        if close_btn_rect.collidepoint(event.pos):
                            try:
                                dig_window.destroy()
                            except Exception:
                                pass
                            dig_window = None
                            dig_session = None
                            sfx_click.play()
                            continue
                        gx = (event.pos[0] - 52) // 52
                        gy = (event.pos[1] - 92) // 52
                        if 0 <= gx < 5 and 0 <= gy < 5 and dig_session:
                            res = dig_session.dig_cell(gx, gy)
                            if res == "win":
                                save_data(savedata)
                                effects.append(FloatingText(SCREEN_WIDTH // 2, 200, f"РЕЛИКВИЯ НАЙДЕНА: {dig_session.relic_info['name']}!", (255, 235, 120)))
                                effects.append(RingEffect(SCREEN_WIDTH // 2, 200, 80, GOLD))
                        continue

                # События фейкового окна раскопок (Android и встроенный режим)
                if dig_session and dig_window is None:
                    fake_x = (SCREEN_WIDTH - 360) // 2
                    fake_y = (SCREEN_HEIGHT - 460) // 2
                    fake_rect = pygame.Rect(fake_x, fake_y, 360, 460)

                    if event.type == pygame.KEYDOWN:
                        if event.key in [pygame.K_ESCAPE, pygame.K_x]:
                            dig_session = None
                            sfx_click.play()
                        continue

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if fake_rect.collidepoint(event.pos):
                            local_x = event.pos[0] - fake_x
                            local_y = event.pos[1] - fake_y
                            close_btn_rect = pygame.Rect(95, 410, 170, 38)
                            if close_btn_rect.collidepoint((local_x, local_y)):
                                dig_session = None
                                sfx_click.play()
                                continue
                            gx = (local_x - 52) // 52
                            gy = (local_y - 92) // 52
                            if 0 <= gx < 5 and 0 <= gy < 5 and dig_session:
                                res = dig_session.dig_cell(gx, gy)
                                if res == "win":
                                    save_data(savedata)
                                    effects.append(FloatingText(SCREEN_WIDTH // 2, 200, f"РЕЛИКВИЯ НАЙДЕНА: {dig_session.relic_info['name']}!", (255, 235, 120)))
                                    effects.append(RingEffect(SCREEN_WIDTH // 2, 200, 80, GOLD))
                            continue
                        else:
                            # Клик мимо окна раскопок закрывает его
                            dig_session = None
                            sfx_click.play()
                            continue

                    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                        continue

                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        selected_tower_type = "magic"
                        upgrade_mode = False
                        inspected_tower = None
                    elif event.key == pygame.K_2:
                        selected_tower_type = "rock"
                        upgrade_mode = False
                        inspected_tower = None
                    elif event.key == pygame.K_3:
                        if savedata["Upgrades"].get("freeze_tower", 0) > 0:
                            selected_tower_type = "freeze"
                            upgrade_mode = False
                            inspected_tower = None
                    elif event.key == pygame.K_4:
                        if savedata["Upgrades"].get("tent_tower", 0) > 0:
                            selected_tower_type = "tent"
                            upgrade_mode = False
                            inspected_tower = None
                    elif event.key == pygame.K_5:
                        if savedata["Upgrades"].get("tesla_tower", 0) > 0:
                            selected_tower_type = "tesla"
                            upgrade_mode = False
                            inspected_tower = None
                    elif event.key == pygame.K_6:
                        if savedata["Upgrades"].get("farm_tower", 0) > 0:
                            selected_tower_type = "farm"
                            upgrade_mode = False
                            inspected_tower = None
                    elif event.key == pygame.K_t and not is_paused:
                        if savedata.get("Upgrades", {}).get("wave_rush", 0) > 0:
                            curr = savedata.get("Toggles", {}).get("wave_rush", True)
                            if "Toggles" not in savedata:
                                savedata["Toggles"] = {}
                            savedata["Toggles"]["wave_rush"] = not curr
                            save_data(savedata)
                            sfx_click.play()
                            status_str = "ВКЛЮЧЕНЫ" if not curr else "ОТКЛЮЧЕНЫ"
                            status_col = GREEN if not curr else (255, 100, 100)
                            effects.append(FloatingText(SCREEN_WIDTH // 2, 160, f"ТУРБО-ВОЛНЫ: {status_str}", status_col))
                            if not curr and not wave_in_progress and not game_over:
                                between_waves_timer = 0.0
                        elif inspected_tower:
                            modes = ["FIRST", "STRONGEST", "LAST", "CLOSEST"]
                            cur_idx = modes.index(inspected_tower.target_priority) if inspected_tower.target_priority in modes else 0
                            inspected_tower.target_priority = modes[(cur_idx + 1) % len(modes)]
                            sfx_click.play()
                    elif event.key == pygame.K_y and not is_paused:
                        if savedata.get("Upgrades", {}).get("spawn_rush", 0) > 0:
                            curr = savedata.get("Toggles", {}).get("spawn_rush", True)
                            if "Toggles" not in savedata:
                                savedata["Toggles"] = {}
                            savedata["Toggles"]["spawn_rush"] = not curr
                            save_data(savedata)
                            sfx_click.play()
                            status_str = "ВКЛЮЧЕН" if not curr else "ОТКЛЮЧЕН"
                            status_col = GREEN if not curr else (255, 100, 100)
                            effects.append(FloatingText(SCREEN_WIDTH // 2, 190, f"ПЛОТНЫЙ СПАВН: {status_str}", status_col))
                    elif event.key == pygame.K_TAB and not is_paused:
                        if savedata.get("Upgrades", {}).get("smart_targeting", 0) > 0 and towers:
                            modes = ["FIRST", "STRONGEST", "WEAKEST", "LAST", "CLOSEST"]
                            modes_ru = {"FIRST": "ПЕРВЫЙ", "STRONGEST": "СИЛЬНЫЙ", "WEAKEST": "СЛАБЫЙ", "LAST": "ПОСЛЕДНИЙ", "CLOSEST": "БЛИЖНИЙ"}
                            ref_mode = inspected_tower.target_priority if inspected_tower else towers[0].target_priority
                            cur_idx = modes.index(ref_mode) if ref_mode in modes else 0
                            new_mode = modes[(cur_idx + 1) % len(modes)]
                            for twr in towers:
                                twr.target_priority = new_mode
                            sfx_click.play()
                            bonus_note = " (+10% УРОНА)" if (savedata.get("Upgrades", {}).get("smart_targeting", 0) >= 2 and new_mode == "STRONGEST") else ""
                            effects.append(FloatingText(SCREEN_WIDTH // 2, 160, f"ПРИЦЕЛ ВСЕХ БАШЕН: {modes_ru[new_mode]}{bonus_note}", (100, 220, 255)))
                    elif event.key == pygame.K_x and not is_paused:
                        if savedata.get("Upgrades", {}).get("range_grid", 0) > 0:
                            curr = savedata.get("Toggles", {}).get("range_grid", False)
                            if "Toggles" not in savedata:
                                savedata["Toggles"] = {}
                            savedata["Toggles"]["range_grid"] = not curr
                            save_data(savedata)
                            sfx_click.play()
                            stat_str = "ВКЛЮЧЕНА" if not curr else "ОТКЛЮЧЕНА"
                            stat_col = (100, 220, 255) if not curr else (255, 120, 120)
                            effects.append(FloatingText(SCREEN_WIDTH // 2, 160, f"СЕТКА РАДИУСОВ: {stat_str}", stat_col))
                    elif event.key == pygame.K_f and not is_paused and not game_over:
                        if savedata.get("Upgrades", {}).get("orbital_strike", 0) > 0 and orbital_strike_cd <= 0:
                            if not orbital_targeting:
                                orbital_targeting = True
                                selected_tower_type = None
                                inspected_tower = None
                                sfx_click.play()
                                effects.append(FloatingText(SCREEN_WIDTH // 2, 140, "ПРИЦЕЛИВАНИЕ: ЛКМ/F - ЗАЛП, ПКМ/ESC - ОТМЕНА", (240, 160, 255)))
                            else:
                                strike_lvl = savedata["Upgrades"].get("orbital_strike", 1)
                                orbital_strike_cd = 45.0 if strike_lvl <= 1 else (38.0 if strike_lvl == 2 else 30.0)
                                orbital_targeting = False
                                tx, ty = mouse_pos[0], mouse_pos[1]
                                strike_rad = 125
                                effects.append(OrbitalBeamEffect(tx, ty, radius=strike_rad))
                                shake_amount = 20.0
                                sfx_boss_defeat.play()

                                wave_scale = 1.0 + min(2.5, max(0, wave - 1) * 0.04)
                                if active_meteorite and math.hypot(active_meteorite.x - tx, active_meteorite.y - ty) <= (strike_rad + active_meteorite.radius):
                                    m_dmg = int((380 + strike_lvl * 180) * wave_scale)
                                    active_meteorite.take_damage(m_dmg, effects)

                                b_dmg = int((280 + strike_lvl * 140) * wave_scale)
                                void_amp = savedata.get("Upgrades", {}).get("void_amplifier", 0)
                                hits = 0
                                for ne in enemies:
                                    if math.hypot(ne.x - tx, ne.y - ty) <= strike_rad:
                                        actual_dmg = b_dmg
                                        # Сопротивление боссов к прямому орбитальному лучу снижено до -25%
                                        if ne.type >= 1000:
                                            actual_dmg = int(actual_dmg * 0.75)
                                        if void_amp > 0 and (ne.type in (10, 3000, 4000) or ne.type >= 1000):
                                            actual_dmg = int(actual_dmg * (1.0 + 0.30 * void_amp))
                                        # Лимит по урону в 75% от HP слайма
                                        max_limit = max(1, int(getattr(ne, "max_health", ne.health) * 0.75))
                                        actual_dmg = min(actual_dmg, max_limit)
                                        ne.health -= actual_dmg
                                        hits += 1
                                        effects.append(FloatingText(ne.x, ne.y - 12, f"-{actual_dmg}", (220, 100, 255)))
                                        effects.append(RingEffect(ne.x, ne.y, 40, (180, 50, 255)))
                                effects.append(FloatingText(tx, ty - 50, f"ОРБИТАЛЬНЫЙ ЗАЛП! ({hits})", (240, 160, 255)))

                                # Талант «Горизонт Событий»: сингулярность стягивает врагов и замедляет на 60%
                                eh_lvl = savedata.get("Upgrades", {}).get("event_horizon", 0)
                                if eh_lvl > 0:
                                    effects.append(RingEffect(tx, ty, strike_rad + 35, (170, 45, 240)))
                                    for ne in enemies:
                                        if ne.type < 1000:
                                            dist = math.hypot(ne.x - tx, ne.y - ty)
                                            if dist <= (strike_rad + 55) and dist > 4:
                                                ne.x += (tx - ne.x) * 0.55
                                                ne.y += (ty - ne.y) * 0.55
                                                ne.freeze_timer = max(ne.freeze_timer, 2.0 + eh_lvl)
                                                ne.speed_multiplier = min(ne.speed_multiplier, 0.40)
                    elif event.key == pygame.K_s and inspected_tower and not is_paused:
                        sell_val = max(20, int(inspected_tower.total_invested * 0.70))
                        cacti += sell_val
                        for s_idx, slot in enumerate(tower_slots):
                            if math.hypot(inspected_tower.x - slot[0], inspected_tower.y - slot[1]) < 10:
                                occupied_slots[s_idx] = False
                                break
                        effects.append(SplashEffect(inspected_tower.x, inspected_tower.y, 45, GOLD))
                        towers.remove(inspected_tower)
                        sfx_sell.play()
                        inspected_tower = None
                        last_card_rect = last_btn_rect = last_target_rect = last_sell_rect = last_max_rect = None
                    elif event.key == pygame.K_u:
                        if inspected_tower and inspected_tower.level < inspected_tower.max_level and not is_paused:
                            is_shift = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)
                            has_bulk = (savedata.get("Upgrades", {}).get("bulk_upgrade", 0) > 0)
                            if is_shift and has_bulk:
                                cacti, lvls = perform_bulk_upgrade(inspected_tower, cacti, effects, savedata)
                                if lvls > 0:
                                    sfx_upgrade.play()
                                else:
                                    laser.play()
                            elif cacti >= inspected_tower.upgrade_cost:
                                success, cost = inspected_tower.upgrade(cacti)
                                if success:
                                    cacti -= cost
                                    savedata.setdefault("Stats", {})["max_tower_level_reached"] = max(
                                        savedata.get("Stats", {}).get("max_tower_level_reached", 0),
                                        inspected_tower.level
                                    )
                                    effects.append(RingEffect(inspected_tower.x, inspected_tower.y, 52, GOLD))
                                    for _ in range(14):
                                        effects.append(DropSpark(inspected_tower.x, inspected_tower.y, burst=True))
                                    sfx_upgrade.play()
                                else:
                                    laser.play()
                            else:
                                laser.play()
                        else:
                            upgrade_mode = not upgrade_mode
                            selected_tower_type = None
                    elif event.key == pygame.K_r:
                        if game_over:
                            shake_amount = 0.0
                            win_mgr.reset_position()
                            start_battle_session()
                            sfx_click.play()
                    elif event.key == pygame.K_b:
                        if not game_over:
                            if not is_paused:
                                is_paused = True
                                pause_frozen_frame = screen.copy()
                            bestiary_return_state = STATE_PLAYING
                            current_state = STATE_BESTIARY
                            bestiary_scroll_y = 0
                            sfx_click.play()
                    elif event.key == pygame.K_p:
                        if not game_over:
                            is_paused = not is_paused
                            if not is_paused:
                                pause_frozen_frame = None
                            sfx_click.play()
                    elif event.key in [pygame.K_ESCAPE, getattr(pygame, 'K_AC_BACK', -999)]:
                        if rally_targeting_tent:
                            rally_targeting_tent._rally_selecting = False
                            rally_targeting_tent = None
                            sfx_click.play()
                        elif orbital_targeting:
                            orbital_targeting = False
                            sfx_click.play()
                        elif is_paused:
                            is_paused = False
                            pause_frozen_frame = None
                            sfx_click.play()
                        elif game_over:
                            shake_amount = 0.0
                            win_mgr.reset_position()
                            save_data(savedata)
                            current_state = STATE_MAP_SELECT
                            sfx_click.play()
                        elif selected_tower_type:
                            selected_tower_type = None
                        elif inspected_tower:
                            if rally_targeting_tent:
                                rally_targeting_tent._rally_selecting = False
                                rally_targeting_tent = None
                            inspected_tower = None
                        elif upgrade_mode:
                            upgrade_mode = False
                        else:
                            is_paused = True
                            sfx_click.play()
                    elif event.key == pygame.K_SPACE:
                        if not wave_in_progress and not is_paused and not game_over:
                            between_waves_timer = 0.0
                        else:
                            mods = pygame.key.get_mods()
                            if mods & pygame.KMOD_SHIFT:
                                current_speed_index = (current_speed_index - 1) % len(speed_levels)
                            else:
                                current_speed_index = (current_speed_index + 1) % len(speed_levels)
                            game_speed = speed_levels[current_speed_index]
                            sfx_click.play()
                    elif event.key == pygame.K_r:
                        if inspected_tower and inspected_tower.type == "tent" and not is_paused and not game_over:
                            if rally_targeting_tent == inspected_tower:
                                rally_targeting_tent._rally_selecting = False
                                rally_targeting_tent = None
                            else:
                                rally_targeting_tent = inspected_tower
                                inspected_tower._rally_selecting = True
                            sfx_click.play()
                        elif game_over or is_paused:
                            start_battle_session()
                            sfx_click.play()
                        else:
                            save_data(savedata)
                            current_state = STATE_MAP_SELECT

                if event.type == pygame.MOUSEBUTTONDOWN:
                    ctrl_dock_x = 1052
                    speed_btn_rect = pygame.Rect(ctrl_dock_x, SCREEN_HEIGHT - 66, 216, 52)

                    # ПКМ: Отмена прицеливания орбиталки / точки сбора, уменьшение скорости и сброс выбора
                    if event.button == 3:
                        if rally_targeting_tent:
                            rally_targeting_tent._rally_selecting = False
                            rally_targeting_tent = None
                            sfx_click.play()
                            continue
                        if orbital_targeting:
                            orbital_targeting = False
                            sfx_click.play()
                            continue
                        if speed_btn_rect.collidepoint(mouse_pos):
                            current_speed_index = (current_speed_index - 1) % len(speed_levels)
                            game_speed = speed_levels[current_speed_index]
                            sfx_click.play()
                            continue
                        if selected_tower_type:
                            selected_tower_type = None
                            sfx_click.play()
                            continue
                        if inspected_tower:
                            inspected_tower = None
                            last_card_rect = last_btn_rect = last_target_rect = last_sell_rect = last_max_rect = None
                            continue

                    elif event.button == 1:
                        # Клик по активному метеориту (фокус башен на нём)
                        if active_meteorite and not is_paused and not game_over:
                            if math.hypot(mouse_pos[0] - active_meteorite.x, mouse_pos[1] - active_meteorite.y) <= active_meteorite.radius + 15:
                                active_meteorite.targeted = not active_meteorite.targeted
                                sfx_click.play()
                                f_msg = "ЦЕЛЬ БАШЕН: МЕТЕОРИТ (+25% РАДИУС)" if active_meteorite.targeted else "ЦЕЛЬ БАШЕН: СЛАЙМЫ"
                                f_col = (230, 120, 255) if active_meteorite.targeted else (180, 240, 180)
                                effects.append(FloatingText(active_meteorite.x, active_meteorite.y - 28, f_msg, f_col))
                                continue

                        # Клик по кургану раскопок (Морской Бой)
                        if active_dig_site and active_dig_site.collidepoint(mouse_pos) and not is_paused and not game_over:
                            if dig_window is None and dig_session is None:
                                dig_session = DigMinigameSession(game_map, savedata)
                                dig_window_close_timer = 0.0
                                effects.append(FloatingText(active_dig_site.x, active_dig_site.y - 25, "РАСКОПКИ НАЧАТЫ!", (255, 235, 140)))
                                effects.append(RingEffect(active_dig_site.x, active_dig_site.y, 60, (255, 215, 80)))
                                sfx_click.play()
                                active_dig_site = None

                                # На ПК пробуем создать отдельное окно ОС (всегда поверх игры); на Android используем встроенное фейковое окно
                                if not IS_ANDROID:
                                    try:
                                        disp_sizes = pygame.display.get_desktop_sizes() if hasattr(pygame.display, "get_desktop_sizes") else []
                                        disp_w = disp_sizes[0][0] if disp_sizes else 1920
                                        disp_h = disp_sizes[0][1] if disp_sizes else 1080

                                        cur_win = win_mgr.win if win_mgr and win_mgr.win else None
                                        if cur_win:
                                            try:
                                                cur_pos = cur_win.position
                                                cur_sz = cur_win.size
                                            except Exception:
                                                cur_pos = (100, 100)
                                                cur_sz = (SCREEN_WIDTH, SCREEN_HEIGHT)
                                        else:
                                            cur_pos = (100, 100)
                                            cur_sz = (SCREEN_WIDTH, SCREEN_HEIGHT)

                                        # Вычисляем умную позицию: если справа от окна есть место — пристыковываем справа,
                                        # иначе если игра развёрнута на весь экран или места мало — размещаем поверх в правом верхнем углу игрового поля
                                        if cur_pos[0] + cur_sz[0] + 375 <= disp_w:
                                            dw_x = cur_pos[0] + cur_sz[0] + 10
                                            dw_y = cur_pos[1] + 40
                                        elif cur_pos[0] >= 375:
                                            dw_x = cur_pos[0] - 375
                                            dw_y = cur_pos[1] + 40
                                        else:
                                            dw_x = max(20, cur_pos[0] + cur_sz[0] - 380)
                                            dw_y = max(40, cur_pos[1] + 60)

                                        dw_x = max(10, min(disp_w - 370, dw_x))
                                        dw_y = max(30, min(disp_h - 480, dw_y))

                                        dig_window = pygame.Window("Археологические Раскопки 5х5", (360, 460), position=(dw_x, dw_y), always_on_top=True)
                                        dig_window.always_on_top = True

                                        if sys.platform == "win32":
                                            try:
                                                import ctypes
                                                hwnd = dig_window.handle
                                                ctypes.windll.user32.SetWindowPos(
                                                    ctypes.c_void_p(hwnd),
                                                    ctypes.c_void_p(-1),  # HWND_TOPMOST
                                                    0, 0, 0, 0,
                                                    0x0001 | 0x0002 | 0x0040  # SWP_NOSIZE | SWP_NOMOVE | SWP_SHOWWINDOW
                                                )
                                            except Exception:
                                                pass
                                        dig_window.focus()
                                    except Exception as err:
                                        print(f"[DIG] Native window creation failed: {err}")
                                        dig_window = None
                                else:
                                    dig_window = None
                            continue

                        # Клик в меню паузы
                        if is_paused and not game_over:
                            for b_id, brect in pause_click_rects.items():
                                if brect.collidepoint(mouse_pos):
                                    if b_id == "resume":
                                        is_paused = False
                                        pause_frozen_frame = None
                                        sfx_click.play()
                                    elif b_id == "restart":
                                        shake_amount = 0.0
                                        win_mgr.reset_position()
                                        start_battle_session()
                                        sfx_click.play()
                                    elif b_id == "bestiary":
                                        bestiary_return_state = STATE_PLAYING
                                        current_state = STATE_BESTIARY
                                        bestiary_scroll_y = 0
                                        sfx_click.play()
                                    elif b_id == "menu":
                                        shake_amount = 0.0
                                        win_mgr.reset_position()
                                        save_data(savedata)
                                        current_state = STATE_MAP_SELECT
                                        pause_frozen_frame = None
                                        sfx_click.play()
                            continue

                        # Клик на экране конца игры
                        if game_over:
                            if r_btn and r_btn.collidepoint(mouse_pos):
                                shake_amount = 0.0
                                win_mgr.reset_position()
                                start_battle_session()
                                sfx_click.play()
                            elif q_btn and q_btn.collidepoint(mouse_pos):
                                shake_amount = 0.0
                                win_mgr.reset_position()
                                save_data(savedata)
                                current_state = STATE_MAP_SELECT
                                sfx_click.play()
                            continue

                        # Компактные координаты нижнего правого блока управления
                        col2_x = 1164
                        turbo_btn_rect = pygame.Rect(ctrl_dock_x, SCREEN_HEIGHT - 116, 104, 44)
                        spawn_rush_btn_rect = pygame.Rect(col2_x, SCREEN_HEIGHT - 116, 104, 44)
                        range_btn_rect = pygame.Rect(ctrl_dock_x, SCREEN_HEIGHT - 166, 104, 44)
                        orbital_btn_rect = pygame.Rect(col2_x, SCREEN_HEIGHT - 166, 104, 44)

                        # Клик по кнопке скорости (ЛКМ - ускорение вперед)
                        if speed_btn_rect.collidepoint(mouse_pos):
                            current_speed_index = (current_speed_index + 1) % len(speed_levels)
                            game_speed = speed_levels[current_speed_index]
                            sfx_click.play()
                            continue

                    # Клик по кнопке Турбо-Волн
                    if savedata.get("Upgrades", {}).get("wave_rush", 0) > 0 and turbo_btn_rect.collidepoint(mouse_pos) and not is_paused and not game_over:
                        curr = savedata.get("Toggles", {}).get("wave_rush", True)
                        if "Toggles" not in savedata:
                            savedata["Toggles"] = {}
                        savedata["Toggles"]["wave_rush"] = not curr
                        save_data(savedata)
                        sfx_click.play()
                        status_str = "ВКЛЮЧЕНЫ" if not curr else "ОТКЛЮЧЕНЫ"
                        status_col = GREEN if not curr else (255, 100, 100)
                        effects.append(FloatingText(SCREEN_WIDTH // 2, 160, f"ТУРБО-ВОЛНЫ: {status_str}", status_col))
                        if not curr and not wave_in_progress:
                            between_waves_timer = 0.0
                        continue

                    # Клик по кнопке Плотного Спавна
                    if savedata.get("Upgrades", {}).get("spawn_rush", 0) > 0 and spawn_rush_btn_rect.collidepoint(mouse_pos) and not is_paused and not game_over:
                        curr = savedata.get("Toggles", {}).get("spawn_rush", True)
                        if "Toggles" not in savedata:
                            savedata["Toggles"] = {}
                        savedata["Toggles"]["spawn_rush"] = not curr
                        save_data(savedata)
                        sfx_click.play()
                        status_str = "ВКЛЮЧЕН" if not curr else "ОТКЛЮЧЕН"
                        status_col = GREEN if not curr else (255, 100, 100)
                        effects.append(FloatingText(SCREEN_WIDTH // 2, 190, f"ПЛОТНЫЙ СПАВН: {status_str}", status_col))
                        continue

                    # Клик по кнопке Тактической Сетки
                    if savedata.get("Upgrades", {}).get("range_grid", 0) > 0 and range_btn_rect.collidepoint(mouse_pos) and not is_paused and not game_over:
                        curr = savedata.get("Toggles", {}).get("range_grid", False)
                        if "Toggles" not in savedata:
                            savedata["Toggles"] = {}
                        savedata["Toggles"]["range_grid"] = not curr
                        save_data(savedata)
                        sfx_click.play()
                        stat_str = "ВКЛЮЧЕНА" if not curr else "ОТКЛЮЧЕНА"
                        stat_col = (100, 220, 255) if not curr else (255, 120, 120)
                        effects.append(FloatingText(SCREEN_WIDTH // 2, 160, f"СЕТКА РАДИУСОВ: {stat_str}", stat_col))
                        continue

                    # Клик по кнопке Орбитального удара
                    if savedata.get("Upgrades", {}).get("orbital_strike", 0) > 0 and orbital_btn_rect.collidepoint(mouse_pos) and not is_paused and not game_over:
                        if orbital_strike_cd <= 0:
                            orbital_targeting = not orbital_targeting
                            selected_tower_type = None
                            inspected_tower = None
                            sfx_click.play()
                            if orbital_targeting:
                                effects.append(FloatingText(SCREEN_WIDTH // 2, 140, "ПРИЦЕЛИВАНИЕ: ЛКМ/F - ЗАЛП, ПКМ/ESC - ОТМЕНА", (240, 160, 255)))
                        continue

                    # Нанесение удара при активном прицеливании
                    if orbital_targeting and not is_paused and not game_over:
                        if mouse_pos[1] < SCREEN_HEIGHT - 72:
                            strike_lvl = savedata["Upgrades"].get("orbital_strike", 1)
                            orbital_strike_cd = 45.0 if strike_lvl <= 1 else (38.0 if strike_lvl == 2 else 30.0)
                            orbital_targeting = False
                            tx, ty = mouse_pos[0], mouse_pos[1]
                            strike_rad = 125
                            effects.append(OrbitalBeamEffect(tx, ty, radius=strike_rad))
                            shake_amount = 20.0
                            sfx_boss_defeat.play()

                            wave_scale = 1.0 + min(2.5, max(0, wave - 1) * 0.04)
                            if active_meteorite and math.hypot(active_meteorite.x - tx, active_meteorite.y - ty) <= (strike_rad + active_meteorite.radius):
                                m_dmg = int((380 + strike_lvl * 180) * wave_scale)
                                active_meteorite.take_damage(m_dmg, effects)

                            b_dmg = int((280 + strike_lvl * 140) * wave_scale)
                            void_amp = savedata.get("Upgrades", {}).get("void_amplifier", 0)
                            hits = 0
                            for ne in enemies:
                                if math.hypot(ne.x - tx, ne.y - ty) <= strike_rad:
                                    actual_dmg = b_dmg
                                    # Сопротивление боссов к прямому орбитальному лучу снижено до -25%
                                    if ne.type >= 1000:
                                        actual_dmg = int(actual_dmg * 0.75)
                                    if void_amp > 0 and (ne.type in (10, 3000, 4000) or ne.type >= 1000):
                                        actual_dmg = int(actual_dmg * (1.0 + 0.30 * void_amp))
                                    # Лимит по урону в 75% от HP слайма
                                    max_limit = max(1, int(getattr(ne, "max_health", ne.health) * 0.75))
                                    actual_dmg = min(actual_dmg, max_limit)
                                    ne.health -= actual_dmg
                                    hits += 1
                                    effects.append(FloatingText(ne.x, ne.y - 12, f"-{actual_dmg}", (220, 100, 255)))
                                    effects.append(RingEffect(ne.x, ne.y, 40, (180, 50, 255)))
                            effects.append(FloatingText(tx, ty - 50, f"ОРБИТАЛЬНЫЙ ЗАЛП! ({hits})", (240, 160, 255)))

                            # Талант «Горизонт Событий»: сингулярность стягивает врагов и замедляет на 60%
                            eh_lvl = savedata.get("Upgrades", {}).get("event_horizon", 0)
                            if eh_lvl > 0:
                                effects.append(RingEffect(tx, ty, strike_rad + 35, (170, 45, 240)))
                                for ne in enemies:
                                    if ne.type < 1000:
                                        dist = math.hypot(ne.x - tx, ne.y - ty)
                                        if dist <= (strike_rad + 55) and dist > 4:
                                            ne.x += (tx - ne.x) * 0.55
                                            ne.y += (ty - ne.y) * 0.55
                                            ne.freeze_timer = max(ne.freeze_timer, 2.0 + eh_lvl)
                                            ne.speed_multiplier = min(ne.speed_multiplier, 0.40)
                            continue

                    # Установка точки сбора солдат палатки при активном прицеливании
                    if rally_targeting_tent and not is_paused and not game_over:
                        # Если клик внутри карточки осмотра башни
                        if last_card_rect and last_card_rect.collidepoint(mouse_pos):
                            if last_target_rect and last_target_rect.collidepoint(mouse_pos):
                                rally_targeting_tent._rally_selecting = False
                                rally_targeting_tent = None
                                sfx_click.play()
                                continue
                            # Если клик по другим кнопкам карточки — сбрасываем режим выбора, но даём сработать кнопкам
                            rally_targeting_tent._rally_selecting = False
                            rally_targeting_tent = None
                        elif mouse_pos[1] < SCREEN_HEIGHT - 72:
                            r_dist = math.hypot(mouse_pos[0] - rally_targeting_tent.x, mouse_pos[1] - rally_targeting_tent.y)
                            if r_dist <= rally_targeting_tent.range:
                                rally_targeting_tent.set_rally_point(mouse_pos[0], mouse_pos[1], path=path)
                                effects.append(RingEffect(mouse_pos[0], mouse_pos[1], 32, (80, 255, 130)))
                                for _ in range(10):
                                    effects.append(DropSpark(mouse_pos[0], mouse_pos[1], burst=True))
                                effects.append(FloatingText(mouse_pos[0], mouse_pos[1] - 22, "ТОЧКА СБОРА!", (130, 255, 170)))
                                sfx_click.play()
                                rally_targeting_tent._rally_selecting = False
                                rally_targeting_tent = None
                                continue
                            else:
                                effects.append(FloatingText(mouse_pos[0], mouse_pos[1] - 18, "ВНЕ ЗОНЫ ПАЛАТКИ!", (255, 110, 110)))
                                laser.play()
                                continue

                    # Клик по кнопкам дока башен
                    b1_rect = pygame.Rect(18, SCREEN_HEIGHT - 70, 136, 58)
                    b2_rect = pygame.Rect(166, SCREEN_HEIGHT - 70, 136, 58)
                    b3_rect = pygame.Rect(314, SCREEN_HEIGHT - 70, 136, 58)
                    b4_rect = pygame.Rect(462, SCREEN_HEIGHT - 70, 136, 58)
                    b5_rect = pygame.Rect(610, SCREEN_HEIGHT - 70, 136, 58)
                    b6_rect = pygame.Rect(758, SCREEN_HEIGHT - 70, 136, 58)
                    b_upg_rect = pygame.Rect(906, SCREEN_HEIGHT - 70, 136, 58)

                    if b1_rect.collidepoint(mouse_pos):
                        selected_tower_type = "magic"
                        upgrade_mode = False
                        inspected_tower = None
                        continue
                    elif b2_rect.collidepoint(mouse_pos):
                        selected_tower_type = "rock"
                        upgrade_mode = False
                        inspected_tower = None
                        continue
                    elif b3_rect.collidepoint(mouse_pos) and savedata["Upgrades"].get("freeze_tower", 0) > 0:
                        selected_tower_type = "freeze"
                        upgrade_mode = False
                        inspected_tower = None
                        continue
                    elif b4_rect.collidepoint(mouse_pos) and savedata["Upgrades"].get("tent_tower", 0) > 0:
                        selected_tower_type = "tent"
                        upgrade_mode = False
                        inspected_tower = None
                        continue
                    elif b5_rect.collidepoint(mouse_pos) and savedata["Upgrades"].get("tesla_tower", 0) > 0:
                        selected_tower_type = "tesla"
                        upgrade_mode = False
                        inspected_tower = None
                        continue
                    elif b6_rect.collidepoint(mouse_pos) and savedata["Upgrades"].get("farm_tower", 0) > 0:
                        selected_tower_type = "farm"
                        upgrade_mode = False
                        inspected_tower = None
                        continue
                    elif b_upg_rect.collidepoint(mouse_pos):
                        upgrade_mode = not upgrade_mode
                        selected_tower_type = None
                        continue

                    # Клик по плашке ожидания волны — мгновенный старт волны
                    if not wave_in_progress and not game_over:
                        prep_rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT - 130, 480, 52)
                        if prep_rect.collidepoint(mouse_pos):
                            between_waves_timer = 0.0
                            sfx_click.play()
                            continue

                    # Клик по кнопкам в карточке башни
                    if inspected_tower:
                        if last_target_rect and last_target_rect.collidepoint(mouse_pos):
                            if inspected_tower.type == "tent":
                                if rally_targeting_tent == inspected_tower:
                                    rally_targeting_tent._rally_selecting = False
                                    rally_targeting_tent = None
                                else:
                                    rally_targeting_tent = inspected_tower
                                    inspected_tower._rally_selecting = True
                                sfx_click.play()
                                continue
                            elif inspected_tower.type != "farm":
                                if savedata.get("Upgrades", {}).get("smart_targeting", 0) >= 1:
                                    modes = ["FIRST", "STRONGEST", "WEAKEST", "LAST", "CLOSEST"]
                                else:
                                    modes = ["FIRST", "STRONGEST", "LAST", "CLOSEST"]
                                cur_idx = modes.index(inspected_tower.target_priority) if inspected_tower.target_priority in modes else 0
                                inspected_tower.target_priority = modes[(cur_idx + 1) % len(modes)]
                                sfx_click.play()
                                continue

                        if last_sell_rect and last_sell_rect.collidepoint(mouse_pos):
                            if rally_targeting_tent:
                                rally_targeting_tent._rally_selecting = False
                                rally_targeting_tent = None
                            sell_val = max(20, int(inspected_tower.total_invested * 0.70))
                            cacti += sell_val
                            for s_idx, slot in enumerate(tower_slots):
                                if math.hypot(inspected_tower.x - slot[0], inspected_tower.y - slot[1]) < 10:
                                    occupied_slots[s_idx] = False
                                    break
                            effects.append(SplashEffect(inspected_tower.x, inspected_tower.y, 45, GOLD))
                            towers.remove(inspected_tower)
                            sfx_sell.play()
                            inspected_tower = None
                            last_card_rect = last_btn_rect = last_target_rect = last_sell_rect = last_max_rect = None
                            continue

                        # Клик по кнопке [МАКС] (Быстрая прокачка)
                        if last_max_rect and last_max_rect.collidepoint(mouse_pos):
                            cacti, levels = perform_bulk_upgrade(inspected_tower, cacti, effects, savedata)
                            if levels > 0:
                                sfx_upgrade.play()
                            else:
                                laser.play()
                            continue

                        clicked_btn = (last_btn_rect and last_btn_rect.collidepoint(mouse_pos))
                        clicked_tower = (math.hypot(mouse_pos[0] - inspected_tower.x, mouse_pos[1] - inspected_tower.y) < 32)
                        if clicked_btn or (clicked_tower and (upgrade_mode or selected_tower_type is None)):
                            is_shift = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)
                            has_bulk = (savedata.get("Upgrades", {}).get("bulk_upgrade", 0) > 0)
                            if is_shift and has_bulk:
                                cacti, levels = perform_bulk_upgrade(inspected_tower, cacti, effects, savedata)
                                if levels > 0:
                                    sfx_upgrade.play()
                                else:
                                    laser.play()
                            else:
                                success, cost = inspected_tower.upgrade(cacti)
                                if success:
                                    cacti -= cost
                                    savedata.setdefault("Stats", {})["max_tower_level_reached"] = max(
                                        savedata.get("Stats", {}).get("max_tower_level_reached", 0),
                                        inspected_tower.level
                                    )
                                    effects.append(RingEffect(inspected_tower.x, inspected_tower.y, 52, GOLD))
                                    for _ in range(14):
                                        effects.append(DropSpark(inspected_tower.x, inspected_tower.y, burst=True))
                                    sfx_upgrade.play()
                                else:
                                    laser.play()
                            continue

                    if selected_tower_type:
                        closest_slot = None
                        min_dist = float('inf')
                        slot_index = -1

                        for i, slot in enumerate(tower_slots):
                            if occupied_slots[i]: continue
                            dist = math.hypot(mouse_pos[0] - slot[0], mouse_pos[1] - slot[1])
                            if dist < min_dist and dist < 38:
                                min_dist = dist
                                closest_slot = slot
                                slot_index = i

                        cost = get_tower_build_cost(selected_tower_type, towers, savedata=savedata, game_map=game_map, session_towers_bought=session_towers_bought)

                        if closest_slot and cacti >= cost:
                            start_lvl_bonus = savedata["Upgrades"].get("start_tower_level", 0)
                            max_lvl_bonus = savedata["Upgrades"].get("max_tower_level", 0) + savedata["Upgrades"].get("dark_transcendence", 0)
                            dmg_bonus = 1.0 + savedata["Upgrades"].get("global_damage", 0) * 0.04

                            new_tower = Tower(
                                closest_slot[0], closest_slot[1],
                                selected_tower_type,
                                starting_level=start_lvl_bonus,
                                max_level_bonus=max_lvl_bonus,
                                dmg_mult=dmg_bonus,
                                game_map=game_map
                            )
                            new_tower.total_invested = cost
                            towers.append(new_tower)
                            cacti -= cost
                            session_towers_bought += 1
                            occupied_slots[slot_index] = True
                            savedata.setdefault("Stats", {})["total_towers_built"] = savedata.get("Stats", {}).get("total_towers_built", 0) + 1
                            if selected_tower_type == "tesla":
                                savedata.setdefault("Stats", {})["tesla_built"] = savedata.get("Stats", {}).get("tesla_built", 0) + 1
                            if selected_tower_type == "farm":
                                farm_count = sum(1 for tow in towers if tow.type == "farm")
                                savedata.setdefault("Stats", {})["max_farms_built"] = max(
                                    savedata.get("Stats", {}).get("max_farms_built", 0),
                                    farm_count
                                )
                            if selected_tower_type == "tent":
                                savedata.setdefault("Stats", {})["max_tent_level"] = max(
                                    savedata.get("Stats", {}).get("max_tent_level", 0),
                                    new_tower.level
                                )
                            selected_tower_type = None

                    # Клик по башне на карте для её осмотра/выбора (особенно важно для сенсорных экранов)
                    if not selected_tower_type and not orbital_targeting and not rally_targeting_tent and not is_paused and not game_over:
                        clicked_map_tower = None
                        for tower in towers:
                            if math.hypot(mouse_pos[0] - tower.x, mouse_pos[1] - tower.y) < 32:
                                clicked_map_tower = tower
                                break
                        if clicked_map_tower:
                            if rally_targeting_tent and rally_targeting_tent != clicked_map_tower:
                                rally_targeting_tent._rally_selecting = False
                                rally_targeting_tent = None
                            inspected_tower = clicked_map_tower
                            sfx_click.play()
                        else:
                            # Базовая способность: клик по слайму наносит 1 чистый урон
                            clicked_enemy = None
                            if mouse_pos[1] < SCREEN_HEIGHT - 72:
                                for en in enemies:
                                    hit_r = 32 if getattr(en, "is_boss", False) else 22
                                    if math.hypot(mouse_pos[0] - en.x, mouse_pos[1] - en.y) <= hit_r:
                                        clicked_enemy = en
                                        break
                            if clicked_enemy:
                                clicked_enemy.take_damage(1.0, damage_type="pure")
                                effects.append(FloatingText(clicked_enemy.x, clicked_enemy.y - 14, "-1", (255, 230, 100)))
                                effects.append(RingEffect(clicked_enemy.x, clicked_enemy.y, 16, (255, 215, 60)))
                                for _ in range(4):
                                    effects.append(DropSpark(clicked_enemy.x, clicked_enemy.y, burst=True))
                                sfx_click.play()
                                st_stats = savedata.setdefault("Stats", {})
                                st_stats["slime_clicks"] = st_stats.get("slime_clicks", 0) + 1
                            elif inspected_tower and not (last_card_rect and last_card_rect.collidepoint(mouse_pos)):
                                # Клик по свободному полю карты снимает выделение башни
                                if mouse_pos[1] < SCREEN_HEIGHT - 72:
                                    if rally_targeting_tent:
                                        rally_targeting_tent._rally_selecting = False
                                        rally_targeting_tent = None
                                    inspected_tower = None
                                    last_card_rect = last_btn_rect = last_target_rect = last_sell_rect = last_max_rect = None

            # Логика боя
            if not game_over:

                if not wave_in_progress:
                    between_waves_timer -= game_dt
                    if between_waves_timer <= 0:
                        wave_in_progress = True
                        lives_at_wave_start = lives

                        # Спавн кургана раскопок (если археология открыта и реликвии карты не замакшены)
                        if active_dig_site is None and savedata.get("Upgrades", {}).get("archaeology_unlock", 0) > 0 and not are_map_relics_maxed(game_map, savedata):
                            chance = 0.02 + savedata.get("Upgrades", {}).get("dig_site_chance", 0) * 0.01
                            if random.random() < chance:
                                cand_pts = []
                                for _ in range(50):
                                    rx = random.randint(120, 780)
                                    ry = random.randint(80, 540)
                                    if any(math.hypot(rx - sx, ry - sy) < 45 for sx, sy in tower_slots):
                                        continue
                                    dist_to_path = min(math.hypot(rx - px, ry - py) for px, py in path) if path else 100
                                    if dist_to_path < 45:
                                        continue
                                    cand_pts.append((rx, ry))
                                    if len(cand_pts) >= 5:
                                        break
                                if cand_pts:
                                    sp_x, sp_y = random.choice(cand_pts)
                                    dur = 30.0 + savedata.get("Upgrades", {}).get("dig_site_duration", 0) * 10.0
                                    active_dig_site = DigSite(sp_x, sp_y, duration=dur, map_id=game_map)
                                    effects.append(FloatingText(sp_x, sp_y - 25, "ЗОНА РАСКОПОК! КЛИКНИТЕ ДЛЯ ПОИСКА!", (255, 225, 120)))
                                    effects.append(RingEffect(sp_x, sp_y, 50, (255, 215, 80)))
                                    sfx_star.play()
                        dark_aegis_charges = savedata.get("Upgrades", {}).get("dark_aegis", 0)
                        current_wave_queue = get_wave_enemies(wave, game_map=game_map, savedata=savedata)
                        enemies_to_spawn = len(current_wave_queue)
                        enemies_spawned = 0
                        spawn_timer = 0.0
                        base_spawn_delay = max(0.25, 1.2 - 0.04 * (wave / 5))
                        spawn_rush_lvl = savedata.get("Upgrades", {}).get("spawn_rush", 0)
                        spawn_rush_active = savedata.get("Toggles", {}).get("spawn_rush", True)
                        if spawn_rush_lvl > 0 and spawn_rush_active:
                            rush_mult = [1.0, 0.75, 0.55, 0.35][min(3, spawn_rush_lvl)]
                            spawn_delay = max(0.08, base_spawn_delay * rush_mult)
                        else:
                            spawn_delay = base_spawn_delay

                else:
                    spawn_timer += game_dt
                    if spawn_timer >= spawn_delay and enemies_spawned < enemies_to_spawn:
                        spawn_timer = 0.0
                        etype = current_wave_queue[enemies_spawned]
                        new_e = Enemy(etype, wave, path, game_map=game_map)
                        enemies.append(new_e)
                        if etype >= 1000 or getattr(new_e, 'is_boss', False):
                            sfx_boss_alarm.play()
                            shake_amount = max(shake_amount, 10.0)
                        enemies_spawned += 1

                    if enemies_spawned >= enemies_to_spawn and len(enemies) == 0:
                        wave_in_progress = False
                        completed_wave = wave
                        wave += 1

                        # Рекорд карты обновляется только при успешном завершении волны
                        if completed_wave > savedata["LevelsRecords"][game_map]:
                            savedata["LevelsRecords"][game_map] = completed_wave
                            save_data(savedata)

                        wave_rush_lvl = savedata.get("Upgrades", {}).get("wave_rush", 0)
                        wave_rush_active = savedata.get("Toggles", {}).get("wave_rush", True)
                        if wave_rush_lvl > 0 and wave_rush_active:
                            delays = [1.0, 0.5, 0.2, 0.0]
                            between_waves_timer = delays[min(len(delays) - 1, wave_rush_lvl)]
                        else:
                            between_waves_timer = 1.0
                        upcoming_wave_preview = get_wave_enemies(wave, game_map=game_map, savedata=savedata)

                        # Триумфальные титры при победе над 100 волной на финальной карте (титры != конец игры, запускаются 1 раз)
                        if completed_wave == 100 and game_map == 8:
                            if not savedata.get("GameCompleted", False):
                                savedata["GameCompleted"] = True
                                savedata["StellarCactuses"] = savedata.get("StellarCactuses", 0) + 100
                                if is_dark_cacti_unlocked(savedata):
                                    savedata["DarkCactuses"] = savedata.get("DarkCactuses", 0) + 4
                                save_data(savedata)
                            if not savedata.get("CreditsSeen", False):
                                savedata["CreditsSeen"] = True
                                save_data(savedata)
                                current_state = STATE_CREDITS
                                credits_source = "game"
                                credits_scroll_y = 0.0
                                play_soundtrack("star_realm.ogg")
                                win_mgr.victory_bounce()
                            sfx_boss_defeat.play()
                            win_mgr.flash()
                            effects.append(FloatingText(SCREEN_WIDTH // 2, 170, "КОРОЛЬ СЛАЙМОВ РАЗМАЗАН! * ПОБЕДА!", GOLD))
                            effects.append(RingEffect(SCREEN_WIDTH // 2, 170, 100, GOLD))

                        session_waves_completed = completed_wave - session_start_wave + 1
                        has_beacon = (savedata.get("Upgrades", {}).get("astral_beacon", 0) > 0)

                        # Спавн Астрального Метеорита (только при astral_beacon: начиная с 20 волны, каждые 10-15 волн от точки старта)
                        if active_meteorite is None and has_beacon and completed_wave >= 20 and completed_wave >= next_meteor_wave:
                            active_meteorite = AstralMeteorite(completed_wave, game_map=game_map)
                            sfx_boss_alarm.play()
                            gw_lvl = savedata.get("Upgrades", {}).get("gravity_well", 0)
                            gw_min = max(6, 10 - gw_lvl * 2)
                            gw_max = max(9, 15 - gw_lvl * 2)
                            next_meteor_wave = completed_wave + random.randint(gw_min, gw_max)
                            effects.append(FloatingText(SCREEN_WIDTH // 2, 160, "АСТРАЛЬНЫЙ МЕТЕОРИТ УПАЛ! НАЖМИТЕ ДЛЯ АТАКИ!", (255, 120, 255)))
                            shake_amount = 14.0

                        # Проверка рубежей мастерства (15, 30, 50, 75 волн)
                        awarded_milestones = check_mastery_rewards(game_map, completed_wave, savedata)
                        for mw, rew, rank in awarded_milestones:
                            effects.append(FloatingText(SCREEN_WIDTH // 2, 190, f"РУБЕЖ {rank.upper()}! ВОЛНА {mw} (+{rew} ЗВЁЗД)", GOLD))
                            effects.append(RingEffect(SCREEN_WIDTH // 2, 190, 80, GOLD))
                            for _ in range(16):
                                effects.append(DropSpark(SCREEN_WIDTH // 2, 190, burst=True))
                            sfx_achievement.play()

                        # Проверка разблокировки новых достижений
                        if check_achievements(savedata):
                            save_data(savedata)
                            effects.append(FloatingText(SCREEN_WIDTH // 2, 150, "ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!", GOLD))
                            sfx_achievement.play()


                        # Талант «Звёздная Алхимия»: +1 Звёздный Кактус каждые 5 / 4 / 3 волн
                        star_alchemy_lvl = savedata["Upgrades"].get("star_alchemy", 0)
                        if star_alchemy_lvl > 0:
                            alchemy_interval = 6 - star_alchemy_lvl  # ур 1: каждые 5 волн, ур 2: 4 волны, ур 3: 3 волны
                            if completed_wave % alchemy_interval == 0:
                                savedata["StellarCactuses"] = savedata.get("StellarCactuses", 0) + 1
                                session_stellar += 1
                                save_data(savedata)
                                effects.append(FloatingText(SCREEN_WIDTH // 2, 260, "+1 ЗВЁЗДНЫЙ КАКТУС", GOLD))
                                effects.append(RingEffect(SCREEN_WIDTH // 2, 260, 50, GOLD))

                        # Талант «Регенерация Оазиса»: +1 HP базы за ур. каждые 5 волн
                        regen_lvl = savedata["Upgrades"].get("regeneration", 0)
                        if regen_lvl > 0 and completed_wave % 5 == 0 and lives < max_lives:
                            healed = min(max_lives - lives, regen_lvl)
                            lives += healed
                            effects.append(FloatingText(SCREEN_WIDTH // 2, 290, f"+{healed} HP БАЗЫ", GREEN))

                        wave_c_mult = get_wave_cacti_multiplier(completed_wave)

                        # Талант «Премия за Волну»: +25 кактусов за уровень за волну
                        wave_bounty_lvl = savedata["Upgrades"].get("wave_clearing_bounty", 0)
                        if wave_bounty_lvl > 0:
                            w_rew = max(1, int(wave_bounty_lvl * 25 * wave_c_mult))
                            cacti += w_rew
                            session_cacti += w_rew
                            effects.append(FloatingText(SCREEN_WIDTH // 2, 320, f"+{w_rew} ПРЕМИЯ ЗА ВОЛНУ", (255, 220, 100)))

                        # Талант «Кактусовый Вклад»: +3% дивидендов от текущей казны
                        interest_lvl = savedata["Upgrades"].get("compound_interest", 0)
                        if interest_lvl > 0 and cacti > 0:
                            interest = min(interest_lvl * 30, max(1, int(cacti * interest_lvl * 0.03 * wave_c_mult)))
                            cacti += interest
                            session_cacti += interest
                            effects.append(FloatingText(SCREEN_WIDTH // 2, 350, f"+{interest} ВКЛАД ({interest_lvl * 3}%)", (160, 240, 140)))

                        # Доход от всех построенных Кактусовых Ферм
                        total_farm_income = 0
                        for t in towers:
                            if t.type == "farm":
                                inc = max(1, int(t.get_stats_at_level(t.level).get("income", 35) * wave_c_mult))
                                total_farm_income += inc
                                effects.append(FloatingText(t.x, t.y - 26, f"+{inc}", GOLD))
                                effects.append(RingEffect(t.x, t.y, 42, GOLD))
                                for _ in range(8):
                                    effects.append(DropSpark(t.x, t.y, burst=True))
                        if total_farm_income > 0:
                            cacti += total_farm_income
                            session_cacti += total_farm_income
                            sfx_star.play()

                if active_meteorite:
                    active_meteorite.update(game_dt, effects)
                    if active_meteorite.hp <= 0:
                        savedata.setdefault("Stats", {})["meteorites_destroyed"] = savedata.get("Stats", {}).get("meteorites_destroyed", 0) + 1
                        dark_alch = savedata.get("Upgrades", {}).get("dark_alchemy", 0)
                        # Сбалансированный шанс 30% (+20% за ранг Тёмной Алхимии) получить 1 Тёмный кактус (только при открытом Тёмном Космосе)
                        if is_dark_cacti_unlocked(savedata) and random.random() < (0.30 + dark_alch * 0.20):
                            effects.append(FloatingText(active_meteorite.x, active_meteorite.y - 28, "+1 ТЁМНЫЙ КАКТУС", (200, 100, 255)))
                            item_drops.append(DarkCactusDrop(active_meteorite.x, active_meteorite.y - 28, count=1))
                        # Сбалансированный шанс 70% (+15% за уровень Экспедиций) получить саженец редкого кактуса
                        botanical_lvl = savedata.get("Upgrades", {}).get("botanical_expeditions", 0)
                        if random.random() < (0.70 + botanical_lvl * 0.15):
                            m_cid, m_cname = grant_cactus_sprout(savedata, count=1)
                            save_data(savedata)
                            effects.append(FloatingText(active_meteorite.x, active_meteorite.y - 52, f"+1 САЖЕНЕЦ: {m_cname}", (125, 255, 175)))
                            item_drops.append(SproutDrop(active_meteorite.x, active_meteorite.y - 20, count=1, cactus_name=m_cname))
                        # Гарантированный сноп Звёздных кактусов с астрального осколка
                        gw_lvl = savedata.get("Upgrades", {}).get("gravity_well", 0)
                        num_m_stars = 2 + (1 if dark_alch > 0 else 0) + gw_lvl
                        # Бонус семян от Квантового Жнеца
                        qh_lvl = savedata.get("Upgrades", {}).get("quantum_harvester", 0)
                        if qh_lvl > 0:
                            qh_seeds = max(1, int(150 * qh_lvl * get_wave_cacti_multiplier(wave)))
                            cacti += qh_seeds
                            session_cacti += qh_seeds
                            effects.append(FloatingText(active_meteorite.x, active_meteorite.y - 40, f"+{qh_seeds} (КВАНТОВЫЙ ЖНЕЦ)", (200, 240, 255)))
                        for bi in range(num_m_stars):
                            ox = (bi - (num_m_stars - 1) / 2) * 22
                            item_drops.append(StellarCactusDrop(active_meteorite.x + ox, active_meteorite.y - 10))
                        effects.append(RingEffect(active_meteorite.x, active_meteorite.y, 85, (180, 50, 255)))
                        for _ in range(25):
                            effects.append(DropSpark(active_meteorite.x, active_meteorite.y, burst=True))
                        sfx_boss_defeat.play()
                        active_meteorite = None

                if active_dig_site:
                    active_dig_site.update(game_dt, effects)
                    if not active_dig_site.is_active:
                        active_dig_site = None

                if cactus_drone:
                    cactus_drone.update(game_dt, enemies, projectiles, effects, active_meteorite=active_meteorite)

                if orbital_strike_cd > 0:
                    orbital_strike_cd = max(0.0, orbital_strike_cd - game_dt)

                # Аура орошения от Кактусовых Ферм (зависит строго от таланта «Система Орошения» в Древе)
                irrig_lvl = savedata["Upgrades"].get("farm_irrigation", 0)
                active_farms = [f for f in towers if f.type == "farm"] if irrig_lvl > 0 else []

                for t in towers:
                    f_boost = 0.0
                    if t.type != "farm" and active_farms:
                        f_pct = [0, 0.10, 0.20, 0.35][irrig_lvl]
                        for f in active_farms:
                            f_range = getattr(f, "range", 90 + (irrig_lvl - 1) * 40 + f.level * 3)
                            if math.hypot(t.x - f.x, t.y - f.y) <= f_range:
                                f_boost = max(f_boost, f_pct)
                    farm_inc = t.update(game_dt, enemies, projectiles, path, effects, active_meteorite=active_meteorite, farm_boost=f_boost)
                    if farm_inc:
                        actual_farm_inc = max(1, int(farm_inc * get_wave_cacti_multiplier(wave)))
                        cacti += actual_farm_inc
                        session_cacti += actual_farm_inc

                for p in projectiles[:]:
                    p.update(game_dt, enemies, effects, active_meteorite=active_meteorite)
                    if not p.active: projectiles.remove(p)

                for e in enemies[:]:
                    reached = e.update(game_dt, towers, enemies, effects)
                    if reached:
                        is_boss = (e.type >= 1000)
                        if is_boss:
                            # У босса бесконечный урон и БЕЗ возможности блокировки/отражения!
                            lives = 0
                            shake_amount = 26.0
                            effects.append(RingEffect(e.x, e.y, 260, (255, 30, 30)))
                            effects.append(FloatingText(SCREEN_WIDTH // 2, 220, "БОСС СОКРУШИЛ БАЗУ! МГНОВЕННОЕ ПОРАЖЕНИЕ!", (255, 50, 50)))
                            sfx_boss_defeat.play()
                            enemies.remove(e)
                            game_over = True
                            break
                        else:
                            dmg = getattr(e, "base_damage", 1)
                            thorn_lvl = savedata["Upgrades"].get("thorn_armor", 0)
                            repelled = False
                            if thorn_lvl > 0:
                                # Отражение только для обычных и элитных мобов (не боссов!)
                                # Шанс: 8% / 15% / 22%
                                repel_chance = 0.08 + (thorn_lvl - 1) * 0.07
                                if random.random() < repel_chance:
                                    repelled = True
                                    effects.append(RingEffect(e.x, e.y, 60, GOLD))
                                    effects.append(FloatingText(e.x, e.y - 20, "ШИПЫ ОТРАЗИЛИ МОБА!", GOLD))
                                    sfx_tesla.play()
                            if not repelled and dark_aegis_charges > 0:
                                dark_aegis_charges -= 1
                                repelled = True
                                effects.append(RingEffect(e.x, e.y, 85, (180, 50, 255)))
                                effects.append(FloatingText(e.x, e.y - 25, "ТЁМНЫЙ ЭГИС: УРОН ПОГЛОЩЁН!", (210, 120, 255)))
                                sfx_freeze_shot.play()
                            if not repelled:
                                lives = max(0, lives - dmg)
                                shake_amount = max(shake_amount, 6.0 + dmg * 2.5)
                                heart_lbl = "СЕРДЦЕ" if dmg == 1 else ("СЕРДЦА" if dmg < 5 else "СЕРДЕЦ")
                                effects.append(FloatingText(e.x, e.y - 22, f"-{dmg} {heart_lbl}!", (255, 70, 70)))
                                laser.play()
                                if thorn_lvl > 0:
                                    # Ответный залп шипов: фиксированный урон (150 / 220 / 290)
                                    spike_dmg = 80 + thorn_lvl * 70
                                    effects.append(RingEffect(e.x, e.y, 180, (255, 80, 80)))
                                    effects.append(FloatingText(e.x, e.y - 18, f"ОТВЕТНЫЙ ЗАЛП ШИПОВ! -{spike_dmg}", (255, 120, 120)))
                                    for other in enemies:
                                        if other != e:
                                            other.health -= spike_dmg
                                            effects.append(DropSpark(other.x, other.y, burst=True))
                            enemies.remove(e)
                            if lives <= 0:
                                game_over = True
                    elif e.health <= 0:
                        gh_buffs = get_greenhouse_buffs(savedata)
                        bounty_mult = (1.0 + savedata["Upgrades"].get("cacti_bounty", 0) * 0.10) * (1.0 + gh_buffs.get("bounty_mult", 0.0)) * get_wave_cacti_multiplier(wave)
                        rew = max(1, int(e.reward * bounty_mult))
                        cacti += rew
                        session_kills += 1
                        session_cacti += rew
                        savedata.setdefault("Stats", {})["total_kills"] = savedata.get("Stats", {}).get("total_kills", 0) + 1
                        savedata.setdefault("Stats", {})["max_session_cacti"] = max(
                            savedata.get("Stats", {}).get("max_session_cacti", 0),
                            session_cacti
                        )

                        magnet_lvl = savedata["Upgrades"].get("stellar_magnet", 0)
                        magnet_mult = 1.0 + magnet_lvl * 0.10
                        golden_fortune_lvl = savedata["Upgrades"].get("golden_fortune", 0)
                        map_stellar_mult = MAP_BIOMES_DATA.get(game_map, {}).get("stellar_mult", 1.0)

                        if getattr(e, "is_golden", False):
                            savedata.setdefault("Stats", {})["killed_golden"] = savedata.get("Stats", {}).get("killed_golden", 0) + 1
                            # 1 гарантированный Звёздный Кактус (+ шанс на доп. при Золотой Фортуне и бонусе карты)
                            item_drops.append(StellarCactusDrop(e.x, e.y))
                            extra_gold_chance = 0.0
                            if golden_fortune_lvl >= 2:
                                extra_gold_chance += 0.50
                            if map_stellar_mult > 1.0:
                                extra_gold_chance += (map_stellar_mult - 1.0)
                            extra_stars = int(extra_gold_chance)
                            if random.random() < (extra_gold_chance - extra_stars):
                                extra_stars += 1
                            for _ in range(extra_stars):
                                item_drops.append(StellarCactusDrop(e.x + random.randint(-14, 14), e.y - 14))
                            for _ in range(12):
                                effects.append(DropSpark(e.x, e.y, burst=True))

                        if e.type >= 1000:
                            savedata.setdefault("Stats", {})["bosses_defeated"] = savedata.get("Stats", {}).get("bosses_defeated", 0) + 1
                            dark_gain = 0
                            dark_alch = savedata.get("Upgrades", {}).get("dark_alchemy", 0)
                            if is_dark_cacti_unlocked(savedata):
                                if e.type >= 4000:
                                    dark_gain = 2 + dark_alch
                                elif e.type >= 3000:
                                    dark_gain = 1 + dark_alch
                                elif e.type >= 2000:
                                    dark_gain = dark_alch

                            if e.type >= 4000:
                                savedata.setdefault("Stats", {})["void_lord_defeated"] = savedata.get("Stats", {}).get("void_lord_defeated", 0) + 1
                                num_boss_stars = 5
                            elif e.type >= 3000:
                                savedata.setdefault("Stats", {})["void_defeated"] = savedata.get("Stats", {}).get("void_defeated", 0) + 1
                                num_boss_stars = 3
                            elif e.type >= 2000:
                                savedata.setdefault("Stats", {})["colossus_defeated"] = savedata.get("Stats", {}).get("colossus_defeated", 0) + 1
                                num_boss_stars = 2
                            else:
                                num_boss_stars = 1

                            num_boss_stars = max(1, int(round(num_boss_stars * map_stellar_mult)))

                            if dark_gain > 0:
                                dk_lbl = "ТЁМНЫЙ КАКТУС" if dark_gain == 1 else ("ТЁМНЫХ КАКТУСА" if dark_gain < 5 else "ТЁМНЫХ КАКТУСОВ")
                                effects.append(FloatingText(e.x, e.y - 32, f"+{dark_gain} {dk_lbl}", (210, 110, 255)))
                                effects.append(RingEffect(e.x, e.y, 80, (190, 60, 255)))
                                for di in range(dark_gain):
                                    ox = (di - (dark_gain - 1) / 2) * 20
                                    item_drops.append(DarkCactusDrop(e.x + ox, e.y - 15, count=1))

                            # Талант «Квантовый Жнец»: +25% к казне и фикс. бонус семян за каждого босса
                            qh_lvl = savedata.get("Upgrades", {}).get("quantum_harvester", 0)
                            if qh_lvl > 0:
                                bonus_qh_cacti = max(1, int((int(cacti * 0.25 * qh_lvl) + 200 * qh_lvl) * get_wave_cacti_multiplier(wave)))
                                cacti += bonus_qh_cacti
                                session_cacti += bonus_qh_cacti
                                effects.append(FloatingText(e.x, e.y - 76, f"+{bonus_qh_cacti} (КВАНТОВЫЙ ЖНЕЦ)", (200, 240, 255)))

                            # Награда саженцами оранжереи за победу над боссом (только при открытой Оранжерее)
                            if is_greenhouse_unlocked(savedata):
                                harvest_lvl = savedata.get("Upgrades", {}).get("sprout_harvest", 0)
                                bonus_sprouts = harvest_lvl
                                if e.type >= 4000:
                                    base_sprouts = 4
                                elif e.type >= 3000:
                                    base_sprouts = 3
                                elif e.type >= 2000:
                                    base_sprouts = 2
                                else:
                                    base_sprouts = 2

                                num_sprouts = base_sprouts + bonus_sprouts
                                s_cid, s_name = grant_cactus_sprout(savedata, count=num_sprouts)
                                save_data(savedata)
                                sprout_word = "САЖЕНЕЦ" if num_sprouts == 1 else ("САЖЕНЦА" if num_sprouts < 5 else "САЖЕНЦЕВ")
                                effects.append(FloatingText(e.x, e.y - 56, f"+{num_sprouts} {sprout_word}: {s_name}", (110, 255, 170)))
                                for si in range(min(num_sprouts, 4)):
                                    ox = (si - (min(num_sprouts, 4) - 1) / 2) * 18
                                    item_drops.append(SproutDrop(e.x + ox, e.y - 20, count=1, cactus_name=s_name))

                            shake_amount = 22.0 if e.type >= 4000 else 18.0
                            sfx_boss_defeat.play()
                            for _ in range(30 if e.type >= 4000 else 25):
                                effects.append(DropSpark(e.x, e.y, burst=True))
                            
                            for bi in range(num_boss_stars):
                                ox = (bi - (num_boss_stars - 1) / 2) * 20
                                item_drops.append(StellarCactusDrop(e.x + ox, e.y - 10))

                        # Редкий шанс дропа Тёмного кактуса с Теневого слайма (тип 10): 1.0% (только при открытом Тёмном Космосе)
                        if is_dark_cacti_unlocked(savedata) and e.type == 10 and random.random() < 0.01:
                            effects.append(FloatingText(e.x, e.y - 25, "+1 ТЁМНЫЙ КАКТУС", (215, 120, 255)))
                            effects.append(RingEffect(e.x, e.y, 55, (190, 70, 255)))
                            item_drops.append(DarkCactusDrop(e.x, e.y - 15, count=1))

                        # Шанс дропа саженца с золотого слайма: 15% (только при открытой Оранжерее)
                        if is_greenhouse_unlocked(savedata) and getattr(e, "is_golden", False) and random.random() < 0.15:
                            s_cid, s_name = grant_cactus_sprout(savedata, count=1)
                            save_data(savedata)
                            effects.append(FloatingText(e.x, e.y - 42, f"+1 САЖЕНЕЦ: {s_name}", (125, 255, 175)))
                            item_drops.append(SproutDrop(e.x, e.y - 15, count=1, cactus_name=s_name))

                        # Шанс дропа саженца с элитных и бронированных слаймов: 2.5% (+1% за Экспедиции, только при открытой Оранжерее)
                        botanical_lvl = savedata.get("Upgrades", {}).get("botanical_expeditions", 0)
                        if is_greenhouse_unlocked(savedata) and e.type >= 50 and e.type < 1000 and random.random() < (0.025 + botanical_lvl * 0.010):
                            s_cid, s_name = grant_cactus_sprout(savedata, count=1)
                            save_data(savedata)
                            effects.append(FloatingText(e.x, e.y - 42, f"+1 САЖЕНЕЦ: {s_name}", (125, 255, 175)))
                            item_drops.append(SproutDrop(e.x, e.y - 15, count=1, cactus_name=s_name))

                        # Шанс дропа Звёздного кактуса со слаймов:
                        # До 20 волны полный базовый шанс (3.5% с обычных, 15% с элитных).
                        # После 20 волны плавное линейное снижение, чтобы к 100 волне шанс стал ровно в 3 раза меньше.
                        raw_mob_chance = 0.035 if e.type < 50 else 0.15
                        if wave <= 20:
                            wave_decay = 1.0
                        else:
                            wave_decay = max(1.0 / 3.0, 1.0 - ((wave - 20) / 80.0) * (2.0 / 3.0))

                        mob_star_base = raw_mob_chance * wave_decay

                        map_mob_mult = 1.0 + (map_stellar_mult - 1.0) * 0.5
                        base_star_chance = mob_star_base * magnet_mult * map_mob_mult
                        if not getattr(e, "is_golden", False) and e.type < 1000:
                            guar_stars = int(base_star_chance)
                            rem_star_chance = base_star_chance - guar_stars
                            total_stars = guar_stars + (1 if random.random() < rem_star_chance else 0)
                            for s_idx in range(total_stars):
                                ox = (s_idx - (total_stars - 1) / 2) * 14 if total_stars > 1 else 0
                                item_drops.append(StellarCactusDrop(e.x + ox, e.y))

                        # Осколочная Сверхновая (Shatter Nova)
                        shatter_lvl = savedata["Upgrades"].get("shatter_nova", 0)
                        if shatter_lvl > 0 and random.random() < 0.15 * shatter_lvl:
                            s_dmg = 30 * shatter_lvl
                            effects.append(RingEffect(e.x, e.y, 65, (200, 100, 255)))
                            for ne in enemies:
                                if ne is not e and math.hypot(ne.x - e.x, ne.y - e.y) <= 85:
                                    ne.health -= s_dmg
                                    effects.append(FloatingText(ne.x, ne.y - 10, f"-{s_dmg}", (200, 100, 255)))

                        if get_graphics_preset() != "optimized":
                            splat_col = e.get_splat_color()
                            splat_sz = 26 if e.type >= 1000 else (20 if e.type >= 50 else 15)
                            slime_splats.append(SlimeSplat(e.x, e.y, splat_col, size=splat_sz))
                            num_drops = 10 if e.type >= 1000 else (7 if e.type >= 50 else 5)
                            for _ in range(num_drops):
                                effects.append(JellyDroplet(e.x, e.y, splat_col))

                        enemies.remove(e)

                for drop in item_drops[:]:
                    collected = drop.update(effects, ui_dt)
                    if collected:
                        if drop.drop_type == "stellar":
                            savedata["StellarCactuses"] = savedata.get("StellarCactuses", 0) + drop.count
                            session_stellar += drop.count
                            save_data(savedata)
                            sfx_star.play()
                        elif drop.drop_type == "dark":
                            savedata["DarkCactuses"] = savedata.get("DarkCactuses", 0) + drop.count
                            save_data(savedata)
                            sfx_combo.play()
                        elif drop.drop_type == "sprout":
                            sfx_sprout_pickup.play()
                    if not drop.active: item_drops.remove(drop)

                for eff in effects[:]:
                    eff_dt = ui_dt if isinstance(eff, (FloatingText, DropSpark)) else game_dt
                    if eff.update(eff_dt):
                        effects.remove(eff)

                for splat in slime_splats[:]:
                    if splat.update(ui_dt):
                        slime_splats.remove(splat)
                if len(slime_splats) > 40:
                    slime_splats = slime_splats[-40:]

            if is_paused and not game_over and pause_frozen_frame is not None:
                screen.blit(pause_frozen_frame, (0, 0))
            else:
                # --- Отрисовка поля с Screen Shake ---
                shake_enabled = savedata.get("Settings", {}).get("screen_shake", False)
                if shake_amount > 0.01 and shake_enabled:
                    ox = int(random.uniform(-shake_amount, shake_amount))
                    oy = int(random.uniform(-shake_amount, shake_amount))
                else:
                    ox, oy = 0, 0

                generate_background(field_surf, bg_time, map_id=game_map)

                # Атмосферный фоновый декор биома (кристаллы, камни, кактусы, лавовые трещины)
                map_decor.draw(field_surf, bg_time)

                # Дорога биома (двойная окантовка и цвет грунта)
                biome = MAP_BIOMES_DATA.get(game_map, MAP_BIOMES_DATA[0])
                r_border = biome["road_border"]
                r_col = biome["road_col"]
                for i in range(len(path) - 1):
                    pygame.draw.line(field_surf, r_border, path[i], path[i + 1], 40)
                    pygame.draw.circle(field_surf, r_border, path[i + 1], 20)
                for i in range(len(path) - 1):
                    pygame.draw.line(field_surf, r_col, path[i], path[i + 1], 32)
                    pygame.draw.circle(field_surf, r_col, path[i + 1], 16)

                # Желейные пятна слаймов на земле и дороге (только на нормальной графике)
                for splat in slime_splats:
                    splat.draw(field_surf)

                # Слоты под башни
                for i, slot in enumerate(tower_slots):
                    if not occupied_slots[i]:
                        field_surf.blit(slot_img, (slot[0] - 22, slot[1] - 22))

                # Атмосферные частицы биома (снежинки, пепел, песчинки, споры)
                if get_graphics_preset() != "optimized":
                    ambient_particles.update(game_dt)
                    ambient_particles.draw(field_surf)

                # Подсветка радиусов всех башен (Талант «Тактическая Сетка»)
                if savedata.get("Upgrades", {}).get("range_grid", 0) > 0 and savedata.get("Toggles", {}).get("range_grid", False):
                    t_cols = {
                        "magic": (170, 70, 230),
                        "rock": (255, 130, 30),
                        "freeze": (70, 200, 255),
                        "tesla": (100, 235, 255),
                        "tent": (80, 215, 125),
                        "farm": (245, 215, 45)
                    }
                    for t in towers:
                        if getattr(t, "range", 0) > 0:
                            rad = int(t.range)
                            col = t_cols.get(t.type, (100, 200, 255))
                            pygame.draw.circle(field_surf, col, (int(t.x), int(t.y)), rad, width=1)

                if active_meteorite: active_meteorite.draw(field_surf)
                if active_dig_site: active_dig_site.draw(field_surf)
                for e in sorted(enemies, key=lambda m: m.y): e.draw(field_surf)
                for t in towers: t.draw(field_surf, hovered=(t == hovered_tower), upgrade_mode=upgrade_mode)
                for p in projectiles: p.draw(field_surf)
                if cactus_drone: cactus_drone.draw(field_surf)
                for drop in item_drops: drop.draw(field_surf)
                for eff in effects: eff.draw(field_surf)

                # --- Призрак башни при установке (Placement Preview) ---
                if selected_tower_type:
                    near_slot = None
                    for i, slot in enumerate(tower_slots):
                        if not occupied_slots[i]:
                            if math.hypot(mouse_pos[0] - slot[0], mouse_pos[1] - slot[1]) < 38:
                                near_slot = slot
                                break

                    preview_x, preview_y = near_slot if near_slot else mouse_pos
                    t_ranges = {"magic": 150, "rock": 125, "freeze": 135, "tent": 165, "tesla": 145, "farm": 60}
                    pr_range = t_ranges.get(selected_tower_type, 130)

                    # Радиус установки с полупрозрачным кругом (кэшированный, 0 аллокаций)
                    if selected_tower_type == "farm":
                        col = (255, 195, 45, 40) if near_slot else (220, 40, 40, 40)
                        bcol = (255, 195, 45, 180) if near_slot else (220, 40, 40, 180)
                    else:
                        col = (60, 240, 100, 45) if near_slot else (220, 40, 40, 40)
                        bcol = (40, 180, 70, 180) if near_slot else (220, 40, 40, 180)
                    pr_surf = get_cached_range_surf(pr_range, col, bcol, 2)
                    if pr_surf:
                        field_surf.blit(pr_surf, (int(preview_x - pr_range), int(preview_y - pr_range)))

                    # Полупрозрачная иконка башни
                    t_imgs = {
                        "magic": magic_tower_img,
                        "rock": rock_tower_img,
                        "freeze": freeze_tower_img,
                        "tent": tent_tower_img,
                        "tesla": tesla_tower_img,
                        "farm": farm_tower_img
                    }
                    p_img = t_imgs.get(selected_tower_type, magic_tower_img).copy()
                    p_img.set_alpha(170)
                    field_surf.blit(p_img, (preview_x - p_img.get_width() // 2, preview_y - p_img.get_height() // 2 - 8))

                screen.fill((16, 20, 26))
                screen.blit(field_surf, (ox, oy))

                saved_field_backdrop = None
                if battle_ui_fade_alpha < 255.0:
                    battle_ui_fade_alpha = min(255.0, battle_ui_fade_alpha + game_dt * 300.0)
                    saved_field_backdrop = screen.copy()

                # --- Игровой HUD ---
                # 1. Счётчик кактусов (деньги) - увеличенная статусная плашка (y=6..44)
                cacti_panel = pygame.Rect(16, 6, 185, 38)
                pygame.draw.rect(screen, (245, 252, 246), cacti_panel, border_radius=10)
                pygame.draw.rect(screen, (65, 170, 90), cacti_panel, width=2, border_radius=10)
                c_icon_scaled = pygame.transform.smoothscale(cactus_img, (30, 30))
                screen.blit(c_icon_scaled, (24, cacti_panel.centery - 15))
                cacti_txt = large_font.render(f"{cacti:,}".replace(",", " "), True, (15, 55, 22))
                screen.blit(cacti_txt, (64, cacti_panel.centery - cacti_txt.get_height() // 2))

                # 2. Звёздные кактусы
                st_hud = pygame.Rect(16, SCREEN_HEIGHT - 138, 145, 48)
                pygame.draw.rect(screen, (245, 250, 245), st_hud, border_radius=8)
                pygame.draw.rect(screen, GOLD, st_hud, width=2, border_radius=8)
                screen.blit(stellar_cactus_img_m, (22, st_hud.centery - 18))
                st_num = font.render(f"{savedata['StellarCactuses']}", True, (20, 50, 80))
                screen.blit(st_num, (66, st_hud.centery - st_num.get_height() // 2))

                # 2.1 Тёмные кактусы (показываются ТОЛЬКО если открыт Тёмный Космос)
                if is_dark_cacti_unlocked(savedata):
                    dark_cacti_cnt = savedata.get("DarkCactuses", 0)
                    dark_hud = pygame.Rect(16, SCREEN_HEIGHT - 192, 145, 48)
                    pygame.draw.rect(screen, (24, 18, 32), dark_hud, border_radius=8)
                    pygame.draw.rect(screen, (175, 75, 245), dark_hud, width=2, border_radius=8)
                    screen.blit(dark_cactus_img_m, (22, dark_hud.centery - 18))
                    d_num = font.render(f"{dark_cacti_cnt}", True, (240, 220, 255))
                    screen.blit(d_num, (66, dark_hud.centery - d_num.get_height() // 2))

                # 3. Жизни базы (Увеличенный красный Healthbar, плавное заполнение и волна щита)
                hb_w = 280
                hb_h = 38
                hb_x = SCREEN_WIDTH - 16 - hb_w
                hb_y = 6
                hb_rect = pygame.Rect(hb_x, hb_y, hb_w, hb_h)

                has_shield = (dark_aegis_charges > 0)
                is_crit_hp = (lives <= max(3, int(max_lives * 0.25)))

                # Плавная интерполяция уменьшения и увеличения HP
                target_ratio = max(0.0, min(1.0, lives / float(max(1, max_lives))))
                animated_hp_ratio += (target_ratio - animated_hp_ratio) * min(1.0, game_dt * 6.5)
                if hp_catchup_ratio > animated_hp_ratio:
                    hp_catchup_ratio += (animated_hp_ratio - hp_catchup_ratio) * min(1.0, game_dt * 2.5)
                else:
                    hp_catchup_ratio = animated_hp_ratio

                if has_shield:
                    sh_pulse = (math.sin(bg_time * 0.005) + 1.0) * 0.5
                    border_col = (int(50 + 40 * sh_pulse), int(190 + 55 * sh_pulse), 255)
                    bg_col = (16, 20, 30)
                elif is_crit_hp:
                    border_col = (245, 60, 75) if (pygame.time.get_ticks() // 250) % 2 == 0 else (140, 35, 45)
                    bg_col = (28, 12, 16)
                else:
                    border_col = (65, 80, 100)
                    bg_col = (22, 14, 18)

                pygame.draw.rect(screen, bg_col, hb_rect, border_radius=10)
                pygame.draw.rect(screen, border_col, hb_rect, width=2, border_radius=10)

                # Иконка сердечка слева
                h_icon = pygame.transform.smoothscale(heart_img, (26, 26))
                screen.blit(h_icon, (hb_x + 8, hb_y + 6))

                # Внутренняя дорожка полосы здоровья
                track_x = hb_x + 40
                track_y = hb_y + 6
                track_w = hb_w - 50
                track_h = hb_h - 12
                pygame.draw.rect(screen, (36, 12, 16), (track_x, track_y, track_w, track_h), border_radius=6)

                # 1. Отстающая полоса урона (Ghost bar затухания)
                catch_w = int(track_w * max(0.0, min(1.0, hp_catchup_ratio)))
                if catch_w > 0:
                    pygame.draw.rect(screen, (245, 175, 60), (track_x, track_y, catch_w, track_h), border_radius=6)

                # 2. Основная сочная красная полоса (плавная интерполяция)
                fill_w = int(track_w * max(0.0, min(1.0, animated_hp_ratio)))
                if fill_w > 0:
                    pygame.draw.rect(screen, (225, 40, 50), (track_x, track_y, fill_w, track_h), border_radius=6)
                    pygame.draw.rect(screen, (255, 115, 125), (track_x, track_y, fill_w, track_h // 2), border_radius=5)
                    pygame.draw.rect(screen, (160, 20, 30), (track_x, track_y + track_h - 3, fill_w, 3), border_radius=2)

                    # 3. Голубая анимация переливания щита
                    if has_shield:
                        sheen_surf = pygame.Surface((fill_w, track_h), pygame.SRCALPHA)
                        sheen_surf.fill((40, 180, 255, 45))
                        wave_pos = (bg_time * 0.14) % (fill_w + 80) - 40
                        pts = [(wave_pos, track_h), (wave_pos + 26, 0), (wave_pos + 52, 0), (wave_pos + 26, track_h)]
                        pygame.draw.polygon(sheen_surf, (120, 240, 255, 140), pts)
                        pts_core = [(wave_pos + 10, track_h), (wave_pos + 30, 0), (wave_pos + 40, 0), (wave_pos + 20, track_h)]
                        pygame.draw.polygon(sheen_surf, (255, 255, 255, 220), pts_core)
                        screen.blit(sheen_surf, (track_x, track_y))

                # Чёткий текст HP поверх полосы
                hp_str = f"{lives} / {max_lives} HP"
                t_shad = font.render(hp_str, True, (0, 0, 0))
                t_main = font.render(hp_str, True, (255, 255, 255))
                tx = track_x + 14
                ty = track_y + track_h // 2 - t_main.get_height() // 2
                screen.blit(t_shad, (tx + 1, ty + 1))
                screen.blit(t_main, (tx, ty))

                # Индикатор щита (Тёмный Эгис)
                if has_shield:
                    s_txt = small_font.render(f"ЩИТ x{dark_aegis_charges}", True, (120, 240, 255))
                    s_shad = small_font.render(f"ЩИТ x{dark_aegis_charges}", True, (0, 0, 0))
                    sx = track_x + track_w - s_txt.get_width() - 8
                    sy = track_y + track_h // 2 - s_txt.get_height() // 2
                    screen.blit(s_shad, (sx + 1, sy + 1))
                    screen.blit(s_txt, (sx, sy))

                # 4. Волна и инфо о карте (Единая верхняя строка y=6..44, гармонично с ХП баром и кактусами)
                w_str = f"ВОЛНА: {wave}"
                w_t = font.render(w_str, True, (245, 250, 245))
                biome = MAP_BIOMES_DATA.get(game_map, MAP_BIOMES_DATA[0])
                b_str = f"Биом: {biome['name']}  |  {biome['mutator_badge']}"
                b_t = small_font.render(b_str, True, (215, 235, 255))

                tot_w = w_t.get_width() + b_t.get_width() + 38
                bar_h = 38
                bar_y = 6
                bar_rect = pygame.Rect((SCREEN_WIDTH - tot_w) // 2, bar_y, tot_w, bar_h)

                bar_surf = pygame.Surface((tot_w, bar_h), pygame.SRCALPHA)
                pygame.draw.rect(bar_surf, (18, 26, 36, 220), (0, 0, tot_w, bar_h), border_radius=10)
                pygame.draw.rect(bar_surf, (55, 135, 100, 240), (0, 0, tot_w, bar_h), width=2, border_radius=10)
                screen.blit(bar_surf, (bar_rect.x, bar_rect.y))

                w_pill = pygame.Rect(bar_rect.x + 3, bar_rect.y + 3, w_t.get_width() + 14, bar_h - 6)
                pygame.draw.rect(screen, (32, 82, 52), w_pill, border_radius=7)
                screen.blit(w_t, (w_pill.centerx - w_t.get_width() // 2, w_pill.centery - w_t.get_height() // 2))

                screen.blit(b_t, (w_pill.right + 10, bar_rect.centery - b_t.get_height() // 2))

                # Полоса здоровья Босса (Boss HP Bar) - компактно под верхней плашкой (y=42..64)
                active_bosses = [e for e in enemies if e.type >= 1000 and e.active]
                if active_bosses:
                    boss = active_bosses[0]
                    bb_w, bb_h = 440, 22
                    bb_x = (SCREEN_WIDTH - bb_w) // 2
                    bb_y = 42
                    pygame.draw.rect(screen, (24, 14, 18), (bb_x - 3, bb_y - 2, bb_w + 6, bb_h + 4), border_radius=8)
                    pygame.draw.rect(screen, (240, 60, 60), (bb_x - 3, bb_y - 2, bb_w + 6, bb_h + 4), width=2, border_radius=8)
                    hp_ratio = max(0.0, min(1.0, boss.health / max(1.0, boss.max_health)))
                    fill_w = int(bb_w * hp_ratio)
                    if fill_w > 0:
                        pygame.draw.rect(screen, (225, 45, 55), (bb_x, bb_y, fill_w, bb_h), border_radius=6)
                        pygame.draw.rect(screen, (255, 125, 135), (bb_x, bb_y, fill_w, bb_h // 2), border_radius=4)
                    crown_scaled = pygame.transform.smoothscale(crown_upg_icon, (24, 24))
                    screen.blit(crown_scaled, (bb_x - 28, bb_y - 1))
                    if boss.type >= 4000:
                        boss_title = "КОРОЛЬ СЛАЙМОВ"
                    elif boss.type >= 3000:
                        boss_title = "ТЕНЕВОЙ ИСПОЛИН"
                    elif boss.type >= 2000:
                        boss_title = "СЛИЗНЕБАРОН"
                    else:
                        boss_title = "ЦАРЬ-СЛИЗЕНЬ"
                    b_info_txt = tiny_font.render(f"{boss_title}: {int(boss.health):,} / {int(boss.max_health):,} HP", True, WHITE)
                    screen.blit(b_info_txt, (bb_x + bb_w // 2 - b_info_txt.get_width() // 2, bb_y + bb_h // 2 - b_info_txt.get_height() // 2))

                # ФПС
                fps_val = int(clock.get_fps())
                fps_txt = tiny_font.render(f"FPS: {fps_val}", True, (80, 100, 80))
                screen.blit(fps_txt, (SCREEN_WIDTH - 85, 42))

                # 5. Компактная панель управления (нижний правый угол, не перекрывает дорогу)
                ctrl_dock_x = 1052
                col2_x = 1164
                speed_btn_rect = pygame.Rect(ctrl_dock_x, SCREEN_HEIGHT - 66, 216, 52)
                turbo_btn_rect = pygame.Rect(ctrl_dock_x, SCREEN_HEIGHT - 116, 104, 44)
                spawn_rush_btn_rect = pygame.Rect(col2_x, SCREEN_HEIGHT - 116, 104, 44)
                range_btn_rect = pygame.Rect(ctrl_dock_x, SCREEN_HEIGHT - 166, 104, 44)
                orbital_btn_rect = pygame.Rect(col2_x, SCREEN_HEIGHT - 166, 104, 44)

                # 5.1 Кнопка скорости (ЛКМ - быстрее, ПКМ - медленнее)
                spd_hov = speed_btn_rect.collidepoint(mouse_pos)
                pygame.draw.rect(screen, (50, 55, 60) if not spd_hov else (70, 75, 80), speed_btn_rect, border_radius=10)
                spd_col = CYAN if game_speed < 1 else (YELLOW if game_speed > 1 else WHITE)
                pygame.draw.rect(screen, spd_col, speed_btn_rect, width=2, border_radius=10)
                spd_label = f">> {game_speed}X  [ПРОБЕЛ]" if game_speed >= 1 else ">> 0.2X [ПРОБЕЛ]"
                speed_txt = font.render(spd_label, True, spd_col)
                screen.blit(speed_txt, (speed_btn_rect.centerx - speed_txt.get_width() // 2, speed_btn_rect.centery - speed_txt.get_height() // 2))

                # 5.2 Кнопка Турбо-Волн
                if savedata.get("Upgrades", {}).get("wave_rush", 0) > 0:
                    tb_hov = turbo_btn_rect.collidepoint(mouse_pos)
                    is_turbo = savedata.get("Toggles", {}).get("wave_rush", True)
                    tb_bg = (24, 65, 36) if is_turbo else (60, 32, 36)
                    if tb_hov:
                        tb_bg = (34, 85, 48) if is_turbo else (80, 42, 48)
                    tb_border = (65, 220, 100) if is_turbo else (235, 75, 75)
                    pygame.draw.rect(screen, tb_bg, turbo_btn_rect, border_radius=8)
                    pygame.draw.rect(screen, tb_border, turbo_btn_rect, width=2 if tb_hov else 1, border_radius=8)
                    tb_txt = tiny_font.render(f"ТУРБО [T]: {'ВКЛ' if is_turbo else 'ВЫКЛ'}", True, (210, 255, 220) if is_turbo else (255, 195, 195))
                    screen.blit(tb_txt, (turbo_btn_rect.centerx - tb_txt.get_width() // 2, turbo_btn_rect.centery - tb_txt.get_height() // 2))

                # 5.3 Кнопка Плотного Спавна
                if savedata.get("Upgrades", {}).get("spawn_rush", 0) > 0:
                    sr_hov = spawn_rush_btn_rect.collidepoint(mouse_pos)
                    is_sr = savedata.get("Toggles", {}).get("spawn_rush", True)
                    sr_bg = (65, 45, 15) if is_sr else (45, 40, 35)
                    if sr_hov:
                        sr_bg = (85, 60, 20) if is_sr else (60, 55, 45)
                    sr_border = (255, 170, 40) if is_sr else (140, 130, 120)
                    pygame.draw.rect(screen, sr_bg, spawn_rush_btn_rect, border_radius=8)
                    pygame.draw.rect(screen, sr_border, spawn_rush_btn_rect, width=2 if sr_hov else 1, border_radius=8)
                    sr_txt = tiny_font.render(f"СПАВН [Y]: {'ВКЛ' if is_sr else 'ВЫКЛ'}", True, (255, 220, 150) if is_sr else (190, 185, 175))
                    screen.blit(sr_txt, (spawn_rush_btn_rect.centerx - sr_txt.get_width() // 2, spawn_rush_btn_rect.centery - sr_txt.get_height() // 2))

                # 5.4 Кнопка Тактической Сетки
                if savedata.get("Upgrades", {}).get("range_grid", 0) > 0:
                    rg_hov = range_btn_rect.collidepoint(mouse_pos)
                    is_rg = savedata.get("Toggles", {}).get("range_grid", False)
                    rg_bg = (24, 52, 80) if is_rg else (45, 48, 55)
                    if rg_hov:
                        rg_bg = (35, 72, 110) if is_rg else (60, 65, 75)
                    rg_border = (90, 200, 255) if is_rg else (130, 140, 150)
                    pygame.draw.rect(screen, rg_bg, range_btn_rect, border_radius=8)
                    pygame.draw.rect(screen, rg_border, range_btn_rect, width=2 if rg_hov else 1, border_radius=8)
                    rg_txt = tiny_font.render(f"СЕТКА [X]: {'ВКЛ' if is_rg else 'ВЫКЛ'}", True, (210, 240, 255) if is_rg else (190, 195, 205))
                    screen.blit(rg_txt, (range_btn_rect.centerx - rg_txt.get_width() // 2, range_btn_rect.centery - rg_txt.get_height() // 2))

                # 5.5 Кнопка Орбитального Удара
                if savedata.get("Upgrades", {}).get("orbital_strike", 0) > 0:
                    orb_hov = orbital_btn_rect.collidepoint(mouse_pos)
                    is_ready = (orbital_strike_cd <= 0)
                    if orbital_targeting:
                        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1.0) * 0.5
                        orb_bg = (int(90 + 50 * pulse), 30, int(130 + 70 * pulse))
                        orb_border = (255, 180, 255)
                        pygame.draw.rect(screen, orb_bg, orbital_btn_rect, border_radius=8)
                        pygame.draw.rect(screen, orb_border, orbital_btn_rect, width=2, border_radius=8)
                        orb_txt = tiny_font.render("ПРИЦЕЛ...", True, (255, 240, 255))
                    else:
                        orb_bg = (55, 20, 75) if is_ready else (35, 30, 40)
                        if orb_hov and is_ready:
                            orb_bg = (80, 25, 110)
                        orb_border = (210, 80, 255) if is_ready else (120, 90, 140)
                        pygame.draw.rect(screen, orb_bg, orbital_btn_rect, border_radius=8)
                        pygame.draw.rect(screen, orb_border, orbital_btn_rect, width=2 if (orb_hov and is_ready) else 1, border_radius=8)
                        if is_ready:
                            orb_txt = tiny_font.render("ОРБИТА [F]", True, (245, 210, 255))
                        else:
                            orb_txt = tiny_font.render(f"КД: {int(orbital_strike_cd + 0.9)}с", True, (170, 150, 190))
                    screen.blit(orb_txt, (orbital_btn_rect.centerx - orb_txt.get_width() // 2, orbital_btn_rect.centery - orb_txt.get_height() // 2))

                has_freeze = savedata["Upgrades"].get("freeze_tower", 0) > 0
                has_tent = savedata["Upgrades"].get("tent_tower", 0) > 0
                has_tesla = savedata["Upgrades"].get("tesla_tower", 0) > 0
                has_farm = savedata["Upgrades"].get("farm_tower", 0) > 0

                buttons_data = [
                    ("1", "Маг", get_tower_build_cost("magic", towers, savedata=savedata, game_map=game_map, session_towers_bought=session_towers_bought), magic_tower_img, (18, SCREEN_HEIGHT - 70, 136, 58), "magic", True),
                    ("2", "Огонь", get_tower_build_cost("rock", towers, savedata=savedata, game_map=game_map, session_towers_bought=session_towers_bought), rock_tower_img, (166, SCREEN_HEIGHT - 70, 136, 58), "rock", True),
                    ("3", "Мороз", get_tower_build_cost("freeze", towers, savedata=savedata, game_map=game_map, session_towers_bought=session_towers_bought), freeze_tower_img, (314, SCREEN_HEIGHT - 70, 136, 58), "freeze", has_freeze),
                    ("4", "Палатка", get_tower_build_cost("tent", towers, savedata=savedata, game_map=game_map, session_towers_bought=session_towers_bought), tent_tower_img, (462, SCREEN_HEIGHT - 70, 136, 58), "tent", has_tent),
                    ("5", "Тесла", get_tower_build_cost("tesla", towers, savedata=savedata, game_map=game_map, session_towers_bought=session_towers_bought), tesla_tower_img, (610, SCREEN_HEIGHT - 70, 136, 58), "tesla", has_tesla),
                    ("6", "Ферма", get_tower_build_cost("farm", towers, savedata=savedata, game_map=game_map, session_towers_bought=session_towers_bought), farm_tower_img, (758, SCREEN_HEIGHT - 70, 136, 58), "farm", has_farm),
                    ("U", "Прокачка", None, upgrade_dock_icon, (906, SCREEN_HEIGHT - 70, 136, 58), "upgrade", True),
                ]

                hovered_dock_btn = None
                for b_key, b_name, b_cost, b_icon, b_rect_tuple, b_action, b_unlocked in buttons_data:
                    b_rect = pygame.Rect(*b_rect_tuple)
                    is_active = (selected_tower_type == b_action) or (b_action == "upgrade" and upgrade_mode)
                    b_hov = b_rect.collidepoint(mouse_pos)
                    if b_hov:
                        hovered_dock_btn = (b_key, b_name, b_cost, b_rect, b_action, b_unlocked)

                    if not b_unlocked:
                        pygame.draw.rect(screen, (45, 50, 55), b_rect, border_radius=8)
                        pygame.draw.rect(screen, (80, 85, 90), b_rect, width=1, border_radius=8)
                        # Реальная иконка замка и звездного кактуса
                        screen.blit(lock_icon, (b_rect.left + 8, b_rect.centery - 8))
                        l_txt = tiny_font.render("В ДРЕВЕ", True, (180, 185, 190))
                        screen.blit(l_txt, (b_rect.left + 28, b_rect.centery - l_txt.get_height() // 2))
                        screen.blit(stellar_cactus_img_xs, (b_rect.left + 28 + l_txt.get_width() + 2, b_rect.centery - 9))
                    else:
                        if is_active: bg_col = (45, 180, 80)
                        elif b_hov: bg_col = (65, 75, 80)
                        else: bg_col = (45, 50, 55)

                        pygame.draw.rect(screen, bg_col, b_rect, border_radius=8)
                        pygame.draw.rect(screen, YELLOW if is_active else (WHITE if b_hov else (110, 120, 125)), b_rect, width=2 if is_active else 1, border_radius=8)

                        if b_icon:
                            if b_action not in _dock_icon_cache:
                                _dock_icon_cache[b_action] = pygame.transform.smoothscale(b_icon, (32, 32))
                            screen.blit(_dock_icon_cache[b_action], (b_rect.left + 6, b_rect.centery - 16))

                        if b_action == "upgrade":
                            t_lbl = small_font.render("[U] Прокачка", True, WHITE)
                            sub_lbl = tiny_font.render("РЕЖИМ" if not upgrade_mode else "АКТИВЕН", True, (255, 215, 80) if upgrade_mode else (180, 190, 200))
                            screen.blit(t_lbl, (b_rect.left + 40, b_rect.top + 10))
                            screen.blit(sub_lbl, (b_rect.left + 40, b_rect.top + 32))
                        else:
                            title_str = f"[{b_key}] {b_name}"
                            t_lbl = small_font.render(title_str, True, WHITE)
                            screen.blit(t_lbl, (b_rect.left + 40, b_rect.top + 8))

                            # Цена с кактусом
                            can_buy = (cacti >= b_cost)
                            screen.blit(cactus_img_s, (b_rect.left + 40, b_rect.top + 30))
                            c_lbl = small_font.render(f"{b_cost}", True, WHITE if can_buy else RED)
                            screen.blit(c_lbl, (b_rect.left + 66, b_rect.top + 32))

                # Всплывающая подсказка над кнопкой дока при наведении (если башня на поле не инспектируется)
                if hovered_dock_btn and not inspected_tower:
                    hb_key, hb_name, hb_cost, hb_rect, hb_action, hb_unlocked = hovered_dock_btn
                    tip_w, tip_h = 248, 72
                    tip_x = max(10, min(SCREEN_WIDTH - tip_w - 10, hb_rect.centerx - tip_w // 2))
                    tip_y = hb_rect.top - tip_h - 10

                    tip_surf = pygame.Surface((tip_w, tip_h), pygame.SRCALPHA)
                    pygame.draw.rect(tip_surf, (16, 24, 34, 248), (0, 0, tip_w, tip_h), border_radius=8)

                    if not hb_unlocked:
                        pygame.draw.rect(tip_surf, (180, 60, 60), (0, 0, tip_w, tip_h), width=1, border_radius=8)
                        t1 = small_font.render(f"[{hb_key}] {hb_name} (ЗАКРЫТО)", True, (255, 140, 140))
                        t2 = tiny_font.render("Требуется разблокировать в Древе", True, (220, 220, 220))
                        t3 = tiny_font.render("Талантов Оазиса за Звёздные кактусы.", True, GOLD)
                        tip_surf.blit(t1, (10, 8))
                        tip_surf.blit(t2, (10, 30))
                        tip_surf.blit(t3, (10, 48))
                    elif hb_action == "upgrade":
                        pygame.draw.rect(tip_surf, GOLD if upgrade_mode else (70, 160, 240), (0, 0, tip_w, tip_h), width=1, border_radius=8)
                        t1 = small_font.render("[U] РЕЖИМ ПРОКАЧКИ", True, GOLD)
                        t2 = tiny_font.render("Активирует режим апгрейда башен.", True, WHITE)
                        t3 = tiny_font.render("Кликните на башню на поле для улучшения.", True, (160, 215, 255))
                        tip_surf.blit(t1, (10, 8))
                        tip_surf.blit(t2, (10, 30))
                        tip_surf.blit(t3, (10, 48))
                    else:
                        tip_info = {
                            "magic": ("Магическая Башня", (130, 210, 255), "Урон: 1.0 (Магия)  |  Радиус: 145px", "Пассивно: Пробивает броню и критует"),
                            "rock": ("Огненная Башня", (255, 150, 60), "Урон: 1.8 (Огонь)  |  Сплэш: 50px", "Синергия: +75% комбо-урона по льду"),
                            "freeze": ("Ледяная Башня", (90, 230, 255), "Урон: 0.5 (Лёд)  |  Замедление: 45%", "Аура: Замедляет толпы и тушит огонь"),
                            "tent": ("Палатка Солдат", (130, 235, 130), "Гарнизон: 2 воина (30 HP) | Урон: 2.0", "Тактика: Блокирует мобов на тропе"),
                            "tesla": ("Башня Тесла", (100, 225, 255), "Урон: 2.0 (Электро) | Рикошет: 3 цели", "Эффект: Цепной электрический разряд"),
                            "farm": ("Кактусовая Ферма", (255, 215, 60), "Доход: +35 какт. в конце волны", "Экономика: Чистая пассивная прибыль")
                        }
                        info = tip_info.get(hb_action, ("Башня", WHITE, "", ""))
                        pygame.draw.rect(tip_surf, info[1], (0, 0, tip_w, tip_h), width=1, border_radius=8)
                        t1 = small_font.render(f"[{hb_key}] {info[0]}", True, info[1])
                        t2 = tiny_font.render(info[2], True, (220, 230, 240))
                        t3 = tiny_font.render(info[3], True, GOLD)
                        tip_surf.blit(t1, (10, 8))
                        tip_surf.blit(t2, (10, 30))
                        tip_surf.blit(t3, (10, 48))

                    screen.blit(tip_surf, (tip_x, tip_y))

                # Текст ожидания волны и превью предстоящих мобов
                if not wave_in_progress and not game_over:
                    prep_rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT - 130, 480, 52)
                    p_hov = prep_rect.collidepoint(mouse_pos)
                    pygame.draw.rect(screen, (255, 250, 235) if p_hov else (245, 250, 245), prep_rect, border_radius=8)
                    pygame.draw.rect(screen, (255, 175, 20) if p_hov else GOLD, prep_rect, width=2 if not p_hov else 3, border_radius=8)
                    prep_txt = small_font.render(f"Волна {wave} через {max(0.0, between_waves_timer):.1f} сек. [ПРОБЕЛ / Клик]", True, (160, 85, 0))
                    screen.blit(prep_txt, (prep_rect.centerx - prep_txt.get_width() // 2, prep_rect.top + 6))

                    # Мини-иконки предстоящих типов врагов
                    if not upcoming_wave_preview:
                        upcoming_wave_preview = get_wave_enemies(wave, game_map=game_map, savedata=savedata)
                    types_present = sorted(list(set(upcoming_wave_preview)))
                    mob_sprites = {
                        1: mob1_img, 2: mob2_img, 3: mob3_img,
                        4: mob4_img, 5: mob5_img, 6: mob6_img,
                        7: mob7_img, 8: mob8_img, 9: mob9_img, 10: mob10_img,
                        777: gold_slime_img, 1000: boss_img,
                        2000: colossus_boss_img, 3000: void_boss_img, 4000: void_lord_boss_img
                    }
                    icons_to_show = [mob_sprites[t] for t in types_present if t in mob_sprites]
                    if icons_to_show:
                        tot_i_w = len(icons_to_show) * 24
                        i_start_x = prep_rect.centerx - tot_i_w // 2
                        for i_idx, spr in enumerate(icons_to_show):
                            t_val = types_present[i_idx] if i_idx < len(types_present) else i_idx
                            if t_val not in _wave_preview_icon_cache:
                                _wave_preview_icon_cache[t_val] = pygame.transform.smoothscale(spr, (20, 20))
                            screen.blit(_wave_preview_icon_cache[t_val], (i_start_x + i_idx * 24, prep_rect.top + 27))

                # Прицельная сетка орбитального удара
                if orbital_targeting and not is_paused and not game_over:
                    mx, my = mouse_pos
                    r_surf = pygame.Surface((360, 360), pygame.SRCALPHA)
                    p_alpha = int(45 + 25 * math.sin(pygame.time.get_ticks() * 0.008))
                    pygame.draw.circle(r_surf, (200, 60, 255, p_alpha), (180, 180), 180)
                    pygame.draw.circle(r_surf, (240, 150, 255, 180), (180, 180), 180, width=2)
                    pygame.draw.circle(r_surf, (255, 200, 255, 120), (180, 180), 60, width=1)
                    pygame.draw.line(r_surf, (255, 220, 255, 200), (180, 20), (180, 340), 1)
                    pygame.draw.line(r_surf, (255, 220, 255, 200), (20, 180), (340, 180), 1)
                    pygame.draw.circle(r_surf, (255, 255, 255, 230), (180, 180), 4)
                    screen.blit(r_surf, (mx - 180, my - 180))

                    t_txt = small_font.render("ЗОНА ПОРАЖЕНИЯ (R=180)", True, (255, 230, 255))
                    t_sub = tiny_font.render("[ЛКМ / F] - Залп  |  [ПКМ / ESC] - Отмена", True, (230, 200, 240))
                    bw = max(t_txt.get_width(), t_sub.get_width()) + 20
                    bh = 42
                    bx = max(10, min(SCREEN_WIDTH - bw - 10, mx - bw // 2))
                    by = max(40, my - 215)
                    b_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
                    pygame.draw.rect(b_surf, (30, 15, 45, 220), (0, 0, bw, bh), border_radius=6)
                    pygame.draw.rect(b_surf, (220, 100, 255, 240), (0, 0, bw, bh), width=1, border_radius=6)
                    screen.blit(b_surf, (bx, by))
                    screen.blit(t_txt, (bx + 10, by + 4))
                    screen.blit(t_sub, (bx + 10, by + 23))

                # Подсветка и прицел точки сбора солдат палатки
                if rally_targeting_tent and not is_paused and not game_over:
                    tx, ty = int(rally_targeting_tent.x), int(rally_targeting_tent.y)
                    tr = int(rally_targeting_tent.range)
                    pulse = (math.sin(pygame.time.get_ticks() * 0.009) + 1.0) * 0.5

                    # Полупрозрачная зона действия палатки с пульсирующей каймой
                    r_surf = pygame.Surface((tr * 2 + 10, tr * 2 + 10), pygame.SRCALPHA)
                    p_alpha = int(22 + 16 * pulse)
                    pygame.draw.circle(r_surf, (50, 200, 90, p_alpha), (tr + 5, tr + 5), tr)
                    pygame.draw.circle(r_surf, (80, 255, 130, int(160 + 80 * pulse)), (tr + 5, tr + 5), tr, width=2)
                    screen.blit(r_surf, (tx - tr - 5, ty - tr - 5))

                    mx, my = mouse_pos
                    in_range = (math.hypot(mx - tx, my - ty) <= tr)
                    line_col = (80, 255, 120, 190) if in_range else (255, 90, 90, 180)

                    # Линия связи от центра палатки к курсору
                    guide_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    pygame.draw.line(guide_surf, line_col, (tx, ty), (mx, my), 2)
                    screen.blit(guide_surf, (0, 0))

                    # Превью флага на курсоре
                    draw_rally_flag(screen, mx, my, active=True, bg_time=pygame.time.get_ticks())

                    # Подсказка рядом с курсором
                    if in_range:
                        t_txt = small_font.render("ТОЧКА СБОРА СОЛДАТ", True, (160, 255, 190))
                        t_sub = tiny_font.render("[ЛКМ] - Установить  |  [ПКМ / ESC] - Отмена", True, (210, 255, 220))
                        b_border = (80, 240, 120, 240)
                    else:
                        t_txt = small_font.render("ВНЕ ЗОНЫ ДЕЙСТВИЯ!", True, (255, 130, 130))
                        t_sub = tiny_font.render("Выберите точку внутри зоны палатки", True, (255, 200, 200))
                        b_border = (255, 90, 90, 240)
                    bw = max(t_txt.get_width(), t_sub.get_width()) + 20
                    bh = 42
                    bx = max(10, min(SCREEN_WIDTH - bw - 10, mx - bw // 2))
                    by = max(40, my - 65)
                    b_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
                    pygame.draw.rect(b_surf, (20, 38, 26, 230), (0, 0, bw, bh), border_radius=6)
                    pygame.draw.rect(b_surf, b_border, (0, 0, bw, bh), width=1, border_radius=6)
                    b_surf.blit(t_txt, (10, 4))
                    b_surf.blit(t_sub, (10, 23))
                    screen.blit(b_surf, (bx, by))

                # Применение плавного появления интерфейса на старте катки
                if saved_field_backdrop is not None:
                    hud_overlay = screen.copy()
                    screen.blit(saved_field_backdrop, (0, 0))
                    hud_overlay.set_alpha(int(battle_ui_fade_alpha))
                    screen.blit(hud_overlay, (0, 0))

                # Интерактивная карточка башни при наведении (в обычном и upgrade режимах)
                if inspected_tower:
                    last_card_rect, last_btn_rect, last_target_rect, last_sell_rect, last_max_rect = draw_tower_inspect_card(
                        screen, inspected_tower, upgrade_mode, cacti, mouse_pos, savedata=savedata
                    )
                else:
                    last_card_rect = None
                    last_btn_rect = None
                    last_target_rect = None
                    last_sell_rect = None
                    last_max_rect = None

                # Меню паузы
                if is_paused and not game_over and pause_frozen_frame is None:
                    pause_frozen_frame = screen.copy()

            if is_paused and not game_over:
                screen.blit(pause_overlay_surf, (0, 0))

                pw, ph = 380, 340
                px = (SCREEN_WIDTH - pw) // 2
                py = (SCREEN_HEIGHT - ph) // 2
                p_box = pygame.Rect(px, py, pw, ph)

                pygame.draw.rect(screen, (22, 28, 38), p_box, border_radius=14)
                pygame.draw.rect(screen, (65, 160, 245), p_box, width=2, border_radius=14)

                screen.blit(_pause_title_surf, (p_box.centerx - _pause_title_surf.get_width() // 2, py + 18))

                btn_w, btn_h = 300, 42
                bx = p_box.centerx - btn_w // 2

                btn_resume = pygame.Rect(bx, py + 74, btn_w, btn_h)
                btn_restart = pygame.Rect(bx, py + 126, btn_w, btn_h)
                btn_bestiary = pygame.Rect(bx, py + 178, btn_w, btn_h)
                btn_menu = pygame.Rect(bx, py + 230, btn_w, btn_h)

                pause_click_rects = {
                    "resume": btn_resume,
                    "restart": btn_restart,
                    "bestiary": btn_bestiary,
                    "menu": btn_menu
                }

                p_btns = [
                    (btn_resume, _pause_btn_res_txt, (40, 140, 70), (55, 175, 90)),
                    (btn_restart, _pause_btn_rst_txt, (50, 70, 95), (65, 95, 130)),
                    (btn_bestiary, _pause_btn_bst_txt, (45, 80, 120), (60, 110, 165)),
                    (btn_menu, _pause_btn_mnu_txt, (110, 35, 40), (145, 45, 52))
                ]

                # Инфо-строка биома внизу меню паузы
                biome = MAP_BIOMES_DATA.get(game_map, MAP_BIOMES_DATA[0])
                p_sub_txt = tiny_font.render(f"{biome['name']}  •  Волна {wave}  •  {biome['mutator_badge']}", True, (150, 175, 205))
                screen.blit(p_sub_txt, (p_box.centerx - p_sub_txt.get_width() // 2, py + 292))

                for brect, bt_surf, col_normal, col_hov in p_btns:
                    b_hovered = brect.collidepoint(mouse_pos)
                    pygame.draw.rect(screen, col_hov if b_hovered else col_normal, brect, border_radius=8)
                    pygame.draw.rect(screen, YELLOW if b_hovered else WHITE, brect, width=1, border_radius=8)
                    screen.blit(bt_surf, (brect.centerx - bt_surf.get_width() // 2, brect.centery - bt_surf.get_height() // 2))

            # Экран конца игры (Подробная статистика сессии)
            if game_over:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 205))
                screen.blit(overlay, (0, 0))

                gw, gh = 520, 390
                gx = (SCREEN_WIDTH - gw) // 2
                gy = (SCREEN_HEIGHT - gh) // 2
                g_box = pygame.Rect(gx, gy, gw, gh)

                pygame.draw.rect(screen, (20, 25, 35), g_box, border_radius=14)
                pygame.draw.rect(screen, RED, g_box, width=2, border_radius=14)

                go_txt = massive_font.render("ИГРА ОКОНЧЕНА", True, RED)
                screen.blit(go_txt, (g_box.centerx - go_txt.get_width() // 2, gy + 18))

                sub_txt = small_font.render(f"Карта: {MAP_NAMES_LIST[game_map]}", True, (200, 210, 220))
                screen.blit(sub_txt, (g_box.centerx - sub_txt.get_width() // 2, gy + 68))

                mvp_str = "Нет построенных башен"
                if towers:
                    mvp_t = max(towers, key=lambda t: t.damage_dealt)
                    t_names = {"magic": "Маг", "rock": "Огонь", "freeze": "Мороз", "tent": "Палатка", "tesla": "Тесла"}
                    mvp_str = f"{t_names.get(mvp_t.type, 'Башня')} (Ур. {mvp_t.level}) - {mvp_t.damage_dealt:.0f} урона"

                stats_lines = [
                    ("Достигнутая волна:", f"{wave} (Рекорд: {savedata['LevelsRecords'][game_map]})", GOLD),
                    ("Уничтожено слаймов:", f"{session_kills}", WHITE),
                    ("Заработано кактусов:", f"+{session_cacti}", GREEN),
                    ("Звёздных кактусов:", f"+{session_stellar}", (255, 215, 80)),
                    ("MVP Башня:", mvp_str, CYAN)
                ]

                sy = gy + 105
                for label, val, val_col in stats_lines:
                    l_surf = small_font.render(label, True, (180, 190, 205))
                    v_surf = small_font.render(val, True, val_col)
                    screen.blit(l_surf, (gx + 32, sy))
                    screen.blit(v_surf, (gx + gw - 32 - v_surf.get_width(), sy))
                    pygame.draw.line(screen, (40, 50, 65), (gx + 30, sy + 25), (gx + gw - 30, sy + 25), 1)
                    sy += 36

                r_btn = pygame.Rect(gx + 30, gy + gh - 65, 215, 46)
                q_btn = pygame.Rect(gx + gw - 245, gy + gh - 65, 215, 46)

                r_hov = r_btn.collidepoint(mouse_pos)
                q_hov = q_btn.collidepoint(mouse_pos)

                pygame.draw.rect(screen, (35, 140, 60) if r_hov else (25, 105, 45), r_btn, border_radius=8)
                pygame.draw.rect(screen, YELLOW if r_hov else WHITE, r_btn, width=1, border_radius=8)
                rt = font.render("[R] Заново", True, WHITE)
                screen.blit(rt, (r_btn.centerx - rt.get_width() // 2, r_btn.centery - rt.get_height() // 2))

                pygame.draw.rect(screen, (130, 45, 50) if q_hov else (95, 30, 35), q_btn, border_radius=8)
                pygame.draw.rect(screen, YELLOW if q_hov else WHITE, q_btn, width=1, border_radius=8)
                qt = font.render("[ESC] Меню", True, WHITE)
                screen.blit(qt, (q_btn.centerx - qt.get_width() // 2, q_btn.centery - qt.get_height() // 2))

            # Отрисовка мини-игры Раскопок (Нативное окно на PC либо фейковое окно на Android/встроенном режиме)
            if dig_session:
                if dig_window:
                    try:
                        if not dig_window.always_on_top:
                            dig_window.always_on_top = True
                        dig_surf = dig_window.get_surface()
                        draw_dig_window(dig_surf, dig_session, dig_mouse_pos)
                        dig_window.flip()
                    except Exception as err:
                        print(f"Dig window render error: {err}")
                else:
                    # Фейковое окно раскопок (Android и встроенный режим)
                    fake_w, fake_h = 360, 460
                    fake_x = (SCREEN_WIDTH - fake_w) // 2
                    fake_y = (SCREEN_HEIGHT - fake_h) // 2

                    # Полупрозрачное затемнение игрового поля
                    dim_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    dim_overlay.fill((0, 0, 0, 150))
                    screen.blit(dim_overlay, (0, 0))

                    # Тень и обводка фейкового окна
                    shadow_rect = pygame.Rect(fake_x - 4, fake_y - 4, fake_w + 8, fake_h + 8)
                    pygame.draw.rect(screen, (10, 8, 6), shadow_rect, border_radius=12)

                    fake_dig_surf = pygame.Surface((fake_w, fake_h))
                    local_mouse = (mouse_pos[0] - fake_x, mouse_pos[1] - fake_y)
                    draw_dig_window(fake_dig_surf, dig_session, local_mouse)
                    screen.blit(fake_dig_surf, (fake_x, fake_y))

                # Таймер авто-закрытия после победы или обвала
                if dig_session.is_won or dig_session.is_lost:
                    dig_window_close_timer += raw_dt
                    if dig_window_close_timer >= 1.8:
                        if dig_window:
                            try:
                                dig_window.destroy()
                            except Exception:
                                pass
                        dig_window = None
                        dig_session = None
                        dig_window_close_timer = 0.0

            pygame.display.flip()

    if dig_window:
        try:
            dig_window.destroy()
        except Exception:
            pass
        dig_window = None

    win_mgr.reset_position()
    save_data(savedata)
    pygame.quit()


if __name__ == "__main__":
    run_game()
