# -*- coding: utf-8 -*-
import pygame
import math

_relic_cache = {}
_relic_icon_cache = {}

def create_relic_surface(relic_id):
    """Создает полноценный арт реликвии строго под размер её сетки (w_cells*52-4, h_cells*52-4)."""
    if relic_id == 'ancient_urn':
        # 100 x 48 (2x1) - Древний кувшин/амфора
        s = pygame.Surface((100, 48), pygame.SRCALPHA)
        # Тень в углублении
        pygame.draw.ellipse(s, (20, 15, 10, 120), (12, 10, 80, 36))
        # Тело амфоры
        pygame.draw.ellipse(s, (190, 110, 55), (16, 6, 74, 36))
        pygame.draw.ellipse(s, (135, 70, 30), (16, 6, 74, 36), width=2)
        # Верхний блик керамики
        pygame.draw.ellipse(s, (225, 145, 85), (24, 9, 58, 14))
        # Горлышко слева
        pygame.draw.rect(s, (160, 90, 40), (8, 14, 18, 20), border_radius=3)
        pygame.draw.ellipse(s, (230, 190, 70), (4, 12, 9, 24))
        pygame.draw.ellipse(s, (130, 60, 25), (4, 12, 9, 24), width=2)
        # Золотые узорные ленты
        pygame.draw.arc(s, (245, 210, 80), (32, 7, 28, 34), 0.8, 5.4, 3)
        pygame.draw.arc(s, (245, 210, 80), (52, 9, 24, 30), 0.8, 5.4, 3)
        pygame.draw.circle(s, (80, 220, 255), (46, 24), 3)
        pygame.draw.circle(s, (80, 220, 255), (64, 24), 3)
        # Ручки кувшина
        pygame.draw.arc(s, (120, 60, 25), (18, 2, 22, 18), 0.4, 3.14, 3)
        pygame.draw.arc(s, (120, 60, 25), (18, 28, 22, 18), 3.14, 5.9, 3)
        return s

    elif relic_id == 'fossil_needle':
        # 48 x 152 (1x3) - Окаменелая игла / древний бивень
        s = pygame.Surface((48, 152), pygame.SRCALPHA)
        # Тень
        pygame.draw.polygon(s, (20, 15, 10, 100), [(24, 8), (38, 24), (32, 148), (16, 148), (10, 24)])
        # Навершие с янтарём
        pygame.draw.circle(s, (215, 175, 90), (24, 20), 15)
        pygame.draw.circle(s, (135, 100, 45), (24, 20), 15, width=2)
        pygame.draw.circle(s, (255, 170, 30), (24, 20), 9)
        pygame.draw.circle(s, (255, 235, 150), (22, 17), 3)
        # Клинообразный стержень иглы
        pts = [(18, 28), (30, 28), (28, 80), (26, 125), (24, 148), (22, 125), (20, 80)]
        pygame.draw.polygon(s, (230, 220, 195), pts)
        pygame.draw.polygon(s, (140, 130, 110), pts, width=2)
        # Центральная грань и бороздки
        pygame.draw.line(s, (255, 250, 235), (24, 28), (24, 144), 2)
        for yy in range(40, 120, 14):
            pygame.draw.line(s, (170, 155, 130), (20, yy), (28, yy), 2)
        return s

    elif relic_id == 'sand_hammer':
        # 100 x 100 (L-shape: (0,0), (1,0), (0,1)) - Песчаный молот
        s = pygame.Surface((100, 100), pygame.SRCALPHA)
        # Боёк молота в верхних клетках [(0,0), (1,0)]: от x=8 до x=92, y=8 до y=44
        pygame.draw.rect(s, (185, 145, 90), (8, 8, 84, 38), border_radius=6)
        pygame.draw.rect(s, (110, 80, 45), (8, 8, 84, 38), width=3, border_radius=6)
        pygame.draw.rect(s, (220, 185, 130), (14, 12, 72, 14), border_radius=3)
        # Золотые руны на молоте
        pygame.draw.polygon(s, (255, 220, 80), [(24, 27), (32, 18), (40, 27), (32, 36)])
        pygame.draw.polygon(s, (255, 220, 80), [(60, 27), (68, 18), (76, 27), (68, 36)])
        # Рукоять в [(0,1)]: x=18 до x=32, y=42 до y=92
        pygame.draw.rect(s, (120, 75, 35), (20, 44, 14, 48), border_radius=4)
        pygame.draw.rect(s, (70, 40, 15), (20, 44, 14, 48), width=2, border_radius=4)
        for yy in range(50, 85, 8):
            pygame.draw.line(s, (190, 140, 80), (21, yy), (33, yy + 4), 2)
        pygame.draw.circle(s, (230, 185, 60), (27, 92), 7)
        pygame.draw.circle(s, (120, 85, 20), (27, 92), 7, width=2)
        return s

    elif relic_id == 'pioneer_flask':
        # 48 x 48 (1x1) - Фляга первопроходца
        s = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(s, (175, 105, 55), (24, 26), 18)
        pygame.draw.circle(s, (105, 55, 25), (24, 26), 18, width=2)
        pygame.draw.circle(s, (215, 145, 85), (20, 22), 9)
        pygame.draw.rect(s, (200, 160, 60), (20, 5, 8, 6), border_radius=1)
        pygame.draw.rect(s, (160, 100, 40), (21, 2, 6, 4))
        pygame.draw.line(s, (80, 45, 20), (12, 16), (36, 36), 3)
        pygame.draw.line(s, (80, 45, 20), (12, 36), (36, 16), 3)
        pygame.draw.circle(s, (255, 215, 80), (24, 26), 4)
        return s

    elif relic_id == 'magma_clot':
        # 100 x 100 (2x2) - Магматический сгусток
        s = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(s, (35, 22, 26), (50, 50), 44)
        pygame.draw.circle(s, (180, 50, 25), (50, 50), 44, width=3)
        pygame.draw.circle(s, (225, 65, 20), (50, 50), 32)
        pygame.draw.circle(s, (255, 175, 35), (48, 46), 22)
        pygame.draw.circle(s, (255, 245, 160), (46, 44), 11)
        fissures = [
            [(50, 50), (30, 25), (14, 18)],
            [(50, 50), (70, 25), (86, 16)],
            [(50, 50), (25, 70), (16, 82)],
            [(50, 50), (72, 70), (84, 82)]
        ]
        for f in fissures:
            pygame.draw.lines(s, (255, 200, 50), False, f, 3)
            pygame.draw.lines(s, (255, 90, 30), False, f, 5)
        return s

    elif relic_id == 'miner_token':
        # 100 x 48 (2x1) - Шахтёрский жетон
        s = pygame.Surface((100, 48), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (195, 140, 50), (8, 6, 84, 36))
        pygame.draw.ellipse(s, (115, 75, 20), (8, 6, 84, 36), width=3)
        pygame.draw.ellipse(s, (235, 180, 75), (14, 10, 72, 28), width=2)
        pygame.draw.line(s, (70, 45, 20), (30, 34), (70, 14), 4)
        pygame.draw.line(s, (70, 45, 20), (30, 14), (70, 34), 4)
        pygame.draw.arc(s, (210, 220, 235), (58, 8, 22, 16), 0.2, 2.5, 4)
        pygame.draw.arc(s, (210, 220, 235), (58, 24, 22, 16), 3.6, 5.8, 4)
        pygame.draw.circle(s, (235, 40, 60), (50, 24), 6)
        pygame.draw.circle(s, (255, 180, 190), (48, 22), 2)
        return s

    elif relic_id == 'frost_rune':
        # 152 x 152 (cross) - Морозная руна
        s = pygame.Surface((152, 152), pygame.SRCALPHA)
        cx, cy = 76, 76
        pygame.draw.rect(s, (45, 95, 155), (58, 12, 36, 128), border_radius=8)
        pygame.draw.rect(s, (45, 95, 155), (12, 58, 128, 36), border_radius=8)
        pygame.draw.rect(s, (110, 185, 245), (58, 12, 36, 128), width=2, border_radius=8)
        pygame.draw.rect(s, (110, 185, 245), (12, 58, 128, 36), width=2, border_radius=8)
        pygame.draw.polygon(s, (170, 230, 255), [(cx, 40), (cx + 28, cy), (cx, 112), (cx - 28, cy)])
        pygame.draw.polygon(s, (240, 250, 255), [(cx, 52), (cx + 18, cy), (cx, 100), (cx - 18, cy)])
        for ang in [0, 45, 90, 135, 180, 225, 270, 315]:
            rad = math.radians(ang)
            ex = cx + int(math.cos(rad) * 46)
            ey = cy + int(math.sin(rad) * 46)
            pygame.draw.line(s, (220, 245, 255), (cx, cy), (ex, ey), 2)
            pygame.draw.circle(s, (120, 210, 255), (ex, ey), 3)
        return s

    elif relic_id == 'aquamarine_shard':
        # 100 x 100 (corner) - Аквамариновый осколок
        s = pygame.Surface((100, 100), pygame.SRCALPHA)
        poly1 = [(65, 10), (90, 30), (84, 85), (52, 92), (40, 50)]
        pygame.draw.polygon(s, (30, 135, 160), poly1)
        pygame.draw.polygon(s, (110, 225, 240), poly1, width=2)
        pygame.draw.line(s, (200, 250, 255), (65, 10), (60, 65), 2)
        pygame.draw.line(s, (200, 250, 255), (60, 65), (84, 85), 2)
        poly2 = [(12, 38), (42, 14), (55, 45), (32, 60)]
        pygame.draw.polygon(s, (25, 115, 140), poly2)
        pygame.draw.polygon(s, (90, 205, 220), poly2, width=2)
        pygame.draw.circle(s, (255, 255, 255), (65, 18), 3)
        pygame.draw.circle(s, (255, 255, 255), (28, 25), 2)
        return s

    elif relic_id == 'thunder_fang':
        # 152 x 48 (3x1) - Громовой зуб
        s = pygame.Surface((152, 48), pygame.SRCALPHA)
        pts = [(14, 18), (50, 12), (100, 16), (142, 28), (105, 34), (55, 36), (14, 30)]
        pygame.draw.polygon(s, (240, 235, 200), pts)
        pygame.draw.polygon(s, (135, 125, 90), pts, width=2)
        for xx in range(25, 125, 14):
            pygame.draw.line(s, (175, 165, 130), (xx, 14), (xx - 4, 34), 2)
        l_pts = [(18, 24), (38, 16), (62, 28), (88, 18), (115, 26), (140, 28)]
        pygame.draw.lines(s, (255, 240, 90), False, l_pts, 3)
        pygame.draw.lines(s, (255, 255, 255), False, l_pts, 1)
        return s

    elif relic_id == 'emerald_sprout':
        # 48 x 100 (1x2) - Изумрудный росток
        s = pygame.Surface((48, 100), pygame.SRCALPHA)
        pygame.draw.arc(s, (20, 125, 55), (14, 15, 22, 75), 1.2, 5.0, 5)
        leaf1 = [(24, 25), (42, 18), (36, 32)]
        leaf2 = [(22, 45), (4, 36), (12, 54)]
        leaf3 = [(24, 60), (42, 52), (34, 68)]
        for lf in [leaf1, leaf2, leaf3]:
            pygame.draw.polygon(s, (45, 185, 80), lf)
            pygame.draw.polygon(s, (15, 95, 40), lf, width=2)
        pygame.draw.circle(s, (90, 245, 140), (26, 18), 7)
        pygame.draw.circle(s, (230, 255, 240), (24, 15), 3)
        return s

    elif relic_id == 'optical_lens':
        # 152 x 100 (T-shape) - Оптический прицел
        s = pygame.Surface((152, 100), pygame.SRCALPHA)
        pygame.draw.rect(s, (190, 140, 50), (10, 14, 132, 26), border_radius=4)
        pygame.draw.rect(s, (120, 80, 25), (10, 14, 132, 26), width=2, border_radius=4)
        pygame.draw.rect(s, (240, 195, 90), (18, 18, 116, 8), border_radius=2)
        pygame.draw.circle(s, (215, 160, 60), (76, 50), 34)
        pygame.draw.circle(s, (130, 85, 25), (76, 50), 34, width=3)
        pygame.draw.circle(s, (60, 180, 240), (76, 50), 28)
        pygame.draw.circle(s, (140, 220, 255), (70, 44), 16)
        pygame.draw.circle(s, (255, 255, 255), (66, 40), 5)
        pygame.draw.line(s, (255, 80, 80), (76, 26), (76, 74), 2)
        pygame.draw.line(s, (255, 80, 80), (52, 50), (100, 50), 2)
        return s

    elif relic_id == 'shadow_compass':
        # 152 x 152 (diamond) - Теневой компас
        s = pygame.Surface((152, 152), pygame.SRCALPHA)
        cx, cy = 76, 76
        pygame.draw.circle(s, (35, 25, 50), (cx, cy), 58)
        pygame.draw.circle(s, (140, 75, 220), (cx, cy), 58, width=3)
        pygame.draw.circle(s, (22, 16, 32), (cx, cy), 46)
        pts_star = [(cx, 18), (cx + 12, cy - 12), (134, cy), (cx + 12, cy + 12), (cx, 134), (cx - 12, cy + 12), (18, cy), (cx - 12, cy - 12)]
        pygame.draw.polygon(s, (180, 120, 255), pts_star)
        pygame.draw.polygon(s, (240, 200, 255), pts_star, width=2)
        pygame.draw.polygon(s, (240, 70, 100), [(cx, cy), (cx - 8, cy - 8), (cx, cy - 42), (cx + 8, cy - 8)])
        pygame.draw.polygon(s, (80, 120, 220), [(cx, cy), (cx - 8, cy + 8), (cx, cy + 42), (cx + 8, cy + 8)])
        pygame.draw.circle(s, (255, 220, 100), (cx, cy), 6)
        return s

    elif relic_id == 'spiked_carapace':
        # 100 x 100 (2x2) - Шипастый панцирь
        s = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (95, 55, 45), (10, 12, 80, 76))
        pygame.draw.ellipse(s, (55, 30, 25), (10, 12, 80, 76), width=3)
        for yy in range(24, 80, 12):
            pygame.draw.arc(s, (145, 85, 70), (14, yy - 10, 72, 28), 0.2, 2.9, 3)
        spikes = [(8, 30), (6, 50), (10, 70), (92, 30), (94, 50), (90, 70)]
        for sx, sy in spikes:
            pygame.draw.circle(s, (215, 175, 120), (sx, sy), 5)
            pygame.draw.circle(s, (90, 50, 40), (sx, sy), 5, width=2)
        return s

    elif relic_id == 'vortex_bracelet':
        # 100 x 100 (corner) - Вихревой браслет
        s = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.arc(s, (235, 185, 60), (16, 16, 68, 68), 0.5, 4.8, 8)
        pygame.draw.arc(s, (140, 95, 20), (16, 16, 68, 68), 0.5, 4.8, 2)
        pygame.draw.circle(s, (60, 190, 255), (74, 30), 8)
        pygame.draw.circle(s, (255, 255, 255), (72, 28), 3)
        pygame.draw.circle(s, (60, 190, 255), (32, 76), 8)
        pygame.draw.circle(s, (255, 255, 255), (30, 74), 3)
        return s

    elif relic_id == 'inferno_seal':
        # 152 x 152 (cross) - Печать Инферно
        s = pygame.Surface((152, 152), pygame.SRCALPHA)
        cx, cy = 76, 76
        pygame.draw.rect(s, (40, 15, 15), (56, 10, 40, 132), border_radius=8)
        pygame.draw.rect(s, (40, 15, 15), (10, 56, 132, 40), border_radius=8)
        pygame.draw.rect(s, (220, 50, 30), (56, 10, 40, 132), width=3, border_radius=8)
        pygame.draw.rect(s, (220, 50, 30), (10, 56, 132, 40), width=3, border_radius=8)
        pygame.draw.circle(s, (255, 120, 20), (cx, cy), 26)
        pygame.draw.circle(s, (255, 240, 80), (cx, cy), 14)
        pygame.draw.ellipse(s, (50, 10, 10), (cx - 4, cy - 16, 8, 32))
        return s

    elif relic_id == 'hardened_anvil':
        # 152 x 100 (T-shape) - Закалённая наковальня
        s = pygame.Surface((152, 100), pygame.SRCALPHA)
        pts_top = [(14, 25), (45, 15), (135, 15), (142, 38), (115, 42), (40, 42)]
        pygame.draw.polygon(s, (140, 150, 165), pts_top)
        pygame.draw.polygon(s, (70, 75, 85), pts_top, width=3)
        pygame.draw.polygon(s, (210, 220, 235), [(46, 18), (133, 18), (128, 28), (44, 28)])
        pts_base = [(55, 42), (97, 42), (108, 88), (44, 88)]
        pygame.draw.polygon(s, (110, 120, 135), pts_base)
        pygame.draw.polygon(s, (55, 60, 70), pts_base, width=3)
        return s

    elif relic_id == 'void_eye':
        # 152 x 100 (T-shape) - Око Бездны
        s = pygame.Surface((152, 100), pygame.SRCALPHA)
        pygame.draw.arc(s, (160, 70, 240), (12, 12, 128, 70), 0.1, 3.0, 5)
        pygame.draw.arc(s, (160, 70, 240), (12, 12, 128, 70), 3.2, 6.1, 5)
        pygame.draw.circle(s, (25, 15, 38), (76, 48), 32)
        pygame.draw.circle(s, (200, 80, 255), (76, 48), 22)
        pygame.draw.circle(s, (255, 230, 255), (76, 48), 10)
        pygame.draw.ellipse(s, (10, 5, 20), (73, 34, 6, 28))
        return s

    elif relic_id == 'conqueror_crown':
        # 152 x 100 (crown) - Корона Завоевателя
        s = pygame.Surface((152, 100), pygame.SRCALPHA)
        pts = [(18, 82), (18, 20), (45, 52), (76, 12), (107, 52), (134, 20), (134, 82)]
        pygame.draw.polygon(s, (245, 195, 50), pts)
        pygame.draw.polygon(s, (160, 110, 20), pts, width=3)
        for px, py in [(18, 18), (76, 10), (134, 18)]:
            pygame.draw.circle(s, (235, 45, 65), (px, py), 6)
            pygame.draw.circle(s, (255, 200, 210), (px - 1, py - 1), 2)
        pygame.draw.rect(s, (190, 40, 50), (22, 68, 108, 14), border_radius=3)
        for xx in range(32, 125, 20):
            pygame.draw.circle(s, (60, 200, 255), (xx, 75), 4)
        return s

    elif relic_id == 'creator_mirror':
        # 100 x 100 (2x2) - Зеркало Создателя
        s = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.rect(s, (230, 180, 55), (10, 10, 80, 80), border_radius=12)
        pygame.draw.rect(s, (140, 95, 25), (10, 10, 80, 80), width=4, border_radius=12)
        pygame.draw.rect(s, (24, 28, 36), (18, 18, 64, 64), border_radius=8)
        pygame.draw.polygon(s, (80, 170, 240, 140), [(24, 24), (54, 24), (24, 54)])
        pygame.draw.polygon(s, (255, 255, 255, 180), [(58, 58), (74, 58), (58, 74)])
        pygame.draw.circle(s, (255, 215, 80), (50, 50), 8)
        return s

    elif relic_id == 'dimension_prism':
        # 152 x 100 (prism) - Призма измерений
        s = pygame.Surface((152, 100), pygame.SRCALPHA)
        poly_top = [(76, 12), (132, 68), (76, 85), (20, 68)]
        pygame.draw.polygon(s, (140, 100, 240), poly_top)
        pygame.draw.polygon(s, (210, 170, 255), poly_top, width=3)
        pygame.draw.polygon(s, (255, 110, 180, 160), [(76, 12), (76, 85), (20, 68)])
        pygame.draw.polygon(s, (60, 210, 255, 160), [(76, 12), (132, 68), (76, 85)])
        pygame.draw.circle(s, (255, 255, 255), (76, 48), 8)
        return s

    # Универсальный фоллбек
    s = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.circle(s, (240, 185, 45), (50, 50), 38)
    return s

def get_relic_art_surface(relic_id):
    if relic_id not in _relic_cache:
        _relic_cache[relic_id] = create_relic_surface(relic_id)
    return _relic_cache[relic_id]

def get_relic_icon_preview(relic_id, sz=32):
    key = (relic_id, sz)
    if key not in _relic_icon_cache:
        base = get_relic_art_surface(relic_id)
        bw, bh = base.get_size()
        scale = min(sz / bw, sz / bh)
        nw, nh = max(1, int(bw * scale)), max(1, int(bh * scale))
        scaled = pygame.transform.smoothscale(base, (nw, nh))
        res = pygame.Surface((sz, sz), pygame.SRCALPHA)
        res.blit(scaled, ((sz - nw) // 2, (sz - nh) // 2))
        _relic_icon_cache[key] = res
    return _relic_icon_cache[key]
