# -*- coding: utf-8 -*-
"""
generate_tower_redesigns.py
Скрипт для процедурной отрисовки пиксельных спрайтов башен
в точно таком же фирменном стиле Pygame-графики Cactus TD.
"""
import os
import math
import pygame

pygame.init()
pygame.font.init()

OUT_DIR = "assets/textures/redesign_previews"
os.makedirs(OUT_DIR, exist_ok=True)
ARTIFACT_DIR = r"C:\Users\Mechrevo\.gemini\antigravity\brain\4366c795-d4d4-4ad8-bf46-ce83ac98f773"

def save(surf, name):
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(surf, path)
    return path

# -------------------------------------------------------------------------
# ОБЩИЙ ПОСТАМЕНТ (для контекста)
# -------------------------------------------------------------------------
def draw_base_pedestal(s, ox=32, oy=54):
    pygame.draw.ellipse(s, (15, 20, 15, 120), (ox - 24, oy - 8, 48, 16))
    pygame.draw.ellipse(s, (42, 50, 42), (ox - 22, oy - 7, 44, 14))
    pygame.draw.ellipse(s, (65, 85, 68), (ox - 22, oy - 7, 44, 14), width=2)
    pygame.draw.ellipse(s, (90, 130, 95), (ox - 14, oy - 5, 28, 9), width=1)

# =========================================================================
# 1. МАГИЧЕСКАЯ БАШНЯ
# =========================================================================

# Вариант 1: «Астральный кактус-шпиль»
def draw_magic_v1():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    draw_base_pedestal(s)

    # Обсидиановое руническое кольцо-основание
    pygame.draw.polygon(s, (32, 22, 45), [(16, 56), (48, 56), (42, 46), (22, 46)])
    pygame.draw.polygon(s, (52, 36, 75), [(18, 54), (46, 54), (41, 47), (23, 47)])
    # Фиолетовые рунические глифы
    for rx in [26, 32, 38]:
        pygame.draw.circle(s, (180, 110, 255), (rx, 51), 1)

    # Стебель мистического звёздного кактуса
    # Теневая сторона
    pygame.draw.polygon(s, (38, 28, 62), [(24, 46), (40, 46), (37, 24), (27, 24)])
    # Освещённая сторона (изумрудно-пурпурная мякоть)
    pygame.draw.polygon(s, (68, 45, 105), [(26, 45), (38, 45), (36, 25), (28, 25)])
    pygame.draw.polygon(s, (105, 65, 155), [(28, 44), (34, 44), (33, 26), (30, 26)])

    # Кактусовые колючки-звёздочки (светятся)
    spines = [(24, 38), (40, 36), (23, 30), (41, 28), (25, 22), (39, 22)]
    for sx, sy in spines:
        pygame.draw.line(s, (220, 140, 255), (sx, sy), (sx + (-2 if sx < 32 else 2), sy - 1), 2)
        pygame.draw.circle(s, (255, 220, 255), (sx, sy), 1)

    # Золотая зубчатая корона-подставка для кристалла
    pygame.draw.polygon(s, (140, 95, 30), [(24, 25), (40, 25), (42, 21), (22, 21)])
    pygame.draw.polygon(s, (225, 175, 55), [(25, 24), (39, 24), (41, 22), (23, 22)])
    # Зубцы короны
    for zx in [24, 32, 40]:
        pygame.draw.polygon(s, (255, 215, 80), [(zx - 2, 22), (zx, 18), (zx + 2, 22)])

    # Парящие орбитальные кольца магии
    pygame.draw.ellipse(s, (190, 80, 255, 180), (18, 9, 28, 10), width=1)
    pygame.draw.ellipse(s, (255, 140, 255, 120), (20, 10, 24, 8), width=1)

    # Большой октаэдрический астральный кристалл (ромб с гранями)
    # Задняя тень
    pygame.draw.polygon(s, (110, 30, 150), [(32, 2), (40, 13), (32, 23), (24, 13)])
    # Левая грань (средний тон)
    pygame.draw.polygon(s, (185, 60, 230), [(32, 2), (32, 23), (24, 13)])
    # Правая грань (яркая)
    pygame.draw.polygon(s, (230, 100, 255), [(32, 2), (40, 13), (32, 23)])
    # Центральный фасетный блик
    pygame.draw.polygon(s, (255, 210, 255), [(32, 5), (35, 13), (32, 20), (29, 13)])
    # Точечные искры
    pygame.draw.circle(s, (255, 255, 255), (32, 13), 2)
    pygame.draw.circle(s, (220, 160, 255), (19, 7), 1)
    pygame.draw.circle(s, (220, 160, 255), (45, 11), 1)
    return s

# Вариант 2: «Рунический Обелиск Архимага»
def draw_magic_v2():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    draw_base_pedestal(s)

    # Обсидиановый ступенчатый цоколь
    pygame.draw.polygon(s, (24, 20, 36), [(14, 56), (50, 56), (46, 48), (18, 48)])
    pygame.draw.polygon(s, (42, 34, 60), [(17, 54), (47, 54), (44, 49), (20, 49)])

    # Основная башня (тёмный эльфийский монолит)
    pygame.draw.polygon(s, (30, 25, 46), [(21, 48), (43, 48), (39, 18), (25, 18)])
    pygame.draw.polygon(s, (52, 42, 78), [(23, 47), (41, 47), (37, 20), (27, 20)])

    # Светящиеся неоново-фиолетовые руны на теле башни
    pygame.draw.line(s, (190, 90, 255), (32, 44), (32, 24), 2)
    pygame.draw.line(s, (230, 150, 255), (32, 38), (36, 34), 2)
    pygame.draw.line(s, (230, 150, 255), (32, 32), (28, 28), 2)

    # 3 парящих каменных осколка вокруг шпиля
    for ox, oy in [(18, 22), (46, 24), (32, 6)]:
        pygame.draw.polygon(s, (38, 30, 58), [(ox, oy - 3), (ox + 3, oy), (ox, oy + 3), (ox - 3, oy)])
        pygame.draw.polygon(s, (160, 80, 240), [(ox, oy - 2), (ox + 2, oy), (ox, oy + 2), (ox - 2, oy)], width=1)

    # Сфера чистой эфирной магии в чаше наверху
    pygame.draw.polygon(s, (70, 55, 95), [(24, 20), (40, 20), (44, 15), (20, 15)])
    pygame.draw.circle(s, (150, 50, 220), (32, 13), 8)
    pygame.draw.circle(s, (215, 100, 255), (32, 13), 6)
    pygame.draw.circle(s, (255, 200, 255), (32, 13), 3)
    pygame.draw.circle(s, (255, 255, 255), (31, 11), 1)
    return s

# =========================================================================
# 2. ОГНЕННАЯ БАШНЯ (ROCK / MAGMA)
# =========================================================================

# Вариант 1: «Вулканическое Горнило»
def draw_rock_v1():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    draw_base_pedestal(s)

    # Базальтовое основание с выступающими плитами
    pygame.draw.polygon(s, (36, 24, 20), [(10, 56), (54, 56), (48, 44), (16, 44)])
    pygame.draw.polygon(s, (58, 38, 32), [(13, 54), (51, 54), (46, 45), (18, 45)])
    # Лавовые трещины в камне
    pygame.draw.lines(s, (255, 90, 10), False, [(16, 52), (24, 48), (34, 52), (48, 47)], 2)
    pygame.draw.lines(s, (255, 200, 40), False, [(22, 49), (26, 49), (36, 51)], 1)

    # Средний ярус (грубая каменная кладка)
    pygame.draw.rect(s, (45, 30, 24), (17, 28, 30, 18))
    pygame.draw.rect(s, (70, 48, 38), (19, 29, 26, 15))
    # Вертикальные трещины
    pygame.draw.line(s, (255, 100, 20), (26, 44), (27, 30), 2)
    pygame.draw.line(s, (255, 100, 20), (38, 43), (36, 32), 2)
    pygame.draw.line(s, (255, 220, 50), (26, 40), (27, 34), 1)

    # Вулканические шипы по бокам
    pygame.draw.polygon(s, (55, 35, 28), [(17, 36), (10, 32), (17, 30)])
    pygame.draw.polygon(s, (55, 35, 28), [(47, 36), (54, 32), (47, 30)])

    # Верхнее кольцо-жерло (тигель с лавой)
    pygame.draw.ellipse(s, (35, 22, 18), (14, 18, 36, 14))
    pygame.draw.ellipse(s, (65, 42, 34), (14, 18, 36, 14), width=3)
    # Зубцы жерла
    for bx in [15, 23, 31, 39, 45]:
        pygame.draw.rect(s, (80, 52, 40), (bx, 15, 5, 6))

    # Кипящее лавовое озеро внутри жерла
    pygame.draw.ellipse(s, (220, 50, 10), (17, 20, 30, 9))
    pygame.draw.ellipse(s, (255, 140, 20), (20, 21, 24, 7))
    pygame.draw.ellipse(s, (255, 230, 70), (24, 22, 16, 5))
    pygame.draw.circle(s, (255, 255, 200), (29, 23), 2) # лопающийся пузырь

    # Язык пламени / искры над жерлом
    flame_pts = [(32, 4), (37, 13), (33, 11), (35, 17), (29, 17), (31, 12), (27, 14)]
    pygame.draw.polygon(s, (255, 110, 20), flame_pts)
    pygame.draw.polygon(s, (255, 215, 50), [(32, 7), (35, 14), (33, 13), (30, 15), (31, 11)])
    pygame.draw.circle(s, (255, 230, 90), (32, 12), 2)
    # Мелкие искры
    pygame.draw.circle(s, (255, 180, 40), (26, 8), 1)
    pygame.draw.circle(s, (255, 180, 40), (38, 6), 1)
    return s

# Вариант 2: «Магматическая Мортира»
def draw_rock_v2():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    draw_base_pedestal(s)

    # Чугунная платформа с заклепками
    pygame.draw.polygon(s, (32, 30, 36), [(12, 56), (52, 56), (46, 46), (18, 46)])
    pygame.draw.polygon(s, (54, 52, 62), [(15, 54), (49, 54), (44, 48), (20, 48)])
    for kx in [18, 27, 36, 45]:
        pygame.draw.circle(s, (90, 88, 105), (kx, 52), 1)

    # Механическая опора поворотного механизма
    pygame.draw.rect(s, (42, 38, 46), (22, 36, 20, 12))
    pygame.draw.circle(s, (75, 70, 85), (32, 42), 6)
    pygame.draw.circle(s, (140, 135, 155), (32, 42), 3)

    # Наклонный толстый ствол осадной мортиры
    # Тело ствола
    barrel_pts = [(20, 38), (44, 38), (40, 14), (24, 14)]
    pygame.draw.polygon(s, (48, 38, 42), barrel_pts)
    pygame.draw.polygon(s, (76, 58, 62), [(22, 36), (42, 36), (38, 16), (26, 16)])

    # Раскаленные медные кольца-усилители
    pygame.draw.rect(s, (180, 70, 20), (22, 30, 20, 4))
    pygame.draw.rect(s, (240, 130, 30), (23, 31, 18, 2))
    pygame.draw.rect(s, (180, 70, 20), (24, 20, 16, 4))
    pygame.draw.rect(s, (240, 130, 30), (25, 21, 14, 2))

    # Раскаленное жерло орудия (овал)
    pygame.draw.ellipse(s, (30, 15, 15), (22, 10, 20, 10))
    pygame.draw.ellipse(s, (220, 50, 10), (24, 12, 16, 7))
    pygame.draw.ellipse(s, (255, 180, 40), (26, 13, 12, 4))
    pygame.draw.circle(s, (255, 255, 200), (32, 14), 2)

    # Дым и тлеющие угольки
    pygame.draw.circle(s, (80, 70, 70, 160), (34, 7), 3)
    pygame.draw.circle(s, (110, 95, 95, 140), (37, 4), 2)
    pygame.draw.circle(s, (255, 140, 30), (30, 6), 1)
    return s

# =========================================================================
# 3. ЛЕДЯНАЯ БАШНЯ (FREEZE)
# =========================================================================

# Вариант 1: «Крио-Кактус / Ледяной Лотос»
def draw_freeze_v1():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    draw_base_pedestal(s)

    # Заснеженный скальный цоколь с ледяной коркой
    pygame.draw.polygon(s, (25, 45, 75), [(14, 56), (50, 56), (44, 46), (20, 46)])
    pygame.draw.polygon(s, (55, 95, 150), [(17, 54), (47, 54), (42, 48), (22, 48)])
    pygame.draw.polygon(s, (200, 235, 255), [(18, 48), (46, 48), (42, 46), (22, 46)]) # шапка снега

    # Тело кристаллического кактуса (полупрозрачный лазурит)
    pygame.draw.polygon(s, (35, 90, 160), [(24, 46), (40, 46), (37, 22), (27, 22)])
    pygame.draw.polygon(s, (70, 160, 235), [(26, 44), (38, 44), (35, 23), (29, 23)])
    pygame.draw.polygon(s, (140, 220, 255), [(28, 43), (33, 43), (32, 24), (30, 24)])

    # Острые ледяные иглы-сосульки по бокам кактуса
    icicles = [(24, 38, -5, -2), (40, 36, 5, -2), (25, 28, -6, -3), (39, 26, 6, -3)]
    for ix, iy, dx, dy in icicles:
        pygame.draw.polygon(s, (180, 240, 255), [(ix, iy), (ix + dx, iy + dy), (ix, iy + 2)])
        pygame.draw.polygon(s, (255, 255, 255), [(ix, iy), (ix + dx, iy + dy), (ix, iy + 1)], width=1)

    # Ледяные граненые лепестки / кристаллы вокруг бутона
    pygame.draw.polygon(s, (80, 175, 240), [(20, 24), (28, 20), (26, 12)])
    pygame.draw.polygon(s, (150, 225, 255), [(22, 22), (28, 19), (26, 14)])
    pygame.draw.polygon(s, (80, 175, 240), [(44, 24), (36, 20), (38, 12)])
    pygame.draw.polygon(s, (150, 225, 255), [(42, 22), (36, 19), (38, 14)])

    # Главный сверкающий сапфировый пик (бутон холода)
    peak_pts = [(32, 3), (38, 14), (32, 22), (26, 14)]
    pygame.draw.polygon(s, (50, 130, 210), peak_pts)
    # Грани со светотенью
    pygame.draw.polygon(s, (130, 215, 255), [(32, 3), (26, 14), (32, 22)])
    pygame.draw.polygon(s, (210, 245, 255), [(32, 3), (38, 14), (32, 22)])
    pygame.draw.polygon(s, (255, 255, 255), [(32, 5), (34, 13), (32, 19), (30, 13)])

    # Парящие морозные кристаллы-снежинки
    pygame.draw.circle(s, (220, 245, 255), (18, 14), 1)
    pygame.draw.circle(s, (220, 245, 255), (46, 16), 1)
    pygame.draw.circle(s, (255, 255, 255), (32, 13), 2)
    return s

# Вариант 2: «Глициерный Монолит»
def draw_freeze_v2():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    draw_base_pedestal(s)

    # Многогранный ледяной фундамент
    pygame.draw.polygon(s, (30, 65, 110), [(12, 56), (52, 56), (46, 46), (18, 46)])
    pygame.draw.polygon(s, (65, 130, 200), [(15, 54), (49, 54), (44, 48), (20, 48)])

    # Центральный монолитный шпиль со ступенями
    pygame.draw.polygon(s, (40, 95, 165), [(21, 46), (43, 46), (37, 14), (27, 14)])
    # Левая теневая грань
    pygame.draw.polygon(s, (70, 150, 225), [(21, 46), (32, 46), (32, 14), (27, 14)])
    # Правая освещенная грань
    pygame.draw.polygon(s, (150, 225, 255), [(32, 46), (43, 46), (37, 14), (32, 14)])
    # Сверхяркое ледяное ребро по центру
    pygame.draw.line(s, (255, 255, 255), (32, 46), (32, 14), 2)

    # Острый пик обелиска
    pygame.draw.polygon(s, (180, 235, 255), [(27, 14), (37, 14), (32, 4)])
    pygame.draw.polygon(s, (255, 255, 255), [(30, 14), (35, 14), (32, 6)])

    # Вмороженные кристаллы по бокам
    pygame.draw.polygon(s, (90, 180, 245), [(14, 40), (21, 44), (19, 28)])
    pygame.draw.polygon(s, (200, 245, 255), [(16, 38), (20, 42), (19, 30)])
    pygame.draw.polygon(s, (90, 180, 245), [(50, 40), (43, 44), (45, 28)])
    pygame.draw.polygon(s, (200, 245, 255), [(48, 38), (44, 42), (45, 30)])
    return s

# =========================================================================
# 4. ТЕСЛА БАШНЯ (TESLA)
# =========================================================================

# Вариант 1: «Двурогий Арк-Разрядник»
def draw_tesla_v1():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    draw_base_pedestal(s)

    # Стальная опора с заклепками
    pygame.draw.polygon(s, (32, 38, 48), [(14, 56), (50, 56), (44, 46), (20, 46)])
    pygame.draw.polygon(s, (55, 65, 80), [(17, 54), (47, 54), (42, 48), (22, 48)])
    for kx in [20, 32, 44]:
        pygame.draw.circle(s, (100, 115, 135), (kx, 52), 1)

    # Керамические изоляторы
    for iy in [44, 40, 36]:
        pygame.draw.ellipse(s, (110, 70, 40), (22, iy, 20, 5))
        pygame.draw.ellipse(s, (170, 115, 60), (23, iy, 18, 3))

    # Центральная ось башни
    pygame.draw.rect(s, (50, 60, 75), (28, 20, 8, 18))
    pygame.draw.rect(s, (80, 95, 115), (30, 20, 4, 18))

    # Медные тороидальные катушки Теслы
    for cy in [32, 26]:
        pygame.draw.ellipse(s, (160, 80, 25), (18, cy, 28, 7))
        pygame.draw.ellipse(s, (235, 145, 50), (20, cy, 24, 4))
        pygame.draw.ellipse(s, (255, 210, 130), (24, cy, 16, 2))

    # Двурогие электроды (дуга Иакова)
    pygame.draw.polygon(s, (170, 90, 30), [(26, 21), (23, 8), (20, 7), (23, 21)]) # левый рог
    pygame.draw.polygon(s, (235, 150, 55), [(25, 20), (23, 9), (21, 8), (23, 20)])
    pygame.draw.polygon(s, (170, 90, 30), [(38, 21), (41, 8), (44, 7), (41, 21)]) # правый рог
    pygame.draw.polygon(s, (235, 150, 55), [(39, 20), (41, 9), (43, 8), (41, 20)])

    # Шаровые наконечники рогов
    pygame.draw.circle(s, (235, 155, 50), (21, 7), 3)
    pygame.draw.circle(s, (255, 220, 120), (21, 7), 1)
    pygame.draw.circle(s, (235, 155, 50), (43, 7), 3)
    pygame.draw.circle(s, (255, 220, 120), (43, 7), 1)

    # Сияющая плазменная сфера и электрическая дуга между рогами
    pygame.draw.circle(s, (40, 180, 255), (32, 12), 7)
    pygame.draw.circle(s, (140, 230, 255), (32, 12), 5)
    pygame.draw.circle(s, (255, 255, 255), (32, 12), 2)
    # Зигзаг молнии между рогами
    pygame.draw.lines(s, (220, 250, 255), False, [(23, 8), (28, 11), (36, 9), (41, 8)], 2)
    pygame.draw.lines(s, (255, 255, 255), False, [(23, 8), (28, 11), (36, 9), (41, 8)], 1)
    return s

# Вариант 2: «Шпиль Бури / Генератор Молний»
def draw_tesla_v2():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    draw_base_pedestal(s)

    # Металлическая пирамидальная ферма
    pygame.draw.polygon(s, (30, 40, 52), [(14, 56), (50, 56), (42, 38), (22, 38)])
    pygame.draw.polygon(s, (52, 66, 85), [(17, 54), (47, 54), (40, 40), (24, 40)])
    # Распорки фермы
    pygame.draw.line(s, (80, 100, 125), (20, 52), (40, 42), 1)
    pygame.draw.line(s, (80, 100, 125), (44, 52), (24, 42), 1)

    # 3 медных трансформаторных диска (снизу вверх с уменьшением)
    disks = [(36, 26, 6), (28, 22, 5), (20, 16, 4)]
    for dy, dw, dh in disks:
        pygame.draw.ellipse(s, (150, 75, 25), (32 - dw // 2, dy, dw, dh))
        pygame.draw.ellipse(s, (225, 140, 50), (32 - dw // 2, dy, dw, dh - 1))
        pygame.draw.ellipse(s, (255, 210, 120), (32 - dw // 4, dy, dw // 2, dh - 2))

    # Центральный электродный штырь
    pygame.draw.line(s, (120, 140, 165), (32, 20), (32, 4), 3)
    pygame.draw.line(s, (220, 240, 255), (32, 20), (32, 4), 1)

    # Верхняя плазменная сфера Теслы
    pygame.draw.circle(s, (30, 160, 255), (32, 6), 6)
    pygame.draw.circle(s, (120, 220, 255), (32, 6), 4)
    pygame.draw.circle(s, (255, 255, 255), (32, 6), 2)

    # 4 микро-разряда вокруг сферы
    for ang in [0.3, 1.8, 3.5, 4.9]:
        ex = int(32 + math.cos(ang) * 9)
        ey = int(6 + math.sin(ang) * 9)
        pygame.draw.line(s, (180, 240, 255), (32, 6), (ex, ey), 1)
        pygame.draw.circle(s, (255, 255, 255), (ex, ey), 1)
    return s


# =========================================================================
# ГЕНЕРАЦИЯ ОБЩЕЙ СРАВНИТЕЛЬНОЙ ВИТРИНЫ (SHOWCASE)
# =========================================================================
def build_showcase():
    # Загружаем текущие оригинальные спрайты
    old_magic = pygame.image.load("assets/textures/magic_tower.png")
    old_rock = pygame.image.load("assets/textures/rock_tower.png")
    old_freeze = pygame.image.load("assets/textures/freeze_tower.png")
    old_tesla = pygame.image.load("assets/textures/tesla_tower.png")

    # Генерируем новые спрайты
    m_v1 = draw_magic_v1()
    m_v2 = draw_magic_v2()
    save(m_v1, "magic_tower_v1.png")
    save(m_v2, "magic_tower_v2.png")

    r_v1 = draw_rock_v1()
    r_v2 = draw_rock_v2()
    save(r_v1, "rock_tower_v1.png")
    save(r_v2, "rock_tower_v2.png")

    f_v1 = draw_freeze_v1()
    f_v2 = draw_freeze_v2()
    save(f_v1, "freeze_tower_v1.png")
    save(f_v2, "freeze_tower_v2.png")

    t_v1 = draw_tesla_v1()
    t_v2 = draw_tesla_v2()
    save(t_v1, "tesla_tower_v1.png")
    save(t_v2, "tesla_tower_v2.png")

    # Создаём красивую витрину высокого разрешения
    W, H = 1160, 840
    sheet = pygame.Surface((W, H))
    sheet.fill((14, 18, 26)) # Глубокий тёмно-синий фон игры

    # Тонкая космическая сетка
    for x in range(0, W, 40):
        pygame.draw.line(sheet, (22, 28, 40), (x, 0), (x, H), 1)
    for y in range(0, H, 40):
        pygame.draw.line(sheet, (22, 28, 40), (0, y), (W, y), 1)

    title_font = pygame.font.SysFont("arial", 26, bold=True)
    header_font = pygame.font.SysFont("arial", 17, bold=True)
    row_title_font = pygame.font.SysFont("arial", 19, bold=True)
    sub_font = pygame.font.SysFont("arial", 14)
    desc_font = pygame.font.SysFont("arial", 12)

    # Главный заголовок
    t_main = title_font.render("ВАРИАНТЫ РЕДИЗАЙНА БАШЕН ДЛЯ CACTUS TD", True, (255, 215, 80))
    t_sub = sub_font.render("Сравнение оригинального пиксельного вида и новых концепций (масштаб x2)", True, (170, 190, 220))
    sheet.blit(t_main, ((W - t_main.get_width()) // 2, 16))
    sheet.blit(t_sub, ((W - t_sub.get_width()) // 2, 48))

    # Колонки
    cols = [
        ("ТЕКУЩАЯ (Оригинал)", 325),
        ("ВАРИАНТ 1 (Рекомендуемый)", 625),
        ("ВАРИАНТ 2 (Альтернативный)", 925),
    ]
    for cname, cx in cols:
        badge = header_font.render(cname, True, (240, 245, 255))
        sheet.blit(badge, (cx - badge.get_width() // 2, 80))

    rows_data = [
        ("МАГИЧЕСКАЯ", "БАШНЯ", [
            (old_magic, "Старый фиолетовый обелиск"),
            (m_v1, "Астральный кактус + парящий кристалл"),
            (m_v2, "Рунический обелиск + осколки")
        ], (205, 120, 255)),
        ("ОГНЕННАЯ", "БАШНЯ", [
            (old_rock, "Старый серый бастион"),
            (r_v1, "Вулканическое горнило с лавой"),
            (r_v2, "Чугунная осадная мортира")
        ], (255, 135, 40)),
        ("ЛЕДЯНАЯ", "БАШНЯ", [
            (old_freeze, "Старый плоский треугольник"),
            (f_v1, "Крио-кактус с иглами и сапфиром"),
            (f_v2, "Глициерный монолит с рунами")
        ], (95, 220, 255)),
        ("ТЕСЛА", "БАШНЯ", [
            (old_tesla, "Старая простая катушка"),
            (t_v1, "Двурогий арк-разрядник Иакова"),
            (t_v2, "Шпиль Бури с трансформатором")
        ], (255, 215, 60)),
    ]

    start_y = 118
    row_h = 168

    for r_i, (part1, part2, variants, theme_col) in enumerate(rows_data):
        ry = start_y + r_i * row_h

        # Плашка ряда
        row_rect = pygame.Rect(20, ry, W - 40, row_h - 14)
        pygame.draw.rect(sheet, (20, 25, 38), row_rect, border_radius=10)
        pygame.draw.rect(sheet, (38, 48, 70), row_rect, width=1, border_radius=10)

        # Боковая плашка с названием башни слева
        side_rect = pygame.Rect(28, ry + 8, 140, row_h - 30)
        pygame.draw.rect(sheet, (14, 18, 28), side_rect, border_radius=8)
        pygame.draw.rect(sheet, theme_col, side_rect, width=2, border_radius=8)

        rt1 = row_title_font.render(part1, True, theme_col)
        rt2 = row_title_font.render(part2, True, (240, 245, 255))
        sheet.blit(rt1, (side_rect.centerx - rt1.get_width() // 2, side_rect.centery - 18))
        sheet.blit(rt2, (side_rect.centerx - rt2.get_width() // 2, side_rect.centery + 6))

        for v_i, (v_surf, v_desc) in enumerate(variants):
            cx = cols[v_i][1]
            cy = ry + 20

            # Подложка под башню
            card_rect = pygame.Rect(cx - 120, cy, 240, 115)
            pygame.draw.rect(sheet, (14, 18, 28), card_rect, border_radius=8)
            b_col = theme_col if v_i > 0 else (60, 75, 100)
            pygame.draw.rect(sheet, b_col, card_rect, width=1 if v_i == 0 else 2, border_radius=8)

            # Отрисовываем башню в масштабе x2
            target_size = 96
            scaled_t = pygame.transform.scale(v_surf, (target_size, target_size))
            sheet.blit(scaled_t, (cx - target_size // 2, cy + 2))

            # Подпись варианта
            d_txt = desc_font.render(v_desc, True, (210, 225, 240) if v_i > 0 else (140, 155, 175))
            sheet.blit(d_txt, (cx - d_txt.get_width() // 2, cy + 96))

    # Сохраняем в папку проекта и в артефакты
    out_sheet_path = os.path.join(OUT_DIR, "tower_redesign_showcase.png")
    pygame.image.save(sheet, out_sheet_path)

    artifact_sheet_path = os.path.join(ARTIFACT_DIR, "tower_redesign_showcase.png")
    pygame.image.save(sheet, artifact_sheet_path)

    print("SUCCESS: Showcase generated at:", out_sheet_path)
    print("SUCCESS: Artifact saved at:", artifact_sheet_path)

if __name__ == "__main__":
    build_showcase()
