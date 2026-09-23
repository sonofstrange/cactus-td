# =========================================================================
# ИГРОВЫЕ СУЩНОСТИ И ОБЪЕКТЫ (ENTITIES)
# =========================================================================
import collections
import math
import random
import time
import pygame

from config import *
from tree_data_v02 import get_mob_bestiary_tier, get_bestiary_tier_thresholds
from game_data import *

# АНИМАЦИИ ВЫПАДЕНИЯ РЕСУРСОВ (Звёздный, Тёмный кактус, Росток)
# -------------------------------------------------------------------------
class ResourceDrop:
    def __init__(self, start_x, start_y, drop_type="stellar", target_x=None, target_y=None, count=1, info=None):
        self.x = float(start_x)
        self.y = float(start_y)
        self.drop_type = drop_type
        self.count = count
        self.info = info

        if drop_type == "dark":
            self.target_x = float(target_x) if target_x is not None else 55.0
            self.target_y = float(target_y) if target_y is not None else float(SCREEN_HEIGHT - 168)
            self.img = dark_cactus_img_s
            self.spark_colors = [(210, 110, 255), (175, 75, 245), (245, 180, 255), (140, 50, 220)]
        elif drop_type == "sprout":
            self.target_x = float(target_x) if target_x is not None else float(start_x + random.uniform(-35, 35))
            self.target_y = float(target_y) if target_y is not None else -60.0
            self.img = sprout_icon if sprout_icon else cactus_img_s
            self.spark_colors = [(110, 255, 170), (80, 235, 130), (190, 255, 210), (50, 205, 110)]
        else:  # "stellar"
            self.target_x = float(target_x) if target_x is not None else 55.0
            self.target_y = float(target_y) if target_y is not None else float(SCREEN_HEIGHT - 114)
            self.img = stellar_cactus_img_s
            self.spark_colors = [CYAN, YELLOW, WHITE, GOLD]

        self.vx = random.uniform(-3.2, 3.2)
        self.vy = random.uniform(-7.5, -4.5)
        self.gravity = 0.38

        self.age = 0.0
        self.max_bounce_age = random.uniform(22.0, 28.0)
        self.homing = False
        self.homing_speed = 5.0
        self.active = True
        self.spark_timer = 0.0

    def update(self, effects, *args):
        dt = args[0] if (args and isinstance(args[0], (int, float))) else (1.0 / 60.0)
        step = dt * 60.0
        self.age += step
        if not self.homing:
            self.x += self.vx * step
            self.y += self.vy * step
            self.vy += self.gravity * step
            self.spark_timer += step
            if self.spark_timer >= 2.5:
                self.spark_timer = 0.0
                scol = random.choice(self.spark_colors)
                effects.append(DropSpark(self.x, self.y, color=scol))
            if self.age >= self.max_bounce_age:
                self.homing = True
        else:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.hypot(dx, dy)
            self.homing_speed = min(32.0, self.homing_speed + 1.5 * step)
            step_dist = self.homing_speed * step
            self.spark_timer += step
            if self.spark_timer >= 2.0:
                self.spark_timer = 0.0
                scol = random.choice(self.spark_colors)
                effects.append(DropSpark(self.x, self.y, color=scol))
            if dist < step_dist or dist < 20 or self.y < -30:
                self.active = False
                for _ in range(16):
                    scol = random.choice(self.spark_colors)
                    effects.append(DropSpark(self.x, self.y, burst=True, color=scol))
                return True
            else:
                self.x += (dx / dist) * step_dist
                self.y += (dy / dist) * step_dist
        return False

    def draw(self, surface):
        if not self.active or not self.img: return
        rect = self.img.get_rect(center=(int(self.x), int(self.y)))
        glow_col = self.spark_colors[0]
        glow_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*glow_col, 50), (16, 16), 14)
        surface.blit(glow_surf, (int(self.x - 16), int(self.y - 16)))
        surface.blit(self.img, rect)


class StellarCactusDrop(ResourceDrop):
    def __init__(self, start_x, start_y, target_x=None, target_y=None, count=1):
        super().__init__(start_x, start_y, drop_type="stellar", target_x=target_x, target_y=target_y, count=count)


class DarkCactusDrop(ResourceDrop):
    def __init__(self, start_x, start_y, target_x=None, target_y=None, count=1):
        super().__init__(start_x, start_y, drop_type="dark", target_x=target_x, target_y=target_y, count=count)


class SproutDrop(ResourceDrop):
    def __init__(self, start_x, start_y, target_x=None, target_y=None, count=1, cactus_name=None):
        super().__init__(start_x, start_y, drop_type="sprout", target_x=target_x, target_y=target_y, count=count, info=cactus_name)


class DropSpark:
    def __init__(self, x, y, burst=False, color=None):
        self.x = float(x)
        self.y = float(y)
        if burst:
            speed = random.uniform(2.5, 7.0)
            ang = random.uniform(0, math.pi * 2)
            self.vx = math.cos(ang) * speed
            self.vy = math.sin(ang) * speed
            self.life = random.randint(18, 28)
        else:
            self.vx = random.uniform(-1.0, 1.0)
            self.vy = random.uniform(-1.0, 1.0)
            self.life = random.randint(12, 20)
        self.max_life = self.life
        self.color = color if color else random.choice([CYAN, YELLOW, WHITE, GOLD])

    def update(self, *args):
        dt = args[0] if (args and isinstance(args[0], (int, float))) else (1.0 / 60.0)
        step = dt * 60.0
        self.x += self.vx * step
        self.y += self.vy * step
        self.life -= step
        return self.life <= 0

    def draw(self, surface):
        if self.life <= 0: return
        ratio = max(0.0, min(1.0, self.life / self.max_life))
        alpha = int(255 * ratio)
        radius = max(1, int(3.5 * ratio))
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (radius, radius), radius)
        surface.blit(s, (int(self.x - radius), int(self.y - radius)))


# -------------------------------------------------------------------------
# АТМОСФЕРНЫЕ ЧАСТИЦЫ БИОМОВ (Снег, Пепел, Песчинки, Кванты, Споры)
# -------------------------------------------------------------------------
class AmbientParticle:
    def __init__(self, ptype):
        self.ptype = ptype
        self.reset(random_y=True)

    def reset(self, random_y=False):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT) if random_y else -10.0
        self.life = random.uniform(3.5, 7.5)
        self.max_life = self.life
        self.size = random.uniform(2.0, 4.2)
        self.sin_offset = random.uniform(0, math.pi * 2)

        if self.ptype == "snow":
            self.vx = random.uniform(-18.0, 18.0)
            self.vy = random.uniform(38.0, 80.0)
            self.color = (random.randint(230, 255), random.randint(240, 255), 255)
        elif self.ptype == "sand":
            self.vx = random.uniform(65.0, 140.0)
            self.vy = random.uniform(15.0, 45.0)
            self.color = (random.randint(215, 245), random.randint(185, 215), random.randint(110, 150))
        elif self.ptype == "ember":
            self.vx = random.uniform(-25.0, 25.0)
            self.vy = random.uniform(-65.0, -25.0)
            self.color = (255, random.randint(85, 195), 30)
            if not random_y:
                self.y = SCREEN_HEIGHT + 10.0
        elif self.ptype == "cosmic":
            self.vx = random.uniform(-15.0, 15.0)
            self.vy = random.uniform(-25.0, 25.0)
            self.color = random.choice([(140, 180, 255), (200, 130, 255), (100, 240, 255)])
        elif self.ptype == "eclipse":
            self.vx = random.uniform(-30.0, 30.0)
            self.vy = random.uniform(-40.0, 15.0)
            self.color = (random.randint(220, 255), random.randint(30, 75), random.randint(85, 155))
        elif self.ptype == "crystal":
            self.vx = random.uniform(-16.0, 16.0)
            self.vy = random.uniform(-20.0, 20.0)
            self.color = random.choice([(90, 235, 245), (140, 255, 230), (210, 245, 255)])
        elif self.ptype == "toxic":
            self.vx = random.uniform(-20.0, 20.0)
            self.vy = random.uniform(-50.0, -15.0)
            self.color = random.choice([(140, 255, 40), (180, 255, 80), (100, 220, 30)])
            if not random_y:
                self.y = SCREEN_HEIGHT + 10.0
        elif self.ptype == "astral":
            self.vx = random.uniform(-25.0, 25.0)
            self.vy = random.uniform(-25.0, 25.0)
            self.color = random.choice([(255, 225, 80), (255, 245, 160), (255, 190, 40)])
        else: # pollen
            self.vx = random.uniform(-16.0, 16.0)
            self.vy = random.uniform(-22.0, 12.0)
            self.color = (random.randint(215, 245), random.randint(240, 255), random.randint(155, 190))

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.reset(random_y=False)
            return
        wobble = math.sin(self.life * 2.8 + self.sin_offset) * 14.0
        self.x += (self.vx + wobble) * dt
        self.y += self.vy * dt
        if self.x < -25 or self.x > SCREEN_WIDTH + 25 or self.y < -25 or self.y > SCREEN_HEIGHT + 25:
            self.reset(random_y=False)

    def draw(self, surface):
        if self.life <= 0: return
        alpha = int(255 * min(1.0, (self.life / self.max_life) * 2.2, (self.max_life - self.life) * 4.5))
        if alpha <= 0: return
        rad = max(1, int(self.size))
        ps = pygame.Surface((rad * 2 + 2, rad * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(ps, (*self.color, min(220, alpha)), (rad + 1, rad + 1), rad)
        surface.blit(ps, (int(self.x - rad), int(self.y - rad)))


class AmbientParticleSystem:
    def __init__(self, map_id, count=None):
        self.map_id = map_id
        biome = MAP_BIOMES_DATA.get(map_id, MAP_BIOMES_DATA[0])
        self.ptype = biome.get("particle_type", "pollen")
        if count is None:
            count = 18 if get_graphics_preset() == "optimized" else 48
        self.particles = [AmbientParticle(self.ptype) for _ in range(count)]

    def update(self, dt):
        for p in self.particles:
            p.update(dt)

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)


def draw_rally_flag(surface, x, y, active=False, bg_time=None):
    """Отрисовывает тактический флаг точки сбора солдат на карте."""
    x, y = int(x), int(y)
    t = (bg_time / 1000.0) if bg_time is not None else time.time()
    pulse = math.sin(t * 5.0) * 2

    # 1. Тень и маркер на земле
    pygame.draw.ellipse(surface, (0, 0, 0, 95), (x - 11, y + 2, 22, 8))
    if active:
        r_rad = max(8, int(13 + pulse))
        pygame.draw.circle(surface, (60, 235, 120), (x, y + 5), r_rad, width=2)
        pygame.draw.circle(surface, (150, 255, 190), (x, y + 5), 4)
    else:
        pygame.draw.circle(surface, (45, 150, 80), (x, y + 5), 5, width=1)

    # 2. Древко флага
    pygame.draw.line(surface, (60, 50, 40), (x, y + 5), (x, y - 24), 2)
    # Золотое навершие
    pygame.draw.circle(surface, (255, 215, 60), (x, y - 25), 3)

    # 3. Полотно флага (треугольный вымпел с лёгким колыханием)
    flutter = int(math.sin(t * 8.0) * 2)
    flag_pts = [(x, y - 24), (x + 16 + flutter, y - 17), (x, y - 10)]
    f_col = (50, 215, 100) if active else (40, 165, 75)
    b_col = (180, 255, 200) if active else (100, 225, 140)
    pygame.draw.polygon(surface, f_col, flag_pts)
    pygame.draw.polygon(surface, b_col, flag_pts, width=1)


def project_point_to_segment(px, py, ax, ay, bx, by):
    """Проецирует точку (px, py) на отрезок между (ax, ay) и (bx, by)."""
    dx = bx - ax
    dy = by - ay
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0:
        return float(ax), float(ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / seg_len_sq))
    return float(ax + t * dx), float(ay + t * dy)


def get_nearest_point_on_road(px, py, path):
    """
    Находит ближайшую точку проекции на непрерывную линию дороги (отрезки между узлами path).
    Возвращает (proj_x, proj_y, seg_idx, dist_to_road).
    """
    if not path or len(path) < 2:
        return float(px), float(py), 0, 0.0
    best_dist_sq = float('inf')
    best_pt = (float(px), float(py))
    best_idx = 0
    for i in range(len(path) - 1):
        ax, ay = path[i]
        bx, by = path[i + 1]
        proj_x, proj_y = project_point_to_segment(px, py, ax, ay, bx, by)
        d_sq = (px - proj_x) ** 2 + (py - proj_y) ** 2
        if d_sq < best_dist_sq:
            best_dist_sq = d_sq
            best_pt = (proj_x, proj_y)
            best_idx = i
    return best_pt[0], best_pt[1], best_idx, math.sqrt(best_dist_sq)


# -------------------------------------------------------------------------
# СОЛДАТЫ И КАЗАРМА
# -------------------------------------------------------------------------
class Soldier:
    def __init__(self, x, y, path_index, tent, target_x=None, target_y=None):
        self.x = float(x)
        self.y = float(y)
        self.target_x = float(target_x if target_x is not None else x)
        self.target_y = float(target_y if target_y is not None else y)
        self.path_index = path_index
        self.tent = tent
        self.engaged_count = 0
        self.move_speed = 95.0
        self.walk_timer = random.random() * 6.28

        stats = tent.get_stats_at_level(tent.level)
        self.max_hp = stats.get("soldier_hp", 28 + tent.level * 16)
        self.hp = float(self.max_hp)
        self.damage = stats.get("soldier_dmg", round(2.0 + tent.level * 0.8, 1))
        self.attack_cooldown = max(0.50, 0.80 - tent.level * 0.02)
        self.attack_timer = 0.0
        self.active = True
        self.image = soldier_img
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self, dt, enemies, effects=None):
        if not self.active: return
        self.engaged_count = 0
        if getattr(self, "stun_timer", 0.0) > 0.0:
            self.stun_timer -= dt
            return

        self.attack_timer += dt

        # Плавное перемещение к назначенной точке сбора
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist_to_target = math.hypot(dx, dy)
        if dist_to_target > 2.0:
            step = min(dist_to_target, self.move_speed * dt)
            self.x += (dx / dist_to_target) * step
            self.y += (dy / dist_to_target) * step
            self.walk_timer += dt * 12.0
            self.rect.center = (int(self.x), int(self.y))
        else:
            self.x = self.target_x
            self.y = self.target_y
            self.rect.center = (int(self.x), int(self.y))

        closest_enemy = None
        closest_dist = 36.0
        for enemy in enemies:
            if not enemy.active or getattr(enemy, "is_flying", False) or getattr(enemy, "is_burrowed", False):
                continue
            d = math.hypot(self.x - enemy.x, self.y - enemy.y)
            if d < closest_dist:
                closest_dist = d
                closest_enemy = enemy

        if closest_enemy and self.attack_timer >= self.attack_cooldown:
            self.attack_timer = 0.0
            closest_enemy.take_damage(self.damage, damage_type="soldier")
            if self.tent:
                self.tent.record_damage(self.damage)
            if effects is not None:
                effects.append(FloatingText(closest_enemy.x, closest_enemy.y - 12, f"-{self.damage:g}", (180, 245, 160)))

    def take_mob_damage(self, enemy_type, effects=None, attacker=None):
        if enemy_type == 1: dmg = 3        # Зелёный слайм (легкий тычок)
        elif enemy_type == 2: dmg = 6      # Синий слайм
        elif enemy_type == 3: dmg = 12     # Огненный слайм (сильный ожог)
        elif enemy_type == 4: dmg = 5      # Быстрый слайм
        elif enemy_type == 5: dmg = 16     # Бронированный слайм (тяжелый таран)
        elif enemy_type == 6: dmg = 4      # Слайм-лекарь
        elif enemy_type == 7: dmg = 8      # Тигровый слайм (агрессивный укус)
        elif enemy_type == 8: dmg = 7      # Ледяное желе
        elif enemy_type == 9: dmg = 14     # Слаймовая пирамида (тяжёлое падение)
        elif enemy_type == 10: dmg = 12    # Теневой слайм (теневой удар)
        elif enemy_type == 11: dmg = 10    # Призматический слайм
        elif enemy_type == 12: dmg = 14    # Пожиратель маны
        elif enemy_type == 13: dmg = 16    # Обсидиановый слайм
        elif enemy_type == 14: dmg = 10    # Паровой слайм
        elif enemy_type == 15: dmg = 25    # Слайм-камикадзе
        elif enemy_type == 16: dmg = 15    # Слайм-защитник
        elif enemy_type == 17: dmg = 8     # Призрачный слайм
        elif enemy_type == 18: dmg = 12    # Песчаный крот
        elif enemy_type == 777: dmg = 2    # Золотой слайм
        elif enemy_type == 51: dmg = 22    # Элитный страж
        elif enemy_type == 52: dmg = 32    # Элитный крушитель
        elif enemy_type == 53: dmg = 45    # Элитный титан
        elif enemy_type >= 4000: dmg = 260 # Король Всех Слаймов (мгновенный прорыв)
        elif enemy_type >= 3000: dmg = 180 # Теневой Исполин (сокрушительный удар)
        elif enemy_type >= 2000: dmg = 120 # Слизнебарон (огромный урон)
        elif enemy_type >= 1000: dmg = 70  # Царь-Слизень (ощутимый урон)
        s_data = globals().get('savedata', None)
        knight_lvl = s_data.get("Upgrades", {}).get("knight_training", 0) if isinstance(s_data, dict) else 0
        if knight_lvl > 0:
            dmg = max(1, int(dmg * (1.0 - knight_lvl * 0.06)))

        self.hp -= dmg
        if effects is not None:
            col = (255, 50, 50) if enemy_type >= 1000 else (245, 120, 100)
            effects.append(FloatingText(self.x, self.y - 14, f"-{dmg}", col))
            if enemy_type >= 1000:
                effects.append(RingEffect(self.x, self.y, 32, (255, 60, 60)))

        # Способность палатки «Кактусовые Шипы» (tent_thorns): возврат +30% урона за ранг атакующему
        thorns_lvl = s_data.get("Upgrades", {}).get("tent_thorns", 0) if isinstance(s_data, dict) else 0
        if thorns_lvl > 0 and attacker is not None and getattr(attacker, "active", False):
            thorns_dmg = round(dmg * (thorns_lvl * 0.30), 1)
            if thorns_dmg > 0:
                attacker.take_damage(thorns_dmg, damage_type="soldier", savedata=s_data)
                if self.tent:
                    self.tent.record_damage(thorns_dmg)
                if effects is not None:
                    effects.append(FloatingText(attacker.x, attacker.y - 16, f"-{thorns_dmg:g} 🌵 ШИПЫ!", (160, 255, 120)))
                    effects.append(DropSpark(attacker.x, attacker.y, burst=False))

        if self.hp <= 0:
            self.active = False

    def draw(self, surface):
        if not self.active: return
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        is_walking = math.hypot(dx, dy) > 2.0
        bob = int(math.sin(self.walk_timer) * 2) if is_walking else 0
        draw_y = self.rect.y + bob
        surface.blit(self.image, (self.rect.x, draw_y))
        # Шкала здоровья с тенью
        bw = 26
        ratio = max(0.0, self.hp / self.max_hp)
        pygame.draw.rect(surface, BLACK, (int(self.x - bw // 2 - 1), int(self.y - 19 + bob), bw + 2, 5))
        pygame.draw.rect(surface, RED, (int(self.x - bw // 2), int(self.y - 18 + bob), bw, 3))
        pygame.draw.rect(surface, GREEN, (int(self.x - bw // 2), int(self.y - 18 + bob), int(bw * ratio), 3))

        # Визуализация оглушения (звёздочки стана над головой)
        if getattr(self, "stun_timer", 0.0) > 0.0:
            t_angle = pygame.time.get_ticks() * 0.008
            cx, cy = self.x, self.y - 24 + bob
            for ai in range(3):
                ang = t_angle + ai * (2.0 * math.pi / 3.0)
                sx = cx + math.cos(ang) * 9
                sy = cy + math.sin(ang) * 4
                pygame.draw.circle(surface, (255, 230, 80), (int(sx), int(sy)), 2)


# -------------------------------------------------------------------------
# БАШНИ
# -------------------------------------------------------------------------
_RANGE_SURF_CACHE = {}
_ORB_GLOW_CACHE = {}

def get_cached_orb_glow(ocol):
    surf = _ORB_GLOW_CACHE.get(ocol)
    if surf is None:
        surf = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*ocol, 75), (9, 9), 8)
        _ORB_GLOW_CACHE[ocol] = surf
    return surf

def get_cached_range_surf(radius, col, bcol, width=2):
    """Возвращает кэшированную поверхность с полупрозрачным кругом радиуса атаки.
    Исключает покадровое выделение памяти (0 FPS drop, максимальная производительность)."""
    r = int(radius)
    if r <= 0:
        return None
    key = (r, tuple(col), tuple(bcol), width)
    surf = _RANGE_SURF_CACHE.get(key)
    if surf is None:
        size = r * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # Полупрозрачная заливка
        pygame.draw.circle(surf, col, (r, r), r)
        # Внешняя граница
        if width > 0:
            pygame.draw.circle(surf, bcol, (r, r), r, width=width)
        _RANGE_SURF_CACHE[key] = surf
    return surf


class Tower:
    def __init__(self, x, y, tower_type, starting_level=0, max_level_bonus=0, dmg_mult=1.0, game_map=0):
        self.x = x
        self.y = y
        self.type = tower_type
        self.level = 0
        self.dmg_mult = dmg_mult
        self.game_map = game_map
        tower_built.play()

        if tower_type == "magic":
            self.image = magic_tower_img
            self.base_max_level = 15
            self.cost = 100
        elif tower_type == "rock":
            self.image = rock_tower_img
            self.base_max_level = 20
            self.cost = 200
        elif tower_type == "freeze":
            self.image = freeze_tower_img
            self.base_max_level = 15
            self.cost = 150
        elif tower_type == "tent":
            self.image = tent_tower_img
            self.base_max_level = 15
            self.cost = 220
            self.soldiers = []
            self.target_path_point = None
            self.rally_point = None
        elif tower_type == "tesla":
            self.image = tesla_tower_img
            self.base_max_level = 15
            self.cost = 250
        elif tower_type == "farm":
            self.image = farm_tower_img
            self.base_max_level = 15
            self.cost = 120
            self.income = 35
        elif tower_type == "sun":
            self.image = sun_tower_img
            self.base_max_level = 10
            self.cost = 200
            self.current_beam_target = None
            self.beam_multiplier = 0.5
            self.beam_tick_timer = 0.0

        # Базовые характеристики напрямую из формул нулевого уровня
        base_s = self.get_stats_at_level(0)
        self.range = base_s["range"]
        self.damage = base_s["damage"]
        self.cooldown = base_s["cooldown"]
        self.upgrade_cost = base_s["upgrade_cost"]
        if tower_type == "magic":
            self.crit_chance = base_s.get("crit_chance", 5)
            self.crit_mult = base_s.get("crit_mult", 2.0)
        elif tower_type == "rock":
            self.splash_radius = base_s["splash"]
            self.frozen_multiplier = base_s.get("frozen_multiplier", 1.75)
        elif tower_type == "freeze":
            self.slow_ratio = base_s["slow_ratio"]
            self.slow_duration = base_s["slow_dur"]
        elif tower_type == "tent":
            self.max_soldiers = base_s["soldiers"]
        elif tower_type == "tesla":
            self.max_chains = base_s["chains"]
        elif tower_type == "farm":
            self.income = base_s["income"]
        elif tower_type == "sun":
            self.max_multiplier = base_s.get("max_multiplier", 2.5)
            self.ramp_time = base_s.get("ramp_time", 1.0)

        max_level_bonus_final = max_level_bonus
        self.max_level = self.base_max_level + max_level_bonus_final
        self.timer = 0.0
        self.rect = self.image.get_rect(center=(x, y - 8))
        self.target_priority = "FIRST"  # "FIRST", "LAST", "STRONGEST", "CLOSEST"
        self.damage_dealt = 0.0
        self.total_damage_dealt = 0.0
        self.damage_history = collections.deque()
        self.total_gold_earned = 0
        self.farm_drop_timer = 0.0
        self.speed_boost = 0
        self.drop_interval = 18.0
        self.total_invested = self.cost

        for _ in range(starting_level):
            if self.level < self.max_level:
                self._apply_level_stats()

    def record_damage(self, dmg, cur_time=None):
        if cur_time is None:
            cur_time = time.time()
        self.damage_dealt += dmg
        self.total_damage_dealt += dmg
        self.damage_history.append((cur_time, dmg))

    def get_dynamic_dps(self, cur_time=None, window=3.0):
        if cur_time is None:
            cur_time = time.time()
        cutoff = cur_time - window
        while self.damage_history and self.damage_history[0][0] < cutoff:
            self.damage_history.popleft()
        tot = sum(d for t, d in self.damage_history)
        return round(tot / max(0.5, window), 1)

    def set_rally_point(self, rx, ry, path=None):
        """Устанавливает точку сбора солдат для палатки (с притягиванием к полотну дороги)."""
        best_idx = 0
        if path and len(path) >= 2:
            proj_x, proj_y, s_idx, road_dist = get_nearest_point_on_road(rx, ry, path)
            # Притягивание к дороге, если точка в пределах 90 пикселей от оси дороги
            if road_dist <= 90:
                rx, ry = proj_x, proj_y
                best_idx = s_idx
        elif path and len(path) == 1:
            rx, ry = path[0]
            best_idx = 0

        d = math.hypot(rx - self.x, ry - self.y)
        max_r = float(self.range)
        if d > max_r and d > 0:
            rx = self.x + (rx - self.x) * (max_r / d)
            ry = self.y + (ry - self.y) * (max_r / d)

        self.rally_point = (float(rx), float(ry))
        self.target_path_point = (float(rx), float(ry), best_idx)
        self._reposition_soldiers()

    def _get_soldier_formation_offsets(self, count):
        """Возвращает тактические смещения солдат вокруг флага сбора."""
        if count <= 1:
            return [(0, 0)]
        elif count == 2:
            return [(-12, 0), (12, 0)]
        elif count == 3:
            return [(0, -12), (-12, 10), (12, 10)]
        elif count == 4:
            return [(0, -14), (0, 14), (-14, 0), (14, 0)]
        else:
            offsets = []
            radius = 16.0
            for i in range(count):
                ang = (2 * math.pi / count) * i
                offsets.append((int(round(math.cos(ang) * radius)), int(round(math.sin(ang) * radius))))
            return offsets

    def _reposition_soldiers(self):
        if not self.rally_point:
            return
        rx, ry = self.rally_point
        active_soldiers = [s for s in self.soldiers if s.active]
        offsets = self._get_soldier_formation_offsets(len(active_soldiers))
        for s, (ox, oy) in zip(active_soldiers, offsets):
            s.target_x = rx + ox
            s.target_y = ry + oy

    def get_stats_at_level(self, lvl):
        """Возвращает словарь всех характеристик башни для заданного уровня."""
        mult = getattr(self, "dmg_mult", 1.0)
        g_map = getattr(self, "game_map", 0)
        if g_map == 3:  # Волны: башни наносят +10% урона
            mult *= 1.10

        sniper_lvl = savedata.get("Upgrades", {}).get("sniper_optics", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
        atk_spd_lvl = savedata.get("Upgrades", {}).get("attack_speed_overdrive", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
        crit_mast_lvl = savedata.get("Upgrades", {}).get("critical_mastery", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
        blizzard_lvl = savedata.get("Upgrades", {}).get("blizzard", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
        shield_lvl = savedata.get("Upgrades", {}).get("shield_wall", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
        gh_buffs = get_greenhouse_buffs(savedata) if 'savedata' in globals() and isinstance(savedata, dict) else {}
        relic_buffs = get_all_relic_buffs(savedata) if 'savedata' in globals() and isinstance(savedata, dict) else {}
        if gh_buffs.get("compost_dmg_mult", 0.0) > 0:
            mult *= (1.0 + gh_buffs["compost_dmg_mult"])
        if relic_buffs.get("global_dmg_mult", 0.0) > 0:
            mult *= (1.0 + relic_buffs["global_dmg_mult"])
        if g_map == 3:  # Волны (Жар): +5% урона башен
            mult *= 1.05
        rng_relic_mult = 1.0 + relic_buffs.get("range_mult", 0.0)
        if g_map == 2:  # Перекрёстки (Песчаная буря): видимость/дальность башен -10%
            rng_relic_mult *= 0.90
        relic_atk_spd = relic_buffs.get("atk_spd_mult", 0.0)

        upg_discount = min(0.50, relic_buffs.get("upgrade_cost_discount", 0.0))
        diff = savedata.get("difficulty", "normal") if 'savedata' in globals() and isinstance(savedata, dict) else "normal"
        diff_upg_mult = 0.8 if diff == "casual" else 1.0
        cost_mult = (1.0 - upg_discount) * diff_upg_mult

        if self.type == "magic":
            magic_focus_lvl = savedata.get("Upgrades", {}).get("magic_focus", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            magic_power_lvl = savedata.get("Upgrades", {}).get("magic_power", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            rng_lvl = min(lvl, 5) * 6.0 + min(max(0, lvl - 5), 7) * 3.0 + max(0, lvl - 12) * 1.5
            rng = int((145 + rng_lvl + sniper_lvl * 8) * rng_relic_mult)
            dmg_per_lvl = 0.75 + magic_power_lvl * 0.10
            dmg = round((1.0 + dmg_per_lvl * lvl) * mult * (1.0 + magic_focus_lvl * 0.12 + gh_buffs.get("void_dmg_mult", 0.0)), 1)
            raw_cd = max(0.35, 0.95 - lvl * 0.038)
            cd = max(0.20, round(raw_cd / (1.0 + atk_spd_lvl * 0.04 + relic_atk_spd), 2))
            cost = max(5, int((75 * (1.18 ** lvl) + 25 * lvl) * cost_mult))
            map6_crit = 8 if g_map == 6 else 0  # Лабиринт: крит-шанс +8%
            crit_bonus = int(relic_buffs.get("crit_chance_bonus", 0.0) * 100)
            arcane_precision_lvl = savedata.get("Upgrades", {}).get("arcane_precision", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            crit_chance = min(100, 5 + 1 * lvl + magic_focus_lvl * 4 + crit_mast_lvl * 1.5 + map6_crit + crit_bonus + arcane_precision_lvl * 2)
            crit_mult = round(2.0 + magic_focus_lvl * 0.25 + relic_buffs.get("crit_dmg_bonus", 0.0), 2)
            return {
                "damage": dmg,
                "range": rng,
                "cooldown": cd,
                "crit_chance": crit_chance,
                "crit_mult": crit_mult,
                "dps": dmg / cd,
                "upgrade_cost": cost,
                "special_name": "Крит-шанс",
                "special_val": f"{crit_chance:g}% (крит x{crit_mult:.2f})",
                "passive_desc": "Пассивно: пробивает маг. броню врагов"
            }
        elif self.type == "rock":
            inferno_lvl = savedata.get("Upgrades", {}).get("inferno_mastery", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            rng_lvl = min(lvl, 5) * 5.0 + min(max(0, lvl - 5), 7) * 2.8 + max(0, lvl - 12) * 1.4
            rng = int((135 + rng_lvl + sniper_lvl * 8) * rng_relic_mult)
            dmg = round((1.5 + 0.62 * lvl) * mult * (1.0 + inferno_lvl * 0.10 + gh_buffs.get("fire_dmg_mult", 0.0)) * (1.0 + relic_buffs.get("rock_damage_mult", 0.0)), 1)
            splash_lvl = min(lvl, 5) * 2.2 + min(max(0, lvl - 5), 7) * 1.4 + max(0, lvl - 12) * 0.7
            splash = int((44 + splash_lvl + inferno_lvl * 4) * (1.0 + relic_buffs.get("rock_splash_mult", 0.0)))
            if g_map == 2:  # Перекрёстки: +15% сплэш
                splash = int(splash * 1.15)
            elif g_map == 7:  # Петля: +20% сплэш
                splash = int(splash * 1.20)
            frozen_multiplier = round(1.40 + inferno_lvl * 0.10 + relic_buffs.get("frozen_dmg_bonus", 0.0), 2)
            raw_cd = max(0.90, 1.75 - lvl * 0.04)
            cd = max(0.50, round(raw_cd / (1.0 + atk_spd_lvl * 0.04 + relic_atk_spd), 2))
            cost = max(5, int((90 * (1.17 ** lvl) + 20 * lvl) * cost_mult))
            combo_pct = int((frozen_multiplier - 1.0) * 100)
            return {
                "damage": dmg,
                "range": rng,
                "splash": splash,
                "frozen_multiplier": frozen_multiplier,
                "cooldown": cd,
                "dps": dmg / cd,
                "upgrade_cost": cost,
                "special_name": "Радиус сплэша",
                "special_val": f"{splash} px",
                "passive_desc": f"Синергия: +{combo_pct}% урона по заморозке"
            }
        elif self.type == "freeze":
            frost_lvl = savedata.get("Upgrades", {}).get("frost_nova", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            rng_lvl = min(lvl, 5) * 5.0 + min(max(0, lvl - 5), 7) * 2.8 + max(0, lvl - 12) * 1.4
            rng = int((135 + rng_lvl + sniper_lvl * 8 + blizzard_lvl * 18) * rng_relic_mult)
            if g_map == 6:  # Лабиринт: радиус заморозки +20%
                rng = int(rng * 1.20)
            dmg = round((0.35 + 0.16 * lvl) * mult * (1.0 + frost_lvl * 0.20), 1)
            base_slow = 36.0
            diminishing_lvl_slow = 18.0 * lvl / (lvl + 3.5)
            talent_bonus = frost_lvl * 2.7 + blizzard_lvl * 3.3 + gh_buffs.get("frost_slow_mult", 0.0) * 100
            total_slow_pct = min(80.0, base_slow + diminishing_lvl_slow + talent_bonus)
            slow_ratio = max(0.20, round(1.0 - (total_slow_pct / 100.0), 2))
            slow_pct = int(round((1.0 - slow_ratio) * 100))
            frost_linger_lvl = savedata.get("Upgrades", {}).get("frost_linger", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            slow_dur = round((2.4 + lvl * 0.12 + frost_linger_lvl * 0.15) * (1.0 + frost_lvl * 0.10) * (1.0 + relic_buffs.get("freeze_duration_mult", 0.0)), 2)
            if g_map == 1:  # Круговорот: Заморозка длится +15% дольше
                slow_dur = round(slow_dur * 1.15, 1)
            raw_cd = max(0.55, 1.30 - lvl * 0.045)
            cd = max(0.30, round(raw_cd / (1.0 + atk_spd_lvl * 0.04 + relic_atk_spd), 2))
            cost = max(5, int((85 * (1.18 ** lvl) + 20 * lvl) * cost_mult))
            return {
                "damage": dmg,
                "range": rng,
                "slow_ratio": slow_ratio,
                "slow_pct": slow_pct,
                "slow_dur": slow_dur,
                "cooldown": cd,
                "dps": dmg / cd,
                "upgrade_cost": cost,
                "special_name": "Замедление",
                "special_val": f"{slow_pct}% (на {slow_dur:.1f}с)",
                "passive_desc": "Аура льда: тушит горение и замедляет толпу"
            }
        elif self.type == "tent":
            knight_lvl = savedata.get("Upgrades", {}).get("knight_training", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            rally_range_lvl = savedata.get("Upgrades", {}).get("rally_range", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            rng_lvl = min(lvl, 5) * 5.0 + min(max(0, lvl - 5), 7) * 2.8 + max(0, lvl - 12) * 1.4
            rng = int((105 + rng_lvl + rally_range_lvl * 25) * rng_relic_mult)
            raw_cd = max(6.0, 9.5 - lvl * 0.16)
            cd = max(4.5, round(raw_cd / (1.0 + atk_spd_lvl * 0.03 + relic_atk_spd * 0.5), 2))
            soldiers = 2 + (lvl // 10)
            soldier_hp = int((28 + lvl * 16 + knight_lvl * 10 + shield_lvl * 30) * (1.0 + gh_buffs.get("soldier_hp_mult", 0.0) + relic_buffs.get("soldier_hp_mult", 0.0)))
            soldier_dmg = round((2.0 + lvl * 0.8) * mult * (1.0 + knight_lvl * 0.15 + gh_buffs.get("soldier_dmg_mult", 0.0)), 1)
            cost = max(5, int((100 * (1.20 ** lvl) + 25 * lvl) * cost_mult))
            armor_red = min(50, knight_lvl * 6 + int(relic_buffs.get("soldier_armor_mult", 0.0) * 100))
            p_desc = f"Орден: -{armor_red}% урона воинам" if armor_red > 0 else "Тактика: удерживают врагов на тропе"
            if shield_lvl > 0:
                p_desc += f" (Щит +{shield_lvl * 30} HP)"
            w_lbl = f"{soldiers} воина" if soldiers < 5 else f"{soldiers} воинов"
            return {
                "damage": soldier_dmg,
                "range": rng,
                "soldiers": soldiers,
                "soldier_hp": soldier_hp,
                "soldier_dmg": soldier_dmg,
                "cooldown": cd,
                "dps": soldier_dmg * soldiers,
                "upgrade_cost": cost,
                "armor_red": armor_red,
                "special_name": "Гарнизон",
                "special_val": f"{w_lbl} ({soldier_hp} HP)",
                "passive_desc": p_desc + ", +1 воин каждые 10 ур."
            }
        elif self.type == "tesla":
            ball_lvl = savedata.get("Upgrades", {}).get("ball_lightning", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            rng_lvl = min(lvl, 5) * 5.0 + min(max(0, lvl - 5), 7) * 2.8 + max(0, lvl - 12) * 1.4
            rng = int((145 + rng_lvl + ball_lvl * 18) * rng_relic_mult)
            if g_map == 4:  # Змейка: Дальность Теслы +10%
                rng = int(rng * 1.10)
            dmg = round((2.0 + 0.68 * lvl) * mult * (1.0 + ball_lvl * 0.12 + gh_buffs.get("tesla_dmg_mult", 0.0)), 1)
            raw_cd = max(0.50, 1.15 - lvl * 0.038)
            cd = max(0.28, round(raw_cd / (1.0 + atk_spd_lvl * 0.04 + relic_atk_spd), 2))
            overcharge_lvl = savedata.get("Upgrades", {}).get("overcharge", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            chains = 3 + (lvl // 5) + overcharge_lvl + gh_buffs.get("extra_jumps", 0) + relic_buffs.get("tesla_extra_targets", 0)
            cost = max(5, int((120 * (1.19 ** lvl) + 25 * lvl) * cost_mult))
            bounces = max(1, chains - 1)
            b_lbl = f"{bounces} отскок" if bounces % 10 == 1 and bounces % 100 != 11 else (f"{bounces} отскока" if 2 <= bounces % 10 <= 4 and not 12 <= bounces % 100 <= 14 else f"{bounces} отскоков")
            chains_lbl = f"{chains} цели" if 2 <= chains <= 4 else f"{chains} целей"
            return {
                "damage": dmg,
                "range": rng,
                "chains": chains,
                "cooldown": cd,
                "dps": dmg / cd,
                "upgrade_cost": cost,
                "special_name": "Отскоки цепи",
                "special_val": f"{b_lbl} ({chains_lbl})",
                "passive_desc": f"Разряд: {b_lbl} (+1 отскок каждые 5 ур. башни)"
            }
        elif self.type == "farm":
            soil_lvl = savedata.get("Upgrades", {}).get("fertile_soil", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            irrig_lvl = savedata.get("Upgrades", {}).get("farm_irrigation", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            relic_farm = relic_buffs.get("farm_income_mult", 0.0)
            income = int((35 + 25 * lvl + 8 * (lvl ** 1.35)) * (1.0 + soil_lvl * 0.10 + gh_buffs.get("farm_mult", 0.0) + relic_farm))
            cost = max(5, int((80 * (1.20 ** lvl) + 25 * lvl) * cost_mult))
            if irrig_lvl > 0:
                aura_range = 90 + (irrig_lvl - 1) * 40 + lvl * 3
                speed_boost = [0, 8, 14, 20][irrig_lvl]
                drop_interval = [0, 24.0, 18.0, 14.0][irrig_lvl]
                bonus_harvest = [0, 12, 24, 40][irrig_lvl]
            else:
                aura_range = 0
                speed_boost = 0
                drop_interval = 999999.0
                bonus_harvest = 0

            return {
                "damage": 0.0,
                "range": aura_range,
                "aura_range": aura_range,
                "cooldown": drop_interval,
                "income": income,
                "dps": 0.0,
                "speed_boost": speed_boost,
                "bonus_harvest": bonus_harvest,
                "upgrade_cost": cost,
                "special_name": "Аура Орошения" if irrig_lvl > 0 else "Урожай волны",
                "special_val": f"+{speed_boost}% скор. башен" if irrig_lvl > 0 else f"+{income} какт.",
                "passive_desc": f"Орошение (R={aura_range}): +{speed_boost}% темпа, полив раз в {int(drop_interval)}с" if irrig_lvl > 0 else "Требуется талант Система Орошения в Древе"
            }
        elif self.type == "sun":
            solar_power_lvl = savedata.get("Upgrades", {}).get("solar_power", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            beam_limit_lvl = savedata.get("Upgrades", {}).get("beam_limit", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            solar_trail_lvl = savedata.get("Upgrades", {}).get("solar_trail", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            prism_beams_lvl = savedata.get("Upgrades", {}).get("prism_beams", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0

            rng_lvl = min(lvl, 5) * 4.0 + min(max(0, lvl - 5), 7) * 2.2 + max(0, lvl - 12) * 1.0
            rng = int((140 + rng_lvl + sniper_lvl * 8) * rng_relic_mult)
            # Базово скромный урон (фигня в начале), разгоняемый прокачкой и талантом Солнечная Мощь (+20% за ранг)
            dmg_per_tick = round((0.20 + 0.06 * lvl) * mult * (1.0 + solar_power_lvl * 0.20), 2)
            max_mult = 2.5 + beam_limit_lvl * 0.5
            max_beams = 1 + prism_beams_lvl
            ramp_time = max(0.20, 1.0 - lvl * 0.01)
            cost = max(5, int((110 * (1.18 ** lvl) + 25 * lvl) * cost_mult))
            beam_lbl = f"{max_beams} луча" if 2 <= max_beams <= 4 else f"{max_beams} луч"
            return {
                "damage": dmg_per_tick,
                "range": rng,
                "cooldown": 0.10,
                "max_multiplier": max_mult,
                "ramp_time": ramp_time,
                "max_beams": max_beams,
                "dps": round((dmg_per_tick * 10.0) * ((0.5 + max_mult) / 2.0) * max_beams, 1),
                "upgrade_cost": cost,
                "special_name": "Потолок Разгона",
                "special_val": f"x{max_mult:.1f} ({beam_lbl})",
                "passive_desc": f"Солярный луч: {beam_lbl}, урон растёт до x{max_mult:.1f} (зарядка {ramp_time:.2f}с/x)" + (f", взрыв {solar_trail_lvl*2.5:.1f}% HP" if solar_trail_lvl > 0 else "")
            }
        return {}

    def recalculate_stats(self):
        stats = self.get_stats_at_level(self.level)
        self.range = stats["range"]
        self.damage = stats["damage"]
        self.cooldown = stats["cooldown"]
        self.upgrade_cost = stats["upgrade_cost"]
        if self.type == "magic":
            self.crit_chance = stats.get("crit_chance", 5)
            self.crit_mult = stats.get("crit_mult", 2.0)
        elif self.type == "rock":
            self.splash_radius = stats["splash"]
            self.frozen_multiplier = stats.get("frozen_multiplier", 1.75)
        elif self.type == "freeze":
            self.slow_ratio = stats["slow_ratio"]
            self.slow_duration = stats["slow_dur"]
        elif self.type == "tent":
            self.max_soldiers = stats["soldiers"]
        elif self.type == "tesla":
            self.max_chains = stats["chains"]
        elif self.type == "farm":
            self.income = stats["income"]
            self.speed_boost = stats.get("speed_boost", 0)
            self.drop_interval = stats.get("cooldown", 18.0)
        elif self.type == "sun":
            self.max_multiplier = stats.get("max_multiplier", 2.5)
            self.ramp_time = stats.get("ramp_time", 1.0)

    def _apply_level_stats(self):
        self.level += 1
        if 'savedata' in globals() and isinstance(savedata, dict):
            savedata.setdefault("Stats", {})["max_tower_level_reached"] = max(
                savedata.get("Stats", {}).get("max_tower_level_reached", 0),
                self.level
            )
            if self.type == "tent":
                savedata.setdefault("Stats", {})["max_tent_level"] = max(
                    savedata.get("Stats", {}).get("max_tent_level", 0),
                    self.level
                )
        self.recalculate_stats()

    def upgrade(self, current_cacti):
        if self.level < self.max_level and current_cacti >= self.upgrade_cost:
            cost = self.upgrade_cost
            self.total_invested += cost
            self._apply_level_stats()
            sfx_upgrade.play()
            return True, cost
        return False, 0

    def update(self, dt, enemies, projectiles, path, effects=None, active_meteorite=None, farm_boost=0.0):
        if self.type == "farm":
            irrig_lvl = savedata.get("Upgrades", {}).get("farm_irrigation", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            if irrig_lvl > 0:
                self.farm_drop_timer += dt
                drop_int = [0, 20.0, 15.0, 10.0][irrig_lvl]
                if self.farm_drop_timer >= drop_int:
                    self.farm_drop_timer = 0.0
                    soil_lvl = savedata.get("Upgrades", {}).get("fertile_soil", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
                    base_bonus = [0, 15, 30, 50][irrig_lvl]
                    bonus_c = int(base_bonus * (1.0 + soil_lvl * 0.15))
                    self.total_gold_earned += bonus_c
                    if effects is not None:
                        effects.append(FloatingText(self.x, self.y - 24, f"+{bonus_c} 🌵 ПОЛИВ!", (140, 255, 120)))
                        effects.append(RingEffect(self.x, self.y, 40, (120, 240, 100)))
                        for _ in range(6):
                            effects.append(DropSpark(self.x, self.y - 10, burst=True))
                        sfx_sprout_pickup.play()
                    return bonus_c
            return 0

        # Отключение башни при заморозке (способность Слизнебарона)
        if getattr(self, "freeze_disabled_timer", 0.0) > 0.0:
            self.freeze_disabled_timer -= dt
            if self.type == "sun":
                self.beams = []
            return 0

        # Ускорение перезарядки от ауры соседних ферм
        eff_dt = dt * (1.0 + farm_boost)
        self.timer += eff_dt

        if self.type == "sun":
            stats = self.get_stats_at_level(self.level)
            max_beams = stats.get("max_beams", 1)
            max_m = stats.get("max_multiplier", 2.5)
            ramp_t = stats.get("ramp_time", 1.0)
            solar_trail_lvl = savedata.get("Upgrades", {}).get("solar_trail", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0

            if not hasattr(self, "beams"):
                self.beams = []

            # 1. Фильтруем активные лучи, цели которых всё ещё живы и находятся в радиусе
            valid_beams = []
            assigned_targets = set()
            for b in self.beams:
                tgt = b.get("target")
                tgt_hp = getattr(tgt, "health", getattr(tgt, "hp", 0))
                tgt_alive = tgt and getattr(tgt, "active", False) and (tgt_hp > 0)
                if tgt_alive:
                    d = math.hypot(self.x - tgt.x, self.y - tgt.y)
                    max_d = self.range * 1.25 if tgt == active_meteorite else self.range
                    if d <= max_d:
                        valid_beams.append(b)
                        assigned_targets.add(tgt)
            self.beams = valid_beams[:max_beams]

            # 2. Если метеорит активен и выбран игроком, обязательно направляем на него один из лучей
            can_target_meteor = active_meteorite and getattr(active_meteorite, "active", False) and (getattr(active_meteorite, "hp", 0) > 0)
            if can_target_meteor and active_meteorite.targeted:
                d_met = math.hypot(self.x - active_meteorite.x, self.y - active_meteorite.y)
                if d_met <= self.range * 1.25 and active_meteorite not in assigned_targets:
                    new_b = {
                        "target": active_meteorite,
                        "multiplier": 0.5,
                        "tick_timer": 0.0,
                        "accum_dmg": 0.0,
                        "float_timer": 0.0
                    }
                    if len(self.beams) < max_beams:
                        self.beams.append(new_b)
                        assigned_targets.add(active_meteorite)
                    elif self.beams:
                        self.beams[0] = new_b
                        assigned_targets.add(active_meteorite)

            # 3. Находим новые цели для свободных слотов лучей
            if len(self.beams) < max_beams:
                in_range = []
                for enemy in enemies:
                    if enemy.active and enemy not in assigned_targets and getattr(enemy, "health", 0) > 0:
                        d_e = math.hypot(self.x - enemy.x, self.y - enemy.y)
                        if d_e <= self.range:
                            in_range.append((enemy, d_e))

                if in_range:
                    if self.target_priority == "FIRST":
                        in_range.sort(key=lambda p: p[0].progress, reverse=True)
                    elif self.target_priority == "LAST":
                        in_range.sort(key=lambda p: p[0].progress)
                    elif self.target_priority == "STRONGEST":
                        in_range.sort(key=lambda p: p[0].health, reverse=True)
                    elif self.target_priority == "WEAKEST":
                        in_range.sort(key=lambda p: p[0].health)
                    elif self.target_priority == "CLOSEST":
                        in_range.sort(key=lambda p: p[1])

                    needed = max_beams - len(self.beams)
                    for candidate, _ in in_range[:needed]:
                        self.beams.append({
                            "target": candidate,
                            "multiplier": 0.5,
                            "tick_timer": 0.0,
                            "accum_dmg": 0.0,
                            "float_timer": 0.0
                        })
                        assigned_targets.add(candidate)

                # Если остались свободные лучи и врагов в радиусе нет — направляем оставшийся луч на метеорит!
                if len(self.beams) < max_beams and can_target_meteor and active_meteorite not in assigned_targets:
                    d_met = math.hypot(self.x - active_meteorite.x, self.y - active_meteorite.y)
                    if d_met <= self.range * 1.25:
                        self.beams.append({
                            "target": active_meteorite,
                            "multiplier": 0.5,
                            "tick_timer": 0.0,
                            "accum_dmg": 0.0,
                            "float_timer": 0.0
                        })
                        assigned_targets.add(active_meteorite)

            # 4. Обновляем урон и плавающий текст по каждому лучу
            active_beams_after_tick = []
            for b in self.beams:
                tgt = b["target"]
                b["multiplier"] = min(max_m, b["multiplier"] + (1.0 / max(0.1, ramp_t)) * eff_dt)
                b["tick_timer"] += eff_dt
                b["float_timer"] += eff_dt

                if b["tick_timer"] >= 0.10:
                    b["tick_timer"] -= 0.10
                    tick_dmg = round(self.damage * b["multiplier"], 2)
                    tgt_max_hp = getattr(tgt, "max_health", getattr(tgt, "health", getattr(tgt, "hp", 1.0)))
                    tgt.take_damage(tick_dmg, damage_type="sun")
                    self.record_damage(tick_dmg)
                    b["accum_dmg"] += tick_dmg

                tgt_cur_hp = getattr(tgt, "health", getattr(tgt, "hp", 0))
                target_dead = (not getattr(tgt, "active", False)) or (tgt_cur_hp <= 0)
                if b["float_timer"] >= 0.20 or target_dead:
                    if effects is not None and b["accum_dmg"] > 0:
                        if b["multiplier"] >= 3.0:
                            t_col = (255, 95, 25)   # Сверхнагрев (плазма)
                        elif b["multiplier"] >= 1.5:
                            t_col = (255, 185, 35)  # Нагретый луч
                        else:
                            t_col = (255, 235, 100) # Базовый луч
                        effects.append(FloatingText(tgt.x, tgt.y - 14, f"-{round(b['accum_dmg'], 1):g}", t_col))
                    b["accum_dmg"] = 0.0
                    b["float_timer"] = 0.0

                if target_dead:
                    if solar_trail_lvl > 0:
                        pct = solar_trail_lvl * 0.025
                        explode_dmg = round(tgt_max_hp * pct, 1)
                        if explode_dmg > 0:
                            for other in enemies:
                                if other.active and other != tgt:
                                    if math.hypot(tgt.x - other.x, tgt.y - other.y) <= 50:
                                        other.take_damage(explode_dmg, damage_type="sun_aoe")
                                        self.record_damage(explode_dmg)
                            if effects is not None:
                                effects.append(RingEffect(tgt.x, tgt.y, 50, (255, 200, 50)))
                                effects.append(FloatingText(tgt.x, tgt.y - 16, f"ВСПЫШКА -{explode_dmg:g}", (255, 230, 100)))
                else:
                    active_beams_after_tick.append(b)

            self.beams = active_beams_after_tick
            self.current_beam_target = self.beams[0]["target"] if self.beams else None
            return 0

        # Метеорит: атака метеорита башнями
        # 1) Если игрок выбрал метеорит целью — атакуем в приоритете (радиус x1.25)
        # 2) Если нет врагов в радиусе атаки башни — башня автоматически атакует метеорит!
        has_enemies_in_range = False
        if enemies:
            for enemy in enemies:
                if enemy.active and math.hypot(self.x - enemy.x, self.y - enemy.y) <= self.range:
                    has_enemies_in_range = True
                    break

        meteor_in_reach = active_meteorite and getattr(active_meteorite, "active", False) and (getattr(active_meteorite, "hp", 0) > 0)
        should_shoot_meteor = False
        if meteor_in_reach and self.type != "tent":
            d_met = math.hypot(self.x - active_meteorite.x, self.y - active_meteorite.y)
            if active_meteorite.targeted and d_met <= self.range * 1.25:
                should_shoot_meteor = True
            elif not has_enemies_in_range and d_met <= self.range * 1.25:
                should_shoot_meteor = True

        if should_shoot_meteor:
            if self.timer >= self.cooldown:
                self.timer = 0.0
                actual_damage = round(self.damage, 1)
                if self.type == "magic":
                    projectiles.append(MagicBullet(self.x, self.y - 18, active_meteorite, actual_damage, self))
                elif self.type == "rock":
                    projectiles.append(RockBullet(self.x, self.y, active_meteorite.x, active_meteorite.y, actual_damage, self.splash_radius, self))
                elif self.type == "freeze":
                    projectiles.append(FrostBullet(self.x, self.y - 15, active_meteorite, actual_damage, self.range, self.slow_ratio, self.slow_duration, self))
                elif self.type == "tesla":
                    active_meteorite.take_damage(actual_damage, damage_type="lightning")
                    self.record_damage(actual_damage)
                    if effects is not None:
                        effects.append(FloatingText(active_meteorite.x, active_meteorite.y - 12, f"-{actual_damage:g}", (90, 225, 255)))
                        effects.append(LightningEffect([(self.x, self.y - 18), (active_meteorite.x, active_meteorite.y)]))
                    sfx_tesla.play()
            return 0

        if self.type == "tent":
            if self.rally_point is None:
                if self.target_path_point is not None:
                    self.rally_point = (float(self.target_path_point[0]), float(self.target_path_point[1]))
                else:
                    if path and len(path) >= 2:
                        rx, ry, best_idx, _ = get_nearest_point_on_road(self.x, self.y, path)
                    elif path and len(path) == 1:
                        rx, ry, best_idx = float(path[0][0]), float(path[0][1]), 0
                    else:
                        rx, ry, best_idx = float(self.x), float(self.y), 0
                    self.target_path_point = (float(rx), float(ry), best_idx)
                    self.rally_point = (float(rx), float(ry))

            self.soldiers = [s for s in self.soldiers if s.active]
            if len(self.soldiers) >= self.max_soldiers:
                self.timer = min(self.timer, self.cooldown)

            if self.timer >= self.cooldown and len(self.soldiers) < self.max_soldiers and self.rally_point:
                self.timer = 0.0
                rx, ry = self.rally_point
                pidx = self.target_path_point[2] if self.target_path_point else 0
                offsets = self._get_soldier_formation_offsets(len(self.soldiers) + 1)
                assigned_offset = offsets[len(self.soldiers)] if len(self.soldiers) < len(offsets) else (0, 0)
                target_x = rx + assigned_offset[0]
                target_y = ry + assigned_offset[1]
                spawn_x = self.x
                spawn_y = self.y + 6
                self.soldiers.append(Soldier(spawn_x, spawn_y, pidx, self, target_x=target_x, target_y=target_y))

            for s in self.soldiers:
                s.update(dt, enemies, effects)
            return

        if self.timer < self.cooldown:
            return

        in_range_enemies = []
        for enemy in enemies:
            if not enemy.active: continue
            d = math.hypot(self.x - enemy.x, self.y - enemy.y)
            if d <= self.range:
                in_range_enemies.append((enemy, d))

        if not in_range_enemies:
            return

        # Талант «Элементный Фокус»: тактическая синергия льда и огня
        ef_lvl = savedata.get("Upgrades", {}).get("elemental_focus", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
        ef_active = savedata.get("Toggles", {}).get("elemental_focus", True) if 'savedata' in globals() and isinstance(savedata, dict) else True
        candidate_pool = in_range_enemies
        if ef_lvl > 0 and ef_active:
            if self.type == "freeze":
                # Морозная башня бьёт по ещё НЕ замедленным врагам
                unfrozen = [pair for pair in in_range_enemies if not pair[0].is_frozen()]
                if unfrozen:
                    candidate_pool = unfrozen
            elif self.type == "rock":
                # Огненная башня бьёт по замороженным врагам (100% КРИТЫ!)
                frozen = [pair for pair in in_range_enemies if pair[0].is_frozen()]
                if frozen:
                    candidate_pool = frozen

        if self.target_priority == "FIRST":
            target = max(candidate_pool, key=lambda pair: pair[0].progress)[0]
        elif self.target_priority == "LAST":
            target = min(candidate_pool, key=lambda pair: pair[0].progress)[0]
        elif self.target_priority == "STRONGEST":
            target = max(candidate_pool, key=lambda pair: pair[0].health)[0]
        elif self.target_priority == "WEAKEST":
            target = min(candidate_pool, key=lambda pair: pair[0].health)[0]
        elif self.target_priority == "CLOSEST":
            target = min(candidate_pool, key=lambda pair: pair[1])[0]
        else:
            target = candidate_pool[0][0]

        if target:
            self.timer = 0.0
            st_lvl = savedata.get("Upgrades", {}).get("smart_targeting", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
            dmg_mult = 1.10 if (st_lvl >= 2 and self.target_priority == "STRONGEST") else 1.0
            actual_damage = round(self.damage * dmg_mult, 1)

            if self.type == "magic":
                projectiles.append(MagicBullet(self.x, self.y - 18, target, actual_damage, self))
            elif self.type == "rock":
                projectiles.append(RockBullet(self.x, self.y, target.x, target.y, actual_damage, self.splash_radius, self))
            elif self.type == "freeze":
                projectiles.append(FrostBullet(self.x, self.y - 15, target, actual_damage, self.range, self.slow_ratio, self.slow_duration, self))
            elif self.type == "tesla":
                hit_enemies = [target]
                target.take_damage(actual_damage, damage_type="lightning")
                self.record_damage(actual_damage)
                if effects is not None:
                    effects.append(FloatingText(target.x, target.y - 12, f"-{actual_damage:g}", (90, 225, 255)))

                chain_pts = [(self.x, self.y - 18), (target.x, target.y)]
                cur_target = target
                max_chain_d = 110 if getattr(self, "game_map", 0) == 4 else 95
                supercond_lvl = savedata.get("Upgrades", {}).get("superconductor", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0
                retention = [0.65, 0.75, 0.82, 0.90][min(3, supercond_lvl)]
                jump_count = 0
                for _ in range(self.max_chains - 1):
                    next_target = None
                    min_chain_d = float('inf')
                    for other in enemies:
                        if other.active and other not in hit_enemies:
                            d_other = math.hypot(cur_target.x - other.x, cur_target.y - other.y)
                            if d_other <= max_chain_d and d_other < min_chain_d:
                                min_chain_d = d_other
                                next_target = other
                    if next_target:
                        jump_count += 1
                        chain_dmg = round(actual_damage * (retention ** jump_count), 1)
                        hit_enemies.append(next_target)
                        next_target.take_damage(chain_dmg, damage_type="lightning")
                        self.record_damage(chain_dmg)
                        chain_pts.append((next_target.x, next_target.y))
                        if effects is not None:
                            effects.append(FloatingText(next_target.x, next_target.y - 12, f"-{chain_dmg:g}", (90, 225, 255)))
                        cur_target = next_target
                    else:
                        break

                if effects is not None:
                    effects.append(LightningEffect(chain_pts, (90, 225, 255)))
                sfx_tesla.play()

    def draw(self, surface, hovered=False, upgrade_mode=False, show_rally_flag=False):
        # Каменный постамент под башней
        surface.blit(slot_img, (self.x - 22, self.y - 14))

        # Визуальная эволюция на высоких уровнях (5+ и 10+)
        ticks = pygame.time.get_ticks()
        if self.level >= 5:
            aura_cols = {
                "magic": (190, 70, 245),
                "rock": (255, 120, 30),
                "freeze": (70, 215, 255),
                "tent": (80, 225, 95),
                "tesla": (90, 225, 255),
                "farm": (245, 210, 40)
            }
            acol = aura_cols.get(self.type, (255, 215, 80))
            p_rad = 24 + int(math.sin(ticks * 0.006) * 3)
            pygame.draw.circle(surface, (*acol, 90), (int(self.x), int(self.y + 8)), p_rad, width=2)

        front_orbs = []
        if self.level >= 10:
            orb_cols = {
                "magic": (220, 110, 255),
                "rock": (255, 170, 40),
                "freeze": (130, 240, 255),
                "tent": (130, 255, 140),
                "tesla": (140, 240, 255),
                "farm": (255, 230, 120)
            }
            ocol = orb_cols.get(self.type, (255, 230, 120))
            orb_angle = ticks * 0.0035
            for oi in range(3):
                ang = orb_angle + oi * (2 * math.pi / 3)
                sin_v = math.sin(ang)
                ox = int(self.x + math.cos(ang) * 28)
                oy = int((self.y - 10) + sin_v * 12)
                if sin_v < 0:
                    # Задняя половина орбиты — рисуем ЗА башней
                    pygame.draw.circle(surface, ocol, (ox, oy), 3)
                    pygame.draw.circle(surface, (230, 230, 230), (ox, oy), 1)
                else:
                    # Передняя половина орбиты — отрисуем ПЕРЕД башней
                    front_orbs.append((ox, oy, ocol))

        # Отрисовка самой башни
        surface.blit(self.image, self.rect)

        # Передняя половина орбиты (вращается ПЕРЕД башней, создавая честный 3D-эффект)
        for ox, oy, ocol in front_orbs:
            if get_graphics_preset() != "optimized":
                glow_surf = get_cached_orb_glow(ocol)
                surface.blit(glow_surf, (ox - 9, oy - 9))
            pygame.draw.circle(surface, ocol, (ox, oy), 5)
            pygame.draw.circle(surface, (255, 255, 255), (ox - 1, oy - 1), 2)

        if self.type == "sun":
            sun_y = self.y - 28 + math.sin(ticks * 0.005) * 2
            s_ang = ticks * 0.002
            for ray_i in range(6):
                ra = s_ang + ray_i * (math.pi / 3)
                rx1 = self.x + math.cos(ra) * 7
                ry1 = sun_y + math.sin(ra) * 7
                rx2 = self.x + math.cos(ra) * 13
                ry2 = sun_y + math.sin(ra) * 13
                pygame.draw.line(surface, (255, 220, 80), (int(rx1), int(ry1)), (int(rx2), int(ry2)), 2)
            pygame.draw.circle(surface, (255, 190, 40), (int(self.x), int(sun_y)), 9)
            pygame.draw.circle(surface, (255, 245, 140), (int(self.x), int(sun_y)), 6)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(sun_y)), 3)

            beams_to_draw = getattr(self, "beams", [])
            if not beams_to_draw:
                cur_t = getattr(self, "current_beam_target", None)
                if cur_t and getattr(cur_t, "active", False):
                    beams_to_draw = [{"target": cur_t, "multiplier": getattr(self, "beam_multiplier", 0.5)}]

            for b in beams_to_draw:
                tgt = b.get("target")
                if tgt and getattr(tgt, "active", False):
                    b_mult = b.get("multiplier", 0.5)
                    tx, ty = int(tgt.x), int(tgt.y)
                    sx, sy = int(self.x), int(sun_y)
                    glow_w = max(4, int(3 + b_mult * 2.2))
                    core_w = max(2, int(1 + b_mult * 1.2))
                    pygame.draw.line(surface, (255, 170, 30), (sx, sy), (tx, ty), glow_w)
                    pygame.draw.line(surface, (255, 240, 160), (sx, sy), (tx, ty), core_w)
                    pygame.draw.line(surface, WHITE, (sx, sy), (tx, ty), 1)
                    pygame.draw.circle(surface, (255, 210, 60), (tx, ty), max(4, int(3 + b_mult * 1.5)))
                    pygame.draw.circle(surface, WHITE, (tx, ty), max(2, int(1 + b_mult)))

        # Бейдж уровня башни (кэшируем текст уровня, для Солнца поднимаем выше сияния)
        lvl_y = self.y - 50 if self.type == "sun" else self.y - 34
        lvl_badge = pygame.Rect(self.x - 16, lvl_y, 32, 16)
        pygame.draw.rect(surface, (20, 30, 20), lvl_badge, border_radius=4)
        pygame.draw.rect(surface, GOLD if self.level >= self.max_level else GREEN, lvl_badge, width=1, border_radius=4)
        if getattr(self, "_cached_lvl_key", None) != self.level or not hasattr(self, "_cached_lvl_text"):
            self._cached_lvl_key = self.level
            self._cached_lvl_text = tiny_font.render(f"L{self.level}", True, WHITE)
        upg_text = self._cached_lvl_text
        surface.blit(upg_text, (lvl_badge.centerx - upg_text.get_width() // 2, lvl_badge.centery - upg_text.get_height() // 2))

        # Визуальный эффект ледяной глыбы при заморозке башни
        if getattr(self, "freeze_disabled_timer", 0.0) > 0.0:
            ice_s = pygame.Surface((56, 56), pygame.SRCALPHA)
            ice_s.fill((90, 215, 255, 110))
            pygame.draw.rect(ice_s, (220, 250, 255, 220), (0, 0, 56, 56), width=2, border_radius=6)
            surface.blit(ice_s, (int(self.x - 28), int(self.y - 28)))
            ice_txt = tiny_font.render(f"ЛЁД {self.freeze_disabled_timer:.1f}с", True, CYAN)
            surface.blit(ice_txt, (int(self.x - ice_txt.get_width() // 2), int(self.y - 42)))

        if self.type == "tent":
            for s in self.soldiers:
                s.draw(surface)
            is_active = (hovered or getattr(self, "_rally_selecting", False) or getattr(self, "_is_inspected", False) or getattr(self, "_is_rally_targeting", False))
            if show_rally_flag or is_active:
                rp = getattr(self, "rally_point", None)
                if rp is None and self.target_path_point:
                    rp = (self.target_path_point[0], self.target_path_point[1])
                if rp:
                    rx, ry = int(rp[0]), int(rp[1])
                    if is_active:
                        pygame.draw.line(surface, (70, 210, 120), (self.x, self.y), (rx, ry), 2)
                    draw_rally_flag(surface, rx, ry, active=is_active)

        if hovered and self.range > 0:
            rx, ry, rr = int(self.x), int(self.y), int(self.range)
            col = (60, 240, 100, 45) if not upgrade_mode else (255, 140, 40, 55)
            bcol = (40, 180, 70, 170) if not upgrade_mode else (255, 140, 30, 190)
            r_surf = get_cached_range_surf(rr, col, bcol, 2)
            if r_surf:
                surface.blit(r_surf, (rx - rr, ry - rr))

            # В режиме улучшений показываем круг будущего радиуса с полупрозрачной заливкой
            if upgrade_mode and self.level < self.max_level:
                nxt_rng = getattr(self, "_cached_nxt_range", None)
                if nxt_rng is None or getattr(self, "_cached_nxt_range_lvl", None) != self.level:
                    nxt_s = self.get_stats_at_level(self.level + 1)
                    nxt_rng = int(nxt_s.get("range", self.range))
                    self._cached_nxt_range = nxt_rng
                    self._cached_nxt_range_lvl = self.level
                if nxt_rng > self.range:
                    nxt_col = (255, 200, 50, 30)
                    nxt_bcol = (255, 200, 50, 150)
                    nxt_surf = get_cached_range_surf(nxt_rng, nxt_col, nxt_bcol, 1)
                    if nxt_surf:
                        surface.blit(nxt_surf, (rx - nxt_rng, ry - nxt_rng))


# -------------------------------------------------------------------------
# СНАРЯДЫ И ЭФФЕКТЫ
# -------------------------------------------------------------------------
class MagicBullet:
    def __init__(self, x, y, target, damage, source_tower=None):
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.speed = 340.0
        self.damage = damage
        self.source_tower = source_tower
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.active = True
        self.trail = []
        laser.play()

    def update(self, dt, enemies, effects, active_meteorite=None, **kwargs):
        if not self.target.active:
            valid_targets = [e for e in enemies if e.active and not getattr(e, 'is_cloaked', False)]
            if valid_targets:
                self.target = min(valid_targets, key=lambda e: math.hypot(e.x - self.x, e.y - self.y))
            else:
                self.active = False
                return
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8: self.trail.pop(0)

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        step = self.speed * dt

        if dist <= step or dist < 8:
            is_crit = False
            crit_chance = getattr(self.source_tower, 'crit_chance', 5) if self.source_tower else 5
            if random.random() * 100 < crit_chance:
                is_crit = True
            crit_mult = getattr(self.source_tower, 'crit_mult', 2.0) if self.source_tower else 2.0
            dmg_to_deal = round(self.damage * (crit_mult if is_crit else 1.0), 1)
            self.target.take_damage(dmg_to_deal, damage_type="magic")

            actual_dmg = dmg_to_deal
            if getattr(self.target, 'magic_resist', 0.0) > 0:
                actual_dmg = round(dmg_to_deal * (1.0 - self.target.magic_resist), 1)

            if self.source_tower:
                self.source_tower.record_damage(actual_dmg)

            if is_crit:
                savedata.setdefault("Stats", {})["total_crits"] = savedata.get("Stats", {}).get("total_crits", 0) + 1
                effects.append(FloatingText(self.target.x, self.target.y - 14, f"-{actual_dmg:g} CRIT!", (240, 110, 255), is_crit=True))
                sfx_combo.play()
            else:
                color = (195, 155, 230) if getattr(self.target, 'magic_resist', 0.0) > 0 else (235, 175, 255)
                effects.append(FloatingText(self.target.x, self.target.y - 12, f"-{actual_dmg:g}", color))
            self.active = False
        else:
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step
            self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            alpha = int(220 * (i / max(1, len(self.trail))))
            rad = max(1, int(4 * (i / max(1, len(self.trail)))))
            s = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (180, 80, 240, alpha), (rad, rad), rad)
            surface.blit(s, (int(pos[0] - rad), int(pos[1] - rad)))
        surface.blit(self.image, self.rect)


class RockBullet:
    def __init__(self, x, y, target_x, target_y, damage, splash_radius, source_tower=None):
        self.x = float(x)
        self.y = float(y)
        self.target_x = float(target_x)
        self.target_y = float(target_y)
        self.speed = 320.0
        self.damage = damage
        self.splash_radius = splash_radius
        self.source_tower = source_tower
        self.image = earth_ball_img
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.active = True
        self.trail = []
        sfx_mortar_shot.play()

    def update(self, dt, enemies, effects, active_meteorite=None, **kwargs):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8: self.trail.pop(0)

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        step = self.speed * dt

        if dist <= step or dist < 10:
            had_crit = False
            meteor_lvl = savedata.get("Upgrades", {}).get("meteor_strike", 0) if 'savedata' in globals() and isinstance(savedata, dict) else 0

            # Урон по метеориту, если он в зоне сплэша
            if active_meteorite and getattr(active_meteorite, "active", False) and (getattr(active_meteorite, "hp", 0) > 0):
                mdist = math.hypot(self.x - active_meteorite.x, self.y - active_meteorite.y)
                if mdist <= self.splash_radius:
                    actual_dmg = round(self.damage, 1)
                    active_meteorite.take_damage(actual_dmg, damage_type="rock")
                    if self.source_tower:
                        self.source_tower.record_damage(actual_dmg)
                    effects.append(FloatingText(active_meteorite.x, active_meteorite.y - 12, f"-{actual_dmg:g}", (255, 175, 75)))

            for enemy in enemies:
                if enemy.active:
                    edist = math.hypot(self.x - enemy.x, self.y - enemy.y)
                    if edist <= self.splash_radius:
                        is_crit = enemy.is_frozen()
                        frozen_mult = getattr(self.source_tower, 'frozen_multiplier', 1.75) if self.source_tower else 1.75
                        multiplier = frozen_mult if is_crit else 1.0
                        if meteor_lvl > 0 and edist <= self.splash_radius * 0.55:
                            multiplier *= (1.0 + meteor_lvl * 0.30)
                        actual_dmg = round(self.damage * multiplier, 1)
                        enemy.take_damage(actual_dmg, damage_type="rock")
                        if self.source_tower:
                            self.source_tower.record_damage(actual_dmg)
                        if is_crit:
                            had_crit = True
                            savedata.setdefault("Stats", {})["total_crits"] = savedata.get("Stats", {}).get("total_crits", 0) + 1
                            effects.append(FloatingText(enemy.x, enemy.y - 14, f"-{actual_dmg:g} CRIT!", GOLD, is_crit=True))
                        else:
                            effects.append(FloatingText(enemy.x, enemy.y - 10, f"-{actual_dmg:g}", (255, 175, 75)))
            if had_crit:
                sfx_combo.play()
            self.active = False
            effects.append(SplashEffect(self.x, self.y, self.splash_radius, (255, 120, 20)))
        else:
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step
            self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            alpha = int(200 * (i / max(1, len(self.trail))))
            rad = max(1, int(4 * (i / max(1, len(self.trail)))))
            s = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 140, 20, alpha), (rad, rad), rad)
            surface.blit(s, (int(pos[0] - rad), int(pos[1] - rad)))
        surface.blit(self.image, self.rect)


class FrostBullet:
    def __init__(self, x, y, target, damage, tower_range, slow_ratio, slow_duration, source_tower=None):
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.speed = 280.0
        self.damage = damage
        self.slow_ratio = slow_ratio
        self.slow_duration = slow_duration
        self.splash_radius = 45
        self.source_tower = source_tower
        self.image = frost_ball_img
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.active = True
        self.trail = []
        sfx_freeze_shot.play()

    def update(self, dt, enemies, effects, active_meteorite=None, **kwargs):
        if not self.target.active:
            valid_targets = [e for e in enemies if e.active and not getattr(e, 'is_cloaked', False)]
            if valid_targets:
                self.target = min(valid_targets, key=lambda e: math.hypot(e.x - self.x, e.y - self.y))
            else:
                self.active = False
                return
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8: self.trail.pop(0)

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        step = self.speed * dt

        if dist <= step or dist < 10:
            if active_meteorite and getattr(active_meteorite, "active", False) and (getattr(active_meteorite, "hp", 0) > 0):
                mdist = math.hypot(self.x - active_meteorite.x, self.y - active_meteorite.y)
                if mdist <= self.splash_radius:
                    active_meteorite.take_damage(self.damage, damage_type="freeze")
                    if self.source_tower:
                        self.source_tower.record_damage(self.damage)
                    effects.append(FloatingText(active_meteorite.x, active_meteorite.y - 10, f"-{self.damage:g}", CYAN))

            for enemy in enemies:
                if enemy.active:
                    edist = math.hypot(self.x - enemy.x, self.y - enemy.y)
                    if edist <= self.splash_radius:
                        enemy.take_damage(self.damage, damage_type="freeze")
                        enemy.apply_freeze(self.slow_ratio, self.slow_duration)
                        if self.source_tower:
                            self.source_tower.record_damage(self.damage)
                        effects.append(FloatingText(enemy.x, enemy.y - 10, f"-{self.damage:g}", CYAN))
            self.active = False
            effects.append(SplashEffect(self.x, self.y, self.splash_radius, (70, 200, 255)))
        else:
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step
            self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            alpha = int(220 * (i / max(1, len(self.trail))))
            rad = max(1, int(4 * (i / max(1, len(self.trail)))))
            s = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (140, 230, 255, alpha), (rad, rad), rad)
            surface.blit(s, (int(pos[0] - rad), int(pos[1] - rad)))
        surface.blit(self.image, self.rect)


class SplashEffect:
    def __init__(self, x, y, max_radius, color):
        self.x = int(x)
        self.y = int(y)
        self.max_radius = max_radius
        self.color = color
        self.life = 0.25
        self.max_life = 0.25

    def update(self, dt=0.016):
        if dt is None: dt = 0.016
        self.life -= dt
        return self.life <= 0

    def draw(self, surface):
        if self.life <= 0: return
        progress = 1.0 - (self.life / self.max_life)
        cur_rad = int(self.max_radius * progress)
        alpha = int(220 * (1.0 - progress))
        if cur_rad > 0:
            s = pygame.Surface((cur_rad * 2, cur_rad * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (cur_rad, cur_rad), cur_rad, width=3)
            surface.blit(s, (self.x - cur_rad, self.y - cur_rad))

RingEffect = SplashEffect


class JellyDroplet:
    """Летящая желейная капля при лопании слайма."""
    def __init__(self, x, y, color, speed=None, angle=None):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        ang = random.uniform(0, math.pi * 2) if angle is None else angle
        spd = random.uniform(45.0, 135.0) if speed is None else speed
        self.vx = math.cos(ang) * spd
        self.vy = math.sin(ang) * spd
        self.life = random.uniform(0.35, 0.55)
        self.max_life = self.life
        self.radius = random.uniform(2.5, 4.5)

    def update(self, dt=0.016):
        if dt is None: dt = 0.016
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 120.0 * dt  # легкая гравитация
        self.vx *= (1.0 - 1.8 * dt)  # сопротивление воздуха
        return self.life <= 0

    def draw(self, surface):
        if self.life <= 0: return
        progress = max(0.0, min(1.0, self.life / self.max_life))
        r = max(1, int(self.radius * progress))
        alpha = int(220 * progress)
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (r + 1, r + 1), r)
        if r >= 2:
            pygame.draw.circle(s, (255, 255, 255, int(alpha * 0.7)), (r, r - 1), max(1, r // 2))
        surface.blit(s, (int(self.x - r), int(self.y - r)))


class SlimeSplat:
    """Желейное пятно-клякса на земле от лопнувшего слайма."""
    def __init__(self, x, y, color, size=16):
        self.x = int(x)
        self.y = int(y)
        self.color = color
        self.size = size
        self.life = 3.2
        self.max_life = 3.2
        self.satellites = []
        num_sat = random.randint(2, 4)
        for _ in range(num_sat):
            ang = random.uniform(0, math.pi * 2)
            dist = random.uniform(size * 0.45, size * 0.95)
            sr = random.randint(max(2, size // 6), max(3, size // 3))
            self.satellites.append((math.cos(ang) * dist, math.sin(ang) * dist, sr))

    def update(self, dt=0.016):
        if dt is None: dt = 0.016
        self.life -= dt
        return self.life <= 0

    def draw(self, surface):
        if self.life <= 0: return
        ratio = max(0.0, min(1.0, self.life / self.max_life))
        alpha = int(140 * min(1.0, ratio * 1.5))
        if alpha <= 0: return

        surf_sz = int(self.size * 2.6)
        splat_surf = pygame.Surface((surf_sz, surf_sz), pygame.SRCALPHA)
        scx, scy = surf_sz // 2, surf_sz // 2

        main_w = int(self.size * (0.8 + 0.2 * ratio))
        main_h = int(self.size * 0.55 * (0.8 + 0.2 * ratio))
        pygame.draw.ellipse(splat_surf, (*self.color, alpha), (scx - main_w, scy - main_h, main_w * 2, main_h * 2))

        hi_w = max(1, main_w // 2)
        hi_h = max(1, main_h // 2)
        pygame.draw.ellipse(splat_surf, (255, 255, 255, int(alpha * 0.45)), (scx - hi_w, scy - hi_h - 1, hi_w * 2, hi_h * 2))

        for ox, oy, sr in self.satellites:
            c_r = max(1, int(sr * ratio))
            pygame.draw.circle(splat_surf, (*self.color, int(alpha * 0.85)), (int(scx + ox), int(scy + oy)), c_r)

        surface.blit(splat_surf, (self.x - scx, self.y - scy))


class LightningEffect:
    def __init__(self, points, color=(100, 225, 255)):
        self.points = points
        self.color = color
        self.life = 0.22
        self.max_life = 0.22
        self.segments = []
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            steps = max(2, int(dist / 14))
            seg = [p1]
            for s in range(1, steps):
                t = s / steps
                bx = p1[0] + (p2[0] - p1[0]) * t + random.uniform(-6, 6)
                by = p1[1] + (p2[1] - p1[1]) * t + random.uniform(-6, 6)
                seg.append((bx, by))
            seg.append(p2)
            self.segments.append(seg)

    def update(self, dt=0.016):
        if dt is None: dt = 0.016
        self.life -= dt
        return self.life <= 0

    def draw(self, surface):
        if self.life <= 0: return
        for seg in self.segments:
            if len(seg) > 1:
                pygame.draw.lines(surface, self.color, False, seg, 4)
                pygame.draw.lines(surface, (255, 255, 255), False, seg, 2)


class FloatingText:
    def __init__(self, x, y, text, color, life=0.85, is_crit=False):
        self.x = float(x) + random.uniform(-6, 6)
        self.y = float(y)
        self.text = str(text)
        self.color = color
        self.life = life
        self.max_life = life
        self.vy = -40.0 if is_crit else -28.0
        self.is_crit = is_crit

    def update(self, dt=0.016):
        if dt is None: dt = 0.016
        self.y += self.vy * dt
        self.life -= dt
        return self.life <= 0

    def draw(self, surface):
        if self.life <= 0: return
        ratio = max(0.0, min(1.0, self.life / self.max_life))
        alpha = int(255 * ratio)
        used_font = font if self.is_crit else small_font
        txt_surf = used_font.render(self.text, True, self.color)
        if alpha < 250:
            txt_surf.set_alpha(alpha)
        # Тень для контраста на любом фоне
        sh_surf = used_font.render(self.text, True, (0, 0, 0))
        sh_surf.set_alpha(int(alpha * 0.7))
        cx = int(self.x - txt_surf.get_width() // 2)
        cy = int(self.y - txt_surf.get_height() // 2)
        surface.blit(sh_surf, (cx + 1, cy + 1))
        surface.blit(txt_surf, (cx, cy))


# -------------------------------------------------------------------------
# АСТРАЛЬНЫЕ МЕХАНИКИ: МЕТЕОРИТ, ДРОН И ОРБИТАЛЬНЫЙ УДАР
# -------------------------------------------------------------------------
class AstralMeteorite:
    def __init__(self, arg1, arg2=None, arg3=None, game_map=0):
        if arg2 is None and arg3 is None:
            self.wave = arg1
            self.x = 640.0
            self.y = 330.0
            self.game_map = game_map
        elif arg3 is None:
            self.x = float(arg1)
            self.y = float(arg2)
            self.wave = 12
            self.game_map = game_map
        else:
            self.x = float(arg1)
            self.y = float(arg2)
            self.wave = arg3
            self.game_map = game_map
        hp_mod = calculate_hp_modificator(self.wave)
        biome = MAP_BIOMES_DATA.get(self.game_map, {})
        hp_mult = biome.get("hp_mult", 1.0)
        diff = savedata.get("difficulty", "normal") if 'savedata' in globals() and isinstance(savedata, dict) else "normal"
        diff_hp = 0.75 if diff == "casual" else (2.0 if diff == "hardcore" else 1.0)
        self.max_hp = float(max(200, int(200.0 * hp_mod * hp_mult * diff_hp)))
        self.hp = self.max_hp
        self.targeted = False
        self.radius = 26
        self.active = True
        self.pulse = 0.0
        self.fall_anim = 1.0

    @property
    def health(self):
        return self.hp

    @health.setter
    def health(self, val):
        self.hp = val

    @property
    def max_health(self):
        return self.max_hp

    @max_health.setter
    def max_health(self, val):
        self.max_hp = val

    def take_damage(self, amount, damage_type="normal", *args, **kwargs):
        self.hp -= amount
        effects = kwargs.get("effects")
        if effects is None and len(args) > 0 and isinstance(args[0], list):
            effects = args[0]
        elif isinstance(damage_type, list):
            effects = damage_type
            damage_type = "normal"
        if effects is not None:
            effects.append(FloatingText(self.x + random.uniform(-10, 10), self.y - 15, f"-{int(amount)}", (235, 100, 255)))
            effects.append(RingEffect(self.x, self.y, 35, (190, 60, 255)))
        if self.hp <= 0:
            self.hp = 0
            self.active = False
            return True
        return False

    def update(self, dt, effects=None):
        self.pulse += dt * 4.0
        if self.fall_anim > 0.0:
            self.fall_anim = max(0.0, self.fall_anim - dt * 2.5)

    def draw(self, surface):
        if not self.active: return
        cur_y = self.y - (400.0 * (self.fall_anim ** 2))
        center = (int(self.x), int(cur_y))

        glow_alpha = int(120 + 50 * math.sin(self.pulse))
        glow_r = int(self.radius + 12 + 4 * math.sin(self.pulse * 1.5))
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        col = (190, 60, 255, min(255, max(0, glow_alpha // 3))) if not self.targeted else (255, 60, 70, min(255, max(0, glow_alpha // 2)))
        pygame.draw.circle(glow_surf, col, (glow_r, glow_r), glow_r)
        surface.blit(glow_surf, (center[0] - glow_r, center[1] - glow_r))

        surface.blit(meteorite_img, (center[0] - 26, center[1] - 26))

        if self.targeted:
            tgt_color = (255, 60, 70)
            pygame.draw.circle(surface, tgt_color, center, self.radius + 6, width=2)
            pygame.draw.line(surface, tgt_color, (center[0] - self.radius - 10, center[1]), (center[0] + self.radius + 10, center[1]), 2)
            pygame.draw.line(surface, tgt_color, (center[0], center[1] - self.radius - 10), (center[0], center[1] + self.radius + 10), 2)
            lbl = tiny_font.render("[ЦЕЛЬ: ОГОНЬ!]", True, (255, 90, 90))
            surface.blit(lbl, (center[0] - lbl.get_width() // 2, center[1] - self.radius - 26))
        else:
            lbl = tiny_font.render("[КЛИК: АТАКА]", True, (235, 195, 255))
            surface.blit(lbl, (center[0] - lbl.get_width() // 2, center[1] - self.radius - 22))

        bw, bh = 64, 7
        bx, by = center[0] - bw // 2, center[1] + self.radius + 6
        pygame.draw.rect(surface, (20, 15, 30), (bx, by, bw, bh), border_radius=3)
        fill_w = max(0, int(bw * (self.hp / self.max_hp)))
        hp_col = (195, 75, 255) if not self.targeted else (255, 80, 80)
        pygame.draw.rect(surface, hp_col, (bx, by, fill_w, bh), border_radius=3)
        pygame.draw.rect(surface, (90, 60, 120), (bx, by, bw, bh), width=1, border_radius=3)

        hp_txt = tiny_font.render(f"{int(self.hp)}/{int(self.max_hp)}", True, WHITE)
        surface.blit(hp_txt, (center[0] - hp_txt.get_width() // 2, by + bh + 1))


class CactusDrone:
    def __init__(self, level):
        self.level = level
        self.angle = 0.0
        self.shoot_timer = 0.0
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2 - 40
        self.radius_x = 380.0
        self.radius_y = 210.0
        self.x = self.center_x
        self.y = self.center_y

    def update(self, dt, enemies, projectiles, effects, active_meteorite=None):
        self.angle += dt * 0.75
        self.x = self.center_x + math.cos(self.angle) * self.radius_x
        self.y = self.center_y + math.sin(self.angle) * self.radius_y

        self.shoot_timer += dt
        cd = max(0.6, 1.4 - self.level * 0.25)
        if self.shoot_timer >= cd:
            self.shoot_timer = 0.0
            dmg = round(12.0 * (1.5 ** (self.level - 1)), 1)
            # Приоритет: метеорит, если он в таргете
            if active_meteorite and active_meteorite.active and active_meteorite.targeted:
                if math.hypot(self.x - active_meteorite.x, self.y - active_meteorite.y) <= 380:
                    projectiles.append(DroneSpike(self.x, self.y, active_meteorite, dmg))
                    laser.play()
                    return

            alive_enemies = [e for e in enemies if e.active]
            if alive_enemies:
                nearest = min(alive_enemies, key=lambda e: math.hypot(self.x - e.x, self.y - e.y))
                if math.hypot(self.x - nearest.x, self.y - nearest.y) <= 320:
                    projectiles.append(DroneSpike(self.x, self.y, nearest, dmg))
                    laser.play()

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        r = 20
        pygame.draw.circle(surface, (140, 60, 220), (cx, cy), r, width=2)
        p1 = (int(cx + math.cos(self.angle * 3) * r), int(cy + math.sin(self.angle * 3) * (r * 0.5)))
        p2 = (int(cx - math.cos(self.angle * 3) * r), int(cy - math.sin(self.angle * 3) * (r * 0.5)))
        pygame.draw.circle(surface, (230, 160, 255), p1, 4)
        pygame.draw.circle(surface, (230, 160, 255), p2, 4)
        surface.blit(cactus_img_s, (cx - 11, cy - 11))


class DroneSpike:
    def __init__(self, x, y, target, damage):
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.damage = damage
        self.speed = 420.0
        self.active = True

    def update(self, dt, enemies, effects, active_meteorite=None, **kwargs):
        if not self.target.active:
            self.active = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        step = self.speed * dt
        if dist <= step or dist < 12:
            self.target.take_damage(self.damage, damage_type="physical")
            if effects is not None:
                effects.append(FloatingText(self.target.x, self.target.y - 12, f"-{self.damage:g}", (220, 140, 255)))
                effects.append(DropSpark(self.target.x, self.target.y))
            self.active = False
        else:
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step

    def draw(self, surface):
        pygame.draw.circle(surface, (235, 160, 255), (int(self.x), int(self.y)), 4)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 2)


class OrbitalBeamEffect:
    def __init__(self, x, y, radius=120):
        self.x = float(x)
        self.y = float(y)
        self.radius = float(radius)
        self.timer = 0.0
        self.duration = 0.65

    def update(self, dt):
        self.timer += dt
        return self.timer >= self.duration

    def draw(self, surface):
        progress = self.timer / self.duration
        alpha = int(255 * (1.0 - progress))
        beam_w = max(4, int(self.radius * 0.4 * (1.0 - progress * 0.7)))
        beam_surf = pygame.Surface((beam_w * 2, int(self.y)), pygame.SRCALPHA)
        pygame.draw.rect(beam_surf, (220, 120, 255, min(255, alpha)), (0, 0, beam_w * 2, int(self.y)))
        pygame.draw.rect(beam_surf, (255, 255, 255, min(255, alpha)), (beam_w // 2, 0, beam_w, int(self.y)))
        surface.blit(beam_surf, (int(self.x - beam_w), 0))

        gr = int(self.radius * (0.3 + progress * 0.7))
        g_surf = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
        pygame.draw.circle(g_surf, (210, 80, 255, min(255, alpha // 2)), (gr, gr), gr)
        pygame.draw.circle(g_surf, (255, 255, 255, min(255, alpha)), (gr, gr), gr, width=3)
        surface.blit(g_surf, (int(self.x - gr), int(self.y - gr)))


# -------------------------------------------------------------------------
# КЛАСС ВРАГА (Слаймы)
# -------------------------------------------------------------------------
class Enemy:
    def __init__(self, enemy_type, current_wave, path, game_map=0, is_demo=False):
        self.type = enemy_type
        self.path = path
        self.wave = current_wave
        self.game_map = game_map
        self.is_demo = is_demo
        hp_mod = calculate_hp_modificator(current_wave)

        self.is_armored = False
        self.is_healer = False
        self.is_golden = False
        self.is_boss = (enemy_type >= 1000)
        self.magic_resist = 0.0
        self.heal_timer = 0.0

        if enemy_type == 1:
            self.base_speed = 90.0
            self.health = max(3.0, float(int(3 * hp_mod)))
            self.reward = 10
            self.base_damage = 1
            self.image = mob1_img
        elif enemy_type == 2:
            self.base_speed = 62.0
            self.health = max(6.0, float(int(6 * hp_mod)))
            self.reward = 20
            self.base_damage = 2
            self.image = mob2_img
            self.freeze_resist = 0.40
        elif enemy_type == 3:
            self.base_speed = 46.0
            self.health = max(12.0, float(int(12 * hp_mod)))
            self.reward = 30
            self.base_damage = 2
            self.image = mob3_img
            self.magic_resist = 0.35
        elif enemy_type == 4:
            self.base_speed = 130.0
            self.health = max(4.0, float(int(4 * hp_mod)))
            self.reward = 15
            self.base_damage = 1
            self.image = mob4_img
        elif enemy_type == 5:
            self.base_speed = 50.0
            self.health = max(15.0, float(int(15 * hp_mod)))
            self.reward = 35
            self.base_damage = 3
            self.image = mob5_img
            self.is_armored = True
        elif enemy_type == 6:
            self.base_speed = 60.0
            self.health = max(10.0, float(int(10 * hp_mod)))
            self.reward = 35
            self.base_damage = 2
            self.image = mob6_img
            self.is_healer = True
            self.magic_resist = 0.45
        elif enemy_type == 7:
            # Тигровый Слайм — Стремительный прыгун (периодические рывки)
            self.base_speed = 88.0
            self.health = max(12.0, float(int(12 * hp_mod)))
            self.reward = 45
            self.base_damage = 2
            self.image = mob7_img
            self.is_tiger = True
            self.tiger_dash_timer = random.uniform(0.5, 2.0)
        elif enemy_type == 8:
            # Ледяное Желе — Контр-пик мороза (иммунитет к льду, уязвимость к огню)
            self.base_speed = 66.0
            self.health = max(22.0, float(int(22 * hp_mod)))
            self.reward = 50
            self.base_damage = 2
            self.image = mob8_img
            self.is_frost_jelly = True
            self.is_frost_immune = True
        elif enemy_type == 9:
            # Слаймовая Пирамида — Высокий HP, при гибели делится на 2 быстрых слайма
            self.base_speed = 48.0
            self.health = max(36.0, float(int(36 * hp_mod)))
            self.reward = 65
            self.base_damage = 3
            self.image = mob9_img
            self.is_stacked = True
        elif enemy_type == 10:
            # Теневой Слайм — Антимагия (45% резист) и скрытный покров
            self.base_speed = 63.0
            self.health = max(26.0, float(int(26 * hp_mod)))
            self.reward = 70
            self.base_damage = 3
            self.image = mob10_img
            self.is_shadow = True
            self.magic_resist = 0.45
            self.shadow_timer = random.uniform(0.5, 2.5)
            self.is_cloaked = False
        elif enemy_type == 11:
            # Призматический Слайм — Преломление магии (70% резист) и иммунитет к критическому урону
            self.base_speed = 68.0
            self.health = max(18.0, float(int(18 * hp_mod)))
            self.reward = 55
            self.base_damage = 2
            self.image = mob11_img
            self.is_prism = True
            self.magic_resist = 0.70
        elif enemy_type == 12:
            # Пожиратель Маны — Поглощение магии и молний (лечится вместо урона)
            self.base_speed = 52.0
            self.health = max(28.0, float(int(28 * hp_mod)))
            self.reward = 70
            self.base_damage = 3
            self.image = mob12_img
            self.is_mana_devourer = True
        elif enemy_type == 13:
            # Обсидиановый Слайм — 90% защита от огня, ускорение от пламени, термошок от льда
            self.base_speed = 42.0
            self.health = max(40.0, float(int(40 * hp_mod)))
            self.reward = 80
            self.base_damage = 3
            self.image = mob13_img
            self.is_obsidian = True
            self.fire_speed_buff_timer = 0.0
        elif enemy_type == 14:
            # Паровой Слайм-Огнетушитель — Неуязвим к сплэшу, испускает пар при ударе огнем
            self.base_speed = 58.0
            self.health = max(24.0, float(int(24 * hp_mod)))
            self.reward = 60
            self.base_damage = 2
            self.image = mob14_img
            self.is_steam = True
        elif enemy_type == 15:
            # Слайм-Камикадзе — Детонирует при гибели или контакте с воинами, -3 HP базы
            self.base_speed = 95.0
            self.health = max(14.0, float(int(14 * hp_mod)))
            self.reward = 45
            self.base_damage = 3
            self.image = mob15_img
            self.is_kamikaze = True
        elif enemy_type == 16:
            # Слайм-Защитник — Аура щита (-40% входящего урона союзникам в радиусе 90px)
            self.base_speed = 46.0
            self.health = max(45.0, float(int(45 * hp_mod)))
            self.reward = 90
            self.base_damage = 3
            self.image = mob16_img
            self.is_protector = True
        elif enemy_type == 17:
            # Призрачный Слайм — Бесплотный летун, игнорирует наземных солдат палатки
            self.base_speed = 78.0
            self.health = max(16.0, float(int(16 * hp_mod)))
            self.reward = 50
            self.base_damage = 2
            self.image = mob17_img
            self.is_flying = True
        elif enemy_type == 18:
            # Песчаный Крот — Каждые 5с закапывается под землю на 2.5с (неуязвим для атак)
            self.base_speed = 64.0
            self.health = max(26.0, float(int(26 * hp_mod)))
            self.reward = 65
            self.base_damage = 2
            self.image = mob18_img
            self.is_burrower = True
            self.burrow_timer = random.uniform(0.5, 2.5)
            self.is_burrowed = False
        elif enemy_type == 777:
            self.base_speed = 98.0
            self.health = max(22.0, float(int(18 * hp_mod)))
            self.reward = 150
            self.base_damage = 1
            self.image = gold_slime_img
            self.is_golden = True
        elif enemy_type == 51:
            self.base_speed = 85.0
            self.health = float(int(25 * hp_mod))
            self.reward = 100
            self.base_damage = 3
            self.image = mob1_img
            self.is_armored = True
        elif enemy_type == 52:
            self.base_speed = 60.0
            self.health = float(int(50 * hp_mod))
            self.reward = 200
            self.base_damage = 4
            self.image = mob2_img
            self.is_armored = True
        elif enemy_type == 53:
            self.base_speed = 45.0
            self.health = float(int(90 * hp_mod))
            self.reward = 350
            self.base_damage = 5
            self.image = mob3_img
            self.magic_resist = 0.35
            self.is_armored = True
        elif enemy_type >= 4000:
            # Король Всех Слаймов (Волна 100) — Финальный Колос с адаптивным щитом и похищением уровней
            self.base_speed = 26.0
            self.health = float(int(120000 * (1.5 ** max(0, current_wave // 25 - 4))))
            self.reward = 15000
            self.base_damage = 999999
            self.image = void_lord_boss_img
            self.is_armored = True
            self.magic_resist = 0.50
            self.level_drain_timer = 12.0
            self.barrier_cycle_timer = 14.0
            self.adaptive_element = 0
        elif enemy_type >= 3000:
            # Багровый Титан (Волна 75+) — Грозный титан с лавовым следом и берсерком (<40% HP)
            self.base_speed = 28.0
            self.health = float(int(44000 * (1.5 ** max(0, current_wave // 25 - 3))))
            self.reward = 8000
            self.base_damage = 999999
            self.image = void_boss_img
            self.is_armored = True
            self.magic_resist = 0.40
            self.lava_trail_timer = 1.2
            self.is_enraged = False
        elif enemy_type >= 2000:
            # Слизнебарон (Волна 50) — Ледяной щит и заморозка ближайшей башни
            self.base_speed = 25.0
            self.health = float(int(12500 * (1.5 ** max(0, current_wave // 25 - 2))))
            self.reward = 3500
            self.base_damage = 999999
            self.image = colossus_boss_img
            self.is_armored = True
            self.magic_resist = 0.30
            self.freeze_tower_timer = 5.0
            self.ice_shield_timer = 9.0
            self.ice_shield_hp = 0.0
        elif enemy_type >= 1000:
            # Царь-Слизень (Волна 25) — Землетрясение (стан воинов) и призыв свиты на 75%/50%/25% HP
            self.base_speed = 22.0
            self.health = float(int(2600 * (1.5 ** max(0, current_wave // 25 - 1))))
            self.reward = 1500
            self.base_damage = 999999
            self.image = boss_img
            self.is_armored = True
            self.magic_resist = 0.25
            self.earthquake_timer = 5.0
            self.minion_hp_thresholds = [0.75, 0.50, 0.25]
        else:
            self.base_speed = 60.0
            self.health = 20.0
            self.reward = 20
            self.base_damage = 1
            self.image = mob1_img

        # Модификаторы карт из MAP_BIOMES_DATA
        biome = MAP_BIOMES_DATA.get(game_map, {})
        hp_mult = biome.get("hp_mult", 1.0)
        spd_mult = biome.get("spd_mult", 1.0)
        cacti_mult = biome.get("cacti_mult", biome.get("reward_mult", 1.0))

        if hp_mult != 1.0:
            self.health *= hp_mult

        diff = savedata.get("difficulty", "normal") if 'savedata' in globals() and isinstance(savedata, dict) else "normal"
        if diff == "casual":
            self.health *= 0.75
        elif diff == "hardcore":
            self.health *= 2.0
        self.health = max(1.0, self.health)

        if spd_mult != 1.0:
            self.base_speed *= spd_mult
        if cacti_mult != 1.0:
            self.reward = max(1, int(round(self.reward * cacti_mult)))

        # Открытие слайма в Словаре (Bestiary)
        if not self.is_demo and 'savedata' in globals() and isinstance(savedata, dict):
            disc = savedata.setdefault("BestiaryDiscovered", [])
            base_id = enemy_type
            if base_id >= 4000: base_id = 4000
            elif base_id >= 3000: base_id = 3000
            elif base_id >= 2000: base_id = 2000
            elif base_id >= 1000: base_id = 1000
            if base_id not in disc:
                disc.append(base_id)
                save_data(savedata)

        self.max_health = self.health
        self.path = path
        self.path_index = 0

        # Разброс по полосе движения (ширина дорожки ~32px, держимся внутри)
        if self.type >= 4000:
            self.lane_offset = random.uniform(-4.0, 4.0)
        elif self.type >= 1000:
            self.lane_offset = random.uniform(-6.0, 6.0)
        elif getattr(self, "is_stacked", False):
            self.lane_offset = random.uniform(-8.0, 8.0)
        else:
            self.lane_offset = random.uniform(-11.5, 11.5)

        # Вычисляем первое нормальное смещение относительно первого сегмента
        p0 = self.path[0]
        p1 = self.path[1] if len(self.path) > 1 else p0
        sdx = p1[0] - p0[0]
        sdy = p1[1] - p0[1]
        slen = math.hypot(sdx, sdy) or 1.0
        nx = -sdy / slen
        ny = sdx / slen

        self.x = float(p0[0] + nx * self.lane_offset)
        self.y = float(p0[1] + ny * self.lane_offset)
        self.target_x = float(p1[0] + nx * self.lane_offset)
        self.target_y = float(p1[1] + ny * self.lane_offset)
        self.progress = 0.0
        self.active = True
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

        # Индивидуальная вариация скорости, чтобы мобы не маршировали роботами
        self.individual_speed = random.uniform(0.93, 1.07) if self.type < 1000 else 1.0
        self.facing_left = False

        self.freeze_timer = 0.0
        self.speed_multiplier = 1.0
        self.soldier_hit_timer = 0.0

    def get_freeze_resistance(self):
        """
        Сопротивление замедлению/заморозке:
        - Обычные враги: 0.0 (кроме Ледяного Желе, у которого полный иммунитет)
        - 1-й Босс (Царь-Слизень, тип 1000, волна 25): 0.0 (нет сопротивления)
        - 2-й Босс (Слизнебарон, тип 2000, волна 50): 0.50 (50% сопротивление)
        - 3-й Босс (Теневой Исполин/Багровый Титан, тип 3000, волна 75): -0.10 (уязвимость: замедление на 10% сильнее)
        - 4-й Босс и дальше (Король Всех Слаймов, тип >= 4000, волна 100+): 30% + 10% за лвл босса (до 75%)
        """
        if self.type >= 4000:
            boss_lvl = max(0, (getattr(self, "wave", 100) - 100) // 25)
            return min(0.75, 0.30 + 0.10 * boss_lvl)
        elif self.type >= 3000:
            return -0.10
        elif self.type >= 2000:
            return 0.50
        elif self.type >= 1000:
            return 0.0
        return getattr(self, "freeze_resist", 0.0)

    def apply_freeze(self, slow_ratio, duration):
        if getattr(self, "is_frost_immune", False):
            return  # Ледяное желе полностью иммунно к замедлению от льда!
        if getattr(self, "game_map", 0) == 1:  # Круговорот: заморозка +25%
            duration *= 1.25
        if self.type == 4:  # Быстрый Слайм: быстрый метаболизм (-50% времени заморозки)
            duration *= 0.50
        self.freeze_timer = max(self.freeze_timer, duration)

        res = self.get_freeze_resistance()
        effective_slow = (1.0 - slow_ratio) * (1.0 - res)
        effective_ratio = max(0.10, min(1.0, 1.0 - effective_slow))

        if self.freeze_timer > 0 and self.speed_multiplier < 1.0:
            self.speed_multiplier = min(self.speed_multiplier, effective_ratio)
        else:
            self.speed_multiplier = effective_ratio

    def is_frozen(self):
        return self.freeze_timer > 0.0

    def take_damage(self, amount, damage_type="normal", is_crit=False, savedata=None):
        if getattr(self, "is_burrowed", False):
            return 0.0  # Песчаный крот под землей полностью неуязвим для атак!

        # Адаптивный барьер Короля Всех Слаймов (волна 100)
        if self.type >= 4000:
            elem = getattr(self, "adaptive_element", 0)
            if elem == 0 and damage_type in ["rock", "soldier", "physical"]:
                return 0.0
            elif elem == 1 and damage_type in ["magic", "lightning", "sun"]:
                return 0.0
            elif elem == 2 and damage_type in ["freeze", "orbital", "laser"]:
                return 0.0

        # Ледяной щит Слизнебарона
        if getattr(self, "ice_shield_hp", 0.0) > 0.0:
            absorbed = min(self.ice_shield_hp, amount)
            self.ice_shield_hp -= absorbed
            amount -= absorbed
            if amount <= 0:
                return 0.0

        # Багровый Титан в ярости (<40% HP): огонь исцеляет!
        if self.type >= 3000 and self.type < 4000 and getattr(self, "is_enraged", False):
            if damage_type in ["rock", "sun"]:
                heal = min(self.max_health - self.health, amount * 0.5)
                self.health += heal
                return -heal
            elif damage_type == "freeze":
                amount *= 0.20  # В берсерке мороз почти не действует

        # Пожиратель Маны (тип 12): поглощает магию и теслу, восстанавливая HP
        if getattr(self, "is_mana_devourer", False):
            if damage_type in ["magic", "lightning"]:
                heal = min(self.max_health - self.health, amount * 0.5)
                self.health += heal
                return -heal

        # Призматический Слайм (тип 11): 70% резист к магии, игнор крит урона
        if getattr(self, "is_prism", False):
            if is_crit:
                amount /= 1.5  # Отменяет крит-множитель урона

        # Обсидиановый Слайм (тип 13): 90% защита от огня, ускорение от пламени, термошок от льда
        if getattr(self, "is_obsidian", False):
            if damage_type in ["rock", "sun"]:
                amount *= 0.10
                self.fire_speed_buff_timer = 2.5
            elif damage_type == "freeze" and getattr(self, "fire_speed_buff_timer", 0.0) > 0.0:
                amount *= 2.0  # Термошок! Двойной урон от контраста температур
                self.freeze_timer = 2.5
                self.speed_multiplier = 0.0

        # Паровой Слайм (тип 14): неуязвим к сплэшу
        if getattr(self, "is_steam", False):
            if damage_type in ["rock_aoe", "sun_aoe"]:
                return 0.0
            if damage_type in ["rock", "sun"]:
                self.steam_cloud_timer = 2.5

        # Аура щита от Слайма-Защитника (тип 16)
        if getattr(self, "shield_protected_timer", 0.0) > 0.0:
            amount *= 0.60

        if getattr(self, 'is_armored', False) and damage_type in ["rock", "soldier", "physical"]:
            armor_factor = 0.25 if getattr(self, 'game_map', 0) == 7 else (0.75 if self.type >= 1000 else 0.50)
            amount *= armor_factor
        if getattr(self, 'magic_resist', 0.0) > 0 and damage_type in ["magic", "lightning"]:
            amount *= (1.0 - self.magic_resist)
        if getattr(self, 'is_frost_jelly', False):
            if damage_type == "rock":  # Огненный урон наносит +60%
                amount *= 1.60
            elif damage_type == "freeze":
                amount *= 0.30
        if getattr(self, 'is_cloaked', False):
            amount *= 0.50  # Теневой покров снижает любой входящий урон на 50%
        # Определение savedata
        s_data = savedata if isinstance(savedata, dict) else globals().get('savedata', None)
        # Талант «Охотник на Боссов»: +10% урона по боссам и элитам за ур.
        if self.type >= 50 and s_data and isinstance(s_data, dict):
            giant_lvl = s_data.get("Upgrades", {}).get("giant_hunter", 0)
            if giant_lvl > 0:
                amount *= (1.0 + giant_lvl * 0.10)
        # Талант «Анатомия Слаймов» (Бестиарий): +1%/+2%/+3% урона за каждый тир бестиария
        if s_data and isinstance(s_data, dict):
            b_dmg_lvl = s_data.get("Upgrades", {}).get("bestiary_damage", 0)
            if b_dmg_lvl > 0:
                mob_kills = s_data.get("BestiaryKills", {}).get(str(self.type), 0)
                mob_tier = get_mob_bestiary_tier(self.type, mob_kills)
                if mob_tier > 0:
                    amount *= (1.0 + (b_dmg_lvl * 0.01) * mob_tier)

        # Талант «Эссенция Бездны»: чистый урон Бездны (+10% за ранг)
        if s_data and isinstance(s_data, dict):
            vi_lvl = s_data.get("Upgrades", {}).get("void_infusion", 0)
            if vi_lvl > 0:
                amount *= (1.0 + vi_lvl * 0.10)
            r_buffs = get_all_relic_buffs(s_data)
            if self.type in (4, 10) and r_buffs.get("fast_shadow_dmg_mult", 0.0) > 0:
                amount *= (1.0 + r_buffs["fast_shadow_dmg_mult"])
            if (self.speed_multiplier < 1.0 or self.freeze_timer > 0) and r_buffs.get("slowed_target_dmg_mult", 0.0) > 0:
                amount *= (1.0 + r_buffs["slowed_target_dmg_mult"])
        old_hp = self.health
        self.health -= amount
        if self.health <= 0:
            self.active = False
        return old_hp - self.health

    def update(self, dt, towers, enemies=None, effects=None):
        if not self.active: return False

        if self.freeze_timer > 0:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.speed_multiplier = 1.0

        # Способность Целителя восстанавливать HP союзникам
        if getattr(self, 'is_healer', False) and enemies:
            self.heal_timer += dt
            if self.heal_timer >= 2.5:
                self.heal_timer = 0.0
                healed_any = False
                for other in enemies:
                    if other != self and other.active and other.health < other.max_health:
                        if math.hypot(self.x - other.x, self.y - other.y) <= 120:
                            heal_amt = min(other.max_health - other.health, max(3.0, 5.0 * calculate_hp_modificator(self.wave) * 0.4))
                            other.health += heal_amt
                            healed_any = True
                            if effects is not None:
                                effects.append(FloatingText(other.x, other.y - 14, f"+{heal_amt:g}", (80, 255, 140)))
                if healed_any:
                    sfx_heal.play()
                    if effects is not None:
                        effects.append(SplashEffect(self.x, self.y, 110, (50, 240, 150)))

        # Способность Тигрового Слайма: стремительный рывок
        if getattr(self, "is_tiger", False):
            self.tiger_dash_timer += dt
            if self.tiger_dash_timer >= 3.2:
                if self.tiger_dash_timer >= 3.8:
                    self.tiger_dash_timer = 0.0
                    self.speed_multiplier = 1.0
                else:
                    self.speed_multiplier = 2.4
                    if effects is not None and random.random() < 0.35:
                        effects.append(DropSpark(self.x + random.uniform(-6, 6), self.y + random.uniform(-6, 6), burst=True))

        # Способность Теневого Слайма: теневой покров (снижает входящий урон)
        if getattr(self, "is_shadow", False):
            self.shadow_timer += dt
            if self.shadow_timer >= 4.0:
                if self.shadow_timer >= 5.2:
                    self.shadow_timer = 0.0
                    self.is_cloaked = False
                else:
                    self.is_cloaked = True
                    if effects is not None and random.random() < 0.20:
                        effects.append(DropSpark(self.x + random.uniform(-5, 5), self.y - 10, burst=True))

        # Способность Обсидианового Слайма: ускорение от огня
        if getattr(self, "fire_speed_buff_timer", 0.0) > 0.0:
            self.fire_speed_buff_timer -= dt
            if self.fire_speed_buff_timer > 0.0:
                self.speed_multiplier = max(self.speed_multiplier, 1.35)

        # Способность Слайма-Защитника: аура силового купола для союзников
        if getattr(self, "is_protector", False) and enemies:
            for other in enemies:
                if other != self and other.active and math.hypot(self.x - other.x, self.y - other.y) <= 90:
                    other.shield_protected_timer = 0.4

        # Способность Песчаного Крота: закапывание под землю
        if getattr(self, "is_burrower", False):
            self.burrow_timer += dt
            if self.burrow_timer >= 5.0:
                if self.burrow_timer >= 7.5:
                    self.burrow_timer = 0.0
                    self.is_burrowed = False
                else:
                    self.is_burrowed = True
                    if effects is not None and random.random() < 0.20:
                        effects.append(DropSpark(self.x + random.uniform(-6, 6), self.y + 6, burst=False))

        # Способности Босса 1000 (Царь-Слизень, волна 25)
        if self.type >= 1000 and self.type < 2000:
            if hasattr(self, "earthquake_timer"):
                self.earthquake_timer -= dt
                if self.earthquake_timer <= 0:
                    self.earthquake_timer = 8.0
                    if effects is not None:
                        effects.append(RingEffect(self.x, self.y, 160, (180, 140, 80)))
                        effects.append(FloatingText(self.x, self.y - 28, "ЗЕМЛЕТРЯСЕНИЕ! (СТАН ВОИНОВ)", (255, 180, 60)))
                    sfx_boss_alarm.play()
                    for t in towers:
                        if t.type == "tent":
                            for s in t.soldiers:
                                if s.active:
                                    s.stun_timer = 2.5
            if hasattr(self, "minion_hp_thresholds"):
                hp_ratio = self.health / max(1.0, self.max_health)
                triggered = [th for th in self.minion_hp_thresholds if hp_ratio <= th]
                for th in triggered:
                    self.minion_hp_thresholds.remove(th)
                    if enemies is not None:
                        for _ in range(3):
                            m_type = random.choice([4, 7])
                            me = Enemy(m_type, getattr(self, "wave", 25), self.path, game_map=getattr(self, "game_map", 0))
                            me.path_index = max(0, self.path_index - 1)
                            me.x = self.x + random.uniform(-18, 18)
                            me.y = self.y + random.uniform(-18, 18)
                            enemies.append(me)
                        if effects is not None:
                            effects.append(FloatingText(self.x, self.y - 36, "ПРИЗЫВ СВИТЫ!", (120, 255, 160)))
                            effects.append(RingEffect(self.x, self.y, 70, (100, 240, 140)))

        # Способности Босса 2000 (Слизнебарон, волна 50)
        if self.type >= 2000 and self.type < 3000:
            if hasattr(self, "freeze_tower_timer"):
                self.freeze_tower_timer -= dt
                if self.freeze_tower_timer <= 0:
                    self.freeze_tower_timer = 9.0
                    target_tower = None
                    min_d = float('inf')
                    for t in towers:
                        if t.type != "farm":
                            td = math.hypot(self.x - t.x, self.y - t.y)
                            if td < min_d and td <= 240:
                                min_d = td
                                target_tower = t
                    if target_tower:
                        target_tower.freeze_disabled_timer = 3.0
                        if effects is not None:
                            effects.append(RingEffect(target_tower.x, target_tower.y, 48, (120, 230, 255)))
                            effects.append(FloatingText(target_tower.x, target_tower.y - 24, "ЗАМОРОЗКА! (3с)", (140, 230, 255)))
                        sfx_freeze_shot.play()
            if hasattr(self, "ice_shield_timer"):
                self.ice_shield_timer -= dt
                if self.ice_shield_timer <= 0:
                    self.ice_shield_timer = 11.0
                    self.ice_shield_hp = self.max_health * 0.12
                    if effects is not None:
                        effects.append(RingEffect(self.x, self.y, 80, (160, 240, 255)))
                        effects.append(FloatingText(self.x, self.y - 30, "ЛЕДЯНОЙ ЩИТ!", (180, 245, 255)))

        # Способности Босса 3000 (Багровый Титан, волна 75)
        if self.type >= 3000 and self.type < 4000:
            if not getattr(self, "is_enraged", False):
                if self.health / max(1.0, self.max_health) < 0.40:
                    self.is_enraged = True
                    self.base_speed = 39.0
                    self.freeze_timer = 0.0
                    self.speed_multiplier = 1.0
                    if effects is not None:
                        effects.append(RingEffect(self.x, self.y, 110, (255, 40, 40)))
                        effects.append(FloatingText(self.x, self.y - 34, "ЯРОСТЬ БЕРСЕРКА! (ОГОНЬ ЛЕЧИТ)", (255, 70, 70)))
                    sfx_boss_alarm.play()
            if hasattr(self, "lava_trail_timer"):
                self.lava_trail_timer -= dt
                if self.lava_trail_timer <= 0:
                    self.lava_trail_timer = 1.0
                    if effects is not None:
                        effects.append(DropSpark(self.x + random.uniform(-8, 8), self.y + random.uniform(-8, 8), burst=True))

        # Способности Босса 4000 (Король Всех Слаймов, волна 100)
        if self.type >= 4000:
            if hasattr(self, "barrier_cycle_timer"):
                self.barrier_cycle_timer -= dt
                if self.barrier_cycle_timer <= 0:
                    self.barrier_cycle_timer = 13.0
                    self.adaptive_element = (getattr(self, "adaptive_element", 0) + 1) % 3
                    names = {0: "АНТИ-ФИЗИКА (БРОНЯ)", 1: "АНТИ-МАГИЯ / ТЕСЛА", 2: "АНТИ-МОРОЗ / ОРБИТА"}
                    cols = {0: (255, 140, 60), 1: (200, 100, 255), 2: (100, 230, 255)}
                    if effects is not None:
                        effects.append(RingEffect(self.x, self.y, 120, cols[self.adaptive_element]))
                        effects.append(FloatingText(self.x, self.y - 36, f"ЩИТ: {names[self.adaptive_element]}", cols[self.adaptive_element]))
                    sfx_boss_alarm.play()
            if hasattr(self, "level_drain_timer"):
                self.level_drain_timer -= dt
                if self.level_drain_timer <= 0:
                    self.level_drain_timer = 16.0
                    best_tower = None
                    max_lvl = 1
                    for t in towers:
                        if t.type != "farm" and t.level > 1:
                            td = math.hypot(self.x - t.x, self.y - t.y)
                            if td <= 160 and t.level > max_lvl:
                                max_lvl = t.level
                                best_tower = t
                    if best_tower:
                        best_tower.level -= 1
                        best_tower.recalculate_stats()
                        if effects is not None:
                            effects.append(RingEffect(best_tower.x, best_tower.y, 64, (180, 50, 220)))
                            effects.append(FloatingText(best_tower.x, best_tower.y - 28, "-1 УРОВЕНЬ! (ПОХИЩЕНИЕ)", (220, 80, 255)))
                        sfx_boss_defeat.play()

        blocked_by_soldier = False
        self.soldier_hit_timer += dt
        boss_engaged_soldier = None

        # Призраки (17) и кроты под землей (18) не блокируются воинами
        can_engage_soldiers = not getattr(self, "is_flying", False) and not getattr(self, "is_burrowed", False)
        if can_engage_soldiers:
            for tower in towers:
                if tower.type == "tent":
                    for soldier in tower.soldiers:
                        if not soldier.active: continue
                        dist = math.hypot(self.x - soldier.x, self.y - soldier.y)
                        hit_range = 36 if self.type >= 1000 else 24
                        if dist < hit_range:
                            if self.type == 15:
                                # Детонация камикадзе при ударе о солдата!
                                soldier.take_mob_damage(15, effects=effects, attacker=self)
                                self.health = 0
                                self.active = False
                                if effects is not None:
                                    effects.append(SplashEffect(self.x, self.y, 65, (255, 60, 40)))
                                    effects.append(FloatingText(self.x, self.y - 18, "БАБАХ!", (255, 80, 50)))
                                sfx_tesla.play()
                                return False
                            elif self.type >= 1000:
                                # Боссы сражаются с воинами: замедляются на 50% и бьют воина раз в 0.75с, не зависая навечно
                                boss_engaged_soldier = soldier
                                if self.soldier_hit_timer >= 0.75:
                                    self.soldier_hit_timer = 0.0
                                    soldier.take_mob_damage(self.type, effects=effects, attacker=self)
                                break
                            else:
                                # Обычные и элитные слаймы: каждый воин сдерживает до 4 слаймов
                                if getattr(soldier, 'engaged_count', 0) < 4:
                                    soldier.engaged_count = getattr(soldier, 'engaged_count', 0) + 1
                                    blocked_by_soldier = True
                                    if self.soldier_hit_timer >= 0.75:
                                        self.soldier_hit_timer = 0.0
                                        soldier.take_mob_damage(self.type, effects=effects, attacker=self)
                                    break
                    if blocked_by_soldier or boss_engaged_soldier:
                        break

        if blocked_by_soldier:
            return False

        speed = self.base_speed * self.speed_multiplier * getattr(self, "individual_speed", 1.0)
        if boss_engaged_soldier:
            speed *= 0.50  # Замедление босса в ближнем бою с воинами
        step = speed * dt

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < step or dist < 3.0:
            self.path_index += 1
            if self.path_index >= len(self.path) - 1:
                self.active = False
                return True

            p_curr = self.path[self.path_index]
            p_next = self.path[self.path_index + 1]
            sdx = p_next[0] - p_curr[0]
            sdy = p_next[1] - p_curr[1]
            slen = math.hypot(sdx, sdy) or 1.0
            nx = -sdy / slen
            ny = sdx / slen

            self.target_x = float(p_next[0] + nx * self.lane_offset)
            self.target_y = float(p_next[1] + ny * self.lane_offset)
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.hypot(dx, dy)

        if dist > 0:
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step
            self.rect.center = (int(self.x), int(self.y))

        # Определение направления взгляда (разворот спрайта влево/вправо)
        if dx < -0.8:
            self.facing_left = True
        elif dx > 0.8:
            self.facing_left = False

        self.progress = self.path_index / max(1, len(self.path) - 1)
        return False

    def draw(self, surface):
        if not self.active: return

        # Чёткий пиксель-арт без искажений и сжатия
        img_to_draw = self.image
        if self.facing_left:
            img_to_draw = pygame.transform.flip(img_to_draw, True, False)

        # Призрачный слайм (17) парит над землёй с тенью
        draw_y = self.rect.y
        if getattr(self, "is_flying", False):
            bob = int(math.sin(pygame.time.get_ticks() * 0.007) * 3) - 6
            draw_y += bob
            # Тень на земле
            shadow_s = pygame.Surface((28, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_s, (20, 20, 30, 80), (0, 0, 28, 12))
            surface.blit(shadow_s, (int(self.x - 14), int(self.y + 12)))

        # Аура Слайма-Защитника (16)
        if getattr(self, "is_protector", False):
            pulse = math.sin(pygame.time.get_ticks() * 0.008) * 4
            p_surf = pygame.Surface((190, 190), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (255, 200, 50, 35), (95, 95), int(90 + pulse))
            pygame.draw.circle(p_surf, (255, 220, 80, 140), (95, 95), int(90 + pulse), width=2)
            surface.blit(p_surf, (int(self.x - 95), int(self.y - 95)))

        # Если заморожен — рисуем морозную ауру позади слайма
        if self.is_frozen():
            aura_rad = max(18, self.rect.width // 2 + 5)
            aura_s = pygame.Surface((aura_rad * 2, aura_rad * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_s, (80, 200, 255, 90), (aura_rad, aura_rad), aura_rad)
            pygame.draw.circle(aura_s, (160, 240, 255, 160), (aura_rad, aura_rad), aura_rad, width=2)
            surface.blit(aura_s, (int(self.x - aura_rad), int(self.y - aura_rad)))

        # Уникальные визуальные ауры боссов (соответствуют цветам 4 Больших Слаймов)
        if self.type >= 4000:
            # Фиолетовый Исполин Бездны (Волна 100) с динамическим кольцом адаптивного барьера
            elem = getattr(self, "adaptive_element", 0)
            elem_cols = {0: (255, 140, 60), 1: (200, 100, 255), 2: (100, 230, 255)}
            e_col = elem_cols.get(elem, (200, 100, 255))
            b_aura = pygame.Surface((116, 116), pygame.SRCALPHA)
            pygame.draw.circle(b_aura, (140, 20, 220, 115), (58, 58), 48)
            pygame.draw.circle(b_aura, (*e_col, 220), (58, 58), 54, width=3)
            pygame.draw.circle(b_aura, (255, 255, 255, 140), (58, 58), 32, width=1)
            surface.blit(b_aura, (int(self.x - 58), int(self.y - 58)))
        elif self.type >= 3000:
            # Багровый Титан (Волна 75)
            b_aura = pygame.Surface((92, 92), pygame.SRCALPHA)
            bg_col = (255, 20, 20, 150) if getattr(self, "is_enraged", False) else (225, 40, 40, 95)
            pygame.draw.circle(b_aura, bg_col, (46, 46), 40)
            pygame.draw.circle(b_aura, (255, 120, 50, 180), (46, 46), 42, width=2)
            pygame.draw.circle(b_aura, (255, 200, 70, 120), (46, 46), 28, width=1)
            surface.blit(b_aura, (int(self.x - 46), int(self.y - 46)))
        elif self.type >= 2000:
            # Лазурный Барон (Волна 50)
            b_aura = pygame.Surface((90, 90), pygame.SRCALPHA)
            pygame.draw.circle(b_aura, (40, 160, 240, 95), (45, 45), 38)
            pygame.draw.circle(b_aura, (120, 235, 255, 190), (45, 45), 40, width=2)
            if getattr(self, "ice_shield_hp", 0.0) > 0.0:
                pygame.draw.circle(b_aura, (200, 245, 255, 230), (45, 45), 44, width=3)
            surface.blit(b_aura, (int(self.x - 45), int(self.y - 45)))
        elif self.type >= 1000:
            # Изумрудный Царь (Волна 25)
            b_aura = pygame.Surface((84, 84), pygame.SRCALPHA)
            pygame.draw.circle(b_aura, (35, 200, 75, 90), (42, 42), 36)
            pygame.draw.circle(b_aura, (100, 255, 140, 170), (42, 42), 38, width=2)
            surface.blit(b_aura, (int(self.x - 42), int(self.y - 42)))

        # Отрисовка спрайта слайма (чистый пиксель-арт без искажений)
        if getattr(self, "is_burrowed", False):
            # Под землёй: полупрозрачный силуэт и песчаная насыпь
            c_surf = img_to_draw.copy()
            c_surf.set_alpha(80)
            surface.blit(c_surf, (self.rect.x, self.rect.y + 12))
            sand_s = pygame.Surface((38, 16), pygame.SRCALPHA)
            pygame.draw.ellipse(sand_s, (190, 150, 95, 180), (0, 0, 38, 16))
            pygame.draw.ellipse(sand_s, (230, 190, 120, 230), (4, 2, 30, 10))
            surface.blit(sand_s, (int(self.x - 19), int(self.y + 6)))
        elif getattr(self, "is_cloaked", False):
            c_surf = img_to_draw.copy()
            c_surf.set_alpha(115)
            surface.blit(c_surf, (self.rect.x, draw_y))
        else:
            surface.blit(img_to_draw, (self.rect.x, draw_y))

        # Шкала здоровья с точным позиционированием над макушкой моба
        bar_w = 34 if self.type < 1000 else 64
        ratio = max(0.0, self.health / self.max_health)
        bar_y = int(self.rect.top - 8)
        if getattr(self, "is_flying", False):
            bar_y += (draw_y - self.rect.y)
        pygame.draw.rect(surface, BLACK, (int(self.x - bar_w // 2 - 1), bar_y - 1, bar_w + 2, 5))
        pygame.draw.rect(surface, RED, (int(self.x - bar_w // 2), bar_y, bar_w, 3))
        pygame.draw.rect(surface, GREEN, (int(self.x - bar_w // 2), bar_y, int(bar_w * ratio), 3))

        # Если заморожен — рисуем кристаллик льда над шкалой HP
        if self.is_frozen():
            cx = int(self.x)
            cy = bar_y - 8
            pygame.draw.polygon(surface, CYAN, [(cx, cy - 6), (cx + 4, cy), (cx, cy + 6), (cx - 4, cy)])
            pygame.draw.polygon(surface, WHITE, [(cx, cy - 3), (cx + 2, cy), (cx, cy + 3), (cx - 2, cy)])

        if self.type >= 50:
            htxt = tiny_font.render(f"{int(self.health)}", True, WHITE if self.type < 1000 else YELLOW)
            surface.blit(htxt, (int(self.x - htxt.get_width() // 2), bar_y - 13))

    def get_splat_color(self):
        """Возвращает фирменный сочный оттенок желе для эффекта гибели слайма."""
        if getattr(self, "is_golden", False):
            return (255, 220, 60)
        elif self.type >= 4000:
            return (240, 60, 60)   # Король Всех Слаймов (рубиново-красный)
        elif self.type >= 3000:
            return (185, 50, 255)  # Теневой Исполин (глубокий аметист)
        elif self.type >= 2000:
            return (60, 215, 140)  # Слизнебарон (изумрудная лазурь)
        elif self.type >= 1000:
            return (80, 190, 255)  # Царь-Слизень (небесно-голубой)
        elif self.type == 1:
            return (85, 215, 60)   # Зеленый слайм (лайм)
        elif self.type == 2:
            return (55, 160, 245)  # Синий слайм (лазурь)
        elif self.type == 3:
            return (255, 95, 35)   # Огненный слайм (пламя)
        elif self.type == 4:
            return (255, 80, 165)  # Быстрый слайм (розовый неон)
        elif self.type == 5:
            return (150, 165, 185) # Бронированный слайм (стальной)
        elif self.type == 6:
            return (70, 245, 150)  # Лекарь (мята)
        elif self.type == 7:
            return (255, 160, 40)  # Тигровый слайм (янтарный)
        elif self.type == 8:
            return (120, 230, 255) # Ледяное желе (морозный лед)
        elif self.type == 9:
            return (235, 195, 85)  # Пирамида (песчаное золото)
        elif self.type == 10:
            return (175, 65, 245)  # Теневой слайм (теневой фиолетовый)
        elif self.type == 11:
            return (180, 230, 255) # Призматический (кристальный лазурит)
        elif self.type == 12:
            return (130, 40, 210)  # Пожиратель маны (эфирный пурпур)
        elif self.type == 13:
            return (45, 45, 55)    # Обсидиановый (вулканический уголь)
        elif self.type == 14:
            return (190, 215, 230) # Паровой (белый туман)
        elif self.type == 15:
            return (255, 60, 40)   # Камикадзе (детонационный пламень)
        elif self.type == 16:
            return (240, 200, 70)  # Защитник (золотой янтарь)
        elif self.type == 17:
            return (140, 255, 230) # Призрак (бирюзовый эфир)
        elif self.type == 18:
            return (200, 160, 105) # Песчаный крот (пустынный песок)
        elif self.type >= 50:
            return (255, 140, 40)  # Элитные мобы
        return (100, 220, 80)

# -------------------------------------------------------------------------
# ЗОНА АРХЕОЛОГИЧЕСКИХ РАСКОПОК НА КАРТЕ (DIG SITE)
# -------------------------------------------------------------------------
class DigSite:
    """Курган раскопок, появляющийся на поле боя в начале волны."""
    def __init__(self, x, y, duration=30.0, map_id=0):
        self.x = float(x)
        self.y = float(y)
        self.duration = float(duration)
        self.max_duration = float(duration)
        self.map_id = map_id
        self.radius = 26
        self.is_active = True
        self.t_spawn = time.time()
        self.pulse = 0.0

    def update(self, dt, effects=None):
        self.duration -= dt
        if self.duration <= 0:
            self.is_active = False
            return
        self.pulse = math.sin(time.time() * 4.0) * 3.0
        if effects is not None and random.random() < 0.15:
            # Золотистые песчинки
            effects.append(DropSpark(self.x + random.uniform(-16, 16), self.y + random.uniform(-10, 10), burst=False))

    def collidepoint(self, pos):
        return math.hypot(pos[0] - self.x, pos[1] - self.y) <= (self.radius + 6)

    def draw(self, surface):
        if not self.is_active:
            return
        cx, cy = int(self.x), int(self.y)

        # Песчаный курган (насыпь)
        pygame.draw.ellipse(surface, (120, 85, 45), (cx - 24, cy - 8, 48, 22))
        pygame.draw.ellipse(surface, (195, 145, 80), (cx - 22, cy - 11, 44, 18))
        pygame.draw.ellipse(surface, (235, 185, 110), (cx - 16, cy - 12, 32, 12))

        # Лопата в кургане
        surface.blit(shovel_icon_s, (cx - 11, cy - 18))

        # Пульсирующий ореол раскопок
        aura_rad = int(self.radius + self.pulse)
        pygame.draw.circle(surface, (255, 215, 90), (cx, cy), aura_rad, width=1)

        # Круговой таймер жизни
        ratio = max(0.0, min(1.0, self.duration / max(0.1, self.max_duration)))
        timer_col = (80, 230, 120) if ratio > 0.40 else ((245, 180, 50) if ratio > 0.20 else (245, 75, 75))
        rect_timer = pygame.Rect(cx - 28, cy - 28, 56, 56)
        angle_end = int(360 * ratio)
        if angle_end > 5:
            pygame.draw.arc(surface, timer_col, rect_timer, -math.pi / 2, -math.pi / 2 + math.radians(angle_end), 3)

        # Подсказка [КЛИК: КОПАТЬ]
        lbl = tiny_font.render(f"РАСКОПКИ ({int(self.duration)}с)", True, (255, 235, 160))
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - 36))


# -------------------------------------------------------------------------
# СЕССИЯ МИНИ-ИГРЫ «МОРСКОЙ БОЙ 5x5»
# -------------------------------------------------------------------------
class DigMinigameSession:
    """Управляет состоянием сетки 5х5 мини-игры раскопок."""
    def __init__(self, map_id, savedata):
        self.map_id = map_id
        self.savedata = savedata
        self.grid_size = 5
        self.dug = [[False for _ in range(5)] for _ in range(5)]
        
        buff_lvl = savedata.get("Upgrades", {}).get("dig_minigame_buff", 0)
        self.max_moves = 12 + buff_lvl * 2
        self.moves_left = self.max_moves

        # Выбираем реликвию карты (ту, которая еще не замакшена)
        r_ids = get_relics_for_map(map_id)
        max_cap = get_relic_max_level(savedata)
        valid_rids = []
        for rid in r_ids:
            cur_lvl = savedata.get("Relics", {}).get(rid, {}).get("level", 0)
            if cur_lvl < max_cap:
                valid_rids.append(rid)
        if not valid_rids:
            valid_rids = r_ids if r_ids else ["ancient_urn"]

        self.relic_id = random.choice(valid_rids)
        self.relic_info = RELICS_DATA.get(self.relic_id, RELICS_DATA["ancient_urn"])

        # Размещаем фигуру реликвии на сетке 5х5
        shape = self.relic_info["shape"]
        max_dx = max(dx for dx, dy in shape)
        max_dy = max(dy for dx, dy in shape)

        origin_x = random.randint(0, self.grid_size - 1 - max_dx)
        origin_y = random.randint(0, self.grid_size - 1 - max_dy)
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.relic_cells = set((origin_x + dx, origin_y + dy) for dx, dy in shape)

        self.uncovered_cells = set()
        self.is_won = False
        self.is_lost = False
        self.closed = False
        self.status_text = "Найдите скрытую реликвию!"
        self.status_color = (255, 230, 140)
        self.result_reward_text = ""

    def dig_cell(self, gx, gy):
        if self.is_won or self.is_lost or self.closed:
            return None
        if not (0 <= gx < 5 and 0 <= gy < 5):
            return None
        if self.dug[gy][gx]:
            return None

        self.dug[gy][gx] = True
        self.moves_left -= 1

        hit = (gx, gy) in self.relic_cells
        if hit:
            self.uncovered_cells.add((gx, gy))
            sfx_dig_hit.play()
            if self.uncovered_cells == self.relic_cells:
                # Победа!
                self.is_won = True
                diff = self.savedata.get("difficulty", "normal") if isinstance(self.savedata, dict) else "normal"
                if diff == "hardcore" and random.random() < 0.25:
                    self.status_text = "ОБВАЛ! Реликвия разрушена (Хардкор)!"
                    self.result_reward_text = "Артефакт поврежден при раскопках"
                    self.status_color = (255, 120, 120)
                    sfx_dig_miss.play()
                    return "win"

                sfx_relic_found.play()
                bonus_count = 2 if self.savedata.get("Upgrades", {}).get("relic_double_drop", 0) > 0 else 1
                new_lvl, lvl_up = add_relic_drop(self.relic_id, self.savedata, count=bonus_count)
                up_str = f" (ПОВЫШЕНИЕ ДО {new_lvl} УР!)" if lvl_up else f" ({new_lvl} ур.)"
                double_str = " x2 [Астральный Землекоп]" if bonus_count > 1 else ""
                self.status_text = f"НАЙДЕНО: {self.relic_info['name']}{up_str}!"
                self.result_reward_text = f"+{bonus_count} {self.relic_info['name']}{double_str}"
                self.status_color = (120, 255, 140)
                return "win"
            else:
                self.status_text = f"Фрагмент найден! ({len(self.uncovered_cells)}/{len(self.relic_cells)})"
                self.status_color = (255, 220, 100)
                return "hit"
        else:
            sfx_dig_miss.play()
            if self.savedata.get("Upgrades", {}).get("sonar_ping", 0) > 0:
                remaining = self.relic_cells - self.uncovered_cells
                if remaining:
                    nearest = min(remaining, key=lambda c: math.hypot(c[0] - gx, c[1] - gy))
                    self.last_sonar_hint = ((gx, gy), nearest)
            if self.moves_left <= 0:
                self.is_lost = True
                self.status_text = "Вскопки закончились! Раскоп обвалился."
                self.status_color = (255, 100, 100)
                return "lose"
            else:
                self.status_text = f"Пустой песок... Осталось ходов: {self.moves_left}"
                self.status_color = (200, 205, 215)
                return "miss"


# -------------------------------------------------------------------------
# АТМОСФЕРНЫЙ ДЕКОР ПОЛЕЙ БОЯ И БИОМОВ (MAP BACKGROUND DECOR)
# -------------------------------------------------------------------------
def _create_mini_cactus():
    """Крупный живописный кактус сагуаро с ветвями, иголками и пустынным цветком (44x56 px)."""
    s = pygame.Surface((44, 56), pygame.SRCALPHA)
    # Мягкая тень у основания
    pygame.draw.ellipse(s, (0, 0, 0, 75), (4, 44, 36, 10))
    # Основной ствол
    pygame.draw.rect(s, (40, 130, 55), (17, 10, 10, 38), border_radius=4)
    # Левая ветвь
    pygame.draw.lines(s, (40, 130, 55), False, [(9, 22), (9, 32), (17, 32)], 5)
    pygame.draw.circle(s, (40, 130, 55), (9, 22), 3)
    # Правая ветвь
    pygame.draw.lines(s, (40, 130, 55), False, [(27, 26), (35, 26), (35, 16)], 5)
    pygame.draw.circle(s, (40, 130, 55), (35, 16), 3)
    # Блики и ребра на стволе
    pygame.draw.line(s, (75, 185, 95), (20, 12), (20, 46), 2)
    pygame.draw.line(s, (75, 185, 95), (10, 22), (10, 30), 1)
    pygame.draw.line(s, (75, 185, 95), (34, 18), (34, 25), 1)
    # Иголки (золотистые точки)
    for ny in [16, 24, 32, 40]:
        s.set_at((16, ny), (220, 240, 130, 200))
        s.set_at((27, ny + 4), (220, 240, 130, 200))
    # Яркий пустынный цветок на макушке
    pygame.draw.circle(s, (245, 100, 150), (22, 9), 4)
    pygame.draw.circle(s, (255, 220, 100), (22, 9), 2)
    return s

def _create_desert_rock():
    """Массивный гранёный песчаный валун со сколами и тенями (52x34 px)."""
    s = pygame.Surface((52, 34), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 70), (4, 18, 44, 14))
    poly = [(8, 22), (14, 8), (32, 6), (44, 14), (46, 24), (36, 28), (14, 28)]
    pygame.draw.polygon(s, (180, 145, 95), poly)
    # Теневая грань
    poly_dark = [(32, 6), (44, 14), (46, 24), (36, 28), (28, 20)]
    pygame.draw.polygon(s, (135, 105, 65), poly_dark)
    # Освещенная грань
    poly_hi = [(8, 22), (14, 8), (32, 6), (28, 20)]
    pygame.draw.polygon(s, (215, 180, 125), poly_hi)
    # Контур и трещины
    pygame.draw.polygon(s, (110, 80, 45), poly, width=2)
    pygame.draw.line(s, (110, 80, 45), (28, 20), (32, 6), 2)
    pygame.draw.line(s, (110, 80, 45), (28, 20), (36, 28), 2)
    pygame.draw.line(s, (110, 80, 45), (28, 20), (14, 28), 2)
    # Мелкий камушек рядом
    pygame.draw.circle(s, (160, 125, 80), (6, 26), 4)
    pygame.draw.circle(s, (110, 80, 45), (6, 26), 4, width=1)
    return s

def _create_desert_shrub():
    """Пышный пустынный кустарник с ветвями и листвой (44x32 px)."""
    s = pygame.Surface((44, 32), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 60), (4, 18, 36, 10))
    pygame.draw.circle(s, (140, 125, 65), (14, 18), 9)
    pygame.draw.circle(s, (120, 105, 50), (28, 18), 10)
    pygame.draw.circle(s, (165, 145, 80), (22, 12), 11)
    pygame.draw.circle(s, (185, 165, 95), (20, 10), 7)
    pygame.draw.line(s, (90, 75, 40), (14, 18), (8, 12), 2)
    pygame.draw.line(s, (90, 75, 40), (28, 18), (34, 14), 2)
    pygame.draw.circle(s, (210, 190, 115), (22, 8), 3)
    return s

def _create_canyon_rock():
    """Слоистая терракотовая скала каньона с геологическими прожилками (54x38 px)."""
    s = pygame.Surface((54, 38), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 75), (4, 20, 46, 15))
    poly = [(8, 26), (12, 10), (34, 6), (46, 16), (48, 28), (34, 32), (16, 32)]
    pygame.draw.polygon(s, (190, 85, 55), poly)
    poly_dark = [(34, 6), (46, 16), (48, 28), (34, 32), (26, 22)]
    pygame.draw.polygon(s, (135, 50, 30), poly_dark)
    poly_hi = [(8, 26), (12, 10), (34, 6), (26, 22)]
    pygame.draw.polygon(s, (230, 125, 90), poly_hi)
    pygame.draw.line(s, (250, 150, 110), (14, 16), (32, 14), 2)
    pygame.draw.line(s, (110, 40, 25), (16, 22), (40, 20), 2)
    pygame.draw.polygon(s, (95, 35, 20), poly, width=2)
    return s

def _create_crystal(color=(70, 215, 250)):
    """Кристаллическая друза с гранями и каменным пьедесталом (48x52 px)."""
    s = pygame.Surface((48, 52), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 85), (6, 36, 36, 12))
    # Каменное основание
    pygame.draw.polygon(s, (45, 50, 60), [(10, 42), (18, 34), (30, 34), (38, 42), (24, 46)])
    pygame.draw.polygon(s, (30, 35, 42), [(10, 42), (18, 34), (30, 34), (38, 42), (24, 46)], width=1)

    c1_hi = (min(255, color[0] + 60), min(255, color[1] + 60), min(255, color[2] + 60))
    c1_dark = (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40))

    # Центральный обелиск
    pygame.draw.polygon(s, c1_hi, [(18, 36), (24, 8), (28, 36)])
    pygame.draw.polygon(s, c1_dark, [(24, 8), (30, 36), (28, 36)])
    pygame.draw.polygon(s, (255, 255, 255), [(18, 36), (24, 8), (30, 36)], width=1)
    pygame.draw.line(s, (255, 255, 255), (24, 8), (24, 34), 2)

    # Левый осколок
    pygame.draw.polygon(s, color, [(8, 38), (14, 18), (18, 38)])
    pygame.draw.polygon(s, (255, 255, 255), [(8, 38), (14, 18), (18, 38)], width=1)

    # Правый осколок
    pygame.draw.polygon(s, c1_dark, [(28, 40), (36, 22), (40, 40)])
    pygame.draw.polygon(s, (255, 255, 255), [(28, 40), (36, 22), (40, 40)], width=1)
    return s

def _create_ice_shard():
    """Острые ледниковые кристаллы из снежного наста (42x54 px)."""
    s = pygame.Surface((42, 54), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 70), (4, 38, 34, 12))
    pygame.draw.ellipse(s, (190, 230, 245), (6, 36, 30, 10))
    poly_center = [(16, 40), (21, 6), (27, 40)]
    pygame.draw.polygon(s, (165, 235, 255), poly_center)
    pygame.draw.polygon(s, (110, 195, 235), [(21, 6), (27, 40), (24, 40)])
    pygame.draw.polygon(s, (140, 215, 245), [(8, 40), (13, 20), (18, 40)])
    pygame.draw.polygon(s, (100, 180, 225), [(25, 40), (32, 24), (36, 40)])
    pygame.draw.line(s, (255, 255, 255), (21, 6), (21, 38), 2)
    pygame.draw.polygon(s, (255, 255, 255), poly_center, width=1)
    return s

def _create_rune_stone():
    """Древний рунический монолит с сияющими символами (44x58 px)."""
    s = pygame.Surface((44, 58), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 80), (4, 42, 36, 12))
    poly = [(12, 44), (10, 14), (22, 6), (32, 12), (30, 44)]
    pygame.draw.polygon(s, (65, 70, 82), poly)
    pygame.draw.polygon(s, (95, 102, 120), [(12, 44), (10, 14), (22, 6), (20, 44)])
    pygame.draw.polygon(s, (40, 44, 52), poly, width=2)
    # Магическая руна
    pygame.draw.lines(s, (100, 240, 255), False, [(21, 16), (21, 38)], 2)
    pygame.draw.lines(s, (100, 240, 255), False, [(16, 24), (26, 24)], 2)
    pygame.draw.lines(s, (100, 240, 255), False, [(17, 32), (21, 28), (25, 32)], 2)
    pygame.draw.circle(s, (255, 255, 255), (21, 16), 2)
    return s

def _create_desert_flower():
    """Цветущий пустынный лотос / агава с сочными листьями и лепестками (42x40 px)."""
    s = pygame.Surface((42, 40), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 65), (4, 26, 34, 10))
    for angle in [math.pi * 0.8, math.pi * 0.5, math.pi * 0.2]:
        lx = int(21 + math.cos(angle) * 14)
        ly = int(26 + math.sin(angle) * 6)
        pygame.draw.circle(s, (45, 125, 55), (lx, ly), 7)
        pygame.draw.circle(s, (70, 175, 80), (lx, ly), 5)
    for i in range(7):
        ang = (i / 7.0) * math.pi * 2
        px = int(21 + math.cos(ang) * 9)
        py = int(18 + math.sin(ang) * 9)
        pygame.draw.circle(s, (255, 95, 155), (px, py), 6)
        pygame.draw.circle(s, (255, 150, 195), (px, py), 4)
    pygame.draw.circle(s, (255, 225, 60), (21, 18), 5)
    pygame.draw.circle(s, (255, 255, 200), (20, 17), 2)
    return s

def _create_magma_crack():
    """Раскол базальтовой коры с бурлящей лавой (64x30 px)."""
    s = pygame.Surface((64, 30), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (20, 14, 16, 200), (4, 4, 56, 22))
    pts = [(6, 15), (16, 8), (26, 20), (38, 9), (50, 18), (58, 14)]
    pygame.draw.lines(s, (150, 30, 15), False, pts, 7)
    pygame.draw.lines(s, (255, 90, 20), False, pts, 4)
    pygame.draw.lines(s, (255, 230, 80), False, pts, 2)
    pygame.draw.lines(s, (255, 255, 255), False, [(24, 18), (28, 18), (38, 10)], 1)
    return s

def _create_astral_star():
    """Астральный парящий обелиск с сияющим ядром (44x56 px)."""
    s = pygame.Surface((44, 56), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 80), (4, 40, 36, 12))
    poly_base = [(10, 44), (16, 36), (28, 36), (34, 44), (22, 48)]
    pygame.draw.polygon(s, (28, 22, 42), poly_base)
    prism = [(22, 8), (32, 24), (22, 38), (12, 24)]
    pygame.draw.polygon(s, (180, 110, 255), prism)
    pygame.draw.polygon(s, (230, 180, 255), [(22, 8), (22, 38), (12, 24)])
    pygame.draw.polygon(s, (255, 255, 255), prism, width=2)
    pygame.draw.circle(s, (255, 255, 255), (22, 23), 4)
    pygame.draw.line(s, (255, 255, 255), (22, 13), (22, 33), 1)
    pygame.draw.line(s, (255, 255, 255), (14, 23), (30, 23), 1)
    return s


class MapDecorManager:
    """Генерирует и отрисовывает крупный органичный декор биома на свободном поле карты."""
    def __init__(self, map_id, path, tower_slots):
        self.map_id = map_id
        self.items = []
        self._build_decor(map_id, path, tower_slots)

    def _build_decor(self, map_id, path, tower_slots):
        rng = random.Random(1337 + map_id * 97)
        points = []
        attempts = 0
        while len(points) < 14 and attempts < 400:
            attempts += 1
            px = rng.randint(55, SCREEN_WIDTH - 55)
            py = rng.randint(65, SCREEN_HEIGHT - 75)

            if len(path) > 1:
                min_p_dist = min(self._dist_to_seg((px, py), path[i], path[i + 1]) for i in range(len(path) - 1))
                if min_p_dist < 52:
                    continue

            if tower_slots:
                min_s_dist = min(math.hypot(px - sx, py - sy) for sx, sy in tower_slots)
                if min_s_dist < 46:
                    continue

            if any(math.hypot(px - ox, py - oy) < 55 for ox, oy, _ in points):
                continue

            d_type = self._pick_type_for_biome(map_id, rng)
            points.append((px, py, d_type))

        for px, py, d_type in points:
            surf, has_glow = self._get_decor_surface(d_type, rng)
            self.items.append({
                "x": px, "y": py,
                "type": d_type,
                "surf": surf,
                "has_glow": has_glow,
                "phase": rng.uniform(0, math.pi * 2)
            })

    def _dist_to_seg(self, p, a, b):
        px, py = p
        ax, ay = a
        bx, by = b
        abx, aby = bx - ax, by - ay
        apx, apy = px - ax, py - ay
        mag2 = abx * abx + aby * aby
        if mag2 == 0:
            return math.hypot(px - ax, py - ay)
        t = max(0.0, min(1.0, (apx * abx + apy * aby) / mag2))
        cx, cy = ax + t * abx, ay + t * aby
        return math.hypot(px - cx, py - cy)

    def _pick_type_for_biome(self, map_id, rng):
        if map_id == 0:
            return rng.choice(["mini_cactus", "mini_cactus", "desert_rock", "desert_shrub", "desert_flower"])
        elif map_id == 1:
            return rng.choice(["canyon_rock", "canyon_rock", "desert_rock", "desert_shrub"])
        elif map_id == 2:
            return rng.choice(["crystal_cyan", "crystal_purple", "desert_rock", "canyon_rock"])
        elif map_id == 3:
            return rng.choice(["ice_shard", "ice_shard", "desert_rock", "crystal_cyan"])
        elif map_id == 4:
            return rng.choice(["rune_stone", "rune_stone", "crystal_cyan", "desert_rock"])
        elif map_id == 5:
            return rng.choice(["rune_stone", "desert_rock", "canyon_rock"])
        elif map_id == 6:
            return rng.choice(["desert_flower", "mini_cactus", "desert_rock", "desert_shrub"])
        elif map_id == 7:
            return rng.choice(["magma_crack", "magma_crack", "canyon_rock"])
        elif map_id == 8:
            return rng.choice(["astral_star", "crystal_purple", "rune_stone"])
        else:
            return rng.choice(["mini_cactus", "desert_flower", "desert_rock", "crystal_cyan"])

    def _get_decor_surface(self, d_type, rng):
        if d_type == "mini_cactus":
            return _create_mini_cactus(), False
        elif d_type == "desert_rock":
            return _create_desert_rock(), False
        elif d_type == "desert_shrub":
            return _create_desert_shrub(), False
        elif d_type == "canyon_rock":
            return _create_canyon_rock(), False
        elif d_type == "crystal_cyan":
            return _create_crystal((70, 215, 250)), True
        elif d_type == "crystal_purple":
            return _create_crystal((195, 90, 255)), True
        elif d_type == "ice_shard":
            return _create_ice_shard(), True
        elif d_type == "rune_stone":
            return _create_rune_stone(), True
        elif d_type == "desert_flower":
            return _create_desert_flower(), False
        elif d_type == "magma_crack":
            return _create_magma_crack(), True
        elif d_type == "astral_star":
            return _create_astral_star(), True
        return _create_desert_rock(), False

    def draw(self, surface, bg_time=0):
        if get_graphics_preset() == "optimized":
            return
        for item in self.items:
            x, y = item["x"], item["y"]
            surf = item["surf"]
            surface.blit(surf, (x - surf.get_width() // 2, y - surf.get_height() // 2))
