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

# 2. Новые редизайны башен (утверждённые версии)
from generate_tower_redesigns import (
    draw_magic_v1,
    draw_rock_v1,
    draw_freeze_v2,
    draw_tesla_v1,
)

# 2.1 Магическая башня (Астральный кактус + парящий кристалл)
save_sprite("magic_tower.png", draw_magic_v1())

# 2.2 Огненная башня (Вулканическое горнило с лавой и пламенем)
save_sprite("rock_tower.png", draw_rock_v1())

# 2.3 Ледяная башня (Глициерный монолит с рунами)
save_sprite("freeze_tower.png", draw_freeze_v2())

# 2.4 Тесла башня (Двурогий арк-разрядник Иакова)
save_sprite("tesla_tower.png", draw_tesla_v1())


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
