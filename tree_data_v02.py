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
        "oasis_core": {
            "title": "Оазис Кактусов",
            "branch": "core",
            "branch_title": "Истоки",
            "scale": 2.0,
            "x": 350,
            "y": -80,
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
            "icon_key": "cactus",
        },
        "start_tower_level": {
            "title": "Стартовый Уровень",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190,
            "y": 60,
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
            "icon_key": "start_lvl",
        },
        "attack_speed_overdrive": {
            "title": "Форсаж Атаки",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 40,
            "y": 60,
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
            "icon_key": "speed",
        },
        "max_tower_level": {
            "title": "Предельный Кап",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510,
            "y": 60,
            "max_lvl": 10,
            "costs": [2, 5, 9, 15, 23, 33, 46, 62, 81, 105],
            "requires": {'oasis_core': 1},
            "desc": [
            "Повышает максимальный лимит прокачки",
            "для всех видов башен в бою.",
            "Колоссальный DPS на поздних волнах!"
            ],
            "stat_cur": lambda lvl: f"+{lvl} к макс. уровню всех башен" if lvl > 0 else "Базовый предел уровней",
            "stat_nxt": lambda lvl: f"+{lvl + 1} к макс. уровню всех башен",
            "icon_key": "crown",
        },
        "bulk_upgrade": {
            "title": "Быстрая Прокачка",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 660,
            "y": 60,
            "max_lvl": 1,
            "costs": [10],
            "requires": {'max_tower_level': 1},
            "toggleable": False,
            "desc": [
            "Мгновенная прокачка башен до максимального уровня.",
            "Кнопка [МАКС] в карточке или зажатый [Shift]",
            "улучшает башню сразу на все доступные кактусы в 1 клик!"
            ],
            "stat_cur": lambda lvl: "Прокачка на максимум [Shift / МАКС]" if lvl > 0 else "Пошаговое улучшение по 1 уровню",
            "stat_nxt": lambda lvl: "Прокачка на максимум [Shift / МАКС]",
            "icon_key": "crown",
        },
        "magic_tower": {
            "title": "Магическая Башня",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.3,
            "x": 350,
            "y": 180,
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
            "icon_key": "magic_tower",
        },
        "sniper_optics": {
            "title": "Оптика Дальнобоя",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190,
            "y": 180,
            "max_lvl": 4,
            "costs": [3, 7, 14, 25],
            "requires": {'magic_tower': 1},
            "desc": [
            "Прицельные линзы высокой точности.",
            "+8px к дальности атаки всех стрелковых",
            "башен (Магия, Огонь, Заморозка) за ур.!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 8}px к радиусу башен" if lvl > 0 else "Базовый радиус атаки башен",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 8}px к радиусу башен",
            "icon_key": "magic_tower",
        },
        "magic_power": {
            "title": "Магический Резонанс",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 40,
            "y": 180,
            "max_lvl": 4,
            "costs": [8, 18, 35, 60],
            "requires": {'sniper_optics': 1},
            "desc": [
            "Усиливает магический урон за уровень.",
            "Увеличивает прирост урона Магической",
            "Башни: +0.1 / +0.2 / +0.3 / +0.4 за ур.!"
            ],
            "stat_cur": lambda lvl: f"+{round(lvl * 0.1, 1)} к урону за ур. башни ({round(0.75 + lvl * 0.1, 2)}/ур.)" if lvl > 0 else "Базовый прирост (+0.75 урона/ур.)",
            "stat_nxt": lambda lvl: f"+{round((lvl + 1) * 0.1, 1)} к урону за ур. башни ({round(0.85 + lvl * 0.1, 2)}/ур.)",
            "icon_key": "magic_tower",
        },
        "arcane_precision": {
            "title": "Тайная Точность",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510,
            "y": 180,
            "max_lvl": 5,
            "costs": [3, 6, 11, 18, 28],
            "requires": {'magic_tower': 1},
            "desc": [
            "Фокусировка магических импульсов.",
            "+2% к шансу критического удара",
            "для Магической башни за каждый ранг (до +10%)!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 2}% к шансу крита Магической башни" if lvl > 0 else "Базовый шанс крита",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 2}% к шансу крита Магической башни",
            "icon_key": "target",
        },
        "rock_tower": {
            "title": "Огненная Башня",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.3,
            "x": 350,
            "y": 360,
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
            "icon_key": "rock_tower",
        },
        "inferno_mastery": {
            "title": "Адский Жар",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510,
            "y": 360,
            "max_lvl": 5,
            "costs": [4, 8, 15, 25, 38],
            "requires": {'rock_tower': 'max'},
            "desc": [
            "Заряжает снаряды вулканической лавой.",
            "+10% урона огня, +6px сплэш-радиус",
            "и повышенный урон по заморозке (+10%/ур.)!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 10}% урона огня, +{lvl * 6}px сплэш, +{lvl * 10}% по льду" if lvl > 0 else "Базовый сплэш 50px (без бонусов)",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 10}% урона огня, +{(lvl + 1) * 6}px сплэш, +{(lvl + 1) * 10}% по льду",
            "icon_key": "rock_tower",
        },
        "freeze_tower": {
            "title": "Заморозка",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.3,
            "x": 350,
            "y": 540,
            "max_lvl": 1,
            "costs": [10],
            "requires": {'rock_tower': 'max'},
            "desc": [
            "Открывает Ледяную Башню [3].",
            "Замедляет толпы мобов на тропе.",
            "Огненная башня бьёт по льду +40%!"
            ],
            "stat_cur": lambda lvl: "Ледяная Башня разблокирована [3]" if lvl >= 1 else "Заблокирована (требуется покупка)",
            "stat_nxt": lambda lvl: "Открыть доступ к Ледяной Башне [3]",
            "icon_key": "freeze_tower",
        },
        "frost_nova": {
            "title": "Ледяная Нова",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190,
            "y": 540,
            "max_lvl": 3,
            "costs": [7, 16, 28],
            "requires": {'freeze_tower': 'max'},
            "desc": [
            "Глубокая абсолютная заморозка.",
            "Замедление сильнее на +4%, длительность +10%",
            "и периодический урон обморожения!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 4}% замедления, +{lvl * 10}% время действия" if lvl > 0 else "Базовый мороз (без бонусов)",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 4}% замедления, +{(lvl + 1) * 10}% время действия",
            "icon_key": "freeze_tower",
        },
        "frost_linger": {
            "title": "Остаточный Холод",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510,
            "y": 540,
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
            "icon_key": "frost",
        },
        "farm_tower": {
            "title": "Башня-Ферма",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.3,
            "x": 350,
            "y": 720,
            "max_lvl": 1,
            "costs": [14],
            "requires": {'freeze_tower': 'max'},
            "desc": [
            "Открывает Кактусовую Ферму [6].",
            "Пассивно приносит кактусы в конце волны.",
            "Ключевая аграрная башня и путь к Оранжерее!"
            ],
            "stat_cur": lambda lvl: "Кактусовая Ферма разблокирована [6]" if lvl >= 1 else "Заблокирована (требуется покупка)",
            "stat_nxt": lambda lvl: "Открыть доступ к Кактусовой Ферме [6]",
            "icon_key": "farm",
        },
        "fertile_soil": {
            "title": "Плодородная Почва",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190,
            "y": 720,
            "max_lvl": 3,
            "costs": [8, 18, 32],
            "requires": {'farm_tower': 'max'},
            "desc": [
            "Обогащает почву для Кактусовых Ферм.",
            "+10% к пассивному доходу всех Ферм",
            "в конце каждой завершенной волны!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 10}% к доходу Кактусовых Ферм" if lvl > 0 else "Базовый урожай Ферм",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 10}% к доходу Кактусовых Ферм (+10%)",
            "icon_key": "farm",
        },
        "compound_interest": {
            "title": "Кактусовый Вклад",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 40,
            "y": 720,
            "max_lvl": 4,
            "costs": [6, 15, 30, 50],
            "requires": {'fertile_soil': 2},
            "desc": [
            "Накопительный процент для оазиса.",
            "Начисляет +3% дивидендов от текущей",
            "казны в конце каждой волны (кап +30 🌵/ур.)!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 3}% дохода от казны (кап {lvl * 30} 🌵)" if lvl > 0 else "Без дивидендов от казны",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 3}% дохода от казны (кап {(lvl + 1) * 30} 🌵)",
            "icon_key": "farm",
        },
        "farm_irrigation": {
            "title": "Система Орошения",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510,
            "y": 720,
            "max_lvl": 3,
            "costs": [20, 42, 75],
            "requires": {'farm_tower': 'max'},
            "desc": [
            "Оснащает Кактусовые Фермы системой полива.",
            "Фермы создают Ауру Орошения, ускоряя башни,",
            "и периодически сбрасывают бонусные кактусы!"
            ],
            "stat_cur": lambda lvl: f"Орошение (R={90 + (lvl - 1) * 40}px + 3px/ур.): +{[0, 8, 14, 20][lvl]}% темпа, полив раз в {[0, 24, 18, 14][lvl]}с" if lvl > 0 else "Пассивный полив закрыт",
            "stat_nxt": lambda lvl: f"Орошение (R={90 + lvl * 40}px + 3px/ур.): +{[0, 8, 14, 20][lvl + 1]}% темпа, полив раз в {[0, 24, 18, 14][lvl + 1]}с",
            "icon_key": "farm",
        },
        "golden_fortune": {
            "title": "Золотая Фортуна",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 660,
            "y": 720,
            "max_lvl": 4,
            "costs": [6, 14, 26, 42],
            "requires": {'farm_irrigation': 1},
            "desc": [
            "Приманка для редких золотых слаймов.",
            "Золотые слаймы спавнятся на +25% чаще",
            "и гарантированно приносят Звёздный Кактус!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 25}% спавн золотых, гарантия Зв. кактуса" if lvl > 0 else "Обычный спавн золотых слаймов",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 25}% спавн золотых, гарантия Зв. кактуса",
            "icon_key": "start_cacti",
        },
        "tent_tower": {
            "title": "Палатка Солдат",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.3,
            "x": 350,
            "y": 900,
            "max_lvl": 1,
            "costs": [15],
            "requires": {'farm_tower': 'max'},
            "desc": [
            "Открывает Палатку Воинов [4].",
            "Призывает двух верных солдат-кактусов,",
            "блокирующих слаймов на тропе своими телами!"
            ],
            "stat_cur": lambda lvl: "Палатка Воинов разблокирована [4]" if lvl >= 1 else "Заблокирована (требуется покупка)",
            "stat_nxt": lambda lvl: "Открыть доступ к Палатке Воинов [4]",
            "icon_key": "tent_tower",
        },
        "knight_training": {
            "title": "Латы Воинов",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190,
            "y": 900,
            "max_lvl": 3,
            "costs": [6, 12, 24],
            "requires": {'tent_tower': 'max'},
            "desc": [
            "Защитная экипировка для гарнизона.",
            "+10% HP солдатам казармы и -6% урона",
            "от столкновений со слаймами за ранг!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 10}% HP воинам, защита от ударов -{lvl * 6}%" if lvl > 0 else "Базовая броня солдат",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 10}% HP воинам, защита от ударов -{(lvl + 1) * 6}%",
            "icon_key": "soldier",
        },
        "shield_wall": {
            "title": "Стена Щитов",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 40,
            "y": 900,
            "max_lvl": 3,
            "costs": [8, 18, 32],
            "requires": {'knight_training': 2},
            "desc": [
            "Тактический защитный строй казармы.",
            "+1 дополнительный боец гарнизона",
            "(до 5 воинов) за каждый изученный ранг!"
            ],
            "stat_cur": lambda lvl: f"+{lvl} доп. боец казармы ({2 + lvl} бойца)" if lvl > 0 else "Базовый гарнизон из 2 бойцов",
            "stat_nxt": lambda lvl: f"+{lvl + 1} доп. боец казармы ({3 + lvl} бойца)",
            "icon_key": "soldier",
        },
        "tent_thorns": {
            "title": "Шипы Кактуса",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510,
            "y": 900,
            "max_lvl": 5,
            "costs": [4, 8, 14, 22, 35],
            "requires": {'tent_tower': 'max'},
            "desc": [
            "Острые кактусовые шипы на доспехах гарнизона.",
            "При атаке на воинов возвращают атакующему слайму",
            "+30% урона за каждый изученный уровень шипов!"
            ],
            "stat_cur": lambda lvl: f"Шипы: возврат +{lvl * 30}% урона атакующему" if lvl > 0 else "Воины без шипов (0% возврата)",
            "stat_nxt": lambda lvl: f"Шипы: возврат +{(lvl + 1) * 30}% урона атакующему",
            "icon_key": "soldier",
        },
        "rally_range": {
            "title": "Призывной Горн",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 660,
            "y": 900,
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
            "icon_key": "optics",
        },
        "tesla_tower": {
            "title": "Башня Тесла",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.3,
            "x": 350,
            "y": 1080,
            "max_lvl": 1,
            "costs": [25],
            "requires": {'tent_tower': 'max'},
            "desc": [
            "Открывает Башню Тесла [5].",
            "Выпускает сокрушительные цепные молнии,",
            "рикошетящие по нескольким слаймам подряд!"
            ],
            "stat_cur": lambda lvl: "Башня Тесла разблокирована [5]" if lvl >= 1 else "Заблокирована (требуется покупка)",
            "stat_nxt": lambda lvl: "Открыть доступ к Башне Тесла [5]",
            "icon_key": "tesla_tower",
        },
        "ball_lightning": {
            "title": "Шаровая Молния",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190,
            "y": 1080,
            "max_lvl": 3,
            "costs": [8, 18, 30],
            "requires": {'tesla_tower': 'max'},
            "desc": [
            "Плазменная дуга высокого напряжения.",
            "+12% урона молнии и +18px дальность",
            "поражения цепного разряда за уровень!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 12}% урона молнии, +{lvl * 18}px к дальности прыжка" if lvl > 0 else "Базовый разряд молнии (без дуги)",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 12}% урона молнии, +{(lvl + 1) * 18}px к дальности прыжка",
            "icon_key": "tesla_tower",
        },
        "overcharge": {
            "title": "Перегрузка Цепи",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510,
            "y": 1080,
            "max_lvl": 3,
            "costs": [10, 20, 35],
            "requires": {'tesla_tower': 'max'},
            "desc": [
            "Накачивает цепи Теслы перегрузкой.",
            "+1 дополнительная пораженная цель",
            "в каждой вспышке цепной молнии!"
            ],
            "stat_cur": lambda lvl: f"+{lvl} доп. цель цепи ({3 + lvl} целей молнии)" if lvl > 0 else "Базовые 3 цели цепной молнии",
            "stat_nxt": lambda lvl: f"+{lvl + 1} доп. цель цепи ({4 + lvl} целей молнии)",
            "icon_key": "sword",
        },
        "superconductor": {
            "title": "Сверхпроводник",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 660,
            "y": 1080,
            "max_lvl": 3,
            "costs": [14, 28, 55],
            "requires": {'overcharge': 2, 'ball_lightning': 2},
            "desc": [
            "Сверхпроводящие катушки Теслы.",
            "Цепная молния сохраняет больше урона при",
            "каждом рикошете (до 90% урона на 3 ур.)!"
            ],
            "stat_cur": lambda lvl: ["Базовое сохранение: 65% за рикошет", "Сохранение урона цепи: 75% за рикошет", "Сохранение урона цепи: 82% за рикошет", "Сохранение урона цепи: 90% [МАКС]"][min(3, lvl)],
            "stat_nxt": lambda lvl: ["Сохранение урона: 75%", "Сохранение урона: 82%", "Сохранение урона: 90% [МАКС]"][min(2, lvl)],
            "icon_key": "tesla_tower",
        },
        "sun_tower": {
            "title": "Обелиск Солнца",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "scale": 1.4,
            "x": 350,
            "y": 1260,
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
            "icon_key": "sun_tower",
        },
        "solar_power": {
            "title": "Солнечная Мощь",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 190,
            "y": 1260,
            "max_lvl": 5,
            "costs": [4, 8, 15, 25, 40],
            "requires": {'sun_tower': 1},
            "desc": [
            "Усиливает кристалл солярной фокусировки.",
            "Увеличивает урон Обелиска Солнца на +20%",
            "за каждый изученный ранг (вплоть до +100%)!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 20}% к урону Обелиска Солнца" if lvl > 0 else "Базовый урон луча",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 20}% к урону Обелиска Солнца",
            "icon_key": "damage",
        },
        "solar_trail": {
            "title": "Солнечный След",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 40,
            "y": 1260,
            "max_lvl": 4,
            "costs": [5, 12, 22, 35],
            "requires": {'solar_power': 2},
            "desc": [
            "Термальная детонация погибшей цели.",
            "При гибели от луча моб взрывается в радиусе",
            "50 px на 2.5% .. 10% от своего макс. HP!"
            ],
            "stat_cur": lambda lvl: f"Взрыв при гибели: {lvl * 2.5:.1f}% max HP цели" if lvl > 0 else "Без солярного взрыва",
            "stat_nxt": lambda lvl: f"Взрыв при гибели: {(lvl + 1) * 2.5:.1f}% max HP цели",
            "icon_key": "inferno",
        },
        "prism_beams": {
            "title": "Солнечная Призма",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 510,
            "y": 1260,
            "max_lvl": 3,
            "costs": [8, 16, 28],
            "requires": {'sun_tower': 1},
            "desc": [
            "Оптическое расщепление светового потока.",
            "Обелиск получает +1 независимый луч за ранг,",
            "атакуя до 4 разных целей одновременно!"
            ],
            "stat_cur": lambda lvl: f"Число лучей обелиска: {1 + lvl}" if lvl > 0 else "1 сфокусированный луч",
            "stat_nxt": lambda lvl: f"Число лучей обелиска: {2 + lvl}",
            "icon_key": "optics",
        },
        "beam_limit": {
            "title": "Предел Луча",
            "branch": "tech",
            "branch_title": "Башни Оазиса",
            "x": 660,
            "y": 1260,
            "max_lvl": 5,
            "costs": [5, 10, 18, 30, 45],
            "requires": {'prism_beams': 1},
            "desc": [
            "Калибровка сверхкритической мощности.",
            "Увеличивает потолок множителя урона луча",
            "на +0.5x за ранг (с базовых x2.5 до x5.0)!"
            ],
            "stat_cur": lambda lvl: f"Потолок разогрева луча: x{2.5 + lvl * 0.5:.1f}" if lvl > 0 else "Базовый предел x2.5",
            "stat_nxt": lambda lvl: f"Потолок разогрева луча: x{2.5 + (lvl + 1) * 0.5:.1f}",
            "icon_key": "overcharge",
        },
        "speed_limit": {
            "title": "Ускорение Времени",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -500,
            "y": 140,
            "max_lvl": 8,
            "costs": [2, 4, 8, 14, 22, 32, 45, 60],
            "requires": {'oasis_core': 1},
            "desc": [
            "Увеличивает максимальную скорость игры (+1x за ур.).",
            "0.2x: тактический режим для точного контроля!",
            "На 3 ур. (5x) открывает Турбо-Волны и Плотный Спавн!"
            ],
            "stat_cur": lambda lvl: [
            "Скорости: 0.2x, 1x, 2x",
            "Скорости: 0.2x, 1x, 2x, 3x",
            "Скорости: 0.2x, 1x, 2x, 3x, 4x",
            "Скорости: до 5x [Турбо-открытие]",
            "Скорости: до 6x",
            "Скорости: до 7x",
            "Скорости: до 8x",
            "Скорости: до 9x",
            "Скорости: до 10x [МАКСИМУМ]"
            ][min(8, lvl)],
            "stat_nxt": lambda lvl: f"Добавит {lvl + 3}x скорость" if lvl < 8 else "Максимальный уровень",
            "icon_key": "speed",
        },
        "spawn_rush": {
            "title": "Плотный Спавн",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -640,
            "y": 140,
            "max_lvl": 3,
            "costs": [5, 12, 24],
            "requires": {'speed_limit': 3},
            "toggleable": True,
            "desc": [
            "Ускоряет появление слаймов из портала в бой.",
            "Мобы выходят плотными группами (-25% / -45% / -65% задержки).",
            "Делает волну быстрее, но опаснее! Переключение [ВКЛ/ВЫКЛ] или [Y]."
            ],
            "stat_cur": lambda lvl: [
            "Обычный темп выхода мобов (1.2с)",
            "Пауза выхода -25% (быстрый поток)",
            "Пауза выхода -45% (штурмовой напор)",
            "Пауза выхода -65% (мгновенная лавина)"
            ][min(3, lvl)],
            "stat_nxt": lambda lvl: [
            "Ускорение выхода мобов на 25%",
            "Ускорение выхода мобов на 45%",
            "Ускорение выхода мобов на 65%",
            "Максимальный уровень"
            ][min(3, lvl)],
            "icon_key": "speed",
        },
        "wave_rush": {
            "title": "Турбо-Волны",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -360,
            "y": 140,
            "max_lvl": 3,
            "costs": [6, 14, 25],
            "requires": {'speed_limit': 3},
            "toggleable": True,
            "desc": [
            "Управление темпом наступления врагов.",
            "Снижает паузу между волнами до 0.5с / 0.2с / 0.0с (мгновенно).",
            "Можно отключить в Древе [ВКЛ/ВЫКЛ] или кнопкой [T] в бою!"
            ],
            "stat_cur": lambda lvl: ("Пауза 0.5 сек." if lvl == 1 else ("Пауза 0.2 сек." if lvl == 2 else "Мгновенный старт (0.0 сек.)")) if lvl > 0 else "Обычная пауза (1.0 сек.)",
            "stat_nxt": lambda lvl: "Пауза 0.5 сек." if lvl == 0 else ("Пауза 0.2 сек." if lvl == 1 else "Мгновенный старт (0.0 сек.)"),
            "icon_key": "speed",
        },
        "base_health": {
            "title": "Крепость Базы",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -500,
            "y": 280,
            "max_lvl": 5,
            "costs": [3, 6, 11, 18, 28],
            "requires": {'oasis_core': 1},
            "desc": [
            "Укрепляет кактусовый оазис и стены базы.",
            "+3 к максимальным жизням базы за уровень.",
            "Помогает сдержать прорывы быстрых мобов!"
            ],
            "stat_cur": lambda lvl: f"Здоровье базы: {10 + lvl * 3} HP (+{lvl * 3} HP)" if lvl > 0 else "Базовое здоровье: 10 HP",
            "stat_nxt": lambda lvl: f"Здоровье базы: {10 + (lvl + 1) * 3} HP (+{(lvl + 1) * 3} HP)",
            "icon_key": "health",
        },
        "global_damage": {
            "title": "Острые Шипы",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -640,
            "y": 430,
            "max_lvl": 5,
            "costs": [4, 8, 16, 28, 44],
            "requires": {'base_health': 1},
            "desc": [
            "Заостряет колючки всех кактусов.",
            "+4% базового урона для всех видов башен,",
            "палаток воинов и цепных молний!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 4}% ко всему общему урону оазиса" if lvl > 0 else "Базовый урон (без бонуса шипов)",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 4}% ко всему общему урону оазиса (+4%)",
            "icon_key": "damage",
        },
        "critical_mastery": {
            "title": "Критический Удар",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -500,
            "y": 430,
            "max_lvl": 10,
            "costs": [3, 6, 11, 18, 27, 38, 51, 66, 83, 102],
            "requires": {'base_health': 2},
            "desc": [
            "Изучение уязвимых точек слаймов.",
            "+2.5% шанс нанести сокрушительный КРИТ (x2.0 урона)",
            "для абсолютно всех типов башен!"
            ],
            "stat_cur": lambda lvl: f"Шанс крита: {lvl * 2.5:g}% (урон x2.0)" if lvl > 0 else "Без критов",
            "stat_nxt": lambda lvl: f"Шанс крита: {(lvl + 1) * 2.5:g}% (урон x2.0)",
            "icon_key": "sword",
        },
        "thorn_armor": {
            "title": "Шипованный Оазис",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -360,
            "y": 430,
            "max_lvl": 3,
            "costs": [7, 16, 32],
            "requires": {'base_health': 2},
            "desc": [
            "Шипы базы защищают от рядовых мобов (боссы не отражаются!).",
            "Шанс 8% / 15% / 22% отразить моба БЕЗ потери жизни.",
            "При потере жизни: ответный залп шипов (150 / 220 / 290 урон ВСЕМ мобам на карте)!"
            ],
            "stat_cur": lambda lvl: f"Шанс отражения {8 + (lvl - 1) * 7}%, залп шипов {80 + lvl * 70} всем на карте" if lvl > 0 else "База не защищена шипами",
            "stat_nxt": lambda lvl: f"Шанс отражения {8 + lvl * 7}%, залп шипов {80 + (lvl + 1) * 70} всем на карте",
            "icon_key": "damage",
        },
        "regeneration": {
            "title": "Регенерация Оазиса",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -640,
            "y": 570,
            "max_lvl": 3,
            "costs": [6, 15, 30],
            "requires": {'global_damage': 2, 'base_health': 3},
            "desc": [
            "Живительные кактусовые соки.",
            "Восстанавливает +1 HP базы за ур. каждые",
            "5 завершенных волн (вплоть до максимума)!"
            ],
            "stat_cur": lambda lvl: f"+{lvl} HP базы каждые 5 волн" if lvl > 0 else "Без регенерации жизней",
            "stat_nxt": lambda lvl: f"+{lvl + 1} HP базы каждые 5 волн",
            "icon_key": "health",
        },
        "giant_hunter": {
            "title": "Охотник на Боссов",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -500,
            "y": 570,
            "max_lvl": 3,
            "costs": [10, 22, 42],
            "requires": {'critical_mastery': 2},
            "desc": [
            "Специализация на уничтожении гигантов.",
            "+10% урона по Боссам (25, 50, 75 волны)",
            "и элитным слаймам за каждый ранг таланта!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 10}% урона по Боссам и Элите" if lvl > 0 else "Базовый урон по боссам",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 10}% урона по Боссам и Элите",
            "icon_key": "crown",
        },
        "range_grid": {
            "title": "Тактическая Сетка",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -360,
            "y": 570,
            "max_lvl": 1,
            "costs": [3],
            "requires": {'thorn_armor': 1},
            "toggleable": True,
            "desc": [
            "Подсвечивает радиусы всех башен одновременно.",
            "Позволяет легко видеть зоны перекрытия и слепые пятна.",
            "Включается клавишей [X], кнопкой в HUD или в Древе!"
            ],
            "stat_cur": lambda lvl: "Отображение радиусов всех башен [X]" if lvl > 0 else "Обычный скрытый режим радиусов",
            "stat_nxt": lambda lvl: "Отображение радиусов всех башен [X]",
            "icon_key": "crown",
        },
        "smart_targeting": {
            "title": "Умный Прицел",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -500,
            "y": 710,
            "max_lvl": 2,
            "costs": [5, 12],
            "requires": {'critical_mastery': 1},
            "toggleable": False,
            "desc": [
            "Тактический протокол наведения всех башен.",
            "1 ур.: открывает режим 'Слабый' (цели с мин. HP) и быструю смену цели [TAB].",
            "2 ур.: +10% урона всем башням по целям 'Сильный' (Боссы и Элита)!"
            ],
            "stat_cur": lambda lvl: ("Смена цели [TAB] + наведение 'Слабый' + 10% урона по СИЛЬНЫМ" if lvl >= 2 else "Смена цели всех башен [TAB] + наведение 'Слабый'") if lvl > 0 else "Ручной выбор каждой башни отдельно",
            "stat_nxt": lambda lvl: "Смена цели всех башен [TAB] + наведение 'Слабый'" if lvl == 0 else "+10% урона всем башням по целям 'СИЛЬНЫЙ'",
            "icon_key": "sword",
        },
        "elemental_focus": {
            "title": "Элементный Фокус",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -360,
            "y": 710,
            "max_lvl": 1,
            "costs": [12],
            "requires": {'range_grid': 1},
            "toggleable": True,
            "desc": [
            "Тактическая синергия стихий льда и огня.",
            "Морозная башня бьёт по ещё не замедленным целям,",
            "а Огненная - по замороженным для 100% критических ударов."
            ],
            "stat_cur": lambda lvl: "Умный фокус стихий (Заморозка + Крит-комбо)" if lvl > 0 else "Обычный выбор целей без учёта стихий",
            "stat_nxt": lambda lvl: "Умный фокус стихий (Заморозка + Крит-комбо)",
            "icon_key": "magic_tower",
        },
        "bestiary_damage": {
            "title": "Анатомия Слаймов",
            "branch": "combat",
            "branch_title": "Оборона и Тактика",
            "x": -640,
            "y": 710,
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
            "icon_key": "sword",
        },
        "start_cacti": {
            "title": "Стартовая Казна",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1080,
            "y": 200,
            "max_lvl": 10,
            "costs": [1, 2, 4, 7, 11, 16, 22, 29, 37, 46],
            "requires": {'oasis_core': 1},
            "desc": [
            "Начальный капитал кактусов при старте боя.",
            "+75 кактусов в начале каждой игры за ур.",
            "Позволяет ставить дорогие башни с первых секунд!"
            ],
            "stat_cur": lambda lvl: f"Старт: {180 + lvl * 75} кактусов (+{lvl * 75})" if lvl > 0 else "Базовый старт: 180 кактусов",
            "stat_nxt": lambda lvl: f"Старт: {180 + (lvl + 1) * 75} кактусов (+{(lvl + 1) * 75})",
            "icon_key": "start_cacti",
        },
        "wave_clearing_bounty": {
            "title": "Премия за Волну",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 960,
            "y": 350,
            "max_lvl": 5,
            "costs": [3, 7, 13, 21, 32],
            "requires": {'start_cacti': 1},
            "desc": [
            "Награда за успешное отражение волны.",
            "+25 кактусов в казну после зачистки",
            "каждой завершенной волны за уровень таланта!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 25} кактусов за каждую волну" if lvl > 0 else "Без премии за волну",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 25} кактусов за каждую волну",
            "icon_key": "bounty",
        },
        "start_wave_step": {
            "title": "Выбор Волны",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1080,
            "y": 350,
            "max_lvl": 20,
            "costs": [2 + i * 2 for i in range(20)],
            "requires": {'start_cacti': 1},
            "desc": [
            "Старт боя сразу с шагом +5 волн за ур.",
            "(до текущего рекорда карты).",
            "Выдает стартовые ресурсы за пропуск!"
            ],
            "stat_cur": lambda lvl: f"Быстрый старт: выбор до {lvl * 5} волны" if lvl > 0 else "Старт только с 1-й волны",
            "stat_nxt": lambda lvl: f"Быстрый старт: выбор до {(lvl + 1) * 5} волны",
            "icon_key": "wave",
        },
        "cacti_bounty": {
            "title": "Сбор Урожая",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1200,
            "y": 350,
            "max_lvl": 5,
            "costs": [3, 6, 10, 16, 25],
            "requires": {'start_cacti': 2},
            "desc": [
            "Больше кактусов за поверженных слаймов.",
            "+10% к награде за каждого уничтоженного",
            "врага на поле боя!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 10}% кактусов за поверженных врагов" if lvl > 0 else "Базовая награда за слаймов",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 10}% кактусов за поверженных врагов (+10%)",
            "icon_key": "bounty",
        },
        "stellar_magnet": {
            "title": "Звёздный Магнит",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1080,
            "y": 500,
            "max_lvl": 5,
            "costs": [4, 8, 14, 22, 32],
            "requires": {'cacti_bounty': 3},
            "desc": [
            "Притягивает космическую пыль и звёзды.",
            "+10% к шансу дропа Звёздных Кактусов",
            "с мобов за каждый уровень таланта!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 10}% к шансу выпадения Звёзд" if lvl > 0 else "Базовый шанс выпадения Звёзд",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 10}% к шансу выпадения Звёзд (+10%)",
            "icon_key": "magnet",
        },
        "star_alchemy": {
            "title": "Звёздная Алхимия",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1080,
            "y": 650,
            "max_lvl": 3,
            "costs": [8, 20, 40],
            "requires": {'stellar_magnet': 2},
            "desc": [
            "Космический синтез древних кактусов.",
            "Синтезирует +1 Звёздный Кактус каждые",
            "5 / 4 / 3 завершенных волн прямо в копилку!"
            ],
            "stat_cur": lambda lvl: f"+1 Зв. Кактус каждые {6 - lvl} волн" if lvl > 0 else "Без алхимии Звёзд",
            "stat_nxt": lambda lvl: f"+1 Зв. Кактус каждые {6 - (lvl + 1)} волн",
            "icon_key": "magnet",
        },
        "bestiary_cacti": {
            "title": "Охотничья Премия",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1200,
            "y": 500,
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
            "icon_key": "cactus",
        },
        "bestiary_stars": {
            "title": "Звёздный Трофей",
            "branch": "econ",
            "branch_title": "Экономика Оазиса",
            "x": 1200,
            "y": 650,
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
            "icon_key": "stellar",
        },
        "greenhouse_unlock": {
            "title": "Оранжерея Оазиса",
            "branch": "flora",
            "branch_title": "Оранжерея и Флора",
            "scale": 1.5,
            "x": 1080,
            "y": 950,
            "max_lvl": 1,
            "costs": [20],
            "requires": {'farm_irrigation': 1},
            "desc": [
            "Открывает Оранжерею [G] и коллекцию",
            "редких кактусов с постоянными бонусами."
            ],
            "stat_cur": lambda lvl: "Оранжерея построена [G]" if lvl >= 1 else "Заблокирована (требуется постройка)",
            "stat_nxt": lambda lvl: "Построить Оранжерею и открыть меню Флоры [G]",
            "icon_key": "greenhouse",
        },
        "botanical_expeditions": {
            "title": "Экспедиции",
            "branch": "flora",
            "branch_title": "Оранжерея и Флора",
            "x": 950,
            "y": 1100,
            "max_lvl": 3,
            "costs": [8, 18, 32],
            "requires": {'greenhouse_unlock': 'max'},
            "desc": [
            "Поиск редких ростков в дикой пустыне.",
            "+15% к шансу найти саженец редкого вида",
            "при раскалывании астральных метеоритов!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 15}% к шансу найти саженцы" if lvl > 0 else "Базовый шанс дропа саженцев",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 15}% к шансу найти саженцы (+15%)",
            "icon_key": "sprout",
        },
        "fertile_compost": {
            "title": "Живой Компост",
            "branch": "flora",
            "branch_title": "Оранжерея и Флора",
            "x": 1080,
            "y": 1100,
            "max_lvl": 5,
            "costs": [8, 16, 26, 38, 52],
            "requires": {'greenhouse_unlock': 'max'},
            "desc": [
            "Питательный гумус на основе кактусовой золы.",
            "+0.2% урона за уровень таланта ВСЕМ башням на",
            "поле боя за каждый уровень кактусов в Оранжерее!"
            ],
            "stat_cur": lambda lvl: f"+{round(lvl * 0.2, 1)}% урона за ур. кактуса (всего: +{round(lvl * 0.2 * count_total_greenhouse_cacti_levels(), 1)}%)" if lvl > 0 else "Без бонуса компоста",
            "stat_nxt": lambda lvl: f"+{round((lvl + 1) * 0.2, 1)}% урона за ур. кактуса (будет: +{round((lvl + 1) * 0.2 * count_total_greenhouse_cacti_levels(), 1)}%)",
            "icon_key": "farm",
        },
        "sprout_harvest": {
            "title": "Обильный Урожай",
            "branch": "flora",
            "branch_title": "Оранжерея и Флора",
            "x": 1210,
            "y": 1100,
            "max_lvl": 3,
            "costs": [12, 25, 45],
            "requires": {'greenhouse_unlock': 'max'},
            "desc": [
            "Мастерство черенкования и прививки флоры.",
            "+50% к шансу получить доп. саженец",
            "с поверженного босса волны за каждый уровень!",
            ],
            "stat_cur": lambda lvl: ("+50% шанс на +1 саженец с босса" if lvl == 1 else ("+1 гарантированный доп. саженец с босса" if lvl == 2 else "+1 гарант. и +50% шанс на 2-й саженец")) if lvl > 0 else "Стандартная награда с боссов",
            "stat_nxt": lambda lvl: ("+50% шанс на +1 саженец с босса" if lvl == 0 else ("+1 гарантированный доп. саженец с босса" if lvl == 1 else "+1 гарант. и +50% шанс на 2-й саженец")),
            "icon_key": "bounty",
        },
        "flora_resonance": {
            "title": "Резонанс Флоры",
            "branch": "flora",
            "branch_title": "Оранжерея и Флора",
            "x": 1080,
            "y": 1250,
            "max_lvl": 4,
            "costs": [12, 24, 40, 60],
            "requires": {'greenhouse_unlock': 'max'},
            "desc": [
            "Симбиоз Оазиса и редкой растительности.",
            "Усиливает ВСЕ пассивные эффекты кактусов",
            "в Оранжерее на +10% за каждый ранг!"
            ],
            "stat_cur": lambda lvl: f"+{10 * lvl}% к силе всех эффектов Оранжереи" if lvl > 0 else "Базовая сила эффектов Оранжереи",
            "stat_nxt": lambda lvl: f"+{10 * (lvl + 1)}% к силе всех эффектов Оранжереи",
            "icon_key": "crown",
        },
        "botanic_harvest": {
            "title": "Ботанический Сбор",
            "branch": "flora",
            "branch_title": "Оранжерея и Флора",
            "x": 1210,
            "y": 1250,
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
            "icon_key": "sprout",
        },
        "archaeology_unlock": {
            "title": "Археология Оазиса",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "scale": 1.5,
            "x": 1750,
            "y": 350,
            "max_lvl": 1,
            "costs": [8],
            "requires": {'start_cacti': 1},
            "desc": [
            "Открывает появление зон раскопок на картах (шанс 2%)",
            "и доступ к Музею Реликвий [R]."
            ],
            "stat_cur": lambda lvl: "Археология открыта, Музей доступен по [R]" if lvl > 0 else "Раскопки закрыты",
            "stat_nxt": lambda lvl: "Открыть Археологию и Музей Реликвий [R]",
            "icon_key": "shovel",
        },
        "dig_site_duration": {
            "title": "Стойкий Раскоп",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "x": 1620,
            "y": 500,
            "max_lvl": 3,
            "costs": [5, 12, 22],
            "requires": {'archaeology_unlock': 'max'},
            "desc": [
            "Укрепляет песчаные насыпи от осыпания ветром.",
            "+10 секунд к времени жизни кургана",
            "на поле боя за уровень таланта (до 60 секунд)!"
            ],
            "stat_cur": lambda lvl: f"Время жизни зоны: {30 + lvl * 10} секунд" if lvl > 0 else "Базовое время: 30 секунд",
            "stat_nxt": lambda lvl: f"Время жизни зоны: {30 + (lvl + 1) * 10} секунд",
            "icon_key": "speed",
        },
        "dig_minigame_buff": {
            "title": "Опыт Раскопок",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "x": 1750,
            "y": 500,
            "max_lvl": 5,
            "costs": [4, 8, 15, 25, 40],
            "requires": {'archaeology_unlock': 'max'},
            "desc": [
            "Искусная техника аккуратного снятия слоев песка.",
            "+2 дополнительных хода/вскопки в мини-игре",
            "Морского Боя 5х5 за каждый уровень таланта!"
            ],
            "stat_cur": lambda lvl: f"Вскопок в мини-игре: {12 + lvl * 2} (база 12 + {lvl * 2})" if lvl > 0 else "Базовые 12 вскопок",
            "stat_nxt": lambda lvl: f"Вскопок в мини-игре: {12 + (lvl + 1) * 2}",
            "icon_key": "bounty",
        },
        "dig_site_chance": {
            "title": "Гео-Разведка",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "x": 1880,
            "y": 500,
            "max_lvl": 3,
            "costs": [6, 14, 25],
            "requires": {'archaeology_unlock': 'max'},
            "desc": [
            "Песчаные радары древних культур.",
            "+1% к шансу появления зоны раскопок",
            "в начале каждой волны за уровень таланта (до 5%)!"
            ],
            "stat_cur": lambda lvl: f"Шанс раскопок: {2 + lvl}% за волну" if lvl > 0 else "Базовый шанс: 2%",
            "stat_nxt": lambda lvl: f"Шанс раскопок: {2 + lvl + 1}% за волну",
            "icon_key": "shovel",
        },
        "relic_pedestals": {
            "title": "Пьедесталы Мощи",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "x": 1620,
            "y": 650,
            "max_lvl": 3,
            "costs": [15, 35, 65],
            "requires": {'archaeology_unlock': 'max'},
            "desc": [
            "Увеличивает число активных пьедесталов в Музее",
            "с базовых 2 до 5 слотов (по +1 за уровень)!",
            "Позволяет активировать больше древних реликвий одновременно."
            ],
            "stat_cur": lambda lvl: f"Пьедесталов в Музее: {2 + lvl}/5" if lvl > 0 else "Базовые 2 пьедестала",
            "stat_nxt": lambda lvl: f"Пьедесталов в Музее: {2 + lvl + 1}/5",
            "icon_key": "relic",
        },
        "relic_max_level": {
            "title": "Древние Знания",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "x": 1750,
            "y": 650,
            "max_lvl": 4,
            "costs": [12, 25, 45, 75],
            "requires": {'archaeology_unlock': 'max'},
            "desc": [
            "Расшифровка старинных папирусов и рун оазиса.",
            "Повышает макс. предел прокачки реликвий",
            "с 1 до 5 уровня (каждый ур. удваивает силу бонуса)!"
            ],
            "stat_cur": lambda lvl: f"Предел уровня реликвий: {1 + lvl} ур." if lvl > 0 else "Базовый предел: 1 ур. реликвий",
            "stat_nxt": lambda lvl: f"Предел уровня реликвий: {2 + lvl} ур.",
            "icon_key": "relic",
        },
        "relic_double_drop": {
            "title": "Астральный Землекоп",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "currency": "hybrid",
            "x": 1880,
            "y": 650,
            "max_lvl": 1,
            "costs": [50],
            "dark_costs": [4],
            "requires": {'relic_max_level': 2},
            "desc": [
            "Космический резонанс удваивает находки Бездны.",
            "Каждая успешная раскопка на поле боя",
            "приносит сразу +2 копии найденной реликвии!"
            ],
            "stat_cur": lambda lvl: "Двойная добыча реликвий (+1 доп. копия) активна!" if lvl > 0 else "Обычная добыча по 1 реликвии",
            "stat_nxt": lambda lvl: "Открыть удвоение добываемых реликвий",
            "icon_key": "crown",
        },
        "dark_relic_resonance": {
            "title": "Тёмный Резонанс",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "currency": "hybrid",
            "x": 1750,
            "y": 800,
            "max_lvl": 4,
            "costs": [65, 110, 165, 230],
            "dark_costs": [5, 9, 15, 24],
            "requires": {'relic_pedestals': 2, 'relic_max_level': 2},
            "desc": [
            "Тёмная энергия Бездны связывает все залы Музея.",
            "Неэкипированные реликвии действуют пассивно",
            "на +5% силы за уровень прокачки (до 20% на 4 ур.)!"
            ],
            "stat_cur": lambda lvl: f"Пассивная сила реликвий вне пьедесталов: +{lvl * 5}%" if lvl > 0 else "Неэкипированные реликвии не активны",
            "stat_nxt": lambda lvl: f"Пассивная сила реликвий вне пьедесталов: +{(lvl + 1) * 5}%",
            "icon_key": "relic",
        },
        "sonar_ping": {
            "title": "Око Бездны",
            "branch": "relics",
            "branch_title": "Музей Реликвий",
            "currency": "dark",
            "x": 1880,
            "y": 800,
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
            "icon_key": "shovel",
        },
        "astral_beacon": {
            "title": "Тёмный Космос",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "stellar",
            "scale": 1.5,
            "x": 350,
            "y": 1520,
            "max_lvl": 1,
            "costs": [25],
            "dark_costs": [0],
            "requires": {'sun_tower': 1},
            "desc": [
            "Открывает появление Тёмных кактусов,",
            "падение Астральных Метеоритов",
            "и ветку космических улучшений."
            ],
            "stat_cur": lambda lvl: "Тёмный Космос открыт, Тёмные кактусы активны" if lvl > 0 else "Тёмный Космос закрыт",
            "stat_nxt": lambda lvl: "Открыть ветку Тёмного Космоса",
            "icon_key": "dark_cactus",
        },
        "dark_aegis": {
            "title": "Тёмный Эгис",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "hybrid",
            "x": 220,
            "y": 1670,
            "max_lvl": 2,
            "costs": [25, 45],
            "dark_costs": [1, 2],
            "requires": {'astral_beacon': 'max'},
            "desc": [
            "Защитный барьер базы.",
            "Раз за волну поглощает 1 (на ур. 2: 2)",
            "прорыв слаймов к базе без потери сердец."
            ],
            "stat_cur": lambda lvl: f"Щит Бездны: поглощает {lvl} утечки за волну" if lvl > 0 else "Без щита Бездны",
            "stat_nxt": lambda lvl: f"Щит Бездны: поглощает {lvl + 1} утечки за волну",
            "icon_key": "health",
        },
        "gravity_well": {
            "title": "Грави-Захват",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "hybrid",
            "x": 480,
            "y": 1670,
            "max_lvl": 3,
            "costs": [20, 38, 65],
            "dark_costs": [1, 2, 3],
            "requires": {'astral_beacon': 'max'},
            "desc": [
            "Искажает космическую гравитацию.",
            "Метеориты появляются на +20% чаще за ранг,",
            "замедляются при падении и дают +1 доп. кактус!"
            ],
            "stat_cur": lambda lvl: f"Метеориты чаще на +{lvl * 20}%, +{lvl} зв. кактус" if lvl > 0 else "Стандартный космос",
            "stat_nxt": lambda lvl: f"Метеориты чаще на +{(lvl + 1) * 20}%, +{lvl + 1} зв. кактус",
            "icon_key": "meteor",
        },
        "orbital_strike": {
            "title": "Орбитальный Удар",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "hybrid",
            "scale": 1.2,
            "x": 350,
            "y": 1670,
            "max_lvl": 3,
            "costs": [30, 55, 90],
            "dark_costs": [2, 3, 5],
            "requires": {'astral_beacon': 'max'},
            "desc": [
            "Вызывает сокрушительный лазерный луч из космоса [F].",
            "Наносит урон по площади (макс. до 75% HP слайма).",
            "Требует Звёздные и Тёмные кактусы."
            ],
            "stat_cur": lambda lvl: f"Орбитальный залп (ур. {lvl}), КД {45 if lvl==1 else (38 if lvl==2 else 30)}с [F]" if lvl > 0 else "Орбитальный луч не активен",
            "stat_nxt": lambda lvl: f"Усиление залпа до ур. {lvl + 1}, КД {38 if lvl==1 else 30}с [F]",
            "icon_key": "dark_cactus",
        },
        "dark_vitality": {
            "title": "Тёмная Живучесть",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "dark",
            "x": 100,
            "y": 1820,
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
            "icon_key": "heart",
        },
        "cactus_drone": {
            "title": "Дрон-Кактус",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "hybrid",
            "x": 220,
            "y": 1820,
            "max_lvl": 3,
            "costs": [25, 45, 75],
            "dark_costs": [1, 2, 3],
            "requires": {'orbital_strike': 1},
            "desc": [
            "Автономный боевой дрон летает над полем боя.",
            "Непрерывно обстреливает слаймов иглами!",
            "+50% урона и скорострельности за уровень."
            ],
            "stat_cur": lambda lvl: f"Боевой дрон активен (ур. {lvl})" if lvl > 0 else "Дрон не построен",
            "stat_nxt": lambda lvl: f"Усиление дрона до ур. {lvl + 1}",
            "icon_key": "drone",
        },
        "shatter_nova": {
            "title": "Сверхновая Раскола",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "hybrid",
            "x": 480,
            "y": 1820,
            "max_lvl": 3,
            "costs": [30, 50, 85],
            "dark_costs": [2, 3, 5],
            "requires": {'orbital_strike': 1},
            "desc": [
            "Абсолютный взрыв при поражении боссов и метеоритов.",
            "Замораживает и наносит колоссальный урон всем",
            "окружающим слаймам на тропе!"
            ],
            "stat_cur": lambda lvl: f"Урон сверхновой: {1000 if lvl==1 else (2500 if lvl==2 else 5000)}" if lvl > 0 else "Сверхновая не активна",
            "stat_nxt": lambda lvl: f"Урон сверхновой: {1000 if lvl==0 else (2500 if lvl==1 else 5000)}",
            "icon_key": "meteor",
        },
        "void_amplifier": {
            "title": "Усилитель Бездны",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "hybrid",
            "x": 350,
            "y": 1820,
            "max_lvl": 3,
            "costs": [35, 65, 110],
            "dark_costs": [2, 4, 6],
            "requires": {'orbital_strike': 2},
            "desc": [
            "Тёмный космический резонанс всех башен оазиса.",
            "+12% общего урона для башен, воинов и дрона за ранг!",
            "Требует синтез Звёздных и Тёмных кактусов."
            ],
            "stat_cur": lambda lvl: f"+{lvl * 12}% общего урона оазиса (Тёмная мощь)" if lvl > 0 else "Без резонанса Бездны",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 12}% общего урона оазиса",
            "icon_key": "damage",
        },
        "void_infusion": {
            "title": "Эссенция Бездны",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "hybrid",
            "x": 220,
            "y": 1970,
            "max_lvl": 3,
            "costs": [35, 60, 95],
            "dark_costs": [2, 4, 6],
            "requires": {'cactus_drone': 1, 'void_amplifier': 1},
            "desc": [
            "Насыщает выстрелы всех башен чистой Бездной.",
            "Критические удары игнорируют броню и наносят",
            "чистый урон Бездны сквозь любое сопротивление!"
            ],
            "stat_cur": lambda lvl: f"Криты игнорируют {lvl * 10}% сопротивлений мобов" if lvl > 0 else "Обычные криты",
            "stat_nxt": lambda lvl: f"Криты игнорируют {(lvl + 1) * 10}% сопротивлений мобов",
            "icon_key": "damage",
        },
        "dark_alchemy": {
            "title": "Тёмная Алхимия",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "hybrid",
            "x": 480,
            "y": 1970,
            "max_lvl": 2,
            "costs": [45, 90],
            "dark_costs": [3, 5],
            "requires": {'shatter_nova': 1, 'void_amplifier': 1},
            "desc": [
            "Тёмный синтез кристаллов Бездны.",
            "Победа над великими боссами (каждые 25 волн)",
            "приносит +1 дополнительный Тёмный кактус за ранг!"
            ],
            "stat_cur": lambda lvl: f"+{lvl} доп. Тёмный кактус за победу над боссами" if lvl > 0 else "Без алхимии Тьмы",
            "stat_nxt": lambda lvl: f"+{lvl + 1} доп. Тёмный кактус за победу над боссами",
            "icon_key": "dark_cactus",
        },
        "event_horizon": {
            "title": "Горизонт Событий",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "hybrid",
            "x": 280,
            "y": 2120,
            "max_lvl": 2,
            "costs": [45, 85],
            "dark_costs": [3, 6],
            "requires": {'void_infusion': 1, 'void_amplifier': 2},
            "desc": [
            "Гравитационная сингулярность Орбитального Удара [F].",
            "В точке удара открывается чёрная дыра, которая",
            "стягивает врагов к центру и замедляет их на 60%!"
            ],
            "stat_cur": lambda lvl: f"Сингулярность {1 + lvl}с (стягивание и 60% мороз)" if lvl > 0 else "Без чёрной дыры",
            "stat_nxt": lambda lvl: f"Сингулярность {2 + lvl}с (стягивание и 60% мороз)",
            "icon_key": "dark_cactus",
        },
        "quantum_harvester": {
            "title": "Квантовый Жнец",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "hybrid",
            "x": 420,
            "y": 2120,
            "max_lvl": 2,
            "costs": [50, 95],
            "dark_costs": [4, 7],
            "requires": {'dark_alchemy': 1, 'void_amplifier': 2},
            "desc": [
            "Квантовая переработка поверженных боссов оазиса.",
            "Даёт +25% семян от текущей казны за каждого босса",
            "и повышает шанс редких сортов в Оранжерее!"
            ],
            "stat_cur": lambda lvl: f"+{lvl * 25}% награды за боссов и удача Оранжереи" if lvl > 0 else "Без квантового жнеца",
            "stat_nxt": lambda lvl: f"+{(lvl + 1) * 25}% награды за боссов",
            "icon_key": "farm",
        },
        "dark_transcendence": {
            "title": "Тёмный Предел",
            "branch": "astral",
            "branch_title": "Тёмный Космос",
            "currency": "hybrid",
            "scale": 1.8,
            "x": 350,
            "y": 2270,
            "max_lvl": 5,
            "costs": [40, 65, 95, 130, 180],
            "dark_costs": [3, 5, 8, 12, 18],
            "requires": {'event_horizon': 1, 'quantum_harvester': 1},
            "desc": [
            "Расширяет предельный уровень прокачки",
            "всех видов башен на +1 за ранг (до +5)."
            ],
            "stat_cur": lambda lvl: f"+{lvl} к макс. уровню всех башен" if lvl > 0 else "Базовый предел башен",
            "stat_nxt": lambda lvl: f"+{lvl + 1} к макс. уровню всех башен",
            "icon_key": "crown",
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