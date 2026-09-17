import pygame
import os

os.makedirs("assets/textures", exist_ok=True)
pygame.init()

def save_sprite(name, surf):
    path = os.path.join("assets/textures", name)
    pygame.image.save(surf, path)
    print(f"Saved {path} ({surf.get_size()})")

# 1. Слот для башни (красивый рунический каменный постамент 48x48)
slot = pygame.Surface((48, 48), pygame.SRCALPHA)
pygame.draw.circle(slot, (35, 45, 35, 160), (24, 24), 22)
pygame.draw.circle(slot, (90, 140, 95, 230), (24, 24), 22, width=3)
pygame.draw.circle(slot, (140, 210, 150, 180), (24, 24), 15, width=2)
pygame.draw.circle(slot, (180, 240, 190, 220), (24, 24), 5)
save_sprite("slot.png", slot)

# 2. Магическая башня (64x64)
# Стильный фиолетовый шпиль с парящим сияющим кристаллом
mag = pygame.Surface((64, 64), pygame.SRCALPHA)
# Каменное основание
pygame.draw.polygon(mag, (45, 35, 60), [(12, 60), (52, 60), (44, 46), (20, 46)])
pygame.draw.polygon(mag, (65, 50, 90), [(14, 58), (50, 58), (43, 48), (21, 48)])
# Колонны башни
pygame.draw.polygon(mag, (55, 40, 80), [(20, 46), (44, 46), (40, 26), (24, 26)])
pygame.draw.polygon(mag, (80, 60, 115), [(22, 44), (42, 44), (38, 28), (26, 28)])
# Арка и подставка под кристалл
pygame.draw.rect(mag, (120, 90, 170), (20, 23, 24, 5), border_radius=2)
pygame.draw.polygon(mag, (150, 110, 210), [(18, 23), (24, 15), (28, 23)])
pygame.draw.polygon(mag, (150, 110, 210), [(46, 23), (40, 15), (36, 23)])
# Парящий кристалл (ромб)
crystal_pts = [(32, 6), (40, 16), (32, 26), (24, 16)]
pygame.draw.polygon(mag, (240, 120, 255), crystal_pts)
pygame.draw.polygon(mag, (255, 210, 255), [(32, 9), (38, 16), (32, 23), (26, 16)])
pygame.draw.polygon(mag, (180, 60, 210), crystal_pts, width=2)
save_sprite("magic_tower.png", mag)

# 3. Огненная/Каменная башня (64x64)
# Магматический бастион с раскалённым жерлом
rock = pygame.Surface((64, 64), pygame.SRCALPHA)
# Массивное основание
pygame.draw.polygon(rock, (45, 30, 25), [(8, 60), (56, 60), (48, 42), (16, 42)])
pygame.draw.polygon(rock, (75, 45, 35), [(11, 57), (53, 57), (46, 44), (18, 44)])
# Трещины с лавой в основании
pygame.draw.lines(rock, (255, 120, 20), False, [(16, 54), (28, 48), (38, 52), (48, 47)], 2)
# Башня
pygame.draw.rect(rock, (55, 38, 30), (18, 22, 28, 22))
pygame.draw.rect(rock, (85, 55, 45), (21, 24, 22, 18))
# Зубцы
for bx in [16, 27, 38]:
    pygame.draw.rect(rock, (65, 45, 35), (bx, 15, 10, 8))
# Раскалённое лавовое жерло / пушка
pygame.draw.circle(rock, (220, 50, 20), (32, 14), 8)
pygame.draw.circle(rock, (255, 200, 50), (32, 14), 5)
pygame.draw.circle(rock, (255, 255, 200), (32, 14), 2)
save_sprite("rock_tower.png", rock)

# 4. Башня Заморозки (64x64)
# Ледяной обелиск с сияющими синими кристаллами
frz = pygame.Surface((64, 64), pygame.SRCALPHA)
# Ледяной постамент
pygame.draw.polygon(frz, (30, 60, 95), [(12, 60), (52, 60), (46, 48), (18, 48)])
pygame.draw.polygon(frz, (60, 120, 180), [(15, 57), (49, 57), (44, 50), (20, 50)])
# Обелиск
pygame.draw.polygon(frz, (70, 150, 220), [(22, 48), (42, 48), (38, 18), (26, 18)])
pygame.draw.polygon(frz, (130, 210, 255), [(24, 46), (40, 46), (36, 20), (28, 20)])
# Ледяной пик
pygame.draw.polygon(frz, (180, 240, 255), [(26, 18), (38, 18), (32, 4)])
pygame.draw.polygon(frz, (255, 255, 255), [(29, 18), (35, 18), (32, 8)])
# Кристаллы по бокам
pygame.draw.polygon(frz, (110, 190, 245), [(14, 42), (20, 46), (18, 30)])
pygame.draw.polygon(frz, (110, 190, 245), [(50, 42), (44, 46), (46, 30)])
save_sprite("freeze_tower.png", frz)

# 5. Палатка Солдат (64x64)
# Армейская палатка с флагом и входом
tent = pygame.Surface((64, 64), pygame.SRCALPHA)
# Земляная подстилка
pygame.draw.ellipse(tent, (55, 75, 50), (6, 46, 52, 16))
# Палаточный тент
pygame.draw.polygon(tent, (190, 170, 120), [(10, 54), (54, 54), (32, 20)])
pygame.draw.polygon(tent, (220, 200, 150), [(14, 52), (50, 52), (32, 22)])
# Тёмный вход
pygame.draw.polygon(tent, (35, 25, 20), [(24, 54), (40, 54), (32, 34)])
# Флагшток и красный вымпел
pygame.draw.line(tent, (80, 60, 40), (32, 22), (32, 6), 3)
pygame.draw.polygon(tent, (220, 40, 40), [(32, 6), (46, 11), (32, 16)])
save_sprite("tent_tower.png", tent)

# 6. Кактус-воин (Солдат) 36x36
sol = pygame.Surface((36, 36), pygame.SRCALPHA)
# Тело кактуса
pygame.draw.rect(sol, (45, 140, 50), (11, 10, 14, 18), border_radius=6)
pygame.draw.rect(sol, (70, 185, 75), (13, 12, 10, 14), border_radius=4)
# Глазки
pygame.draw.rect(sol, (20, 30, 20), (14, 15, 2, 3))
pygame.draw.rect(sol, (20, 30, 20), (19, 15, 2, 3))
# Повязка воина (красная лента на лбу)
pygame.draw.rect(sol, (220, 40, 40), (10, 12, 16, 3))
# Щит воина
pygame.draw.ellipse(sol, (60, 110, 190), (3, 13, 9, 14))
pygame.draw.ellipse(sol, (110, 170, 240), (4, 14, 7, 12))
pygame.draw.circle(sol, (255, 220, 50), (7, 20), 2)
# Копьё
pygame.draw.line(sol, (120, 90, 50), (26, 28), (30, 4), 2)
pygame.draw.polygon(sol, (210, 210, 220), [(30, 4), (28, 9), (32, 9)])
save_sprite("soldier.png", sol)

print("All custom sprites saved successfully!")
