# -*- coding: utf-8 -*-
"""
tree_data_v02.py - Tree nodes v0.2 (81 nodes), Metro-routing and 10 Bestiary tiers.
"""
import math

# -------------------------------------------------------------------------
# BESTIARY 10 TIERS SYSTEM
# -------------------------------------------------------------------------
BESTIARY_TIER_THRESHOLDS = {
    "basic": [25, 60, 120, 200, 350, 550, 800, 1200, 1700, 2500],
    "medium": [15, 35, 75, 130, 220, 350, 500, 750, 1100, 1600],
    "elite": [10, 25, 50, 90, 150, 230, 340, 500, 750, 1000],
    "gold": [1, 3, 6, 10, 16, 25, 38, 55, 80, 120],
    "boss": [1, 2, 4, 7, 11, 16, 23, 32, 45, 60]
}

ROMAN_TIERS = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

def get_bestiary_tier_thresholds(mob_id):
    try:
        mid = int(mob_id)
    except (ValueError, TypeError):
        mid = 1
    if mid in (1000, 2000, 3000, 4000) or mid >= 1000:
        return BESTIARY_TIER_THRESHOLDS["boss"]
    elif mid == 777:
        return BESTIARY_TIER_THRESHOLDS["gold"]
    elif mid in (51, 52, 53):
        return BESTIARY_TIER_THRESHOLDS["elite"]
    elif mid in (1, 2, 3, 4):
        return BESTIARY_TIER_THRESHOLDS["basic"]
    else:
        return BESTIARY_TIER_THRESHOLDS["medium"]

def get_mob_bestiary_tier(arg1, arg2=0):
    try:
        v1, v2 = int(arg1), int(arg2)
    except (ValueError, TypeError):
        return 0
    if v1 in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 51, 52, 53, 777, 1000, 2000, 3000, 4000) or v1 >= 1000:
        mob_id, kills = v1, v2
    else:
        kills, mob_id = v1, v2

    thresholds = get_bestiary_tier_thresholds(mob_id)
    tier = 0
    for req in thresholds:
        if kills >= req:
            tier += 1
        else:
            break
    return tier

def get_mob_bestiary_progress(arg1, arg2=0):
    try:
        v1, v2 = int(arg1), int(arg2)
    except (ValueError, TypeError):
        return 0, 0, 1, 0.0
    if v1 in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 51, 52, 53, 777, 1000, 2000, 3000, 4000) or v1 >= 1000:
        mob_id, kills = v1, v2
    else:
        kills, mob_id = v1, v2

    thresholds = get_bestiary_tier_thresholds(mob_id)
    tier = get_mob_bestiary_tier(mob_id, kills)
    if tier >= 10:
        return 10, thresholds[-1], thresholds[-1], 1.0
    prev_req = thresholds[tier - 1] if tier > 0 else 0
    next_req = thresholds[tier]
    cur_in_tier = max(0, kills - prev_req)
    span = next_req - prev_req
    ratio = min(1.0, max(0.0, cur_in_tier / max(1, span)))
    return tier, cur_in_tier, span, ratio

def get_bestiary_buffs(savedata, mob_id=None):
    if not isinstance(savedata, dict):
        return {"dmg_mult": 1.0, "cacti_mult": 1.0, "star_chance_bonus": 0.0}
    upgrades = savedata.get("Upgrades", {})
    dmg_lvl = upgrades.get("bestiary_damage", 0)
    cacti_lvl = upgrades.get("bestiary_cacti", 0)
    stars_lvl = upgrades.get("bestiary_stars", 0)

    if mob_id is None:
        return {
            "dmg_per_tier": dmg_lvl * 0.01,
            "cacti_per_tier": cacti_lvl * 0.01,
            "stars_per_tier": stars_lvl * 0.01
        }

    kills_dict = savedata.get("BestiaryKills", {})
    k_count = kills_dict.get(str(mob_id), 0)
    tier = get_mob_bestiary_tier(mob_id, k_count)

    dmg_mult = 1.0 + tier * (dmg_lvl * 0.01)
    cacti_mult = 1.0 + tier * (cacti_lvl * 0.01)
    star_bonus = tier * (stars_lvl * 0.01)

    return {
        "tier": tier,
        "dmg_mult": dmg_mult,
        "cacti_mult": cacti_mult,
        "star_chance_bonus": star_bonus
    }

def get_all_81_nodes():
    nodes = {
        # ---------------- ИСТОКИ ----------------
        "oasis_core": {
            "title": "Оазис Кактусов",
            "branch": "core",
            "branch_title": "Истоки",
            "scale": 2.0,
            "x": 350, "y": -80,
            "max_lvl": 1,
            "costs": [0],
            "requires": {},
            "desc": [
                "Главное древо улучшений.",
                "Открывает доступ ко всем веткам",
                "улучшений оазиса."
            ],
            "stat_cur": lambda lvl: "Ядро оазиса активно",
            "stat_nxt": lambda lvl: "Активировать ядро оазиса",
            "icon_key": "cactus"
        },

        # ---------------- БАШНИ ОАЗИСА (ОБЩЕЕ) ----------------
        "start_tower_level": {
            "title": "Стартовый Уровень",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190, "y": 60,
            "max_lvl": 10,
            "costs": [2, 3, 5, 8, 12, 17, 23, 30, 38, 47],
            "requires": {'oasis_core': 1},
            "desc": [
                "Башни возводятся сразу улучшенными.",
                "+1 к стартовому уровню всех возводимых башен",
                "за каждый изученный ранг (вплоть до 11 ур.)!"
            ],
            "stat_cur": lambda lvl: f"Старт постройки: {1 + lvl} ур. башни" if lvl > 0 else "Базовый 1 уровень постройки",
            "stat_nxt": lambda lvl: f"Старт постройки: {2 + lvl} ур. башни",
            "icon_key": "start_lvl"
        },
        "attack_speed_overdrive": {
            "title": "Форсаж Атаки",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 40, "y": 60,
            "max_lvl": 5,
            "costs": [3, 6, 12, 20, 32],
            "requires": {'start_tower_level': 2},
            "desc": [
                "Механизмы ускоренной перезарядки.",
                "Ускоряет перезарядку атак всех башен",
                "и казарм на +4% за уровень!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 4}% к скорости атаки всех башен" if lvl > 0 else "Базовая скорость стрельбы",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 4}% к скорости атаки всех башен",
            "icon_key": "speed"
        },
        "max_tower_level": {
            "title": "Предел Инженерии",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510, "y": 60,
            "max_lvl": 5,
            "costs": [4, 8, 15, 25, 40],
            "requires": {'oasis_core': 1},
            "desc": [
                "Улучшение материалов и фундамента.",
                "Повышает максимальный уровень прокачки",
                "всех типов башен на +1 за каждый ранг."
            ],
            "stat_cur": lambda lvl: f"+{lvl} к макс. уровню всех башен" if lvl > 0 else "Базовый предел уровней",
            "stat_nxt": lambda lvl: f"+{lvl + 1} к макс. уровню всех башен",
            "icon_key": "max_lvl"
        },
        "bulk_upgrade": {
            "title": "Оптовая Стройка",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 660, "y": 60,
            "max_lvl": 2,
            "costs": [6, 14],
            "requires": {'max_tower_level': 1},
            "desc": [
                "Быстрое возведение инфраструктуры.",
                "Позволяет улучшать башни сразу на +5",
                "уровней одним нажатием кнопки."
            ],
            "stat_cur": lambda lvl: f"Оптовое улучшение: +{lvl * 5} уровней за клик" if lvl > 0 else "Одиночное улучшение",
            "stat_nxt": lambda lvl: f"Оптовое улучшение: +{(lvl + 1) * 5} уровней за клик",
            "icon_key": "bulk"
        },

        # ---------------- 1. МАГИЧЕСКАЯ БАШНЯ (Y = 180) ----------------
        "magic_tower": {
            "title": "Магическая Башня",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.3,
            "x": 350, "y": 180,
            "max_lvl": 1,
            "costs": [0],
            "requires": {'oasis_core': 1},
            "desc": [
                "Древний кристаллический шпиль.",
                "Атакует одиночные цели быстрыми",
                "самонаводящимися магическими зарядами."
            ],
            "stat_cur": lambda lvl: "Постройка разблокирована",
            "stat_nxt": lambda lvl: "Разблокировать Магическую Башню",
            "icon_key": "magic_tower"
        },
        "sniper_optics": {
            "title": "Дальняя Оптика",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190, "y": 180,
            "max_lvl": 5,
            "costs": [2, 4, 7, 12, 18],
            "requires": {'magic_tower': 1},
            "desc": [
                "Магические призмы наведения.",
                "Увеличивает дальность поражения всех",
                "дальнобойных башен на +8 px за ранг!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 8} px к дальности башен" if lvl > 0 else "Базовый радиус обзора",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 8} px к дальности башен",
            "icon_key": "optics"
        },
        "magic_power": {
            "title": "Магический Резонанс",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 40, "y": 180,
            "max_lvl": 5,
            "costs": [2, 5, 9, 15, 24],
            "requires": {'sniper_optics': 1},
            "desc": [
                "Усиливает прирост урона кристаллов.",
                "Каждый уровень Магической башни в бою",
                "дает на +0.10 больше чистого урона!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 0.10:.2f} урона за уровень башни" if lvl > 0 else "Базовый прирост урона",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 0.10:.2f} урона за уровень башни",
            "icon_key": "magic_resonance"
        },
        "arcane_precision": {
            "title": "Тайная Точность",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510, "y": 180,
            "max_lvl": 3,
            "costs": [3, 7, 14],
            "requires": {'magic_tower': 1},
            "desc": [
                "Фокусировка магических импульсов.",
                "+2% / +4% / +6% к шансу крита",
                "для Магической башни!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 2}% к крит-шансу Магической башни" if lvl > 0 else "Базовый шанс крита",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 2}% к крит-шансу Магической башни",
            "icon_key": "target"
        },

        # ---------------- 2. ОГНЕННАЯ БАШНЯ (Y = 360) ----------------
        "rock_tower": {
            "title": "Огненная Башня",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.3,
            "x": 350, "y": 360,
            "max_lvl": 1,
            "costs": [2],
            "requires": {'magic_tower': 1},
            "desc": [
                "Метатель раскалённых валунов.",
                "Наносит сокрушительный сплэш-урон по площади.",
                "Наносит +75% урона замороженным врагам!"
            ],
            "stat_cur": lambda lvl: "Постройка разблокирована",
            "stat_nxt": lambda lvl: "Разблокировать Огненную Башню",
            "icon_key": "rock_tower"
        },
        "inferno_mastery": {
            "title": "Пламенное Горнило",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510, "y": 360,
            "max_lvl": 5,
            "costs": [3, 6, 11, 18, 28],
            "requires": {'rock_tower': 'max'},
            "desc": [
                "Экстремальная температура огненных бомб.",
                "+10% к урону, +6 px к радиусу сплэша и +10%",
                "к бонусу по замороженным врагам за уровень!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 10}% урона, +{lvl * 6} px сплэша" if lvl > 0 else "Базовые огненные бомбы",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 10}% урона, +{(lvl + 1) * 6} px сплэша",
            "icon_key": "inferno"
        },

        # ---------------- 3. ЛЕДЯНАЯ БАШНЯ (Y = 540) ----------------
        "freeze_tower": {
            "title": "Ледяная Башня",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.3,
            "x": 350, "y": 540,
            "max_lvl": 1,
            "costs": [3],
            "requires": {'rock_tower': 'max'},
            "desc": [
                "Морозный генератор оазиса.",
                "Выпускает ледяные волны по всем врагам в радиусе,",
                "нанося урон и замедляя их скорость перемещения."
            ],
            "stat_cur": lambda lvl: "Постройка разблокирована",
            "stat_nxt": lambda lvl: "Разблокировать Ледяную Башню",
            "icon_key": "freeze_tower"
        },
        "frost_nova": {
            "title": "Абсолютный Ноль",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190, "y": 540,
            "max_lvl": 5,
            "costs": [3, 7, 13, 21, 32],
            "requires": {'freeze_tower': 'max'},
            "desc": [
                "Глубокая заморозка крио-камерами.",
                "+2.7% замедления, +10% длительности льда",
                "и +20% к прямому урону Ледяной башни за ранг!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 2.7:.1f}% замедл., +{lvl * 10}% длит." if lvl > 0 else "Базовый мороз",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 2.7:.1f}% замедл., +{(lvl + 1) * 10}% длит.",
            "icon_key": "frost"
        },
        "frost_linger": {
            "title": "Остаточный Холод",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510, "y": 540,
            "max_lvl": 5,
            "costs": [3, 6, 11, 18, 27],
            "requires": {'freeze_tower': 'max'},
            "desc": [
                "Ледяная корка удерживает мороз.",
                "+0.15с за ранг к сохранению замедления",
                "после выхода врагов из радиуса башни (до +0.75с)!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 0.15:.2f}с остаточного замедления" if lvl > 0 else "Базовое рассеивание",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 0.15:.2f}с остаточного замедления",
            "icon_key": "frost"
        },

        # ---------------- 4. КАКТУСОВАЯ ФЕРМА (Y = 720) ----------------
        "farm_tower": {
            "title": "Кактусовая Ферма",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.3,
            "x": 350, "y": 720,
            "max_lvl": 1,
            "costs": [5],
            "requires": {'freeze_tower': 'max'},
            "desc": [
                "Экономическая плантация кактусов.",
                "Приносит пассивный доход в конце каждой волны.",
                "Позволяет инвестировать и окупать защиту!"
            ],
            "stat_cur": lambda lvl: "Постройка разблокирована",
            "stat_nxt": lambda lvl: "Разблокировать Кактусовую Ферму",
            "icon_key": "farm_tower"
        },
        "fertile_soil": {
            "title": "Плодородная Почва",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190, "y": 720,
            "max_lvl": 5,
            "costs": [4, 8, 14, 22, 34],
            "requires": {'farm_tower': 'max'},
            "desc": [
                "Обогащение почвы минералами пустыни.",
                "+10% к доходу всех Кактусовых Ферм за ранг,",
                "а также усиливает бонус от полива!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 10}% к доходу Ферм" if lvl > 0 else "Базовый урожай",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 10}% к доходу Ферм",
            "icon_key": "soil"
        },
        "compound_interest": {
            "title": "Кактусовый Вклад",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 40, "y": 720,
            "max_lvl": 3,
            "costs": [6, 15, 30],
            "requires": {'fertile_soil': 2},
            "desc": [
                "Банковская система оазиса.",
                "+3% дивидендов от текущей казны в конце",
                "каждой волны за каждый изученный уровень!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 3}% дивидендов в конце волны" if lvl > 0 else "Нет процентов по вкладу",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 3}% дивидендов в конце волны",
            "icon_key": "coin"
        },
        "farm_irrigation": {
            "title": "Система Орошения",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510, "y": 720,
            "max_lvl": 3,
            "costs": [6, 14, 26],
            "requires": {'farm_tower': 'max'},
            "desc": [
                "Капельный полив окружающих башен.",
                "Ферма ускоряет башни в радиусе на +8%/+14%/+20%",
                "и периодически выбрасывает плоды кактусов!"
            ],
            "stat_cur": lambda lvl: f"Орошение: +{[0, 8, 14, 20][lvl]}% темпа башням" if lvl > 0 else "Ферма без полива",
            "stat_nxt": lambda lvl: f"Орошение: +{[0, 8, 14, 20][lvl + 1]}% темпа башням",
            "icon_key": "irrigation"
        },
        "golden_fortune": {
            "title": "Золотая Фортуна",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 660, "y": 720,
            "max_lvl": 2,
            "costs": [10, 25],
            "requires": {'farm_irrigation': 1},
            "desc": [
                "Легендарные золотые кактусы.",
                "С Золотых Слаймов выпадает дополнительный",
                "Звёздный Кактус с шансом 50% / 100%!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 50}% шанс на доп. Звёздный Кактус" if lvl > 0 else "Базовый дроп с золотых",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 50}% шанс на доп. Звёздный Кактус",
            "icon_key": "golden"
        },

        # ---------------- 5. ПАЛАТКА СОЛДАТ (Y = 900) ----------------
        "tent_tower": {
            "title": "Палатка Солдат",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.3,
            "x": 350, "y": 900,
            "max_lvl": 1,
            "costs": [4],
            "requires": {'farm_tower': 'max'},
            "desc": [
                "Казармы гарнизона оазиса.",
                "Призывает отважных стражей на дорогу.",
                "Блокируют проход мобов и сражаются врукопашную!"
            ],
            "stat_cur": lambda lvl: "Постройка разблокирована",
            "stat_nxt": lambda lvl: "Разблокировать Палатку Солдат",
            "icon_key": "tent_tower"
        },
        "knight_training": {
            "title": "Орден Защитников",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190, "y": 900,
            "max_lvl": 5,
            "costs": [3, 7, 12, 19, 30],
            "requires": {'tent_tower': 'max'},
            "desc": [
                "Тяжелое обмундирование пехотинцев.",
                "+10 HP, +15% урона и -6% входящего урона",
                "по воинам за каждый изученный уровень!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 10} HP, +{lvl * 15}% урона, -{lvl * 6}% урона" if lvl > 0 else "Новобранцы без брони",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 10} HP, +{(lvl + 1) * 15}% урона, -{(lvl + 1) * 6}% урона",
            "icon_key": "sword"
        },
        "shield_wall": {
            "title": "Стена Щитов",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 40, "y": 900,
            "max_lvl": 3,
            "costs": [5, 12, 22],
            "requires": {'knight_training': 2},
            "desc": [
                "Монолитные щиты гарнизона.",
                "Дает всем призванным воинам дополнительный",
                "энергетический щит на +30 HP за уровень!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 30} HP щита каждому воину" if lvl > 0 else "Без щитовой защиты",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 30} HP щита каждому воину",
            "icon_key": "shield"
        },
        "tent_thorns": {
            "title": "Шипастая Защита",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510, "y": 900,
            "max_lvl": 3,
            "costs": [4, 9, 16],
            "requires": {'tent_tower': 'max'},
            "desc": [
                "Броня солдат покрыта кактусовыми шипами.",
                "Отражает 25% урона обратно атакующим слаймам",
                "за каждый ранг улучшения!"
            ],
            "stat_cur": lambda lvl: f"Возврат {lvl * 25}% урона мобам" if lvl > 0 else "Обычные латы",
            "stat_nxt": lambda lvl: f"Возврат {(lvl + 1) * 25}% урона мобам",
            "icon_key": "spikes"
        },
        "rally_range": {
            "title": "Призывной Горн",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 660, "y": 900,
            "max_lvl": 4,
            "costs": [3, 7, 13, 22],
            "requires": {'tent_tower': 'max'},
            "desc": [
                "Звон горна направляет бойцов дальше.",
                "+25 px за ранг к радиусу выставления флага",
                "сбора гарнизона (до +100 px к дальности)!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 25} px к дальности флага палатки" if lvl > 0 else "Базовый радиус флага",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 25} px к дальности флага палатки",
            "icon_key": "optics"
        },

        # ---------------- 6. БАШНЯ ТЕСЛА (Y = 1080) ----------------
        "tesla_tower": {
            "title": "Башня Тесла",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.3,
            "x": 350, "y": 1080,
            "max_lvl": 1,
            "costs": [6],
            "requires": {'tent_tower': 'max'},
            "desc": [
                "Генератор высоковольтных разрядов.",
                "Выпускает цепную молнию, рикошетящую",
                "по цепочке ближайших слаймов!"
            ],
            "stat_cur": lambda lvl: "Постройка разблокирована",
            "stat_nxt": lambda lvl: "Разблокировать Башню Тесла",
            "icon_key": "tesla_tower"
        },
        "ball_lightning": {
            "title": "Шаровая Молния",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190, "y": 1080,
            "max_lvl": 5,
            "costs": [4, 9, 16, 26, 40],
            "requires": {'tesla_tower': 'max'},
            "desc": [
                "Сферическая плазменная катушка.",
                "+12% к урону разряда и +18 px к дальности",
                "атаки Башни Тесла за каждый уровень!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 12}% урона, +{lvl * 18} px дальности" if lvl > 0 else "Базовые разряды",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 12}% урона, +{(lvl + 1) * 18} px дальности",
            "icon_key": "lightning"
        },
        "overcharge": {
            "title": "Перегрузка Сети",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510, "y": 1080,
            "max_lvl": 3,
            "costs": [6, 14, 26],
            "requires": {'tesla_tower': 'max'},
            "desc": [
                "Дополнительные каскадные конденсаторы.",
                "+1 цель для рикошета цепной молнии",
                "за каждый изученный уровень улучшения!"
            ],
            "stat_cur": lambda lvl: f"+{lvl} доп. цели для молнии" if lvl > 0 else "Базовое число целей",
            "stat_nxt": lambda lvl: f"+{lvl + 1} доп. цели для молнии",
            "icon_key": "overcharge"
        },
        "superconductor": {
            "title": "Сверхпроводник",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 660, "y": 1080,
            "max_lvl": 3,
            "costs": [8, 18, 35],
            "requires": {'overcharge': 2, 'ball_lightning': 2},
            "desc": [
                "Нулевое сопротивление плазменной цепи.",
                "Снижает потерю урона при каждом прыжке молнии:",
                "с 35% за прыжок до 25% / 18% / 10%!"
            ],
            "stat_cur": lambda lvl: f"Сохранение силы: {[65, 75, 82, 90][lvl]}% за прыжок" if lvl > 0 else "Базовое угасание дуги",
            "stat_nxt": lambda lvl: f"Сохранение силы: {[65, 75, 82, 90][lvl + 1]}% за прыжок",
            "icon_key": "superconductor"
        },

        # ---------------- 7. ОБЕЛИСК СОЛНЦА (Y = 1260) ----------------
        "sun_tower": {
            "title": "Обелиск Солнца",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.4,
            "x": 350, "y": 1260,
            "max_lvl": 1,
            "costs": [8],
            "requires": {'tesla_tower': 'max'},
            "desc": [
                "Древний монумент солярной энергии.",
                "Фокусирует непрерывный луч, наносящий урон",
                "10 раз в секунду и разгоняющийся по одной цели!"
            ],
            "stat_cur": lambda lvl: "Постройка разблокирована",
            "stat_nxt": lambda lvl: "Разблокировать Обелиск Солнца",
            "icon_key": "sun_tower"
        },
        "solar_focus": {
            "title": "Солярный Фокус",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190, "y": 1260,
            "max_lvl": 5,
            "costs": [4, 8, 15, 25, 38],
            "requires": {'sun_tower': 1},
            "desc": [
                "Кварцевые оптические линзы обелиска.",
                "Ускоряет разгон урона луча на -0.05с за 1x",
                "за каждый ранг (до -0.25с к набору силы)!"
            ],
            "stat_cur": lambda lvl: f"-{lvl * 0.05:.2f}с к набору 1x урона луча" if lvl > 0 else "Базовая скорость разгона",
            "stat_nxt": lambda lvl: f"-{(lvl + 1) * 0.05:.2f}с к набору 1x урона луча",
            "icon_key": "optics"
        },
        "solar_trail": {
            "title": "Солнечный След",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 40, "y": 1260,
            "max_lvl": 4,
            "costs": [5, 12, 22, 35],
            "requires": {'solar_focus': 2},
            "desc": [
                "Термальная детонация погибшей цели.",
                "При гибели от луча моб взрывается в радиусе",
                "50 px на 2.5% .. 10% от своего макс. HP!"
            ],
            "stat_cur": lambda lvl: f"Взрыв при гибели: {lvl * 2.5:.1f}% max HP цели" if lvl > 0 else "Без солярного взрыва",
            "stat_nxt": lambda lvl: f"Взрыв при гибели: {(lvl + 1) * 2.5:.1f}% max HP цели",
            "icon_key": "inferno"
        },
        "beam_limit": {
            "title": "Предел Луча",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510, "y": 1260,
            "max_lvl": 5,
            "costs": [5, 10, 18, 30, 45],
            "requires": {'sun_tower': 1},
            "desc": [
                "Калибровка сверхкритической мощности.",
                "Увеличивает потолок множителя урона луча",
                "на +0.5x за ранг (с базовых x2.5 до x5.0)!"
            ],
            "stat_cur": lambda lvl: f"Потолок разогрева луча: x{2.5 + lvl * 0.5:.1f}" if lvl > 0 else "Базовый предел x2.5",
            "stat_nxt": lambda lvl: f"Потолок разогрева луча: x{2.5 + (lvl + 1) * 0.5:.1f}",
            "icon_key": "overcharge"
        },

        # ---------------- ОБОРОНА И ТАКТИКА (COMBAT) ----------------
        "speed_limit": {
            "title": "Контроль Темпа",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -500, "y": 140,
            "max_lvl": 3,
            "costs": [2, 4, 8],
            "requires": {'oasis_core': 1},
            "desc": [
                "Управление скоростью течения боя.",
                "Открывает дополнительные режимы ускорения x2.5,",
                "x3.0 и x4.0 для комфортной игры!"
            ],
            "stat_cur": lambda lvl: f"Макс. скорость: {[1.5, 2.5, 3.0, 4.0][lvl]}x" if lvl > 0 else "Базовая скорость 1.5x",
            "stat_nxt": lambda lvl: f"Макс. скорость: {[1.5, 2.5, 3.0, 4.0][lvl + 1]}x",
            "icon_key": "speed"
        },
        "spawn_rush": {
            "title": "Ритм Волны",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -640, "y": 140,
            "max_lvl": 3,
            "costs": [3, 7, 14],
            "requires": {'speed_limit': 3},
            "desc": [
                "Уплотнение набегов врагов.",
                "Ускоряет интервал между выходом слаймов на волне",
                "на +15% / +30% / +45% для динамичных боев."
            ],
            "stat_cur": lambda lvl: f"Выход слаймов ускорен на +{lvl * 15}%" if lvl > 0 else "Обычный интервал спавна",
            "stat_nxt": lambda lvl: f"Выход слаймов ускорен на +{(lvl + 1) * 15}%",
            "icon_key": "speed"
        },
        "wave_rush": {
            "title": "Без Пауз",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -360, "y": 140,
            "max_lvl": 3,
            "costs": [3, 7, 14],
            "requires": {'speed_limit': 3},
            "desc": [
                "Непрерывный штурм оазиса.",
                "Сокращает перерыв между волнами до 3.0с,",
                "1.5с или мгновенного старта (0.5с)!"
            ],
            "stat_cur": lambda lvl: f"Перерыв между волнами: {[5.0, 3.0, 1.5, 0.5][lvl]}с" if lvl > 0 else "Базовый перерыв 5.0с",
            "stat_nxt": lambda lvl: f"Перерыв между волнами: {[5.0, 3.0, 1.5, 0.5][lvl + 1]}с",
            "icon_key": "speed"
        },
        "base_health": {
            "title": "Ограда Оазиса",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -500, "y": 280,
            "max_lvl": 5,
            "costs": [1, 2, 4, 7, 11],
            "requires": {'oasis_core': 1},
            "desc": [
                "Укрепление частокола вокруг оазиса.",
                "+3 к максимальному запасу жизней оазиса",
                "за каждый изученный ранг!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 3} HP оазиса" if lvl > 0 else "Базовый запас жизней",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 3} HP оазиса",
            "icon_key": "heart"
        },
        "global_damage": {
            "title": "Оружейный Арсенал",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -640, "y": 430,
            "max_lvl": 5,
            "costs": [2, 5, 9, 15, 24],
            "requires": {'base_health': 1},
            "desc": [
                "Заточка наконечников и калибровка орудий.",
                "+5% к урону всех башен, казарм и дронов",
                "за каждый изученный ранг!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 5}% к урону всех орудий" if lvl > 0 else "Базовый урон оазиса",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 5}% к урону всех орудий",
            "icon_key": "sword"
        },
        "critical_mastery": {
            "title": "Критический Удар",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -500, "y": 430,
            "max_lvl": 5,
            "costs": [3, 6, 12, 20, 32],
            "requires": {'base_health': 2},
            "desc": [
                "Поиск уязвимых точек слаймов.",
                "+2.5% к шансу крита и +0.15 к множителю",
                "критического урона башен за ранг!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 2.5:.1f}% шанс крита, +{lvl * 0.15:.2f}x урон" if lvl > 0 else "Базовые криты",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 2.5:.1f}% шанс крита, +{(lvl + 1) * 0.15:.2f}x урон",
            "icon_key": "target"
        },
        "thorn_armor": {
            "title": "Колючий Частокол",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -360, "y": 430,
            "max_lvl": 3,
            "costs": [3, 7, 14],
            "requires": {'base_health': 2},
            "desc": [
                "Стены базы покрыты ядовитыми иглами.",
                "При получении урона оазис выпускает шипы,",
                "наносящие 150 / 220 / 290 урона всем мобам!"
            ],
            "stat_cur": lambda lvl: f"Ответный залп: {[0, 150, 220, 290][lvl]} урона" if lvl > 0 else "Частокол без шипов",
            "stat_nxt": lambda lvl: f"Ответный залп: {[0, 150, 220, 290][lvl + 1]} урона",
            "icon_key": "spikes"
        },
        "regeneration": {
            "title": "Регенерация Оазиса",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -640, "y": 570,
            "max_lvl": 3,
            "costs": [4, 9, 18],
            "requires": {'global_damage': 2, 'base_health': 3},
            "desc": [
                "Живительные воды восстанавливают базу.",
                "Восстанавливает +1/+2/+3 HP базе каждые",
                "5 успешно отраженных волн!"
            ],
            "stat_cur": lambda lvl: f"Лечение: +{lvl} HP каждые 5 волн" if lvl > 0 else "Нет автолечения базы",
            "stat_nxt": lambda lvl: f"Лечение: +{lvl + 1} HP каждые 5 волн",
            "icon_key": "heart"
        },
        "giant_hunter": {
            "title": "Охотник на Боссов",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -500, "y": 570,
            "max_lvl": 3,
            "costs": [5, 12, 24],
            "requires": {'critical_mastery': 2},
            "desc": [
                "Тактика противостояния гигантам.",
                "+10% к урону всех башен по боссам и элитным",
                "слаймам за каждый изученный уровень!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 10}% урона по боссам и элитам" if lvl > 0 else "Базовый урон по боссам",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 10}% урона по боссам и элитам",
            "icon_key": "sword"
        },
        "range_grid": {
            "title": "Дозорные Вышки",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -360, "y": 570,
            "max_lvl": 3,
            "costs": [4, 9, 17],
            "requires": {'thorn_armor': 1},
            "desc": [
                "Высокие обзорные помосты оазиса.",
                "Увеличивает радиус действия всех башен",
                "на +6 px за каждый изученный уровень!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 6} px к радиусу всех башен" if lvl > 0 else "Базовые сектора обзора",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 6} px к радиусу всех башен",
            "icon_key": "optics"
        },
        "smart_targeting": {
            "title": "Умное Наведение",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -500, "y": 710,
            "max_lvl": 2,
            "costs": [4, 10],
            "requires": {'critical_mastery': 1},
            "desc": [
                "Тактический выбор целей для башен.",
                "Открывает режимы: Сильный / Слабый / Близкий,",
                "а ур. 2 дает +10% урона по сильным целям!"
            ],
            "stat_cur": lambda lvl: "Приоритеты + 10% урона по сильным" if lvl >= 2 else ("Приоритеты целей открыты" if lvl == 1 else "Только первый / последний"),
            "stat_nxt": lambda lvl: "Открыть режимы приоритетов целей" if lvl == 0 else "+10% урона в режиме 'Сильный'",
            "icon_key": "target"
        },
        "elemental_focus": {
            "title": "Элементный Фокус",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -360, "y": 710,
            "max_lvl": 1,
            "costs": [7],
            "requires": {'range_grid': 1},
            "desc": [
                "Синергия льда и огня.",
                "Огненные башни бьют по замороженным врагам,",
                "а Ледяные выбирают ещё не замедленные цели!"
            ],
            "stat_cur": lambda lvl: "Тактическая синергия активна" if lvl > 0 else "Башни стреляют хаотично",
            "stat_nxt": lambda lvl: "Активировать элементную синергию",
            "icon_key": "frost"
        },
        "bestiary_damage": {
            "title": "Анатомия Слаймов",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -640, "y": 710,
            "max_lvl": 3,
            "costs": [4, 9, 18],
            "requires": {'smart_targeting': 1},
            "desc": [
                "Знание слабых мест бестиария.",
                "+1% / +2% / +3% к урону по каждому существу",
                "за каждый открытый тир его бестиария (до +30%)!"
            ],
            "stat_cur": lambda lvl: f"+{lvl}% урона за тир бестиария цели" if lvl > 0 else "Базовый урон бестиария",
            "stat_nxt": lambda lvl: f"+{lvl + 1}% урона за тир бестиария цели",
            "icon_key": "sword"
        },

        # ---------------- ЭКОНОМИКА ОАЗИСА (ECON) ----------------
        "start_cacti": {
            "title": "Стартовая Казна",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1080, "y": 200,
            "max_lvl": 5,
            "costs": [1, 2, 4, 7, 12],
            "requires": {'oasis_core': 1},
            "desc": [
                "Начальный запас кактусов в экспедиции.",
                "+25 кактусов в казну на старте игры",
                "за каждый изученный уровень улучшения!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 25} кактусов на старте забега" if lvl > 0 else "Стандартная казна 200 какт.",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 25} кактусов на старте забега",
            "icon_key": "coin"
        },
        "wave_clearing_bounty": {
            "title": "Премия за Волну",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 960, "y": 350,
            "max_lvl": 5,
            "costs": [2, 4, 7, 12, 19],
            "requires": {'start_cacti': 1},
            "desc": [
                "Награда за успешную оборону волны.",
                "+25 кактусов (масштабируется волной)",
                "в казну за каждую зачищенную волну!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 25} кактусов за волну" if lvl > 0 else "Базовая награда за волны",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 25} кактусов за волну",
            "icon_key": "coin"
        },
        "start_wave_step": {
            "title": "Быстрый Старт",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1080, "y": 350,
            "max_lvl": 3,
            "costs": [3, 8, 16],
            "requires": {'start_cacti': 1},
            "desc": [
                "Пропуск начальных тренировочных волн.",
                "Позволяет начинать забег сразу с 6, 11 или 16",
                "волны с начислением всей стартовой валюты!"
            ],
            "stat_cur": lambda lvl: f"Старт забега: {[1, 6, 11, 16][lvl]} волна" if lvl > 0 else "Старт с 1 волны",
            "stat_nxt": lambda lvl: f"Старт забега: {[1, 6, 11, 16][lvl + 1]} волна",
            "icon_key": "speed"
        },
        "cacti_bounty": {
            "title": "Щедрая Пустыня",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1200, "y": 350,
            "max_lvl": 5,
            "costs": [2, 5, 9, 15, 24],
            "requires": {'start_cacti': 2},
            "desc": [
                "Сбор кактусов с поверженных врагов.",
                "+10% к выпадению кактусов со всех слаймов",
                "за каждый изученный уровень улучшения!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 10}% кактусов за поверженных мобов" if lvl > 0 else "Базовая добыча с врагов",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 10}% кактусов за поверженных мобов",
            "icon_key": "cactus"
        },
        "stellar_magnet": {
            "title": "Звёздный Магнит",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1080, "y": 500,
            "max_lvl": 5,
            "costs": [3, 7, 13, 21, 32],
            "requires": {'cacti_bounty': 3},
            "desc": [
                "Притяжение звёздной энергии слаймов.",
                "+10% к общему шансу выпадения редких",
                "Звёздных Кактусов за каждый ранг!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 10}% к шансу Звёздных Кактусов" if lvl > 0 else "Базовый шанс дропа звезд",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 10}% к шансу Звёздных Кактусов",
            "icon_key": "stellar"
        },
        "star_alchemy": {
            "title": "Звёздная Алхимия",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1080, "y": 650,
            "max_lvl": 3,
            "costs": [6, 14, 28],
            "requires": {'stellar_magnet': 2},
            "desc": [
                "Преобразование космической пыли.",
                "Дарит +1 гарантированный Звёздный Кактус",
                "каждые 5 / 4 / 3 успешно завершенных волн!"
            ],
            "stat_cur": lambda lvl: f"+1 Звёздный Кактус каждые {[0, 5, 4, 3][lvl]} волн" if lvl > 0 else "Без алхимии звёзд",
            "stat_nxt": lambda lvl: f"+1 Звёздный Кактус каждые {[0, 5, 4, 3][lvl + 1]} волн",
            "icon_key": "stellar"
        },
        "bestiary_cacti": {
            "title": "Охотничья Премия",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1200, "y": 500,
            "max_lvl": 3,
            "costs": [3, 7, 14],
            "requires": {'cacti_bounty': 2},
            "desc": [
                "Бонус за изучение популяции пустыни.",
                "+1% / +2% / +3% обычных кактусов за моба",
                "за каждый открытый тир его бестиария!"
            ],
            "stat_cur": lambda lvl: f"+{lvl}% кактусов за тир бестиария моба" if lvl > 0 else "Базовые награды",
            "stat_nxt": lambda lvl: f"+{lvl + 1}% кактусов за тир бестиария моба",
            "icon_key": "cactus"
        },
        "bestiary_stars": {
            "title": "Звёздный Трофей",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1200, "y": 650,
            "max_lvl": 3,
            "costs": [5, 12, 24],
            "requires": {'stellar_magnet': 2},
            "desc": [
                "Редкие кристаллы в телах монстров.",
                "+1% / +2% / +3% к шансу Звёздного кактуса",
                "за каждый открытый тир бестиария монстра!"
            ],
            "stat_cur": lambda lvl: f"+{lvl}% к шансу звёзд за тир бестиария" if lvl > 0 else "Базовый шанс трофея",
            "stat_nxt": lambda lvl: f"+{lvl + 1}% к шансу звёзд за тир бестиария",
            "icon_key": "stellar"
        },

        # ---------------- ОРАНЖЕРЕЯ И ФЛОРА (FLORA) ----------------
        "greenhouse_unlock": {
            "title": "Оранжерея Оазиса",
            "branch": "flora",
            "branch_title": "Оранжерея и Флора",
            "scale": 1.5,
            "x": 1080, "y": 950,
            "max_lvl": 1,
            "costs": [5],
            "requires": {'farm_irrigation': 1},
            "desc": [
                "Святилище кактусовой селекции.",
                "Открывает режим Оранжереи: выращивание уникальных",
                "видов кактусов, дающих постоянные бонусы!"
            ],
            "stat_cur": lambda lvl: "Оранжерея построена и активна",
            "stat_nxt": lambda lvl: "Построить Оранжерею Оазиса",
            "icon_key": "greenhouse"
        },
        "botanical_expeditions": {
            "title": "Экспедиции за Семенами",
            "branch": "flora",
            "branch_title": "Оранжерея и Флора",
            "x": 950, "y": 1100,
            "max_lvl": 3,
            "costs": [4, 9, 18],
            "requires": {'greenhouse_unlock': 'max'},
            "desc": [
                "Поиски редких образцов флоры в пустыне.",
                "+1.0% к шансу выпадения саженца с элитных мобов",
                "за каждый изученный ранг улучшения!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 1.0:.1f}% к шансу саженца с элит" if lvl > 0 else "Базовый шанс саженцев",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 1.0:.1f}% к шансу саженца с элит",
            "icon_key": "sprout"
        },
        "fertile_compost": {
            "title": "Живой Компост",
            "branch": "flora",
            "branch_title": "Оранжерея и Флора",
            "x": 1080, "y": 1100,
            "max_lvl": 3,
            "costs": [5, 11, 20],
            "requires": {'greenhouse_unlock': 'max'},
            "desc": [
                "Питательный субстрат для всех растений.",
                "+20% к скорости созревания всех кактусов",
                "в Оранжерее за каждый ранг улучшения!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 20}% к скорости созревания" if lvl > 0 else "Обычный темп роста",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 20}% к скорости созревания",
            "icon_key": "compost"
        },
        "sprout_harvest": {
            "title": "Обильный Сбор",
            "branch": "flora",
            "branch_title": "Оранжерея и Флора",
            "x": 1210, "y": 1100,
            "max_lvl": 3,
            "costs": [6, 14, 25],
            "requires": {'greenhouse_unlock': 'max'},
            "desc": [
                "Бережный сбор семян с боссов.",
                "+1 дополнительный случайный саженец в награду",
                "за победу над каждым боссом волны!"
            ],
            "stat_cur": lambda lvl: f"+{lvl} доп. саженца с каждого босса" if lvl > 0 else "Стандартная награда с босса",
            "stat_nxt": lambda lvl: f"+{lvl + 1} доп. саженца с каждого босса",
            "icon_key": "sprout"
        },
        "flora_resonance": {
            "title": "Резонанс Флоры",
            "branch": "flora",
            "branch_title": "Оранжерея и Флора",
            "x": 1080, "y": 1250,
            "max_lvl": 3,
            "costs": [8, 18, 35],
            "requires": {'greenhouse_unlock': 'max'},
            "desc": [
                "Единство всех выращенных растений.",
                "+15% к эффективности всех пассивных бонусов",
                "зрелых кактусов в вашей коллекции!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 15}% к силе бонусов оранжереи" if lvl > 0 else "Базовая сила бонусов",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 15}% к силе бонусов оранжереи",
            "icon_key": "greenhouse"
        },
        "botanic_harvest": {
            "title": "Ботанический Сбор",
            "branch": "flora",
            "branch_title": "Оранжерея и Флора",
            "x": 1210, "y": 1250,
            "max_lvl": 3,
            "costs": [5, 12, 22],
            "requires": {'sprout_harvest': 2},
            "desc": [
                "Регулярные поставки редких всходов.",
                "Каждые 20 / 15 / 10 волн дарят +1 росток",
                "случайного кактуса для Оранжереи!"
            ],
            "stat_cur": lambda lvl: f"+1 росток каждые {[0, 20, 15, 10][lvl]} волн" if lvl > 0 else "Без регулярных всходов",
            "stat_nxt": lambda lvl: f"+1 росток каждые {[0, 20, 15, 10][lvl + 1]} волн",
            "icon_key": "sprout"
        },

        # ---------------- МУЗЕЙ РЕЛИКВИЙ (RELICS) ----------------
        "archaeology_unlock": {
            "title": "Музей Реликвий",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "scale": 1.5,
            "x": 1750, "y": 350,
            "max_lvl": 1,
            "costs": [5],
            "requires": {'start_cacti': 1},
            "desc": [
                "Раскопки древней цивилизации пустыни.",
                "Открывает доступ к местам раскопок на картах",
                "и пьедесталам для размещения найденных реликвий!"
            ],
            "stat_cur": lambda lvl: "Археология разблокирована",
            "stat_nxt": lambda lvl: "Открыть Музей Реликвий",
            "icon_key": "shovel"
        },
        "dig_site_duration": {
            "title": "Крепкие Шурфы",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "x": 1620, "y": 500,
            "max_lvl": 3,
            "costs": [3, 7, 14],
            "requires": {'archaeology_unlock': 'max'},
            "desc": [
                "Укрепление стенок раскопа от засыпания.",
                "+4с к длительности активности места раскопок",
                "на игровой карте за каждый изученный уровень!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 4}с к времени раскопок" if lvl > 0 else "Базовые 12 секунд",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 4}с к времени раскопок",
            "icon_key": "shovel"
        },
        "dig_minigame_buff": {
            "title": "Георадар",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "x": 1750, "y": 500,
            "max_lvl": 3,
            "costs": [4, 9, 18],
            "requires": {'archaeology_unlock': 'max'},
            "desc": [
                "Улучшенное сканирование слоёв песка.",
                "+1 дополнительный ход и +1 взрыв динамита",
                "в мини-игре раскопок за каждый изученный уровень!"
            ],
            "stat_cur": lambda lvl: f"+{lvl} ходов и +{lvl} динамита" if lvl > 0 else "Базовый набор инструментов",
            "stat_nxt": lambda lvl: f"+{lvl + 1} ходов и +{lvl + 1} динамита",
            "icon_key": "relic_pedestal"
        },
        "dig_site_chance": {
            "title": "Золотая Жила",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "x": 1880, "y": 500,
            "max_lvl": 3,
            "costs": [4, 9, 18],
            "requires": {'archaeology_unlock': 'max'},
            "desc": [
                "Частое обнаружение древних пластов.",
                "+15% к шансу появления раскопок на волне",
                "и уменьшение времени между раскопками!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 15}% к шансу раскопок" if lvl > 0 else "Обычный шанс появления",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 15}% к шансу раскопок",
            "icon_key": "relic_pedestal"
        },
        "relic_pedestals": {
            "title": "Пьедесталы Экспонатов",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "x": 1620, "y": 650,
            "max_lvl": 2,
            "costs": [6, 15],
            "requires": {'archaeology_unlock': 'max'},
            "desc": [
                "Мраморные постаменты зала славы.",
                "+1 активный слот для размещения реликвий",
                "за каждый изученный уровень улучшения!"
            ],
            "stat_cur": lambda lvl: f"Активных слотов: {2 + lvl}" if lvl > 0 else "Базовые 2 слота",
            "stat_nxt": lambda lvl: f"Активных слотов: {3 + lvl}",
            "icon_key": "relic_pedestal"
        },
        "relic_max_level": {
            "title": "Реставрация Артефактов",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "x": 1750, "y": 650,
            "max_lvl": 3,
            "costs": [5, 12, 22],
            "requires": {'archaeology_unlock': 'max'},
            "desc": [
                "Мастерство восстановления реликвий.",
                "Повышает максимальный уровень прокачки",
                "всех реликвий на +1 за каждый изученный ранг!"
            ],
            "stat_cur": lambda lvl: f"+{lvl} к макс. уровню реликвий" if lvl > 0 else "Базовый предел (3 ур.)",
            "stat_nxt": lambda lvl: f"+{lvl + 1} к макс. уровню реликвий",
            "icon_key": "relic_pedestal"
        },
        "relic_double_drop": {
            "title": "Двойная Находка",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "x": 1880, "y": 650,
            "max_lvl": 2,
            "costs": [8, 20],
            "requires": {'relic_max_level': 2},
            "desc": [
                "Богатые схроны древних сокровищниц.",
                "С шансом 25% / 50% найденный артефакт приносит",
                "сразу два фрагмента вместо одного!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 25}% шанс двойного фрагмента" if lvl > 0 else "Одиночные фрагменты",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 25}% шанс двойного фрагмента",
            "icon_key": "relic_pedestal"
        },
        "dark_relic_resonance": {
            "title": "Тёмный Резонанс Реликвий",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "currency": "dark",
            "x": 1750, "y": 800,
            "max_lvl": 2,
            "costs": [10, 25],
            "requires": {'relic_pedestals': 2, 'relic_max_level': 2},
            "desc": [
                "Насыщение реликвий энергией Бездны.",
                "+25% к силе пассивных эффектов всех реликвий",
                "за каждый ранг улучшения!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 25}% к силе эффектов реликвий" if lvl > 0 else "Базовая сила артефактов",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 25}% к силе эффектов реликвий",
            "icon_key": "dark_matter"
        },
        "sonar_ping": {
            "title": "Око Бездны",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "currency": "dark",
            "x": 1880, "y": 800,
            "max_lvl": 1,
            "costs": [8],
            "requires": {'archaeology_unlock': 'max'},
            "desc": [
                "Тёмный компас сквозь песчаные дюны.",
                "При раскопке пустой клетки стрелка",
                "указывает на ближайший скрытый артефакт!"
            ],
            "stat_cur": lambda lvl: "Око Бездны указывает на артефакты" if lvl > 0 else "Раскопки вслепую",
            "stat_nxt": lambda lvl: "Активировать Око Бездны для раскопок",
            "icon_key": "shovel"
        },

        # ---------------- ТЁМНЫЙ КОСМОС (ASTRAL) ----------------
        "astral_beacon": {
            "title": "Астральный Маяк",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "scale": 1.5,
            "x": 350, "y": 1520,
            "max_lvl": 1,
            "costs": [8],
            "requires": {'sun_tower': 1},
            "desc": [
                "Притягивает космические метеориты.",
                "Начиная с 20 волны на карте будут падать",
                "Астральные Метеориты с ценной тёмной материей!"
            ],
            "stat_cur": lambda lvl: "Астральные Метеориты падают на волнах",
            "stat_nxt": lambda lvl: "Запустить Астральный Маяк",
            "icon_key": "astral_beacon"
        },
        "dark_aegis": {
            "title": "Тёмный Эгис",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "x": 220, "y": 1670,
            "max_lvl": 3,
            "costs": [4, 9, 18],
            "requires": {'astral_beacon': 'max'},
            "desc": [
                "Гравитационный барьер вокруг оазиса.",
                "Поглощает 1/2/3 прорыва врагов за забег,",
                "полностью спасая базу от потери жизней!"
            ],
            "stat_cur": lambda lvl: f"Щит поглощает {lvl} прорыва мобов" if lvl > 0 else "Нет защитного барьера",
            "stat_nxt": lambda lvl: f"Щит поглотит {lvl + 1} прорыва мобов",
            "icon_key": "shield"
        },
        "gravity_well": {
            "title": "Гравитационный Колодцы",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "x": 480, "y": 1670,
            "max_lvl": 3,
            "costs": [4, 9, 18],
            "requires": {'astral_beacon': 'max'},
            "desc": [
                "Колебания гравитационного поля пустыни.",
                "Увеличивает частоту падения метеоритов на 25%",
                "и расширяет окно для их разрушения!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 25}% к частоте метеоритов" if lvl > 0 else "Обычный темп падения",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 25}% к частоте метеоритов",
            "icon_key": "void"
        },
        "orbital_strike": {
            "title": "Орбитальный Удар",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "scale": 1.2,
            "x": 350, "y": 1670,
            "max_lvl": 3,
            "costs": [6, 14, 28],
            "requires": {'astral_beacon': 'max'},
            "desc": [
                "Активная способность: Орбитальный Лазер [F].",
                "Вызывает разрушительный удар из космоса,",
                "сжигающий волну врагов на пути!"
            ],
            "stat_cur": lambda lvl: f"Орбита: 250 ур. (КД: {[60, 45, 35, 25][lvl]}с)" if lvl > 0 else "Орбита заблокирована",
            "stat_nxt": lambda lvl: f"Орбита: 250 ур. (КД: {[60, 45, 35, 25][lvl + 1]}с)",
            "icon_key": "orbital"
        },
        "dark_vitality": {
            "title": "Тёмная Живучесть",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "dark",
            "x": 100, "y": 1820,
            "max_lvl": 2,
            "costs": [5, 10],
            "requires": {'dark_aegis': 1},
            "desc": [
                "Укрепление оазиса тёмной материей.",
                "+5 HP к базовому здоровью оазиса за уровень",
                "(до +10 постоянных жизней базы)!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 5} HP к базе оазиса" if lvl > 0 else "Базовое здоровье",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 5} HP к базе оазиса",
            "icon_key": "heart"
        },
        "cactus_drone": {
            "title": "Кактусовый Дрон",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "x": 220, "y": 1820,
            "max_lvl": 3,
            "costs": [5, 12, 24],
            "requires": {'orbital_strike': 1},
            "desc": [
                "Автономный охранный спутник оазиса.",
                "Патрулирует периметр базы и непрерывно",
                "обстреливает ближайших врагов иглами!"
            ],
            "stat_cur": lambda lvl: f"Дрон L{lvl} (урон: {2 + lvl * 1.5})" if lvl > 0 else "Дрон не собран",
            "stat_nxt": lambda lvl: f"Дрон L{lvl + 1} (урон: {2 + (lvl + 1) * 1.5})",
            "icon_key": "drone"
        },
        "shatter_nova": {
            "title": "Осколочная Нова",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "x": 480, "y": 1820,
            "max_lvl": 3,
            "costs": [5, 11, 22],
            "requires": {'orbital_strike': 1},
            "desc": [
                "Метеоритные осколки при взрывах.",
                "При гибели мобов с шансом 15%/30%/45% возникает",
                "вспышка, ранящая соседних врагов на 30/60/90!"
            ],
            "stat_cur": lambda lvl: f"Шанс новы: {lvl * 15}% (урон {lvl * 30})" if lvl > 0 else "Без осколочной новы",
            "stat_nxt": lambda lvl: f"Шанс новы: {(lvl + 1) * 15}% (урон {(lvl + 1) * 30})",
            "icon_key": "supernova"
        },
        "void_amplifier": {
            "title": "Усилитель Бездны",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "dark",
            "x": 350, "y": 1820,
            "max_lvl": 3,
            "costs": [6, 14, 25],
            "requires": {'orbital_strike': 2},
            "desc": [
                "Резонатор космической энергии.",
                "+20% к урону Орбитального Удара и урону",
                "Дрона за каждый изученный уровень!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 20}% урона способностей Бездны" if lvl > 0 else "Базовая мощность космоса",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 20}% урона способностей Бездны",
            "icon_key": "dark_matter"
        },
        "void_infusion": {
            "title": "Эссенция Бездны",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "dark",
            "x": 220, "y": 1970,
            "max_lvl": 3,
            "costs": [8, 18, 32],
            "requires": {'cactus_drone': 1, 'void_amplifier': 1},
            "desc": [
                "Пропитывает всё вооружение оазиса.",
                "+10% к урону всех башен чистой космической",
                "энергией, игнорирующей броню врагов!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 10}% чистого урона всех башен" if lvl > 0 else "Обычные типы атак",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 10}% чистого урона всех башен",
            "icon_key": "void"
        },
        "dark_alchemy": {
            "title": "Тёмная Алхимия",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "dark",
            "x": 480, "y": 1970,
            "max_lvl": 3,
            "costs": [10, 22, 40],
            "requires": {'shatter_nova': 1, 'void_amplifier': 1},
            "desc": [
                "Синтез Тёмных Кактусов.",
                "+1 гарантированный Тёмный Кактус за победу",
                "над каждым Колоссом, Красным и Фиолетовым Боссом!"
            ],
            "stat_cur": lambda lvl: f"+{lvl} Тёмных Кактуса с каждого босса" if lvl > 0 else "Стандартная добыча боссов",
            "stat_nxt": lambda lvl: f"+{lvl + 1} Тёмных Кактуса с каждого босса",
            "icon_key": "dark_cactus"
        },
        "event_horizon": {
            "title": "Горизонт Событий",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "dark",
            "x": 280, "y": 2120,
            "max_lvl": 2,
            "costs": [15, 35],
            "requires": {'void_infusion': 1, 'void_amplifier': 2},
            "desc": [
                "Сверхмассивная гравитационная воронка.",
                "Орбитальный удар замедляет всех выживших врагов",
                "на 60% / 80% на 6.0 секунд!"
            ],
            "stat_cur": lambda lvl: f"Замедление после удара: {[0, 60, 80][lvl]}%" if lvl > 0 else "Без замедления от удара",
            "stat_nxt": lambda lvl: f"Замедление после удара: {[0, 60, 80][lvl + 1]}%",
            "icon_key": "void"
        },
        "quantum_harvester": {
            "title": "Квантовый Жнец",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "dark",
            "x": 420, "y": 2120,
            "max_lvl": 2,
            "costs": [15, 35],
            "requires": {'dark_alchemy': 1, 'void_amplifier': 2},
            "desc": [
                "Квантовый сбор ресурсов с боссов.",
                "+25% / +50% к награде кактусами за каждого босса,",
                "а также гарантированные семена!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 25}% к казне за поверженных боссов" if lvl > 0 else "Обычная награда с босса",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 25}% к казне за поверженных боссов",
            "icon_key": "coin"
        },
        "dark_transcendence": {
            "title": "Трансцендентность Бездны",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "dark",
            "scale": 1.8,
            "x": 350, "y": 2270,
            "max_lvl": 1,
            "costs": [50],
            "requires": {'event_horizon': 1, 'quantum_harvester': 1},
            "desc": [
                "Высшая ступень познания космоса.",
                "Все башни, дроны и казармы наносят +25% урона,",
                "а Орбитальный удар перезаряжается на 35% быстрее!"
            ],
            "stat_cur": lambda lvl: "Абсолютная мощь Бездны активна" if lvl > 0 else "Пик эволюции не достигнут",
            "stat_nxt": lambda lvl: "Обрести Трансцендентность Бездны",
            "icon_key": "transcendence"
        }
    }
    return nodes

def get_metro_route(p1, p2):
    """
    Вычисляет точки ломаной в стиле Метро (0, 90, 45 градусов) от p1 (psx, psy) до p2 (csx, csy).
    """
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 or dy == 0 or abs(dx) == abs(dy):
        return [(x1, y1), (x2, y2)]

    if abs(dx) > abs(dy):
        diag_x_span = abs(dy) * (1 if dx > 0 else -1)
        turn_x = x2 - diag_x_span
        turn_y = y1
        return [(x1, y1), (turn_x, turn_y), (x2, y2)]
    else:
        diag_y_span = abs(dx) * (1 if dy > 0 else -1)
        turn_x = x1
        turn_y = y2 - diag_y_span
        return [(x1, y1), (turn_x, turn_y), (x2, y2)]

def get_fillet_points(route, radius=8.0):
    """
    Скругляет углы ломаной route радиусом radius.
    """
    if len(route) <= 2:
        return route

    result = [route[0]]
    for i in range(1, len(route) - 1):
        prev_pt = route[i - 1]
        cur_pt = route[i]
        next_pt = route[i + 1]

        v1_x = prev_pt[0] - cur_pt[0]
        v1_y = prev_pt[1] - cur_pt[1]
        d1 = math.hypot(v1_x, v1_y)

        v2_x = next_pt[0] - cur_pt[0]
        v2_y = next_pt[1] - cur_pt[1]
        d2 = math.hypot(v2_x, v2_y)

        if d1 < 1e-4 or d2 < 1e-4:
            continue

        u1_x, u1_y = v1_x / d1, v1_y / d1
        u2_x, u2_y = v2_x / d2, v2_y / d2

        cut = min(radius, d1 * 0.45, d2 * 0.45)
        p_start = (cur_pt[0] + u1_x * cut, cur_pt[1] + u1_y * cut)
        p_end = (cur_pt[0] + u2_x * cut, cur_pt[1] + u2_y * cut)

        result.append(p_start)
        for t in (0.33, 0.66):
            omt = 1.0 - t
            bx = omt * omt * p_start[0] + 2 * omt * t * cur_pt[0] + t * t * p_end[0]
            by = omt * omt * p_start[1] + 2 * omt * t * cur_pt[1] + t * t * p_end[1]
            result.append((bx, by))
        result.append(p_end)

    result.append(route[-1])
    return result
