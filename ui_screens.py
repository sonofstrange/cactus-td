# =========================================================================
# ЭКРАНЫ И ИНТЕРФЕЙС ИГРЫ (UI SCREENS)
# =========================================================================
import os
import math
import random
import time
import pygame

from config import *
from game_data import *
from entities import *
from relic_art import get_relic_art_surface, get_relic_icon_preview

# Кэши UI поверхностей и масштабированных иконок для ускорения рендеринга (0 аллокаций в секунду)
_cached_card_shadow_surf = None
_cached_inspect_card_surf = None
_tower_inspect_icon_cache = {}
_bestiary_slime_icon_cache = {}
_bestiary_card_cache = {}
_bestiary_btn_cache = {}
_unknown_slime_texts = None
_ach_icon_cache = {}
_tower_inspect_btn_cache = {}



def generate_background(surf, bg_time, map_id=None, custom_cols=None):
    if custom_cols is not None:
        col_a, col_b = custom_cols
    elif map_id is not None and map_id in MAP_BIOMES_DATA:
        col_a = MAP_BIOMES_DATA[map_id]["bg_col_a"]
        col_b = MAP_BIOMES_DATA[map_id]["bg_col_b"]
    else:
        col_a = BG_GRID_A
        col_b = BG_GRID_B

    surf.fill(col_a)
    cell_size = 50
    sw, sh = surf.get_width(), surf.get_height()

    # Делаем линии в подменю и на экранах более выразительными и четкими
    line_col = (
        min(255, int(col_b[0] * 1.45 + 18)),
        min(255, int(col_b[1] * 1.45 + 18)),
        min(255, int(col_b[2] * 1.45 + 18))
    ) if col_a[0] < 50 else (
        min(255, int(col_b[0] * 1.12 + 12)),
        min(255, int(col_b[1] * 1.12 + 12)),
        min(255, int(col_b[2] * 1.12 + 12))
    )

    if get_graphics_preset() == "optimized":
        ox = int((bg_time * 0.025) % cell_size)
        oy = int((bg_time * 0.025) % cell_size)
        for x in range(ox - cell_size, sw + cell_size, cell_size):
            pygame.draw.line(surf, line_col, (x, 0), (x, sh), 2)
        for y in range(oy - cell_size, sh + cell_size, cell_size):
            pygame.draw.line(surf, line_col, (0, y), (sw, y), 2)
        return

    offset_x = math.sin(bg_time * 0.001) * 30
    offset_y = math.cos(bg_time * 0.001) * 30

    for x in range(-cell_size, sw + cell_size, cell_size):
        warp = math.sin(x * 0.01 + bg_time * 0.002) * 15
        pygame.draw.line(surf, line_col, (x + offset_x + warp, 0), (x + offset_y - warp, sh), 2)

    for y in range(-cell_size, sh + cell_size, cell_size):
        warp = math.cos(y * 0.015 + bg_time * 0.0018) * 15
        pygame.draw.line(surf, line_col, (0, y + offset_y + warp), (sw, y + offset_x - warp), 2)


def draw_dark_cactus_counter(surface, rect, savedata, mouse_pos=None):
    """
    Отрисовывает счётчик Тёмных кактусов:
    - Если Тёмный Космос открыт: кристально-фиолетовая панель со значением и иконкой.
    - Если заблокирован: тёмно-стальная панель под крестообразным замком с цепями!
    """
    is_unlocked = is_dark_cacti_unlocked(savedata)
    is_hov = mouse_pos is not None and rect.collidepoint(mouse_pos)

    if is_unlocked:
        pygame.draw.rect(surface, (30, 18, 42), rect, border_radius=8)
        pygame.draw.rect(surface, (205, 90, 255) if is_hov else (180, 70, 240), rect, width=2 if is_hov else 1, border_radius=8)
        surface.blit(dark_cactus_img_m, (rect.left + 8, rect.centery - 18))
        dark_txt = font.render(f"{savedata.get('DarkCactuses', 0)}", True, WHITE)
        surface.blit(dark_txt, (rect.left + 46, rect.centery - dark_txt.get_height() // 2))
    else:
        # Стальная подложка с мистическим фиолетовым отливом
        pygame.draw.rect(surface, (20, 16, 28) if not is_hov else (32, 24, 44), rect, border_radius=8)
        pygame.draw.rect(surface, (130, 105, 160) if not is_hov else (190, 150, 230), rect, width=2 if is_hov else 1, border_radius=8)

        # Теневой силуэт кактуса на заднем плане
        d_ghost = dark_cactus_img_m.copy()
        d_ghost.fill((45, 30, 60, 100), special_flags=pygame.BLEND_RGB_MULT)
        surface.blit(d_ghost, (rect.left + 8, rect.centery - 18))

        # Перекрещенные кованые цепи (эффект звеньев крест-накрест)
        chain_sh = (40, 35, 50)
        chain_fg = (150, 145, 170)
        # Тень цепей
        pygame.draw.line(surface, chain_sh, (rect.left + 5, rect.top + 4), (rect.right - 5, rect.bottom - 4), 4)
        pygame.draw.line(surface, chain_sh, (rect.left + 5, rect.bottom - 4), (rect.right - 5, rect.top + 4), 4)
        # Основные цепи
        pygame.draw.line(surface, chain_fg, (rect.left + 5, rect.top + 4), (rect.right - 5, rect.bottom - 4), 2)
        pygame.draw.line(surface, chain_fg, (rect.left + 5, rect.bottom - 4), (rect.right - 5, rect.top + 4), 2)
        # Звенья цепи (металлические кольца на лучах)
        for pct in [0.22, 0.78]:
            p1 = (int(rect.left + 5 + (rect.width - 10) * pct), int(rect.top + 4 + (rect.height - 8) * pct))
            p2 = (int(rect.left + 5 + (rect.width - 10) * pct), int(rect.bottom - 4 - (rect.height - 8) * pct))
            pygame.draw.circle(surface, (200, 195, 220), p1, 3, width=1)
            pygame.draw.circle(surface, (200, 195, 220), p2, 3, width=1)

        # Центральная круглая стальная печать с золотым замком
        lock_center = (rect.centerx, rect.centery)
        pygame.draw.circle(surface, (25, 20, 34), lock_center, 14)
        pygame.draw.circle(surface, (220, 180, 75) if is_hov else (160, 130, 60), lock_center, 14, width=2)
        surface.blit(lock_icon, (lock_center[0] - lock_icon.get_width() // 2, lock_center[1] - lock_icon.get_height() // 2))


# -------------------------------------------------------------------------
# ЭКРАН 1: ВЫБОР КАРТЫ (ГЛАВНОЕ МЕНЮ)
# -------------------------------------------------------------------------
_minimap_cache = {}

def draw_minimap(surface, path, tower_slots, pos_x, pos_y, width, height, selected=False, map_id=0, is_unlocked=True):
    cache_key = (map_id, width, height, is_unlocked)
    mm_surf = _minimap_cache.get(cache_key)
    if mm_surf is None:
        biome = MAP_BIOMES_DATA.get(map_id, MAP_BIOMES_DATA[0])
        bg_col_a = biome["bg_col_a"]
        bg_col_b = biome["bg_col_b"]
        road_col = biome["road_col"]
        road_border = biome.get("road_border", (50, 40, 30))

        mm_surf = pygame.Surface((width, height), pygame.SRCALPHA)

        # 1. Заливка фона с микро-текстурой биома (шахматная плитка)
        mm_surf.fill(bg_col_a)
        grid_sz = 14
        for gx in range(0, width, grid_sz):
            for gy in range(0, height, grid_sz):
                if ((gx // grid_sz) + (gy // grid_sz)) % 2 == 1:
                    pygame.draw.rect(mm_surf, (*bg_col_b[:3], 120), (gx, gy, grid_sz, grid_sz))

        # 2. Масштабирование координат
        scale_x = width / 1280.0
        scale_y = height / 720.0
        pts = [(int(pt[0] * scale_x), int(pt[1] * scale_y)) for pt in path]

        # 3. Рисуем дорогу с каймой биома
        if len(pts) > 1:
            for i in range(len(pts) - 1):
                pygame.draw.line(mm_surf, road_border, pts[i], pts[i + 1], 12)
                pygame.draw.circle(mm_surf, road_border, pts[i], 6)
            pygame.draw.circle(mm_surf, road_border, pts[-1], 6)

            for i in range(len(pts) - 1):
                pygame.draw.line(mm_surf, road_col, pts[i], pts[i + 1], 8)
                pygame.draw.circle(mm_surf, road_col, pts[i], 4)
            pygame.draw.circle(mm_surf, road_col, pts[-1], 4)

        # 4. Слоты башен (стилизованные постаменты)
        for slot in tower_slots:
            sx = int(slot[0] * scale_x)
            sy = int(slot[1] * scale_y)
            pygame.draw.circle(mm_surf, (20, 28, 38, 220), (sx, sy), 6)
            pygame.draw.circle(mm_surf, (80, 160, 230), (sx, sy), 5)
            pygame.draw.circle(mm_surf, (210, 240, 255), (sx, sy), 3)

        # 5. Маркер портала спавна слаймов (Старт)
        if len(pts) > 0:
            sp_x, sp_y = pts[0]
            pygame.draw.circle(mm_surf, (245, 45, 85), (sp_x, sp_y), 7)
            pygame.draw.circle(mm_surf, (255, 210, 225), (sp_x, sp_y), 4)
            pygame.draw.circle(mm_surf, WHITE, (sp_x, sp_y), 2)

        # 6. Маркер базы кактусов (Финиш)
        if len(pts) > 1:
            ep_x, ep_y = pts[-1]
            pygame.draw.circle(mm_surf, (45, 225, 85), (ep_x, ep_y), 7)
            pygame.draw.circle(mm_surf, (190, 255, 210), (ep_x, ep_y), 4)
            pygame.draw.circle(mm_surf, WHITE, (ep_x, ep_y), 2)

        # Тонкая внутренняя рамка
        pygame.draw.rect(mm_surf, (0, 0, 0, 70), (0, 0, width, height), 1, border_radius=6)

        # Блокировка (если не открыта)
        if not is_unlocked:
            lock_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            lock_overlay.fill((10, 14, 20, 215))
            mm_surf.blit(lock_overlay, (0, 0))
            mm_surf.blit(lock_icon, (width // 2 - lock_icon.get_width() // 2, height // 2 - lock_icon.get_height() // 2))

        _minimap_cache[cache_key] = mm_surf

    surface.blit(mm_surf, (pos_x, pos_y))

    # Внешняя рамка мини-карты
    mm_border = GOLD if selected else (65, 90, 120)
    pygame.draw.rect(surface, mm_border, (pos_x - 1, pos_y - 1, width + 2, height + 2), 2 if selected else 1, border_radius=7)


def draw_map_info_modal(surface, map_id, sdata, mouse_pos, inspect_wave=1):
    dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim_surf.fill((0, 0, 0, 205))
    surface.blit(dim_surf, (0, 0))

    modal_w = 980
    modal_h = 610
    modal_rect = pygame.Rect((SCREEN_WIDTH - modal_w) // 2, (SCREEN_HEIGHT - modal_h) // 2, modal_w, modal_h)

    pygame.draw.rect(surface, (16, 22, 32), modal_rect, border_radius=16)
    pygame.draw.rect(surface, (55, 125, 200), modal_rect, width=2, border_radius=16)

    biome = MAP_BIOMES_DATA.get(map_id, MAP_BIOMES_DATA[0])

    # Шапка
    surface.blit(info_icon, (modal_rect.left + 24, modal_rect.top + 16))
    m_title = large_font.render(f"КАРТА {map_id + 1}: {biome['name'].upper()} - {biome['sub']}", True, WHITE)
    surface.blit(m_title, (modal_rect.left + 54, modal_rect.top + 14))

    close_btn = pygame.Rect(modal_rect.right - 42, modal_rect.top + 14, 28, 28)
    cl_hov = close_btn.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (180, 40, 40) if cl_hov else (40, 48, 60), close_btn, border_radius=6)
    pygame.draw.rect(surface, WHITE, close_btn, width=1, border_radius=6)
    cl_txt = font.render("X", True, WHITE)
    surface.blit(cl_txt, (close_btn.centerx - cl_txt.get_width() // 2, close_btn.centery - cl_txt.get_height() // 2))

    pygame.draw.line(surface, (45, 60, 80), (modal_rect.left + 20, modal_rect.top + 48), (modal_rect.right - 20, modal_rect.top + 48), 1)

    # Описание и мутатор карты
    lore_txt = tiny_font.render(biome.get("lore_desc", ""), True, (215, 230, 245))
    surface.blit(lore_txt, (modal_rect.left + 24, modal_rect.top + 56))

    # Мутатор блок
    mut_box = pygame.Rect(modal_rect.left + 24, modal_rect.top + 78, modal_w - 48, 36)
    pygame.draw.rect(surface, (22, 32, 46), mut_box, border_radius=8)
    pygame.draw.rect(surface, (50, 100, 165), mut_box, width=1, border_radius=8)

    m_title_txt = font.render(f"МУТАТОР: {biome['mutator_title'].upper()}", True, (100, 215, 255))
    surface.blit(m_title_txt, (mut_box.left + 12, mut_box.top + 6))
    m_desc_full = f"{biome['mutator_desc']}"
    if map_id == 0:
        m_desc_full += " (+10% стартовых кактусов)"
    m_desc_txt = tiny_font.render(m_desc_full, True, (225, 240, 255))
    surface.blit(m_desc_txt, (mut_box.left + 14 + m_title_txt.get_width(), mut_box.top + 9))

    # Чипы параметров карты
    chip_y = mut_box.bottom + 8
    stellar_m = biome.get('stellar_mult', 1.0)
    cacti_m = biome.get('cacti_mult', 1.0)
    chips = [
        (f"HP мобов: x{biome.get('hp_mult', 1.0):.2f}", (255, 120, 120), (45, 20, 24)),
        (f"Скорость мобов: x{biome.get('spd_mult', 1.0):.2f}", (255, 185, 90), (45, 32, 18)),
        (f"Звёздные кактусы: x{stellar_m:.2f}*", (255, 225, 75), (50, 42, 16)),
    ]
    if cacti_m > 1.0:
        chips.append((f"Кактусы с мобов: +{int(round((cacti_m - 1.0) * 100))}%", (110, 245, 140), (18, 44, 26)))
    chips.append((f"Саундтрек: {biome.get('soundtrack', ('', ''))[0]}", (215, 170, 255), (38, 22, 50)))
    cur_cx = modal_rect.left + 24
    for c_text, c_fg, c_bg in chips:
        c_surf = tiny_font.render(c_text, True, c_fg)
        cw = c_surf.get_width() + 16
        c_rect = pygame.Rect(cur_cx, chip_y, cw, 24)
        pygame.draw.rect(surface, c_bg, c_rect, border_radius=6)
        pygame.draw.rect(surface, c_fg, c_rect, width=1, border_radius=6)
        surface.blit(c_surf, (c_rect.left + 8, c_rect.centery - c_surf.get_height() // 2))
        cur_cx += cw + 8

    # Линия разделения
    p_y = chip_y + 32
    pygame.draw.line(surface, (50, 75, 105), (modal_rect.left + 20, p_y), (modal_rect.right - 20, p_y), 2)
    p_y += 8

    # =========================================================================
    # ПОВОЛНОВОЙ АНАЛИЗ (ИНТЕРАКТИВНЫЙ ИНСПЕКТОР ВОЛН)
    # =========================================================================
    w_title = font.render("АНАЛИЗ ВОЛНЫ:", True, (255, 220, 100))
    surface.blit(w_title, (modal_rect.left + 24, p_y + 4))

    nav_buttons = []

    # Навигационные кнопки: [-10] [-1] << ВОЛНА N >> [+1] [+10]
    nav_y = p_y + 2
    b_x = modal_rect.left + 220

    btn_m10 = pygame.Rect(b_x, nav_y, 44, 28)
    m10_hov = btn_m10.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (40, 60, 85) if m10_hov else (25, 38, 55), btn_m10, border_radius=6)
    pygame.draw.rect(surface, (90, 170, 240) if m10_hov else (50, 80, 115), btn_m10, width=1, border_radius=6)
    t_m10 = tiny_font.render("-10", True, WHITE)
    surface.blit(t_m10, (btn_m10.centerx - t_m10.get_width() // 2, btn_m10.centery - t_m10.get_height() // 2))
    nav_buttons.append((btn_m10, "-10"))

    btn_m1 = pygame.Rect(btn_m10.right + 6, nav_y, 34, 28)
    m1_hov = btn_m1.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (40, 60, 85) if m1_hov else (25, 38, 55), btn_m1, border_radius=6)
    pygame.draw.rect(surface, (90, 170, 240) if m1_hov else (50, 80, 115), btn_m1, width=1, border_radius=6)
    t_m1 = tiny_font.render("-1", True, WHITE)
    surface.blit(t_m1, (btn_m1.centerx - t_m1.get_width() // 2, btn_m1.centery - t_m1.get_height() // 2))
    nav_buttons.append((btn_m1, "-1"))

    # Центральный бейдж волны
    cur_w_rect = pygame.Rect(btn_m1.right + 8, nav_y - 2, 140, 32)
    pygame.draw.rect(surface, (36, 48, 70), cur_w_rect, border_radius=8)
    pygame.draw.rect(surface, (255, 215, 60), cur_w_rect, width=2, border_radius=8)
    w_num_txt = font.render(f"ВОЛНА {inspect_wave}", True, (255, 235, 120))
    surface.blit(w_num_txt, (cur_w_rect.centerx - w_num_txt.get_width() // 2, cur_w_rect.centery - w_num_txt.get_height() // 2))

    btn_p1 = pygame.Rect(cur_w_rect.right + 8, nav_y, 34, 28)
    p1_hov = btn_p1.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (40, 60, 85) if p1_hov else (25, 38, 55), btn_p1, border_radius=6)
    pygame.draw.rect(surface, (90, 170, 240) if p1_hov else (50, 80, 115), btn_p1, width=1, border_radius=6)
    t_p1 = tiny_font.render("+1", True, WHITE)
    surface.blit(t_p1, (btn_p1.centerx - t_p1.get_width() // 2, btn_p1.centery - t_p1.get_height() // 2))
    nav_buttons.append((btn_p1, "+1"))

    btn_p10 = pygame.Rect(btn_p1.right + 6, nav_y, 44, 28)
    p10_hov = btn_p10.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (40, 60, 85) if p10_hov else (25, 38, 55), btn_p10, border_radius=6)
    pygame.draw.rect(surface, (90, 170, 240) if p10_hov else (50, 80, 115), btn_p10, width=1, border_radius=6)
    t_p10 = tiny_font.render("+10", True, WHITE)
    surface.blit(t_p10, (btn_p10.centerx - t_p10.get_width() // 2, btn_p10.centery - t_p10.get_height() // 2))
    nav_buttons.append((btn_p10, "+10"))

    # Пресеты важных волн (1, 10, 20, 25, 35, 50, 75)
    presets = [(1, "1"), (10, "10"), (20, "20"), (25, "25*"), (35, "35"), (50, "50*"), (75, "75*")]
    pr_x = btn_p10.right + 18
    for pw, plbl in presets:
        pw_rect = pygame.Rect(pr_x, nav_y, 36 if len(plbl) <= 2 else 48, 28)
        is_cur = (inspect_wave == pw)
        pw_hov = pw_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (60, 48, 20) if is_cur else ((45, 55, 75) if pw_hov else (25, 34, 48)), pw_rect, border_radius=6)
        pygame.draw.rect(surface, GOLD if is_cur else ((100, 190, 255) if pw_hov else (50, 68, 92)), pw_rect, width=1, border_radius=6)
        pw_txt = tiny_font.render(plbl, True, (255, 230, 100) if is_cur else WHITE)
        surface.blit(pw_txt, (pw_rect.centerx - pw_txt.get_width() // 2, pw_rect.centery - pw_txt.get_height() // 2))
        nav_buttons.append((pw_rect, pw))
        pr_x += pw_rect.width + 6

    # Получаем детальный анализ выбранной волны
    w_data = get_wave_analysis(map_id, inspect_wave, sdata)

    # Панель сводки волны
    sum_y = nav_y + 36
    sum_rect = pygame.Rect(modal_rect.left + 24, sum_y, modal_w - 48, 38)
    pygame.draw.rect(surface, (20, 30, 44), sum_rect, border_radius=8)
    pygame.draw.rect(surface, (45, 80, 125), sum_rect, width=1, border_radius=8)

    stat1 = tiny_font.render(f"Врагов: {w_data['total_count']} шт.", True, (160, 225, 255))
    surface.blit(stat1, (sum_rect.left + 16, sum_rect.centery - stat1.get_height() // 2))

    stat2 = tiny_font.render(f"Множитель HP: x{w_data['total_hp_mult']:.2f}", True, (255, 145, 145))
    surface.blit(stat2, (sum_rect.left + 140, sum_rect.centery - stat2.get_height() // 2))

    stat3 = tiny_font.render(f"Добыча волны: ~{w_data['total_reward']} какт.", True, (120, 245, 140))
    surface.blit(stat3, (sum_rect.left + 315, sum_rect.centery - stat3.get_height() // 2))

    # Бейджи событий
    ev_x = sum_rect.right - 10
    for ev in reversed(w_data['events']):
        ev_surf = tiny_font.render(ev, True, (255, 225, 110))
        ev_w = ev_surf.get_width() + 14
        ev_r = pygame.Rect(ev_x - ev_w, sum_rect.centery - 12, ev_w, 24)
        pygame.draw.rect(surface, (48, 38, 16), ev_r, border_radius=6)
        pygame.draw.rect(surface, GOLD, ev_r, width=1, border_radius=6)
        surface.blit(ev_surf, (ev_r.centerx - ev_surf.get_width() // 2, ev_r.centery - ev_surf.get_height() // 2))
        ev_x -= ev_w + 6

    # Заголовок списка слаймов
    list_y = sum_y + 46
    hdr_line_y = list_y + 18
    hdr_slime = tiny_font.render("СЛАЙМ", True, (140, 165, 195))
    hdr_cnt = tiny_font.render("КОЛИЧЕСТВО", True, (140, 165, 195))
    hdr_hp = tiny_font.render("HP ЕДИНИЦЫ", True, (140, 165, 195))
    hdr_spd = tiny_font.render("СКОРОСТЬ", True, (140, 165, 195))
    hdr_rew = tiny_font.render("ДОБЫЧА", True, (140, 165, 195))
    hdr_spec = tiny_font.render("ОСОБЕННОСТИ И СПОСОБНОСТИ", True, (140, 165, 195))

    surface.blit(hdr_slime, (modal_rect.left + 64, list_y))
    surface.blit(hdr_cnt, (modal_rect.left + 310, list_y))
    surface.blit(hdr_hp, (modal_rect.left + 405, list_y))
    surface.blit(hdr_spd, (modal_rect.left + 495, list_y))
    surface.blit(hdr_rew, (modal_rect.left + 580, list_y))
    surface.blit(hdr_spec, (modal_rect.left + 670, list_y))

    pygame.draw.line(surface, (38, 52, 72), (modal_rect.left + 24, hdr_line_y), (modal_rect.right - 24, hdr_line_y), 1)

    # Список карточек слаймов на этой волне (с проверкой открытия в Бестиарии)
    discovered_set = set(sdata.get("BestiaryDiscovered", [1]))
    row_y = hdr_line_y + 6
    card_h = 42

    for r_item in w_data['roster']:
        r_box = pygame.Rect(modal_rect.left + 24, row_y, modal_w - 48, card_h)
        is_boss = r_item['is_boss']
        is_known = (r_item['id'] in discovered_set) or (is_boss and r_item['id'] in discovered_set)

        row_bg = (34, 22, 38) if is_boss else (18, 26, 38)
        row_border = (200, 80, 255) if is_boss else (38, 56, 78)
        pygame.draw.rect(surface, row_bg, r_box, border_radius=6)
        pygame.draw.rect(surface, row_border, r_box, width=1, border_radius=6)

        # Портрет слайма (если не открыт - темная плашка с вопросом)
        if is_known:
            tex = get_slime_texture(r_item['img_key'])
            scaled_t = pygame.transform.smoothscale(tex, (32, 32))
            surface.blit(scaled_t, (r_box.left + 8, r_box.centery - 16))
        else:
            q_box = pygame.Rect(r_box.left + 8, r_box.centery - 16, 32, 32)
            pygame.draw.rect(surface, (28, 36, 48), q_box, border_radius=6)
            pygame.draw.rect(surface, (60, 80, 105), q_box, width=1, border_radius=6)
            q_lbl = font.render("?", True, (130, 150, 175))
            surface.blit(q_lbl, (q_box.centerx - q_lbl.get_width() // 2, q_box.centery - q_lbl.get_height() // 2))

        # Имя слайма
        if is_known:
            name_col = (255, 215, 80) if is_boss else WHITE
            nm_txt = font.render(r_item['name'], True, name_col)
        else:
            name_col = (145, 160, 180)
            nm_txt = font.render("??? Неизвестный Босс" if is_boss else "??? Неизвестно", True, name_col)
        surface.blit(nm_txt, (r_box.left + 48, r_box.centery - nm_txt.get_height() // 2))

        # Количество
        cnt_txt = font.render(f"x{r_item['count']} шт.", True, (255, 235, 120))
        surface.blit(cnt_txt, (modal_rect.left + 310, r_box.centery - cnt_txt.get_height() // 2))

        # HP (показываем расчетное HP для тактического планирования)
        hp_txt = font.render(f"{r_item['hp']:,}".replace(",", " "), True, (255, 125, 125))
        surface.blit(hp_txt, (modal_rect.left + 405, r_box.centery - hp_txt.get_height() // 2))

        # Скорость
        spd_str = f"{r_item['speed']}" if is_known else "???"
        spd_txt = font.render(spd_str, True, (255, 185, 90) if is_known else (130, 145, 165))
        surface.blit(spd_txt, (modal_rect.left + 495, r_box.centery - spd_txt.get_height() // 2))

        # Добыча
        rew_str = f"+{r_item['reward']}" if is_known else "???"
        rew_txt = font.render(rew_str, True, (110, 245, 140) if is_known else (130, 145, 165))
        surface.blit(rew_txt, (modal_rect.left + 580, r_box.centery - rew_txt.get_height() // 2))

        # Особенности
        if is_known:
            tr_col = (230, 160, 255) if is_boss else (180, 215, 245)
            tr_txt = tiny_font.render(r_item['traits'], True, tr_col)
        else:
            tr_col = (120, 140, 165)
            tr_txt = tiny_font.render("Победите в бою для открытия в бестиарии", True, tr_col)
        surface.blit(tr_txt, (modal_rect.left + 670, r_box.centery - tr_txt.get_height() // 2))

        row_y += card_h + 5

    # Подсказка внизу
    hint_txt = tiny_font.render("Подсказка: нажимайте стрелки [<-] / [->] на клавиатуре или колесо мыши для быстрой смены волны", True, (115, 145, 175))
    surface.blit(hint_txt, (modal_rect.centerx - hint_txt.get_width() // 2, modal_rect.bottom - 22))

    return close_btn, nav_buttons

def _render_wrapped_lines(text, font, max_w):
    words = text.split(' ')
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_greenhouse_modal(surface, cactus_id, savedata, mouse_pos):
    c_data = next((c for c in GREENHOUSE_CACTI if c["id"] == cactus_id), None)
    if not c_data:
        return None, None

    dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim_surf.fill((0, 0, 0, 215))
    surface.blit(dim_surf, (0, 0))

    modal_w = 940
    modal_h = 580
    modal_rect = pygame.Rect((SCREEN_WIDTH - modal_w) // 2, (SCREEN_HEIGHT - modal_h) // 2, modal_w, modal_h)

    pygame.draw.rect(surface, (16, 26, 22), modal_rect, border_radius=16)
    pygame.draw.rect(surface, (60, 160, 110), modal_rect, width=2, border_radius=16)

    # Заголовок модального окна
    surface.blit(sprout_icon, (modal_rect.left + 24, modal_rect.top + 16))
    m_title = large_font.render(f"{c_data['name'].upper()} - {c_data['title']}", True, (240, 255, 245))
    surface.blit(m_title, (modal_rect.left + 54, modal_rect.top + 14))

    close_btn = pygame.Rect(modal_rect.right - 42, modal_rect.top + 14, 28, 28)
    cl_hov = close_btn.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (180, 40, 40) if cl_hov else (40, 52, 45), close_btn, border_radius=6)
    pygame.draw.rect(surface, WHITE, close_btn, width=1, border_radius=6)
    cl_txt = font.render("X", True, WHITE)
    surface.blit(cl_txt, (close_btn.centerx - cl_txt.get_width() // 2, close_btn.centery - cl_txt.get_height() // 2))

    pygame.draw.line(surface, (45, 80, 60), (modal_rect.left + 20, modal_rect.top + 48), (modal_rect.right - 20, modal_rect.top + 48), 1)

    gh = savedata.get("Greenhouse", {})
    c_save = gh.get(cactus_id, {"level": 0, "sprouts": 0})
    level = c_save.get("level", 0)
    sprouts = c_save.get("sprouts", 0)

    # Левая колонка: портрет, описание, саженцы, кнопка улучшения
    left_w = 320
    p_box = pygame.Rect(modal_rect.left + 24, modal_rect.top + 64, 128, 128)
    pygame.draw.rect(surface, (22, 38, 30), p_box, border_radius=12)
    pygame.draw.rect(surface, (70, 175, 115) if level > 0 else (45, 65, 55), p_box, width=2, border_radius=12)

    raw_tex = gh_cacti_textures.get(c_data["img_key"])
    if raw_tex:
        scaled_tex = pygame.transform.scale(raw_tex, (96, 96))
        if level == 0:
            dark_t = scaled_tex.copy()
            dark_t.fill((60, 80, 70, 180), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(dark_t, (p_box.centerx - 48, p_box.centery - 48))
        else:
            surface.blit(scaled_tex, (p_box.centerx - 48, p_box.centery - 48))

    # Статус уровня рядом с портретом
    st_x = p_box.right + 16
    lvl_str = f"УРОВЕНЬ {level} / 5" if level > 0 else "НЕ ВЫРАЩЕН"
    lvl_col = GOLD if level == 5 else ((110, 245, 160) if level > 0 else (170, 175, 170))
    lvl_txt = font.render(lvl_str, True, lvl_col)
    surface.blit(lvl_txt, (st_x, p_box.top + 10))

    bname_lbl = tiny_font.render("Особый дар флоры:", True, (140, 175, 160))
    surface.blit(bname_lbl, (st_x, p_box.top + 40))
    bname_txt = font.render(c_data["buff_name"], True, (255, 230, 130))
    surface.blit(bname_txt, (st_x, p_box.top + 58))

    spr_str = f"Саженцев в наличии: {sprouts}"
    spr_txt = tiny_font.render(spr_str, True, (200, 240, 215))
    surface.blit(sprout_icon_s, (st_x, p_box.top + 94))
    surface.blit(spr_txt, (st_x + 22, p_box.top + 94))

    # Описание / лор кактуса
    desc_rect = pygame.Rect(modal_rect.left + 24, modal_rect.top + 208, left_w + 140, 110)
    pygame.draw.rect(surface, (18, 30, 25), desc_rect, border_radius=10)
    pygame.draw.rect(surface, (45, 75, 60), desc_rect, width=1, border_radius=10)

    lore_hdr = tiny_font.render("БОТАНИЧЕСКАЯ ЗАМЕТКА:", True, (130, 195, 160))
    surface.blit(lore_hdr, (desc_rect.left + 12, desc_rect.top + 10))

    desc_lines = _render_wrapped_lines(c_data["desc"], tiny_font, desc_rect.width - 24)
    for l_idx, line in enumerate(desc_lines[:4]):
        line_t = tiny_font.render(line, True, (215, 235, 225))
        surface.blit(line_t, (desc_rect.left + 12, desc_rect.top + 32 + l_idx * 18))

    # Кнопка улучшения в модалке
    upg_btn_rect = None
    if level < 5:
        req_spr = c_data["req_sprouts"][level]
        can_upg = (sprouts >= req_spr)
        upg_btn_rect = pygame.Rect(modal_rect.left + 24, modal_rect.top + 332, left_w + 140, 48)
        u_hov = upg_btn_rect.collidepoint(mouse_pos) and can_upg

        if can_upg:
            u_bg = (55, 175, 95) if u_hov else (38, 135, 72)
            u_bd = (140, 255, 180) if u_hov else (90, 220, 130)
            btn_label = f"ВЗРАСТИТЬ ДО УР. {level + 1}  (НУЖНО {req_spr} САЖЕНЦЕВ)"
        else:
            u_bg = (32, 44, 38)
            u_bd = (60, 80, 70)
            btn_label = f"НУЖНО САЖЕНЦЕВ: {sprouts} / {req_spr}"

        pygame.draw.rect(surface, u_bg, upg_btn_rect, border_radius=10)
        pygame.draw.rect(surface, u_bd, upg_btn_rect, width=2, border_radius=10)
        lbl_t = small_font.render(btn_label, True, WHITE if can_upg else (145, 160, 150))
        surface.blit(lbl_t, (upg_btn_rect.centerx - lbl_t.get_width() // 2, upg_btn_rect.centery - lbl_t.get_height() // 2))
    else:
        max_b_rect = pygame.Rect(modal_rect.left + 24, modal_rect.top + 332, left_w + 140, 48)
        pygame.draw.rect(surface, (45, 38, 20), max_b_rect, border_radius=10)
        pygame.draw.rect(surface, GOLD, max_b_rect, width=2, border_radius=10)
        lbl_t = font.render("МАКСИМАЛЬНЫЙ УРОВЕНЬ", True, GOLD)
        surface.blit(lbl_t, (max_b_rect.centerx - lbl_t.get_width() // 2, max_b_rect.centery - lbl_t.get_height() // 2))

    # Правая колонка: Все 5 уровней прокачки
    right_x = modal_rect.left + 500
    right_w = 416
    r_hdr = font.render("ПЯТЬ СТУПЕНЕЙ РАЗВИТИЯ:", True, (240, 255, 245))
    surface.blit(r_hdr, (right_x, modal_rect.top + 60))

    for idx_lvl in range(5):
        tier_num = idx_lvl + 1
        tier_rect = pygame.Rect(right_x, modal_rect.top + 94 + idx_lvl * 90, right_w, 82)
        is_unl = (level >= tier_num)
        is_next = (level == tier_num - 1)

        if is_unl:
            t_bg = (24, 42, 34)
            t_bd = (70, 180, 120)
        elif is_next:
            t_bg = (30, 48, 40)
            t_bd = (255, 215, 60)
        else:
            t_bg = (18, 26, 22)
            t_bd = (40, 56, 48)

        pygame.draw.rect(surface, t_bg, tier_rect, border_radius=8)
        pygame.draw.rect(surface, t_bd, tier_rect, width=2 if (is_next or (is_unl and tier_num == 5)) else 1, border_radius=8)

        # Номер ступени
        badge_w = 74
        badge_rect = pygame.Rect(tier_rect.left + 8, tier_rect.top + 8, badge_w, 24)
        if is_unl:
            pygame.draw.rect(surface, (45, 125, 75), badge_rect, border_radius=5)
            b_txt = tiny_font.render(f"УР. {tier_num} OK", True, WHITE)
        elif is_next:
            pygame.draw.rect(surface, (140, 105, 25), badge_rect, border_radius=5)
            b_txt = tiny_font.render(f"УР. {tier_num} >", True, (255, 240, 180))
        else:
            pygame.draw.rect(surface, (32, 42, 38), badge_rect, border_radius=5)
            b_txt = tiny_font.render(f"УР. {tier_num}", True, (120, 135, 130))
        surface.blit(b_txt, (badge_rect.centerx - b_txt.get_width() // 2, badge_rect.centery - b_txt.get_height() // 2))

        # Требуемые саженцы
        req_val = c_data["req_sprouts"][idx_lvl]
        req_txt = tiny_font.render(f"Требует: {req_val} саж.", True, (160, 205, 180) if not is_unl else (120, 170, 140))
        surface.blit(req_txt, (tier_rect.right - req_txt.get_width() - 12, tier_rect.top + 12))

        # Текст эффекта ступени
        eff_desc = c_data["buff_desc"][idx_lvl]
        eff_lines = _render_wrapped_lines(eff_desc, tiny_font, right_w - 24)
        for l_i, line in enumerate(eff_lines[:2]):
            col = WHITE if is_unl else ((255, 235, 160) if is_next else (135, 150, 145))
            txt = tiny_font.render(line, True, col)
            surface.blit(txt, (tier_rect.left + 12, tier_rect.top + 38 + l_i * 18))

    return close_btn, upg_btn_rect


def draw_greenhouse_screen(surface, savedata, mouse_pos, inspected_cactus_id=None, bg_time=None):
    if bg_time is None:
        bg_time = pygame.time.get_ticks()
    generate_background(surface, bg_time, custom_cols=((16, 26, 22), (24, 40, 32)))

    # Верхняя панель
    top_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 70)
    pygame.draw.rect(surface, (22, 36, 30), top_rect)
    pygame.draw.line(surface, (45, 95, 65), (0, 70), (SCREEN_WIDTH, 70), 2)

    back_btn = pygame.Rect(20, 14, 150, 44)
    b_hov = back_btn.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (180, 45, 45) if b_hov else (145, 35, 35), back_btn, border_radius=8)
    pygame.draw.rect(surface, WHITE, back_btn, width=2, border_radius=8)
    b_txt = font.render("< НАЗАД [ESC]", True, WHITE)
    surface.blit(b_txt, (back_btn.centerx - b_txt.get_width() // 2, back_btn.centery - b_txt.get_height() // 2))

    # Кнопка Справка по Оранжерее
    info_btn = pygame.Rect(180, 14, 115, 44)
    inf_hov = info_btn.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (25, 75, 50) if inf_hov else (18, 52, 36), info_btn, border_radius=8)
    pygame.draw.rect(surface, (80, 220, 140) if inf_hov else (45, 140, 90), info_btn, width=1, border_radius=8)
    inf_txt = small_font.render("? ИНФО", True, (210, 255, 230))
    surface.blit(inf_txt, (info_btn.centerx - inf_txt.get_width() // 2, info_btn.centery - inf_txt.get_height() // 2))

    gh = savedata.get("Greenhouse", {})
    disc_count = sum(1 for c in GREENHOUSE_CACTI if gh.get(c["id"], {}).get("level", 0) > 0)
    total_sprouts = sum(gh.get(c["id"], {}).get("sprouts", 0) for c in GREENHOUSE_CACTI)

    # Заголовок по центру
    hdr_txt = large_font.render("ОРАНЖЕРЕЯ КАКТУСОВ", True, (130, 245, 175))
    surface.blit(hdr_txt, (SCREEN_WIDTH // 2 - hdr_txt.get_width() // 2, 8))

    sub_str = f"Коллекция флоры Оазиса: {disc_count} / {len(GREENHOUSE_CACTI)} видов выращено  |  Всего саженцев: {total_sprouts}"
    sub_txt = tiny_font.render(sub_str, True, (170, 220, 195))
    surface.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, 44))

    # Счётчики ресурсов справа
    st_panel = pygame.Rect(SCREEN_WIDTH - 296, 12, 136, 46)
    pygame.draw.rect(surface, (18, 28, 40), st_panel, border_radius=8)
    pygame.draw.rect(surface, GOLD, st_panel, width=1, border_radius=8)
    surface.blit(stellar_cactus_img_m, (st_panel.left + 8, st_panel.centery - 18))
    st_num = font.render(f"{savedata.get('StellarCactuses', 0)}", True, WHITE)
    surface.blit(st_num, (st_panel.left + 48, st_panel.centery - st_num.get_height() // 2))

    dark_panel = pygame.Rect(SCREEN_WIDTH - 150, 12, 136, 46)
    draw_dark_cactus_counter(surface, dark_panel, savedata, mouse_pos)

    # Сетка карточек кактусов (2 ряда по 4)
    upgrade_buttons = []
    card_rects = []

    card_w = 286
    card_h = 246

    for idx, c_data in enumerate(GREENHOUSE_CACTI):
        col = idx % 4
        row = idx // 4
        cx = 35 + col * 306
        cy = 78 + row * 254

        cid = c_data["id"]
        c_save = gh.get(cid, {"level": 0, "sprouts": 0})
        level = c_save.get("level", 0)
        sprouts = c_save.get("sprouts", 0)
        is_unl = (level > 0)

        card_rect = pygame.Rect(cx, cy, card_w, card_h)
        card_rects.append((cid, card_rect))
        cd_hov = card_rect.collidepoint(mouse_pos)

        # Оформление фона карточки
        if level == 5:
            bg_col = (34, 30, 20) if cd_hov else (28, 25, 18)
            bd_col = (255, 220, 80) if cd_hov else (210, 175, 55)
            bd_w = 2
        elif is_unl:
            bg_col = (28, 44, 36) if cd_hov else (22, 34, 28)
            bd_col = (90, 195, 140) if cd_hov else (55, 120, 85)
            bd_w = 2 if cd_hov else 1
        else:
            req_0 = c_data["req_sprouts"][0]
            if sprouts >= req_0:
                bg_col = (26, 40, 32) if cd_hov else (20, 32, 25)
                bd_col = (110, 230, 140)
                bd_w = 2
            else:
                bg_col = (18, 24, 22)
                bd_col = (42, 56, 50)
                bd_w = 1

        pygame.draw.rect(surface, bg_col, card_rect, border_radius=10)
        pygame.draw.rect(surface, bd_col, card_rect, width=bd_w, border_radius=10)

        # Рамка спрайта кактуса
        ibox = pygame.Rect(cx + 10, cy + 10, 72, 72)
        pygame.draw.rect(surface, (14, 22, 18), ibox, border_radius=8)
        pygame.draw.rect(surface, bd_col, ibox, width=1, border_radius=8)

        # Текстура кактуса
        raw_tex = gh_cacti_textures.get(c_data["img_key"])
        if raw_tex:
            if is_unl:
                surface.blit(raw_tex, (ibox.centerx - 32, ibox.centery - 32))
            else:
                # Силуэт для заблокированного
                d_surf = raw_tex.copy()
                d_surf.fill((45, 60, 52, 190), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(d_surf, (ibox.centerx - 32, ibox.centery - 32))
                q_txt = font.render("?", True, (130, 150, 140))
                surface.blit(q_txt, (ibox.centerx - q_txt.get_width() // 2, ibox.centery - q_txt.get_height() // 2))

        # Заголовок и уровень справа от иконки
        tx_x = cx + 90
        n_col = GOLD if level == 5 else (WHITE if is_unl else (160, 175, 170))
        name_font = small_font if font.size(c_data["name"])[0] > (card_w - 98) else font
        n_txt = name_font.render(c_data["name"], True, n_col)
        surface.blit(n_txt, (tx_x, cy + (12 if name_font == small_font else 10)))

        sub_col = (130, 200, 160) if is_unl else (105, 125, 115)
        s_txt = tiny_font.render(c_data["title"], True, sub_col)
        surface.blit(s_txt, (tx_x, cy + 34))

        # Бейдж уровня
        if level == 5:
            badge_t = tiny_font.render("МАКСИМУМ", True, GOLD)
        elif is_unl:
            badge_t = tiny_font.render(f"УРОВЕНЬ {level} / 5", True, (110, 245, 160))
        else:
            badge_t = tiny_font.render("НЕ ВЫРАЩЕН", True, (150, 160, 155))
        surface.blit(badge_t, (tx_x, cy + 56))

        # Разделитель
        pygame.draw.line(surface, (38, 62, 50), (cx + 10, cy + 88), (cx + card_w - 10, cy + 88), 1)

        # Название и описание бонуса
        bhdr = tiny_font.render(f"Дар: {c_data['buff_name']}", True, (255, 230, 130) if is_unl else (135, 150, 140))
        surface.blit(bhdr, (cx + 12, cy + 94))

        if is_unl:
            cur_desc = c_data["buff_desc"][level - 1]
            c_lines = _render_wrapped_lines(cur_desc, tiny_font, card_w - 24)
            for l_i, line in enumerate(c_lines[:2]):
                surface.blit(tiny_font.render(line, True, (230, 245, 238)), (cx + 12, cy + 116 + l_i * 18))

            if level < 5:
                nxt_desc = f"След. ур: {c_data['buff_desc'][level]}"
                nxt_lines = _render_wrapped_lines(nxt_desc, tiny_font, card_w - 24)
                if nxt_lines:
                    surface.blit(tiny_font.render(nxt_lines[0], True, (125, 205, 160)), (cx + 12, cy + 158))
        else:
            p_desc = f"При взращивании: {c_data['buff_desc'][0]}"
            p_lines = _render_wrapped_lines(p_desc, tiny_font, card_w - 24)
            for l_i, line in enumerate(p_lines[:3]):
                surface.blit(tiny_font.render(line, True, (135, 155, 145)), (cx + 12, cy + 116 + l_i * 18))

        # Подсказка подробностей
        det_hint = tiny_font.render("[Клик: подробнее]", True, (80, 140, 110) if cd_hov else (50, 95, 75))
        surface.blit(det_hint, (cx + card_w - det_hint.get_width() - 10, cy + 184))

        # Нижняя часть: Шкала саженцев и кнопка улучшения
        if level < 5:
            req_sprouts = c_data["req_sprouts"][level]
            can_upg = (sprouts >= req_sprouts)

            bar_rect = pygame.Rect(cx + 10, cy + 206, 136, 28)
            pygame.draw.rect(surface, (14, 22, 18), bar_rect, border_radius=6)
            fill_w = int(bar_rect.width * min(1.0, sprouts / req_sprouts))
            if fill_w > 0:
                fill_rect = pygame.Rect(bar_rect.left, bar_rect.top, fill_w, bar_rect.height)
                pygame.draw.rect(surface, (50, 180, 95) if can_upg else (35, 115, 65), fill_rect, border_radius=6)
            pygame.draw.rect(surface, (65, 120, 90), bar_rect, width=1, border_radius=6)

            # Текст саженцев
            surface.blit(sprout_icon_s, (bar_rect.left + 6, bar_rect.centery - 8))
            sp_txt = tiny_font.render(f"{sprouts} / {req_sprouts}", True, WHITE)
            surface.blit(sp_txt, (bar_rect.left + 26, bar_rect.centery - sp_txt.get_height() // 2))

            # Кнопка повышения
            upg_btn = pygame.Rect(cx + 152, cy + 204, 124, 32)
            u_hov = upg_btn.collidepoint(mouse_pos) and can_upg
            if can_upg:
                pygame.draw.rect(surface, (60, 185, 105) if u_hov else (42, 145, 80), upg_btn, border_radius=8)
                pygame.draw.rect(surface, (160, 255, 195) if u_hov else (100, 230, 145), upg_btn, width=2, border_radius=8)
                btn_txt_str = "ВЗРАСТИТЬ ↑" if level == 0 else "ПОВЫСИТЬ ↑"
                u_txt = small_font.render(btn_txt_str, True, WHITE)
                upgrade_buttons.append((cid, upg_btn))
            else:
                pygame.draw.rect(surface, (28, 38, 32), upg_btn, border_radius=8)
                pygame.draw.rect(surface, (50, 70, 60), upg_btn, width=1, border_radius=8)
                u_txt = tiny_font.render("МАЛО САЖЕНЦЕВ", True, (130, 145, 135))

            surface.blit(u_txt, (upg_btn.centerx - u_txt.get_width() // 2, upg_btn.centery - u_txt.get_height() // 2))
        else:
            m_bar = pygame.Rect(cx + 10, cy + 206, card_w - 20, 28)
            pygame.draw.rect(surface, (36, 32, 18), m_bar, border_radius=6)
            pygame.draw.rect(surface, GOLD, m_bar, width=1, border_radius=6)
            m_txt = tiny_font.render("МАКСИМАЛЬНЫЙ УРОВЕНЬ", True, GOLD)
            surface.blit(m_txt, (m_bar.centerx - m_txt.get_width() // 2, m_bar.centery - m_txt.get_height() // 2))

    # Нижняя панель итоговых бонусов
    bot_rect = pygame.Rect(35, 592, 1210, 116)
    pygame.draw.rect(surface, (20, 32, 26), bot_rect, border_radius=12)
    pygame.draw.rect(surface, (52, 105, 78), bot_rect, width=1, border_radius=12)

    gh_buffs = get_greenhouse_buffs(savedata)
    active_chips = []

    if gh_buffs.get("base_hp", 0) > 0:
        active_chips.append(f"+{gh_buffs['base_hp']} HP базы")
    if gh_buffs.get("start_gold", 0) > 0:
        active_chips.append(f"+{gh_buffs['start_gold']} кактусов на старте")
    if gh_buffs.get("bounty_mult", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['bounty_mult']*100)}% семян за мобов")
    if gh_buffs.get("farm_mult", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['farm_mult']*100)}% доход ферм")
    if gh_buffs.get("fire_dmg_mult", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['fire_dmg_mult']*100)}% урон Огня")
    if gh_buffs.get("frost_slow_mult", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['frost_slow_mult']*100)}% замедление")
    if gh_buffs.get("frost_range_mult", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['frost_range_mult']*100)}% радиус Льда")
    if gh_buffs.get("armor_shred", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['armor_shred']*100)}% пробив брони")
    if gh_buffs.get("extra_jumps", 0) > 0:
        active_chips.append(f"+{gh_buffs['extra_jumps']} отскока Теслы")
    if gh_buffs.get("tesla_dmg_mult", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['tesla_dmg_mult']*100)}% урон Теслы")
    if gh_buffs.get("stun_chance", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['stun_chance']*100)}% оглушение")
    if gh_buffs.get("void_dmg_mult", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['void_dmg_mult']*100)}% урон Бездны")
    if gh_buffs.get("pierce_magic", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['pierce_magic']*100)}% пробив щита")
    if gh_buffs.get("drone_dmg_mult", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['drone_dmg_mult']*100)}% урон Дрона")
    if gh_buffs.get("drone_spd_mult", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['drone_spd_mult']*100)}% скор. Дрона")
    if gh_buffs.get("soldier_hp_mult", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['soldier_hp_mult']*100)}% HP солдат")
    if gh_buffs.get("soldier_dmg_mult", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['soldier_dmg_mult']*100)}% урон солдат")
    if gh_buffs.get("compost_dmg_mult", 0) > 0:
        active_chips.append(f"+{int(gh_buffs['compost_dmg_mult']*100)}% Компост")
    if gh_buffs.get("magma_burst"):
        active_chips.append("Взрыв магмы")
    if gh_buffs.get("permafrost"):
        active_chips.append("Вечная мерзлота")
    if gh_buffs.get("dual_drone"):
        active_chips.append("Двойной Дрон")
    if gh_buffs.get("soldier_thorns"):
        active_chips.append("Шипы воинов")
    if gh_buffs.get("soldier_shield"):
        active_chips.append("Щит воинов")

    bh_txt = font.render("АКТИВНЫЕ БОНУСЫ ОРАНЖЕРЕИ (ДЕЙСТВУЮТ ВО ВСЕХ БИТВАХ):", True, (140, 245, 180))
    surface.blit(bh_txt, (bot_rect.left + 16, bot_rect.top + 10))

    if active_chips:
        chip_x = bot_rect.left + 16
        chip_y = bot_rect.top + 40
        for chip in active_chips:
            c_txt = tiny_font.render(chip, True, (240, 255, 245))
            c_w = c_txt.get_width() + 16
            if chip_x + c_w > bot_rect.right - 16:
                chip_x = bot_rect.left + 16
                chip_y += 26
            c_rect = pygame.Rect(chip_x, chip_y, c_w, 22)
            pygame.draw.rect(surface, (32, 54, 44), c_rect, border_radius=6)
            pygame.draw.rect(surface, (70, 150, 105), c_rect, width=1, border_radius=6)
            surface.blit(c_txt, (chip_x + 8, chip_y + 3))
            chip_x += c_w + 8
    else:
        empty_t = tiny_font.render("Вырастите первый кактус (Сагуаро доступен на 1 уровне!), чтобы активировать постоянные бонусы флоры.", True, (160, 180, 170))
        surface.blit(empty_t, (bot_rect.left + 16, bot_rect.top + 44))

    hint_str = "Саженцы добываются при победе над боссами (волны 25, 50, 75, 100...) и при разрушении метеоритов."
    h_t = tiny_font.render(hint_str, True, (130, 175, 150))
    surface.blit(h_t, (bot_rect.left + 16, bot_rect.bottom - 24))

    # Модальное окно просмотра/прокачки кактуса
    modal_close_btn = None
    modal_upg_btn = None
    if inspected_cactus_id is not None:
        modal_close_btn, modal_upg_btn = draw_greenhouse_modal(surface, inspected_cactus_id, savedata, mouse_pos)

    return back_btn, upgrade_buttons, card_rects, modal_close_btn, modal_upg_btn, info_btn


def _get_bestiary_card_texts(slime, is_boss, max_txt_w):
    key = slime["id"]
    cached = _bestiary_card_cache.get(key)
    if cached is not None:
        return cached

    title_color = (255, 215, 80) if is_boss else WHITE
    nm_surf = font.render(slime["name"], True, title_color)
    sub_nm = tiny_font.render(f"- {slime['title']}", True, (210, 150, 255) if is_boss else (140, 190, 235))

    b_dmg = slime.get("base_damage", 1)
    dmg_lbl = "∞ (Поражение)" if (is_boss or b_dmg == "∞") else f"{b_dmg} HP"
    if is_boss:
        stat_str = f"HP: {slime['base_hp']}  |  Урон базе: {dmg_lbl}"
    else:
        spd_val = slime['speed'].split()[0] if ' ' in slime['speed'] else slime['speed']
        stat_str = f"HP: {slime['base_hp']}  |  Урон базе: {dmg_lbl}  |  Скор: {spd_val}"
    stat_surf = tiny_font.render(stat_str, True, (240, 180, 120))

    spec_str = f"Особенность: {slime['special']}"
    while tiny_font.size(spec_str)[0] > max_txt_w and len(spec_str) > 12:
        spec_str = spec_str[:-2] + "…"
    spec_surf = tiny_font.render(spec_str, True, (160, 240, 180) if is_boss else (180, 210, 240))

    desc_str = slime.get("desc", "")
    while tiny_font.size(desc_str)[0] > max_txt_w and len(desc_str) > 12:
        desc_str = desc_str[:-2] + "…"
    desc_surf = tiny_font.render(desc_str, True, (140, 155, 175))

    cached = (nm_surf, sub_nm, stat_surf, spec_surf, desc_surf)
    _bestiary_card_cache[key] = cached
    return cached


def _get_unknown_slime_texts():
    global _unknown_slime_texts
    if _unknown_slime_texts is None:
        q_txt = massive_font.render("?", True, (80, 95, 115))
        nm_surf = font.render("Неизвестный Слайм", True, (110, 125, 140))
        un_desc = tiny_font.render("Победите в бою для изучения в бестиарии.", True, (100, 115, 135))
        c_lbl = tiny_font.render("ЗАКРЫТО", True, (110, 120, 130))
        _unknown_slime_texts = (q_txt, nm_surf, un_desc, c_lbl)
    return _unknown_slime_texts


def _get_bestiary_btn_label(label_type):
    surf = _bestiary_btn_cache.get(label_type)
    if surf is not None:
        return surf
    if label_type == "claimed":
        surf = tiny_font.render("ПОЛУЧЕНО  OK", True, (130, 200, 150))
    elif label_type == "boss_reward":
        surf = tiny_font.render("+5 ЗВЁЗД  +1 ТЁМН.", True, WHITE)
    elif label_type == "normal_reward":
        surf = tiny_font.render("+2 ЗВЁЗДЫ  ЗАБРАТЬ", True, WHITE)
    _bestiary_btn_cache[label_type] = surf
    return surf


def draw_bestiary_screen(surface, savedata, mouse_pos, scroll_y=0, bg_time=None):
    if bg_time is None:
        bg_time = pygame.time.get_ticks()
    generate_background(surface, bg_time, custom_cols=((16, 20, 28), (22, 28, 40)))

    top_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 70)
    pygame.draw.rect(surface, (20, 26, 38), top_rect)
    pygame.draw.line(surface, (45, 60, 85), (0, 70), (SCREEN_WIDTH, 70), 2)

    back_btn = pygame.Rect(20, 14, 160, 44)
    b_hov = back_btn.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (180, 45, 45) if b_hov else (145, 35, 35), back_btn, border_radius=8)
    pygame.draw.rect(surface, WHITE, back_btn, width=2, border_radius=8)
    b_txt = font.render("< НАЗАД [ESC]", True, WHITE)
    surface.blit(b_txt, (back_btn.centerx - b_txt.get_width() // 2, back_btn.centery - b_txt.get_height() // 2))

    st_panel = pygame.Rect(SCREEN_WIDTH - 296, 12, 136, 46)
    pygame.draw.rect(surface, (22, 30, 44), st_panel, border_radius=8)
    pygame.draw.rect(surface, GOLD, st_panel, width=1, border_radius=8)
    surface.blit(stellar_cactus_img_m, (st_panel.left + 8, st_panel.centery - 18))
    st_num = font.render(f"{savedata.get('StellarCactuses', 0)}", True, WHITE)
    surface.blit(st_num, (st_panel.left + 48, st_panel.centery - st_num.get_height() // 2))

    dark_panel = pygame.Rect(SCREEN_WIDTH - 150, 12, 136, 46)
    draw_dark_cactus_counter(surface, dark_panel, savedata, mouse_pos)

    hdr_txt = large_font.render("БЕСТИАРИЙ СЛАЙМОВ", True, (240, 255, 245))
    surface.blit(hdr_txt, (SCREEN_WIDTH // 2 - hdr_txt.get_width() // 2, 8))

    discovered = savedata.get("BestiaryDiscovered", [1])
    claimed = savedata.get("BestiaryClaimed", {})

    sub_txt = tiny_font.render(f"Изучено слаймов: {len(discovered)} / {len(BESTIARY_DATA)}  |  Награды: +2 Звёздных кактуса за обычных, +5 Звёздных и +1 Тёмный за боссов!", True, (160, 190, 220))
    surface.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, 44))

    view_rect = pygame.Rect(0, 72, SCREEN_WIDTH, SCREEN_HEIGHT - 72)
    surface.set_clip(view_rect)

    claim_buttons = []
    card_w = 580
    card_h = 106

    for idx, slime in enumerate(BESTIARY_DATA):
        col = idx % 2
        row = idx // 2
        cx = 38 + col * 610
        cy = 85 + row * 118 - scroll_y

        is_disc = (slime["id"] in discovered)
        is_boss = slime.get("is_boss", False)
        is_claimed = (slime["id"] in claimed) if isinstance(claimed, list) else bool(claimed.get(str(slime["id"]), False))

        card_rect = pygame.Rect(cx, cy, card_w, card_h)
        cd_hov = card_rect.collidepoint(mouse_pos)

        if not is_disc:
            bg_col = (18, 22, 28)
            bd_col = (45, 52, 65)
        elif is_boss:
            bg_col = (34, 18, 38) if cd_hov else (26, 14, 30)
            bd_col = (210, 80, 255) if cd_hov else (140, 45, 180)
        else:
            bg_col = (24, 34, 48) if cd_hov else (18, 26, 38)
            bd_col = (75, 160, 235) if cd_hov else (45, 75, 110)

        pygame.draw.rect(surface, bg_col, card_rect, border_radius=10)
        pygame.draw.rect(surface, bd_col, card_rect, width=2 if is_boss else 1, border_radius=10)

        p_box = pygame.Rect(cx + 12, cy + 12, 82, 82)
        pygame.draw.rect(surface, (14, 18, 24), p_box, border_radius=8)
        pygame.draw.rect(surface, bd_col, p_box, width=1, border_radius=8)

        if is_disc:
            scaled_tex = _bestiary_slime_icon_cache.get(slime["img_key"])
            if scaled_tex is None:
                raw_tex = get_slime_texture(slime["img_key"])
                scaled_tex = pygame.transform.scale(raw_tex, (60, 60))
                _bestiary_slime_icon_cache[slime["img_key"]] = scaled_tex
            surface.blit(scaled_tex, (p_box.centerx - 30, p_box.centery - 30))

            btn_w = 145
            btn_h = 34
            btn_rect = pygame.Rect(card_rect.right - btn_w - 12, card_rect.centery - btn_h // 2, btn_w, btn_h)
            max_txt_w = btn_rect.left - (cx + 104) - 10

            nm_surf, sub_nm, stat_surf, spec_surf, desc_surf = _get_bestiary_card_texts(slime, is_boss, max_txt_w)
            surface.blit(nm_surf, (cx + 104, cy + 10))
            surface.blit(sub_nm, (cx + 104 + nm_surf.get_width() + 8, cy + 13))
            surface.blit(stat_surf, (cx + 104, cy + 34))
            surface.blit(spec_surf, (cx + 104, cy + 54))
            surface.blit(desc_surf, (cx + 104, cy + 74))

            if is_claimed:
                pygame.draw.rect(surface, (28, 42, 34), btn_rect, border_radius=6)
                pygame.draw.rect(surface, (50, 95, 65), btn_rect, width=1, border_radius=6)
                c_lbl = _get_bestiary_btn_label("claimed")
                surface.blit(c_lbl, (btn_rect.centerx - c_lbl.get_width() // 2, btn_rect.centery - c_lbl.get_height() // 2))
            else:
                b_hov_btn = btn_rect.collidepoint(mouse_pos)
                if is_boss:
                    pygame.draw.rect(surface, (145, 45, 210) if b_hov_btn else (110, 30, 165), btn_rect, border_radius=6)
                    pygame.draw.rect(surface, (230, 160, 255), btn_rect, width=1, border_radius=6)
                    c_lbl = _get_bestiary_btn_label("boss_reward")
                else:
                    pygame.draw.rect(surface, (215, 145, 25) if b_hov_btn else (175, 115, 20), btn_rect, border_radius=6)
                    pygame.draw.rect(surface, GOLD, btn_rect, width=1, border_radius=6)
                    c_lbl = _get_bestiary_btn_label("normal_reward")
                surface.blit(c_lbl, (btn_rect.centerx - c_lbl.get_width() // 2, btn_rect.centery - c_lbl.get_height() // 2))
                claim_buttons.append((slime["id"], btn_rect, 5 if is_boss else 2, 1 if is_boss else 0))
        else:
            q_txt, nm_surf, un_desc, c_lbl = _get_unknown_slime_texts()
            surface.blit(q_txt, (p_box.centerx - q_txt.get_width() // 2, p_box.centery - q_txt.get_height() // 2))
            surface.blit(nm_surf, (cx + 104, cy + 18))
            surface.blit(un_desc, (cx + 104, cy + 46))

            btn_w = 145
            btn_h = 34
            btn_rect = pygame.Rect(card_rect.right - btn_w - 12, card_rect.centery - btn_h // 2, btn_w, btn_h)
            pygame.draw.rect(surface, (28, 32, 40), btn_rect, border_radius=6)
            pygame.draw.rect(surface, (50, 56, 68), btn_rect, width=1, border_radius=6)
            surface.blit(lock_icon, (btn_rect.centerx - 38, btn_rect.centery - 8))
            surface.blit(c_lbl, (btn_rect.centerx - 16, btn_rect.centery - c_lbl.get_height() // 2))

    surface.set_clip(None)

    total_rows = (len(BESTIARY_DATA) + 1) // 2
    total_content_h = 85 + total_rows * 118 + 20
    max_b_scroll = max(0, total_content_h - (SCREEN_HEIGHT - 72))

    if max_b_scroll > 0:
        bar_area_h = SCREEN_HEIGHT - 76
        bar_h = max(35, int(bar_area_h * (bar_area_h / total_content_h)))
        bar_y = 74 + int((bar_area_h - bar_h) * (scroll_y / max_b_scroll))
        pygame.draw.rect(surface, (24, 34, 48), (SCREEN_WIDTH - 12, 74, 8, bar_area_h), border_radius=4)
        pygame.draw.rect(surface, (70, 140, 210), (SCREEN_WIDTH - 12, bar_y, 8, bar_h), border_radius=4)

    return back_btn, claim_buttons, max_b_scroll


def draw_map_selection_screen(surface, game_map, current_offset, savedata, mouse_pos):
    # 1. Верхняя панель: счётчики ресурсов, центрированный заголовок и Опции в правом углу
    st_panel = pygame.Rect(24, 20, 110, 48)
    pygame.draw.rect(surface, (18, 28, 40), st_panel, border_radius=8)
    pygame.draw.rect(surface, GOLD, st_panel, width=2, border_radius=8)
    surface.blit(stellar_cactus_img_m, (st_panel.left + 8, st_panel.centery - 18))
    st_txt = font.render(f"{savedata.get('StellarCactuses', 0)}", True, WHITE)
    surface.blit(st_txt, (st_panel.left + 46, st_panel.centery - st_txt.get_height() // 2))

    dark_panel = pygame.Rect(144, 20, 110, 48)
    draw_dark_cactus_counter(surface, dark_panel, savedata, mouse_pos)

    # Кнопка возврата в Главное Меню
    menu_btn_rect = pygame.Rect(SCREEN_WIDTH - 150, 20, 126, 48)
    m_hov = menu_btn_rect.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (150, 45, 45) if m_hov else (100, 30, 30), menu_btn_rect, border_radius=8)
    pygame.draw.rect(surface, (255, 120, 120) if m_hov else (180, 60, 60), menu_btn_rect, width=2, border_radius=8)
    m_txt = small_font.render("< МЕНЮ [ESC]", True, WHITE)
    surface.blit(m_txt, (menu_btn_rect.centerx - m_txt.get_width() // 2, menu_btn_rect.centery - m_txt.get_height() // 2))

    # Кнопка Справка / Механики
    guide_btn_rect = pygame.Rect(SCREEN_WIDTH - 298, 20, 138, 48)
    g_hov = guide_btn_rect.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (30, 75, 110) if g_hov else (20, 50, 78), guide_btn_rect, border_radius=8)
    pygame.draw.rect(surface, (90, 200, 255) if g_hov else (50, 140, 190), guide_btn_rect, width=2, border_radius=8)
    g_txt = small_font.render("? МЕХАНИКИ", True, (220, 245, 255))
    surface.blit(g_txt, (guide_btn_rect.centerx - g_txt.get_width() // 2, guide_btn_rect.centery - g_txt.get_height() // 2))

    # Свободный, гордый центрированный заголовок
    title_shadow = large_font.render("ВЫБОР КАРТЫ", True, (10, 20, 15))
    title = large_font.render("ВЫБОР КАРТЫ", True, (240, 255, 245))
    tx = SCREEN_WIDTH // 2 - title.get_width() // 2
    surface.blit(title_shadow, (tx + 2, 26))
    surface.blit(title, (tx, 24))

    # 2. Прямоугольники кнопок нижнего командного мостика (3x3 идеальная симметрия)
    # Левая колонка (под Картой 1): Таланты, Оранжерея, Реликвии
    upg_btn_rect        = pygame.Rect(95, 492, 340, 48)
    greenhouse_btn_rect = pygame.Rect(95, 546, 340, 48)
    relics_btn_rect     = pygame.Rect(95, 600, 340, 48)

    # Правая колонка (под Картой 3): Бестиарий, Достижения, Опции
    bestiary_btn_rect   = pygame.Rect(835, 492, 340, 48)
    ach_btn_rect        = pygame.Rect(835, 546, 340, 48)
    settings_btn_rect   = pygame.Rect(835, 600, 340, 48)

    upg_hover = upg_btn_rect.collidepoint(mouse_pos)
    gh_hover  = greenhouse_btn_rect.collidepoint(mouse_pos)
    relics_hover = relics_btn_rect.collidepoint(mouse_pos)
    bes_hover = bestiary_btn_rect.collidepoint(mouse_pos)
    ach_hover = ach_btn_rect.collidepoint(mouse_pos)
    settings_hover = settings_btn_rect.collidepoint(mouse_pos)

    # Карточки карт в стильном аркадном оформлении
    visible_maps = [current_offset + i for i in range(3) if 0 <= current_offset + i < len(MAP_NAMES_LIST)]
    map_rects = []
    info_btn_rects = []

    for i, mid in enumerate(visible_maps):
        x_pos = 95 + i * 370
        y_pos = 98
        card_w = 340
        card_h = 368
        is_selected = (game_map == mid)
        biome = MAP_BIOMES_DATA.get(mid, MAP_BIOMES_DATA[0])
        unlocked, lock_reason = is_map_unlocked(mid, savedata)

        card_container = pygame.Rect(x_pos, y_pos, card_w, card_h)
        c_hover = card_container.collidepoint(mouse_pos)

        # Фон и окантовка карточки в глубокой аркадной теме
        if not unlocked:
            bg_col = (18, 20, 28)
            border_col = (130, 60, 60) if c_hover else (50, 56, 68)
            border_w = 2
        elif is_selected:
            bg_col = (20, 32, 46)
            border_col = (70, 235, 110)
            border_w = 3
        else:
            bg_col = (20, 28, 40)
            border_col = (100, 170, 240) if c_hover else (52, 72, 98)
            border_w = 2

        pygame.draw.rect(surface, bg_col, card_container, border_radius=12)
        pygame.draw.rect(surface, border_col, card_container, width=border_w, border_radius=12)

        # Акцентная кайма сверху в цвет сложности карты
        accent_col = biome["diff_color"] if unlocked else (70, 76, 88)
        pygame.draw.line(surface, accent_col, (x_pos + 14, y_pos + 2), (x_pos + card_w - 14, y_pos + 2), 2)

        # Шапка карточки: Номер, Название и Бейдж сложности
        name_str = f"{mid + 1}. {biome['name']}"
        m_num_txt = font.render(name_str, True, WHITE if unlocked else (120, 130, 140))
        surface.blit(m_num_txt, (x_pos + 14, y_pos + 11))

        # Бейдж сложности
        diff_w = 78
        diff_h = 22
        diff_rect = pygame.Rect(x_pos + card_w - diff_w - 14, y_pos + 10, diff_w, diff_h)
        pygame.draw.rect(surface, (26, 34, 46) if unlocked else (22, 24, 30), diff_rect, border_radius=6)
        pygame.draw.rect(surface, accent_col, diff_rect, width=1, border_radius=6)
        d_lbl = tiny_font.render(biome["diff_label"], True, accent_col)
        surface.blit(d_lbl, (diff_rect.centerx - d_lbl.get_width() // 2, diff_rect.centery - d_lbl.get_height() // 2))

        # Кнопка [ ℹ ИНФО ] в шапке карточки (стильный компактный чип)
        info_btn_w = 68
        info_btn_rect = pygame.Rect(diff_rect.left - info_btn_w - 6, y_pos + 10, info_btn_w, diff_h)
        inf_hov = info_btn_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (40, 75, 115) if inf_hov else (24, 38, 56), info_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (100, 210, 255) if inf_hov else (52, 88, 128), info_btn_rect, width=1, border_radius=6)
        surface.blit(info_icon_s, (info_btn_rect.left + 6, info_btn_rect.centery - 8))
        inf_lbl = tiny_font.render("ИНФО", True, (210, 240, 255) if inf_hov else (165, 200, 235))
        surface.blit(inf_lbl, (info_btn_rect.left + 26, info_btn_rect.centery - inf_lbl.get_height() // 2))
        info_btn_rects.append((mid, info_btn_rect))

        # Сочная увеличенная мини-карта биома (высота 148px)
        mm_x = x_pos + 14
        mm_y = y_pos + 38
        mm_w = card_w - 28
        mm_h = 148
        draw_minimap(surface, path_list[mid], tower_slots_list[mid], mm_x, mm_y, mm_w, mm_h, is_selected, map_id=mid, is_unlocked=unlocked)

        # Подзаголовок биома (чистая атмосфера)
        sub_str = f"Биом: {biome['sub']}"
        sub_txt = tiny_font.render(sub_str, True, (160, 195, 225) if unlocked else (105, 115, 125))
        surface.blit(sub_txt, (x_pos + card_w // 2 - sub_txt.get_width() // 2, y_pos + 192))

        # Рубежи мастерства (4 звезды: 15, 30, 50, 75 волн)
        rec = savedata["LevelsRecords"][mid]
        stars_lbl = tiny_font.render("РУБЕЖИ:", True, (140, 165, 195) if unlocked else (90, 95, 105))
        surface.blit(stars_lbl, (x_pos + 14, y_pos + 219))

        for s_idx, (mw, rew, rank) in enumerate(get_map_mastery_milestones(mid)):
            achieved = (rec >= mw)
            star_box = pygame.Rect(x_pos + 72 + s_idx * 63, y_pos + 215, 58, 24)
            sb_hov = star_box.collidepoint(mouse_pos)
            if achieved:
                pygame.draw.rect(surface, (60, 48, 20) if sb_hov else (46, 36, 14), star_box, border_radius=6)
                pygame.draw.rect(surface, (255, 235, 130) if sb_hov else GOLD, star_box, width=2 if sb_hov else 1, border_radius=6)
                surface.blit(stellar_cactus_img_xs, (star_box.left + 3, star_box.centery - 9))
                s_txt = tiny_font.render(f"{mw}в", True, (255, 225, 110))
                surface.blit(s_txt, (star_box.left + 23, star_box.centery - s_txt.get_height() // 2))
            else:
                pygame.draw.rect(surface, (26, 34, 46) if sb_hov else (16, 22, 32), star_box, border_radius=6)
                pygame.draw.rect(surface, (70, 95, 125) if sb_hov else (44, 56, 72), star_box, width=1, border_radius=6)
                s_txt = tiny_font.render(f"{mw}в", True, (160, 185, 205) if sb_hov else (105, 120, 135))
                surface.blit(s_txt, (star_box.centerx - s_txt.get_width() // 2, star_box.centery - s_txt.get_height() // 2))

            if sb_hov:
                txt_prefix = f"{rank}: {mw} волна (+{rew}"
                tt_txt = tiny_font.render(txt_prefix, True, (255, 235, 130) if achieved else (200, 220, 240))
                tt_close = tiny_font.render(")", True, (255, 235, 130) if achieved else (200, 220, 240))
                icon_w = stellar_cactus_img_xs.get_width()
                tt_w = tt_txt.get_width() + icon_w + tt_close.get_width() + 18
                tt_h = 24
                tt_x = max(10, min(SCREEN_WIDTH - tt_w - 10, star_box.centerx - tt_w // 2))
                tt_y = star_box.top - 28
                pygame.draw.rect(surface, (14, 18, 26), (tt_x, tt_y, tt_w, tt_h), border_radius=6)
                pygame.draw.rect(surface, GOLD if achieved else (60, 90, 130), (tt_x, tt_y, tt_w, tt_h), width=1, border_radius=6)
                cur_draw_x = tt_x + 8
                surface.blit(tt_txt, (cur_draw_x, tt_y + 12 - tt_txt.get_height() // 2))
                cur_draw_x += tt_txt.get_width() + 3
                surface.blit(stellar_cactus_img_xs, (cur_draw_x, tt_y + 12 - stellar_cactus_img_xs.get_height() // 2))
                cur_draw_x += icon_w + 1
                surface.blit(tt_close, (cur_draw_x, tt_y + 12 - tt_close.get_height() // 2))

        # Нижняя плашка: Рекорд, выбор карты и кнопка анализа волн
        bot_rect = pygame.Rect(x_pos + 14, y_pos + 250, card_w - 28, 104)
        if not unlocked:
            pygame.draw.rect(surface, (36, 18, 22), bot_rect, border_radius=8)
            pygame.draw.rect(surface, (160, 48, 58), bot_rect, width=1, border_radius=8)
            surface.blit(lock_icon, (bot_rect.left + 10, bot_rect.top + 10))
            l_hdr = tiny_font.render("КАРТА ЗАБЛОКИРОВАНА", True, (255, 95, 95))
            surface.blit(l_hdr, (bot_rect.left + 32, bot_rect.top + 9))
            l_req = tiny_font.render(lock_reason, True, (240, 180, 180))
            surface.blit(l_req, (bot_rect.left + 10, bot_rect.top + 34))

            # Кнопка инфо для заблокированной карты
            lock_info_btn = pygame.Rect(bot_rect.left + 10, bot_rect.top + 62, bot_rect.width - 20, 32)
            li_hov = lock_info_btn.collidepoint(mouse_pos)
            pygame.draw.rect(surface, (48, 24, 30) if li_hov else (30, 18, 22), lock_info_btn, border_radius=6)
            pygame.draw.rect(surface, (180, 70, 85) if li_hov else (90, 36, 45), lock_info_btn, width=1, border_radius=6)
            surface.blit(info_icon_s, (lock_info_btn.left + 8, lock_info_btn.centery - 8))
            li_txt = tiny_font.render("Мутаторы и информация карты >", True, (255, 200, 210) if li_hov else (190, 140, 150))
            surface.blit(li_txt, (lock_info_btn.left + 30, lock_info_btn.centery - li_txt.get_height() // 2))
            info_btn_rects.append((mid, lock_info_btn))
        else:
            pygame.draw.rect(surface, (16, 25, 37), bot_rect, border_radius=8)
            pygame.draw.rect(surface, (42, 72, 105), bot_rect, width=1, border_radius=8)

            # Верхняя строка: Рекорд слева, Кнопка ВЫБРАТЬ справа
            rec_str = f"Рекорд: {rec} волн"
            rec_txt = small_font.render(rec_str, True, (255, 195, 65))
            surface.blit(rec_txt, (bot_rect.left + 10, bot_rect.top + 18 - rec_txt.get_height() // 2))

            if is_selected:
                sel_w, sel_h = 104, 30
                sel_rect = pygame.Rect(bot_rect.right - sel_w - 10, bot_rect.top + 8, sel_w, sel_h)
                pygame.draw.rect(surface, (38, 190, 80), sel_rect, border_radius=6)
                pygame.draw.rect(surface, (160, 255, 185), sel_rect, width=1, border_radius=6)
                sel_txt = tiny_font.render("ВЫБРАНО", True, WHITE)
                surface.blit(sel_txt, (sel_rect.centerx - sel_txt.get_width() // 2, sel_rect.centery - sel_txt.get_height() // 2))
            else:
                btn_w, btn_h = 104, 30
                sel_rect = pygame.Rect(bot_rect.right - btn_w - 10, bot_rect.top + 8, btn_w, btn_h)
                pygame.draw.rect(surface, (38, 76, 118) if c_hover else (26, 48, 76), sel_rect, border_radius=6)
                pygame.draw.rect(surface, (95, 175, 255) if c_hover else (52, 98, 152), sel_rect, width=1, border_radius=6)
                sel_txt = tiny_font.render("ВЫБРАТЬ", True, (220, 240, 255))
                surface.blit(sel_txt, (sel_rect.centerx - sel_txt.get_width() // 2, sel_rect.centery - sel_txt.get_height() // 2))

            # Нижняя строка: Кнопка «АНАЛИЗ ВОЛН» или «НАСТРОЙКА КАРТЫ» для карты 10
            wave_info_btn = pygame.Rect(bot_rect.left + 10, bot_rect.top + 48, bot_rect.width - 20, 44)
            wi_hov = wave_info_btn.collidepoint(mouse_pos)
            if mid == 9:
                pygame.draw.rect(surface, (70, 32, 95) if wi_hov else (44, 20, 62), wave_info_btn, border_radius=6)
                pygame.draw.rect(surface, (255, 120, 220) if wi_hov else (190, 75, 175), wave_info_btn, width=2 if wi_hov else 1, border_radius=6)
                c_seed = savedata.get("CustomMapConfig", {}).get("seed", 777)
                wi_t = font.render("НАСТРОИТЬ КАРТУ", True, (255, 235, 255) if wi_hov else (245, 195, 240))
                surface.blit(wi_t, (wave_info_btn.left + 32, wave_info_btn.top + 5))
                wi_sub = tiny_font.render(f"Сид: {c_seed}  |  Генерация и параметры мира >", True, (255, 200, 245) if wi_hov else (200, 150, 200))
                surface.blit(wi_sub, (wave_info_btn.left + 32, wave_info_btn.top + 24))
            else:
                pygame.draw.rect(surface, (28, 52, 80) if wi_hov else (20, 34, 52), wave_info_btn, border_radius=6)
                pygame.draw.rect(surface, (90, 205, 255) if wi_hov else (45, 78, 115), wave_info_btn, width=1, border_radius=6)
                surface.blit(info_icon_s, (wave_info_btn.left + 10, wave_info_btn.centery - 8))
                wi_t = font.render("АНАЛИЗ ВОЛН", True, (225, 245, 255) if wi_hov else (175, 215, 250))
                surface.blit(wi_t, (wave_info_btn.left + 32, wave_info_btn.top + 5))
                wi_sub = tiny_font.render("Слаймы, HP, скорость и награды >", True, (130, 185, 235) if wi_hov else (95, 135, 175))
                surface.blit(wi_sub, (wave_info_btn.left + 32, wave_info_btn.top + 24))
            info_btn_rects.append((mid, wave_info_btn))

        map_rects.append((mid, card_container))

    # Стрелки прокрутки карт
    l_arr_rect = pygame.Rect(18, 240, 56, 72)
    r_arr_rect = pygame.Rect(SCREEN_WIDTH - 74, 240, 56, 72)
    l_hov = l_arr_rect.collidepoint(mouse_pos)
    r_hov = r_arr_rect.collidepoint(mouse_pos)

    if current_offset > 0:
        pygame.draw.rect(surface, (35, 62, 92) if l_hov else (20, 34, 52), l_arr_rect, border_radius=10)
        pygame.draw.rect(surface, (85, 160, 240) if l_hov else (48, 85, 128), l_arr_rect, width=2, border_radius=10)
        l_arr = massive_font.render("<", True, WHITE)
        surface.blit(l_arr, (l_arr_rect.centerx - l_arr.get_width() // 2, l_arr_rect.centery - l_arr.get_height() // 2 - 2))

    if current_offset + 3 < len(MAP_NAMES_LIST):
        pygame.draw.rect(surface, (35, 62, 92) if r_hov else (20, 34, 52), r_arr_rect, border_radius=10)
        pygame.draw.rect(surface, (85, 160, 240) if r_hov else (48, 85, 128), r_arr_rect, width=2, border_radius=10)
        r_arr = massive_font.render(">", True, WHITE)
        surface.blit(r_arr, (r_arr_rect.centerx - r_arr.get_width() // 2, r_arr_rect.centery - r_arr.get_height() // 2 - 2))

    # Индикатор страниц [ ● ○ ○ ]
    total_pages = max(1, (len(MAP_NAMES_LIST) + 2) // 3)
    cur_page = current_offset // 3
    dot_rects = []
    dot_y = 472
    start_dot_x = SCREEN_WIDTH // 2 - ((total_pages - 1) * 28) // 2
    for p in range(total_pages):
        dx = start_dot_x + p * 28
        d_rect = pygame.Rect(dx - 12, dot_y - 12, 24, 24)
        dot_rects.append((p, d_rect))
        is_cur = (p == cur_page)
        d_hov = d_rect.collidepoint(mouse_pos)
        if is_cur:
            pygame.draw.circle(surface, (255, 215, 60), (dx, dot_y), 6)
            pygame.draw.circle(surface, WHITE, (dx, dot_y), 8, width=1)
        else:
            dot_col = (130, 180, 230) if d_hov else (45, 65, 88)
            pygame.draw.circle(surface, dot_col, (dx, dot_y), 4)
            pygame.draw.circle(surface, (70, 95, 125), (dx, dot_y), 5, width=1)

    # Селектор стартовой волны в темном стиле
    wave_step_lvl = savedata["Upgrades"].get("start_wave_step", 0)
    current_rec = savedata["LevelsRecords"][game_map]
    max_allowed_start_wave = 1 + wave_step_lvl * 5
    if current_rec > 1:
        max_allowed_start_wave = min(max_allowed_start_wave, (current_rec // 5) * 5 + 1)
    else:
        max_allowed_start_wave = 1

    selected_wave = min(savedata.get("SelectedStartWave", 1), max_allowed_start_wave)
    savedata["SelectedStartWave"] = selected_wave

    # --- ЛЕВАЯ КОЛОНКА (под Картой 1): Прокачка, Оранжерея, Реликвии ---
    # 1. Кнопка Талантов [U]
    pygame.draw.rect(surface, (35, 110, 200) if upg_hover else (24, 80, 155), upg_btn_rect, border_radius=10)
    pygame.draw.rect(surface, (110, 195, 255) if upg_hover else (60, 145, 230), upg_btn_rect, width=2, border_radius=10)
    s_stellar_icon = pygame.transform.smoothscale(stellar_cactus_img_s, (20, 20))
    surface.blit(s_stellar_icon, (upg_btn_rect.left + 22, upg_btn_rect.centery - 10))
    upg_btn_txt = nav_font.render("ТАЛАНТЫ [U]", True, WHITE)
    surface.blit(upg_btn_txt, (upg_btn_rect.left + 52, upg_btn_rect.centery - upg_btn_txt.get_height() // 2))

    # 2. Кнопка Оранжереи [G]
    gh_unlocked = is_greenhouse_unlocked(savedata)
    has_gh_upg = has_upgradeable_greenhouse(savedata)
    if gh_unlocked:
        pygame.draw.rect(surface, (45, 135, 75) if gh_hover else (32, 98, 56), greenhouse_btn_rect, border_radius=10)
        pygame.draw.rect(surface, (120, 235, 160) if gh_hover else (70, 175, 110), greenhouse_btn_rect, width=2, border_radius=10)
        surface.blit(sprout_icon_s, (greenhouse_btn_rect.left + 24, greenhouse_btn_rect.centery - 8))
        gh_txt = nav_font.render("ОРАНЖЕРЕЯ [G]", True, WHITE)
        surface.blit(gh_txt, (greenhouse_btn_rect.left + 52, greenhouse_btn_rect.centery - gh_txt.get_height() // 2))
        if has_gh_upg:
            g_dot = (greenhouse_btn_rect.right - 14, greenhouse_btn_rect.centery)
            pygame.draw.circle(surface, (80, 255, 120), g_dot, 8)
            pygame.draw.circle(surface, WHITE, g_dot, 8, width=1)
            g_ex = tiny_font.render("↑", True, BLACK)
            surface.blit(g_ex, (g_dot[0] - g_ex.get_width() // 2, g_dot[1] - g_ex.get_height() // 2 - 1))
    else:
        pygame.draw.rect(surface, (34, 42, 48) if gh_hover else (26, 32, 38), greenhouse_btn_rect, border_radius=10)
        pygame.draw.rect(surface, (90, 110, 125) if gh_hover else (55, 65, 75), greenhouse_btn_rect, width=1, border_radius=10)
        surface.blit(lock_icon, (greenhouse_btn_rect.left + 24, greenhouse_btn_rect.centery - 8))
        gh_txt = nav_font.render("ОРАНЖЕРЕЯ [G]", True, (150, 165, 178) if gh_hover else (100, 115, 128))
        surface.blit(gh_txt, (greenhouse_btn_rect.left + 52, greenhouse_btn_rect.centery - gh_txt.get_height() // 2))

    # 3. Кнопка Реликвий [R] (Музей)
    arch_unlocked = savedata.get("Upgrades", {}).get("archaeology_unlock", 0) > 0
    if arch_unlocked:
        pygame.draw.rect(surface, (58, 42, 24) if relics_hover else (38, 28, 16), relics_btn_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 215, 80) if relics_hover else (185, 140, 50), relics_btn_rect, width=2, border_radius=10)
        s_relic_icon = pygame.transform.smoothscale(relic_icon, (20, 20))
        surface.blit(s_relic_icon, (relics_btn_rect.left + 22, relics_btn_rect.centery - 10))
        r_txt = nav_font.render("РЕЛИКВИИ [R]", True, (255, 235, 160))
        surface.blit(r_txt, (relics_btn_rect.left + 52, relics_btn_rect.centery - r_txt.get_height() // 2))
        unlocked_cnt = sum(1 for r_id in RELICS_DATA if savedata.get("Relics", {}).get(r_id, {}).get("level", 0) > 0)
        r_sub = tiny_font.render(f"{unlocked_cnt}/20", True, (240, 210, 140))
        surface.blit(r_sub, (relics_btn_rect.right - r_sub.get_width() - 16, relics_btn_rect.centery - r_sub.get_height() // 2))
    else:
        pygame.draw.rect(surface, (34, 38, 44) if relics_hover else (24, 28, 34), relics_btn_rect, border_radius=10)
        pygame.draw.rect(surface, (95, 110, 125) if relics_hover else (55, 65, 75), relics_btn_rect, width=1, border_radius=10)
        surface.blit(lock_icon, (relics_btn_rect.left + 24, relics_btn_rect.centery - 8))
        r_txt = nav_font.render("РЕЛИКВИИ [R]", True, (150, 165, 178) if relics_hover else (100, 115, 128))
        surface.blit(r_txt, (relics_btn_rect.left + 52, relics_btn_rect.centery - r_txt.get_height() // 2))
        r_sub = tiny_font.render("Закрыто", True, (135, 150, 162) if relics_hover else (90, 102, 115))
        surface.blit(r_sub, (relics_btn_rect.right - r_sub.get_width() - 16, relics_btn_rect.centery - r_sub.get_height() // 2))

    # --- ЦЕНТРАЛЬНАЯ КОЛОНКА (под Картой 2): Управление запуском боя ---
    # 4. Селектор стартовой волны
    wave_box_rect = pygame.Rect(465, 492, 340, 48)
    pygame.draw.rect(surface, (18, 26, 38), wave_box_rect, border_radius=10)
    pygame.draw.rect(surface, (54, 96, 134), wave_box_rect, width=2, border_radius=10)

    btn_minus = pygame.Rect(wave_box_rect.left + 8, wave_box_rect.top + 5, 38, 38)
    btn_plus = pygame.Rect(wave_box_rect.right - 46, wave_box_rect.top + 5, 38, 38)

    m_hov = btn_minus.collidepoint(mouse_pos)
    p_hov = btn_plus.collidepoint(mouse_pos)

    pygame.draw.rect(surface, (45, 75, 110) if m_hov else (28, 48, 72), btn_minus, border_radius=8)
    pygame.draw.rect(surface, (110, 175, 245) if m_hov else (52, 92, 138), btn_minus, width=2, border_radius=8)
    txt_m = large_font.render("-", True, WHITE)
    surface.blit(txt_m, (btn_minus.centerx - txt_m.get_width() // 2, btn_minus.centery - txt_m.get_height() // 2 - 2))

    pygame.draw.rect(surface, (45, 75, 110) if p_hov else (28, 48, 72), btn_plus, border_radius=8)
    pygame.draw.rect(surface, (110, 175, 245) if p_hov else (52, 92, 138), btn_plus, width=2, border_radius=8)
    txt_p = large_font.render("+", True, WHITE)
    surface.blit(txt_p, (btn_plus.centerx - txt_p.get_width() // 2, btn_plus.centery - txt_p.get_height() // 2 - 2))

    w_str = f"СТАРТОВАЯ ВОЛНА: {selected_wave}"
    w_txt = font.render(w_str, True, (245, 250, 255))
    surface.blit(w_txt, (wave_box_rect.centerx - w_txt.get_width() // 2, wave_box_rect.centery - w_txt.get_height() // 2))

    # 5. Кнопка «НАЧАТЬ ИГРУ [ПРОБЕЛ]» (большая премиальная кнопка)
    cur_unlocked, cur_lock_reason = is_map_unlocked(game_map, savedata)
    start_btn_rect = pygame.Rect(465, 546, 340, 102)
    st_hover = start_btn_rect.collidepoint(mouse_pos)

    if cur_unlocked:
        btn_bg = (42, 195, 80) if st_hover else (30, 155, 60)
        btn_border = (180, 255, 200) if st_hover else (80, 220, 120)
        txt_str = "НАЧАТЬ ИГРУ [ПРОБЕЛ]"
        sub_str = f"Карта {game_map + 1}: {MAP_NAMES_LIST[game_map]} | Волна {selected_wave}"
        icon = sword_icon
    else:
        btn_bg = (56, 62, 70) if st_hover else (42, 46, 52)
        btn_border = (90, 96, 106)
        txt_str = "КАРТА ЗАКРЫТА"
        sub_str = cur_lock_reason
        icon = lock_icon

    pygame.draw.rect(surface, btn_bg, start_btn_rect, border_radius=12)
    pygame.draw.rect(surface, btn_border, start_btn_rect, width=3 if st_hover and cur_unlocked else 2, border_radius=12)
    
    start_txt = font.render(txt_str, True, WHITE)
    sub_txt = tiny_font.render(sub_str, True, (215, 250, 225) if cur_unlocked else (190, 170, 170))
    tot_h = start_txt.get_height() + sub_txt.get_height() + 6
    top_y = start_btn_rect.centery - tot_h // 2
    
    tot_st_w = start_txt.get_width() + 32
    st_off = start_btn_rect.centerx - tot_st_w // 2
    surface.blit(icon, (st_off, top_y + 1))
    surface.blit(start_txt, (st_off + 32, top_y))
    surface.blit(sub_txt, (start_btn_rect.centerx - sub_txt.get_width() // 2, top_y + start_txt.get_height() + 6))

    # --- ПРАВАЯ КОЛОНКА (под Картой 3): Бестиарий, Достижения, Опции ---
    # 6. Кнопка Бестиария [B]
    pygame.draw.rect(surface, (125, 45, 185) if bes_hover else (95, 32, 145), bestiary_btn_rect, border_radius=10)
    pygame.draw.rect(surface, (230, 160, 255) if bes_hover else (160, 90, 225), bestiary_btn_rect, width=2, border_radius=10)
    s_dark_icon = pygame.transform.smoothscale(dark_cactus_img_s, (20, 20))
    surface.blit(s_dark_icon, (bestiary_btn_rect.left + 22, bestiary_btn_rect.centery - 10))
    bes_txt = nav_font.render("БЕСТИАРИЙ [B]", True, WHITE)
    surface.blit(bes_txt, (bestiary_btn_rect.left + 52, bestiary_btn_rect.centery - bes_txt.get_height() // 2))
    if has_unclaimed_bestiary(savedata):
        b_dot = (bestiary_btn_rect.right - 14, bestiary_btn_rect.centery)
        pygame.draw.circle(surface, (255, 215, 0), b_dot, 8)
        pygame.draw.circle(surface, WHITE, b_dot, 8, width=1)
        b_ex = tiny_font.render("!", True, BLACK)
        surface.blit(b_ex, (b_dot[0] - b_ex.get_width() // 2, b_dot[1] - b_ex.get_height() // 2 - 1))

    # 7. Кнопка Достижений [A]
    has_unclaimed = has_unclaimed_achievements(savedata)
    pygame.draw.rect(surface, (195, 115, 20) if ach_hover else (155, 88, 12), ach_btn_rect, border_radius=10)
    pygame.draw.rect(surface, (255, 210, 100) if ach_hover else (215, 155, 45), ach_btn_rect, width=2, border_radius=10)
    s_trophy_icon = pygame.transform.smoothscale(trophy_icon, (20, 20))
    surface.blit(s_trophy_icon, (ach_btn_rect.left + 22, ach_btn_rect.centery - 10))
    ach_txt = nav_font.render("ДОСТИЖЕНИЯ [A]", True, WHITE)
    surface.blit(ach_txt, (ach_btn_rect.left + 52, ach_btn_rect.centery - ach_txt.get_height() // 2))
    if has_unclaimed:
        badge_center = (ach_btn_rect.right - 14, ach_btn_rect.centery)
        pygame.draw.circle(surface, RED, badge_center, 8)
        pygame.draw.circle(surface, WHITE, badge_center, 8, width=1)
        b_ex = tiny_font.render("!", True, WHITE)
        surface.blit(b_ex, (badge_center[0] - b_ex.get_width() // 2, badge_center[1] - b_ex.get_height() // 2 - 1))

    # 8. Кнопка Опций [O]
    pygame.draw.rect(surface, (55, 75, 105) if settings_hover else (36, 52, 74), settings_btn_rect, border_radius=10)
    pygame.draw.rect(surface, (140, 195, 255) if settings_hover else (75, 110, 155), settings_btn_rect, width=2, border_radius=10)
    surface.blit(gear_icon, (settings_btn_rect.left + 22, settings_btn_rect.centery - 10))
    set_txt = nav_font.render("ОПЦИИ [O]", True, WHITE)
    surface.blit(set_txt, (settings_btn_rect.left + 52, settings_btn_rect.centery - set_txt.get_height() // 2))

    return upg_btn_rect, ach_btn_rect, bestiary_btn_rect, settings_btn_rect, map_rects, info_btn_rects, btn_minus, btn_plus, start_btn_rect, l_arr_rect, r_arr_rect, dot_rects, greenhouse_btn_rect, relics_btn_rect, dark_panel, menu_btn_rect, guide_btn_rect



# -------------------------------------------------------------------------
# СИСТЕМА ЧЕТКИХ ИКОНОК ДРЕВА УЛУЧШЕНИЙ (БЕЗ "МЫЛА" / PIXEL ART & CRISP VECTORS)
# -------------------------------------------------------------------------
_tree_raw_cache = {}

def _get_tree_raw_texture(filename):
    if filename not in _tree_raw_cache:
        for sub in ["assets/textures", "_internal/assets/textures", "."]:
            p = os.path.join(BASE_DIR, sub, filename)
            if os.path.exists(p):
                try:
                    _tree_raw_cache[filename] = pygame.image.load(p).convert_alpha()
                    break
                except Exception:
                    pass
        if filename not in _tree_raw_cache:
            _tree_raw_cache[filename] = None
    return _tree_raw_cache[filename]

def _create_crisp_sprout(sz):
    s = pygame.Surface((sz, sz), pygame.SRCALPHA)
    pw = max(4, int(sz * 0.52))
    ph = max(3, int(sz * 0.18))
    px = (sz - pw) // 2
    py = int(sz * 0.65)
    pygame.draw.rect(s, (160, 95, 45), (px, py, pw, ph), border_radius=max(1, sz // 16))
    pygame.draw.rect(s, (100, 55, 20), (px, py, pw, ph), width=max(1, sz // 20), border_radius=max(1, sz // 16))
    sx = sz // 2
    pygame.draw.line(s, (70, 210, 80), (sx, py), (sx, int(sz * 0.35)), max(2, sz // 10))
    pygame.draw.ellipse(s, (90, 230, 100), (sx - int(sz * 0.32), int(sz * 0.26), int(sz * 0.34), int(sz * 0.24)))
    pygame.draw.ellipse(s, (45, 160, 65), (sx - int(sz * 0.32), int(sz * 0.26), int(sz * 0.34), int(sz * 0.24)), width=max(1, sz // 20))
    pygame.draw.ellipse(s, (130, 250, 140), (sx, int(sz * 0.20), int(sz * 0.34), int(sz * 0.24)))
    pygame.draw.ellipse(s, (45, 160, 65), (sx, int(sz * 0.20), int(sz * 0.34), int(sz * 0.24)), width=max(1, sz // 20))
    return s

def _create_crisp_shovel(sz):
    s = pygame.Surface((sz, sz), pygame.SRCALPHA)
    handle_col = (175, 115, 60)
    metal_col = (205, 215, 225)
    metal_dark = (120, 135, 150)
    pygame.draw.line(s, handle_col, (int(sz * 0.22), int(sz * 0.22)), (int(sz * 0.68), int(sz * 0.68)), max(2, sz // 8))
    pygame.draw.circle(s, handle_col, (int(sz * 0.22), int(sz * 0.22)), max(3, sz // 6), width=max(2, sz // 9))
    poly = [
        (int(sz * 0.52), int(sz * 0.74)),
        (int(sz * 0.74), int(sz * 0.52)),
        (int(sz * 0.88), int(sz * 0.72)),
        (int(sz * 0.72), int(sz * 0.88)),
    ]
    pygame.draw.polygon(s, metal_col, poly)
    pygame.draw.polygon(s, metal_dark, poly, width=max(1, sz // 18))
    pygame.draw.line(s, (240, 245, 255), (int(sz * 0.63), int(sz * 0.63)), (int(sz * 0.8), int(sz * 0.8)), max(1, sz // 16))
    return s

def _create_crisp_relic(sz):
    s = pygame.Surface((sz, sz), pygame.SRCALPHA)
    hs = sz // 2
    pygame.draw.circle(s, (255, 215, 80), (hs, hs), hs - 2, width=max(2, sz // 14))
    pygame.draw.circle(s, (180, 130, 30), (hs, hs), hs - 2 - max(2, sz // 14), width=1)
    poly = [
        (hs - int(sz * 0.18), hs - int(sz * 0.32)),
        (hs + int(sz * 0.18), hs - int(sz * 0.32)),
        (hs + int(sz * 0.30), hs - int(sz * 0.05)),
        (hs + int(sz * 0.15), hs + int(sz * 0.30)),
        (hs - int(sz * 0.15), hs + int(sz * 0.30)),
        (hs - int(sz * 0.30), hs - int(sz * 0.05)),
    ]
    pygame.draw.polygon(s, (245, 190, 50), poly)
    pygame.draw.polygon(s, (150, 100, 20), poly, width=max(1, sz // 18))
    pygame.draw.circle(s, (60, 220, 255), (hs, hs - 2), max(2, sz // 7))
    pygame.draw.circle(s, (220, 250, 255), (hs - 1, hs - 3), max(1, sz // 14))
    return s

_TREE_ICON_FILES = {
    "bounty": "bounty_upg_icon.png",
    "cactus": "Cactus.png",
    "crown": "crown_upg_icon.png",
    "damage": "damage_upg_icon.png",
    "dark_cactus": "Dark_Cactus.png",
    "drone": "Cactus.png",
    "farm": "farm_tower.png",
    "freeze_tower": "freeze_tower.png",
    "greenhouse": "greenhouse_icon.png",
    "health": "health_upg_icon.png",
    "magic_tower": "magic_tower.png",
    "magnet": "magnet_upg_icon.png",
    "rock_tower": "rock_tower.png",
    "soldier": "soldier.png",
    "speed": "speed_upg_icon.png",
    "start_cacti": "start_cacti_icon.png",
    "start_lvl": "start_lvl_icon.png",
    "sword": "sword_icon.png",
    "tent_tower": "tent_tower.png",
    "tesla_tower": "tesla_tower.png",
    "wave": "wave_upg_icon.png",
    "lock": "lock_icon.png",
    "shovel": "shovel_icon.png",
}

_PIXEL_ART_KEYS = {
    "sword", "soldier", "crown", "speed", "wave", "start_lvl",
    "start_cacti", "bounty", "damage", "health", "magnet", "dark_cactus", "drone", "lock", "shovel"
}

_tree_icon_cache = {}

def get_tree_node_icon(icon_key, dim, unlocked=True):
    dim = max(10, dim)
    cache_key = (icon_key, dim, unlocked)
    if cache_key in _tree_icon_cache:
        return _tree_icon_cache[cache_key]

    if icon_key == "sprout":
        base = _create_crisp_sprout(dim)
    elif icon_key == "relic":
        base = _create_crisp_relic(dim)
    elif icon_key == "meteor":
        base = pygame.transform.smoothscale(meteorite_img, (dim, dim))
    elif icon_key == "drone":
        raw = _get_tree_raw_texture("Cactus.png")
        base = pygame.transform.scale(raw, (dim, dim)) if raw else cactus_img_s
    elif icon_key in _TREE_ICON_FILES:
        raw = _get_tree_raw_texture(_TREE_ICON_FILES[icon_key])
        if raw is not None:
            if icon_key in _PIXEL_ART_KEYS:
                # Четкое масштабирование ближайшим соседом (без блюра / мыла)
                base = pygame.transform.scale(raw, (dim, dim))
            else:
                base = pygame.transform.smoothscale(raw, (dim, dim))
        else:
            base = get_node_texture(icon_key)
    else:
        base = get_node_texture(icon_key)

    if not unlocked:
        res = base.copy()
        tint = pygame.Surface((dim, dim), pygame.SRCALPHA)
        tint.fill((110, 130, 160, 160))
        res.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        res.set_alpha(150)
    else:
        res = base

    _tree_icon_cache[cache_key] = res
    return res

def get_crisp_lock_icon(dim):
    dim = max(8, dim)
    cache_key = ("__lock__", dim)
    if cache_key in _tree_icon_cache:
        return _tree_icon_cache[cache_key]
    raw = _get_tree_raw_texture("lock_icon.png")
    if raw is not None:
        res = pygame.transform.scale(raw, (dim, dim))
    else:
        res = pygame.transform.scale(lock_icon, (dim, dim))
    _tree_icon_cache[cache_key] = res
    return res

def get_node_texture(icon_key):
    mapping = {
        "cactus": cactus_img,
        "dark_cactus": dark_cactus_img,
        "drone": cactus_img_s,
        "meteor": meteorite_img,
        "start_lvl": start_lvl_icon,
        "freeze_tower": freeze_tower_img,
        "tent_tower": tent_tower_img,
        "tesla_tower": tesla_tower_img,
        "magic_tower": magic_tower_img,
        "rock_tower": rock_tower_img,
        "crown": crown_upg_icon,
        "speed": speed_upg_icon,
        "health": health_upg_icon,
        "damage": damage_upg_icon,
        "start_cacti": start_cacti_icon,
        "wave": wave_upg_icon,
        "bounty": bounty_upg_icon,
        "farm": farm_tower_img,
        "magnet": magnet_upg_icon,
        "sword": sword_icon,
        "soldier": soldier_img if "soldier_img" in globals() else cactus_img,
        "greenhouse": greenhouse_icon,
        "sprout": sprout_icon,
        "shovel": shovel_icon,
        "relic": relic_icon
    }
    return mapping.get(icon_key, cactus_img)


def draw_upgrade_tree_screen(surface, savedata, mouse_pos, cam_x, cam_y, selected_node_id, is_dragging=False, zoom=1.0, bg_time=None):
    if bg_time is None:
        bg_time = pygame.time.get_ticks()
    generate_background(surface, bg_time, custom_cols=((14, 18, 26), (22, 30, 42)))

    viewport_w = SCREEN_WIDTH - 350
    viewport_h = SCREEN_HEIGHT - 64
    viewport_rect = pygame.Rect(0, 64, viewport_w, viewport_h)

    # 1. Сетка фонового холста
    grid_spacing = max(24, int(60 * zoom))
    ox = int(-cam_x * zoom) % grid_spacing
    oy = int((64 - cam_y * zoom)) % grid_spacing
    for gx in range(ox, viewport_w, grid_spacing):
        pygame.draw.line(surface, (23, 30, 42), (gx, 64), (gx, 64 + viewport_h), 1)
    for gy in range(64 + oy, 64 + viewport_h, grid_spacing):
        pygame.draw.line(surface, (23, 30, 42), (0, gy), (viewport_w, gy), 1)

    # Устанавливаем отсечение для холста древа
    surface.set_clip(viewport_rect)

    upgrades = savedata.get("Upgrades", {})

    # 2. Отрисовка соединительных линий (ребер графа)
    for node_id, node in UPGRADE_TREE_NODES.items():
        csx = int((node["x"] - cam_x) * zoom)
        csy = int((node["y"] - cam_y) * zoom)

        for parent_id, req_val in node["requires"].items():
            parent = UPGRADE_TREE_NODES.get(parent_id)
            if not parent:
                continue
            psx = int((parent["x"] - cam_x) * zoom)
            psy = int((parent["y"] - cam_y) * zoom)

            p_lvl = upgrades.get(parent_id, 0)
            p_max = parent["max_lvl"]
            req_met = (p_lvl >= p_max) if req_val == "max" else (p_lvl >= req_val)

            # Определение цвета линии
            if req_met:
                if p_lvl >= p_max:
                    line_col = (255, 215, 75)
                    line_w = max(1, int(3 * zoom))
                else:
                    line_col = (50, 210, 140)
                    line_w = max(1, int(2 * zoom))
            else:
                line_col = (48, 58, 70)
                line_w = 1

            mid_y = (psy + csy) // 2
            pygame.draw.lines(surface, line_col, False, [(psx, psy), (psx, mid_y), (csx, mid_y), (csx, csy)], line_w)

            if req_met:
                mx = (psx + csx) // 2
                pygame.draw.circle(surface, line_col, (mx, mid_y), max(2, int(3 * zoom)))

    # 3. Отрисовка нод графа
    node_screen_rects = {}

    for node_id, node in UPGRADE_TREE_NODES.items():
        scale = node.get("scale", 1.0)
        eff_scale = scale * zoom
        base_rad = max(8, int(27 * eff_scale))
        hit_rad = max(10, int(28 * eff_scale))
        nsx = int((node["x"] - cam_x) * zoom)
        nsy = int((node["y"] - cam_y) * zoom)
        node_rect = pygame.Rect(nsx - hit_rad, nsy - hit_rad, hit_rad * 2, hit_rad * 2)
        node_screen_rects[node_id] = node_rect

        # Пропускаем отрисовку, если нода полностью вне экрана
        margin = hit_rad + 60
        if nsx < -margin or nsx > viewport_w + margin or nsy < 64 - margin or nsy > 64 + viewport_h + margin:
            continue

        cur_lvl = upgrades.get(node_id, 0)
        max_lvl = node["max_lvl"]
        is_maxed = (cur_lvl >= max_lvl)
        unlocked, _ = check_node_requirements(node_id, savedata)
        is_selected = (node_id == selected_node_id)
        is_hov = (math.hypot(mouse_pos[0] - nsx, mouse_pos[1] - nsy) <= hit_rad and viewport_rect.collidepoint(mouse_pos))

        # Спецэффект пульсирующей ауры для великих нод (scale > 1.2, например Оранжерея)
        if scale > 1.2:
            t_now = pygame.time.get_ticks()
            pulse = math.sin(t_now * 0.005) * 4 * zoom
            aura_rad = max(12, int(base_rad + 8 * zoom + pulse))
            aura_surf = pygame.Surface((aura_rad * 2 + 10, aura_rad * 2 + 10), pygame.SRCALPHA)
            aura_col = (80, 240, 150, 48 if unlocked else 20)
            pygame.draw.circle(aura_surf, aura_col, (aura_rad + 5, aura_rad + 5), aura_rad)
            pygame.draw.circle(aura_surf, (140, 255, 190, 90 if unlocked else 35), (aura_rad + 5, aura_rad + 5), aura_rad - max(1, int(4 * zoom)), width=max(1, int(2 * zoom)))
            surface.blit(aura_surf, (nsx - aura_rad - 5, nsy - aura_rad - 5))

        if is_selected:
            pygame.draw.circle(surface, (255, 235, 90), (nsx, nsy), max(base_rad + 3, int(34 * eff_scale)), width=max(1, int(2 * eff_scale)))
            pygame.draw.circle(surface, (255, 235, 90), (nsx, nsy), max(base_rad + 6, int(37 * eff_scale)), width=1)
        elif is_hov:
            pygame.draw.circle(surface, WHITE, (nsx, nsy), max(base_rad + 3, int(32 * eff_scale)), width=max(1, int(1.5 * eff_scale)))

        if is_maxed:
            bg_col = (40, 32, 16)
            border_col = GOLD
            border_w = max(2, int(4 * eff_scale if scale > 1.2 else 3 * eff_scale))
        elif cur_lvl > 0:
            bg_col = (16, 36, 26)
            border_col = (50, 210, 100)
            border_w = max(1, int(3 * eff_scale if scale > 1.2 else 2 * eff_scale))
        elif unlocked:
            is_dark_node = (node.get("currency") in ("dark", "hybrid")) or (node.get("branch") == "astral")
            if is_dark_node:
                bg_col = (28, 16, 40)
                border_col = (195, 120, 255)
            else:
                bg_col = (20, 32, 46) if scale <= 1.2 else (20, 42, 34)
                border_col = (80, 200, 255) if scale <= 1.2 else (90, 240, 170)
            border_w = max(1, int(3 * eff_scale if scale > 1.2 else 2 * eff_scale))
        else:
            bg_col = (22, 26, 32)
            border_col = (60, 70, 80)
            border_w = max(1, int(2 * eff_scale if scale > 1.2 else 1 * eff_scale))

        pygame.draw.circle(surface, bg_col, (nsx, nsy), base_rad)
        pygame.draw.circle(surface, border_col, (nsx, nsy), base_rad, width=border_w)

        icon_dim = max(10, int(32 * eff_scale))
        node_icon = get_tree_node_icon(node["icon_key"], icon_dim, unlocked=unlocked)
        surface.blit(node_icon, (nsx - icon_dim // 2, nsy - icon_dim // 2))

        if not unlocked:
            l_dim = max(8, min(22, int(14 * eff_scale)))
            s_lock = get_crisp_lock_icon(l_dim)
            surface.blit(s_lock, (nsx + icon_dim // 4 - l_dim // 2, nsy + icon_dim // 4 - l_dim // 2))

        # Заголовок ноды (скрываем при сильном отдалении, если не наведена и не выбрана)
        if zoom >= 0.58 or is_hov or is_selected:
            b_colors = {
                "tech": (140, 215, 255),
                "combat": (255, 150, 130),
                "econ": (150, 240, 160),
                "core": GOLD,
                "astral": (210, 110, 255)
            }
            t_col = b_colors.get(node["branch"], WHITE)
            t_font = font if eff_scale > 1.2 else tiny_font
            words = node["title"].split(" ")
            if len(words) == 2 and t_font.size(node["title"])[0] > (95 if scale > 1.2 else 75):
                l1 = t_font.render(words[0], True, t_col)
                l2 = t_font.render(words[1], True, t_col)
                l1_sh = t_font.render(words[0], True, (6, 8, 12))
                l2_sh = t_font.render(words[1], True, (6, 8, 12))
                th = l1.get_height() + l2.get_height()
                ty = nsy - (base_rad + th + 6)
                surface.blit(l1_sh, (nsx - l1.get_width() // 2 + 1, ty + 1))
                surface.blit(l1, (nsx - l1.get_width() // 2, ty))
                surface.blit(l2_sh, (nsx - l2.get_width() // 2 + 1, ty + l1.get_height() + 1))
                surface.blit(l2, (nsx - l2.get_width() // 2, ty + l1.get_height()))
            else:
                title_surf = t_font.render(node["title"], True, t_col)
                sh_surf = t_font.render(node["title"], True, (6, 8, 12))
                ty = nsy - (base_rad + title_surf.get_height() + 5)
                surface.blit(sh_surf, (nsx - title_surf.get_width() // 2 + 1, ty + 1))
                surface.blit(title_surf, (nsx - title_surf.get_width() // 2, ty))

        cost, dark_cost, _ = get_upgrade_node_cost(node_id, cur_lvl)
        is_node_toggleable = node.get("toggleable", False)
        is_node_toggled_off = is_node_toggleable and (cur_lvl > 0) and not savedata.get("Toggles", {}).get(node_id, True)

        icon_sz = max(9, int(14 if scale > 1.2 else 12))
        s_ic = pygame.transform.smoothscale(stellar_cactus_img_xs, (icon_sz, icon_sz))
        d_ic = pygame.transform.smoothscale(dark_cactus_img_xs, (icon_sz, icon_sz))

        pill_h = max(15, int(22 * zoom if scale > 1.2 else 18 * zoom))

        if is_maxed:
            if is_node_toggled_off:
                pill_bg = (140, 35, 35)
                p_surf = tiny_font.render("ВЫКЛ", True, (255, 210, 210))
            else:
                pill_bg = (190, 150, 25)
                p_surf = tiny_font.render("ОТКРЫТО" if scale > 1.2 else "МАКС", True, WHITE)
            pill_w = max(int((56 if scale > 1.2 else 48) * zoom), p_surf.get_width() + 12)
            pill_rect = pygame.Rect(nsx - pill_w // 2, nsy + base_rad - 1, pill_w, pill_h)
            pygame.draw.rect(surface, pill_bg, pill_rect, border_radius=5)
            surface.blit(p_surf, (pill_rect.centerx - p_surf.get_width() // 2, pill_rect.centery - p_surf.get_height() // 2))

        elif not unlocked:
            pill_bg = (36, 42, 50)
            p_surf = tiny_font.render("ЗАКРЫТО", True, (150, 160, 170))
            pill_w = max(int((62 if scale > 1.2 else 54) * zoom), p_surf.get_width() + 12)
            pill_rect = pygame.Rect(nsx - pill_w // 2, nsy + base_rad - 1, pill_w, pill_h)
            pygame.draw.rect(surface, pill_bg, pill_rect, border_radius=5)
            surface.blit(p_surf, (pill_rect.centerx - p_surf.get_width() // 2, pill_rect.centery - p_surf.get_height() // 2))

        else:
            # Узел доступен для прокачки (cur_lvl == 0 или в процессе 0 < cur_lvl < max_lvl)
            is_dark_curr = (node.get("currency") == "dark") or (dark_cost > 0 and (cost is None or cost == 0))
            is_hybrid = (dark_cost is not None and dark_cost > 0 and cost is not None and cost > 0)

            if cur_lvl > 0:
                pill_bg = (140, 35, 35) if is_node_toggled_off else (24, 115, 60)
            elif is_hybrid:
                pill_bg = (75, 30, 105)
            elif is_dark_curr:
                pill_bg = (65, 26, 88)
            else:
                pill_bg = (25, 95, 135)

            items = []
            if cur_lvl > 0:
                lvl_str = f"{cur_lvl} ВЫКЛ" if is_node_toggled_off else f"{cur_lvl}/{max_lvl}"
                lvl_surf = tiny_font.render(lvl_str, True, (255, 220, 220) if is_node_toggled_off else (210, 255, 220))
                items.append((lvl_surf, False))
                sep_surf = tiny_font.render("|", True, (160, 210, 180))
                items.append((sep_surf, False))

            if is_hybrid:
                t1 = tiny_font.render(str(cost), True, (255, 235, 160))
                items.append((t1, False))
                items.append((s_ic, True))
                plus_t = tiny_font.render("+", True, (220, 210, 235))
                items.append((plus_t, False))
                t2 = tiny_font.render(str(dark_cost), True, (235, 175, 255))
                items.append((t2, False))
                items.append((d_ic, True))
            elif is_dark_curr:
                t2 = tiny_font.render(str(dark_cost), True, (235, 175, 255))
                items.append((t2, False))
                items.append((d_ic, True))
            else:
                c_val = cost if cost is not None else 0
                t1 = tiny_font.render(str(c_val), True, (255, 230, 110))
                items.append((t1, False))
                items.append((s_ic, True))

            spacing = 2
            tot_w = sum(img.get_width() for img, _ in items) + spacing * (len(items) - 1)
            pill_w = max(int((52 if scale <= 1.2 else 64) * zoom), tot_w + 10)
            pill_rect = pygame.Rect(nsx - pill_w // 2, nsy + base_rad - 1, pill_w, pill_h)
            pygame.draw.rect(surface, pill_bg, pill_rect, border_radius=5)

            curr_x = pill_rect.centerx - tot_w // 2
            for img, _ in items:
                img_y = pill_rect.centery - img.get_height() // 2
                surface.blit(img, (curr_x, img_y))
                curr_x += img.get_width() + spacing

    surface.set_clip(None)

    # 3.5. Панель управления зумом (HUD в правом нижнем углу холста)
    hud_w = 172
    hud_h = 36
    hud_x = viewport_w - hud_w - 14
    hud_y = 64 + viewport_h - hud_h - 12

    hud_bg = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
    pygame.draw.rect(hud_bg, (14, 20, 30, 220), (0, 0, hud_w, hud_h), border_radius=8)
    pygame.draw.rect(hud_bg, (45, 65, 90, 240), (0, 0, hud_w, hud_h), width=1, border_radius=8)
    surface.blit(hud_bg, (hud_x, hud_y))

    # Кнопка Уменьшить [-]
    zoom_out_rect = pygame.Rect(hud_x + 4, hud_y + 4, 30, 28)
    zo_hov = zoom_out_rect.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (42, 60, 84) if zo_hov else (22, 32, 46), zoom_out_rect, border_radius=6)
    pygame.draw.rect(surface, (90, 150, 215) if zo_hov else (52, 76, 105), zoom_out_rect, width=1, border_radius=6)
    zo_txt = font.render("-", True, WHITE if zo_hov else (200, 220, 240))
    surface.blit(zo_txt, (zoom_out_rect.centerx - zo_txt.get_width() // 2, zoom_out_rect.centery - zo_txt.get_height() // 2 - 1))

    # Кнопка Индикатор / Сброс [ 100% ]
    zoom_reset_rect = pygame.Rect(hud_x + 38, hud_y + 4, 96, 28)
    zr_hov = zoom_reset_rect.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (45, 68, 96) if zr_hov else (22, 32, 46), zoom_reset_rect, border_radius=6)
    pygame.draw.rect(surface, GOLD if zr_hov else (52, 76, 105), zoom_reset_rect, width=1, border_radius=6)
    pct_str = f"ЗУМ {int(round(zoom * 100))}%"
    zr_txt = small_font.render(pct_str, True, GOLD if zr_hov else (220, 235, 255))
    surface.blit(zr_txt, (zoom_reset_rect.centerx - zr_txt.get_width() // 2, zoom_reset_rect.centery - zr_txt.get_height() // 2))

    # Кнопка Увеличить [+]
    zoom_in_rect = pygame.Rect(hud_x + 138, hud_y + 4, 30, 28)
    zi_hov = zoom_in_rect.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (42, 60, 84) if zi_hov else (22, 32, 46), zoom_in_rect, border_radius=6)
    pygame.draw.rect(surface, (90, 150, 215) if zi_hov else (52, 76, 105), zoom_in_rect, width=1, border_radius=6)
    zi_txt = font.render("+", True, WHITE if zi_hov else (200, 220, 240))
    surface.blit(zi_txt, (zoom_in_rect.centerx - zi_txt.get_width() // 2, zoom_in_rect.centery - zi_txt.get_height() // 2))

    # 4. Верхняя панель навигации
    top_bar = pygame.Rect(0, 0, SCREEN_WIDTH, 64)
    pygame.draw.rect(surface, (14, 18, 24), top_bar)
    pygame.draw.line(surface, (40, 52, 68), (0, 64), (SCREEN_WIDTH, 64), 1)

    # Звёздные кактусы
    bal_rect = pygame.Rect(14, 8, 132, 48)
    pygame.draw.rect(surface, (20, 28, 38), bal_rect, border_radius=8)
    pygame.draw.rect(surface, GOLD, bal_rect, width=2, border_radius=8)
    surface.blit(stellar_cactus_img_m, (bal_rect.left + 8, bal_rect.centery - 18))
    bal_txt = font.render(f"{savedata.get('StellarCactuses', 0)}", True, WHITE)
    surface.blit(bal_txt, (bal_rect.left + 48, bal_rect.centery - bal_txt.get_height() // 2))

    # Тёмные кактусы
    dark_bal_rect = pygame.Rect(154, 8, 132, 48)
    draw_dark_cactus_counter(surface, dark_bal_rect, savedata, mouse_pos)

    # Кнопка Справка по Древу
    info_btn_rect = pygame.Rect(SCREEN_WIDTH - 465, 10, 115, 44)
    inf_hov = info_btn_rect.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (30, 75, 110) if inf_hov else (20, 50, 78), info_btn_rect, border_radius=8)
    pygame.draw.rect(surface, (90, 200, 255) if inf_hov else (50, 140, 190), info_btn_rect, width=1, border_radius=8)
    inf_txt = small_font.render("? ИНФО", True, (220, 245, 255))
    surface.blit(inf_txt, (info_btn_rect.centerx - inf_txt.get_width() // 2, info_btn_rect.centery - inf_txt.get_height() // 2))

    center_btn_rect = pygame.Rect(SCREEN_WIDTH - 340, 10, 120, 44)
    c_hov = center_btn_rect.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (40, 60, 80) if c_hov else (28, 42, 58), center_btn_rect, border_radius=8)
    pygame.draw.rect(surface, (100, 140, 180), center_btn_rect, width=1, border_radius=8)
    c_txt = small_font.render("[C] ЦЕНТР", True, WHITE)
    surface.blit(c_txt, (center_btn_rect.centerx - c_txt.get_width() // 2, center_btn_rect.centery - c_txt.get_height() // 2))

    back_btn_rect = pygame.Rect(SCREEN_WIDTH - 200, 10, 180, 44)
    b_hov = back_btn_rect.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (200, 50, 50) if b_hov else (160, 40, 40), back_btn_rect, border_radius=8)
    pygame.draw.rect(surface, WHITE, back_btn_rect, width=2, border_radius=8)
    back_txt = font.render("< НАЗАД [ESC]", True, WHITE)
    surface.blit(back_txt, (back_btn_rect.centerx - back_txt.get_width() // 2, back_btn_rect.centery - back_txt.get_height() // 2))

    hdr_center_x = (dark_bal_rect.right + info_btn_rect.left) // 2
    t_main = large_font.render("ДРЕВО УЛУЧШЕНИЙ ОАЗИСА", True, GOLD)
    surface.blit(t_main, (hdr_center_x - t_main.get_width() // 2, 6))

    # Счётчик прогресса древа: куплено нод X/Y, куплено улучшений A/B
    total_nodes = len(UPGRADE_TREE_NODES)
    bought_nodes = sum(1 for nid, n in UPGRADE_TREE_NODES.items() if upgrades.get(nid, 0) > 0)
    total_upgrades = sum(n["max_lvl"] for n in UPGRADE_TREE_NODES.values())
    bought_upgrades = sum(min(n["max_lvl"], upgrades.get(nid, 0)) for nid, n in UPGRADE_TREE_NODES.items())
    upg_pct = int(round(bought_upgrades / max(1, total_upgrades) * 100))

    stat_str = f"Куплено нод: {bought_nodes}/{total_nodes}   •   Куплено улучшений: {bought_upgrades}/{total_upgrades} ({upg_pct}%)"
    stat_surf = font.render(stat_str, True, (160, 245, 195))
    surface.blit(stat_surf, (hdr_center_x - stat_surf.get_width() // 2, 36))

    # 5. Боковой Инспектор выбранной ноды
    inspector_rect = pygame.Rect(SCREEN_WIDTH - 340, 72, 325, SCREEN_HEIGHT - 82)
    pygame.draw.rect(surface, (18, 24, 32), inspector_rect, border_radius=12)
    pygame.draw.rect(surface, (55, 72, 95), inspector_rect, width=2, border_radius=12)

    sel_node = UPGRADE_TREE_NODES.get(selected_node_id, UPGRADE_TREE_NODES["oasis_core"])
    cur_lvl = upgrades.get(selected_node_id, 0)
    max_lvl = sel_node["max_lvl"]
    is_maxed = (cur_lvl >= max_lvl)
    unlocked, req_details = check_node_requirements(selected_node_id, savedata)

    iy = inspector_rect.top + 16

    b_tag_cols = {
        "tech": ((30, 70, 120), (120, 200, 255)),
        "combat": ((110, 40, 35), (255, 160, 140)),
        "econ": ((30, 90, 50), (140, 240, 160)),
        "core": ((100, 80, 20), GOLD),
        "astral": ((60, 25, 85), (225, 160, 255))
    }
    b_bg, b_fg = b_tag_cols.get(sel_node["branch"], ((40, 50, 60), WHITE))

    t_surf = font.render(sel_node["title"], True, WHITE)
    surface.blit(t_surf, (inspector_rect.left + 14, iy))
    iy += 30

    icon_box = pygame.Rect(inspector_rect.left + 14, iy, 56, 56)
    pygame.draw.rect(surface, (12, 16, 22), icon_box, border_radius=8)
    pygame.draw.rect(surface, b_fg, icon_box, width=1, border_radius=8)
    big_icon = get_tree_node_icon(sel_node["icon_key"], 44, unlocked=True)
    surface.blit(big_icon, (icon_box.centerx - 22, icon_box.centery - 22))
    if not unlocked:
        s_lock = get_crisp_lock_icon(16)
        surface.blit(s_lock, (icon_box.right - 18, icon_box.bottom - 18))

    lvl_txt = font.render(f"УРОВЕНЬ: {cur_lvl} / {max_lvl if max_lvl < 90 else 'МАКС'}", True, GOLD if is_maxed else WHITE)
    surface.blit(lvl_txt, (inspector_rect.left + 80, iy + 6))

    pips_x = inspector_rect.left + 80
    pips_y = iy + 36
    pips_total_w = 230
    if max_lvl <= 10:
        pips_count = max(1, max_lvl)
        pip_w = max(4, (pips_total_w - (pips_count - 1) * 3) // pips_count)
        for p_i in range(pips_count):
            p_rect = pygame.Rect(pips_x + p_i * (pip_w + 3), pips_y, pip_w, 8)
            if p_i < cur_lvl:
                pygame.draw.rect(surface, GOLD if is_maxed else GREEN, p_rect, border_radius=2)
            else:
                pygame.draw.rect(surface, (35, 45, 55), p_rect, border_radius=2)
        iy += 68
    else:
        # 2 аккуратных ряда индикаторов для высоких уровней (например, 20 уровней Выбора Волны)
        per_row = (max_lvl + 1) // 2
        pip_w = max(4, (pips_total_w - (per_row - 1) * 3) // per_row)
        for p_i in range(max_lvl):
            r_idx = p_i // per_row
            c_idx = p_i % per_row
            p_rect = pygame.Rect(pips_x + c_idx * (pip_w + 3), pips_y + r_idx * 9, pip_w, 6)
            if p_i < cur_lvl:
                pygame.draw.rect(surface, GOLD if is_maxed else GREEN, p_rect, border_radius=2)
            else:
                pygame.draw.rect(surface, (35, 45, 55), p_rect, border_radius=2)
        iy += 72

    pygame.draw.line(surface, (40, 52, 68), (inspector_rect.left + 14, iy), (inspector_rect.right - 14, iy), 1)
    iy += 10

    max_w = inspector_rect.width - 28
    for line in sel_node["desc"]:
        words = line.split()
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            if tiny_font.size(test_line)[0] <= max_w:
                current_line.append(word)
            else:
                if current_line:
                    d_surf = tiny_font.render(" ".join(current_line), True, (185, 200, 215))
                    surface.blit(d_surf, (inspector_rect.left + 14, iy))
                    iy += 17
                current_line = [word]
        if current_line:
            d_surf = tiny_font.render(" ".join(current_line), True, (185, 200, 215))
            surface.blit(d_surf, (inspector_rect.left + 14, iy))
            iy += 17
        iy += 2

    iy += 4
    pygame.draw.line(surface, (40, 52, 68), (inspector_rect.left + 14, iy), (inspector_rect.right - 14, iy), 1)
    iy += 10

    ef_title = small_font.render("ХАРАКТЕРИСТИКА:", True, (140, 210, 255))
    surface.blit(ef_title, (inspector_rect.left + 14, iy))
    iy += 22

    max_w = inspector_rect.width - 28
    def draw_wrapped_stat(prefix, text, color):
        nonlocal iy
        full_text = f"{prefix} {text}"
        words = full_text.split()
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            if tiny_font.size(test_line)[0] <= max_w:
                current_line.append(word)
            else:
                if current_line:
                    line_surf = tiny_font.render(" ".join(current_line), True, color)
                    surface.blit(line_surf, (inspector_rect.left + 14, iy))
                    iy += 17
                current_line = [word]
        if current_line:
            line_surf = tiny_font.render(" ".join(current_line), True, color)
            surface.blit(line_surf, (inspector_rect.left + 14, iy))
            iy += 20

    draw_wrapped_stat("Текущий:", sel_node['stat_cur'](cur_lvl), GOLD if cur_lvl > 0 else (160, 175, 190))

    if not is_maxed:
        draw_wrapped_stat("Следующий:", sel_node['stat_nxt'](cur_lvl), GREEN)
    else:
        max_stat_txt = tiny_font.render("Достигнут максимальный предел развития!", True, GOLD)
        surface.blit(max_stat_txt, (inspector_rect.left + 14, iy))
        iy += 22

    iy += 2
    pygame.draw.line(surface, (40, 52, 68), (inspector_rect.left + 14, iy), (inspector_rect.right - 14, iy), 1)
    iy += 10

    req_title = small_font.render("УСЛОВИЯ РАЗБЛОКИРОВКИ:", True, (255, 215, 100))
    surface.blit(req_title, (inspector_rect.left + 14, iy))
    iy += 22

    if not sel_node["requires"]:
        r_txt = tiny_font.render("Доступно со старта оазиса", True, GREEN)
        surface.blit(r_txt, (inspector_rect.left + 14, iy))
        iy += 20
    else:
        for r_item in req_details:
            if r_item["met"]:
                r_txt = tiny_font.render(f"{r_item['req_str']} (Выполнено)", True, GREEN)
            else:
                r_txt = tiny_font.render(f"{r_item['req_str']} (Сейчас: {r_item['cur_lvl']})", True, (255, 105, 105))
            surface.blit(r_txt, (inspector_rect.left + 14, iy))
            iy += 20

    toggle_btn_rect = None
    if sel_node.get("toggleable", False) and cur_lvl > 0:
        toggle_btn_rect = pygame.Rect(inspector_rect.left + 14, inspector_rect.bottom - 100, inspector_rect.width - 28, 38)
        t_hov = toggle_btn_rect.collidepoint(mouse_pos)
        is_active = savedata.get("Toggles", {}).get(selected_node_id, True)
        if is_active:
            t_bg = (24, 75, 42) if not t_hov else (35, 95, 54)
            t_border = (65, 220, 100)
            t_str = "[ВКЛ] АКТИВНО (Клик: ВЫКЛ)"
            t_col = (185, 255, 205)
        else:
            t_bg = (75, 26, 30) if not t_hov else (95, 36, 40)
            t_border = (235, 75, 75)
            t_str = "[ВЫКЛ] ОТКЛЮЧЕНО (Клик: ВКЛ)"
            t_col = (255, 185, 185)

        pygame.draw.rect(surface, t_bg, toggle_btn_rect, border_radius=8)
        pygame.draw.rect(surface, t_border, toggle_btn_rect, width=2 if t_hov else 1, border_radius=8)
        t_surf = small_font.render(t_str, True, t_col)
        surface.blit(t_surf, (toggle_btn_rect.centerx - t_surf.get_width() // 2, toggle_btn_rect.centery - t_surf.get_height() // 2))

    buy_btn_rect = pygame.Rect(inspector_rect.left + 14, inspector_rect.bottom - 54, inspector_rect.width - 28, 42)
    b_hov = buy_btn_rect.collidepoint(mouse_pos)

    if is_maxed:
        if selected_node_id == "archaeology_unlock":
            pygame.draw.rect(surface, (68, 50, 24) if b_hov else (46, 32, 16), buy_btn_rect, border_radius=8)
            pygame.draw.rect(surface, (255, 220, 80) if b_hov else (190, 150, 50), buy_btn_rect, width=2, border_radius=8)
            surface.blit(relic_icon, (buy_btn_rect.left + 14, buy_btn_rect.centery - 12))
            b_txt = font.render("В МУЗЕЙ РЕЛИКВИЙ [R]", True, (255, 235, 160))
            surface.blit(b_txt, (buy_btn_rect.left + 44, buy_btn_rect.centery - b_txt.get_height() // 2))
        elif selected_node_id == "greenhouse_unlock":
            pygame.draw.rect(surface, (36, 115, 65) if b_hov else (24, 85, 45), buy_btn_rect, border_radius=8)
            pygame.draw.rect(surface, (120, 245, 160) if b_hov else (60, 180, 100), buy_btn_rect, width=2, border_radius=8)
            surface.blit(sprout_icon_s, (buy_btn_rect.left + 14, buy_btn_rect.centery - 8))
            b_txt = font.render("В ОРАНЖЕРЕЮ [G]", True, WHITE)
            surface.blit(b_txt, (buy_btn_rect.left + 42, buy_btn_rect.centery - b_txt.get_height() // 2))
        elif selected_node_id == "astral_beacon":
            pygame.draw.rect(surface, (55, 22, 75) if b_hov else (38, 16, 52), buy_btn_rect, border_radius=8)
            pygame.draw.rect(surface, (215, 120, 255) if b_hov else (160, 80, 210), buy_btn_rect, width=2, border_radius=8)
            surface.blit(dark_cactus_img_s, (buy_btn_rect.left + 14, buy_btn_rect.centery - 12))
            b_txt = font.render("ТЁМНЫЙ КОСМОС ОТКРЫТ!", True, (240, 210, 255))
            surface.blit(b_txt, (buy_btn_rect.left + 42, buy_btn_rect.centery - b_txt.get_height() // 2))
        else:
            pygame.draw.rect(surface, (40, 48, 56), buy_btn_rect, border_radius=8)
            b_txt = small_font.render("МАКСИМАЛЬНЫЙ УРОВЕНЬ", True, (150, 160, 170))
            surface.blit(b_txt, (buy_btn_rect.centerx - b_txt.get_width() // 2, buy_btn_rect.centery - b_txt.get_height() // 2))
    elif not unlocked:
        pygame.draw.rect(surface, (55, 26, 30), buy_btn_rect, border_radius=8)
        pygame.draw.rect(surface, (110, 45, 50), buy_btn_rect, width=1, border_radius=8)
        b_txt = small_font.render("ТРЕБОВАНИЯ НЕ ВЫПОЛНЕНЫ", True, (255, 130, 130))
        surface.blit(lock_icon, (buy_btn_rect.centerx - b_txt.get_width() // 2 - 18, buy_btn_rect.centery - 8))
        surface.blit(b_txt, (buy_btn_rect.centerx - b_txt.get_width() // 2 + 6, buy_btn_rect.centery - b_txt.get_height() // 2))
    else:
        cost, dark_cost, _ = get_upgrade_node_cost(selected_node_id, cur_lvl)
        st_have = savedata.get("StellarCactuses", 0)
        dk_have = savedata.get("DarkCactuses", 0)
        can_afford = (st_have >= cost and dk_have >= dark_cost)
        is_hybrid = (cost > 0 and dark_cost > 0)
        is_dark_only = (dark_cost > 0 and cost == 0)

        if can_afford:
            b_col = (115, 45, 165) if is_hybrid else ((135, 45, 190) if is_dark_only else ((45, 185, 80) if not b_hov else (60, 215, 95)))
            pygame.draw.rect(surface, b_col, buy_btn_rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, buy_btn_rect, width=2 if b_hov else 1, border_radius=8)
            if is_hybrid:
                a_txt = font.render("КУПИТЬ: ", True, WHITE)
                c1_txt = font.render(str(cost), True, WHITE)
                plus_txt = font.render(" + ", True, (225, 210, 240))
                c2_txt = font.render(str(dark_cost), True, WHITE)
                tot_w = a_txt.get_width() + c1_txt.get_width() + 26 + plus_txt.get_width() + c2_txt.get_width() + 26
                bx = buy_btn_rect.centerx - tot_w // 2
                surface.blit(a_txt, (bx, buy_btn_rect.centery - a_txt.get_height() // 2))
                bx += a_txt.get_width()
                surface.blit(c1_txt, (bx, buy_btn_rect.centery - c1_txt.get_height() // 2))
                bx += c1_txt.get_width() + 2
                surface.blit(stellar_cactus_img_s, (bx, buy_btn_rect.centery - 12))
                bx += 24
                surface.blit(plus_txt, (bx, buy_btn_rect.centery - plus_txt.get_height() // 2))
                bx += plus_txt.get_width()
                surface.blit(c2_txt, (bx, buy_btn_rect.centery - c2_txt.get_height() // 2))
                bx += c2_txt.get_width() + 2
                surface.blit(dark_cactus_img_s, (bx, buy_btn_rect.centery - 12))
            elif is_dark_only:
                b_txt = font.render(f"КУПИТЬ: {dark_cost}", True, WHITE)
                tot_w = b_txt.get_width() + 28
                start_bx = buy_btn_rect.centerx - tot_w // 2
                surface.blit(b_txt, (start_bx, buy_btn_rect.centery - b_txt.get_height() // 2))
                surface.blit(dark_cactus_img_s, (start_bx + b_txt.get_width() + 4, buy_btn_rect.centery - 12))
            else:
                b_txt = font.render(f"КУПИТЬ: {cost}", True, WHITE)
                tot_w = b_txt.get_width() + 28
                start_bx = buy_btn_rect.centerx - tot_w // 2
                surface.blit(b_txt, (start_bx, buy_btn_rect.centery - b_txt.get_height() // 2))
                surface.blit(stellar_cactus_img_s, (start_bx + b_txt.get_width() + 4, buy_btn_rect.centery - 12))
        else:
            pygame.draw.rect(surface, (170, 50, 50), buy_btn_rect, border_radius=8)
            pygame.draw.rect(surface, (220, 80, 80), buy_btn_rect, width=1, border_radius=8)
            if is_hybrid:
                a_txt = font.render("НУЖНО: ", True, WHITE)
                c1_txt = font.render(str(cost), True, WHITE)
                plus_txt = font.render(" + ", True, (225, 210, 240))
                c2_txt = font.render(str(dark_cost), True, WHITE)
                tot_w = a_txt.get_width() + c1_txt.get_width() + 26 + plus_txt.get_width() + c2_txt.get_width() + 26
                bx = buy_btn_rect.centerx - tot_w // 2
                surface.blit(a_txt, (bx, buy_btn_rect.centery - a_txt.get_height() // 2))
                bx += a_txt.get_width()
                surface.blit(c1_txt, (bx, buy_btn_rect.centery - c1_txt.get_height() // 2))
                bx += c1_txt.get_width() + 2
                surface.blit(stellar_cactus_img_s, (bx, buy_btn_rect.centery - 12))
                bx += 24
                surface.blit(plus_txt, (bx, buy_btn_rect.centery - plus_txt.get_height() // 2))
                bx += plus_txt.get_width()
                surface.blit(c2_txt, (bx, buy_btn_rect.centery - c2_txt.get_height() // 2))
                bx += c2_txt.get_width() + 2
                surface.blit(dark_cactus_img_s, (bx, buy_btn_rect.centery - 12))
            elif is_dark_only:
                b_txt = font.render(f"НУЖНО: {dark_cost}", True, WHITE)
                tot_w = b_txt.get_width() + 28
                start_bx = buy_btn_rect.centerx - tot_w // 2
                surface.blit(b_txt, (start_bx, buy_btn_rect.centery - b_txt.get_height() // 2))
                surface.blit(dark_cactus_img_s, (start_bx + b_txt.get_width() + 4, buy_btn_rect.centery - 12))
            else:
                b_txt = font.render(f"НУЖНО: {cost}", True, WHITE)
                tot_w = b_txt.get_width() + 28
                start_bx = buy_btn_rect.centerx - tot_w // 2
                surface.blit(b_txt, (start_bx, buy_btn_rect.centery - b_txt.get_height() // 2))
                surface.blit(stellar_cactus_img_s, (start_bx + b_txt.get_width() + 4, buy_btn_rect.centery - 12))

    return back_btn_rect, center_btn_rect, buy_btn_rect, toggle_btn_rect, node_screen_rects, dark_bal_rect, zoom_in_rect, zoom_out_rect, zoom_reset_rect, info_btn_rect

draw_upgrades_screen = draw_upgrade_tree_screen


# -------------------------------------------------------------------------
# ЭКРАН 4: ДОСТИЖЕНИЯ И НАГРАДЫ (Используется ACHIEVEMENTS_DATA из game_data)
# -------------------------------------------------------------------------

def draw_achievements_screen(surface, savedata, mouse_pos, scroll_y=0, filter_status="all", filter_cat="all", bg_time=None):
    check_achievements(savedata)
    if bg_time is None:
        bg_time = pygame.time.get_ticks()
    generate_background(surface, bg_time, custom_cols=((16, 22, 32), (24, 32, 46)))

    total_cnt = len(ACHIEVEMENTS_DATA)
    ach_dict = savedata.get("Achievements", {})
    claimed_cnt = sum(1 for a in ACHIEVEMENTS_DATA if ach_dict.get(a["id"], {}).get("claimed", False))
    ready_cnt = get_unclaimed_achievements_count(savedata)
    in_prog_cnt = max(0, total_cnt - claimed_cnt - ready_cnt)
    completion_pct = int(((claimed_cnt + ready_cnt) / max(1, total_cnt)) * 100)

    # 1. Фильтрация списка достижений
    filtered_list = []
    for ach in ACHIEVEMENTS_DATA:
        aid = ach["id"]
        st = ach_dict.get(aid, {"unlocked": False, "claimed": False})
        is_unlocked = st.get("unlocked", False)
        is_claimed = st.get("claimed", False)

        if filter_cat != "all" and ach.get("category", "") != filter_cat:
            continue
        if filter_status == "ready" and not (is_unlocked and not is_claimed):
            continue
        if filter_status == "progress" and is_unlocked:
            continue
        if filter_status == "claimed" and not is_claimed:
            continue

        filtered_list.append((ach, is_unlocked, is_claimed))

    # 2. Умная сортировка:
    # 0 -> Готовы к награде (первые!)
    # 1 -> В процессе (сортируются по прогрессу от большего к меньшему)
    # 2 -> Выполненные (в конце)
    def sort_key(item):
        ach, unl, clm = item
        if unl and not clm:
            return (0, 0)
        if not unl:
            cur_p, max_p = ach["progress"](savedata)
            return (1, -(cur_p / max(1, max_p)))
        return (2, 0)

    filtered_list.sort(key=sort_key)

    card_w = 560
    card_h = 124
    start_x = 35
    start_y = 192
    row_h = 136
    col_gap = 20

    total_rows = (len(filtered_list) + 1) // 2
    total_content_h = start_y + total_rows * row_h + 20
    max_scroll = max(0, total_content_h - SCREEN_HEIGHT)

    # Клиппинг зоны скролла карточек
    viewport_rect = pygame.Rect(0, 182, SCREEN_WIDTH, SCREEN_HEIGHT - 182)
    surface.set_clip(viewport_rect)

    claim_buttons = []

    if not filtered_list:
        # Пустое состояние
        empty_box = pygame.Rect(SCREEN_WIDTH // 2 - 280, 270, 560, 160)
        pygame.draw.rect(surface, (22, 28, 38), empty_box, border_radius=12)
        pygame.draw.rect(surface, (55, 70, 90), empty_box, width=1, border_radius=12)

        e_title = font.render("Нет достижений в выбранной категории", True, (210, 225, 240))
        surface.blit(e_title, (empty_box.centerx - e_title.get_width() // 2, empty_box.centery - 28))

        e_sub = small_font.render("Переключите фильтры выше или продолжайте сражения в Оазисе!", True, (140, 160, 185))
        surface.blit(e_sub, (empty_box.centerx - e_sub.get_width() // 2, empty_box.centery + 12))
    else:
        # Категорийные цветовые схемы для тегов
        cat_badge_colors = {
            "combat": ((180, 55, 45), (255, 140, 130), "БОЙ"),
            "towers": ((30, 110, 165), (140, 215, 255), "БАШНИ"),
            "greenhouse": ((35, 135, 70), (140, 255, 170), "ФЛОРА"),
            "talents": ((110, 60, 165), (215, 170, 255), "ТАЛАНТЫ")
        }

        for idx, (ach, is_unlocked, is_claimed) in enumerate(filtered_list):
            col = idx % 2
            row = idx // 2
            cx = start_x + col * (card_w + col_gap)
            cy = start_y + row * row_h - scroll_y

            # Отсечение карточек вне экрана
            if cy + card_h < 178 or cy > SCREEN_HEIGHT:
                continue

            aid = ach["id"]
            card_rect = pygame.Rect(cx, cy, card_w, card_h)

            # Фон и обводка карточки
            if is_claimed:
                bg_col = (20, 26, 35)
                border_col = (45, 58, 72)
                border_w = 1
            elif is_unlocked:
                bg_col = (26, 42, 34)
                border_col = (255, 215, 60)
                border_w = 2
            else:
                bg_col = (22, 29, 39)
                border_col = (55, 72, 92)
                border_w = 1

            pygame.draw.rect(surface, bg_col, card_rect, border_radius=10)
            pygame.draw.rect(surface, border_col, card_rect, width=border_w, border_radius=10)

            # Иконка достижения
            i_box = pygame.Rect(cx + 12, cy + 12, 46, 46)
            pygame.draw.rect(surface, (14, 18, 25), i_box, border_radius=8)
            pygame.draw.rect(surface, GOLD if is_unlocked else (60, 75, 92), i_box, width=1, border_radius=8)
            raw_icon = ach.get("icon", trophy_icon)
            icon_id = id(raw_icon)
            scaled_ach_icon = _ach_icon_cache.get(icon_id)
            if scaled_ach_icon is None:
                scaled_ach_icon = pygame.transform.scale(raw_icon, (34, 34))
                _ach_icon_cache[icon_id] = scaled_ach_icon
            surface.blit(scaled_ach_icon, (i_box.centerx - 17, i_box.centery - 17))

            # Тег категории (бейдж)
            cat_key = ach.get("category", "combat")
            bg_badge, fg_badge, badge_lbl = cat_badge_colors.get(cat_key, ((40, 60, 80), WHITE, "ОАЗИС"))
            b_surf = tiny_font.render(badge_lbl, True, fg_badge)
            b_rect = pygame.Rect(cx + 68, cy + 12, b_surf.get_width() + 10, 16)
            pygame.draw.rect(surface, bg_badge, b_rect, border_radius=4)
            surface.blit(b_surf, (b_rect.centerx - b_surf.get_width() // 2, b_rect.centery - b_surf.get_height() // 2))

            # Кнопка действия (Справа)
            btn_w, btn_h = 175, 46
            btn_x = cx + card_w - btn_w - 14
            btn_y = cy + (card_h - btn_h) // 2
            btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            b_hover = btn_rect.collidepoint(mouse_pos)

            # Название достижения (с защитой от наложения на правую кнопку)
            avail_title_w = btn_x - (b_rect.right + 10) - 8
            t_col = GOLD if is_unlocked else (WHITE if not is_claimed else (160, 175, 190))
            use_t_font = font if font.size(ach["title"])[0] <= avail_title_w else small_font
            title_surf = use_t_font.render(ach["title"], True, t_col)
            surface.blit(title_surf, (b_rect.right + 8, cy + 10 if use_t_font == font else cy + 12))

            # Описание (перенос строк с ограничением ширины max_w = 285px)
            d_col = (185, 200, 215) if not is_claimed else (135, 150, 165)
            desc_lines = _render_wrapped_lines(ach["desc"], small_font, 285)
            for l_idx, l_str in enumerate(desc_lines[:2]):
                l_surf = small_font.render(l_str, True, d_col)
                surface.blit(l_surf, (cx + 68, cy + 34 + l_idx * 16))

            # Прогресс
            cur_p, max_p = ach["progress"](savedata)
            p_ratio = min(1.0, cur_p / max(1, max_p))
            bar_rect = pygame.Rect(cx + 68, cy + 74, 280, 18)
            pygame.draw.rect(surface, (12, 16, 22), bar_rect, border_radius=6)
            if p_ratio > 0:
                fill_w = max(6, int(bar_rect.width * p_ratio))
                fill_c = GOLD if is_unlocked else ((45, 180, 85) if not is_claimed else (60, 85, 110))
                pygame.draw.rect(surface, fill_c, (bar_rect.left, bar_rect.top, fill_w, bar_rect.height), border_radius=6)
            pygame.draw.rect(surface, (65, 80, 100), bar_rect, width=1, border_radius=6)

            pct_val = int(p_ratio * 100)
            p_txt_str = f"{cur_p:,} / {max_p:,} ({pct_val}%)".replace(",", " ") if max_p >= 1000 else f"{cur_p} / {max_p} ({pct_val}%)"
            p_txt = tiny_font.render(p_txt_str, True, (230, 240, 250))
            surface.blit(p_txt, (bar_rect.centerx - p_txt.get_width() // 2, bar_rect.centery - p_txt.get_height() // 2))

            if is_claimed:
                pygame.draw.rect(surface, (26, 34, 44), btn_rect, border_radius=8)
                pygame.draw.rect(surface, (50, 65, 80), btn_rect, width=1, border_radius=8)
                lbl = small_font.render("ВЫПОЛНЕНО", True, (130, 160, 190))
                # Рисуем аккуратную векторную галочку перед текстом
                chk_x = btn_rect.centerx - lbl.get_width() // 2 - 12
                chk_y = btn_rect.centery
                pygame.draw.lines(surface, (90, 210, 130), False, [(chk_x, chk_y), (chk_x + 3, chk_y + 4), (chk_x + 8, chk_y - 4)], 2)
                surface.blit(lbl, (chk_x + 13, btn_rect.centery - lbl.get_height() // 2))
            elif is_unlocked:
                pygame.draw.rect(surface, (45, 175, 75) if not b_hover else (60, 205, 95), btn_rect, border_radius=8)
                pygame.draw.rect(surface, YELLOW, btn_rect, width=2, border_radius=8)
                claim_txt = font.render(f"ЗАБРАТЬ +{ach['reward']}", True, WHITE)
                tot_w = claim_txt.get_width() + 26
                start_cx = btn_rect.centerx - tot_w // 2
                surface.blit(claim_txt, (start_cx, btn_rect.centery - claim_txt.get_height() // 2))
                surface.blit(stellar_cactus_img_s, (start_cx + claim_txt.get_width() + 4, btn_rect.centery - 12))
                if btn_rect.bottom >= 182 and btn_rect.top <= SCREEN_HEIGHT:
                    claim_buttons.append((aid, btn_rect, ach['reward']))
            else:
                pygame.draw.rect(surface, (26, 33, 44), btn_rect, border_radius=8)
                pygame.draw.rect(surface, (48, 60, 76), btn_rect, width=1, border_radius=8)
                lbl = small_font.render(f"НАГРАДА: +{ach['reward']}", True, (165, 185, 210))
                tot_w = lbl.get_width() + 26
                start_lx = btn_rect.centerx - tot_w // 2
                surface.blit(lbl, (start_lx, btn_rect.centery - lbl.get_height() // 2))
                surface.blit(stellar_cactus_img_s, (start_lx + lbl.get_width() + 4, btn_rect.centery - 12))

    # Снимаем клиппинг
    surface.set_clip(None)

    # Интерактивный скроллбар справа
    if max_scroll > 0:
        sb_track = pygame.Rect(SCREEN_WIDTH - 14, 185, 6, SCREEN_HEIGHT - 200)
        pygame.draw.rect(surface, (25, 34, 46), sb_track, border_radius=3)
        sb_h = max(35, int(sb_track.height * (sb_track.height / total_content_h)))
        sb_y = sb_track.top + int((sb_track.height - sb_h) * (scroll_y / max_scroll))
        sb_thumb = pygame.Rect(SCREEN_WIDTH - 14, sb_y, 6, sb_h)
        pygame.draw.rect(surface, (90, 135, 185), sb_thumb, border_radius=3)

    # 3. НЕПОДВИЖНЫЙ ВЕРХНИЙ БЛОК: ШАПКА И ДВУХУРОВНЕВЫЕ ТАБЫ (y = 0 .. 180)
    # ---------------------------------------------------------------------
    # Верхняя плашка шапки (y = 0 .. 96)
    header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 96)
    pygame.draw.rect(surface, (14, 18, 26), header_rect)
    pygame.draw.line(surface, (42, 56, 75), (0, 96), (SCREEN_WIDTH, 96), 2)

    # Кнопка «Назад»
    back_rect = pygame.Rect(30, 24, 140, 48)
    b_hov = back_rect.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (215, 65, 65) if b_hov else (180, 50, 50), back_rect, border_radius=8)
    pygame.draw.rect(surface, WHITE, back_rect, width=2, border_radius=8)
    back_txt = font.render("< НАЗАД", True, WHITE)
    surface.blit(back_txt, (back_rect.centerx - back_txt.get_width() // 2, back_rect.centery - back_txt.get_height() // 2))

    # Баланс Звёздных Кактусов
    bal_rect = pygame.Rect(185, 24, 160, 48)
    pygame.draw.rect(surface, (20, 28, 38), bal_rect, border_radius=8)
    pygame.draw.rect(surface, GOLD, bal_rect, width=2, border_radius=8)
    surface.blit(stellar_cactus_img, (190, 25))
    bal_txt = large_font.render(f"{savedata.get('StellarCactuses', 0)}", True, WHITE)
    surface.blit(bal_txt, (246, 31))

    # Заголовок по центру
    title = large_font.render("ДОСТИЖЕНИЯ И НАГРАДЫ", True, GOLD)
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 14))

    # Сводный прогресс в шапке
    prog_info = small_font.render(f"Выполнено: {claimed_cnt + ready_cnt} / {total_cnt} ({completion_pct}%)", True, (210, 225, 240))
    surface.blit(prog_info, (SCREEN_WIDTH // 2 - prog_info.get_width() // 2, 46))

    top_bar_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 72, 260, 8)
    pygame.draw.rect(surface, (12, 16, 22), top_bar_rect, border_radius=4)
    if total_cnt > 0 and (claimed_cnt + ready_cnt) > 0:
        fill_w = max(4, int(top_bar_rect.width * ((claimed_cnt + ready_cnt) / total_cnt)))
        pygame.draw.rect(surface, GOLD, (top_bar_rect.left, top_bar_rect.top, fill_w, top_bar_rect.height), border_radius=4)
    pygame.draw.rect(surface, (60, 75, 95), top_bar_rect, width=1, border_radius=4)

    # Кнопка «Забрать всё» (Справа в шапке)
    claim_all_btn = None
    if ready_cnt > 0:
        unclaimed_stars = sum(
            a["reward"] for a in ACHIEVEMENTS_DATA
            if savedata.get("Achievements", {}).get(a["id"], {}).get("unlocked", False)
            and not savedata.get("Achievements", {}).get(a["id"], {}).get("claimed", False)
        )
        claim_all_btn = pygame.Rect(SCREEN_WIDTH - 255, 24, 225, 48)
        ca_hov = claim_all_btn.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 175, 75) if not ca_hov else (60, 210, 95), claim_all_btn, border_radius=8)
        pygame.draw.rect(surface, GOLD, claim_all_btn, width=2, border_radius=8)
        ca_txt = font.render(f"ЗАБРАТЬ ВСЁ (+{unclaimed_stars})", True, WHITE)
        tot_w = ca_txt.get_width() + 26
        st_x = claim_all_btn.centerx - tot_w // 2
        surface.blit(ca_txt, (st_x, claim_all_btn.centery - ca_txt.get_height() // 2))
        surface.blit(stellar_cactus_img_s, (st_x + ca_txt.get_width() + 4, claim_all_btn.centery - 12))
    else:
        info_badge = pygame.Rect(SCREEN_WIDTH - 240, 24, 210, 48)
        pygame.draw.rect(surface, (22, 28, 38), info_badge, border_radius=8)
        pygame.draw.rect(surface, (50, 65, 82), info_badge, width=1, border_radius=8)
        ib_txt = small_font.render("Все награды получены", True, (135, 155, 180))
        surface.blit(ib_txt, (info_badge.centerx - ib_txt.get_width() // 2, info_badge.centery - ib_txt.get_height() // 2))

    # Двухуровневая плашка с табами и фильтрами (y = 96 .. 180)
    tabs_rect = pygame.Rect(0, 96, SCREEN_WIDTH, 84)
    pygame.draw.rect(surface, (18, 23, 33), tabs_rect)
    pygame.draw.line(surface, (35, 48, 65), (0, 180), (SCREEN_WIDTH, 180), 1)

    tab_actions = {"status": [], "cat": []}

    # Строка 1: Статусные фильтры (y = 102 .. 132)
    status_tabs_def = [
        ("all", f"ВСЕ ({total_cnt})"),
        ("ready", f"К НАГРАДЕ ({ready_cnt})" if ready_cnt > 0 else "К НАГРАДЕ (0)"),
        ("progress", f"В ПРОЦЕССЕ ({in_prog_cnt})"),
        ("claimed", f"ВЫПОЛНЕНЫ ({claimed_cnt})")
    ]
    cur_x = 35
    for s_key, s_label in status_tabs_def:
        s_surf = small_font.render(s_label, True, WHITE if filter_status == s_key else ((255, 220, 90) if s_key == "ready" and ready_cnt > 0 else (170, 185, 205)))
        tw = max(110, s_surf.get_width() + 22)
        s_btn = pygame.Rect(cur_x, 102, tw, 30)
        s_hov = s_btn.collidepoint(mouse_pos)
        is_sel = (filter_status == s_key)

        if is_sel:
            bg_tab = (40, 75, 115)
            bd_tab = (120, 190, 255)
        elif s_key == "ready" and ready_cnt > 0:
            bg_tab = (50, 42, 18) if not s_hov else (70, 58, 25)
            bd_tab = GOLD
        else:
            bg_tab = (25, 34, 48) if not s_hov else (35, 48, 68)
            bd_tab = (55, 72, 95) if not s_hov else (90, 120, 155)

        pygame.draw.rect(surface, bg_tab, s_btn, border_radius=6)
        pygame.draw.rect(surface, bd_tab, s_btn, width=2 if is_sel or (s_key == "ready" and ready_cnt > 0) else 1, border_radius=6)
        surface.blit(s_surf, (s_btn.centerx - s_surf.get_width() // 2, s_btn.centery - s_surf.get_height() // 2))
        tab_actions["status"].append((s_btn, s_key))
        cur_x += tw + 10

    # Навигационная подсказка справа в строке 1
    hint_str = f"Доступно наград: {ready_cnt} | Нажмите ЗАБРАТЬ ВСЁ" if ready_cnt > 0 else "[W/S] или [Колесо Мыши]: прокрутка списка"
    h_surf = tiny_font.render(hint_str, True, (255, 220, 120) if ready_cnt > 0 else (130, 150, 175))
    surface.blit(h_surf, (SCREEN_WIDTH - h_surf.get_width() - 35, 110))

    # Строка 2: Категории (y = 140 .. 172)
    cat_tabs_def = [
        ("all", "Все разделы"),
        ("combat", "Бой и Боссы"),
        ("towers", "Башни и Экономика"),
        ("greenhouse", "Оранжерея и Карты"),
        ("talents", "Таланты")
    ]
    cur_cx = 35
    for c_key, c_label in cat_tabs_def:
        c_surf = small_font.render(c_label, True, (255, 230, 120) if filter_cat == c_key else (160, 180, 205))
        cw = max(110, c_surf.get_width() + 24)
        c_btn = pygame.Rect(cur_cx, 140, cw, 28)
        c_hov = c_btn.collidepoint(mouse_pos)
        is_sel = (filter_cat == c_key)

        bg_c = (35, 55, 80) if is_sel else ((28, 38, 52) if not c_hov else (38, 52, 70))
        bd_c = GOLD if is_sel else ((50, 68, 90) if not c_hov else (85, 115, 150))

        pygame.draw.rect(surface, bg_c, c_btn, border_radius=6)
        pygame.draw.rect(surface, bd_c, c_btn, width=2 if is_sel else 1, border_radius=6)
        surface.blit(c_surf, (c_btn.centerx - c_surf.get_width() // 2, c_btn.centery - c_surf.get_height() // 2))
        tab_actions["cat"].append((c_btn, c_key))
        cur_cx += cw + 10

    return back_rect, claim_buttons, claim_all_btn, tab_actions, max_scroll


def perform_bulk_upgrade(tower, cacti, effects=None, savedata=None):
    if not tower or tower.level >= tower.max_level:
        return cacti, 0
    levels_upgraded = 0
    total_spent = 0
    while tower.level < tower.max_level:
        if cacti >= tower.upgrade_cost:
            success, cost = tower.upgrade(cacti)
            if success:
                cacti -= cost
                total_spent += cost
                levels_upgraded += 1
            else:
                break
        else:
            break
    if levels_upgraded > 0:
        if savedata and "Stats" in savedata:
            savedata["Stats"]["max_tower_level_reached"] = max(
                savedata.get("Stats", {}).get("max_tower_level_reached", 0),
                tower.level
            )
        if effects is not None:
            effects.append(RingEffect(tower.x, tower.y, 65, GOLD))
            effects.append(FloatingText(tower.x, tower.y - 25, f"+{levels_upgraded} УР. (-{total_spent})", GOLD))
            for _ in range(16):
                effects.append(DropSpark(tower.x, tower.y, burst=True))
    return cacti, levels_upgraded


def _get_tower_inspect_static_surf(tower, upgrade_mode):
    key = (tower.type, tower.level, upgrade_mode, tower.target_priority)
    cached = getattr(tower, '_cached_inspect_static', None)
    if cached is not None and cached[0] == key:
        return cached[1], cached[2]

    card_w = 336
    card_h = 250
    static_surf = pygame.Surface((card_w, card_h))
    static_surf.fill((0, 0, 0))
    pygame.draw.rect(static_surf, (18, 24, 32), (0, 0, card_w, card_h), border_radius=12)
    static_surf.set_colorkey((0, 0, 0))

    # Шапка карточки
    header_h = 44
    if upgrade_mode:
        border_col = (255, 175, 45)
        header_bg = (42, 30, 16, 255)
        tag_text = "РЕЖИМ ПРОКАЧКИ"
        tag_col = (255, 195, 75)
    else:
        border_col = (65, 165, 245)
        header_bg = (20, 34, 52, 255)
        tag_text = "ХАРАКТЕРИСТИКИ"
        tag_col = (130, 205, 255)

    pygame.draw.rect(static_surf, header_bg, (0, 0, card_w, header_h), border_top_left_radius=12, border_top_right_radius=12)
    pygame.draw.line(static_surf, (60, 75, 95), (0, header_h), (card_w, header_h), 1)

    # Иконка башни в мини-рамке (кэшированное масштабирование)
    icon_box = pygame.Rect(8, 6, 32, 32)
    pygame.draw.rect(static_surf, (10, 15, 20), icon_box, border_radius=6)
    pygame.draw.rect(static_surf, border_col, icon_box, width=1, border_radius=6)
    scaled_icon = _tower_inspect_icon_cache.get(tower.type)
    if scaled_icon is None:
        scaled_icon = pygame.transform.scale(tower.image, (26, 26))
        _tower_inspect_icon_cache[tower.type] = scaled_icon
    static_surf.blit(scaled_icon, (11, 9))

    # Название башни
    t_titles = {
        "magic": ("МАГИЧЕСКАЯ БАШНЯ", (130, 210, 255)),
        "rock": ("ОГНЕННАЯ БАШНЯ", (255, 150, 60)),
        "freeze": ("ЛЕДЯНАЯ БАШНЯ", (90, 230, 255)),
        "tent": ("ПАЛАТКА СОЛДАТ", (130, 235, 130)),
        "tesla": ("БАШНЯ ТЕСЛА", (100, 225, 255)),
        "farm": ("КАКТУСОВАЯ ФЕРМА", (255, 215, 60))
    }
    t_title, t_color = t_titles.get(tower.type, ("БАШНЯ", WHITE))
    title_lbl = small_font.render(t_title, True, t_color)
    static_surf.blit(title_lbl, (46, 7))

    # Бейдж режима и уровня
    tag_lbl = tiny_font.render(tag_text, True, tag_col)
    static_surf.blit(tag_lbl, (46, 26))

    if tower.level >= tower.max_level:
        lvl_str = "МАКС"
        lvl_c = GOLD
    else:
        if upgrade_mode:
            lvl_str = f"Ур. {tower.level} -> {tower.level + 1}"
            lvl_c = (255, 215, 80)
        else:
            lvl_str = f"Ур. {tower.level}/{tower.max_level}"
            lvl_c = WHITE
    lvl_lbl = small_font.render(lvl_str, True, lvl_c)
    static_surf.blit(lvl_lbl, (card_w - lvl_lbl.get_width() - 10, 12))

    # Тонкая полоска прогресса уровня под шапкой
    bar_rect = pygame.Rect(10, header_h + 5, card_w - 20, 5)
    pygame.draw.rect(static_surf, (40, 50, 60), bar_rect, border_radius=3)
    fill_ratio = min(1.0, tower.level / max(1, tower.max_level))
    if fill_ratio > 0:
        fill_w = max(4, int((card_w - 20) * fill_ratio))
        fill_c = GOLD if tower.level >= tower.max_level else GREEN
        pygame.draw.rect(static_surf, fill_c, (10, header_h + 5, fill_w, 5), border_radius=3)

    cur = tower.get_stats_at_level(tower.level)
    nxt = tower.get_stats_at_level(tower.level + 1) if tower.level < tower.max_level else None

    y_off = header_h + 15
    row_step = 20

    if not upgrade_mode:
        if tower.type == "farm":
            r1_a = small_font.render("Доход волны:", True, WHITE)
            r1_b = small_font.render(f"+{cur['income']} какт.", True, GOLD)
            static_surf.blit(r1_a, (12, y_off))
            static_surf.blit(r1_b, (card_w - r1_b.get_width() - 12, y_off))
            y_off += row_step

            irrig_lvl = savedata.get("Upgrades", {}).get("farm_irrigation", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            if irrig_lvl > 0:
                r2_lbl = small_font.render(f"Аура (R={cur['range']}): +{cur.get('speed_boost', 0)}% темпа башен", True, (130, 245, 160))
            else:
                r2_lbl = small_font.render("Аура: требуется Система Орошения в Древе", True, (180, 190, 200))
            static_surf.blit(r2_lbl, (12, y_off))
            y_off += row_step

            # tot_gold динамический, пропускаем строку
            y_off += row_step

            r4_title = small_font.render("Свойство: ", True, (130, 215, 255))
            r4_val = small_font.render("Орошение и полив", True, WHITE)
            static_surf.blit(r4_title, (12, y_off))
            static_surf.blit(r4_val, (12 + r4_title.get_width(), y_off))
            y_off += row_step

            r5_lbl = tiny_font.render(cur.get('passive_desc', 'Экономика: приносит кактус каждый раунд'), True, (160, 220, 245))
            static_surf.blit(r5_lbl, (12, y_off + 1))
            y_off += row_step
        elif tower.type == "tent":
            r1_a = small_font.render(f"Урон: {cur['damage']}", True, WHITE)
            static_surf.blit(r1_a, (12, y_off))
            y_off += row_step

            r2_a = small_font.render(f"Радиус: {cur['range']} px", True, (220, 230, 240))
            static_surf.blit(r2_a, (12, y_off))
            y_off += row_step

            r3_lbl = small_font.render(f"Призыв бойца: каждые {cur['cooldown']:.2f} сек", True, (220, 230, 240))
            static_surf.blit(r3_lbl, (12, y_off))
            y_off += row_step

            r4_title = small_font.render("Гарнизон: ", True, (130, 215, 255))
            r4_val = small_font.render(cur.get("special_val", f"{cur['soldiers']} воина"), True, GOLD)
            static_surf.blit(r4_title, (12, y_off))
            static_surf.blit(r4_val, (12 + r4_title.get_width(), y_off))
            y_off += row_step

            r5_lbl = tiny_font.render(cur.get('passive_desc', 'Тактика: воины сдерживают мобов на тропе'), True, (160, 220, 245))
            static_surf.blit(r5_lbl, (12, y_off + 1))
            y_off += row_step
        else:
            r1_a = small_font.render(f"Урон: {cur['damage']}", True, WHITE)
            static_surf.blit(r1_a, (12, y_off))
            y_off += row_step

            r2_a = small_font.render(f"Дальность: {cur['range']} px", True, (220, 230, 240))
            static_surf.blit(r2_a, (12, y_off))
            y_off += row_step

            r3_lbl = small_font.render(f"Кулдаун атаки: {cur['cooldown']:.2f} сек", True, (220, 230, 240))
            static_surf.blit(r3_lbl, (12, y_off))
            y_off += row_step

            s_name = cur.get("special_name", "Свойство")
            s_val = cur.get("special_val", "")
            r4_title = small_font.render(f"{s_name}: ", True, (130, 215, 255))
            r4_val = small_font.render(s_val, True, GOLD)
            static_surf.blit(r4_title, (12, y_off))
            static_surf.blit(r4_val, (12 + r4_title.get_width(), y_off))
            y_off += row_step

            p_desc = cur.get('passive_desc', '')
            r5_lbl = tiny_font.render(p_desc, True, (160, 220, 245))
            static_surf.blit(r5_lbl, (12, y_off + 1))
            y_off += row_step
    else:
        # Режим улучшений (диффы)
        if tower.type == "farm":
            if nxt:
                d_inc = nxt.get('income', 0) - cur.get('income', 0)
                c_inc = small_font.render(f"Доход: +{cur.get('income', 0)} -> ", True, WHITE)
                n_inc = small_font.render(f"+{nxt.get('income', 0)} (+{d_inc})", True, GREEN)
                static_surf.blit(c_inc, (12, y_off))
                static_surf.blit(n_inc, (12 + c_inc.get_width(), y_off))
                y_off += row_step

                nxt_bst = nxt.get('speed_boost', 0)
                cur_bst = cur.get('speed_boost', 0)
                c_bst = small_font.render(f"Аура темпа: +{cur_bst}% -> ", True, WHITE)
                n_bst = small_font.render(f"+{nxt_bst}% (+{nxt_bst - cur_bst}%)", True, (120, 255, 150))
                static_surf.blit(c_bst, (12, y_off))
                static_surf.blit(n_bst, (12 + c_bst.get_width(), y_off))
                y_off += row_step

                payback = nxt['upgrade_cost'] // max(1, d_inc)
                r_info = small_font.render(f"Окупаемость: {payback} волн | Полив раз в {int(nxt.get('cooldown', 18))}с", True, (255, 215, 90))
                static_surf.blit(r_info, (12, y_off))
                y_off += row_step

                r_prop = small_font.render("Свойство: Ускорение башен + бонусные кактусы", True, (130, 215, 255))
                static_surf.blit(r_prop, (12, y_off))
                y_off += row_step

                r_hint = tiny_font.render("Орошает соседние башни и сбрасывает урожай!", True, (160, 220, 245))
                static_surf.blit(r_hint, (12, y_off + 1))
                y_off += row_step
            else:
                max_info = font.render("Максимальный уровень развития!", True, GOLD)
                static_surf.blit(max_info, (card_w // 2 - max_info.get_width() // 2, y_off + 20))
        elif tower.type == "tent":
            if nxt:
                d_dmg = round(nxt['damage'] - cur['damage'], 1)
                d_dmg_str = f"(+{d_dmg:g})" if d_dmg > 0 else ""
                c_dmg = small_font.render(f"Урон воина: {cur['damage']} -> ", True, WHITE)
                n_dmg = small_font.render(f"{nxt['damage']} {d_dmg_str}", True, GREEN)
                static_surf.blit(c_dmg, (12, y_off))
                static_surf.blit(n_dmg, (12 + c_dmg.get_width(), y_off))
                y_off += row_step

                d_rng = nxt['range'] - cur['range']
                d_rng_str = f"(+{d_rng})" if d_rng > 0 else ""
                c_rng = small_font.render(f"Патруль: {cur['range']}px -> ", True, (220, 230, 240))
                n_rng = small_font.render(f"{nxt['range']}px {d_rng_str}", True, GREEN)
                static_surf.blit(c_rng, (12, y_off))
                static_surf.blit(n_rng, (12 + c_rng.get_width(), y_off))
                y_off += row_step

                d_cd = round(nxt['cooldown'] - cur['cooldown'], 2)
                d_cd_str = f"({d_cd:+.2f}с)" if abs(d_cd) > 0.001 else ""
                c_cd = small_font.render(f"Призыв: {cur['cooldown']:.2f}с -> ", True, (220, 230, 240))
                n_cd = small_font.render(f"{nxt['cooldown']:.2f}с {d_cd_str}", True, GREEN if d_cd < 0 else WHITE)
                static_surf.blit(c_cd, (12, y_off))
                static_surf.blit(n_cd, (12 + c_cd.get_width(), y_off))
                y_off += row_step

                d_dps = round(nxt['dps'] - cur['dps'], 1)
                c_dps = small_font.render(f"DPS отряда: {cur['dps']:.1f} -> ", True, (255, 215, 90))
                n_dps = small_font.render(f"{nxt['dps']:.1f} (+{d_dps:.1f})", True, GREEN)
                static_surf.blit(c_dps, (12, y_off))
                static_surf.blit(n_dps, (12 + c_dps.get_width(), y_off))
                y_off += row_step

                if nxt.get('soldiers', 0) > cur.get('soldiers', 0):
                    c_spec = small_font.render(f"Гарнизон: {cur.get('soldiers', 0)} -> ", True, (130, 215, 255))
                    n_spec = small_font.render(f"{nxt.get('soldiers', 0)} воина (+1 боец!)", True, GREEN)
                else:
                    d_hp = nxt.get('soldier_hp', 0) - cur.get('soldier_hp', 0)
                    c_spec = small_font.render(f"HP воина: {cur.get('soldier_hp', 0)} -> ", True, (130, 215, 255))
                    n_spec = small_font.render(f"{nxt.get('soldier_hp', 0)} HP (+{d_hp})", True, GREEN)
                static_surf.blit(c_spec, (12, y_off))
                static_surf.blit(n_spec, (12 + c_spec.get_width(), y_off))
                y_off += row_step
            else:
                max_info = font.render("Максимальный уровень развития!", True, GOLD)
                static_surf.blit(max_info, (card_w // 2 - max_info.get_width() // 2, y_off + 20))
        elif nxt:
            d_dmg = round(nxt['damage'] - cur['damage'], 1)
            d_dmg_str = f"(+{d_dmg:g})" if d_dmg > 0 else ""
            c_dmg = small_font.render(f"Урон: {cur['damage']} -> ", True, WHITE)
            n_dmg = small_font.render(f"{nxt['damage']} {d_dmg_str}", True, GREEN)
            static_surf.blit(c_dmg, (12, y_off))
            static_surf.blit(n_dmg, (12 + c_dmg.get_width(), y_off))
            y_off += row_step

            d_rng = nxt['range'] - cur['range']
            d_rng_str = f"(+{d_rng})" if d_rng > 0 else ""
            c_rng = small_font.render(f"Дальность: {cur['range']} -> ", True, (220, 230, 240))
            n_rng = small_font.render(f"{nxt['range']} {d_rng_str}", True, GREEN)
            static_surf.blit(c_rng, (12, y_off))
            static_surf.blit(n_rng, (12 + c_rng.get_width(), y_off))
            y_off += row_step

            d_cd = round(nxt['cooldown'] - cur['cooldown'], 2)
            d_cd_str = f"({d_cd:+.2f}с)" if abs(d_cd) > 0.001 else ""
            c_cd = small_font.render(f"Кулдаун: {cur['cooldown']:.2f}с -> ", True, (220, 230, 240))
            n_cd = small_font.render(f"{nxt['cooldown']:.2f}с {d_cd_str}", True, GREEN if d_cd < 0 else WHITE)
            static_surf.blit(c_cd, (12, y_off))
            static_surf.blit(n_cd, (12 + c_cd.get_width(), y_off))
            y_off += row_step

            d_dps = round(nxt['dps'] - cur['dps'], 1)
            c_dps = small_font.render(f"DPS: {cur['dps']:.1f} -> ", True, (255, 215, 90))
            n_dps = small_font.render(f"{nxt['dps']:.1f} (+{d_dps:.1f})", True, GREEN)
            static_surf.blit(c_dps, (12, y_off))
            static_surf.blit(n_dps, (12 + c_dps.get_width(), y_off))
            y_off += row_step

            s_name = cur.get("special_name", "Спец-стата")
            if tower.type == "magic":
                d_crit = nxt.get('crit_chance', 0) - cur.get('crit_chance', 0)
                s_cur_str = f"{cur.get('crit_chance', 0)}%"
                s_nxt_str = f"{nxt.get('crit_chance', 0)}% (+{d_crit}%)"
            elif tower.type == "rock":
                d_spl = nxt.get('splash', 0) - cur.get('splash', 0)
                s_cur_str = f"{cur.get('splash', 0)}px"
                s_nxt_str = f"{nxt.get('splash', 0)}px (+{d_spl}px)"
            elif tower.type == "freeze":
                d_slow = nxt.get('slow_pct', 0) - cur.get('slow_pct', 0)
                d_dur = round(nxt.get('slow_dur', 0) - cur.get('slow_dur', 0), 1)
                s_cur_str = f"{cur.get('slow_pct', 0)}%"
                s_nxt_str = f"{nxt.get('slow_pct', 0)}% (+{d_slow}%, +{d_dur:g}с)"
            elif tower.type == "tesla":
                if nxt.get('chains', 0) > cur.get('chains', 0):
                    s_cur_str = f"{cur.get('chains', 0)} цели"
                    s_nxt_str = f"{nxt.get('chains', 0)} цели (+1 цель!)"
                else:
                    s_cur_str = f"{cur.get('chains', 0)} цели"
                    s_nxt_str = f"{nxt.get('chains', 0)} цели (макс.)"
            else:
                s_cur_str = "-"
                s_nxt_str = "-"

            c_spec = small_font.render(f"{s_name}: {s_cur_str} -> ", True, (130, 215, 255))
            n_spec = small_font.render(s_nxt_str, True, GREEN)
            static_surf.blit(c_spec, (12, y_off))
            static_surf.blit(n_spec, (12 + c_spec.get_width(), y_off))
            y_off += row_step
        else:
            max_info = font.render("Максимальный уровень развития!", True, GOLD)
            static_surf.blit(max_info, (card_w // 2 - max_info.get_width() // 2, y_off + 20))

    # Кнопка приоритета цели (базовая отрисовка)
    t_mode_names = {
        "FIRST": "Первый",
        "LAST": "Последний",
        "STRONGEST": "Сильный",
        "WEAKEST": "Слабый",
        "CLOSEST": "Близкий"
    }
    cur_t_mode = t_mode_names.get(tower.target_priority, "Первый")
    target_row_y = y_off + 4
    target_btn_local = pygame.Rect(10, target_row_y, card_w - 20, 24)

    if tower.type == "farm":
        pygame.draw.rect(static_surf, (22, 38, 26), target_btn_local, border_radius=5)
        pygame.draw.rect(static_surf, (60, 150, 80), target_btn_local, width=1, border_radius=5)
        t_lbl = tiny_font.render("ПРОИЗВОДСТВО: АВТО-СБОР УРОЖАЯ", True, (140, 235, 160))
    elif tower.type == "tent":
        pygame.draw.rect(static_surf, (22, 54, 34), target_btn_local, border_radius=5)
        pygame.draw.rect(static_surf, (70, 210, 120), target_btn_local, width=1, border_radius=5)
        t_lbl = tiny_font.render("[ФЛАГ / R] ТОЧКА СБОРА СОЛДАТ", True, (160, 255, 190))
    else:
        pygame.draw.rect(static_surf, (24, 32, 42), target_btn_local, border_radius=5)
        pygame.draw.rect(static_surf, (55, 75, 95), target_btn_local, width=1, border_radius=5)
        t_lbl = tiny_font.render(f"[T] ЦЕЛЬ: {cur_t_mode.upper()}", True, (190, 215, 240))
    static_surf.blit(t_lbl, (target_btn_local.centerx - t_lbl.get_width() // 2, target_btn_local.centery - t_lbl.get_height() // 2))

    # Обводка всей карточки
    pygame.draw.rect(static_surf, border_col, (0, 0, card_w, card_h), width=2, border_radius=12)

    tower._cached_inspect_static = (key, static_surf, target_row_y)
    return static_surf, target_row_y


def draw_tower_inspect_card(surface, tower, upgrade_mode, cacti, mouse_pos, savedata=None):
    """
    Отрисовывает информационное / улучшающее меню башни:
    - Сверхбыстрый прямой рендеринг: статическая часть кэшируется, 0 промежуточных альфа-буферов.
    - В режиме оптимизации пропускается тень для идеального 60 FPS.
    """
    card_w = 336
    card_h = 250

    # Умное позиционирование относительно башни
    card_x = tower.x - card_w // 2
    card_x = max(15, min(SCREEN_WIDTH - card_w - 15, card_x))

    card_y = tower.y - card_h - 26
    if card_y < 72:
        card_y = tower.y + 44
    if card_y + card_h > SCREEN_HEIGHT - 82:
        if tower.x > SCREEN_WIDTH // 2:
            card_x = max(15, tower.x - card_w - 38)
        else:
            card_x = min(SCREEN_WIDTH - card_w - 15, tower.x + 38)
        card_y = max(72, min(SCREEN_HEIGHT - card_h - 82, tower.y - card_h // 2))

    card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

    # Соединительная линия между башней и меню
    conn_color = (255, 175, 45) if upgrade_mode else (65, 160, 245)
    pygame.draw.line(surface, conn_color, (card_rect.centerx, card_rect.centery), (tower.x, tower.y), 2)

    # Кэшированная тень карточки (только в нормальном режиме графики для максимального FPS)
    global _cached_card_shadow_surf
    if not IS_ANDROID and get_graphics_preset() != "optimized":
        if _cached_card_shadow_surf is None:
            _cached_card_shadow_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(_cached_card_shadow_surf, (0, 0, 0, 110), (0, 0, card_w, card_h), border_radius=12)
        surface.blit(_cached_card_shadow_surf, (card_x + 3, card_y + 5))

    # Статическая пререндеренная карточка выводится напрямую
    static_surf, target_row_y = _get_tower_inspect_static_surf(tower, upgrade_mode)
    surface.blit(static_surf, card_rect.topleft)

    # Динамические статы (ограничение до 0.35с для предотвращения сброса шрифтового кэша)
    now = time.time()
    if now - getattr(tower, '_inspect_dyn_time', 0.0) >= 0.35 or not hasattr(tower, '_cached_dyn_dps_surf'):
        tower._inspect_dyn_time = now
        cur_dps = getattr(tower, 'dps', 0.0)
        dyn_dps = tower.get_dynamic_dps() if hasattr(tower, 'get_dynamic_dps') else 0.0
        tot_dmg = getattr(tower, 'total_damage_dealt', 0.0)
        tot_gold = getattr(tower, 'total_gold_earned', 0)

        tower._cached_dyn_dps_surf = small_font.render(f"DPS: {cur_dps:.1f} (Факт: {dyn_dps:.1f})", True, (255, 215, 90))
        tower._cached_tot_dmg_surf = tiny_font.render(f"Урон: {int(tot_dmg):,}", True, (200, 240, 255))
        tower._cached_tot_gold_surf = small_font.render(f"Всего заработано: +{tot_gold} какт.", True, (255, 220, 100))

    if not upgrade_mode:
        header_h = 44
        y_off = card_y + header_h + 15
        row_step = 20
        if tower.type == "farm":
            surface.blit(tower._cached_tot_gold_surf, (card_x + 12, y_off + row_step * 2))
        else:
            dps_s = tower._cached_dyn_dps_surf
            surface.blit(dps_s, (card_x + card_w - dps_s.get_width() - 12, y_off))
            dmg_s = tower._cached_tot_dmg_surf
            surface.blit(dmg_s, (card_x + card_w - dmg_s.get_width() - 12, y_off + row_step + 2))

    # Строка приоритета цели / точки сбора
    target_btn_screen = pygame.Rect(card_x + 10, card_y + target_row_y, card_w - 20, 24)
    if tower.type == "farm":
        target_btn_screen = None
    elif tower.type == "tent":
        t_hov = target_btn_screen.collidepoint(mouse_pos)
        is_rally_active = getattr(tower, '_rally_selecting', False)
        if is_rally_active:
            pygame.draw.rect(surface, (30, 85, 45), target_btn_screen, border_radius=5)
            pygame.draw.rect(surface, (110, 255, 160), target_btn_screen, width=2, border_radius=5)
            k_t = "rally_active_txt"
            if k_t not in _tower_inspect_btn_cache:
                _tower_inspect_btn_cache[k_t] = tiny_font.render(">> ВЫБЕРИТЕ ТОЧКУ НА КАРТЕ <<", True, (240, 255, 240))
            t_lbl = _tower_inspect_btn_cache[k_t]
            surface.blit(t_lbl, (target_btn_screen.centerx - t_lbl.get_width() // 2, target_btn_screen.centery - t_lbl.get_height() // 2))
        elif t_hov:
            pygame.draw.rect(surface, (32, 75, 48), target_btn_screen, border_radius=5)
            pygame.draw.rect(surface, (90, 240, 140), target_btn_screen, width=1, border_radius=5)
            k_t = "rally_hover_txt"
            if k_t not in _tower_inspect_btn_cache:
                _tower_inspect_btn_cache[k_t] = tiny_font.render("[КЛИК / R] СМЕНИТЬ ТОЧКУ СБОРА", True, (215, 255, 225))
            t_lbl = _tower_inspect_btn_cache[k_t]
            surface.blit(t_lbl, (target_btn_screen.centerx - t_lbl.get_width() // 2, target_btn_screen.centery - t_lbl.get_height() // 2))
    else:
        t_hov = target_btn_screen.collidepoint(mouse_pos)
        if t_hov:
            pygame.draw.rect(surface, (35, 48, 62), target_btn_screen, border_radius=5)
            pygame.draw.rect(surface, (90, 180, 255), target_btn_screen, width=1, border_radius=5)
            t_mode_names = {"FIRST": "Первый", "LAST": "Последний", "STRONGEST": "Сильный", "WEAKEST": "Слабый", "CLOSEST": "Близкий"}
            cur_t_mode = t_mode_names.get(tower.target_priority, "Первый")
            k_t = ("target_txt", cur_t_mode)
            if k_t not in _tower_inspect_btn_cache:
                _tower_inspect_btn_cache[k_t] = tiny_font.render(f"[T] ЦЕЛЬ: {cur_t_mode.upper()}", True, (140, 220, 255))
            t_lbl = _tower_inspect_btn_cache[k_t]
            surface.blit(t_lbl, (target_btn_screen.centerx - t_lbl.get_width() // 2, target_btn_screen.centery - t_lbl.get_height() // 2))

    # Нижние кнопки действия (Апгрейд + Макс + Продажа)
    btn_h = 32
    btn_y = card_y + card_h - btn_h - 9

    s_data = savedata if isinstance(savedata, dict) else globals().get('savedata', None)
    has_bulk = (s_data.get("Upgrades", {}).get("bulk_upgrade", 0) > 0) if s_data and isinstance(s_data, dict) else False
    can_upgrade = (tower.level < tower.max_level)
    max_screen_rect = None

    if has_bulk and can_upgrade:
        sell_w = 72
        max_w = 64
        upg_w = card_w - 20 - sell_w - max_w - 12

        upg_screen_rect = pygame.Rect(card_x + 10, btn_y, upg_w, btn_h)
        upg_hovered = upg_screen_rect.collidepoint(mouse_pos)

        max_screen_rect = pygame.Rect(card_x + 10 + upg_w + 6, btn_y, max_w, btn_h)
        max_hovered = max_screen_rect.collidepoint(mouse_pos)

        sell_screen_rect = pygame.Rect(card_x + 10 + upg_w + 6 + max_w + 6, btn_y, sell_w, btn_h)
        sell_hovered = sell_screen_rect.collidepoint(mouse_pos)
    else:
        sell_w = 98
        upg_w = card_w - 20 - sell_w - 8

        upg_screen_rect = pygame.Rect(card_x + 10, btn_y, upg_w, btn_h)
        upg_hovered = upg_screen_rect.collidepoint(mouse_pos)

        sell_screen_rect = pygame.Rect(card_x + 10 + upg_w + 8, btn_y, sell_w, btn_h)
        sell_hovered = sell_screen_rect.collidepoint(mouse_pos)

    sell_value = max(20, int(tower.total_invested * 0.70))

    # Отрисовка кнопки апгрейда
    if can_upgrade:
        can_afford = (cacti >= tower.upgrade_cost)
        if can_afford:
            bg_c = (35, 150, 60) if not upg_hovered else (45, 180, 75)
            bd_c = GOLD if upgrade_mode else GREEN
            k_u = ("upg_ok", tower.upgrade_cost)
            if k_u not in _tower_inspect_btn_cache:
                _tower_inspect_btn_cache[k_u] = small_font.render(f"[U] {tower.upgrade_cost}", True, WHITE)
            btn_txt = _tower_inspect_btn_cache[k_u]
        else:
            missing = tower.upgrade_cost - cacti
            bg_c = (90, 25, 30) if not upg_hovered else (115, 35, 40)
            bd_c = RED
            k_u = ("upg_no", tower.upgrade_cost, missing)
            if k_u not in _tower_inspect_btn_cache:
                if len(_tower_inspect_btn_cache) > 64:
                    _tower_inspect_btn_cache.clear()
                _tower_inspect_btn_cache[k_u] = small_font.render(f"{tower.upgrade_cost} (-{missing})", True, (255, 200, 200))
            btn_txt = _tower_inspect_btn_cache[k_u]

        pygame.draw.rect(surface, bg_c, upg_screen_rect, border_radius=6)
        pygame.draw.rect(surface, bd_c, upg_screen_rect, width=2 if upg_hovered else 1, border_radius=6)

        tot_btn_w = cactus_img_s.get_width() + 4 + btn_txt.get_width()
        b_x = upg_screen_rect.centerx - tot_btn_w // 2
        surface.blit(cactus_img_s, (b_x, upg_screen_rect.centery - cactus_img_s.get_height() // 2))
        surface.blit(btn_txt, (b_x + cactus_img_s.get_width() + 4, upg_screen_rect.centery - btn_txt.get_height() // 2))

        # Отрисовка кнопки МАКС
        if max_screen_rect is not None:
            can_afford_any = (cacti >= tower.upgrade_cost)
            m_bg = (30, 80, 115) if not max_hovered else (45, 105, 145)
            m_bd = (90, 200, 255) if can_afford_any else (125, 75, 80)
            pygame.draw.rect(surface, m_bg, max_screen_rect, border_radius=6)
            pygame.draw.rect(surface, m_bd, max_screen_rect, width=2 if max_hovered else 1, border_radius=6)
            k_m = ("max_txt", can_afford_any)
            if k_m not in _tower_inspect_btn_cache:
                _tower_inspect_btn_cache[k_m] = tiny_font.render("МАКС", True, (210, 245, 255) if can_afford_any else (180, 145, 145))
            m_txt = _tower_inspect_btn_cache[k_m]
            surface.blit(m_txt, (max_screen_rect.centerx - m_txt.get_width() // 2, max_screen_rect.centery - m_txt.get_height() // 2))
    else:
        pygame.draw.rect(surface, (60, 50, 20), upg_screen_rect, border_radius=6)
        pygame.draw.rect(surface, GOLD, upg_screen_rect, width=1, border_radius=6)
        k_ml = "max_lvl_done"
        if k_ml not in _tower_inspect_btn_cache:
            _tower_inspect_btn_cache[k_ml] = tiny_font.render("МАКС. УРОВЕНЬ", True, GOLD)
        max_txt = _tower_inspect_btn_cache[k_ml]
        surface.blit(max_txt, (upg_screen_rect.centerx - max_txt.get_width() // 2, upg_screen_rect.centery - max_txt.get_height() // 2))

    # Отрисовка кнопки продажи
    pygame.draw.rect(surface, (110, 35, 40) if sell_hovered else (75, 25, 30), sell_screen_rect, border_radius=6)
    pygame.draw.rect(surface, (240, 80, 85) if sell_hovered else (150, 50, 55), sell_screen_rect, width=2 if sell_hovered else 1, border_radius=6)
    k_s = ("sell_val", sell_value)
    if k_s not in _tower_inspect_btn_cache:
        _tower_inspect_btn_cache[k_s] = small_font.render(f"[S]+{sell_value}", True, (255, 230, 230))
    s_txt = _tower_inspect_btn_cache[k_s]
    s_tot = cactus_img_s.get_width() + 3 + s_txt.get_width()
    sx = sell_screen_rect.centerx - s_tot // 2
    surface.blit(cactus_img_s, (sx, sell_screen_rect.centery - cactus_img_s.get_height() // 2))
    surface.blit(s_txt, (sx + cactus_img_s.get_width() + 3, sell_screen_rect.centery - s_txt.get_height() // 2))

    return card_rect, upg_screen_rect, target_btn_screen, sell_screen_rect, max_screen_rect



def draw_custom_map_setup_modal(surface, savedata, mouse_pos):
    """
    Модальное окно настройки Кастомной Карты 10 («Оазис Создателя»):
    - Ввод / рандомизация сида
    - Множитель HP
    - Множитель скорости
    - Стартовый баланс кактусов
    - Визуальный стиль биома
    - Бесконечный режим (Endless)
    """
    cfg = savedata.setdefault("CustomMapConfig", {
        "seed": 777,
        "hp_mult": 1.5,
        "spd_mult": 1.0,
        "start_gold": 400,
        "biome_style": 0,
        "endless": True
    })

    # Затемняющий оверлей
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 185))
    surface.blit(overlay, (0, 0))

    box_w, box_h = 840, 614
    box_x = (SCREEN_WIDTH - box_w) // 2
    box_y = (SCREEN_HEIGHT - box_h) // 2
    modal_rect = pygame.Rect(box_x, box_y, box_w, box_h)

    pygame.draw.rect(surface, (22, 18, 32), modal_rect, border_radius=14)
    pygame.draw.rect(surface, (255, 120, 220), modal_rect, width=2, border_radius=14)

    # Шапка
    header_rect = pygame.Rect(box_x, box_y, box_w, 54)
    pygame.draw.rect(surface, (38, 22, 54), header_rect, border_top_left_radius=14, border_top_right_radius=14)
    pygame.draw.line(surface, (140, 60, 150), (box_x, box_y + 54), (box_x + box_w, box_y + 54), 2)

    title_txt = font.render("НАСТРОЙКА КАРТЫ 10: ОАЗИС СОЗДАТЕЛЯ (ГЕНЕРАТОР)", True, (255, 235, 255))
    surface.blit(title_txt, (box_x + 24, box_y + 14))

    # Кнопка закрытия [X]
    close_btn = pygame.Rect(box_x + box_w - 44, box_y + 11, 32, 32)
    cl_hov = close_btn.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (160, 40, 60) if cl_hov else (90, 25, 40), close_btn, border_radius=6)
    pygame.draw.rect(surface, (255, 100, 120) if cl_hov else (180, 50, 75), close_btn, width=1, border_radius=6)
    x_txt = font.render("X", True, WHITE)
    surface.blit(x_txt, (close_btn.centerx - x_txt.get_width() // 2, close_btn.centery - x_txt.get_height() // 2 - 1))

    action_buttons = []

    y_pos = box_y + 64
    row_h = 49

    # 1. СИД КАРТЫ
    lbl1 = font.render("1. Сид карты (Seed):", True, (245, 210, 255))
    surface.blit(lbl1, (box_x + 26, y_pos + 6))

    seed_val = cfg.get("seed", 777)
    seed_box = pygame.Rect(box_x + 280, y_pos, 100, 36)
    pygame.draw.rect(surface, (14, 10, 20), seed_box, border_radius=6)
    pygame.draw.rect(surface, (200, 100, 220), seed_box, width=1, border_radius=6)
    s_txt = font.render(f"{seed_val}", True, GOLD)
    surface.blit(s_txt, (seed_box.centerx - s_txt.get_width() // 2, seed_box.centery - s_txt.get_height() // 2))

    s_btns = [
        ("-100", -100, 48),
        ("-1", -1, 36),
        ("+1", 1, 36),
        ("+100", 100, 48),
        ("Рандом", "rand", 82)
    ]
    cur_bx = box_x + 388
    for s_label, s_act, s_bw in s_btns:
        b_r = pygame.Rect(cur_bx, y_pos, s_bw, 36)
        b_hov = b_r.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (65, 35, 90) if b_hov else (40, 22, 58), b_r, border_radius=6)
        pygame.draw.rect(surface, (230, 130, 240) if b_hov else (140, 70, 160), b_r, width=1, border_radius=6)
        bt_txt = tiny_font.render(s_label, True, (255, 235, 255) if b_hov else (220, 190, 230))
        surface.blit(bt_txt, (b_r.centerx - bt_txt.get_width() // 2, b_r.centery - bt_txt.get_height() // 2))
        action_buttons.append((b_r, "seed", s_act))
        cur_bx += s_bw + 6

    y_pos += row_h

    # 2. МНОЖИТЕЛЬ HP МОБОВ
    lbl2 = font.render("2. Здоровье врагов (HP):", True, (245, 210, 255))
    surface.blit(lbl2, (box_x + 26, y_pos + 6))
    hp_opts = [0.75, 1.0, 1.5, 2.0, 3.0]
    cur_hp = cfg.get("hp_mult", 1.5)
    for idx, h_val in enumerate(hp_opts):
        b_r = pygame.Rect(box_x + 280 + idx * 88, y_pos, 80, 36)
        is_sel = abs(cur_hp - h_val) < 0.05
        b_hov = b_r.collidepoint(mouse_pos)
        bg = (40, 130, 60) if is_sel else ((60, 32, 85) if b_hov else (34, 18, 50))
        bd = (120, 255, 150) if is_sel else ((220, 110, 230) if b_hov else (110, 60, 130))
        pygame.draw.rect(surface, bg, b_r, border_radius=6)
        pygame.draw.rect(surface, bd, b_r, width=2 if is_sel else 1, border_radius=6)
        ht_txt = font.render(f"{h_val}x", True, WHITE if is_sel else (220, 190, 230))
        surface.blit(ht_txt, (b_r.centerx - ht_txt.get_width() // 2, b_r.centery - ht_txt.get_height() // 2))
        action_buttons.append((b_r, "hp_mult", h_val))

    y_pos += row_h

    # 3. МНОЖИТЕЛЬ СКОРОСТИ
    lbl3 = font.render("3. Скорость врагов:", True, (245, 210, 255))
    surface.blit(lbl3, (box_x + 26, y_pos + 6))
    spd_opts = [0.8, 1.0, 1.2, 1.4]
    cur_spd = cfg.get("spd_mult", 1.0)
    for idx, s_val in enumerate(spd_opts):
        b_r = pygame.Rect(box_x + 280 + idx * 98, y_pos, 90, 36)
        is_sel = abs(cur_spd - s_val) < 0.05
        b_hov = b_r.collidepoint(mouse_pos)
        bg = (40, 130, 60) if is_sel else ((60, 32, 85) if b_hov else (34, 18, 50))
        bd = (120, 255, 150) if is_sel else ((220, 110, 230) if b_hov else (110, 60, 130))
        pygame.draw.rect(surface, bg, b_r, border_radius=6)
        pygame.draw.rect(surface, bd, b_r, width=2 if is_sel else 1, border_radius=6)
        st_txt = font.render(f"{s_val}x", True, WHITE if is_sel else (220, 190, 230))
        surface.blit(st_txt, (b_r.centerx - st_txt.get_width() // 2, b_r.centery - st_txt.get_height() // 2))
        action_buttons.append((b_r, "spd_mult", s_val))

    y_pos += row_h

    # 4. СТАРТОВЫЙ БАЛАНС
    lbl4 = font.render("4. Стартовые кактусы:", True, (245, 210, 255))
    surface.blit(lbl4, (box_x + 26, y_pos + 6))
    gold_opts = [200, 400, 800, 1500, 3000]
    cur_gold = cfg.get("start_gold", 400)
    for idx, g_val in enumerate(gold_opts):
        b_r = pygame.Rect(box_x + 280 + idx * 88, y_pos, 80, 36)
        is_sel = (cur_gold == g_val)
        b_hov = b_r.collidepoint(mouse_pos)
        bg = (40, 130, 60) if is_sel else ((60, 32, 85) if b_hov else (34, 18, 50))
        bd = (120, 255, 150) if is_sel else ((220, 110, 230) if b_hov else (110, 60, 130))
        pygame.draw.rect(surface, bg, b_r, border_radius=6)
        pygame.draw.rect(surface, bd, b_r, width=2 if is_sel else 1, border_radius=6)
        gt_txt = small_font.render(f"{g_val}", True, GOLD if is_sel else (230, 200, 150))
        surface.blit(gt_txt, (b_r.centerx - gt_txt.get_width() // 2, b_r.centery - gt_txt.get_height() // 2))
        action_buttons.append((b_r, "start_gold", g_val))

    y_pos += row_h

    # 5. КАКТУСЫ С ВРАГОВ
    lbl5 = font.render("5. Кактусы с врагов:", True, (245, 210, 255))
    surface.blit(lbl5, (box_x + 26, y_pos + 6))
    cacti_opts = [(1.0, "1.0x (База)"), (1.25, "1.25x (+25%)"), (1.5, "1.5x (+50%)"), (2.0, "2.0x (x2)")]
    cur_cacti = cfg.get("cacti_mult", 1.0)
    for idx, (c_val, c_lbl) in enumerate(cacti_opts):
        b_r = pygame.Rect(box_x + 280 + idx * 115, y_pos, 108, 36)
        is_sel = abs(cur_cacti - c_val) < 0.05
        b_hov = b_r.collidepoint(mouse_pos)
        bg = (40, 130, 60) if is_sel else ((60, 32, 85) if b_hov else (34, 18, 50))
        bd = (120, 255, 150) if is_sel else ((220, 110, 230) if b_hov else (110, 60, 130))
        pygame.draw.rect(surface, bg, b_r, border_radius=6)
        pygame.draw.rect(surface, bd, b_r, width=2 if is_sel else 1, border_radius=6)
        ct_txt = small_font.render(c_lbl, True, WHITE if is_sel else (220, 190, 230))
        surface.blit(ct_txt, (b_r.centerx - ct_txt.get_width() // 2, b_r.centery - ct_txt.get_height() // 2))
        action_buttons.append((b_r, "cacti_mult", c_val))

    y_pos += row_h

    # 6. ТЕМА БИОМА
    lbl6 = font.render("6. Визуал биома:", True, (245, 210, 255))
    surface.blit(lbl6, (box_x + 26, y_pos + 6))
    biome_opts = [(0, "Астрал"), (1, "Луг"), (2, "Снег"), (3, "Каньон"), (4, "Бездна")]
    cur_biome = cfg.get("biome_style", 0)
    for idx, (b_id, b_name) in enumerate(biome_opts):
        b_r = pygame.Rect(box_x + 280 + idx * 88, y_pos, 80, 36)
        is_sel = (cur_biome == b_id)
        b_hov = b_r.collidepoint(mouse_pos)
        bg = (40, 130, 60) if is_sel else ((60, 32, 85) if b_hov else (34, 18, 50))
        bd = (120, 255, 150) if is_sel else ((220, 110, 230) if b_hov else (110, 60, 130))
        pygame.draw.rect(surface, bg, b_r, border_radius=6)
        pygame.draw.rect(surface, bd, b_r, width=2 if is_sel else 1, border_radius=6)
        bt_txt = small_font.render(b_name, True, WHITE if is_sel else (220, 190, 230))
        surface.blit(bt_txt, (b_r.centerx - bt_txt.get_width() // 2, b_r.centery - bt_txt.get_height() // 2))
        action_buttons.append((b_r, "biome_style", b_id))

    y_pos += row_h

    # 7. РЕЖИМ ВОЛН
    lbl7 = font.render("7. Режим волн:", True, (245, 210, 255))
    surface.blit(lbl7, (box_x + 26, y_pos + 6))
    is_endless = cfg.get("endless", True)

    b_camp = pygame.Rect(box_x + 280, y_pos, 190, 36)
    b_end = pygame.Rect(box_x + 480, y_pos, 220, 36)

    camp_hov = b_camp.collidepoint(mouse_pos)
    end_hov = b_end.collidepoint(mouse_pos)

    pygame.draw.rect(surface, (40, 130, 60) if not is_endless else ((60, 32, 85) if camp_hov else (34, 18, 50)), b_camp, border_radius=6)
    pygame.draw.rect(surface, (120, 255, 150) if not is_endless else ((220, 110, 230) if camp_hov else (110, 60, 130)), b_camp, width=2 if not is_endless else 1, border_radius=6)
    c_txt = small_font.render("Кампания (до 100 волн)", True, WHITE if not is_endless else (220, 190, 230))
    surface.blit(c_txt, (b_camp.centerx - c_txt.get_width() // 2, b_camp.centery - c_txt.get_height() // 2))
    action_buttons.append((b_camp, "endless", False))

    pygame.draw.rect(surface, (40, 130, 60) if is_endless else ((60, 32, 85) if end_hov else (34, 18, 50)), b_end, border_radius=6)
    pygame.draw.rect(surface, (120, 255, 150) if is_endless else ((220, 110, 230) if end_hov else (110, 60, 130)), b_end, width=2 if is_endless else 1, border_radius=6)
    e_txt = small_font.render("Бесконечный штурм (Endless)", True, WHITE if is_endless else (220, 190, 230))
    surface.blit(e_txt, (b_end.centerx - e_txt.get_width() // 2, b_end.centery - e_txt.get_height() // 2))
    action_buttons.append((b_end, "endless", True))

    # Нижняя панель действий
    bot_y = box_y + box_h - 58
    play_btn = pygame.Rect(box_x + box_w - 270, bot_y, 240, 44)
    is_map10_unlocked, _ = is_map_unlocked(9, savedata)

    if is_map10_unlocked:
        p_hov = play_btn.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 165, 75) if p_hov else (32, 125, 58), play_btn, border_radius=8)
        pygame.draw.rect(surface, (160, 255, 180) if p_hov else (70, 210, 110), play_btn, width=2, border_radius=8)
        p_txt = font.render("ПРИМЕНИТЬ И ИГРАТЬ", True, WHITE)
        surface.blit(p_txt, (play_btn.centerx - p_txt.get_width() // 2, play_btn.centery - p_txt.get_height() // 2))
        action_buttons.append((play_btn, "apply_and_play", None))
    else:
        pygame.draw.rect(surface, (45, 24, 28), play_btn, border_radius=8)
        pygame.draw.rect(surface, (120, 50, 60), play_btn, width=1, border_radius=8)
        p_txt = tiny_font.render("КАРТА ЗАБЛОКИРОВАНА", True, (240, 150, 160))
        surface.blit(p_txt, (play_btn.centerx - p_txt.get_width() // 2, play_btn.centery - p_txt.get_height() // 2))

    save_btn = pygame.Rect(box_x + 26, bot_y, 160, 44)
    s_hov = save_btn.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (50, 75, 110) if s_hov else (34, 52, 78), save_btn, border_radius=8)
    pygame.draw.rect(surface, (130, 195, 255) if s_hov else (70, 120, 180), save_btn, width=2, border_radius=8)
    sv_txt = font.render("СОХРАНИТЬ", True, (230, 245, 255))
    surface.blit(sv_txt, (save_btn.centerx - sv_txt.get_width() // 2, save_btn.centery - sv_txt.get_height() // 2))
    action_buttons.append((save_btn, "save_close", None))

    return close_btn, play_btn, action_buttons



def draw_mechanics_guide_modal(surface, mouse_pos, current_tab=0, context="combat"):
    """
    Универсальное интерактивное окно контекстной помощи и механик игры:
    Контексты:
    - 'combat': башни, боевые синергии, броня мобов, палатка, ферма, скейлинг цен покупки дубликатов (x1.2..x4).
    - 'tree': ветки древа улучшений (Сила, Экономика, Вооружение), Тёмный Космос, метеориты, рубежи, 100% возврат звёзд.
    - 'greenhouse': 8 сортов кактусов, циклы созревания, полив (+100% темпа), саженцы [1, 3, 8, 18, 35], Резонанс и Компост.
    - 'relics': 20 реликвий биомов (по 2 на карту), 2-5 активных пьедесталов, Тёмный Резонанс (+5%/ур. до +20%), раскопки 5х5, прогрессия 2^(lvl-1).
    """
    # 1. Затемняющий оверлей
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 205))
    surface.blit(overlay, (0, 0))

    box_w = 980
    box_h = 610
    box_x = (SCREEN_WIDTH - box_w) // 2
    box_y = (SCREEN_HEIGHT - box_h) // 2
    modal_rect = pygame.Rect(box_x, box_y, box_w, box_h)

    # Определение стилистики под контекст
    if context == "tree":
        accent_col = (255, 205, 75)
        title_str = "СПРАВОЧНИК: ДРЕВО УЛУЧШЕНИЙ"
        sub_info_str = "Таланты • Ветки Оазиса • Тёмный Космос • 100% Сброс"
        tabs = [
            ("ВЕТКИ И ТАЛАНТЫ", (255, 190, 60)),
            ("ТЁМНЫЙ КОСМОС", (190, 110, 255)),
            ("ВАЛЮТЫ И СБРОС", (80, 220, 140))
        ]
    elif context == "greenhouse":
        accent_col = (80, 220, 140)
        title_str = "СПРАВОЧНИК: ОРАНЖЕРЕЯ КАКТУСОВ"
        sub_info_str = "Флора Оазиса • 8 видов • Ростки • Синергии и Полив"
        tabs = [
            ("8 СОРТОВ КАКТУСОВ", (80, 225, 130)),
            ("РОСТКИ И ПОЛИВ", (255, 210, 70)),
            ("СИНЕРГИИ И БОНУСЫ", (100, 200, 255))
        ]
    elif context == "relics":
        accent_col = (255, 180, 75)
        title_str = "СПРАВОЧНИК: МУЗЕЙ И РЕЛИКВИИ"
        sub_info_str = "Археология • 20 реликвий • Пьедесталы • Резонанс"
        tabs = [
            ("20 РЕЛИКВИЙ И БИОМЫ", (255, 195, 75)),
            ("МУЗЕЙ И ПЬЕДЕСТАЛЫ", (185, 120, 255)),
            ("РАСКОПКИ И ПРОКАЧКА", (90, 215, 255))
        ]
    else:
        accent_col = (65, 170, 240)
        title_str = "СПРАВОЧНИК: БОЙ, БАШНИ И ТАКТИКА"
        sub_info_str = "Оазис • Боевые синергии • Тактика башен • Скейлинг цен"
        tabs = [
            ("БОЕВЫЕ СИНЕРГИИ", (255, 160, 50)),
            ("ТАКТИКА БАШЕН", (80, 220, 130)),
            ("ЦЕНЫ И СКЕЙЛИНГ", (255, 215, 60))
        ]

    pygame.draw.rect(surface, (16, 22, 32), modal_rect, border_radius=14)
    pygame.draw.rect(surface, accent_col, modal_rect, width=2, border_radius=14)

    # 2. Шапка
    hdr_h = 50
    header_rect = pygame.Rect(box_x, box_y, box_w, hdr_h)
    pygame.draw.rect(surface, (22, 32, 48), header_rect, border_top_left_radius=14, border_top_right_radius=14)
    pygame.draw.line(surface, (50, 75, 110), (box_x, box_y + hdr_h), (box_x + box_w, box_y + hdr_h), 2)

    title_txt = font.render(title_str, True, (240, 255, 250))
    surface.blit(title_txt, (box_x + 24, box_y + 13))

    sub_info = tiny_font.render(sub_info_str, True, (130, 170, 210))
    surface.blit(sub_info, (box_x + 30 + title_txt.get_width(), box_y + 17))

    # Кнопка закрытия [X]
    close_btn = pygame.Rect(box_x + box_w - 44, box_y + 9, 32, 32)
    cl_hov = close_btn.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (160, 40, 60) if cl_hov else (90, 25, 40), close_btn, border_radius=6)
    pygame.draw.rect(surface, (255, 100, 120) if cl_hov else (180, 50, 75), close_btn, width=1, border_radius=6)
    x_txt = font.render("X", True, WHITE)
    surface.blit(x_txt, (close_btn.centerx - x_txt.get_width() // 2, close_btn.centery - x_txt.get_height() // 2 - 1))

    # 3. Вкладки (Tabs)
    tab_w = 300
    tab_h = 36
    tab_gap = 12
    total_tabs_w = len(tabs) * tab_w + (len(tabs) - 1) * tab_gap
    start_tab_x = box_x + (box_w - total_tabs_w) // 2
    tab_y = box_y + hdr_h + 10
    tab_rects = []

    for t_idx, (t_name, t_accent) in enumerate(tabs):
        t_rect = pygame.Rect(start_tab_x + t_idx * (tab_w + tab_gap), tab_y, tab_w, tab_h)
        tab_rects.append(t_rect)
        is_cur = (current_tab == t_idx)
        t_hov = t_rect.collidepoint(mouse_pos)

        if is_cur:
            bg_c = (32, 48, 70)
            bd_c = t_accent
            txt_c = (255, 255, 255)
        elif t_hov:
            bg_c = (26, 38, 54)
            bd_c = (100, 140, 180)
            txt_c = (220, 235, 250)
        else:
            bg_c = (18, 26, 38)
            bd_c = (42, 60, 84)
            txt_c = (150, 175, 200)

        pygame.draw.rect(surface, bg_c, t_rect, border_radius=8)
        pygame.draw.rect(surface, bd_c, t_rect, width=2 if is_cur else 1, border_radius=8)
        tab_lbl = small_font.render(t_name, True, txt_c)
        surface.blit(tab_lbl, (t_rect.centerx - tab_lbl.get_width() // 2, t_rect.centery - tab_lbl.get_height() // 2))

    # 4. Содержимое вкладок
    content_y = tab_y + tab_h + 12
    content_rect = pygame.Rect(box_x + 18, content_y, box_w - 36, box_h - (content_y - box_y) - 16)
    pygame.draw.rect(surface, (14, 18, 26), content_rect, border_radius=10)
    pygame.draw.rect(surface, (36, 48, 68), content_rect, width=1, border_radius=10)

    cy = content_rect.top + 12
    cx = content_rect.left + 16
    cw = content_rect.width - 32

    def draw_guide_card(title, title_col, lines, badge_text="", icons=None):
        nonlocal cy
        card_h = 126
        c_rect = pygame.Rect(cx, cy, cw, card_h)
        pygame.draw.rect(surface, (20, 26, 38), c_rect, border_radius=10)
        pygame.draw.rect(surface, (42, 60, 85), c_rect, width=1, border_radius=10)

        # Левая цветовая полоска
        pygame.draw.rect(surface, title_col, (cx, cy, 5, card_h), border_top_left_radius=10, border_bottom_left_radius=10)

        # Иконки слева
        valid_icons = [ic for ic in (icons or []) if ic is not None]
        if valid_icons:
            ibox = pygame.Rect(cx + 14, cy + (card_h - 52) // 2, 52, 52)
            pygame.draw.rect(surface, (28, 38, 54), ibox, border_radius=8)
            pygame.draw.rect(surface, title_col, ibox, width=1, border_radius=8)
            if len(valid_icons) == 1:
                ic = pygame.transform.smoothscale(valid_icons[0], (38, 38))
                surface.blit(ic, (ibox.centerx - 19, ibox.centery - 19))
            elif len(valid_icons) >= 2:
                ic1 = pygame.transform.smoothscale(valid_icons[0], (26, 26))
                ic2 = pygame.transform.smoothscale(valid_icons[1], (26, 26))
                surface.blit(ic1, (ibox.left + 4, ibox.top + 4))
                surface.blit(ic2, (ibox.right - 30, ibox.bottom - 30))
            text_x = cx + 78
        else:
            text_x = cx + 18

        # Заголовок
        t_surf = font.render(title, True, title_col)
        surface.blit(t_surf, (text_x, cy + 12))

        # Бэйдж
        if badge_text:
            b_surf = tiny_font.render(badge_text, True, (255, 240, 180))
            bw = b_surf.get_width() + 16
            bh = 22
            b_rect = pygame.Rect(cx + cw - bw - 14, cy + 12, bw, bh)
            pygame.draw.rect(surface, (42, 34, 18), b_rect, border_radius=4)
            pygame.draw.rect(surface, title_col, b_rect, width=1, border_radius=4)
            surface.blit(b_surf, (b_rect.centerx - b_surf.get_width() // 2, b_rect.centery - b_surf.get_height() // 2))

        # Строки пояснений
        start_ly = cy + 42
        for li, (label, val, val_col) in enumerate(lines):
            ly = start_ly + li * 26
            l_surf = small_font.render(label, True, (215, 230, 245))
            surface.blit(l_surf, (text_x, ly))
            if val:
                v_surf = small_font.render(val, True, val_col)
                surface.blit(v_surf, (text_x + l_surf.get_width() + 4, ly))

        cy += card_h + 8

    # -------------------------------------------------------------
    # КОНТЕНТ: ДРЕВО УЛУЧШЕНИЙ
    # -------------------------------------------------------------
    if context == "tree":
        if current_tab == 0:
            draw_guide_card(
                "ВЕТКА «СИЛА И ВРЕМЯ» (БОЕВЫЕ ТАЛАНТЫ)",
                (255, 140, 40),
                [
                    ("• Острые Шипы: ", "+4% ко всему общему урону оазиса за уровень таланта (до +20% на 5 ур.).", (240, 245, 255)),
                    ("• Критический Удар: ", "+3% к шансу крита и +25% к множителю урона за уровень (до 15% шанса и 225% урона).", (255, 215, 80)),
                    ("• Каденция Оазиса: ", "+3% к скорости атаки всех башен за уровень таланта (до +15% на 5 ур.).", (140, 245, 170))
                ],
                badge_text="УРОН И ХАРАКТЕРИСТИКИ",
                icons=[damage_upg_icon, speed_upg_icon]
            )
            draw_guide_card(
                "ВЕТКА «ЭКОНОМИКА» И ФЕРМЫ",
                (255, 210, 60),
                [
                    ("• Кактусовый Урожай: ", "+10% кактусов за ликвидацию слаймов за уровень (до +50% на 5 ур.).", (240, 245, 255)),
                    ("• Стартовый Капитал: ", "+75 кактусов на старте каждого боя за уровень таланта (до +375 кактусов).", (140, 255, 180)),
                    ("• Ферма и Орошение: ", "Открывает Ферму [6], плодородную почву (+10%/ур.) и Ауру Орошения (полив раз в 24..14с).", (255, 220, 120))
                ],
                badge_text="ДОХОД И АГРАРИИ",
                icons=[bounty_upg_icon, farm_tower_img]
            )
            draw_guide_card(
                "ВЕТКА «ВООРУЖЕНИЕ» И КАП БАШЕН",
                (80, 210, 255),
                [
                    ("• Предельный Уровень: ", "Расширяет кап башен в бою с 20 до 30 уровня (+2 уровня за ранг, 5 рангов).", (240, 245, 255)),
                    ("• Стартовый Уровень: ", "Башни строятся сразу 1-3 ур. без затраты времени и кактусов в бою.", (140, 245, 170)),
                    ("• Автосбор и Быстрый Ап: ", "Магнит автосбора (R=120..200px) и кнопка [МАКС] (улучшение на все деньги в 1 клик).", (255, 215, 90))
                ],
                badge_text="ТЕХНОЛОГИИ ОАЗИСА",
                icons=[crown_upg_icon, start_lvl_icon]
            )
        elif current_tab == 1:
            draw_guide_card(
                "АСТРАЛЬНЫЙ МАЯК И МЕТЕОРИТЫ",
                (195, 120, 255),
                [
                    ("• Астральный Маяк: ", "Узел за 25 Звёзд активирует появление Тёмных кактусов и падение Метеоритов.", (255, 215, 80)),
                    ("• Падение Метеоритов: ", "Метеориты падают каждые 15-20 волн, неся в себе 1-2 Тёмных кактуса.", (220, 160, 255)),
                    ("• Квантовый Жатватель: ", "+1 дополнительный Тёмный кактус за уничтожение метеорита за ранг (до +3).", (140, 245, 170))
                ],
                badge_text="ОТКРЫТИЕ ТЬМЫ",
                icons=[dark_cactus_img, meteorite_img]
            )
            draw_guide_card(
                "ТЕХНОЛОГИИ БЕЗДНЫ И ЗАЩИТА",
                (120, 220, 255),
                [
                    ("• Тёмный Эгис: ", "Блокирует 1 (1 ур.) или 2 (2 ур.) прорыва мобов за волну без урона базе!", (120, 240, 255)),
                    ("• Тёмный Резонанс: ", "+5%/ур. силы (до +20% на 4 ур.) ВСЕМ неэкипированным реликвиям музея пассивно!", (225, 160, 255)),
                    ("• Горизонт Событий: ", "+50% радиус и +100% урон гравитационной воронки Орбитального Залпа.", (255, 180, 140))
                ],
                badge_text="ТЁМНЫЕ ТЕХНОЛОГИИ",
                icons=[crown_upg_icon, dark_cactus_img]
            )
            draw_guide_card(
                "КОРОНА ОАЗИСА (КАП 35 УРОВНЯ)",
                (255, 215, 75),
                [
                    ("• Корона Оазиса: ", "Сверхпрокачка: +1 к максимальному уровню башен за ранг (до 35 ур., 5 рангов).", (255, 220, 100)),
                    ("• Стоимость: ", "Требует Тёмные кактусы (3, 5, 8, 12, 18) и открытый Горизонт Событий.", (235, 175, 255)),
                    ("• Сила 35 уровня: ", "Башни 35 ур. наносят колоссальный урон и уничтожают боссов супер-волн 2000+!", (140, 255, 180))
                ],
                badge_text="МАКСИМУМ 35 УР.",
                icons=[crown_upg_icon]
            )
        else:
            draw_guide_card(
                "ДОБЫЧА ЗВЁЗДНЫХ И ТЁМНЫХ КАКТУСОВ",
                (255, 205, 80),
                [
                    ("• Звёздные кактусы: ", "8% шанс дропа с обычных мобов, 25% гарантированно с боссов (каждые 5 волн).", (255, 235, 140)),
                    ("• Тёмные кактусы: ", "Дроп с упавших Метеоритов (1-4 шт.) и боссов супер-волн 2000+.", (220, 140, 255)),
                    ("• Раскопки: ", "Курганы приносят фрагменты реликвий, а замакшенные реликвии дают чистые звёзды!", (140, 245, 170))
                ],
                badge_text="ВАЛЮТЫ ОАЗИСА",
                icons=[stellar_cactus_img_m, dark_cactus_img_m]
            )
            draw_guide_card(
                "РУБЕЖИ ВОЛН И БЫСТРЫЙ СТАРТ",
                (100, 230, 255),
                [
                    ("• Рубежи волн: ", "Преодоление 10, 25, 50, 75, 100 волн на картах даёт разовые пачки звёздных кактусов.", (240, 245, 255)),
                    ("• Выбор волны: ", "Пройденные рубежи открывают старт забега сразу с 6, 11, 26 или 101 волны в меню карт!", (140, 255, 180)),
                    ("• Награды рубежей: ", "Забег с рубежа сразу начисляет стартовое золото и позволяет пропустить ранние волны.", (255, 215, 90))
                ],
                badge_text="РУБЕЖИ КАРТ",
                icons=[start_lvl_icon, trophy_icon]
            )
            draw_guide_card(
                "100% ВОЗВРАТ РЕСУРСОВ ПРИ СБРОСЕ",
                (80, 240, 150),
                [
                    ("• Кнопка сброса: ", "В настройках игры доступен полный сброс древа талантов в любой момент.", (240, 245, 255)),
                    ("• Полный возврат: ", "100% всех потраченных Звёздных и Тёмных кактусов моментально возвращаются на баланс!", (120, 255, 160)),
                    ("• Эксперименты: ", "Перераспределяйте звёзды под разные карты и билды без каких-либо штрафов.", (255, 220, 110))
                ],
                badge_text="БЕЗ КОМИССИЙ И ПОТЕРЬ",
                icons=[crown_upg_icon, stellar_cactus_img_m]
            )

    # -------------------------------------------------------------
    # КОНТЕНТ: ОРАНЖЕРЕЯ КАКТУСОВ
    # -------------------------------------------------------------
    elif context == "greenhouse":
        gh_tex = globals().get("gh_cacti_textures", {})
        if current_tab == 0:
            draw_guide_card(
                "ОБОРОНА: САГУАРО, ОПУНЦИЯ И МАМИЛЛЯРИЯ",
                (80, 225, 130),
                [
                    ("• Пустынный Сагуаро: ", "+2..+15 HP базе, +15%..+60% урона шипов, 5%..10% шанс блока урона.", (240, 245, 255)),
                    ("• Золотая Опунция: ", "+40..+220 кактусов на старте, +5%..+20% семян со слаймов, +10%..+20% фермам.", (255, 220, 100)),
                    ("• Цветущая Мамиллярия: ", "Возрождение воинов на 15%..55% быстрее, +20%..+80% HP, щит и шипы.", (140, 255, 180))
                ],
                badge_text="БАЗА, ЗОЛОТО И ВОИНЫ",
                icons=[gh_tex.get("gh_saguaro", cactus_img), gh_tex.get("gh_opuntia", cactus_img)]
            )
            draw_guide_card(
                "СТИХИИ: ОГНЕННЫЙ БОЧОНОК И ЛЕДЯНОЙ АЛОЭ",
                (255, 140, 80),
                [
                    ("• Огненный Бочонок: ", "+5%..+30% урона Огня, горение +1..+2.5с, уязвимость +10%..+15%, магма-взрыв.", (255, 140, 100)),
                    ("• Ледяной Алоэ: ", "+7%..+30% к замедлению, +10%..+25% радиус, срезает 15%..25% брони врагов, глыба льда.", (100, 220, 255)),
                    ("• Термошок в оранжерее: ", "Совместная прокачка огня и льда усиливает синергию башен в бою в разы!", (255, 215, 80))
                ],
                badge_text="ОГОНЬ И ЛЁД",
                icons=[gh_tex.get("gh_fire_barrel", cactus_img), gh_tex.get("gh_frost_aloe", cactus_img)]
            )
            draw_guide_card(
                "КОСМОС: ЭХИНО, БЕЗДНА И ЦАРИЦА НОЧИ",
                (195, 130, 255),
                [
                    ("• Громовой Эхино: ", "+1..+2 рикошета цепной молнии Теслы, +8%..+28% урона, 6%..10% оглушение 0.6с.", (255, 240, 120)),
                    ("• Астрофитум Бездны: ", "+10%..+45% урона по Теневым/боссам, -15%..-50% маг. защиты, +25% Орбиталке.", (210, 140, 255)),
                    ("• Звёздный Цереус: ", "+15%..+80% урона Дрона, +5%..+20% шанс звёзд, 5 ур. — ДРОН БЬЁТ 2 ЦЕЛИ СРАЗУ!", (130, 245, 170))
                ],
                badge_text="МОЛНИЯ, ТЕНЬ И ДРОН",
                icons=[gh_tex.get("gh_thunder_echino", cactus_img), gh_tex.get("gh_void_astrophytum", cactus_img)]
            )
        elif current_tab == 1:
            draw_guide_card(
                "ПРОКАЧКА И ТРЕБОВАНИЯ САЖЕНЦЕВ",
                (255, 210, 60),
                [
                    ("• Требования ростков: ", "Для достижения уровней 1, 2, 3, 4, 5 требуется ровно 1, 3, 8, 18, 35 саженцев.", (255, 220, 110)),
                    ("• Дроп саженцев: ", "Выпадают при завершении волн, с боссов и при сборе урожая в оранжерее.", (240, 245, 255)),
                    ("• Квантовый Жатватель: ", "Талант древа повышает шансы выпадения редких и поздних видов кактусов.", (140, 255, 180))
                ],
                badge_text="ПРОГРЕССИЯ [1, 3, 8, 18, 35]",
                icons=[sprout_icon, greenhouse_icon]
            )
            draw_guide_card(
                "МЕХАНИКА ПОЛИВА И ВЛАЖНОСТЬ",
                (80, 210, 255),
                [
                    ("• Полив лейкой: ", "Увеличивает скорость роста кактусов на +100% (созревание ровно в 2 раза быстрее!).", (120, 245, 160)),
                    ("• Время действия: ", "Одна порция полива увлажняет почву на 120 секунд. Индикатор показывает влажность.", (240, 245, 255)),
                    ("• Синергия с фермой: ", "Кактусовая ферма с аурой орошения в бою поставляет росу в оранжерею!", (255, 215, 90))
                ],
                badge_text="УСКОРЕНИЕ +100%",
                icons=[farm_tower_img, cactus_img]
            )
            draw_guide_card(
                "СБОР УРОЖАЯ И БУФЕР НАКОПЛЕНИЯ",
                (140, 240, 160),
                [
                    ("• Сбор урожая: ", "При 100% созревании шкалы клик по кактусу собирает от 1 до 5 саженцев в хранилище.", (240, 245, 255)),
                    ("• Буфер накопления: ", "Кактусы могут удерживать до 10 несобранных циклов урожая без потерь.", (140, 255, 180)),
                    ("• Обмен: ", "Накопленные саженцы используются для селекции и обмена на звёздные ресурсы.", (255, 220, 100))
                ],
                badge_text="СБОР САЖЕНЦЕВ",
                icons=[sprout_icon]
            )
        else:
            draw_guide_card(
                "ТАЛАНТ «РЕЗОНАНС ФЛОРЫ»",
                (255, 195, 75),
                [
                    ("• Усиление эффектов: ", "Талант в Древе даёт +10% ко ВСЕМ бонусам Оранжереи за каждый ранг!", (240, 245, 255)),
                    ("• Масштабирование: ", "Усиливает HP базы, урон огня, замедление льда, скачки Теслы и урон Дрона.", (140, 255, 180)),
                    ("• Мультипликативность: ", "Применяется поверх базовых характеристик каждого выращенного кактуса.", (255, 215, 90))
                ],
                badge_text="+10%/УР. КО ВСЕМ БАФФАМ",
                icons=[greenhouse_icon, crown_upg_icon]
            )
            draw_guide_card(
                "ТАЛАНТ «ЖИВОЙ КОМПОСТ»",
                (100, 230, 255),
                [
                    ("• Бонус за уровни: ", "+0.2% урона ВСЕМ башням за каждый суммарный уровень кактуса в Оранжерее!", (255, 220, 100)),
                    ("• Суммарная сила: ", "При 8 кактусах 5 уровня (40 уровней) даёт от +8% до +40% постоянного урона оазиса.", (140, 255, 180)),
                    ("• Стабильный рост: ", "Каждый прокачанный горшок напрямую повышает огневую мощь на поле боя!", (240, 245, 255))
                ],
                badge_text="+0.2%/УР. ВСЕМ БАШНЯМ",
                icons=[farm_tower_img, damage_upg_icon]
            )
            draw_guide_card(
                "ФОНОВОЕ СОЗРЕВАНИЕ И ПРЕСТИЖ",
                (80, 240, 150),
                [
                    ("• Рост во время боя: ", "Оранжерея активно живёт и растёт, пока вы проходите волны на любой карте.", (240, 245, 255)),
                    ("• Селекционный Престиж: ", "Максимальное развитие 8 сортов позволяет запустить Престиж с множителем x1.25.", (255, 215, 90)),
                    ("• Вечные ценности: ", "Звёздные и Тёмные кактусы при престиже сохраняются в полном объёме.", (120, 255, 160))
                ],
                badge_text="АФК-РОСТ И МЕТА",
                icons=[cactus_img, trophy_icon]
            )

    # -------------------------------------------------------------
    # КОНТЕНТ: МУЗЕЙ РЕЛИКВИЙ И АРХЕОЛОГИЯ
    # -------------------------------------------------------------
    elif context == "relics":
        if current_tab == 0:
            draw_guide_card(
                "РЕЛИКВИИ ПЕРВЫХ КАРТ (0 - 2)",
                (255, 195, 75),
                [
                    ("• Карта 0 (Оазис): ", "«Древний Кувшин» (+10%/ур. к фермам) и «Окаменелая Игла» (+4%/ур. дальности башен).", (240, 245, 255)),
                    ("• Карта 1 (Каньон): ", "«Песчаный Молот» (+8%/ур. урона Огня) и «Фляга Первопроходца» (+2 HP базы/ур.).", (255, 215, 90)),
                    ("• Карта 2 (Шахты): ", "«Магматический Сгусток» (+6%/ур. по заморозке) и «Шахтёрский Жетон» (-10%/ур. скидка 1-й башни).", (140, 255, 180))
                ],
                badge_text="ОАЗИС, КАНЬОН, ШАХТЫ",
                icons=[relic_icon, shovel_icon]
            )
            draw_guide_card(
                "РЕЛИКВИИ СРЕДНИХ И ПОЗДНИХ БИОМОВ (3 - 9)",
                (100, 220, 255),
                [
                    ("• Карта 3 (Дюны): ", "«Солнечный Диск» (+10%/ур. дальности магии) и «Песочные Часы» (+15%/ур. к заморозке).", (240, 245, 255)),
                    ("• Биомы 4-7: ", "«Громовой Зуб» (+3 скачка цепи Теслы), «Кольцо Воина» (+15% HP солдат), «Сердце Оазиса» (+5 HP).", (140, 255, 180)),
                    ("• Карты 8-9 (Космос): ", "«Око Бездны» (+20% пробития брони) и «Астральный Компас» (+15% шанса звёзд).", (220, 160, 255))
                ],
                badge_text="ДЮНЫ, ВУЛКАН, ТЬМА",
                icons=[relic_icon, tesla_tower_img]
            )
            draw_guide_card(
                "ПОТОЛОК УРОВНЕЙ И СИЛА РЕЛИКВИЙ",
                (255, 215, 75),
                [
                    ("• Базовый кап: ", "Базовый предел прокачки реликвии — 5 уровень.", (240, 245, 255)),
                    ("• Талант «Архивы Музея»: ", "Расширяет предельный уровень реликвий до 10, 15 и 20 уровня!", (255, 215, 90)),
                    ("• Линейная формула: ", "Эффект каждой реликвии растёт строго пропорционально уровню (Эффект = База x Уровень).", (140, 255, 180))
                ],
                badge_text="КАП 5..20 УРОВНЯ",
                icons=[crown_upg_icon, relic_icon]
            )
        elif current_tab == 1:
            draw_guide_card(
                "АКТИВНЫЕ ПЬЕДЕСТАЛЫ (100% СИЛЫ)",
                (255, 210, 60),
                [
                    ("• Пьедесталы музея: ", "Базово доступно 2 пьедестала. Таланты древа открывают до 5 активных слотов.", (240, 245, 255)),
                    ("• 100% мощности: ", "Реликвии на пьедесталах передают 100% своих эффектов на поле боя в каждом бою.", (140, 255, 180)),
                    ("• Экипировка: ", "Клик по реликвии на стенде ставит её на пьедестал; клик по пьедесталу снимает её.", (255, 215, 90))
                ],
                badge_text="2 - 5 СЛОТОВ ВЫСТАВКИ",
                icons=[relic_icon, trophy_icon]
            )
            draw_guide_card(
                "ТЁМНЫЙ РЕЗОНАНС БЕЗДНЫ",
                (195, 120, 255),
                [
                    ("• Пассивная сила: ", "Талант «Тёмный Резонанс» даёт +5% силы за ранг (до +20% на 4 ранге) ВСЕМ 20 реликвиям!", (220, 160, 255)),
                    ("• Без пьедестала: ", "Реликвии работают пассивно в фоне, даже если НЕ выставлены на пьедестал!", (140, 255, 180)),
                    ("• Колоссальный буст: ", "Коллекция из 20 прокачанных реликвий с Резонансом даёт гигантскую прибавку ко всей базе.", (255, 220, 100))
                ],
                badge_text="+5%/УР. ДО +20% НА ВСЕ 20",
                icons=[dark_cactus_img, crown_upg_icon]
            )
            draw_guide_card(
                "СИНЕРГИЯ С АРХЕОЛОГИЕЙ И ОАЗИСОМ",
                (80, 220, 140),
                [
                    ("• Музейный зал: ", "Стенды наглядно показывают прогресс сбора всех 20 реликвий по биомам.", (240, 245, 255)),
                    ("• Бонус к фермам и урону: ", "Реликвии суммируются с бонусами Древа талантов и Оранжереи перемножением.", (140, 255, 180)),
                    ("• Защита от перегрузки: ", "Слот-менеджер автоматически валидирует активные реликвии при загрузке сохранений.", (170, 220, 255))
                ],
                badge_text="СИНЕРГИИ МУЗЕЯ",
                icons=[shovel_icon, start_cacti_icon]
            )
        else:
            draw_guide_card(
                "МИНИ-ИГРА РАСКОПОК 5х5",
                (255, 195, 75),
                [
                    ("• Курган раскопок: ", "Появляется на картах в начале волны с шансом 2% (живёт 30-60 сек с талантами).", (240, 245, 255)),
                    ("• Ходы раскопок: ", "Базово даётся 12 ходов (+2 хода за уровень таланта «Археологическое чутьё», до 18+).", (255, 215, 90)),
                    ("• Поиск фигуры: ", "Реликвии имеют форму 1х2, 1х3 или 2х2. Клетки раскопок показывают дальность до клада.", (140, 255, 180))
                ],
                badge_text="СЕТКА 25 КЛЕТОК",
                icons=[shovel_icon]
            )
            draw_guide_card(
                "ФОРМУЛА ПРОКАЧКИ 2^(LVL-1)",
                (100, 230, 255),
                [
                    ("• Закон удвоения: ", "Количество фрагментов для следующего уровня реликвии равно ровно 2^(lvl-1):", (255, 215, 90)),
                    ("• Сетка требований: ", "Ур. 1 -> 1 фрагмент, Ур. 2 -> 2 фрагмента, Ур. 3 -> 4, Ур. 4 -> 8, Ур. 5 -> 16.", (140, 255, 180)),
                    ("• Награды: ", "Каждая победа в раскопках даёт фрагмент реликвии, опыт и ценные Звёздные кактусы!", (240, 245, 255))
                ],
                badge_text="1, 2, 4, 8, 16 ДУБЛИКАТОВ",
                icons=[relic_icon, crown_upg_icon]
            )
            draw_guide_card(
                "МАКСИМАЛЬНЫЕ КАРТЫ И ЗВЁЗДЫ",
                (80, 240, 150),
                [
                    ("• Замакшенные биомы: ", "Когда обе реликвии карты достигают максимума, раскопки на ней приносят чистые звёзды.", (255, 220, 100)),
                    ("• Стойкий Раскоп: ", "Талант «Стойкий Раскоп» увеличивает время жизни кургана на +10 сек за уровень.", (240, 245, 255)),
                    ("• Быстрый вход: ", "Клавиша [R] на клавиатуре мгновенно открывает активный раскоп прямо во время волны!", (120, 245, 160))
                ],
                badge_text="ЗВЁЗДНЫЙ ПРИТОК",
                icons=[stellar_cactus_img_m]
            )

    # -------------------------------------------------------------
    # КОНТЕНТ: БОЙ, БАШНИ И ТАКТИКА (ПО УМОЛЧАНИЮ)
    # -------------------------------------------------------------
    else:
        if current_tab == 0:
            draw_guide_card(
                "ТЕРМОШОК: ОГОНЬ + ЛЁД",
                (255, 140, 40),
                [
                    ("• Заморозка: ", "Ледяная башня замедляет врагов на 36% базово (до 80% на макс ур.) на 2.4-4.2 сек.", (240, 245, 255)),
                    ("• Термоудар: ", "Башня Камней наносит +40% комбо-урона (до +90% с талантом) по заморозке!", (255, 215, 80)),
                    ("• Стихии: ", "Ледяные слаймы получают +60% урона от огня; Огненные слаймы получают +60% ото льда.", (130, 235, 160))
                ],
                badge_text="+40%..+90% КРИТ",
                icons=[rock_tower_img, freeze_tower_img]
            )
            draw_guide_card(
                "БРОНЯ ВРАГОВ (ARMOR) И ЧИСТЫЙ УРОН",
                (80, 210, 255),
                [
                    ("• Броня мобов: ", "Серые и тяжелые слаймы снижают физ. урон на 50% (в Петле 2000+ — на 75%).", (255, 180, 180)),
                    ("• Чистый урон: ", "Стрелы Магии и молнии Теслы на 100% игнорируют физическую броню врагов!", (140, 255, 180)),
                    ("• Сопротивления: ", "Магические слаймы гасят магию/молнию на 50-70%, а Теневые мобы режут весь урон на 50%.", (255, 235, 140))
                ],
                badge_text="ИГНОРИРОВАНИЕ БРОНИ",
                icons=[magic_tower_img, tesla_tower_img]
            )
            draw_guide_card(
                "КОНТРОЛЬ ПОЛЯ И ТЁМНЫЙ ЭГИС",
                (210, 140, 255),
                [
                    ("• Жизни базы: ", "Базово 10 HP (+3 HP за каждый уровень таланта «Крепость Базы», до 25 HP) + оплот жизни.", (240, 245, 255)),
                    ("• Тёмный Эгис: ", "Космический щит блокирует до 2 прорывов врагов за волну без потери жизней!", (120, 240, 255)),
                    ("• Метеорит: ", "Падает каждые 15-20 волн. Клик по нему фокусирует огонь башен (+25% радиуса, +10% урона).", (255, 215, 100))
                ],
                badge_text="ЗАЩИТА БАЗЫ",
                icons=[heart_img, crown_upg_icon]
            )
        elif current_tab == 1:
            draw_guide_card(
                "ПАЛАТКА ВОИНОВ: ТОЧКА СБОРА И ШИПЫ",
                (80, 225, 120),
                [
                    ("• Гарнизон: ", "2 воина (ур. 0-3), 3 воина (ур. 4-7), 4 воина (ур. 8+). Здоровье бойцов: 28-268 HP.", (240, 245, 255)),
                    ("• Точка сбора [R]: ", "Позволяет выставить позицию солдат на любом участке дороги в радиусе палатки.", (160, 230, 255)),
                    ("• Талант «Шипы»: ", "Возвращает атакующим мобам +30%/ур. урона (до 150% возврата урона на 5 ур. таланта)!", (255, 140, 100))
                ],
                badge_text="ГАРНИЗОН И ШИПЫ",
                icons=[tent_tower_img, soldier_img]
            )
            draw_guide_card(
                "КАКТУСОВАЯ ФЕРМА: ОРОШЕНИЕ И ДОХОД",
                (255, 215, 60),
                [
                    ("• Доход: ", "Приносит от 35 до 700+ кактусов в конце волны (+10%/ур. таланта «Плодородная Почва»).", (240, 245, 255)),
                    ("• Аура Орошения: ", "Поле радиусом 90-170 px поливает соседние башни раз в 24 / 18 / 14 секунд.", (130, 240, 160)),
                    ("• Бонус полива: ", "Орошенные башни атакуют на +8%, +14% или +20% быстрее обычного!", (100, 235, 255))
                ],
                badge_text="ЭКОНОМИКА И ТЕМП",
                icons=[farm_tower_img, cactus_img]
            )
            draw_guide_card(
                "БАШНЯ ТЕСЛА И СВЕРХЗАРЯД",
                (90, 235, 255),
                [
                    ("• Цепная молния: ", "Поражает 3 цели базово (+1 цель каждые 5 ур., до 6+ целей на 15 ур.).", (240, 245, 255)),
                    ("• Чистый урон: ", "Электрический разряд на 100% игнорирует физическую броню слаймов.", (140, 255, 180)),
                    ("• Реликвии и Дрон: ", "«Громовой Зуб» даёт +3 перескока цепи, а Дрон наносит 2.5 урона каждые 0.65с.", (255, 215, 80))
                ],
                badge_text="ЦЕПНАЯ МОЛНИЯ",
                icons=[tesla_tower_img]
            )
        else:
            draw_guide_card(
                "СКЕЙЛИНГ ЦЕНЫ ДУБЛИКАТОВ БАШЕН",
                (255, 215, 60),
                [
                    ("• Точный ряд: ", "Каждая башня одного типа умножает цену покупки: x1.2, x1.2, x1.5, x1.5, x2, x3, x4!", (255, 215, 80)),
                    ("• Дальнейший рост: ", "После 7-й башни стоимость покупки умножается на x4.0 каждый следующий раз!", (255, 140, 120)),
                    ("• Тактика: ", "Разнообразьте типы башен на карте, чтобы избежать взрывного удорожания дубликатов.", (140, 245, 170))
                ],
                badge_text="ПРОГРЕССИЯ ПОКУПКИ",
                icons=[cactus_img, crown_upg_icon]
            )
            draw_guide_card(
                "МОДИФИКАТОРЫ КАРТ И ПРОДАЖА",
                (100, 220, 255),
                [
                    ("• Шаг карты: ", "На карте 0 множитель составляет x1.05, на последних картах достигает x1.10.", (240, 245, 255)),
                    ("• Возврат при продаже: ", "Продажа башни возвращает ровно 70% всех вложенных средств (покупка + апгрейды).", (140, 255, 180)),
                    ("• Скидка жетона: ", "Реликвия «Шахтёрский Жетон» снижает цену первой башни каждого типа на -10%/ур.!", (255, 220, 120))
                ],
                badge_text="ШАГ КАРТ И ВОЗВРАТ",
                icons=[bounty_upg_icon, start_cacti_icon]
            )
            draw_guide_card(
                "ОРБИТАЛЬНЫЙ ЗАЛП И УПРАВЛЕНИЕ",
                (255, 120, 150),
                [
                    ("• Меню и Пауза: ", "Кнопка [МЕНЮ] в HUD или [ESC] / [P] — пауза, настройки, бестиарий, выход.", (255, 180, 200)),
                    ("• Орбитальный залп [F]: ", "Залп с орбиты (КД 45-30с) стягивает мобов в воронку и уничтожает метеорит.", (255, 150, 210)),
                    ("• Темп и Прокачка: ", "[ПРОБЕЛ] — скорость (0.2X, 1X, 2X, 3X, 5X). Кнопка [МАКС] — прокачка на все деньги.", (255, 215, 90))
                ],
                badge_text="УПРАВЛЕНИЕ И БОЙ",
                icons=[meteorite_img]
            )

    # Нижняя статусная панель с подсказками
    footer_rect = pygame.Rect(cx, cy + 2, cw, 28)
    pygame.draw.rect(surface, (18, 24, 34), footer_rect, border_radius=6)
    pygame.draw.rect(surface, (40, 56, 78), footer_rect, width=1, border_radius=6)
    nav_hint = tiny_font.render("[СТРЕЛКИ / TAB / Клик] — Навигация по вкладкам  •  [ESC / ПРОБЕЛ] — Закрыть гид", True, (160, 190, 220))
    surface.blit(nav_hint, (footer_rect.centerx - nav_hint.get_width() // 2, footer_rect.centery - nav_hint.get_height() // 2))

    return close_btn, tab_rects



def play_start_window_animation(bg_time, game_map=0, path=None, tower_slots=None):
    # 1. Цвета меню и биома целевой карты
    biome = MAP_BIOMES_DATA.get(game_map, MAP_BIOMES_DATA[0])
    target_col_a = biome.get("bg_col_a", (155, 195, 155))
    target_col_b = biome.get("bg_col_b", (175, 215, 175))
    menu_col_a = BG_GRID_A
    menu_col_b = BG_GRID_B

    # 2. Пререндер карты (фон, дорога и слоты) для появления при расширении
    map_full_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    generate_background(map_full_surf, bg_time, map_id=game_map)
    r_border = biome.get("road_border", (85, 70, 50))
    r_col = biome.get("road_col", (125, 110, 85))
    if path:
        for p_i in range(len(path) - 1):
            pygame.draw.line(map_full_surf, r_border, path[p_i], path[p_i + 1], 40)
            pygame.draw.circle(map_full_surf, r_border, path[p_i + 1], 20)
        for p_i in range(len(path) - 1):
            pygame.draw.line(map_full_surf, r_col, path[p_i], path[p_i + 1], 32)
            pygame.draw.circle(map_full_surf, r_col, path[p_i + 1], 16)
    if tower_slots:
        for slot in tower_slots:
            map_full_surf.blit(slot_img, (slot[0] - 22, slot[1] - 22))

    center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_r = int(math.hypot(center_x, center_y))

    # Выделяем одну быструю Colorkey-маску (0 покадровых аллокаций памяти, 60 FPS на Android и PC)
    mask_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    mask_surf.set_colorkey((255, 0, 255))
    mask_bg = (8, 12, 18)

    # Детерминированные частицы вихря (звёздная пыль и колючки кактуса)
    stardust = [
        {'ang': (k / 24.0) * math.pi * 2, 'dist': 0.75 + (k % 4) * 0.12, 'sz': 2 if k % 2 == 0 else 3}
        for k in range(24)
    ]

    # Фаза 1: Сжатие диафрагмы к центру с закручивающимся вихрем и лучами (10 быстрых кадров)
    steps = 10
    for i in range(steps + 1):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                break
        t = min(1.0, max(0.0, i / float(steps)))
        progress = t ** 1.3
        r = max(0, int(max_r * (1.0 - progress)))
        rot = progress * math.pi * 2.0

        cur_a = (
            int(menu_col_a[0] + (target_col_a[0] - menu_col_a[0]) * t),
            int(menu_col_a[1] + (target_col_a[1] - menu_col_a[1]) * t),
            int(menu_col_a[2] + (target_col_a[2] - menu_col_a[2]) * t),
        )
        cur_b = (
            int(menu_col_b[0] + (target_col_b[0] - menu_col_b[0]) * t),
            int(menu_col_b[1] + (target_col_b[1] - menu_col_b[1]) * t),
            int(menu_col_b[2] + (target_col_b[2] - menu_col_b[2]) * t),
        )
        screen.fill(mask_bg)
        if r > 0:
            generate_background(screen, bg_time + i * 20, custom_cols=(cur_a, cur_b))
            mask_surf.fill(mask_bg)
            pygame.draw.circle(mask_surf, (255, 0, 255), (center_x, center_y), r)
            screen.blit(mask_surf, (0, 0))

            # Многоуровневые светящиеся кольца
            pygame.draw.circle(screen, target_col_b, (center_x, center_y), r, width=3)
            if r > 20:
                pygame.draw.circle(screen, WHITE, (center_x, center_y), r - 2, width=1)
                for k in range(8):
                    ra = rot + k * (math.pi / 4)
                    x1 = center_x + math.cos(ra) * r
                    y1 = center_y + math.sin(ra) * r
                    x2 = center_x + math.cos(ra) * (r + 16)
                    y2 = center_y + math.sin(ra) * (r + 16)
                    pygame.draw.line(screen, (255, 225, 100), (x1, y1), (x2, y2), 2)

            for p in stardust:
                pr = int(r * p['dist'])
                if pr > 5:
                    pa = p['ang'] + rot * 1.5
                    px = int(center_x + math.cos(pa) * pr)
                    py = int(center_y + math.sin(pa) * pr)
                    if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
                        pygame.draw.circle(screen, target_col_b, (px, py), p['sz'])

        pygame.display.flip()
        clock.tick(60)

    # Кульминация в центре: яркая вспышка сверхновой (2 быстрых кадра)
    for fi in range(2):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                break
        screen.fill(mask_bg)
        fr = (fi + 1) * 36
        pygame.draw.circle(screen, WHITE, (center_x, center_y), 16)
        pygame.draw.circle(screen, (255, 220, 100), (center_x, center_y), fr, width=3)
        span = 120 - fi * 40
        pygame.draw.line(screen, WHITE, (center_x - span, center_y), (center_x + span, center_y), 3)
        pygame.draw.line(screen, WHITE, (center_x, center_y - span), (center_x, center_y + span), 3)
        pygame.display.flip()
        clock.tick(60)

    # Фаза 2: Раскрытие карты (10 быстрых кадров)
    steps_exp = 10
    for i in range(1, steps_exp + 1):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                break
        progress = (i / float(steps_exp)) ** 1.25
        r = min(max_r, int(max_r * progress))
        rot = -progress * math.pi * 1.8

        screen.fill(mask_bg)
        if r > 0:
            screen.blit(map_full_surf, (0, 0))
            if r < max_r:
                mask_surf.fill(mask_bg)
                pygame.draw.circle(mask_surf, (255, 0, 255), (center_x, center_y), r)
                screen.blit(mask_surf, (0, 0))

                pygame.draw.circle(screen, WHITE, (center_x, center_y), r, width=2)
                pygame.draw.circle(screen, (255, 215, 80), (center_x, center_y), r + 3, width=3)
                for k in range(8):
                    ra = rot + k * (math.pi / 4)
                    x1 = center_x + math.cos(ra) * r
                    y1 = center_y + math.sin(ra) * r
                    x2 = center_x + math.cos(ra) * (r + 20)
                    y2 = center_y + math.sin(ra) * (r + 20)
                    pygame.draw.line(screen, (255, 215, 80), (x1, y1), (x2, y2), 2)

        pygame.display.flip()
        clock.tick(60)

    return screen


# -------------------------------------------------------------------------
# ЭКРАН 7: ТИТРЫ И ЭПИЛОГ (ПОБЕДА НАД ИСТИННЫМ ПОВЕЛИТЕЛЕМ БЕЗДНЫ)
# -------------------------------------------------------------------------
def draw_credits_screen(surface, scroll_y, savedata, mouse_pos, source="game"):
    ticks = pygame.time.get_ticks()
    
    # 1. Космический фон Бездны
    surface.fill((10, 8, 20))

    # Фоновые туманности
    nebula_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    n_pulse = math.sin(ticks * 0.001) * 0.15 + 0.85
    pygame.draw.circle(nebula_surf, (80, 25, 120, int(35 * n_pulse)), (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3), 280)
    pygame.draw.circle(nebula_surf, (30, 80, 150, int(30 * n_pulse)), (3 * SCREEN_WIDTH // 4, 2 * SCREEN_HEIGHT // 3), 320)
    pygame.draw.circle(nebula_surf, (120, 40, 180, int(25 * n_pulse)), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 220)
    surface.blit(nebula_surf, (0, 0))

    # Звёзды
    for i in range(70):
        sx = (i * 127 + 53) % SCREEN_WIDTH
        sy = (i * 89 + 17) % SCREEN_HEIGHT
        s_brightness = int(140 + 115 * math.sin(ticks * 0.002 + i))
        pygame.draw.circle(surface, (s_brightness, s_brightness, min(255, s_brightness + 30)), (sx, sy), 1 if i % 3 != 0 else 2)

    # 2. Область прокрутки контента титров
    view_x = 100
    view_y = 100
    view_w = SCREEN_WIDTH - 200
    view_h = SCREEN_HEIGHT - 185
    view_rect = pygame.Rect(view_x, view_y, view_w, view_h)

    card_surf = pygame.Surface((view_w, view_h), pygame.SRCALPHA)
    card_surf.fill((16, 14, 28, 225))
    pygame.draw.rect(card_surf, (85, 60, 130), (0, 0, view_w, view_h), width=2, border_radius=12)
    surface.blit(card_surf, (view_x, view_y))

    # Список секций и строк для прокрутки
    stats_data = savedata.get("Stats", {})
    records_data = savedata.get("LevelsRecords", {})
    st_cacti = savedata.get("StellarCactuses", 0)
    dk_cacti = savedata.get("DarkCactuses", 0)
    boss_k = stats_data.get("bosses_defeated", 0)
    void_k = stats_data.get("void_defeated", 0)
    gold_k = stats_data.get("killed_golden", 0)
    map9_rec = records_data[8] if len(records_data) > 8 else 100

    credits_content = [
        ("HEADER", "ПОБЕДА: 100 ВОЛН ПОЗАДИ"),
        ("TEXT", "Ты реально это сделал! Главный слизень побежден."),
        ("TEXT", "Кактусы на грядках могут наконец-то расслабить колючки и выдохнуть."),
        ("TEXT", "Оазис отбит, но впереди ещё бесконечные волны для тех, кому мало..."),
        ("SPACE", 18),
        ("HEADER", "ТИТРЫ - ЭТО НЕ КОНЕЦ ИГРЫ"),
        ("ALERT", "Жми [ПРОДОЛЖИТЬ], если хочешь узнать, сколько продержишься на волнах 101+."),
        ("ALERT", "Все твои башни, кактусы и прокачка остаются в строю (Бесконечный режим)."),
        ("ALERT", "Или выходи в меню - весь прогресс и звёзды уже надёжно сохранены!"),
        ("SPACE", 20),
        ("HEADER", "БЛАГОДАРНОСТИ"),
        ("TEXT", "Игра вдохновлена классическими TD и Pixel-Art проектами."),
        ("TEXT", "Спрайты слаймов: Stardew Valley Wiki (ConcernedApe)."),
        ("SPACE", 20),
        ("HEADER", "ТЁМНЫЕ КАКТУСЫ И ПРОКАЧКА"),
        ("TEXT", "Если обычных кактусов уже в достатке, в дело вступают Тёмные:"),
        ("TEXT", "- Выпадают с теневых слаймов, метеоритов и боссов."),
        ("TEXT", "- Открывают мощные технологии в древе талантов:"),
        ("TEXT", "  - Орбитальный удар (ручное прицеливание курсором)"),
        ("TEXT", "  - Автономный дрон-кактус (летает и расстреливает цели)"),
        ("TEXT", "  - Сверхновая (ударная волна по площади)"),
        ("TEXT", "  - Тёмная алхимия и бонусный урон по боссам"),
        ("SPACE", 20),
        ("HEADER", "СТАТИСТИКА КАМПАНИИ"),
        ("STAT", f"- Собрано Звёздных Кактусов: {st_cacti} шт."),
        ("STAT", f"- Накоплено Тёмных Кактусов: {dk_cacti} шт."),
        ("STAT", f"- Уничтожено боссов: {boss_k}"),
        ("STAT", f"- Повержено Королей Слаймов: {void_k}"),
        ("STAT", f"- Найдено Золотых слаймов: {gold_k}"),
        ("STAT", f"- Рекордная волна на финальной карте: {map9_rec}"),
        ("SPACE", 20),
        ("HEADER", "РАЗРАБОТКА"),
        ("TEXT", "CactusTD Remastered"),
        ("TEXT", "Разработка: Cactus Team"),
        ("SPACE", 25),
        ("HIGHLIGHT", "Оазис спасён! Спасибо за игру в CactusTD Remastered!"),
        ("SPACE", 30),
    ]

    # Рендеринг контента с отсечением
    surface.set_clip(view_rect)
    cur_y = view_y + 20 - scroll_y

    for item_type, val in credits_content:
        if item_type == "SPACE":
            cur_y += val
        elif item_type == "HEADER":
            h_surf = font.render(val, True, GOLD)
            surface.blit(h_surf, (SCREEN_WIDTH // 2 - h_surf.get_width() // 2, cur_y))
            pygame.draw.line(surface, (140, 100, 180), (SCREEN_WIDTH // 2 - 220, cur_y + h_surf.get_height() + 4), (SCREEN_WIDTH // 2 + 220, cur_y + h_surf.get_height() + 4), 1)
            cur_y += h_surf.get_height() + 14
        elif item_type == "ALERT":
            a_surf = small_font.render(val, True, (255, 235, 120))
            surface.blit(a_surf, (SCREEN_WIDTH // 2 - a_surf.get_width() // 2, cur_y))
            cur_y += a_surf.get_height() + 8
        elif item_type == "HIGHLIGHT":
            hl_surf = small_font.render(val, True, (160, 230, 255))
            surface.blit(hl_surf, (view_x + 35, cur_y))
            cur_y += hl_surf.get_height() + 8
        elif item_type == "STAT":
            st_surf = small_font.render(val, True, (220, 180, 255))
            surface.blit(st_surf, (view_x + 45, cur_y))
            cur_y += st_surf.get_height() + 8
        elif item_type == "TEXT":
            t_surf = small_font.render(val, True, (215, 225, 235))
            surface.blit(t_surf, (SCREEN_WIDTH // 2 - t_surf.get_width() // 2, cur_y))
            cur_y += t_surf.get_height() + 8

    total_content_h = (cur_y + scroll_y) - (view_y + 20)
    max_scroll = max(0, total_content_h - (view_h - 40))

    surface.set_clip(None)

    # 3. Верхняя плашка заголовка экрана
    top_bar = pygame.Rect(0, 0, SCREEN_WIDTH, 85)
    pygame.draw.rect(surface, (14, 12, 26), top_bar)
    pygame.draw.line(surface, (70, 50, 105), (0, 85), (SCREEN_WIDTH, 85), 2)

    if source == "settings":
        title_str = "ТИТРЫ И ЭПИЛОГ: ОБОРОНА ГРЯДОК"
        sub_str = "ДОСТУПНО В ЛЮБОЙ МОМЕНТ ИЗ НАСТРОЕК | БЕСКОНЕЧНЫЙ РЕЖИМ 101+ ЖДЁТ"
    else:
        title_str = "ПОБЕДА: 100 ВОЛН ПРОЙДЕНО, КОРОЛЬ СЛАЙМОВ ПОБЕЖДЕН!"
        sub_str = "ТИТРЫ: НЕ КОНЕЦ ИГРЫ! БЕСКОНЕЧНЫЙ РЕЖИМ 101+ УЖЕ ОТКРЫТ"

    title_main = large_font.render(title_str, True, GOLD)
    surface.blit(title_main, (SCREEN_WIDTH // 2 - title_main.get_width() // 2, 10))

    sub_top = small_font.render(sub_str, True, (160, 230, 255))
    surface.blit(sub_top, (SCREEN_WIDTH // 2 - sub_top.get_width() // 2, 50))

    # Спрайты по краям топа
    if void_lord_boss_img:
        s_boss = pygame.transform.smoothscale(void_lord_boss_img, (56, 56))
        surface.blit(s_boss, (25, 14))
        surface.blit(s_boss, (SCREEN_WIDTH - 25 - 56, 14))

    # 4. Нижняя панель действий (кнопки "Продолжить" и "В меню")
    bot_bar = pygame.Rect(0, SCREEN_HEIGHT - 75, SCREEN_WIDTH, 75)
    pygame.draw.rect(surface, (14, 12, 26), bot_bar)
    pygame.draw.line(surface, (70, 50, 105), (0, SCREEN_HEIGHT - 75), (SCREEN_WIDTH, SCREEN_HEIGHT - 75), 2)

    btn_w = 340
    btn_h = 48
    btn_cont_rect = pygame.Rect(SCREEN_WIDTH // 2 - btn_w - 20, SCREEN_HEIGHT - 62, btn_w, btn_h)
    btn_menu_rect = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 62, btn_w, btn_h)

    c_hov = btn_cont_rect.collidepoint(mouse_pos)
    m_hov = btn_menu_rect.collidepoint(mouse_pos)

    # Кнопка 1
    if source == "settings":
        pygame.draw.rect(surface, (45, 80, 125) if not c_hov else (60, 110, 165), btn_cont_rect, border_radius=8)
        pygame.draw.rect(surface, (130, 200, 255) if c_hov else (90, 145, 210), btn_cont_rect, width=2, border_radius=8)
        c_txt = font.render("[<] В НАСТРОЙКИ [ESC]", True, WHITE)
    else:
        pygame.draw.rect(surface, (40, 145, 75) if not c_hov else (55, 185, 95), btn_cont_rect, border_radius=8)
        pygame.draw.rect(surface, GOLD if c_hov else (140, 240, 170), btn_cont_rect, width=2, border_radius=8)
        c_txt = font.render("[>] ПРОДОЛЖИТЬ (ВОЛНА 101+)", True, WHITE)
    surface.blit(c_txt, (btn_cont_rect.centerx - c_txt.get_width() // 2, btn_cont_rect.centery - c_txt.get_height() // 2))

    # Кнопка 2: В МЕНЮ
    pygame.draw.rect(surface, (135, 40, 50) if not m_hov else (175, 50, 65), btn_menu_rect, border_radius=8)
    pygame.draw.rect(surface, WHITE if m_hov else (200, 120, 130), btn_menu_rect, width=2, border_radius=8)
    m_txt = font.render("[<] ВЫЙТИ В МЕНЮ КАРТ", True, WHITE)
    surface.blit(m_txt, (btn_menu_rect.centerx - m_txt.get_width() // 2, btn_menu_rect.centery - m_txt.get_height() // 2))

    # Подсказка по клавишам
    if source == "settings":
        hint_str = "Колёсико / [W/S / Стрелки] - Прокрутка  |  [ESC / ПРОБЕЛ] - Назад в настройки"
    else:
        hint_str = "Колёсико / [W/S / Стрелки] - Прокрутка  |  [ПРОБЕЛ / ENTER] - Продолжить  |  [ESC] - Меню"
    hint_surf = tiny_font.render(hint_str, True, (160, 180, 205))
    surface.blit(hint_surf, (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2, SCREEN_HEIGHT - 13))

    return btn_cont_rect, btn_menu_rect, max_scroll


def draw_settings_screen(surface, savedata, mouse_pos, in_game=False, confirming_reset=False, current_tab="general", saves_scroll_y=0, modal_state=None, bg_time=None):
    """
    Экран настроек и управления сохранениями:
    - Вкладка 1: Параметры игры (Звук, Экран, Тряска окна Windows, Финал и титры)
    - Вкладка 2: Файлы сохранений (Создание, выбор, копирование, переименование, удаление)
    - Диалоговые окна: модальный ввод текста (создание/переименование) и подтверждение удаления
    """
    if bg_time is None:
        bg_time = pygame.time.get_ticks()
    generate_background(surface, bg_time, custom_cols=((12, 16, 24), (18, 24, 36)))

    # Фоновые декоративные полосы
    grid_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for x in range(0, SCREEN_WIDTH, 48):
        pygame.draw.line(grid_surf, (30, 42, 58, 40), (x, 70), (x, SCREEN_HEIGHT), 1)
    for y in range(70, SCREEN_HEIGHT, 48):
        pygame.draw.line(grid_surf, (30, 42, 58, 40), (0, y), (SCREEN_WIDTH, y), 1)
    surface.blit(grid_surf, (0, 0))

    # 1. Верхняя панель навигации
    top_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 70)
    pygame.draw.rect(surface, (18, 24, 35), top_rect)
    pygame.draw.line(surface, (45, 62, 88), (0, 70), (SCREEN_WIDTH, 70), 2)

    back_btn = pygame.Rect(20, 13, 160, 44)
    b_hov = back_btn.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (180, 45, 45) if b_hov else (145, 35, 35), back_btn, border_radius=8)
    pygame.draw.rect(surface, WHITE, back_btn, width=2, border_radius=8)
    b_txt = font.render("< НАЗАД [ESC]", True, WHITE)
    surface.blit(b_txt, (back_btn.centerx - b_txt.get_width() // 2, back_btn.centery - b_txt.get_height() // 2))

    # Центр: заголовок
    hdr_txt = large_font.render("НАСТРОЙКИ И ОПЦИИ", True, (240, 250, 255))
    surface.blit(hdr_txt, (SCREEN_WIDTH // 2 - hdr_txt.get_width() // 2, 9))
    sub_txt = tiny_font.render("* ПЕРСОНАЛИЗАЦИЯ ИГРОВОГО ПРОЦЕССА, ЗВУКА И УПРАВЛЕНИЕ СОХРАНЕНИЯМИ *", True, (140, 195, 240))
    surface.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, 44))

    # Правая панель с кактусами
    st_panel = pygame.Rect(SCREEN_WIDTH - 296, 12, 136, 46)
    pygame.draw.rect(surface, (22, 30, 44), st_panel, border_radius=8)
    pygame.draw.rect(surface, GOLD, st_panel, width=1, border_radius=8)
    surface.blit(stellar_cactus_img_m, (st_panel.left + 8, st_panel.centery - 18))
    st_num = font.render(f"{savedata.get('StellarCactuses', 0)}", True, WHITE)
    surface.blit(st_num, (st_panel.left + 48, st_panel.centery - st_num.get_height() // 2))

    dark_panel = pygame.Rect(SCREEN_WIDTH - 150, 12, 136, 46)
    pygame.draw.rect(surface, (32, 18, 45), dark_panel, border_radius=8)
    pygame.draw.rect(surface, (190, 70, 255), dark_panel, width=1, border_radius=8)
    surface.blit(dark_cactus_img_m, (dark_panel.left + 8, dark_panel.centery - 18))
    dark_num = font.render(f"{savedata.get('DarkCactuses', 0)}", True, WHITE)
    surface.blit(dark_num, (dark_panel.left + 48, dark_panel.centery - dark_num.get_height() // 2))

    # 2. Переключатели вкладок (Tabs)
    tab_y = 78
    tab_w1, tab_w2 = 230, 270
    tab_gen_rect = pygame.Rect(42, tab_y, tab_w1, 36)
    tab_saves_rect = pygame.Rect(42 + tab_w1 + 10, tab_y, tab_w2, 36)

    tg_hov = tab_gen_rect.collidepoint(mouse_pos)
    ts_hov = tab_saves_rect.collidepoint(mouse_pos)

    # Отрисовка вкладки 1: Параметры игры
    is_gen = (current_tab == "general")
    t1_bg = (35, 60, 95) if is_gen else ((28, 42, 60) if tg_hov else (20, 26, 38))
    t1_bd = (90, 195, 255) if is_gen else ((70, 110, 150) if tg_hov else (45, 60, 85))
    pygame.draw.rect(surface, t1_bg, tab_gen_rect, border_radius=6)
    pygame.draw.rect(surface, t1_bd, tab_gen_rect, width=2 if is_gen else 1, border_radius=6)
    t1_txt = font.render("ПАРАМЕТРЫ ИГРЫ", True, WHITE if is_gen else (180, 200, 220))
    surface.blit(t1_txt, (tab_gen_rect.centerx - t1_txt.get_width() // 2, tab_gen_rect.centery - t1_txt.get_height() // 2))

    # Отрисовка вкладки 2: Файлы сохранений
    all_profiles = list_save_profiles()
    is_sav = (current_tab == "saves")
    t2_bg = (35, 60, 95) if is_sav else ((28, 42, 60) if ts_hov else (20, 26, 38))
    t2_bd = (90, 195, 255) if is_sav else ((70, 110, 150) if ts_hov else (45, 60, 85))
    pygame.draw.rect(surface, t2_bg, tab_saves_rect, border_radius=6)
    pygame.draw.rect(surface, t2_bd, tab_saves_rect, width=2 if is_sav else 1, border_radius=6)
    t2_txt = font.render(f"СЛОТЫ СОХРАНЕНИЙ ({len(all_profiles)})", True, WHITE if is_sav else (180, 200, 220))
    surface.blit(t2_txt, (tab_saves_rect.centerx - t2_txt.get_width() // 2, tab_saves_rect.centery - t2_txt.get_height() // 2))

    # Считываем параметры текущего сохранения
    settings_data = savedata.setdefault("Settings", {})
    sfx_vol = settings_data.get("sfx_volume", 0.7)
    mus_vol = settings_data.get("music_volume", 0.5)
    win_shake_val = settings_data.get("window_shake", True)
    shake_val = settings_data.get("screen_shake", False)
    dmg_val = settings_data.get("damage_numbers", True)
    auto_wave_val = settings_data.get("auto_wave", False)
    gfx_preset = settings_data.get("graphics_preset", "normal")

    col1_x = 42
    col2_x = 658
    card_w = 580

    # Инициализация всех возвращаемых элементов интерфейса
    sfx_minus_rect = None
    sfx_plus_rect = None
    music_minus_rect = None
    music_plus_rect = None
    preset_normal_rect = None
    preset_opt_rect = None
    scale_sharp_rect = None
    scale_smooth_rect = None
    win_shake_toggle_rect = None
    shake_toggle_rect = None
    dmg_toggle_rect = None
    auto_wave_toggle_rect = None
    reset_btn_rect = None
    credits_btn_rect = None
    go_to_saves_btn = None
    create_save_btn = None
    import_clipboard_btn = None
    export_active_btn = None
    import_active_btn = None
    modal_copy_code_btn = None
    modal_paste_code_btn = None
    modal_ok_btn = None
    modal_cancel_btn = None
    save_actions = []
    max_scroll = 0

    game_done = savedata.get("GameCompleted", False) or savedata.get("CreditsSeen", False)

    # =========================================================================
    # ВКЛАДКА 1: ПАРАМЕТРЫ ИГРЫ (ОБЩИЕ НАСТРОЙКИ)
    # =========================================================================
    if is_gen:
        # -------------------------------------------------------------
        # КАРТОЧКА 1 (Лево-Верх): ЗВУК И МУЗЫКА
        # -------------------------------------------------------------
        c1_rect = pygame.Rect(col1_x, 126, card_w, 248)
        pygame.draw.rect(surface, (18, 25, 36), c1_rect, border_radius=12)
        pygame.draw.rect(surface, (50, 85, 125), c1_rect, width=2, border_radius=12)

        pygame.draw.rect(surface, (25, 36, 52), (col1_x, 126, card_w, 40), border_top_left_radius=12, border_top_right_radius=12)
        pygame.draw.line(surface, (50, 85, 125), (col1_x, 166), (col1_x + card_w, 166), 1)
        c1_hdr = font.render("ЗВУК И МУЗЫКА (AUDIO)", True, (130, 205, 255))
        surface.blit(c1_hdr, (col1_x + 18, 134))

        # 1.1 SFX Громкость
        row1_y = 180
        lbl_sfx = font.render("Громкость эффектов (SFX):", True, WHITE)
        surface.blit(lbl_sfx, (col1_x + 18, row1_y + 4))

        sfx_minus_rect = pygame.Rect(col1_x + 325, row1_y, 38, 32)
        sfx_plus_rect = pygame.Rect(col1_x + 524, row1_y, 38, 32)
        sm_hov = sfx_minus_rect.collidepoint(mouse_pos)
        sp_hov = sfx_plus_rect.collidepoint(mouse_pos)

        pygame.draw.rect(surface, (45, 75, 110) if sm_hov else (28, 48, 72), sfx_minus_rect, border_radius=6)
        pygame.draw.rect(surface, (110, 175, 245) if sm_hov else (52, 92, 138), sfx_minus_rect, width=1, border_radius=6)
        t_sm = font.render("-", True, WHITE)
        surface.blit(t_sm, (sfx_minus_rect.centerx - t_sm.get_width() // 2, sfx_minus_rect.centery - t_sm.get_height() // 2 - 2))

        pygame.draw.rect(surface, (45, 75, 110) if sp_hov else (28, 48, 72), sfx_plus_rect, border_radius=6)
        pygame.draw.rect(surface, (110, 175, 245) if sp_hov else (52, 92, 138), sfx_plus_rect, width=1, border_radius=6)
        t_sp = font.render("+", True, WHITE)
        surface.blit(t_sp, (sfx_plus_rect.centerx - t_sp.get_width() // 2, sfx_plus_rect.centery - t_sp.get_height() // 2 - 2))

        # Индикатор уровня SFX
        sfx_bar_rect = pygame.Rect(col1_x + 372, row1_y + 4, 144, 24)
        pygame.draw.rect(surface, (12, 18, 26), sfx_bar_rect, border_radius=5)
        pygame.draw.rect(surface, (45, 65, 90), sfx_bar_rect, width=1, border_radius=5)
        sfx_fill_w = int((sfx_bar_rect.width - 4) * sfx_vol)
        if sfx_fill_w > 0:
            pygame.draw.rect(surface, (70, 185, 245), (sfx_bar_rect.left + 2, sfx_bar_rect.top + 2, sfx_fill_w, sfx_bar_rect.height - 4), border_radius=4)
        sfx_pct_txt = tiny_font.render(f"{int(round(sfx_vol * 100))}%", True, WHITE)
        surface.blit(sfx_pct_txt, (sfx_bar_rect.centerx - sfx_pct_txt.get_width() // 2, sfx_bar_rect.centery - sfx_pct_txt.get_height() // 2))

        # 1.2 Музыка Громкость
        row2_y = 228
        lbl_mus = font.render("Громкость музыки (Music):", True, WHITE)
        surface.blit(lbl_mus, (col1_x + 18, row2_y + 4))

        music_minus_rect = pygame.Rect(col1_x + 325, row2_y, 38, 32)
        music_plus_rect = pygame.Rect(col1_x + 524, row2_y, 38, 32)
        mm_hov = music_minus_rect.collidepoint(mouse_pos)
        mp_hov = music_plus_rect.collidepoint(mouse_pos)

        pygame.draw.rect(surface, (45, 75, 110) if mm_hov else (28, 48, 72), music_minus_rect, border_radius=6)
        pygame.draw.rect(surface, (110, 175, 245) if mm_hov else (52, 92, 138), music_minus_rect, width=1, border_radius=6)
        t_mm = font.render("-", True, WHITE)
        surface.blit(t_mm, (music_minus_rect.centerx - t_mm.get_width() // 2, music_minus_rect.centery - t_mm.get_height() // 2 - 2))

        pygame.draw.rect(surface, (45, 75, 110) if mp_hov else (28, 48, 72), music_plus_rect, border_radius=6)
        pygame.draw.rect(surface, (110, 175, 245) if mp_hov else (52, 92, 138), music_plus_rect, width=1, border_radius=6)
        t_mp = font.render("+", True, WHITE)
        surface.blit(t_mp, (music_plus_rect.centerx - t_mp.get_width() // 2, music_plus_rect.centery - t_mp.get_height() // 2 - 2))

        # Индикатор уровня Музыки
        mus_bar_rect = pygame.Rect(col1_x + 372, row2_y + 4, 144, 24)
        pygame.draw.rect(surface, (12, 18, 26), mus_bar_rect, border_radius=5)
        pygame.draw.rect(surface, (45, 65, 90), mus_bar_rect, width=1, border_radius=5)
        mus_fill_w = int((mus_bar_rect.width - 4) * mus_vol)
        if mus_fill_w > 0:
            pygame.draw.rect(surface, (190, 110, 245), (mus_bar_rect.left + 2, mus_bar_rect.top + 2, mus_fill_w, mus_bar_rect.height - 4), border_radius=4)
        mus_pct_txt = tiny_font.render(f"{int(round(mus_vol * 100))}%", True, WHITE)
        surface.blit(mus_pct_txt, (mus_bar_rect.centerx - mus_pct_txt.get_width() // 2, mus_bar_rect.centery - mus_pct_txt.get_height() // 2))

        # Подсказка
        tip_sound = tiny_font.render("Совет: Снижение громкости звуков делает битву приятной на скорости 3x-8x.", True, (140, 170, 200))
        surface.blit(tip_sound, (col1_x + 18, 276))
        tip_sound2 = tiny_font.render("Все синтезированные частоты и музыка адаптируются в реальном времени.", True, (110, 140, 170))
        surface.blit(tip_sound2, (col1_x + 18, 298))

        # -------------------------------------------------------------
        # КАРТОЧКА 2 (Лево-Низ): УПРАВЛЕНИЕ ДАННЫМИ
        # -------------------------------------------------------------
        c2_rect = pygame.Rect(col1_x, 388, card_w, 268)
        pygame.draw.rect(surface, (18, 22, 32), c2_rect, border_radius=12)
        pygame.draw.rect(surface, (75, 45, 60), c2_rect, width=2, border_radius=12)

        pygame.draw.rect(surface, (38, 20, 28), (col1_x, 388, card_w, 40), border_top_left_radius=12, border_top_right_radius=12)
        pygame.draw.line(surface, (75, 45, 60), (col1_x, 428), (col1_x + card_w, 428), 1)
        c2_hdr = font.render("ТЕКУЩИЙ ПРОФИЛЬ И ДАННЫЕ", True, (255, 140, 150))
        surface.blit(c2_hdr, (col1_x + 18, 396))

        player_name = savedata.get("PlayerName", "sonofstrange")
        cur_sname = savedata.get("SaveName", "Основное сохранение")
        cur_sid = savedata.get("SaveId", "slot_main")
        cur_updated = savedata.get("UpdatedAt", "-")

        cur_play_sec = savedata.get("Stats", {}).get("play_time_seconds", 0.0)
        cur_ptime_str = format_play_time(cur_play_sec)

        p_d0 = small_font.render(f"Текущий профиль: '{cur_sname}'", True, (130, 230, 255))
        surface.blit(p_d0, (col1_x + 18, 438))
        p_d_time = tiny_font.render(f"Время в игре: {cur_ptime_str}  •  Обновлён: {cur_updated}", True, (255, 220, 130))
        surface.blit(p_d_time, (col1_x + 18, 464))
        p_d1 = tiny_font.render(f"Слот файла: saves/{cur_sid}.json  (Шифрование CTD1)", True, (185, 205, 230))
        surface.blit(p_d1, (col1_x + 18, 486))
        p_d2 = tiny_font.render("Шифрованный экспорт/импорт позволяет переносить прогресс между ПК и телефоном.", True, (140, 175, 205))
        surface.blit(p_d2, (col1_x + 18, 508))

        # Ряд 1 кнопок: Экспорт и Импорт (быстрый перенос через буфер обмена)
        btn_y1 = 538
        export_active_btn = pygame.Rect(col1_x + 18, btn_y1, 266, 38)
        import_active_btn = pygame.Rect(col1_x + 296, btn_y1, 266, 38)

        exp_hov = export_active_btn.collidepoint(mouse_pos)
        imp_hov = import_active_btn.collidepoint(mouse_pos)

        pygame.draw.rect(surface, (36, 95, 145) if exp_hov else (24, 68, 105), export_active_btn, border_radius=7)
        pygame.draw.rect(surface, (100, 215, 255) if exp_hov else (55, 120, 180), export_active_btn, width=1, border_radius=7)
        t_exp = font.render("ЭКСПОРТ (КОД В БУФЕР)", True, WHITE)
        surface.blit(t_exp, (export_active_btn.centerx - t_exp.get_width() // 2, export_active_btn.centery - t_exp.get_height() // 2))

        pygame.draw.rect(surface, (36, 130, 75) if imp_hov else (25, 95, 52), import_active_btn, border_radius=7)
        pygame.draw.rect(surface, GOLD if imp_hov else (110, 225, 150), import_active_btn, width=1, border_radius=7)
        t_imp = font.render("ИМПОРТ ИЗ БУФЕРА", True, WHITE)
        surface.blit(t_imp, (import_active_btn.centerx - t_imp.get_width() // 2, import_active_btn.centery - t_imp.get_height() // 2))

        # Ряд 2 кнопок: Слоты сохранений и Сброс профиля
        btn_y2 = 586
        go_to_saves_btn = pygame.Rect(col1_x + 18, btn_y2, 360, 44)
        gts_hov = go_to_saves_btn.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (32, 75, 115) if gts_hov else (22, 52, 85), go_to_saves_btn, border_radius=8)
        pygame.draw.rect(surface, (100, 205, 255) if gts_hov else (55, 115, 175), go_to_saves_btn, width=2, border_radius=8)
        gts_txt = font.render(f"СЛОТЫ СОХРАНЕНИЙ ({len(all_profiles)}) >", True, WHITE)
        surface.blit(gts_txt, (go_to_saves_btn.centerx - gts_txt.get_width() // 2, go_to_saves_btn.centery - gts_txt.get_height() // 2))

        reset_btn_rect = pygame.Rect(col1_x + 390, btn_y2, 172, 44)
        r_hov = reset_btn_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (165, 38, 45) if r_hov else (125, 28, 35), reset_btn_rect, border_radius=8)
        pygame.draw.rect(surface, (255, 120, 130) if r_hov else (180, 50, 60), reset_btn_rect, width=2, border_radius=8)
        r_txt = font.render("[!] СБРОСИТЬ", True, WHITE)
        surface.blit(r_txt, (reset_btn_rect.centerx - r_txt.get_width() // 2, reset_btn_rect.centery - r_txt.get_height() // 2))

        # -------------------------------------------------------------
        # КАРТОЧКА 3 (Право-Верх): ГЕЙМПЛЕЙ И ГРАФИКА
        # -------------------------------------------------------------
        c3_rect = pygame.Rect(col2_x, 126, card_w, 252)
        pygame.draw.rect(surface, (18, 25, 36), c3_rect, border_radius=12)
        pygame.draw.rect(surface, (50, 85, 125), c3_rect, width=2, border_radius=12)

        pygame.draw.rect(surface, (25, 36, 52), (col2_x, 126, card_w, 40), border_top_left_radius=12, border_top_right_radius=12)
        pygame.draw.line(surface, (50, 85, 125), (col2_x, 166), (col2_x + card_w, 166), 1)
        c3_hdr = font.render("ИГРОВЫЕ ПАРАМЕТРЫ И ГРАФИКА", True, (130, 205, 255))
        surface.blit(c3_hdr, (col2_x + 18, 134))

        # 3.0 Пресет графики (Graphics Preset)
        row0_y = 172
        lbl_gfx = small_font.render("Пресет графики (Visuals):", True, WHITE)
        surface.blit(lbl_gfx, (col2_x + 18, row0_y + 4))

        preset_normal_rect = pygame.Rect(col2_x + 276, row0_y, 134, 26)
        preset_opt_rect = pygame.Rect(col2_x + 418, row0_y, 144, 26)
        pn_hov = preset_normal_rect.collidepoint(mouse_pos)
        po_hov = preset_opt_rect.collidepoint(mouse_pos)

        is_norm = (gfx_preset == "normal")
        is_opt = (gfx_preset == "optimized")

        # Кнопка: Нормальный
        p_norm_bg = (30, 95, 150) if is_norm else ((28, 40, 56) if pn_hov else (20, 26, 36))
        p_norm_bd = (110, 215, 255) if is_norm else ((70, 105, 140) if pn_hov else (45, 60, 80))
        pygame.draw.rect(surface, p_norm_bg, preset_normal_rect, border_radius=6)
        pygame.draw.rect(surface, p_norm_bd, preset_normal_rect, width=2 if is_norm else 1, border_radius=6)
        t_norm = nav_font.render("НОРМАЛЬНЫЙ", True, WHITE if is_norm else (160, 185, 210))
        surface.blit(t_norm, (preset_normal_rect.centerx - t_norm.get_width() // 2, preset_normal_rect.centery - t_norm.get_height() // 2))

        # Кнопка: Оптимизированный
        p_opt_bg = (35, 125, 65) if is_opt else ((28, 40, 56) if po_hov else (20, 26, 36))
        p_opt_bd = (95, 235, 140) if is_opt else ((70, 105, 140) if po_hov else (45, 60, 80))
        pygame.draw.rect(surface, p_opt_bg, preset_opt_rect, border_radius=6)
        pygame.draw.rect(surface, p_opt_bd, preset_opt_rect, width=2 if is_opt else 1, border_radius=6)
        t_opt = nav_font.render("ОПТИМИЗАЦИЯ", True, WHITE if is_opt else (160, 185, 210))
        surface.blit(t_opt, (preset_opt_rect.centerx - t_opt.get_width() // 2, preset_opt_rect.centery - t_opt.get_height() // 2))

        # 3.1 Масштабирование экрана (Чёткость / Сглаживание)
        row1_y = 204
        lbl_scale = small_font.render("Чёткость экрана (Масштаб):", True, WHITE)
        surface.blit(lbl_scale, (col2_x + 18, row1_y + 4))

        scale_mode = savedata.get("Settings", {}).get("scale_quality", "sharp")
        is_sharp = (scale_mode != "smooth")
        is_smooth = (scale_mode == "smooth")

        scale_sharp_rect = pygame.Rect(col2_x + 276, row1_y, 134, 26)
        scale_smooth_rect = pygame.Rect(col2_x + 418, row1_y, 144, 26)
        ssh_hov = scale_sharp_rect.collidepoint(mouse_pos)
        ssm_hov = scale_smooth_rect.collidepoint(mouse_pos)

        p_sharp_bg = (30, 95, 150) if is_sharp else ((28, 40, 56) if ssh_hov else (20, 26, 36))
        p_sharp_bd = (110, 215, 255) if is_sharp else ((70, 105, 140) if ssh_hov else (45, 60, 80))
        pygame.draw.rect(surface, p_sharp_bg, scale_sharp_rect, border_radius=6)
        pygame.draw.rect(surface, p_sharp_bd, scale_sharp_rect, width=2 if is_sharp else 1, border_radius=6)
        t_sharp = nav_font.render("ПИКСЕЛЬНЫЙ", True, WHITE if is_sharp else (160, 185, 210))
        surface.blit(t_sharp, (scale_sharp_rect.centerx - t_sharp.get_width() // 2, scale_sharp_rect.centery - t_sharp.get_height() // 2))

        p_smooth_bg = (35, 125, 65) if is_smooth else ((28, 40, 56) if ssm_hov else (20, 26, 36))
        p_smooth_bd = (95, 235, 140) if is_smooth else ((70, 105, 140) if ssm_hov else (45, 60, 80))
        pygame.draw.rect(surface, p_smooth_bg, scale_smooth_rect, border_radius=6)
        pygame.draw.rect(surface, p_smooth_bd, scale_smooth_rect, width=2 if is_smooth else 1, border_radius=6)
        t_smooth = nav_font.render("СГЛАЖИВАНИЕ", True, WHITE if is_smooth else (160, 185, 210))
        surface.blit(t_smooth, (scale_smooth_rect.centerx - t_smooth.get_width() // 2, scale_smooth_rect.centery - t_smooth.get_height() // 2))

        # 3.2 Тряска экрана (Screen Shake)
        row2_y = 234
        shake_toggle_rect = pygame.Rect(col2_x + 440, row2_y, 115, 26)
        st_hov = shake_toggle_rect.collidepoint(mouse_pos)
        t_shake_col = (40, 140, 75) if shake_val else (48, 55, 68)
        sh_border = GOLD if st_hov else (((120, 220, 150) if shake_val else (80, 90, 105)))
        pygame.draw.rect(surface, (55, 175, 95) if (st_hov and shake_val) else t_shake_col, shake_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, sh_border, shake_toggle_rect, width=1, border_radius=6)
        s_btn_lbl = font.render("ВКЛ" if shake_val else "ВЫКЛ", True, WHITE)
        surface.blit(s_btn_lbl, (shake_toggle_rect.centerx - s_btn_lbl.get_width() // 2, shake_toggle_rect.centery - s_btn_lbl.get_height() // 2))

        lbl_sh = small_font.render("Тряска экрана (Screen Shake):", True, WHITE)
        surface.blit(lbl_sh, (col2_x + 18, row2_y + 3))

        # 3.3 Цифры урона
        row3_y = 264
        dmg_toggle_rect = pygame.Rect(col2_x + 440, row3_y, 115, 26)
        dt_hov = dmg_toggle_rect.collidepoint(mouse_pos)
        t_dmg_col = (40, 140, 75) if dmg_val else (48, 55, 68)
        dg_border = GOLD if dt_hov else (((120, 220, 150) if dmg_val else (80, 90, 105)))
        pygame.draw.rect(surface, (55, 175, 95) if (dt_hov and dmg_val) else t_dmg_col, dmg_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, dg_border, dmg_toggle_rect, width=1, border_radius=6)
        d_btn_lbl = font.render("ВКЛ" if dmg_val else "ВЫКЛ", True, WHITE)
        surface.blit(d_btn_lbl, (dmg_toggle_rect.centerx - d_btn_lbl.get_width() // 2, dmg_toggle_rect.centery - d_btn_lbl.get_height() // 2))

        lbl_dmg = small_font.render("Всплывающий урон и текст:", True, WHITE)
        surface.blit(lbl_dmg, (col2_x + 18, row3_y + 3))

        # 3.4 Авто-старт волны
        row4_y = 294
        auto_wave_toggle_rect = pygame.Rect(col2_x + 440, row4_y, 115, 26)
        at_hov = auto_wave_toggle_rect.collidepoint(mouse_pos)
        t_auto_col = (40, 140, 75) if auto_wave_val else (48, 55, 68)
        aw_border = GOLD if at_hov else (((120, 220, 150) if auto_wave_val else (80, 90, 105)))
        pygame.draw.rect(surface, (55, 175, 95) if (at_hov and auto_wave_val) else t_auto_col, auto_wave_toggle_rect, border_radius=6)
        pygame.draw.rect(surface, aw_border, auto_wave_toggle_rect, width=1, border_radius=6)
        a_btn_lbl = font.render("ВКЛ" if auto_wave_val else "ВЫКЛ", True, WHITE)
        surface.blit(a_btn_lbl, (auto_wave_toggle_rect.centerx - a_btn_lbl.get_width() // 2, auto_wave_toggle_rect.centery - a_btn_lbl.get_height() // 2))

        lbl_aw = small_font.render("Авто-запуск следующей волны:", True, WHITE)
        surface.blit(lbl_aw, (col2_x + 18, row4_y + 3))

        sub_gp = tiny_font.render("Нормальный: живой фон и декор. Оптимизация: скрыт декор биомов, макс. FPS.", True, (140, 185, 230))
        surface.blit(sub_gp, (col2_x + 18, 326))
        sub_gp2 = tiny_font.render("Режим оптимизации снижает нагрузку на CPU/GPU и бережёт батарею смартфона.", True, (120, 150, 180))
        surface.blit(sub_gp2, (col2_x + 18, 344))

        # -------------------------------------------------------------
        # КАРТОЧКА 4 (Право-Низ): ФИНАЛ И ТИТРЫ ИГРЫ
        # -------------------------------------------------------------
        c4_rect = pygame.Rect(col2_x, 388, card_w, 268)
        pygame.draw.rect(surface, (20, 16, 32), c4_rect, border_radius=12)
        pygame.draw.rect(surface, (110, 65, 170) if game_done else (70, 50, 90), c4_rect, width=2, border_radius=12)

        pygame.draw.rect(surface, (34, 22, 52) if game_done else (28, 22, 38), (col2_x, 388, card_w, 40), border_top_left_radius=12, border_top_right_radius=12)
        pygame.draw.line(surface, (110, 65, 170) if game_done else (70, 50, 90), (col2_x, 428), (col2_x + card_w, 428), 1)
        c4_hdr = font.render("ФИНАЛ И ТИТРЫ (ЭПИЛОГ)", True, (225, 175, 255) if game_done else (170, 150, 190))
        surface.blit(c4_hdr, (col2_x + 18, 396))

        # Бейдж статуса прохождения игры
        if game_done:
            st_bg = (30, 65, 40)
            st_bd = (70, 220, 120)
            st_txt_s = "[* ВОЛНА 100 ПРОЙДЕНА]"
            st_txt_col = (210, 255, 220)
        else:
            st_bg = (55, 20, 25)
            st_bd = (220, 75, 85)
            st_txt_s = "ТРЕБУЕТСЯ ВОЛНА 100"
            st_txt_col = (255, 175, 175)

        status_badge_rect = pygame.Rect(col2_x + card_w - 235, 394, 218, 28)
        pygame.draw.rect(surface, st_bg, status_badge_rect, border_radius=6)
        pygame.draw.rect(surface, st_bd, status_badge_rect, width=1, border_radius=6)
        sb_surf = tiny_font.render(st_txt_s, True, st_txt_col)
        surface.blit(sb_surf, (status_badge_rect.centerx - sb_surf.get_width() // 2, status_badge_rect.centery - sb_surf.get_height() // 2))

        if game_done:
            cr_d1 = small_font.render("Эпилог обороны Оазиса и разгром Короля Слаймов.", True, (220, 215, 235))
            cr_d4 = tiny_font.render("Вы можете просмотреть титры повторно в любой момент без сброса волн.", True, (215, 195, 255))
        else:
            cr_d1 = small_font.render("Финальные титры и эпилог заблокированы до победы.", True, (255, 160, 170))
            cr_d4 = tiny_font.render("Пройдите 100-ю волну на локации Финал, чтобы разблокировать просмотр.", True, (255, 130, 140))

        surface.blit(cr_d1, (col2_x + 18, 440))
        cr_d2 = tiny_font.render("Включает статистику кампании, оригинальные слаймы Stardew Valley,", True, (170, 160, 195))
        surface.blit(cr_d2, (col2_x + 18, 468))
        cr_d3 = tiny_font.render("описание тёмной экономики, саундтрек Звёздного Царства и титры авторов.", True, (170, 160, 195))
        surface.blit(cr_d3, (col2_x + 18, 492))
        surface.blit(cr_d4, (col2_x + 18, 514))

        credits_btn_rect = pygame.Rect(col2_x + 18, 592, 410, 44)
        if game_done:
            cr_hov = credits_btn_rect.collidepoint(mouse_pos)
            pygame.draw.rect(surface, (95, 45, 155) if cr_hov else (72, 32, 120), credits_btn_rect, border_radius=8)
            pygame.draw.rect(surface, GOLD if cr_hov else (195, 130, 255), credits_btn_rect, width=2, border_radius=8)
            cr_btn_txt = font.render("ПРОСМОТР ТИТРОВ И ЭПИЛОГА", True, WHITE)
            surface.blit(cr_btn_txt, (credits_btn_rect.centerx - cr_btn_txt.get_width() // 2, credits_btn_rect.centery - cr_btn_txt.get_height() // 2))
        else:
            # Заблокировано
            pygame.draw.rect(surface, (36, 30, 42), credits_btn_rect, border_radius=8)
            pygame.draw.rect(surface, (80, 60, 80), credits_btn_rect, width=1, border_radius=8)
            cr_btn_txt = font.render("ТИТРЫ ЗАБЛОКИРОВАНЫ", True, (140, 130, 150))
            surface.blit(cr_btn_txt, (credits_btn_rect.centerx - cr_btn_txt.get_width() // 2, credits_btn_rect.centery - cr_btn_txt.get_height() // 2))

    # =========================================================================
    # ВКЛАДКА 2: ФАЙЛЫ СОХРАНЕНИЙ (СЛОТЫ И ПРОФИЛИ)
    # =========================================================================
    else:
        # Подзаголовок и кнопка создания нового профиля
        s_title = font.render("УПРАВЛЕНИЕ СЛОТАМИ СОХРАНЕНИЙ", True, (240, 250, 255))
        surface.blit(s_title, (col1_x, 126))
        s_sub = tiny_font.render("Создавайте сколько угодно профилей, переключайтесь между кампаниями и копируйте слоты.", True, (140, 185, 230))
        surface.blit(s_sub, (col1_x, 150))

        create_save_btn = pygame.Rect(SCREEN_WIDTH - 42 - 250, 122, 250, 42)
        cs_hov = create_save_btn.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (32, 120, 65) if cs_hov else (24, 92, 50), create_save_btn, border_radius=8)
        pygame.draw.rect(surface, GOLD if cs_hov else (100, 225, 145), create_save_btn, width=2, border_radius=8)
        cs_txt = font.render("+ НОВОЕ СОХРАНЕНИЕ", True, WHITE)
        surface.blit(cs_txt, (create_save_btn.centerx - cs_txt.get_width() // 2, create_save_btn.centery - cs_txt.get_height() // 2))

        import_clipboard_btn = pygame.Rect(SCREEN_WIDTH - 42 - 250 - 230 - 14, 122, 230, 42)
        ic_hov = import_clipboard_btn.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (36, 95, 145) if ic_hov else (25, 68, 105), import_clipboard_btn, border_radius=8)
        pygame.draw.rect(surface, (100, 215, 255) if ic_hov else (60, 140, 210), import_clipboard_btn, width=1, border_radius=8)
        ic_txt = font.render("ИМПОРТ ИЗ БУФЕРА", True, WHITE)
        surface.blit(ic_txt, (import_clipboard_btn.centerx - ic_txt.get_width() // 2, import_clipboard_btn.centery - ic_txt.get_height() // 2))

        # Контейнер списка слотов
        container_rect = pygame.Rect(42, 172, 1196, 484)
        pygame.draw.rect(surface, (14, 18, 26), container_rect, border_radius=12)
        pygame.draw.rect(surface, (38, 52, 72), container_rect, width=1, border_radius=12)

        card_gap = 10
        card_h = 106
        total_content_h = len(all_profiles) * (card_h + card_gap) + 16
        max_scroll = max(0, total_content_h - container_rect.height)
        cur_scroll = max(0, min(saves_scroll_y, max_scroll))

        surface.set_clip(container_rect)

        for i, p in enumerate(all_profiles):
            card_y = container_rect.y + 10 + i * (card_h + card_gap) - cur_scroll
            card_w_inner = container_rect.width - 24
            card_rect = pygame.Rect(container_rect.x + 12, card_y, card_w_inner, card_h)

            if card_rect.bottom < container_rect.top or card_rect.top > container_rect.bottom:
                continue

            is_act = p["is_active"]
            bg_col = (26, 38, 54) if is_act else (18, 24, 34)
            bd_col = (90, 205, 255) if is_act else (42, 58, 78)
            bd_w = 2 if is_act else 1

            pygame.draw.rect(surface, bg_col, card_rect, border_radius=10)
            pygame.draw.rect(surface, bd_col, card_rect, width=bd_w, border_radius=10)

            # Левая полоска-акцент для активного профиля
            if is_act:
                pygame.draw.rect(surface, (70, 210, 255), (card_rect.left, card_rect.top, 6, card_rect.height),
                                 border_top_left_radius=10, border_bottom_left_radius=10)

            # 1. Название сохранения и бейдж активного слота
            name_x = card_rect.left + (20 if is_act else 16)
            name_surf = font.render(p["name"], True, (255, 235, 140) if is_act else WHITE)
            surface.blit(name_surf, (name_x, card_rect.top + 8))

            if is_act:
                act_badge_rect = pygame.Rect(name_x + name_surf.get_width() + 12, card_rect.top + 7, 130, 24)
                pygame.draw.rect(surface, (25, 68, 42), act_badge_rect, border_radius=5)
                pygame.draw.rect(surface, (80, 220, 130), act_badge_rect, width=1, border_radius=5)
                ab_txt = tiny_font.render("[ТЕКУЩИЙ СЛОТ]", True, (180, 255, 200))
                surface.blit(ab_txt, (act_badge_rect.centerx - ab_txt.get_width() // 2, act_badge_rect.centery - ab_txt.get_height() // 2))

            # 2. Дата создания и изменения
            dt_txt = f"ID: {p['id']}  |  Создан: {p.get('created_at', '—')}  |  Обновлён: {p.get('updated_at', '—')}"
            dt_surf = tiny_font.render(dt_txt, True, (135, 155, 180))
            surface.blit(dt_surf, (name_x, card_rect.top + 34))

            # 3. Первая строка индикаторов: Звёзды, Тёмные, Рекорд, Время
            r3_y = card_rect.top + 56
            bx = name_x

            # Звёздные кактусы
            surface.blit(stellar_cactus_img_s, (bx, r3_y - 2))
            bx += 18
            s_chip = tiny_font.render(f"{p['stars']:,}", True, (255, 225, 120))
            surface.blit(s_chip, (bx, r3_y))
            bx += s_chip.get_width() + 18

            # Тёмные кактусы
            surface.blit(dark_cactus_img_s, (bx, r3_y - 2))
            bx += 18
            d_chip = tiny_font.render(f"{p['dark']:,}", True, (215, 140, 255))
            surface.blit(d_chip, (bx, r3_y))
            bx += d_chip.get_width() + 18

            # Рекорд волны
            w_chip = tiny_font.render(f"Рекорд: волна {p['max_wave']}", True, (120, 215, 255))
            surface.blit(w_chip, (bx, r3_y))
            bx += w_chip.get_width() + 18

            # Время в игре
            ptime_str = format_play_time(p.get("play_time", 0.0))
            time_chip = tiny_font.render(f"Время: {ptime_str}", True, (255, 225, 130))
            surface.blit(time_chip, (bx, r3_y))
            bx += time_chip.get_width() + 18

            # Финал пройден
            if p.get("game_completed", False):
                fin_chip = tiny_font.render("[ФИНАЛ ПРОЙДЕН]", True, GOLD)
                surface.blit(fin_chip, (bx, r3_y))

            # 4. Вторая строка индикаторов: Оранжерея, Реликвии, Древо улучшений
            r4_y = card_rect.top + 78
            bx4 = name_x

            # Оранжерея
            gh_txt = f"Оранжерея: {p.get('greenhouse_count', 0)}/8 (ур. {p.get('greenhouse_total_lvl', 0)})"
            gh_chip = tiny_font.render(gh_txt, True, (140, 235, 185))
            surface.blit(gh_chip, (bx4, r4_y))
            bx4 += gh_chip.get_width() + 18

            # Реликвии (счётчик сколько открыто + суммарный уровень, как у оранжереи)
            r_c = p.get('relics_count', 0)
            r_m = p.get('relics_max_count', 20)
            r_lvl = p.get('relics_total_lvl', 0)
            rel_txt = f"Реликвии: {r_c}/{r_m} (ур. {r_lvl})"
            rel_chip = tiny_font.render(rel_txt, True, (255, 215, 120))
            surface.blit(rel_chip, (bx4, r4_y))
            bx4 += rel_chip.get_width() + 18

            # Древо улучшений
            tree_txt = f"Древо: {p.get('bought_nodes', 0)}/{p.get('total_nodes', 64)} нод • {p.get('bought_upgrades', 0)}/{p.get('total_upgrades', 239)} улучш."
            tree_chip = tiny_font.render(tree_txt, True, (180, 195, 225))
            surface.blit(tree_chip, (bx4, r4_y))

            # 5. Кнопки действий справа карточки
            btn_w_del = 88
            btn_w_exp = 92
            btn_w_copy = 78
            btn_w_ren = 68
            btn_w_sel = 96
            btn_h = 34
            btn_y = card_rect.top + 36

            rx = card_rect.right - 14

            # Удалить
            del_rect = pygame.Rect(rx - btn_w_del, btn_y, btn_w_del, btn_h)
            d_hov = del_rect.collidepoint(mouse_pos)
            pygame.draw.rect(surface, (160, 35, 42) if d_hov else (115, 25, 32), del_rect, border_radius=6)
            pygame.draw.rect(surface, (255, 110, 120) if d_hov else (160, 50, 60), del_rect, width=1, border_radius=6)
            d_txt = small_font.render("УДАЛИТЬ", True, WHITE)
            surface.blit(d_txt, (del_rect.centerx - d_txt.get_width() // 2, del_rect.centery - d_txt.get_height() // 2))
            rx -= (btn_w_del + 8)

            # Экспорт
            exp_rect = pygame.Rect(rx - btn_w_exp, btn_y, btn_w_exp, btn_h)
            e_hov = exp_rect.collidepoint(mouse_pos)
            pygame.draw.rect(surface, (35, 95, 145) if e_hov else (24, 68, 105), exp_rect, border_radius=6)
            pygame.draw.rect(surface, (100, 215, 255) if e_hov else (55, 120, 180), exp_rect, width=1, border_radius=6)
            e_txt = small_font.render("ЭКСПОРТ", True, WHITE)
            surface.blit(e_txt, (exp_rect.centerx - e_txt.get_width() // 2, exp_rect.centery - e_txt.get_height() // 2))
            rx -= (btn_w_exp + 8)

            # Дублировать / Копия
            copy_rect = pygame.Rect(rx - btn_w_copy, btn_y, btn_w_copy, btn_h)
            c_hov = copy_rect.collidepoint(mouse_pos)
            pygame.draw.rect(surface, (72, 42, 105) if c_hov else (52, 30, 78), copy_rect, border_radius=6)
            pygame.draw.rect(surface, (175, 120, 245) if c_hov else (110, 65, 160), copy_rect, width=1, border_radius=6)
            c_txt = small_font.render("КОПИЯ", True, WHITE)
            surface.blit(c_txt, (copy_rect.centerx - c_txt.get_width() // 2, copy_rect.centery - c_txt.get_height() // 2))
            rx -= (btn_w_copy + 8)

            # Переименовать
            ren_rect = pygame.Rect(rx - btn_w_ren, btn_y, btn_w_ren, btn_h)
            rn_hov = ren_rect.collidepoint(mouse_pos)
            pygame.draw.rect(surface, (45, 68, 95) if rn_hov else (32, 48, 70), ren_rect, border_radius=6)
            pygame.draw.rect(surface, (120, 175, 235) if rn_hov else (65, 95, 135), ren_rect, width=1, border_radius=6)
            rn_txt = small_font.render("ИМЯ", True, WHITE)
            surface.blit(rn_txt, (ren_rect.centerx - rn_txt.get_width() // 2, ren_rect.centery - rn_txt.get_height() // 2))
            rx -= (btn_w_ren + 8)

            # Выбрать (если не активен) или Индикатор текущего
            if is_act:
                act_ind_rect = pygame.Rect(rx - btn_w_sel, btn_y, btn_w_sel, btn_h)
                pygame.draw.rect(surface, (25, 55, 38), act_ind_rect, border_radius=6)
                pygame.draw.rect(surface, (70, 180, 110), act_ind_rect, width=1, border_radius=6)
                ind_txt = small_font.render("АКТИВЕН", True, (180, 255, 200))
                surface.blit(ind_txt, (act_ind_rect.centerx - ind_txt.get_width() // 2, act_ind_rect.centery - ind_txt.get_height() // 2))
                sel_rect = None
            else:
                sel_rect = pygame.Rect(rx - btn_w_sel, btn_y, btn_w_sel, btn_h)
                sl_hov = sel_rect.collidepoint(mouse_pos)
                pygame.draw.rect(surface, (35, 105, 175) if sl_hov else (24, 75, 130), sel_rect, border_radius=6)
                pygame.draw.rect(surface, (100, 215, 255) if sl_hov else (60, 140, 215), sel_rect, width=1, border_radius=6)
                sel_txt = small_font.render("ВЫБРАТЬ", True, WHITE)
                surface.blit(sel_txt, (sel_rect.centerx - sel_txt.get_width() // 2, sel_rect.centery - sel_txt.get_height() // 2))

            save_actions.append({
                "id": p["id"],
                "name": p["name"],
                "select": sel_rect,
                "rename": ren_rect,
                "duplicate": copy_rect,
                "export": exp_rect,
                "delete": del_rect
            })

        surface.set_clip(None)

        # Отрисовка полосы прокрутки, если список длиннее контейнера
        if max_scroll > 0:
            sb_track = pygame.Rect(container_rect.right - 8, container_rect.top + 4, 6, container_rect.height - 8)
            pygame.draw.rect(surface, (20, 26, 36), sb_track, border_radius=3)
            thumb_ratio = container_rect.height / total_content_h
            thumb_h = max(24, int(sb_track.height * thumb_ratio))
            scroll_pct = cur_scroll / max_scroll
            thumb_y = sb_track.y + int((sb_track.height - thumb_h) * scroll_pct)
            thumb_rect = pygame.Rect(sb_track.x, thumb_y, 6, thumb_h)
            pygame.draw.rect(surface, (80, 130, 185), thumb_rect, border_radius=3)

    # =========================================================================
    # МОДАЛЬНЫЕ ОКНА И ДИАЛОГИ
    # =========================================================================
    confirm_yes_btn = None
    confirm_no_btn = None
    modal_ok_btn = None
    modal_cancel_btn = None

    # 1. Модальное окно полного сброса сохранения (confirming_reset)
    if confirming_reset:
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 215))
        surface.blit(dim_surf, (0, 0))

        mw, mh = 560, 250
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        m_rect = pygame.Rect(mx, my, mw, mh)

        pygame.draw.rect(surface, (24, 18, 26), m_rect, border_radius=14)
        pygame.draw.rect(surface, RED, m_rect, width=2, border_radius=14)

        m_title = large_font.render("СБРОС ТЕКУЩЕГО СЛОТА?", True, RED)
        surface.blit(m_title, (m_rect.centerx - m_title.get_width() // 2, my + 24))

        m_msg1 = small_font.render("Вы действительно хотите сбросить прогресс текущего слота?", True, WHITE)
        surface.blit(m_msg1, (m_rect.centerx - m_msg1.get_width() // 2, my + 76))
        m_msg2 = tiny_font.render("Все звёздные кактусы, таланты и рекорды этого слота будут стёрты!", True, (255, 175, 175))
        surface.blit(m_msg2, (m_rect.centerx - m_msg2.get_width() // 2, my + 110))

        confirm_yes_btn = pygame.Rect(mx + 38, my + 160, 220, 48)
        confirm_no_btn = pygame.Rect(mx + mw - 258, my + 160, 220, 48)

        cy_hov = confirm_yes_btn.collidepoint(mouse_pos)
        cn_hov = confirm_no_btn.collidepoint(mouse_pos)

        pygame.draw.rect(surface, (190, 40, 50) if cy_hov else (145, 28, 35), confirm_yes_btn, border_radius=8)
        pygame.draw.rect(surface, WHITE if cy_hov else (240, 120, 130), confirm_yes_btn, width=2, border_radius=8)
        t_cy = font.render("ДА, СБРОСИТЬ", True, WHITE)
        surface.blit(t_cy, (confirm_yes_btn.centerx - t_cy.get_width() // 2, confirm_yes_btn.centery - t_cy.get_height() // 2))

        pygame.draw.rect(surface, (40, 140, 70) if cn_hov else (28, 105, 52), confirm_no_btn, border_radius=8)
        pygame.draw.rect(surface, GOLD if cn_hov else (140, 235, 170), confirm_no_btn, width=2, border_radius=8)
        t_cn = font.render("ОТМЕНА [ESC]", True, WHITE)
        surface.blit(t_cn, (confirm_no_btn.centerx - t_cn.get_width() // 2, confirm_no_btn.centery - t_cn.get_height() // 2))

    # 2. Модальное окно ввода имени (Создание или Переименование)
    elif modal_state and modal_state.get("type") == "input":
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 215))
        surface.blit(dim_surf, (0, 0))

        mw, mh = 580, 240
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        m_rect = pygame.Rect(mx, my, mw, mh)

        pygame.draw.rect(surface, (20, 28, 42), m_rect, border_radius=14)
        pygame.draw.rect(surface, (80, 185, 255), m_rect, width=2, border_radius=14)

        mode = modal_state.get("mode", "create")
        m_title_str = "НОВОЕ СОХРАНЕНИЕ" if mode == "create" else "ПЕРЕИМЕНОВАНИЕ СОХРАНЕНИЯ"
        m_title = large_font.render(m_title_str, True, (240, 250, 255))
        surface.blit(m_title, (m_rect.centerx - m_title.get_width() // 2, my + 20))

        sub_msg = tiny_font.render("Введите название файла сохранения (до 24 символов) и нажмите Enter:", True, (150, 195, 235))
        surface.blit(sub_msg, (m_rect.centerx - sub_msg.get_width() // 2, my + 60))

        # Поле ввода текста
        input_rect = pygame.Rect(mx + 36, my + 92, mw - 72, 44)
        pygame.draw.rect(surface, (12, 16, 26), input_rect, border_radius=8)
        pygame.draw.rect(surface, GOLD, input_rect, width=2, border_radius=8)

        text_str = modal_state.get("text", "")
        cursor_visible = (int(time.time() * 2.2) % 2 == 0)
        display_str = text_str + ("|" if cursor_visible else "")

        t_surf = font.render(display_str, True, WHITE)
        surface.blit(t_surf, (input_rect.left + 14, input_rect.centery - t_surf.get_height() // 2))

        # Кнопки Подтверждения и Отмены
        modal_ok_btn = pygame.Rect(mx + 36, my + 160, 240, 48)
        modal_cancel_btn = pygame.Rect(mx + mw - 276, my + 160, 240, 48)

        m_ok_hov = modal_ok_btn.collidepoint(mouse_pos)
        m_can_hov = modal_cancel_btn.collidepoint(mouse_pos)

        pygame.draw.rect(surface, (35, 135, 75) if m_ok_hov else (25, 105, 58), modal_ok_btn, border_radius=8)
        pygame.draw.rect(surface, GOLD if m_ok_hov else (120, 235, 160), modal_ok_btn, width=2, border_radius=8)
        t_ok = font.render("СОХРАНИТЬ [ENTER]", True, WHITE)
        surface.blit(t_ok, (modal_ok_btn.centerx - t_ok.get_width() // 2, modal_ok_btn.centery - t_ok.get_height() // 2))

        pygame.draw.rect(surface, (135, 45, 52) if m_can_hov else (105, 32, 38), modal_cancel_btn, border_radius=8)
        pygame.draw.rect(surface, WHITE if m_can_hov else (210, 110, 120), modal_cancel_btn, width=2, border_radius=8)
        t_can = font.render("ОТМЕНА [ESC]", True, WHITE)
        surface.blit(t_can, (modal_cancel_btn.centerx - t_can.get_width() // 2, modal_cancel_btn.centery - t_can.get_height() // 2))

    # 3. Модальное окно подтверждения удаления сохранения
    elif modal_state and modal_state.get("type") == "delete_confirm":
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 215))
        surface.blit(dim_surf, (0, 0))

        mw, mh = 580, 250
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        m_rect = pygame.Rect(mx, my, mw, mh)

        pygame.draw.rect(surface, (26, 16, 20), m_rect, border_radius=14)
        pygame.draw.rect(surface, RED, m_rect, width=2, border_radius=14)

        m_title = large_font.render("УДАЛИТЬ СОХРАНЕНИЕ?", True, RED)
        surface.blit(m_title, (m_rect.centerx - m_title.get_width() // 2, my + 22))

        d_name = modal_state.get("name", "")
        d_id = modal_state.get("target_id", "")
        m_msg1 = small_font.render(f"Вы действительно хотите удалить слот '{d_name}'?", True, WHITE)
        surface.blit(m_msg1, (m_rect.centerx - m_msg1.get_width() // 2, my + 72))

        m_msg2 = tiny_font.render(f"Файл saves/{d_id}.json и весь прогресс будут стёрты безвозвратно!", True, (255, 175, 175))
        surface.blit(m_msg2, (m_rect.centerx - m_msg2.get_width() // 2, my + 104))

        modal_ok_btn = pygame.Rect(mx + 36, my + 160, 240, 48)
        modal_cancel_btn = pygame.Rect(mx + mw - 276, my + 160, 240, 48)

        m_ok_hov = modal_ok_btn.collidepoint(mouse_pos)
        m_can_hov = modal_cancel_btn.collidepoint(mouse_pos)

        pygame.draw.rect(surface, (190, 40, 50) if m_ok_hov else (145, 28, 35), modal_ok_btn, border_radius=8)
        pygame.draw.rect(surface, WHITE if m_ok_hov else (240, 120, 130), modal_ok_btn, width=2, border_radius=8)
        t_ok = font.render("ДА, УДАЛИТЬ", True, WHITE)
        surface.blit(t_ok, (modal_ok_btn.centerx - t_ok.get_width() // 2, modal_ok_btn.centery - t_ok.get_height() // 2))

        pygame.draw.rect(surface, (40, 140, 70) if m_can_hov else (28, 105, 52), modal_cancel_btn, border_radius=8)
        pygame.draw.rect(surface, GOLD if m_can_hov else (140, 235, 170), modal_cancel_btn, width=2, border_radius=8)
        t_can = font.render("ОТМЕНА [ESC]", True, WHITE)
        surface.blit(t_can, (modal_cancel_btn.centerx - t_can.get_width() // 2, modal_cancel_btn.centery - t_can.get_height() // 2))

    # 4. Модальное окно успешного экспорта сохранения
    elif modal_state and modal_state.get("type") == "export":
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 215))
        surface.blit(dim_surf, (0, 0))

        mw, mh = 640, 280
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        m_rect = pygame.Rect(mx, my, mw, mh)

        pygame.draw.rect(surface, (18, 26, 38), m_rect, border_radius=14)
        pygame.draw.rect(surface, (90, 205, 255), m_rect, width=2, border_radius=14)

        m_title = large_font.render("ЭКСПОРТ СОХРАНЕНИЯ", True, (130, 220, 255))
        surface.blit(m_title, (m_rect.centerx - m_title.get_width() // 2, my + 20))

        code_str = modal_state.get("code", "")
        fpath = modal_state.get("file", "")

        msg1 = small_font.render("Зашифрованный ключ скопирован в буфер обмена!", True, (120, 255, 170))
        surface.blit(msg1, (m_rect.centerx - msg1.get_width() // 2, my + 64))

        preview_rect = pygame.Rect(mx + 30, my + 98, mw - 60, 42)
        pygame.draw.rect(surface, (10, 14, 22), preview_rect, border_radius=7)
        pygame.draw.rect(surface, (50, 75, 105), preview_rect, width=1, border_radius=7)
        disp_code = code_str[:54] + "..." if len(code_str) > 54 else code_str
        c_surf = tiny_font.render(disp_code, True, (240, 240, 255))
        surface.blit(c_surf, (preview_rect.left + 12, preview_rect.centery - c_surf.get_height() // 2))

        msg2 = tiny_font.render(f"Также создан файл: {os.path.basename(fpath)} (в папке saves)", True, (160, 180, 210))
        surface.blit(msg2, (m_rect.centerx - msg2.get_width() // 2, my + 152))

        modal_copy_code_btn = pygame.Rect(mx + 36, my + 195, 260, 48)
        modal_cancel_btn = pygame.Rect(mx + mw - 276, my + 195, 240, 48)

        cp_hov = modal_copy_code_btn.collidepoint(mouse_pos)
        can_hov = modal_cancel_btn.collidepoint(mouse_pos)

        pygame.draw.rect(surface, (35, 105, 175) if cp_hov else (24, 75, 130), modal_copy_code_btn, border_radius=8)
        pygame.draw.rect(surface, (100, 215, 255) if cp_hov else (60, 140, 215), modal_copy_code_btn, width=2, border_radius=8)
        t_cp = font.render("СКОПИРОВАТЬ ЕЩЁ", True, WHITE)
        surface.blit(t_cp, (modal_copy_code_btn.centerx - t_cp.get_width() // 2, modal_copy_code_btn.centery - t_cp.get_height() // 2))

        pygame.draw.rect(surface, (40, 140, 70) if can_hov else (28, 105, 52), modal_cancel_btn, border_radius=8)
        pygame.draw.rect(surface, GOLD if can_hov else (140, 235, 170), modal_cancel_btn, width=2, border_radius=8)
        t_can = font.render("ЗАКРЫТЬ [ESC]", True, WHITE)
        surface.blit(t_can, (modal_cancel_btn.centerx - t_can.get_width() // 2, modal_cancel_btn.centery - t_can.get_height() // 2))

    # 5. Модальное окно импорта сохранения
    elif modal_state and modal_state.get("type") == "import":
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 215))
        surface.blit(dim_surf, (0, 0))

        mw, mh = 660, 310
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        m_rect = pygame.Rect(mx, my, mw, mh)

        err_msg = modal_state.get("error", "")
        pygame.draw.rect(surface, (18, 24, 36), m_rect, border_radius=14)
        pygame.draw.rect(surface, RED if err_msg else (70, 185, 120), m_rect, width=2, border_radius=14)

        m_title = large_font.render("ИМПОРТ СОХРАНЕНИЯ", True, (130, 230, 170))
        surface.blit(m_title, (m_rect.centerx - m_title.get_width() // 2, my + 18))

        sub_msg = tiny_font.render("Вставьте зашифрованный ключ сохранения (CTD1_...) или нажмите «ВСТАВИТЬ»:", True, (170, 205, 235))
        surface.blit(sub_msg, (m_rect.centerx - sub_msg.get_width() // 2, my + 56))

        input_rect = pygame.Rect(mx + 30, my + 86, mw - 60, 42)
        pygame.draw.rect(surface, (10, 14, 22), input_rect, border_radius=8)
        pygame.draw.rect(surface, GOLD, input_rect, width=2, border_radius=8)

        text_str = modal_state.get("text", "")
        cursor_visible = (int(time.time() * 2.2) % 2 == 0)
        disp_txt = text_str if len(text_str) <= 48 else (text_str[:24] + "..." + text_str[-22:])
        display_str = disp_txt + ("|" if cursor_visible else "")
        t_surf = font.render(display_str, True, WHITE)
        surface.blit(t_surf, (input_rect.left + 12, input_rect.centery - t_surf.get_height() // 2))

        if err_msg:
            e_surf = tiny_font.render(err_msg, True, (255, 120, 130))
            surface.blit(e_surf, (m_rect.centerx - e_surf.get_width() // 2, my + 138))
        else:
            n_surf = tiny_font.render("Сохранение будет добавлено как новый слот и сделано активным.", True, (140, 180, 215))
            surface.blit(n_surf, (m_rect.centerx - n_surf.get_width() // 2, my + 138))

        modal_paste_code_btn = pygame.Rect(mx + 30, my + 172, 280, 44)
        modal_ok_btn = pygame.Rect(mx + 330, my + 172, 300, 44)
        modal_cancel_btn = pygame.Rect(mx + (mw - 240) // 2, my + 236, 240, 44)

        pst_hov = modal_paste_code_btn.collidepoint(mouse_pos)
        ok_hov = modal_ok_btn.collidepoint(mouse_pos)
        can_hov = modal_cancel_btn.collidepoint(mouse_pos)

        pygame.draw.rect(surface, (35, 95, 160) if pst_hov else (24, 68, 120), modal_paste_code_btn, border_radius=8)
        pygame.draw.rect(surface, (100, 215, 255) if pst_hov else (55, 125, 195), modal_paste_code_btn, width=1, border_radius=8)
        t_pst = font.render("ВСТАВИТЬ ИЗ БУФЕРА", True, WHITE)
        surface.blit(t_pst, (modal_paste_code_btn.centerx - t_pst.get_width() // 2, modal_paste_code_btn.centery - t_pst.get_height() // 2))

        pygame.draw.rect(surface, (35, 140, 75) if ok_hov else (25, 105, 58), modal_ok_btn, border_radius=8)
        pygame.draw.rect(surface, GOLD if ok_hov else (120, 235, 160), modal_ok_btn, width=2, border_radius=8)
        t_ok = font.render("ИМПОРТИРОВАТЬ", True, WHITE)
        surface.blit(t_ok, (modal_ok_btn.centerx - t_ok.get_width() // 2, modal_ok_btn.centery - t_ok.get_height() // 2))

        pygame.draw.rect(surface, (115, 35, 42) if can_hov else (85, 25, 32), modal_cancel_btn, border_radius=8)
        pygame.draw.rect(surface, WHITE if can_hov else (180, 80, 90), modal_cancel_btn, width=1, border_radius=8)
        t_can = font.render("ОТМЕНА [ESC]", True, WHITE)
        surface.blit(t_can, (modal_cancel_btn.centerx - t_can.get_width() // 2, modal_cancel_btn.centery - t_can.get_height() // 2))

    return {
        "back": back_btn,
        "tab_general": tab_gen_rect,
        "tab_saves": tab_saves_rect,
        "go_to_saves": go_to_saves_btn,
        "export_active": export_active_btn,
        "import_active": import_active_btn,
        "import_clipboard": import_clipboard_btn,
        "modal_copy_code": modal_copy_code_btn,
        "modal_paste_code": modal_paste_code_btn,
        "sfx_minus": sfx_minus_rect,
        "sfx_plus": sfx_plus_rect,
        "music_minus": music_minus_rect,
        "music_plus": music_plus_rect,
        "preset_normal": preset_normal_rect,
        "preset_opt": preset_opt_rect,
        "scale_sharp": scale_sharp_rect,
        "scale_smooth": scale_smooth_rect,
        "window_shake_toggle": None,
        "shake_toggle": shake_toggle_rect,
        "dmg_toggle": dmg_toggle_rect,
        "auto_wave_toggle": auto_wave_toggle_rect,
        "credits": (credits_btn_rect if (is_gen and game_done) else None),
        "credits_locked": (credits_btn_rect if (is_gen and not game_done) else None),
        "reset": reset_btn_rect,
        "confirm_yes": confirm_yes_btn,
        "confirm_no": confirm_no_btn,
        "create_save": create_save_btn,
        "save_actions": save_actions,
        "max_scroll": max_scroll,
        "modal_ok": modal_ok_btn,
        "modal_cancel": modal_cancel_btn
    }


# -------------------------------------------------------------------------
# ОКНО МИНИ-ИГРЫ: АРХЕОЛОГИЧЕСКИЕ РАСКОПКИ (МОРСКОЙ БОЙ 5x5)
# -------------------------------------------------------------------------
def draw_dig_window(surface, dig_session, mouse_pos):
    """Отрисовывает интерфейс мини-игры раскопок 5х5 во втором нативном окне ОС."""
    surface.fill((22, 18, 16))
    w, h = surface.get_size()

    # Внешняя древняя песчаная рамка
    pygame.draw.rect(surface, (180, 135, 55), (2, 2, w - 4, h - 4), width=2, border_radius=10)
    pygame.draw.rect(surface, (70, 50, 25), (4, 4, w - 8, h - 8), width=1, border_radius=8)

    # Верхний информационный блок
    header_rect = pygame.Rect(12, 10, w - 24, 72)
    pygame.draw.rect(surface, (36, 28, 22), header_rect, border_radius=8)
    pygame.draw.rect(surface, (115, 85, 35), header_rect, width=1, border_radius=8)

    surface.blit(shovel_icon, (header_rect.left + 10, header_rect.top + 14))

    title_txt = font.render("РАСКОПКИ РЕЛИКВИИ", True, (255, 230, 140))
    surface.blit(title_txt, (header_rect.left + 42, header_rect.top + 10))

    relic_name_col = (255, 215, 60) if not dig_session.is_won else (120, 255, 140)
    name_txt = font.render(dig_session.relic_info["name"], True, relic_name_col)
    surface.blit(name_txt, (header_rect.left + 42, header_rect.top + 32))

    # Счётчик оставшихся ходов (вскопок) справа
    moves_cnt = dig_session.moves_left
    col_moves = (100, 255, 140) if moves_cnt > 4 else ((255, 200, 50) if moves_cnt > 2 else (255, 90, 90))
    mv_num = large_font.render(str(moves_cnt), True, col_moves)
    surface.blit(mv_num, (header_rect.right - 44 - mv_num.get_width() // 2, header_rect.top + 12))
    mv_lbl = tiny_font.render("вскопок", True, (190, 175, 150))
    surface.blit(mv_lbl, (header_rect.right - 44 - mv_lbl.get_width() // 2, header_rect.top + 42))

    # Сетка раскопок 5х5 (морской бой)
    # Размер клетки 48х48, зазор 4 (шаг 52). Общая ширина 5*52 - 4 = 256.
    grid_x = (w - 256) // 2
    grid_y = 92

    for gy in range(5):
        for gx in range(5):
            cx = grid_x + gx * 52
            cy = grid_y + gy * 52
            cell_rect = pygame.Rect(cx, cy, 48, 48)

            is_dug = dig_session.dug[gy][gx]
            is_hit = (gx, gy) in dig_session.relic_cells and is_dug
            c_hov = cell_rect.collidepoint(mouse_pos) and not dig_session.is_won and not dig_session.is_lost

            if not is_dug:
                # Нераскопанная песчаная плита
                base_col = (225, 175, 105) if c_hov else (185, 142, 85)
                border_col = (255, 230, 130) if c_hov else (120, 90, 50)
                pygame.draw.rect(surface, base_col, cell_rect, border_radius=6)
                pygame.draw.rect(surface, border_col, cell_rect, width=2, border_radius=6)
                # Песчаные насечки/декор
                pygame.draw.circle(surface, (140, 105, 60), (cx + 14, cy + 14), 2)
                pygame.draw.circle(surface, (140, 105, 60), (cx + 34, cy + 34), 2)
                if c_hov:
                    # Подсветка готовности копать
                    pygame.draw.line(surface, (255, 255, 220), (cx + 24, cy + 16), (cx + 24, cy + 32), 2)
                    pygame.draw.line(surface, (255, 255, 220), (cx + 16, cy + 24), (cx + 32, cy + 24), 2)
            elif is_hit:
                # Попадание во фрагмент реликвии: отображаем текстуру лежащей в земле реликвии
                # 1. Раскопанная земляная траншея
                pygame.draw.rect(surface, (36, 26, 18), cell_rect, border_radius=6)
                pygame.draw.rect(surface, (68, 50, 34), cell_rect, width=1, border_radius=6)
                # Тень по краям раскопа
                pygame.draw.rect(surface, (20, 14, 10), (cx + 2, cy + 2, 44, 4), border_radius=2)
                pygame.draw.rect(surface, (20, 14, 10), (cx + 2, cy + 2, 4, 44), border_radius=2)

                # 2. Вырезаем соответствующий фрагмент арта реликвии
                r_art = get_relic_art_surface(dig_session.relic_id)
                dx = gx - getattr(dig_session, "origin_x", 0)
                dy = gy - getattr(dig_session, "origin_y", 0)
                sub_x = dx * 52
                sub_y = dy * 52
                if 0 <= sub_x < r_art.get_width() and 0 <= sub_y < r_art.get_height():
                    sub_w = min(48, r_art.get_width() - sub_x)
                    sub_h = min(48, r_art.get_height() - sub_y)
                    slice_surf = r_art.subsurface((sub_x, sub_y, sub_w, sub_h))
                    surface.blit(slice_surf, (cx, cy))

                # 3. Бесшовные перемычки для соседних откопанных блоков реликвии
                if (gx + 1, gy) in dig_session.relic_cells and dig_session.dug[gy][gx + 1]:
                    pygame.draw.rect(surface, (36, 26, 18), (cx + 46, cy + 4, 8, 40))
                    if sub_x + 48 + 4 <= r_art.get_width():
                        bridge_r = r_art.subsurface((sub_x + 48, sub_y, 4, sub_h))
                        surface.blit(bridge_r, (cx + 48, cy))
                if (gx, gy + 1) in dig_session.relic_cells and dig_session.dug[gy + 1][gx]:
                    pygame.draw.rect(surface, (36, 26, 18), (cx + 4, cy + 46, 40, 8))
                    if sub_y + 48 + 4 <= r_art.get_height():
                        bridge_d = r_art.subsurface((sub_x, sub_y + 48, sub_w, 4))
                        surface.blit(bridge_d, (cx, cy + 48))

                # 4. Песчаная россыпь по краям
                pygame.draw.circle(surface, (135, 100, 55), (cx + 6, cy + 6), 2)
                pygame.draw.circle(surface, (135, 100, 55), (cx + 42, cy + 42), 2)

                # 5. Эффект свечения при победе (реликвия полностью раскопана)
                if dig_session.is_won:
                    glow_s = pygame.Surface((48, 48), pygame.SRCALPHA)
                    pygame.draw.rect(glow_s, (255, 220, 80, 50), (0, 0, 48, 48), border_radius=6)
                    surface.blit(glow_s, (cx, cy))
                    pygame.draw.rect(surface, (255, 235, 140), cell_rect, width=2, border_radius=6)
            else:
                # Пустая выкопанная яма
                pygame.draw.rect(surface, (45, 35, 28), cell_rect, border_radius=6)
                pygame.draw.rect(surface, (30, 22, 18), cell_rect, width=1, border_radius=6)
                pygame.draw.circle(surface, (70, 58, 48), (cx + 18, cy + 24), 3)
                pygame.draw.circle(surface, (60, 50, 42), (cx + 30, cy + 28), 2)

    # Статусный блок внизу
    status_rect = pygame.Rect(12, 358, w - 24, 42)
    pygame.draw.rect(surface, (30, 24, 20), status_rect, border_radius=6)
    pygame.draw.rect(surface, (80, 60, 40), status_rect, width=1, border_radius=6)

    st_txt = small_font.render(dig_session.status_text, True, dig_session.status_color)
    surface.blit(st_txt, (status_rect.centerx - st_txt.get_width() // 2, status_rect.centery - st_txt.get_height() // 2))

    # Нижняя кнопка управления
    close_btn = pygame.Rect(95, 410, 170, 38)
    b_hov = close_btn.collidepoint(mouse_pos)

    if dig_session.is_won:
        b_bg = (50, 150, 75) if b_hov else (35, 115, 55)
        b_brd = (140, 255, 170) if b_hov else (80, 205, 110)
        btn_label = "ЗАБРАТЬ РЕЛИКВИЮ"
    elif dig_session.is_lost:
        b_bg = (140, 50, 50) if b_hov else (100, 35, 35)
        b_brd = (255, 130, 130) if b_hov else (190, 60, 60)
        btn_label = "ЗАКРЫТЬ РАСКОП"
    else:
        b_bg = (55, 45, 38) if b_hov else (38, 30, 25)
        b_brd = (160, 130, 85) if b_hov else (95, 75, 50)
        btn_label = "ОТСТУПИТЬ [X]"

    pygame.draw.rect(surface, b_bg, close_btn, border_radius=8)
    pygame.draw.rect(surface, b_brd, close_btn, width=2, border_radius=8)
    lbl_s = font.render(btn_label, True, WHITE)
    surface.blit(lbl_s, (close_btn.centerx - lbl_s.get_width() // 2, close_btn.centery - lbl_s.get_height() // 2))

    return close_btn


# -------------------------------------------------------------------------
# ПЬЕДЕСТАЛ И СТЕНДЫ ДРЕВНИХ РЕЛИКВИЙ
# -------------------------------------------------------------------------
def draw_pedestal_stand(surface, cx, cy, w=68, h=34, is_active=False, is_unlocked=True, is_hovered=False):
    """
    Отрисовывает полноценный графический 3D-пьедестал:
    - Нижнее ступенчатое основание (цоколь) с контактной тенью и фаской
    - Рельефная колонна (ствол пьедестала) с вертикальными бороздками и центральным руническим кристаллом
    - Верхний карниз (капитель) с полированной площадкой для размещения реликвии
    Возвращает y-координату центра верхней площадки, на которой лежит реликвия.
    """
    # 1. Тень под основанием
    sh_w = w + 12
    pygame.draw.ellipse(surface, (0, 0, 0, 110), (cx - sh_w // 2, cy + h // 2 - 4, sh_w, 9))

    # 2. Нижний ступенчатый цоколь (Base Plinth)
    b1_w = w
    b1_h = 7
    b1_y = cy + h // 2 - b1_h
    col_base = (46, 52, 64) if is_unlocked else (24, 28, 36)
    col_edge = (255, 215, 80) if is_active else ((100, 125, 160) if is_unlocked else (45, 52, 65))
    if is_hovered and is_unlocked:
        col_edge = (255, 235, 120) if is_active else (135, 185, 245)

    pygame.draw.rect(surface, col_base, (cx - b1_w // 2, b1_y, b1_w, b1_h), border_radius=3)
    pygame.draw.rect(surface, col_edge, (cx - b1_w // 2, b1_y, b1_w, b1_h), width=1, border_radius=3)
    pygame.draw.line(surface, (min(255, col_edge[0] + 30), min(255, col_edge[1] + 30), min(255, col_edge[2] + 30)),
                     (cx - b1_w // 2 + 2, b1_y + 1), (cx + b1_w // 2 - 2, b1_y + 1), 1)

    # 3. Ствол колонны / тело постамента (Fluted Shaft)
    col_w = int(w * 0.72)
    col_h = int(h * 0.44)
    col_y = b1_y - col_h + 2
    col_shaft = (38, 44, 56) if is_unlocked else (18, 22, 28)
    pygame.draw.rect(surface, col_shaft, (cx - col_w // 2, col_y, col_w, col_h))
    pygame.draw.rect(surface, col_edge, (cx - col_w // 2, col_y, col_w, col_h), width=1)

    # Вертикальные желобки колонны
    step_g = max(5, col_w // 5)
    for gx in range(cx - col_w // 2 + step_g, cx + col_w // 2, step_g):
        pygame.draw.line(surface, (14, 18, 24), (gx, col_y + 1), (gx, col_y + col_h - 1), 1)
        pygame.draw.line(surface, (70, 85, 110) if is_unlocked else (32, 38, 48), (gx + 1, col_y + 1), (gx + 1, col_y + col_h - 1), 1)

    # Центральный рунический кристалл
    if is_active:
        pygame.draw.polygon(surface, (255, 215, 80), [(cx, col_y + 3), (cx + 4, col_y + col_h // 2), (cx, col_y + col_h - 3), (cx - 4, col_y + col_h // 2)])
    elif is_unlocked:
        pygame.draw.polygon(surface, (75, 110, 155), [(cx, col_y + 4), (cx + 3, col_y + col_h // 2), (cx, col_y + col_h - 4), (cx - 3, col_y + col_h // 2)])

    # 4. Верхняя капитель и полированная площадка (Capital & Platform)
    t_w = int(w * 0.88)
    t_h = 8
    t_y = col_y - t_h + 2
    top_col = (54, 62, 78) if is_unlocked else (28, 34, 44)
    pygame.draw.rect(surface, top_col, (cx - t_w // 2, t_y, t_w, t_h), border_radius=2)
    pygame.draw.rect(surface, col_edge, (cx - t_w // 2, t_y, t_w, t_h), width=1, border_radius=2)

    # 5. Верхняя платформа-подушка
    plat_w = t_w - 6
    plat_rect = (cx - plat_w // 2, t_y - 2, plat_w, 5)
    inlay_col = (30, 52, 40) if is_active else ((24, 30, 40) if is_unlocked else (16, 20, 26))
    pygame.draw.ellipse(surface, inlay_col, plat_rect)
    pygame.draw.ellipse(surface, col_edge, plat_rect, width=1)

    return t_y


# -------------------------------------------------------------------------
# ЭКРАН: МУЗЕЙ ДРЕВНИХ РЕЛИКВИЙ (20 РЕЛИКВИЙ)
# -------------------------------------------------------------------------
def draw_relics_screen(surface, savedata, mouse_pos, bg_time=None):
    """Отображает полный зал музея: 20 стендов для реликвий и активные пьедесталы (2-5 слотов)."""
    if bg_time is None:
        bg_time = pygame.time.get_ticks()
    generate_background(surface, bg_time, custom_cols=((16, 18, 24), (26, 28, 38)))

    # 1. Верхняя шапка
    head_panel = pygame.Rect(20, 8, SCREEN_WIDTH - 40, 48)
    pygame.draw.rect(surface, (22, 28, 38), head_panel, border_radius=10)
    pygame.draw.rect(surface, (180, 140, 55), head_panel, width=2, border_radius=10)

    surface.blit(relic_icon, (head_panel.left + 14, head_panel.centery - 12))
    title = font.render("МУЗЕЙ ДРЕВНИХ РЕЛИКВИЙ", True, (255, 230, 140))
    surface.blit(title, (head_panel.left + 44, head_panel.top + 6))

    relics_dict = savedata.get("Relics", {})
    unlocked_count = sum(1 for r_id in RELICS_DATA if relics_dict.get(r_id, {}).get("level", 0) > 0)
    tot_excavated = savedata.get("Stats", {}).get("relics_excavated", 0)
    max_cap = get_relic_max_level(savedata)
    max_pedestals = get_max_relic_pedestals(savedata)
    equipped = get_equipped_relics(savedata)
    dark_res_lvl = savedata.get("Upgrades", {}).get("dark_relic_resonance", 0)
    extra_res = f"  |  Тёмный Резонанс: +{dark_res_lvl * 5}% пассивно" if dark_res_lvl > 0 else ""

    sub_txt = tiny_font.render(
        f"Найдено: {unlocked_count}/20  |  Экипировано: {len(equipped)}/{max_pedestals}  |  Всего раскопано: {tot_excavated}  |  Предел: {max_cap} ур.{extra_res}",
        True, (170, 205, 235)
    )
    surface.blit(sub_txt, (head_panel.left + 46, head_panel.top + 28))

    # Кнопка Справка по Реликвиям
    info_btn = pygame.Rect(head_panel.right - 258, head_panel.centery - 17, 120, 34)
    inf_hov = info_btn.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (28, 62, 85) if inf_hov else (18, 38, 55), info_btn, border_radius=8)
    pygame.draw.rect(surface, (90, 200, 255) if inf_hov else (45, 120, 165), info_btn, width=2, border_radius=8)
    inf_txt = small_font.render("? ИНФО", True, (210, 245, 255))
    surface.blit(inf_txt, (info_btn.centerx - inf_txt.get_width() // 2, info_btn.centery - inf_txt.get_height() // 2))

    back_btn = pygame.Rect(head_panel.right - 130, head_panel.centery - 17, 120, 34)
    b_hov = back_btn.collidepoint(mouse_pos)
    pygame.draw.rect(surface, (45, 68, 98) if b_hov else (28, 42, 62), back_btn, border_radius=8)
    pygame.draw.rect(surface, (110, 175, 245) if b_hov else (52, 92, 138), back_btn, width=2, border_radius=8)
    b_txt = small_font.render("НАЗАД [ESC]", True, WHITE)
    surface.blit(b_txt, (back_btn.centerx - b_txt.get_width() // 2, back_btn.centery - b_txt.get_height() // 2))

    # 2. Полка активных пьедесталов (эффекты действуют только с пьедесталов!)
    ped_bar = pygame.Rect(20, 54, SCREEN_WIDTH - 40, 78)
    pygame.draw.rect(surface, (18, 22, 32), ped_bar, border_radius=8)
    pygame.draw.rect(surface, (100, 85, 50), ped_bar, width=1, border_radius=8)

    pedestal_click_rects = []
    slot_w = 236
    slot_h = 68
    gap_p = 10
    total_slots_w = 5 * slot_w + 4 * gap_p
    p_start_x = (SCREEN_WIDTH - total_slots_w) // 2
    p_start_y = 59

    for s_i in range(5):
        s_rect = pygame.Rect(p_start_x + s_i * (slot_w + gap_p), p_start_y, slot_w, slot_h)
        s_hov = s_rect.collidepoint(mouse_pos)
        is_unlocked = (s_i < max_pedestals)
        is_active = is_unlocked and (s_i < len(equipped))
        ped_cx = s_rect.left + 38
        ped_cy = s_rect.centery + 12

        if is_active:
            eq_rid = equipped[s_i]
            rdata = RELICS_DATA.get(eq_rid, {})
            pedestal_click_rects.append((s_i, s_rect, eq_rid))
            # Активный пьедестал со свечением
            p_bg = (32, 44, 30) if s_hov else (20, 28, 20)
            p_brd = (255, 215, 80) if s_hov else (65, 190, 110)
            pygame.draw.rect(surface, p_bg, s_rect, border_radius=6)
            pygame.draw.rect(surface, p_brd, s_rect, width=2, border_radius=6)

            # Настоящий 3D-пьедестал с установленной на него реликвией
            ped_y = draw_pedestal_stand(surface, ped_cx, ped_cy, w=56, h=28, is_active=True, is_unlocked=True, is_hovered=s_hov)
            icon_p = get_relic_icon_preview(eq_rid, 30)
            pygame.draw.ellipse(surface, (0, 0, 0, 140), (ped_cx - 12, ped_y - 2, 24, 6))
            surface.blit(icon_p, (ped_cx - icon_p.get_width() // 2, ped_y - icon_p.get_height() + 2))

            name_s = small_font.render(rdata.get("name", "Реликвия"), True, GOLD if s_hov else WHITE)
            surface.blit(name_s, (s_rect.left + 72, s_rect.top + 7))

            cur_eq_lvl = relics_dict.get(eq_rid, {}).get("level", 1)
            bonus_s = tiny_font.render(f"Бонус: {get_relic_bonus_summary(eq_rid, cur_eq_lvl)}", True, (130, 255, 170))
            surface.blit(bonus_s, (s_rect.left + 72, s_rect.top + 28))

            status_p = tiny_font.render("КЛИК: СНЯТЬ" if s_hov else "[АКТИВЕН В БОЮ]", True, (255, 140, 140) if s_hov else (100, 220, 140))
            surface.blit(status_p, (s_rect.left + 72, s_rect.top + 48))
        elif is_unlocked:
            pedestal_click_rects.append((s_i, s_rect, None))
            # Свободный пьедестал, ожидающий реликвию
            p_bg = (24, 34, 48) if s_hov else (16, 22, 32)
            p_brd = (100, 160, 240) if s_hov else (45, 65, 95)
            pygame.draw.rect(surface, p_bg, s_rect, border_radius=6)
            pygame.draw.rect(surface, p_brd, s_rect, width=1, border_radius=6)

            ped_y = draw_pedestal_stand(surface, ped_cx, ped_cy, w=56, h=28, is_active=False, is_unlocked=True, is_hovered=s_hov)
            plus_s = small_font.render("+", True, (130, 215, 255) if s_hov else (75, 140, 190))
            surface.blit(plus_s, (ped_cx - plus_s.get_width() // 2, ped_y - plus_s.get_height() + 1))

            txt1 = small_font.render(f"ПЬЕДЕСТАЛ #{s_i + 1}", True, (160, 205, 255) if s_hov else (115, 150, 190))
            txt2 = tiny_font.render("Свободен (клик по реликвии)", True, (130, 160, 195))
            surface.blit(txt1, (s_rect.left + 72, s_rect.top + 16))
            surface.blit(txt2, (s_rect.left + 72, s_rect.top + 38))
        else:
            pedestal_click_rects.append((s_i, s_rect, None))
            # Заблокированный пьедестал
            pygame.draw.rect(surface, (14, 16, 22), s_rect, border_radius=6)
            pygame.draw.rect(surface, (38, 44, 56), s_rect, width=1, border_radius=6)

            ped_y = draw_pedestal_stand(surface, ped_cx, ped_cy, w=56, h=28, is_active=False, is_unlocked=False, is_hovered=False)
            s_lock = get_crisp_lock_icon(16)
            surface.blit(s_lock, (ped_cx - s_lock.get_width() // 2, ped_y - 13))

            txt1 = small_font.render(f"СЛОТ #{s_i + 1} [ЗАКРЫТ]", True, (90, 100, 115))
            txt2 = tiny_font.render("Талант «Пьедесталы»", True, (75, 85, 98))
            surface.blit(txt1, (s_rect.left + 72, s_rect.top + 16))
            surface.blit(txt2, (s_rect.left + 72, s_rect.top + 38))

    # 3. Сетка: 20 стендов (5 колонок x 4 строки)
    col_w = 236
    row_h = 138
    gap_x = 10
    gap_y = 6
    start_x = (SCREEN_WIDTH - (5 * col_w + 4 * gap_x)) // 2
    start_y = 138

    relic_click_rects = {}
    relic_keys = list(RELICS_DATA.keys())
    t_now = pygame.time.get_ticks()

    for idx, rid in enumerate(relic_keys[:20]):
        col = idx % 5
        row = idx // 5
        sx = start_x + col * (col_w + gap_x)
        sy = start_y + row * (row_h + gap_y)
        stand_rect = pygame.Rect(sx, sy, col_w, row_h)
        s_hov = stand_rect.collidepoint(mouse_pos)
        relic_click_rects[rid] = stand_rect

        rdata = RELICS_DATA[rid]
        rentry = relics_dict.get(rid, {"level": 0, "finds": 0})
        cur_lvl = rentry.get("level", 0)
        finds = rentry.get("finds", 0)
        req = get_relic_upgrade_requirements(cur_lvl + 1) if cur_lvl < max_cap else 0
        is_unlocked = cur_lvl > 0
        is_maxed = is_unlocked and (cur_lvl >= max_cap)
        is_equipped = (rid in equipped)

        if is_equipped:
            bg_col = (30, 42, 30) if s_hov else (20, 30, 20)
            border_col = (255, 220, 90) if s_hov else (70, 220, 130)
            border_w = 2
        elif is_maxed:
            bg_col = (34, 28, 18) if s_hov else (24, 20, 14)
            border_col = (255, 215, 80) if s_hov else (190, 150, 50)
            border_w = 2
        elif is_unlocked:
            bg_col = (26, 36, 50) if s_hov else (18, 24, 34)
            border_col = (90, 140, 195) if s_hov else (50, 75, 105)
            border_w = 2 if s_hov else 1
        else:
            bg_col = (20, 24, 32) if s_hov else (14, 16, 22)
            border_col = (55, 68, 85) if s_hov else (32, 38, 48)
            border_w = 1

        pygame.draw.rect(surface, bg_col, stand_rect, border_radius=8)
        pygame.draw.rect(surface, border_col, stand_rect, width=border_w, border_radius=8)

        mid = rdata["map"]
        map_lbl = tiny_font.render(f"Карта {mid + 1}", True, (160, 205, 245) if is_unlocked else (95, 110, 125))
        surface.blit(map_lbl, (sx + 8, sy + 4))

        if is_equipped:
            lvl_lbl = tiny_font.render("[В БОЮ]", True, (120, 255, 160))
        elif is_maxed:
            if dark_res_lvl > 0:
                lvl_lbl = tiny_font.render(f"МАКС ({dark_res_lvl * 5}%)", True, (215, 165, 255))
            else:
                lvl_lbl = tiny_font.render("МАКС", True, (255, 220, 90))
        elif is_unlocked:
            if dark_res_lvl > 0:
                lvl_lbl = tiny_font.render(f"Ур. {cur_lvl}/{max_cap} ({dark_res_lvl * 5}%)", True, (200, 160, 255))
            else:
                lvl_lbl = tiny_font.render(f"Ур. {cur_lvl}/{max_cap}", True, (110, 245, 150))
        else:
            lvl_lbl = tiny_font.render("СКРЫТО", True, (110, 120, 130))
        surface.blit(lvl_lbl, (sx + col_w - lvl_lbl.get_width() - 8, sy + 4))

        cx = sx + col_w // 2
        cy = sy + 35

        # Реликвия в карточке: чисто как реликвия (без пьедестала и лишнего мусора)
        # При наведении курсора мягко, плавно покачивается без резких рывков
        phase = t_now * 0.0035 + idx * 0.7
        amp = 2.2 if s_hov else 1.0
        bob = math.sin(phase) * amp
        relic_draw_y = int(cy + bob)

        if s_hov:
            # Мягкое сияние вокруг парящей реликвии
            glow_surf = pygame.Surface((64, 48), pygame.SRCALPHA)
            glow_col = (255, 220, 100, 45) if is_equipped else ((100, 210, 255, 45) if is_unlocked else (100, 120, 140, 20))
            pygame.draw.ellipse(glow_surf, glow_col, (0, 0, 64, 48))
            surface.blit(glow_surf, (cx - 32, relic_draw_y - 24))

            # Динамическая мягкая тень под парящей реликвией
            sh_w = max(16, int(24 - bob * 1.2))
            pygame.draw.ellipse(surface, (0, 0, 0, max(40, min(100, int(75 - bob * 5)))), (cx - sh_w // 2, cy + 16, sh_w, 5))
        else:
            # Спокойная тень под реликвией
            pygame.draw.ellipse(surface, (0, 0, 0, 75), (cx - 12, cy + 16, 24, 5))

        if is_unlocked:
            c_icon = get_relic_icon_preview(rid, 34)
            surface.blit(c_icon, (cx - c_icon.get_width() // 2, relic_draw_y - c_icon.get_height() // 2))
        else:
            q_surf = large_font.render("?", True, (95, 110, 125))
            surface.blit(q_surf, (cx - q_surf.get_width() // 2, relic_draw_y - q_surf.get_height() // 2))

        # Разделитель
        sep_col = (55, 70, 90) if is_unlocked else (30, 36, 45)
        pygame.draw.line(surface, sep_col, (sx + 8, sy + 59), (sx + col_w - 8, sy + 59), 1)

        # Название реликвии
        if is_unlocked:
            name_col = (255, 225, 120) if is_maxed else (235, 215, 140)
            name_txt = small_font.render(rdata["name"], True, name_col)
        else:
            name_txt = small_font.render("??? [Тайна]", True, (95, 105, 118))
        surface.blit(name_txt, (cx - name_txt.get_width() // 2, sy + 62))

        # Прогресс / Статус
        if is_maxed:
            prog_txt = tiny_font.render("Эффект максимален", True, (130, 255, 150))
        elif is_unlocked:
            prog_txt = tiny_font.render(f"Находок: {finds}/{req}", True, (170, 205, 235))
        else:
            map_name = MAP_NAMES_LIST[mid] if mid < len(MAP_NAMES_LIST) else f"Карта {mid + 1}"
            prog_txt = tiny_font.render(f"Раскопки: {map_name}", True, (100, 115, 130))
        surface.blit(prog_txt, (cx - prog_txt.get_width() // 2, sy + 77))

        # Описание баффа / Актуальный бонус
        if is_unlocked:
            if is_equipped:
                b_txt = f"Бонус: {get_relic_bonus_summary(rid, cur_lvl)}"
                b_col = (255, 230, 120)
            elif dark_res_lvl > 0:
                b_txt = f"Пассивно ({dark_res_lvl * 5}%): {get_relic_bonus_summary(rid, cur_lvl)}"
                b_col = (215, 175, 255)
            else:
                b_txt = f"Бонус: {get_relic_bonus_summary(rid, cur_lvl)}"
                b_col = (130, 255, 160) if is_maxed else (140, 235, 180)
            b_surf = tiny_font.render(b_txt, True, b_col)
            surface.blit(b_surf, (cx - b_surf.get_width() // 2, sy + 93))

            desc_lines = _render_wrapped_lines(rdata["desc"], tiny_font, col_w - 14)
            d_surf = tiny_font.render(desc_lines[0], True, (190, 215, 240))
            surface.blit(d_surf, (cx - d_surf.get_width() // 2, sy + 107))
        else:
            h1 = tiny_font.render("Свойство откроется", True, (75, 88, 102))
            h2 = tiny_font.render("после раскопок", True, (75, 88, 102))
            surface.blit(h1, (cx - h1.get_width() // 2, sy + 93))
            surface.blit(h2, (cx - h2.get_width() // 2, sy + 107))

        # Подсказка клика при наведении
        if s_hov and is_unlocked:
            act_txt = "Снять" if is_equipped else ("Экипировать" if len(equipped) < max_pedestals else "Мест нет")
            act_col = (255, 160, 160) if is_equipped else ((140, 255, 180) if len(equipped) < max_pedestals else (255, 200, 100))
            a_surf = tiny_font.render(f"[{act_txt}]", True, act_col)
            surface.blit(a_surf, (cx - a_surf.get_width() // 2, sy + 122))

    return back_btn, relic_click_rects, pedestal_click_rects, info_btn


# -------------------------------------------------------------------------
# СИМУЛЯЦИЯ И ЭКРАН ГЛАВНОГО МЕНЮ (MAIN MENU SIMULATION)
# -------------------------------------------------------------------------
class MenuDemoSimulation:
    def __init__(self):
        self.reset_map()

    def reset_map(self):
        # 50% шанс на одну из существующих карт 0-8 и 50% шанс на карту со случайной процедурной генерацией
        if random.random() < 0.5:
            self.map_id = random.randint(0, min(8, len(path_list) - 1))
            self.path = path_list[self.map_id]
            self.slots = tower_slots_list[self.map_id]
        else:
            seed = random.randint(1, 999999)
            self.path, self.slots = generate_custom_map_path_and_slots(seed)
            self.map_id = random.randint(0, min(8, len(path_list) - 1))  # Выбираем случайный биом для генератора

        self.biome = MAP_BIOMES_DATA.get(self.map_id, MAP_BIOMES_DATA[0])
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.effects = []
        self.slime_splats = []
        try:
            self.ambient_particles = AmbientParticleSystem(self.biome.get("ambient", "dust"), self.map_id)
        except Exception:
            self.ambient_particles = None
        try:
            self.map_decor = MapDecorManager(self.map_id, self.path, self.slots)
        except Exception:
            self.map_decor = None
        self.spawn_timer = 0.5
        self.base_hp = float('inf')

        # Размещаем 4-6 настоящих башен Tower из entities.py на случайных слотах
        num_towers = min(len(self.slots), random.randint(4, 6))
        chosen_slots = random.sample(self.slots, num_towers)
        tower_types = ["magic", "rock", "freeze", "tesla", "tent"]
        random.shuffle(tower_types)
        for idx, (sx, sy) in enumerate(chosen_slots):
            ttype = tower_types[idx % len(tower_types)]
            t_lvl = random.randint(1, 6)
            try:
                tw = Tower(sx, sy, ttype, starting_level=t_lvl, game_map=self.map_id)
                self.towers.append(tw)
            except Exception:
                pass

    def update(self, dt):
        dt = min(dt, 0.1)

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = random.uniform(1.2, 2.2)
            slime_pool = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 50, 51]
            slime_type = random.choice(slime_pool)
            demo_wave = random.randint(3, 16)
            try:
                en = Enemy(slime_type, demo_wave, self.path, game_map=self.map_id)
                self.enemies.append(en)
            except Exception:
                pass

        # 1. Обновление башен (реальная логика из entities.py: стрельба, солдаты, молнии)
        for t in self.towers:
            try:
                t.update(dt, self.enemies, self.projectiles, self.path, self.effects)
            except Exception:
                pass

        # 2. Обновление снарядов (настоящие MagicBullet, RockBullet, FrostBullet)
        for p in self.projectiles[:]:
            try:
                p.update(dt, self.enemies, self.effects)
                if not getattr(p, "active", True):
                    self.projectiles.remove(p)
            except Exception:
                if p in self.projectiles:
                    self.projectiles.remove(p)

        # 3. Обновление врагов (мобы получают урон и умирают; в конце пути просто уходят)
        for e in self.enemies[:]:
            try:
                reached = e.update(dt, self.towers, self.enemies, self.effects)
                if reached:
                    # Враг дошел до конца пути: просто исчезает/уходит
                    self.enemies.remove(e)
                elif not e.active or e.health <= 0:
                    self.enemies.remove(e)
                    if get_graphics_preset() != "optimized":
                        splat_col = e.get_splat_color() if hasattr(e, "get_splat_color") else (100, 220, 80)
                        self.slime_splats.append(SlimeSplat(e.x, e.y, splat_col))
                        for _ in range(5):
                            self.effects.append(JellyDroplet(e.x, e.y, splat_col))
                    for _ in range(6):
                        self.effects.append(DropSpark(e.x, e.y, burst=True))
            except Exception:
                if e in self.enemies:
                    self.enemies.remove(e)

        # 4. Обновление эффектов (плавающий урон, кольца, молнии, искры)
        for eff in self.effects[:]:
            try:
                if eff.update(dt):
                    self.effects.remove(eff)
            except Exception:
                if eff in self.effects:
                    self.effects.remove(eff)

        # Обновление желейных пятен на земле
        for splat in self.slime_splats[:]:
            try:
                if splat.update(dt):
                    self.slime_splats.remove(splat)
            except Exception:
                pass
        if len(self.slime_splats) > 25:
            self.slime_splats = self.slime_splats[-25:]

        # 5. Атмосферные частицы биома
        if self.ambient_particles:
            try:
                self.ambient_particles.update(dt)
            except Exception:
                pass

    def draw(self, surf, bg_time):
        generate_background(surf, bg_time, map_id=self.map_id)

        # Атмосферный декор биома на земле
        if getattr(self, "map_decor", None):
            try:
                self.map_decor.draw(surf, bg_time)
            except Exception:
                pass

        # Дорожка биома (двойная окантовка и цвет грунта)
        r_border = self.biome.get("road_border", (85, 70, 50))
        r_col = self.biome.get("road_col", (125, 110, 85))
        if self.path:
            for p_i in range(len(self.path) - 1):
                pygame.draw.line(surf, r_border, self.path[p_i], self.path[p_i + 1], 40)
                pygame.draw.circle(surf, r_border, self.path[p_i + 1], 20)
            for p_i in range(len(self.path) - 1):
                pygame.draw.line(surf, r_col, self.path[p_i], self.path[p_i + 1], 32)
                pygame.draw.circle(surf, r_col, self.path[p_i + 1], 16)

        # Желейные пятна слаймов на земле и дороге
        for splat in getattr(self, "slime_splats", []):
            try:
                splat.draw(surf)
            except Exception:
                pass

        # Свободные слоты под башни
        occupied_coords = {(int(t.x), int(t.y)) for t in self.towers}
        for slot in self.slots:
            if (int(slot[0]), int(slot[1])) not in occupied_coords:
                surf.blit(slot_img, (slot[0] - 22, slot[1] - 22))

        # Атмосферные частицы биома
        if self.ambient_particles:
            try:
                self.ambient_particles.draw(surf)
            except Exception:
                pass

        # Враги (отсортированы по Y для правильной перспективы спрайтов)
        for e in sorted(self.enemies, key=lambda m: getattr(m, 'y', 0)):
            try:
                e.draw(surf)
            except Exception:
                pass

        # Башни (с каменными постаментами, анимациями, воинами и аурами уровней)
        for t in self.towers:
            try:
                t.draw(surf)
            except Exception:
                pass

        # Настоящие игровые снаряды
        for p in self.projectiles:
            try:
                p.draw(surf)
            except Exception:
                pass

        # Визуальные эффекты (числа урона, вспышки, молнии, искры)
        for eff in self.effects:
            try:
                eff.draw(surf)
            except Exception:
                pass


def draw_main_menu_screen(surface, mouse_pos, demo_sim, bg_time=None):
    """
    Отрисовывает открытое, кинематографичное главное меню игры:
    - На фоне: живая симуляция demo_sim со случайной картой, ходящими слаймами и башнями
    - Мягкие верхний и нижний виньетирующие градиенты, не закрывающие центр битвы
    - По центру: парящий сияющий логотип и стильные полупрозрачные стеклянные кнопки
    - Внизу: плашка версии 0.1.0 и автора sonofstrange
    """
    if bg_time is None:
        bg_time = pygame.time.get_ticks()

    # 1. Живая симуляция на фоне
    demo_sim.draw(surface, bg_time)

    # 2. Мягкая кинематографичная виньетка сверху и снизу (центр экрана открыт и прозрачен!)
    vignette_top = pygame.Surface((SCREEN_WIDTH, 170), pygame.SRCALPHA)
    for y in range(170):
        alpha = int(160 * ((170 - y) / 170.0) ** 1.4)
        pygame.draw.line(vignette_top, (8, 12, 18, alpha), (0, y), (SCREEN_WIDTH, y))
    surface.blit(vignette_top, (0, 0))

    vignette_bot = pygame.Surface((SCREEN_WIDTH, 180), pygame.SRCALPHA)
    for y in range(180):
        alpha = int(170 * (y / 180.0) ** 1.4)
        pygame.draw.line(vignette_bot, (8, 12, 18, alpha), (0, y), (SCREEN_WIDTH, SCREEN_HEIGHT - 180 + y))
    surface.blit(vignette_bot, (0, SCREEN_HEIGHT - 180))

    cx = SCREEN_WIDTH // 2

    # 3. Верхний заголовок (Парящий логотип с четким HD-кактусом)
    title_y = 22
    c_sz = 112
    c_icon = cactus_img_xl if 'cactus_img_xl' in globals() else pygame.transform.smoothscale(cactus_img, (c_sz, c_sz))
    
    # Мягкое парение кактуса без фонового круга
    float_y = math.sin(bg_time * 0.0025) * 5.0
    c_y = title_y - 4 + float_y
    surface.blit(c_icon, (cx - c_sz // 2, int(c_y)))

    t_shadow = massive_font.render("CACTUS TD", True, (0, 0, 0))
    surface.blit(t_shadow, (cx - t_shadow.get_width() // 2 + 2, title_y + 110))
    t_main = massive_font.render("CACTUS TD", True, GOLD)
    surface.blit(t_main, (cx - t_main.get_width() // 2, title_y + 108))

    # Стеклянная плашка подзаголовка с надписью Remastered
    sub_str = "REMASTERED"
    st_surf = font.render(sub_str, True, (140, 245, 205))
    pw = st_surf.get_width() + 40
    ph = 30
    sub_pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(sub_pill, (14, 24, 34, 190), (0, 0, pw, ph), border_radius=15)
    pygame.draw.rect(sub_pill, (55, 175, 130, 220), (0, 0, pw, ph), width=1, border_radius=15)
    surface.blit(sub_pill, (cx - pw // 2, title_y + 168))
    surface.blit(st_surf, (cx - st_surf.get_width() // 2, title_y + 171))

    # 4. Парящие стильные кнопки со стеклянным размытием и неоновым свечением при наведении
    btn_w = 340
    btn_x = cx - btn_w // 2

    # Кнопка: В БОЙ
    play_btn = pygame.Rect(btn_x, 340, btn_w, 64)
    p_hov = play_btn.collidepoint(mouse_pos)
    p_surf = pygame.Surface((btn_w, 64), pygame.SRCALPHA)
    p_bg = (28, 92, 48, 230) if p_hov else (18, 56, 32, 190)
    p_brd = (120, 255, 170, 255) if p_hov else (60, 180, 100, 220)
    pygame.draw.rect(p_surf, p_bg, (0, 0, btn_w, 64), border_radius=16)
    pygame.draw.rect(p_surf, p_brd, (0, 0, btn_w, 64), width=2, border_radius=16)
    surface.blit(p_surf, play_btn)

    p_txt = large_font.render("В БОЙ", True, WHITE)
    surface.blit(p_txt, (play_btn.centerx - p_txt.get_width() // 2, play_btn.centery - p_txt.get_height() // 2))

    # Кнопка: НАСТРОЙКИ
    set_btn = pygame.Rect(btn_x, 424, btn_w, 56)
    s_hov = set_btn.collidepoint(mouse_pos)
    s_surf = pygame.Surface((btn_w, 56), pygame.SRCALPHA)
    s_bg = (30, 62, 98, 230) if s_hov else (20, 38, 62, 190)
    s_brd = (110, 205, 255, 255) if s_hov else (55, 100, 155, 220)
    pygame.draw.rect(s_surf, s_bg, (0, 0, btn_w, 56), border_radius=14)
    pygame.draw.rect(s_surf, s_brd, (0, 0, btn_w, 56), width=2, border_radius=14)
    surface.blit(s_surf, set_btn)

    s_txt = font.render("НАСТРОЙКИ", True, WHITE)
    surface.blit(s_txt, (set_btn.centerx - s_txt.get_width() // 2, set_btn.centery - s_txt.get_height() // 2))

    # Кнопка: ВЫХОД
    exit_btn = pygame.Rect(btn_x, 500, btn_w, 52)
    e_hov = exit_btn.collidepoint(mouse_pos)
    e_surf = pygame.Surface((btn_w, 52), pygame.SRCALPHA)
    e_bg = (95, 30, 36, 230) if e_hov else (58, 20, 24, 190)
    e_brd = (255, 110, 120, 255) if e_hov else (145, 45, 52, 220)
    pygame.draw.rect(e_surf, e_bg, (0, 0, btn_w, 52), border_radius=14)
    pygame.draw.rect(e_surf, e_brd, (0, 0, btn_w, 52), width=2, border_radius=14)
    surface.blit(e_surf, exit_btn)

    e_txt = font.render("ВЫХОД", True, WHITE)
    surface.blit(e_txt, (exit_btn.centerx - e_txt.get_width() // 2, exit_btn.centery - e_txt.get_height() // 2))

    # 5. Нижняя панель информации (Версия 0.1.2 • Автор: sonofstrange)
    foot_str = "Версия 0.1.2 • Автор: sonofstrange"
    foot_txt = tiny_font.render(foot_str, True, (180, 210, 240))
    fp_w = foot_txt.get_width() + 36
    fp_h = 28
    foot_pill = pygame.Surface((fp_w, fp_h), pygame.SRCALPHA)
    pygame.draw.rect(foot_pill, (10, 14, 22, 180), (0, 0, fp_w, fp_h), border_radius=14)
    pygame.draw.rect(foot_pill, (50, 75, 110, 180), (0, 0, fp_w, fp_h), width=1, border_radius=14)
    foot_y = SCREEN_HEIGHT - 38
    surface.blit(foot_pill, (cx - fp_w // 2, foot_y))
    surface.blit(foot_txt, (cx - foot_txt.get_width() // 2, foot_y + (fp_h - foot_txt.get_height()) // 2))

    return play_btn, set_btn, exit_btn






