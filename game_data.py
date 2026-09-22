from tree_data_v02 import (
    BESTIARY_TIER_THRESHOLDS,
    ROMAN_TIERS,
    get_bestiary_tier_thresholds,
    get_mob_bestiary_tier,
    get_mob_bestiary_progress,
    get_bestiary_buffs,
    get_all_81_nodes,
    get_metro_route,
    get_fillet_points,
)
"""
game_data.py - Управление сохранениями, бестиарием, деревом талантов, анализом волн и достижениями.
"""

import json
import os
import random
import time
from datetime import datetime
from config import (
    BASE_DIR, IS_ANDROID, MAP_NAMES_LIST, MAP_BIOMES_DATA, MAP_UNLOCK_REQS,
    MASTERY_MILESTONES, OLD_MASTERY_REWARDS, NEW_MASTERY_REWARDS, get_map_mastery_milestones,
    mob1_img, mob2_img, mob3_img, mob4_img, mob5_img, mob6_img,
    mob7_img, mob8_img, mob9_img, mob10_img,
    gold_slime_img, boss_img, cactus_img, stellar_cactus_img,
    sword_icon, crown_upg_icon, bounty_upg_icon, farm_tower_img,
    soldier_img, tesla_tower_img, magic_tower_img, rock_tower_img,
    freeze_tower_img, tent_tower_img, sun_tower_img, dark_cactus_img, stellar_cactus_img_s,
    speed_upg_icon, health_upg_icon, damage_upg_icon, start_cacti_icon,
    wave_upg_icon, magnet_upg_icon, start_lvl_icon, trophy_icon,
    colossus_boss_img, void_boss_img, void_lord_boss_img,
    gh_cacti_textures, sprout_icon, sprout_icon_s,
    shovel_icon, shovel_icon_s, relic_icon, relic_icon_s
)

# -------------------------------------------------------------------------
# БЕСТИАРИЙ СЛАЙМОВ
# -------------------------------------------------------------------------
BESTIARY_DATA = [
    {
        "id": 1,
        "name": "Зелёный Слайм",
        "title": "Обычный разведчик",
        "desc": "Самый многочисленный обитатель троп. Медленный и мягкий, легко устраняется базовыми башнями.",
        "img_key": "mob1",
        "base_hp": 3,
        "speed": "Средняя (90)",
        "base_damage": 1,
        "special": "Отсутствует (базовый слайм)",
        "is_boss": False
    },
    {
        "id": 2,
        "name": "Синий Слайм",
        "title": "Упругий прыгун",
        "desc": "Плотная холодная слизь. Обладает естественной устойчивостью к холоду и замедлению.",
        "img_key": "mob2",
        "base_hp": 6,
        "speed": "Умеренная (62)",
        "base_damage": 2,
        "special": "Сопротивление холоду (замедление -40%)",
        "is_boss": False
    },
    {
        "id": 3,
        "name": "Магический Слайм",
        "title": "Эфирный сгусток",
        "desc": "Пурпурный сгусток астральной магии шахт. Плотное эфирное поле частично поглощает заклинания башен.",
        "img_key": "mob3",
        "base_hp": 12,
        "speed": "Медленная (46)",
        "base_damage": 2,
        "special": "Сопротивление магии 35%",
        "is_boss": False
    },
    {
        "id": 4,
        "name": "Быстрый Слайм",
        "title": "Стремительный бегун",
        "desc": "Лёгкий и юркий слайм. Благодаря стремительному метаболизму быстро стряхивает с себя заморозку.",
        "img_key": "mob4",
        "base_hp": 4,
        "speed": "Сверхбыстрая (130)",
        "base_damage": 1,
        "special": "Быстрый метаболизм (время заморозки -50%)",
        "is_boss": False
    },
    {
        "id": 5,
        "name": "Каменный Слайм",
        "title": "Панцирный танк",
        "desc": "Тяжёлый бронированный слайм. Обычные снаряды отскакивают от его кристаллической коры.",
        "img_key": "mob5",
        "base_hp": 15,
        "speed": "Тяжелая (50)",
        "base_damage": 3,
        "special": "Каменная броня (-50% урона от камней и солдат)",
        "is_boss": False
    },
    {
        "id": 6,
        "name": "Слайм-Лекарь",
        "title": "Знахарь стаи",
        "desc": "Излучает целебные споры, восстанавливающие здоровье соседним слаймам на тропе.",
        "img_key": "mob6",
        "base_hp": 10,
        "speed": "Умеренная (60)",
        "base_damage": 2,
        "special": "Аура исцеления стаи (раз в 2.5с) | Магический щит 45%",
        "is_boss": False
    },
    {
        "id": 7,
        "name": "Тигровый Слайм",
        "title": "Хищный прыгун",
        "desc": "Свирепый полосатый слайм с острова Имбиря. Резко совершает стремительные прыжки вперед!",
        "img_key": "mob7",
        "base_hp": 12,
        "speed": "Быстрая (88)",
        "base_damage": 2,
        "special": "Рывок хищника: прыжок со скоростью x2.4",
        "is_boss": False
    },
    {
        "id": 8,
        "name": "Ледяное Желе",
        "title": "Хрустальный хлад",
        "desc": "Абсолютно невосприимчив к морозу. Зато горит ярче обычного от пламени Огненной башни!",
        "img_key": "mob8",
        "base_hp": 22,
        "speed": "Средняя (66)",
        "base_damage": 2,
        "special": "Иммунитет к льду | Уязвимость к огню (+60%)",
        "is_boss": False
    },
    {
        "id": 9,
        "name": "Слаймовая Пирамида",
        "title": "Тройной симбиоз",
        "desc": "Пирамида из нескольких слаймов. После уничтожения распадается на двух быстрых бегунов!",
        "img_key": "mob9",
        "base_hp": 36,
        "speed": "Тяжелая (48)",
        "base_damage": 3,
        "special": "Раскол: распадается на 2 быстрых слайма",
        "is_boss": False
    },
    {
        "id": 10,
        "name": "Теневой Слайм",
        "title": "Порождение Бездны",
        "desc": "Тёмный слайм шахт. Обладает врождённым сопротивлением магии и теневой защитой.",
        "img_key": "mob10",
        "base_hp": 26,
        "speed": "Средняя (63)",
        "base_damage": 3,
        "special": "Теневой покров (-50% урона в скрытности) | Антимагия 45%",
        "is_boss": False
    },
    {
        "id": 777,
        "name": "Золотой Слайм",
        "title": "Редкий слайм",
        "desc": "Редкий золотистый слайм. При уничтожении дает 150 кактусов и гарантированный Звёздный кактус.",
        "img_key": "gold_slime",
        "base_hp": 22,
        "speed": "Быстрая (98)",
        "base_damage": 1,
        "special": "+150 кактусов и Звёздный Кактус при гибели",
        "is_boss": False
    },
    {
        "id": 51,
        "name": "Элитный Страж",
        "title": "Закалённый боец",
        "desc": "Тяжёлый слайм поздних волн. Усиленная броня и высокая живучесть.",
        "img_key": "mob1",
        "base_hp": 25,
        "speed": "Средняя (95)",
        "base_damage": 3,
        "special": "Элитная броня (-50% физ. урона)",
        "is_boss": False
    },
    {
        "id": 52,
        "name": "Элитный Крушитель",
        "title": "Осадный таран",
        "desc": "Массивный элитный слайм. Легко сминает гарнизон палатки и выдерживает удары камней.",
        "img_key": "mob2",
        "base_hp": 50,
        "speed": "Умеренная (65)",
        "base_damage": 4,
        "special": "Осадная броня (-50% физ. урона) | Сокрушение воинов",
        "is_boss": False
    },
    {
        "id": 53,
        "name": "Элитный Титан",
        "title": "Тяжелый авангард",
        "desc": "Крупный элитный слайм. Высокий запас здоровья и устойчивость к магии.",
        "img_key": "mob3",
        "base_hp": 90,
        "speed": "Тяжелая (48)",
        "base_damage": 5,
        "special": "Броня и сопротивление магии 35%",
        "is_boss": False
    },
    {
        "id": 1000,
        "name": "Царь-Слизень",
        "title": "Босс 25-й волны",
        "desc": "Первый босс шахт. Идёт напролом, давит солдат и требует сосредоточенного огня.",
        "img_key": "boss",
        "base_hp": 3300,
        "speed": "Медленный (22)",
        "base_damage": "∞",
        "special": "БОСС: 3300+ HP, сминает воинов, без защиты от льда (0%)",
        "is_boss": True
    },
    {
        "id": 2000,
        "name": "Слизнебарон",
        "title": "Босс 50-й волны",
        "desc": "Морозный синий гигант. Имеет прочную броню и частичную защиту от заморозки.",
        "img_key": "colossus_boss",
        "base_hp": 15500,
        "speed": "Медленный (25)",
        "base_damage": "∞",
        "special": "БОСС: 15500+ HP, ледяная броня, резист заморозке 50%",
        "is_boss": True
    },
    {
        "id": 3000,
        "name": "Багровый Титан",
        "title": "Босс 75-й волны",
        "desc": "Раскаленный исполин из магматических глубин. Высокое здоровье и устойчивость к магии.",
        "img_key": "void_boss",
        "base_hp": 56000,
        "speed": "Медленный (28)",
        "base_damage": "∞",
        "special": "БОСС: 56000+ HP, резист магии 40%, уязвимость к льду (-10%)",
        "is_boss": True
    },
    {
        "id": 4000,
        "name": "Король Всех Слаймов",
        "title": "Финальный Босс (100-я волна)",
        "desc": "Финальный иридиевый босс. Колоссальный запас здоровья и мгновенный прорыв базы при утечке.",
        "img_key": "void_lord_boss",
        "base_hp": 155000,
        "speed": "Неумолимый (26)",
        "base_damage": "∞",
        "special": "ФИНАЛ: 155000+ HP, резист заморозке 30% (+10%/ур. до 75%)",
        "is_boss": True
    }
]

def get_slime_texture(key):
    mapping = {
        "mob1": mob1_img,
        "mob2": mob2_img,
        "mob3": mob3_img,
        "mob4": mob4_img,
        "mob5": mob5_img,
        "mob6": mob6_img,
        "mob7": mob7_img,
        "mob8": mob8_img,
        "mob9": mob9_img,
        "mob10": mob10_img,
        "gold_slime": gold_slime_img,
        "boss": boss_img,
        "colossus_boss": colossus_boss_img,
        "void_boss": void_boss_img,
        "void_lord_boss": void_lord_boss_img
    }
    return mapping.get(key, mob1_img)

def calculate_hp_modificator(wave):
    if wave <= 1:
        return 1.0
    if wave <= 25:
        # Мягкий гармоничный старт на ранних волнах с плавным выходом на 10.48 к волне 25
        t = (wave - 1) / 24.0
        return 1.0 + (wave - 1) * 0.20 + (t ** 1.8) * 4.68
    elif wave <= 50:
        base_w25 = 10.48
        w_post25 = wave - 25
        return base_w25 * (1.038 ** w_post25)
    elif wave <= 75:
        base_w25 = 10.48
        base_w50 = base_w25 * (1.038 ** 25)  # 26.78
        w_post50 = wave - 50
        return base_w50 * (1.030 ** w_post50)
    else:
        base_w25 = 10.48
        base_w50 = base_w25 * (1.038 ** 25)
        base_w75 = base_w50 * (1.030 ** 25)  # 56.07
        w_post75 = wave - 75
        return base_w75 * (1.022 ** w_post75)

# -------------------------------------------------------------------------
# КОЛЛЕКЦИЯ КАКТУСОВ ОРАНЖЕРЕИ (GREENHOUSE FLORA)
# -------------------------------------------------------------------------
GREENHOUSE_CACTI = [
    {
        "id": "saguaro",
        "name": "Пустынный Сагуаро",
        "title": "Стойкий исполин",
        "desc": "Величественный кактус пустыни Сонора. Его мощная кора и глубокие корни закаляют Оазис, укрепляя запас жизней и шипы.",
        "img_key": "gh_saguaro",
        "req_sprouts": [1, 3, 8, 18, 35],
        "buff_name": "Каменная кора Оазиса",
        "buff_desc": [
            "+1 к максимальным жизням базы",
            "+2 к жизням базы, +10% урона шипов",
            "+4 к жизням базы, +20% урона шипов",
            "+6 к жизням базы, +30% урона шипов, 3% блок урона",
            "+8 к жизням базы, +40% урона шипов, 5% блок урона"
        ],
        "stats": [
            {"base_hp": 1, "thorn_mult": 0.0, "block_chance": 0.0},
            {"base_hp": 2, "thorn_mult": 0.10, "block_chance": 0.0},
            {"base_hp": 4, "thorn_mult": 0.20, "block_chance": 0.0},
            {"base_hp": 6, "thorn_mult": 0.30, "block_chance": 0.03},
            {"base_hp": 8, "thorn_mult": 0.40, "block_chance": 0.05},
        ]
    },
    {
        "id": "opuntia",
        "name": "Золотая Опунция",
        "title": "Плод изобилия",
        "desc": "Сверкающая сочными жёлтыми плодами опунция. Притягивает караваны торговцев и осыпает Оазис золотом.",
        "img_key": "gh_opuntia",
        "req_sprouts": [1, 3, 8, 18, 35],
        "buff_name": "Щедрый урожай",
        "buff_desc": [
            "+25 кактусов на старте боя",
            "+50 кактусов, +3% семян за слаймов",
            "+75 кактусов, +6% семян за слаймов",
            "+100 кактусов, +10% семян, +6% дохода ферм",
            "+140 кактусов, +14% семян, +12% дохода ферм"
        ],
        "stats": [
            {"start_gold": 25, "bounty_mult": 0.0, "farm_mult": 0.0},
            {"start_gold": 50, "bounty_mult": 0.03, "farm_mult": 0.0},
            {"start_gold": 75, "bounty_mult": 0.06, "farm_mult": 0.0},
            {"start_gold": 100, "bounty_mult": 0.10, "farm_mult": 0.06},
            {"start_gold": 140, "bounty_mult": 0.14, "farm_mult": 0.12},
        ]
    },
    {
        "id": "fire_barrel",
        "name": "Огненный Бочонок",
        "title": "Магматический колючник",
        "desc": "Ствол этого кактуса наполнен кипящей смолой. Распаляет ярость Огненных башен и поджигает слаймов.",
        "img_key": "gh_fire_barrel",
        "req_sprouts": [1, 3, 8, 18, 35],
        "buff_name": "Негасимое пламя",
        "buff_desc": [
            "+3% урона Огненной башни",
            "+6% урона Огненной башни, горение длится +0.5 сек.",
            "+10% урона Огненной башни, горение длится +1.0 сек.",
            "+14% урона Огня, горящие мобы получают +5% от всех башен",
            "+18% урона Огня, взрыв магмы при гибели горящего моба"
        ],
        "stats": [
            {"fire_dmg_mult": 0.03, "burn_extra_sec": 0.0, "burn_vuln": 0.0, "magma_burst": False},
            {"fire_dmg_mult": 0.06, "burn_extra_sec": 0.5, "burn_vuln": 0.0, "magma_burst": False},
            {"fire_dmg_mult": 0.10, "burn_extra_sec": 1.0, "burn_vuln": 0.0, "magma_burst": False},
            {"fire_dmg_mult": 0.14, "burn_extra_sec": 1.2, "burn_vuln": 0.05, "magma_burst": False},
            {"fire_dmg_mult": 0.18, "burn_extra_sec": 1.5, "burn_vuln": 0.08, "magma_burst": True},
        ]
    },
    {
        "id": "frost_aloe",
        "name": "Ледяной Алоэ",
        "title": "Хрустальная прохлада",
        "desc": "Листья наполнены прозрачным гелевым льдом. Усиливает морозное поле и сковывает даже быстрых слаймов.",
        "img_key": "gh_frost_aloe",
        "req_sprouts": [1, 3, 8, 18, 35],
        "buff_name": "Глубокая заморозка",
        "buff_desc": [
            "+4% к силе замедления Ледяной башни",
            "+7% к замедлению, +6% к радиусу действия",
            "+11% к замедлению, +10% к радиусу действия",
            "+15% к замедлению, замороженные враги теряют 8% брони",
            "+20% к замедлению, 6% шанс вморозить моба в глыбу на 1.0 с."
        ],
        "stats": [
            {"frost_slow_mult": 0.04, "frost_range_mult": 0.0, "armor_shred": 0.0, "permafrost": False},
            {"frost_slow_mult": 0.07, "frost_range_mult": 0.06, "armor_shred": 0.0, "permafrost": False},
            {"frost_slow_mult": 0.11, "frost_range_mult": 0.10, "armor_shred": 0.0, "permafrost": False},
            {"frost_slow_mult": 0.15, "frost_range_mult": 0.14, "armor_shred": 0.08, "permafrost": False},
            {"frost_slow_mult": 0.20, "frost_range_mult": 0.18, "armor_shred": 0.12, "permafrost": True},
        ]
    },
    {
        "id": "thunder_echino",
        "name": "Громовой Эхино",
        "title": "Электростатический шар",
        "desc": "Сферический колючий шар, накапливающий разряды бурь. Заряжает молнии Башни Тесла дополнительными скачками.",
        "img_key": "gh_thunder_echino",
        "req_sprouts": [1, 3, 8, 18, 35],
        "buff_name": "Ионизация воздуха",
        "buff_desc": [
            "+1 рикошет цепной молнии Башни Тесла",
            "+1 рикошет, +5% к урону молний",
            "+1 рикошет, +9% к урону молний",
            "+2 рикошета, +13% к урону, 3% шанс оглушить на 0.5 с.",
            "+2 рикошета, +18% к урону, 6% шанс оглушить на 0.5 с."
        ],
        "stats": [
            {"extra_jumps": 1, "tesla_dmg_mult": 0.0, "stun_chance": 0.0},
            {"extra_jumps": 1, "tesla_dmg_mult": 0.05, "stun_chance": 0.0},
            {"extra_jumps": 1, "tesla_dmg_mult": 0.09, "stun_chance": 0.0},
            {"extra_jumps": 2, "tesla_dmg_mult": 0.13, "stun_chance": 0.03},
            {"extra_jumps": 2, "tesla_dmg_mult": 0.18, "stun_chance": 0.06},
        ]
    },
    {
        "id": "void_astrophytum",
        "name": "Астрофитум Бездны",
        "title": "Поглотитель мрака",
        "desc": "Звёздчатый чёрно-фиолетовый кактус из глубинных шахт. Пробивает теневой покров и уничтожает элиту.",
        "img_key": "gh_void_astrophytum",
        "req_sprouts": [1, 3, 8, 18, 35],
        "buff_name": "Анти-Энтропия",
        "buff_desc": [
            "+6% урона всех башен по Теневым слаймам и боссам",
            "+11% урона по ним, игнорирует 10% маг. защиты",
            "+16% урона по ним, игнорирует 16% маг. защиты",
            "+22% урона, +8% урона Орбитального удара",
            "+28% урона, +15% урона Орбиталки, 1% дроп Зв. кактуса с элиты"
        ],
        "stats": [
            {"void_dmg_mult": 0.06, "pierce_magic": 0.0, "orbital_mult": 0.0, "elite_star_drop": False},
            {"void_dmg_mult": 0.11, "pierce_magic": 0.10, "orbital_mult": 0.0, "elite_star_drop": False},
            {"void_dmg_mult": 0.16, "pierce_magic": 0.16, "orbital_mult": 0.0, "elite_star_drop": False},
            {"void_dmg_mult": 0.22, "pierce_magic": 0.22, "orbital_mult": 0.08, "elite_star_drop": False},
            {"void_dmg_mult": 0.28, "pierce_magic": 0.30, "orbital_mult": 0.15, "elite_star_drop": True},
        ]
    },
    {
        "id": "stellar_queen",
        "name": "Звёздный Цереус",
        "title": "Царица Ночи",
        "desc": "Цветёт один раз в столетие в час парада планет. Усиливает Боевой Дрон и притягивает звёздную пыль.",
        "img_key": "gh_stellar_queen",
        "req_sprouts": [1, 3, 8, 18, 35],
        "buff_name": "Астральный резонанс",
        "buff_desc": [
            "+10% урона Боевого Дрона",
            "+20% урона Дрона, +3% шанс дропа Звёздных кактусов",
            "+30% урона Дрона, +6% шанс дропа Звёздных кактусов",
            "+40% урона Дрона, +10% скорость атаки, +9% шанс дропа звёзд",
            "+50% урона Дрона, +15% скорость атаки, Дрон атакует 2 цели!"
        ],
        "stats": [
            {"drone_dmg_mult": 0.10, "star_drop_bonus": 0.0, "drone_spd_mult": 0.0, "dual_drone": False},
            {"drone_dmg_mult": 0.20, "star_drop_bonus": 0.03, "drone_spd_mult": 0.0, "dual_drone": False},
            {"drone_dmg_mult": 0.30, "star_drop_bonus": 0.06, "drone_spd_mult": 0.0, "dual_drone": False},
            {"drone_dmg_mult": 0.40, "star_drop_bonus": 0.09, "drone_spd_mult": 0.10, "dual_drone": False},
            {"drone_dmg_mult": 0.50, "star_drop_bonus": 0.12, "drone_spd_mult": 0.15, "dual_drone": True},
        ]
    },
    {
        "id": "mammillaria",
        "name": "Цветущая Мамиллярия",
        "title": "Вдохновение Оазиса",
        "desc": "Украшена венком алых цветов. Вдохновляет солдат Палатки на стойкую защиту рубежей Оазиса.",
        "img_key": "gh_mammillaria",
        "req_sprouts": [1, 3, 8, 18, 35],
        "buff_name": "Боевое братство",
        "buff_desc": [
            "Воины в Палатке возрождаются на 10% быстрее",
            "Возрождение на 16% быстрее, +15% HP воинам",
            "Возрождение на 22% быстрее, +28% HP, +10% урона",
            "Воины получают щит, поглощающий первый удар",
            "Воины контратакуют залпом шипов при получении урона!"
        ],
        "stats": [
            {"respawn_mult": 0.10, "soldier_hp_mult": 0.0, "soldier_dmg_mult": 0.0, "soldier_shield": False, "soldier_thorns": False},
            {"respawn_mult": 0.16, "soldier_hp_mult": 0.15, "soldier_dmg_mult": 0.0, "soldier_shield": False, "soldier_thorns": False},
            {"respawn_mult": 0.22, "soldier_hp_mult": 0.28, "soldier_dmg_mult": 0.10, "soldier_shield": False, "soldier_thorns": False},
            {"respawn_mult": 0.30, "soldier_hp_mult": 0.42, "soldier_dmg_mult": 0.16, "soldier_shield": True, "soldier_thorns": False},
            {"respawn_mult": 0.38, "soldier_hp_mult": 0.55, "soldier_dmg_mult": 0.22, "soldier_shield": True, "soldier_thorns": True},
        ]
    }
]

def get_greenhouse_buffs(savedata):
    gh = savedata.get("Greenhouse", {})
    aggregated = {
        "base_hp": 0,
        "thorn_mult": 0.0,
        "block_chance": 0.0,
        "start_gold": 0,
        "bounty_mult": 0.0,
        "farm_mult": 0.0,
        "fire_dmg_mult": 0.0,
        "burn_extra_sec": 0.0,
        "burn_vuln": 0.0,
        "magma_burst": False,
        "frost_slow_mult": 0.0,
        "frost_range_mult": 0.0,
        "armor_shred": 0.0,
        "permafrost": False,
        "extra_jumps": 0,
        "tesla_dmg_mult": 0.0,
        "stun_chance": 0.0,
        "void_dmg_mult": 0.0,
        "pierce_magic": 0.0,
        "orbital_mult": 0.0,
        "elite_star_drop": False,
        "drone_dmg_mult": 0.0,
        "star_drop_bonus": 0.0,
        "drone_spd_mult": 0.0,
        "dual_drone": False,
        "respawn_mult": 0.0,
        "soldier_hp_mult": 0.0,
        "soldier_dmg_mult": 0.0,
        "soldier_shield": False,
        "soldier_thorns": False,
    }
    for item in GREENHOUSE_CACTI:
        cid = item["id"]
        c_info = gh.get(cid, {})
        lvl = c_info.get("level", 0)
        if lvl > 0 and lvl <= len(item["stats"]):
            c_stat = item["stats"][lvl - 1]
            for sk, sv in c_stat.items():
                if isinstance(sv, bool):
                    if sv: aggregated[sk] = True
                elif isinstance(sv, (int, float)):
                    aggregated[sk] = aggregated.get(sk, 0) + sv

    # Учет таланта «Резонанс Флоры» (+10% ко всем эффектам Оранжереи за ранг)
    reso_lvl = savedata.get("Upgrades", {}).get("flora_resonance", 0)
    if reso_lvl > 0:
        reso_mult = 1.0 + reso_lvl * 0.10
        for k, v in aggregated.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                aggregated[k] = type(v)(round(v * reso_mult)) if isinstance(v, int) else (v * reso_mult)

    # Учет таланта «Живой Компост» (+0.2% урона ВСЕМ башням за каждый суммарный уровень кактуса в Оранжерее)
    compost_lvl = savedata.get("Upgrades", {}).get("fertile_compost", 0)
    if compost_lvl > 0:
        total_cacti_levels = sum(gh.get(item["id"], {}).get("level", 0) for item in GREENHOUSE_CACTI)
        aggregated["compost_dmg_mult"] = total_cacti_levels * (compost_lvl * 0.002)
    else:
        aggregated["compost_dmg_mult"] = 0.0

    return aggregated

def count_open_greenhouse_cacti(sdata=None):
    if sdata is None:
        sdata = globals().get("savedata", {})
    if not isinstance(sdata, dict):
        return 0
    gh = sdata.get("Greenhouse", {})
    return sum(1 for item in GREENHOUSE_CACTI if gh.get(item["id"], {}).get("level", 0) > 0)

def count_total_greenhouse_cacti_levels(sdata=None):
    if sdata is None:
        sdata = globals().get("savedata", {})
    if not isinstance(sdata, dict):
        return 0
    gh = sdata.get("Greenhouse", {})
    total = sum(gh.get(item["id"], {}).get("level", 0) for item in GREENHOUSE_CACTI)
    known_ids = {item["id"] for item in GREENHOUSE_CACTI}
    for cid, cdata in gh.items():
        if cid not in known_ids and isinstance(cdata, dict):
            total += cdata.get("level", 0)
    return total

def is_greenhouse_unlocked(savedata):
    return savedata.get("Upgrades", {}).get("greenhouse_unlock", 0) > 0

def is_dark_cacti_unlocked(savedata):
    if not isinstance(savedata, dict):
        return False
    return savedata.get("Upgrades", {}).get("astral_beacon", 0) > 0

def has_upgradeable_greenhouse(savedata):
    if not is_greenhouse_unlocked(savedata):
        return False
    gh = savedata.get("Greenhouse", {})
    for item in GREENHOUSE_CACTI:
        cid = item["id"]
        c_info = gh.get(cid, {"level": 0, "sprouts": 0})
        lvl = c_info.get("level", 0)
        sprouts = c_info.get("sprouts", 0)
        if lvl < len(item["req_sprouts"]):
            req = get_greenhouse_sprout_req(item, lvl, savedata)
            if sprouts >= req:
                return True
    return False

def get_greenhouse_sprout_req(item, lvl, savedata=None):
    if lvl < len(item["req_sprouts"]):
        req = item["req_sprouts"][lvl]
        sdata = savedata if isinstance(savedata, dict) else globals().get("savedata", None)
        if sdata and isinstance(sdata, dict) and sdata.get("difficulty") == "hardcore":
            req *= 2
        return req
    return 999999

def level_up_greenhouse_cactus(savedata, cactus_id):
    gh = savedata.setdefault("Greenhouse", {})
    c_info = gh.setdefault(cactus_id, {"level": 0, "sprouts": 0})
    for item in GREENHOUSE_CACTI:
        if item["id"] == cactus_id:
            lvl = c_info.get("level", 0)
            sprouts = c_info.get("sprouts", 0)
            if lvl < len(item["req_sprouts"]):
                req = get_greenhouse_sprout_req(item, lvl, savedata)
                if sprouts >= req:
                    c_info["level"] = lvl + 1
                    c_info["sprouts"] = sprouts - req
                    return True, c_info["level"]
    return False, c_info.get("level", 0)

def grant_cactus_sprout(savedata, cactus_id=None, count=1):
    diff = savedata.get("difficulty", "normal") if isinstance(savedata, dict) else "normal"
    if diff == "casual" and random.random() < 0.50:
        count += 1
    elif diff == "hardcore" and random.random() < 0.25:
        return None, None

    gh = savedata.setdefault("Greenhouse", {})
    if not cactus_id:
        qh_lvl = savedata.get("Upgrades", {}).get("quantum_harvester", 0) if isinstance(savedata, dict) else 0
        c_list = [c["id"] for c in GREENHOUSE_CACTI]
        if qh_lvl > 0 and len(c_list) > 3:
            # Квантовый Жнец увеличивает шанс выпадения редких и поздних сортов кактусов
            weights = [1.0 + (idx / max(1, len(GREENHOUSE_CACTI) - 1)) * (qh_lvl * 1.6) for idx in range(len(GREENHOUSE_CACTI))]
            cactus_id = random.choices(c_list, weights=weights, k=1)[0]
        else:
            cactus_id = random.choice(c_list)
    c_info = gh.setdefault(cactus_id, {"level": 0, "sprouts": 0})
    c_info["sprouts"] = c_info.get("sprouts", 0) + count
    c_name = cactus_id
    for item in GREENHOUSE_CACTI:
        if item["id"] == cactus_id:
            c_name = item["name"]
    return cactus_id, c_name

def generate_wave_roster(wave_num, map_id=0, sdata=None, rng=None):
    if rng is None:
        rng = random

    if wave_num % 25 == 0:
        boss_tier = wave_num // 25
        if boss_tier >= 4:
            b_type = 4000
            # Свита Истинного Владыки Бездны (Волна 100+): свирепые прыгуны, ледяные, пирамиды, теневые, элита
            escort = [7]*6 + [8]*6 + [9]*6 + [10]*6 + [51]*6 + [52]*6 + [53]*4 + [777]*2
        elif boss_tier == 3:
            b_type = 3000
            # Свита Владыки Бездны (Волна 75): Теневые слаймы, тигры, пирамиды, элита
            escort = [10]*6 + [7]*6 + [9]*6 + [5]*6 + [6]*6 + [51]*6 + [52]*4 + [53]*2
        elif boss_tier == 2:
            b_type = 2000
            # Свита Слизнебарона (Волна 50): Золотые слаймы, пирамиды, броня, целители, бегуны
            escort = [4]*8 + [9]*6 + [3]*6 + [6]*6 + [5]*8 + [51]*6 + [777]*1
        else:
            b_type = 1000
            # Свита Царя-Слизня (Волна 25): бегуны, тигры, броня, целители
            escort = [4]*6 + [2]*6 + [7]*4 + [5]*6 + [6]*4
        half = len(escort) // 2
        return escort[:half] + [b_type] + escort[half:]

    count = int((wave_num + 1) ** 0.8) + wave_num
    enemies = []

    gf_lvl = sdata.get("Upgrades", {}).get("golden_fortune", 0) if sdata and isinstance(sdata, dict) else 0
    guaranteed_gold = (wave_num >= 20 and (wave_num - 20) % 15 == 0 and gf_lvl > 0)
    has_gold = guaranteed_gold or (wave_num >= 5 and rng.random() < (0.10 + gf_lvl * 0.08))

    # Биом-зависимый пул врагов:
    for _ in range(count):
        if wave_num < 4:
            t = 1
        elif wave_num < 8:
            t = rng.choices([1, 4], weights=[0.6, 0.4])[0]
        else:
            # Начиная с 8-й волны раскрываются специфические виды врагов в зависимости от карты:
            if map_id == 1:  # Круговорот (Снег): доминирует Ледяное Желе (8)
                pool = [1, 2, 4, 8, 5, 6, 51, 52]
                weights = [0.15, 0.20, 0.15, 0.25, 0.10, 0.10, 0.03, 0.02]
            elif map_id == 2:  # Перекрёстки (Песок): Слаймовые Пирамиды (9) и бегуны (4)
                pool = [1, 2, 4, 9, 5, 6, 51, 52]
                weights = [0.15, 0.15, 0.20, 0.25, 0.10, 0.10, 0.03, 0.02]
            elif map_id == 3:  # Волны (Лава): Огненные (3) и Теневые слаймы (10)
                pool = [2, 3, 5, 10, 6, 51, 52, 53]
                weights = [0.15, 0.25, 0.15, 0.20, 0.10, 0.08, 0.05, 0.02]
            elif map_id == 4:  # Змейка (Космос): Тигровые слаймы (7) с прыжками на поворотах
                pool = [2, 4, 7, 5, 6, 10, 51, 52]
                weights = [0.15, 0.20, 0.25, 0.10, 0.10, 0.10, 0.06, 0.04]
            elif map_id == 5:  # Атака (Штурм): Тигровые слаймы (7) и элитные стражи
                pool = [4, 7, 5, 6, 51, 52, 53, 9]
                weights = [0.15, 0.25, 0.15, 0.10, 0.15, 0.10, 0.05, 0.05]
            elif map_id == 6:  # Лабиринт (Кристаллы): Ледяные (8) и Теневые (10)
                pool = [2, 8, 10, 3, 6, 51, 52, 53]
                weights = [0.15, 0.25, 0.20, 0.15, 0.10, 0.08, 0.04, 0.03]
            elif map_id == 7:  # Петля (Токсик): Пирамиды (9), Теневые (10) и тяжёлые танки
                pool = [3, 9, 10, 5, 6, 51, 52, 53]
                weights = [0.10, 0.25, 0.20, 0.15, 0.10, 0.10, 0.06, 0.04]
            elif map_id == 8:  # Финал: Все типы опасных слаймов в яростном темпе
                pool = [3, 5, 6, 7, 8, 9, 10, 51, 52, 53]
                weights = [0.08, 0.10, 0.08, 0.14, 0.14, 0.14, 0.12, 0.08, 0.07, 0.05]
            else:  # Базовый Оазис (0): классическое обучение
                if wave_num < 14:
                    pool, weights = [1, 2, 4, 5], [0.4, 0.25, 0.2, 0.15]
                elif wave_num < 25:
                    pool, weights = [1, 2, 3, 4, 5, 6, 7], [0.2, 0.2, 0.15, 0.15, 0.15, 0.10, 0.05]
                elif wave_num < 50:
                    pool, weights = [2, 3, 5, 6, 7, 8, 9, 51, 52], [0.12, 0.15, 0.15, 0.12, 0.1, 0.1, 0.1, 0.1, 0.06]
                else:
                    pool, weights = [3, 5, 6, 7, 8, 9, 10, 51, 52, 53], [0.10, 0.10, 0.10, 0.12, 0.12, 0.12, 0.12, 0.10, 0.08, 0.04]
            t = rng.choices(pool, weights=weights)[0]
        enemies.append(t)

    if has_gold and enemies:
        enemies[rng.randint(len(enemies) // 3, len(enemies) - 1)] = 777
    return enemies

def get_wave_enemies(wave_num, map_id=0, sdata=None, game_map=None, savedata=None):
    if game_map is not None:
        map_id = game_map
    if savedata is not None:
        sdata = savedata
    return generate_wave_roster(wave_num, map_id, sdata, rng=random)

def get_wave_analysis(map_id, wave_num, sdata=None):
    rng = random.Random(wave_num * 10007 + map_id * 31)
    enemies = generate_wave_roster(wave_num, map_id, sdata, rng=rng)

    total_count = len(enemies)
    hp_mod = calculate_hp_modificator(wave_num)
    biome = MAP_BIOMES_DATA.get(map_id, MAP_BIOMES_DATA[0])
    map_hp = biome.get("hp_mult", 1.0)
    map_spd = biome.get("spd_mult", 1.0)
    map_rew = biome.get("cacti_mult", biome.get("reward_mult", 1.0))
    total_hp_mult = hp_mod * map_hp

    type_counts = {}
    for t in enemies:
        type_counts[t] = type_counts.get(t, 0) + 1

    roster = []
    total_reward = 0

    for t, cnt in sorted(type_counts.items(), key=lambda x: (0 if x[0] >= 1000 else 1, -x[1])):
        b_data = next((s for s in BESTIARY_DATA if s["id"] == t), None)
        if not b_data:
            if t >= 4000: b_data = next((s for s in BESTIARY_DATA if s["id"] == 4000), None)
            elif t >= 3000: b_data = next((s for s in BESTIARY_DATA if s["id"] == 3000), None)
            elif t >= 2000: b_data = next((s for s in BESTIARY_DATA if s["id"] == 2000), None)
            elif t >= 1000: b_data = next((s for s in BESTIARY_DATA if s["id"] == 1000), None)

        if t == 1: base_hp, base_spd, base_rew, base_dmg, traits = 3.0, 90.0, 3, 1, "Базовый моб (Урон: 1)"
        elif t == 2: base_hp, base_spd, base_rew, base_dmg, traits = 6.0, 62.0, 5, 2, "Удвоенный HP (Урон: 2)"
        elif t == 3: base_hp, base_spd, base_rew, base_dmg, traits = 12.0, 46.0, 8, 2, "Маг. щит 35% (Урон: 2)"
        elif t == 4: base_hp, base_spd, base_rew, base_dmg, traits = 4.0, 130.0, 3, 1, "Быстрый бегун (Урон: 1)"
        elif t == 5: base_hp, base_spd, base_rew, base_dmg, traits = 15.0, 50.0, 10, 3, "Тяжёлая броня (Урон: 3)"
        elif t == 6: base_hp, base_spd, base_rew, base_dmg, traits = 10.0, 60.0, 10, 2, "Целитель, щит 45% (Урон: 2)"
        elif t == 777: base_hp, base_spd, base_rew, base_dmg, traits = 22.0, 105.0, 60, 1, "Золотой (+60 🌵, Урон: 1)"
        elif t == 51: base_hp, base_spd, base_rew, base_dmg, traits = 25.0, 85.0, 20, 3, "Элитный страж, броня (Урон: 3)"
        elif t == 52: base_hp, base_spd, base_rew, base_dmg, traits = 50.0, 60.0, 35, 4, "Элитный таран, броня (Урон: 4)"
        elif t == 53: base_hp, base_spd, base_rew, base_dmg, traits = 90.0, 45.0, 60, 5, "Элитный исполин (Урон: 5)"
        elif t >= 4000:
            base_hp = float(155000 * 1.5 ** max(0, wave_num // 25 - 4))
            base_spd, base_rew, base_dmg, traits = 26.0, 15000, "∞", "БОСС: Король Всех Слаймов (Урон ∞)"
        elif t >= 3000:
            base_hp = float(56000 * 1.5 ** max(0, wave_num // 25 - 3))
            base_spd, base_rew, base_dmg, traits = 28.0, 8000, "∞", "БОСС: Урон ∞ (Мгновенное поражение, без блока!)"
        elif t >= 2000:
            base_hp = float(15500 * 1.5 ** max(0, wave_num // 25 - 2))
            base_spd, base_rew, base_dmg, traits = 25.0, 3500, "∞", "БОСС: Урон ∞ (Мгновенное поражение, без блока!)"
        elif t >= 1000:
            base_hp = float(3300 * 1.5 ** max(0, wave_num // 25 - 1))
            base_spd, base_rew, base_dmg, traits = 22.0, 1500, "∞", "БОСС: Урон ∞ (Мгновенное поражение, без блока!)"
        else:
            base_hp, base_spd, base_rew, base_dmg, traits = 5.0, 60.0, 5, 1, "Обычный"

        final_hp = int(base_hp * total_hp_mult) if t < 1000 else int(base_hp * map_hp)
        final_spd = int(base_spd * map_spd)
        final_rew = int(base_rew * map_rew)
        total_reward += final_rew * cnt

        name = b_data["name"] if b_data else f"Слайм #{t}"
        img_key = b_data["img_key"] if b_data else "mob1"

        roster.append({
            "id": t,
            "name": name,
            "img_key": img_key,
            "count": cnt,
            "hp": final_hp,
            "speed": final_spd,
            "reward": final_rew,
            "damage": base_dmg,
            "traits": traits,
            "is_boss": (t >= 1000)
        })

    events = []
    if wave_num % 25 == 0:
        events.append("БОСС")
    if wave_num >= 20:
        events.append("Метеорит")
    if wave_num % 10 == 0:
        events.append("+1 Зв. кактус")
    if any(r["id"] == 777 for r in roster):
        events.append("Золотой слайм")

    return {
        "wave": wave_num,
        "total_count": total_count,
        "hp_mod": hp_mod,
        "map_hp": map_hp,
        "total_hp_mult": total_hp_mult,
        "map_spd": map_spd,
        "map_rew": map_rew,
        "total_reward": total_reward,
        "events": events,
        "roster": roster
    }

def has_unclaimed_bestiary(sdata):
    claimed = sdata.get("BestiaryClaimed", {})
    disc = sdata.get("BestiaryDiscovered", [])
    for s in BESTIARY_DATA:
        sid = s["id"]
        is_claimed = (sid in claimed) if isinstance(claimed, list) else bool(claimed.get(str(sid), False))
        if sid in disc and not is_claimed:
            return True
    return False

# -------------------------------------------------------------------------
# СИСТЕМА СОХРАНЕНИЙ
# -------------------------------------------------------------------------
DEFAULT_SAVE = {
    "PlayerName": "Игрок",
    "LevelsRecords": [0] * len(MAP_NAMES_LIST),
    "CustomMapConfig": {
        "seed": 777,
        "hp_mult": 1.5,
        "spd_mult": 1.0,
        "start_gold": 400,
        "cacti_mult": 1.0,
        "stellar_mult": 1.0,
        "biome_style": 0,
        "endless": True
    },
    "StellarCactuses": 15,
    "StarterStellarBonus": True,
    "DarkCactuses": 0,
    "MasteryClaimed": {},
    "BestiaryDiscovered": [],
    "BestiaryClaimed": {},
    "BestiaryKills": {},
    "FlawlessWaveStreak": 0,
    "Upgrades": {
        "oasis_core": 1,
        "magic_tower": 1,
        "rock_tower": 0,
        "speed_limit": 0,
        "spawn_rush": 0,
        "start_tower_level": 0,
        "freeze_tower": 0,
        "tent_tower": 0,
        "tesla_tower": 0,
        "max_tower_level": 0,
        "start_wave_step": 0,
        "start_cacti": 0,
        "cacti_bounty": 0,
        "global_damage": 0,
        "base_health": 0,
        "stellar_magnet": 0,
        "fertile_soil": 0,
        "overcharge": 0,
        "magic_focus": 0,
        "magic_power": 0,
        "inferno_mastery": 0,
        "frost_nova": 0,
        "knight_training": 0,
        "ball_lightning": 0,
        "sniper_optics": 0,
        "attack_speed_overdrive": 0,
        "meteor_strike": 0,
        "blizzard": 0,
        "shield_wall": 0,
        "tent_thorns": 0,
        "superconductor": 0,
        "regeneration": 0,
        "thorn_armor": 0,
        "critical_mastery": 0,
        "giant_hunter": 0,
        "wave_clearing_bounty": 0,
        "compound_interest": 0,
        "golden_fortune": 0,
        "star_alchemy": 0,
        "wave_rush": 0,
        "range_grid": 0,
        "bulk_upgrade": 0,
        "elemental_focus": 0,
        "smart_targeting": 0,
        "astral_beacon": 0,
        "orbital_strike": 0,
        "cactus_drone": 0,
        "shatter_nova": 0,
        "void_amplifier": 0,
        "dark_alchemy": 0,
        "dark_aegis": 0,
        "gravity_well": 0,
        "void_infusion": 0,
        "event_horizon": 0,
        "quantum_harvester": 0,
        "dark_transcendence": 0,
        "farm_tower": 0,
        "farm_irrigation": 0,
        "greenhouse_unlock": 0,
        "botanical_expeditions": 0,
        "fertile_compost": 0,
        "sprout_harvest": 0,
        "flora_resonance": 0,
        "archaeology_unlock": 0,
        "dig_site_chance": 0,
        "dig_site_duration": 0,
        "dig_minigame_buff": 0,
        "relic_max_level": 0,
        "relic_double_drop": 0,
        "relic_pedestals": 0,
        "dark_relic_resonance": 0,
        "arcane_precision": 0,
        "frost_linger": 0,
        "rally_range": 0,
        "sun_tower": 0,
        "solar_power": 0,
        "solar_trail": 0,
        "prism_beams": 0,
        "beam_limit": 0,
        "bestiary_damage": 0,
        "bestiary_cacti": 0,
        "bestiary_stars": 0,
        "botanic_harvest": 0,
        "sonar_ping": 0,
        "dark_vitality": 0
    },
    "Toggles": {
        "wave_rush": True,
        "spawn_rush": True,
        "range_grid": False,
        "elemental_focus": True
    },
    "SelectedStartWave": 1,
    "Achievements": {},
    "CreditsSeen": False,
    "GameCompleted": False,
    "Settings": {
        "sfx_volume": 0.7,
        "music_volume": 0.5,
        "window_shake": True,
        "screen_shake": False,
        "damage_numbers": True,
        "auto_wave": False,
        "graphics_preset": "normal"
    },
    "Stats": {
        "total_towers_built": 0,
        "total_crits": 0,
        "total_kills": 0,
        "meteorites_destroyed": 0,
        "killed_golden": 0,
        "bosses_defeated": 0,
        "colossus_defeated": 0,
        "void_defeated": 0,
        "void_lord_defeated": 0,
        "max_tower_level_reached": 0,
        "max_tent_level": 0,
        "max_farms_built": 0,
        "tesla_built": 0,
        "max_session_cacti": 0,
        "relics_excavated": 0,
        "play_time_seconds": 0.0
    },
    "Greenhouse": {
        "saguaro": {"level": 0, "sprouts": 0},
        "opuntia": {"level": 0, "sprouts": 0},
        "fire_barrel": {"level": 0, "sprouts": 0},
        "frost_aloe": {"level": 0, "sprouts": 0},
        "thunder_echino": {"level": 0, "sprouts": 0},
        "void_astrophytum": {"level": 0, "sprouts": 0},
        "stellar_queen": {"level": 0, "sprouts": 0},
        "mammillaria": {"level": 0, "sprouts": 0}
    },
    "Relics": {},
    "difficulty": "normal",
    "difficulty_selected": False,
    "SaveId": "slot_main",
    "SaveName": "Основное сохранение",
    "CreatedAt": "",
    "UpdatedAt": ""
}

# -------------------------------------------------------------------------
# КОНФИГУРАЦИЯ СЛОЖНОСТЕЙ (DIFFICULTY SYSTEM)
# -------------------------------------------------------------------------
DIFFICULTY_CONFIG = {
    "casual": {
        "id": "casual",
        "name": "Казуальная",
        "badge": "[КАЗУАЛ]",
        "desc": "+10 HP базы, +200 старт. кактусов, башни -20% цены, скейлинг макс x3, мобы -25% HP, +25% зв./тёмн. кактусов, +50% шанс на +1 росток",
        "color": (90, 220, 130),
        "bg": (20, 55, 32),
        "border": (60, 180, 100)
    },
    "normal": {
        "id": "normal",
        "name": "Нормальная (Рекомендуется)",
        "badge": "[НОРМАЛЬНАЯ]",
        "desc": "Классический сбалансированный опыт Оазиса. Рекомендуется для всех игроков.",
        "color": (255, 220, 100),
        "bg": (22, 38, 58),
        "border": (90, 175, 255)
    },
    "hardcore": {
        "id": "hardcore",
        "name": "Хардкорная",
        "badge": "[ХАРДКОР]",
        "desc": "1/2 HP базы, у мобов и метеоритов x2 HP, все мета-улучшения в 2 раза дороже, 25% шанс потери ростка и реликвии.",
        "color": (255, 110, 120),
        "bg": (55, 20, 28),
        "border": (220, 65, 75)
    }
}

import sys
import zlib
import base64

if IS_ANDROID:
    try:
        from android.storage import app_storage_path
        SAVE_BASE_DIR = app_storage_path()
    except Exception:
        SAVE_BASE_DIR = os.environ.get("ANDROID_APP_DATA", os.environ.get("ANDROID_PRIVATE", "."))
elif getattr(sys, 'frozen', False):
    SAVE_BASE_DIR = os.path.dirname(sys.executable)
else:
    SAVE_BASE_DIR = BASE_DIR

SAVES_DIR = os.path.join(SAVE_BASE_DIR, "saves")
ACTIVE_PROFILE_FILE = os.path.join(SAVES_DIR, "active_profile.json")
LEGACY_SAVE_PATH = os.path.join(SAVE_BASE_DIR, "savedata.json")
SAVE_PATH = LEGACY_SAVE_PATH

SAVE_CIPHER_KEY = b"CactusTD_Remastered_Key_2026"

def format_play_time(total_seconds):
    """Форматирует секунды в читаемую строку времени (часы, минуты, секунды)."""
    total_seconds = int(total_seconds or 0)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if hours > 0:
        return f"{hours} ч. {minutes} мин."
    elif minutes > 0:
        return f"{minutes} мин. {secs} сек."
    else:
        return f"{secs} сек."

def xor_crypt(data: bytes, key: bytes) -> bytes:
    k_len = len(key)
    return bytes([b ^ key[i % k_len] for i, b in enumerate(data)])

def export_save_string(data: dict) -> str:
    """Шифрует данные сохранения (zlib + XOR + Base64 с префиксом CTD1_)."""
    try:
        raw_json = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        compressed = zlib.compress(raw_json, level=9)
        encrypted = xor_crypt(compressed, SAVE_CIPHER_KEY)
        b64 = base64.b64encode(encrypted).decode('ascii')
        return f"CTD1_{b64}"
    except Exception as e:
        print(f"Export error: {e}")
        return ""

def import_save_string(cipher_str: str) -> dict:
    """Расшифровывает строку сохранения (CTD1_... или JSON) и возвращает словарь данных."""
    if not cipher_str or not isinstance(cipher_str, str):
        raise ValueError("Строка сохранения пуста")
    cipher_str = cipher_str.strip()
    if cipher_str.startswith("CTD1_"):
        b64 = cipher_str[5:].strip()
        encrypted = base64.b64decode(b64.encode('ascii'))
        compressed = xor_crypt(encrypted, SAVE_CIPHER_KEY)
        raw_json = zlib.decompress(compressed)
        data = json.loads(raw_json.decode('utf-8'))
    elif cipher_str.startswith("{") and cipher_str.endswith("}"):
        data = json.loads(cipher_str)
    else:
        raise ValueError("Неверный формат ключа сохранения (требуется CTD1_...)")

    if not isinstance(data, dict):
        raise ValueError("Формат данных сохранения повреждён")
    return data

def read_save_file(filepath: str) -> dict:
    """Читает файл сохранения с диска, поддерживая как зашифрованный (CTD1_...), так и открытый JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    return import_save_string(content)

def write_save_file(filepath: str, data: dict):
    """Записывает данные сохранения на диск в зашифрованном виде (CTD1_...)."""
    cipher_str = export_save_string(data)
    dirpath = os.path.dirname(filepath)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(cipher_str)

def set_clipboard_text(text: str) -> bool:
    """Копирует строку в буфер обмена операционной системы (ПК + Android)."""
    # 1. Попытка через Android ClipboardManager (pyjnius)
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        ClipData = autoclass('android.content.ClipData')
        activity = PythonActivity.mActivity
        clipboard = activity.getSystemService(Context.CLIPBOARD_SERVICE)
        clip = ClipData.newPlainText("CactusTD Save", str(text))
        clipboard.setPrimaryClip(clip)
        return True
    except Exception:
        pass

    # 2. Попытка через pygame.scrap
    try:
        import pygame.scrap
        if not pygame.scrap.get_init():
            pygame.scrap.init()
        if hasattr(pygame.scrap, "put_text"):
            pygame.scrap.put_text(str(text))
            return True
        elif hasattr(pygame.scrap, "put"):
            import pygame
            pygame.scrap.put(pygame.SCRAP_TEXT, str(text).encode('utf-8'))
            return True
    except Exception as e:
        print(f"Clipboard put error: {e}")

    # 3. Fallback через tkinter (ПК)
    try:
        import tkinter as tk
        r = tk.Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(str(text))
        r.update()
        r.destroy()
        return True
    except Exception:
        pass

    return False

def get_clipboard_text() -> str:
    """Извлекает строку из буфера обмена операционной системы (ПК + Android)."""
    # 1. Попытка через Android ClipboardManager (pyjnius)
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        activity = PythonActivity.mActivity
        clipboard = activity.getSystemService(Context.CLIPBOARD_SERVICE)
        if clipboard.hasPrimaryClip():
            clip = clipboard.getPrimaryClip()
            if clip and clip.getItemCount() > 0:
                item = clip.getItemAt(0)
                text = item.getText()
                if text is not None:
                    return str(text.toString()).strip()
    except Exception:
        pass

    # 2. Попытка через pygame.scrap
    try:
        import pygame.scrap
        if not pygame.scrap.get_init():
            pygame.scrap.init()
        if hasattr(pygame.scrap, "get_text"):
            res = pygame.scrap.get_text()
            if res:
                return res.strip()
        elif hasattr(pygame.scrap, "get"):
            import pygame
            raw = pygame.scrap.get(pygame.SCRAP_TEXT)
            if raw:
                return raw.decode('utf-8', errors='ignore').rstrip('\x00').strip()
    except Exception as e:
        print(f"Clipboard get error: {e}")

    # 3. Fallback через tkinter (ПК)
    try:
        import tkinter as tk
        r = tk.Tk()
        r.withdraw()
        res = r.clipboard_get()
        r.destroy()
        if res:
            return str(res).strip()
    except Exception:
        pass

    return ""

def is_map_unlocked(mid, sdata):
    records = sdata.get("LevelsRecords", [0] * len(MAP_NAMES_LIST))
    rec = records[mid] if mid < len(records) else 0
    if mid == 0 or rec > 0:
        return True, ""
    if mid == 9:
        rec_8 = records[8] if len(records) > 8 else 0
        if sdata.get("GameCompleted", False) or sdata.get("CreditsSeen", False) or rec_8 >= 100:
            return True, ""
        req_name = MAP_BIOMES_DATA[8]["name"]
        return False, f"100 волна на '{req_name}' (сейчас: {rec_8})"
    req = MAP_UNLOCK_REQS.get(mid)
    if not req:
        return True, ""
    req_map, req_wave = req
    req_rec = records[req_map] if req_map < len(records) else 0
    if req_rec >= req_wave:
        return True, ""
    req_name = MAP_BIOMES_DATA[req_map]["name"]
    return False, f"{req_wave} волна на '{req_name}' (сейчас: {req_rec})"

def get_map_mastery_stars(mid, sdata):
    records = sdata.get("LevelsRecords", [0] * len(MAP_NAMES_LIST))
    rec = records[mid] if mid < len(records) else 0
    return [rec >= mw for mw, _, _ in get_map_mastery_milestones(mid)]

def check_mastery_rewards(mid, wave, sdata):
    claimed = sdata.setdefault("MasteryClaimed", {})
    awarded = []
    for mw, rew, rank in get_map_mastery_milestones(mid):
        key = f"{mid}_{mw}"
        if wave >= mw and not claimed.get(key, False):
            claimed[key] = True
            sdata["StellarCactuses"] = sdata.get("StellarCactuses", 0) + rew
            awarded.append((mw, rew, rank))
    if awarded:
        save_data(sdata)
    return awarded

def check_retroactive_mastery(sdata):
    claimed = sdata.setdefault("MasteryClaimed", {})
    records = sdata.get("LevelsRecords", [0] * len(MAP_NAMES_LIST))
    awarded_any = False

    for mid, rec in enumerate(records):
        for mw, rew, rank in get_map_mastery_milestones(mid):
            key = f"{mid}_{mw}"
            if rec >= mw and not claimed.get(key, False):
                claimed[key] = True
                sdata["StellarCactuses"] = sdata.get("StellarCactuses", 0) + rew
                awarded_any = True
    if awarded_any:
        save_data(sdata)

def get_all_save_slot_files():
    """Возвращает список файлов слотов сохранений, исключая служебные файлы."""
    if not os.path.exists(SAVES_DIR):
        return []
    ignored = {"active_profile.json", "global_achievements.json", "global_achievements.ctd"}
    return [
        f for f in os.listdir(SAVES_DIR)
        if f.endswith(".json") and f not in ignored and not f.startswith("global_") and not f.startswith("active_") and not f.startswith("export_")
    ]

def _init_saves_system():
    os.makedirs(SAVES_DIR, exist_ok=True)
    active_id = None
    if os.path.exists(ACTIVE_PROFILE_FILE):
        try:
            with open(ACTIVE_PROFILE_FILE, 'r', encoding='utf-8') as f:
                pinfo = json.load(f)
                active_id = pinfo.get("active_id")
        except Exception:
            active_id = None

    slot_files = get_all_save_slot_files()

    if not slot_files:
        if os.path.exists(LEGACY_SAVE_PATH):
            try:
                data = read_save_file(LEGACY_SAVE_PATH)
            except Exception:
                data = json.loads(json.dumps(DEFAULT_SAVE))
        else:
            data = json.loads(json.dumps(DEFAULT_SAVE))

        data.setdefault("SaveId", "slot_main")
        data.setdefault("SaveName", "Основное сохранение")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        data.setdefault("CreatedAt", now_str)
        data["UpdatedAt"] = now_str

        main_slot_path = os.path.join(SAVES_DIR, "slot_main.json")
        try:
            write_save_file(main_slot_path, data)
        except Exception as e:
            print(f"Error initializing slot_main: {e}")
        active_id = "slot_main"
    elif not active_id or not os.path.exists(os.path.join(SAVES_DIR, f"{active_id}.json")):
        active_id = slot_files[0][:-5]

    set_active_save_id(active_id)
    return active_id

def get_active_save_id():
    if os.path.exists(ACTIVE_PROFILE_FILE):
        try:
            with open(ACTIVE_PROFILE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f).get("active_id", "slot_main")
        except Exception:
            pass
    return "slot_main"

def set_active_save_id(save_id):
    os.makedirs(SAVES_DIR, exist_ok=True)
    try:
        with open(ACTIVE_PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump({"active_id": save_id}, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error setting active save ID: {e}")

def get_save_slot_path(save_id=None):
    if not save_id:
        save_id = get_active_save_id()
    return os.path.join(SAVES_DIR, f"{save_id}.json")

def list_save_profiles():
    _init_saves_system()
    active_id = get_active_save_id()
    profiles = []
    slot_files = get_all_save_slot_files()
    for fname in slot_files:
        sid = fname[:-5]
        fpath = os.path.join(SAVES_DIR, fname)
        try:
            data = read_save_file(fpath)
            records = data.get("LevelsRecords", [])
            max_wave = max(records) if records else 0
            gh = data.get("Greenhouse", {})
            gh_unlocked = sum(1 for v in gh.values() if isinstance(v, dict) and v.get("level", 0) > 0)
            gh_total_lvl = sum(v.get("level", 0) for v in gh.values() if isinstance(v, dict))

            relics_dict = data.get("Relics", {})
            relics_unlocked = sum(1 for v in relics_dict.values() if (v.get("level", 0) if isinstance(v, dict) else v) > 0)
            relics_total_lvl = sum((v.get("level", 0) if isinstance(v, dict) else v) for v in relics_dict.values())
            relics_max = len(globals().get("RELICS_DATA", {})) if globals().get("RELICS_DATA") else 20

            upgrades_dict = data.get("Upgrades", {})
            tree_nodes = globals().get("UPGRADE_TREE_NODES", {})
            if tree_nodes:
                bought_nodes = sum(1 for nid in tree_nodes if upgrades_dict.get(nid, 0) > 0)
                bought_upgrades = sum(min(tree_nodes[nid].get("max_lvl", 1), upgrades_dict.get(nid, 0)) for nid in tree_nodes)
                total_nodes = len(tree_nodes)
                total_upgrades = sum(n.get("max_lvl", 1) for n in tree_nodes.values())
            else:
                bought_nodes = sum(1 for v in upgrades_dict.values() if isinstance(v, (int, float)) and v > 0)
                bought_upgrades = sum(v for v in upgrades_dict.values() if isinstance(v, (int, float)) and v > 0)
                total_nodes = 63
                total_upgrades = 235

            profiles.append({
                "id": sid,
                "name": data.get("SaveName", sid),
                "difficulty": data.get("difficulty", "normal"),
                "created_at": data.get("CreatedAt", "-"),
                "updated_at": data.get("UpdatedAt", "-"),
                "is_active": (sid == active_id),
                "stars": data.get("StellarCactuses", 0),
                "dark": data.get("DarkCactuses", 0),
                "max_wave": max_wave,
                "greenhouse_count": gh_unlocked,
                "greenhouse_total_lvl": gh_total_lvl,
                "relics_count": relics_unlocked,
                "relics_max_count": relics_max,
                "relics_total_lvl": relics_total_lvl,
                "bought_nodes": bought_nodes,
                "bought_upgrades": bought_upgrades,
                "total_nodes": total_nodes,
                "total_upgrades": total_upgrades,
                "play_time": data.get("Stats", {}).get("play_time_seconds", 0.0),
                "game_completed": data.get("GameCompleted", False)
            })
        except Exception as e:
            print(f"Error reading profile {fname}: {e}")
    profiles.sort(key=lambda p: (0 if p["is_active"] else 1, p["updated_at"]), reverse=False)
    return profiles

def create_save_profile(name=None, make_active=True, difficulty="normal"):
    _init_saves_system()
    sid = f"slot_{int(time.time())}_{random.randint(100, 999)}"
    new_data = json.loads(json.dumps(DEFAULT_SAVE))
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_data["SaveId"] = sid
    new_data["SaveName"] = name.strip() if (name and name.strip()) else f"Слот #{len(list_save_profiles()) + 1}"
    new_data["CreatedAt"] = now_str
    new_data["UpdatedAt"] = now_str
    new_data["difficulty"] = difficulty
    new_data["difficulty_selected"] = True

    slot_path = os.path.join(SAVES_DIR, f"{sid}.json")
    try:
        write_save_file(slot_path, new_data)
    except Exception as e:
        print(f"Error creating save profile: {e}")

    if make_active:
        set_active_save_id(sid)
        save_data(new_data)
    return sid, new_data

def rename_save_profile(save_id, new_name):
    slot_path = os.path.join(SAVES_DIR, f"{save_id}.json")
    if not os.path.exists(slot_path):
        return False
    try:
        data = read_save_file(slot_path)
        data["SaveName"] = new_name.strip() if (new_name and new_name.strip()) else "Без названия"
        data["UpdatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        write_save_file(slot_path, data)
        if save_id == get_active_save_id():
            savedata["SaveName"] = data["SaveName"]
            save_data(savedata)
        return True
    except Exception as e:
        print(f"Error renaming profile: {e}")
        return False

def duplicate_save_profile(save_id):
    slot_path = os.path.join(SAVES_DIR, f"{save_id}.json")
    if not os.path.exists(slot_path):
        return None
    try:
        data = read_save_file(slot_path)
        new_sid = f"slot_{int(time.time())}_{random.randint(100, 999)}"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        data["SaveId"] = new_sid
        data["SaveName"] = f"{data.get('SaveName', 'Сохранение')} (Копия)"
        data["CreatedAt"] = now_str
        data["UpdatedAt"] = now_str
        new_slot_path = os.path.join(SAVES_DIR, f"{new_sid}.json")
        write_save_file(new_slot_path, data)
        return new_sid
    except Exception as e:
        print(f"Error duplicating profile: {e}")
        return None

def export_save_profile(save_id=None):
    """Экспортирует профиль сохранения в зашифрованную строку CTD1_... и в файл."""
    if not save_id:
        save_id = get_active_save_id()
    slot_path = os.path.join(SAVES_DIR, f"{save_id}.json")
    data = None
    if os.path.exists(slot_path):
        try:
            data = read_save_file(slot_path)
        except Exception:
            pass
    if data is None:
        data = load_data(save_id)

    cipher_str = export_save_string(data)
    out_file = os.path.join(SAVES_DIR, f"export_{save_id}.cactussave")
    try:
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(cipher_str)
    except Exception as e:
        print(f"Error writing export file: {e}")
    return cipher_str, out_file

def import_save_profile(cipher_or_json_str, as_new_slot=True, make_active=True):
    """Импортирует зашифрованную строку CTD1_... или JSON в профиль сохранения."""
    _init_saves_system()
    data = import_save_string(cipher_or_json_str)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    if as_new_slot:
        sid = f"slot_{int(time.time())}_{random.randint(100, 999)}"
        data["SaveId"] = sid
        old_name = data.get("SaveName", "Сохранение")
        data["SaveName"] = f"[Импорт] {old_name}"
        data["CreatedAt"] = now_str
    else:
        sid = get_active_save_id()
        data["SaveId"] = sid

    data["UpdatedAt"] = now_str

    slot_path = os.path.join(SAVES_DIR, f"{sid}.json")
    write_save_file(slot_path, data)

    if make_active:
        set_active_save_id(sid)
        save_data(data)
    return sid, data

def delete_save_profile(save_id):
    slot_path = os.path.join(SAVES_DIR, f"{save_id}.json")
    if os.path.exists(slot_path):
        try:
            os.remove(slot_path)
        except Exception as e:
            print(f"Error deleting profile {save_id}: {e}")

    active_id = get_active_save_id()
    if save_id == active_id:
        slot_files = get_all_save_slot_files()
        if slot_files:
            new_active = slot_files[0][:-5]
            set_active_save_id(new_active)
            new_data = load_data(new_active)
            save_data(new_data)
            return new_data
        else:
            _, new_data = create_save_profile("Основное сохранение", make_active=True)
            return new_data
    return None

def switch_active_save(save_id):
    set_active_save_id(save_id)
    new_data = load_data(save_id)
    save_data(new_data)
    return new_data

def load_data(save_id=None):
    _init_saves_system()
    if not save_id:
        save_id = get_active_save_id()
    slot_path = os.path.join(SAVES_DIR, f"{save_id}.json")
    if not os.path.exists(slot_path):
        slot_path = LEGACY_SAVE_PATH
    if not os.path.exists(slot_path):
        d = json.loads(json.dumps(DEFAULT_SAVE))
        d["SaveId"] = save_id
        return d
    try:
        data = read_save_file(slot_path)
        if "SaveId" not in data:
            data["SaveId"] = save_id
        if "SaveName" not in data:
            data["SaveName"] = "Основное сохранение"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        if "CreatedAt" not in data:
            data["CreatedAt"] = now_str
        if "UpdatedAt" not in data:
            data["UpdatedAt"] = now_str
        if "PlayerName" not in data:
            data["PlayerName"] = "Игрок"
        if "LevelsRecords" not in data or len(data["LevelsRecords"]) < len(MAP_NAMES_LIST):
            old_recs = data.get("LevelsRecords", [])
            data["LevelsRecords"] = old_recs + [0] * (len(MAP_NAMES_LIST) - len(old_recs))
        if "StellarCactuses" not in data:
            data["StellarCactuses"] = 15
            data["StarterStellarBonus"] = True
        elif not data.get("StarterStellarBonus", False):
            data["StarterStellarBonus"] = True
            data["StellarCactuses"] = data.get("StellarCactuses", 0) + 15
        if "DarkCactuses" not in data:
            data["DarkCactuses"] = 0
        if "MasteryClaimed" not in data:
            data["MasteryClaimed"] = {}
        if "BestiaryDiscovered" not in data:
            data["BestiaryDiscovered"] = []
        # Автоматическое открытие 4-го босса (4000), если игрок уже достигал 100-й волны или побеждал его
        if (max(data.get("LevelsRecords", [0]) or [0]) >= 100 or int(data.get("BestiaryKills", {}).get("4000", 0)) > 0) and 4000 not in data["BestiaryDiscovered"]:
            data["BestiaryDiscovered"].append(4000)
        if "BestiaryClaimed" not in data:
            data["BestiaryClaimed"] = {}
        if "BestiaryKills" not in data:
            data["BestiaryKills"] = {}
        if "FlawlessWaveStreak" not in data:
            data["FlawlessWaveStreak"] = 0
        if "Upgrades" not in data:
            data["Upgrades"] = dict(DEFAULT_SAVE["Upgrades"])
        else:
            for k, v in DEFAULT_SAVE["Upgrades"].items():
                if k not in data["Upgrades"]:
                    data["Upgrades"][k] = v
        data["Upgrades"]["oasis_core"] = max(1, data["Upgrades"].get("oasis_core", 1))
        data["Upgrades"]["magic_tower"] = max(1, data["Upgrades"].get("magic_tower", 1))
        if data["Upgrades"].get("rock_tower", 0) == 0 and data["Upgrades"].get("inferno_mastery", 0) > 0:
            data["Upgrades"]["rock_tower"] = 1
        if "Toggles" not in data:
            data["Toggles"] = dict(DEFAULT_SAVE.get("Toggles", {}))
        else:
            for tk, tv in DEFAULT_SAVE.get("Toggles", {}).items():
                if tk not in data["Toggles"]:
                    data["Toggles"][tk] = tv
        if "SelectedStartWave" not in data:
            data["SelectedStartWave"] = 1
        if "Achievements" not in data:
            data["Achievements"] = {}
        else:
            for old_k in ["first_blood", "critical_strike", "gold_rush"]:
                if old_k in data["Achievements"]:
                    del data["Achievements"][old_k]
        if "Stats" not in data:
            data["Stats"] = dict(DEFAULT_SAVE["Stats"])
        else:
            for sk, sv in DEFAULT_SAVE["Stats"].items():
                if sk not in data["Stats"]:
                    data["Stats"][sk] = sv
        if "Settings" not in data:
            data["Settings"] = dict(DEFAULT_SAVE["Settings"])
        else:
            for sk, sv in DEFAULT_SAVE["Settings"].items():
                if sk not in data["Settings"]:
                    data["Settings"][sk] = sv
        if "CreditsSeen" not in data:
            data["CreditsSeen"] = False
        if "GameCompleted" not in data:
            data["GameCompleted"] = False
        if "Greenhouse" not in data:
            data["Greenhouse"] = dict(DEFAULT_SAVE["Greenhouse"])
        else:
            for gk, gv in DEFAULT_SAVE["Greenhouse"].items():
                if gk not in data["Greenhouse"]:
                    data["Greenhouse"][gk] = dict(gv)
        if "CustomMapConfig" not in data:
            data["CustomMapConfig"] = dict(DEFAULT_SAVE["CustomMapConfig"])
        else:
            for ck, cv in DEFAULT_SAVE["CustomMapConfig"].items():
                if ck not in data["CustomMapConfig"]:
                    data["CustomMapConfig"][ck] = cv
        if "LevelsRecords" not in data or not isinstance(data["LevelsRecords"], list):
            data["LevelsRecords"] = [0] * len(MAP_NAMES_LIST)
        while len(data["LevelsRecords"]) < len(MAP_NAMES_LIST):
            data["LevelsRecords"].append(0)
        if "Relics" not in data or not isinstance(data["Relics"], dict):
            data["Relics"] = {}
        if "difficulty" not in data:
            data["difficulty"] = "normal"
        if "difficulty_selected" not in data:
            has_prog = any(r > 0 for r in data.get("LevelsRecords", [])) or data.get("Stats", {}).get("total_kills", 0) > 0
            data["difficulty_selected"] = True if has_prog else False
        check_retroactive_mastery(data)

        # Очистка локального сейва от глобальных ачивок (глобальные хранятся отдельно)
        ach_dict = data.setdefault("Achievements", {})
        for gid in ["global_wave_25", "global_wave_50", "global_wave_100", "global_hardcore_50", "global_all_relics", "global_botanist", "global_talent_master", "global_stellar_millionaire", "global_boss_slayer", "global_ultimate_tower"]:
            ach_dict.pop(gid, None)

        return data
    except Exception as e:
        print(f"Failed to load save: {e}. Using default.")
        d = json.loads(json.dumps(DEFAULT_SAVE))
        d["SaveId"] = save_id
        return d

GLOBAL_ACHIEVEMENTS_PATH = os.path.join(SAVES_DIR, "global_achievements.json")

def load_global_achievements():
    """Загружает глобальные достижения, разделяемые между всеми сейвами."""
    if os.path.exists(GLOBAL_ACHIEVEMENTS_PATH):
        try:
            return read_save_file(GLOBAL_ACHIEVEMENTS_PATH)
        except Exception as e:
            print(f"Error loading global achievements: {e}")
    return {}

def save_global_achievements(global_data):
    """Сохраняет глобальные достижения в saves/global_achievements.json в зашифрованном формате CTD."""
    try:
        os.makedirs(SAVES_DIR, exist_ok=True)
        write_save_file(GLOBAL_ACHIEVEMENTS_PATH, global_data)
    except Exception as e:
        print(f"Error saving global achievements: {e}")

def save_data(data):
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        data["UpdatedAt"] = now_str
        save_id = data.get("SaveId") or get_active_save_id()
        slot_path = os.path.join(SAVES_DIR, f"{save_id}.json")
        write_save_file(slot_path, data)
        write_save_file(LEGACY_SAVE_PATH, data)
        update_global_achievements(data)
    except Exception as e:
        print(f"Save error: {e}")

savedata = load_data()

# -------------------------------------------------------------------------
# ДРЕВО ТАЛАНТОВ
# -------------------------------------------------------------------------
UPGRADE_TREE_NODES = get_all_81_nodes()


def check_node_requirements(node_id, savedata):
    node = UPGRADE_TREE_NODES.get(node_id)
    if not node:
        return False, []
    reqs = node.get("requires", {})
    meta_reqs = node.get("meta_requires", {})
    if not reqs and not meta_reqs and not node.get("gameplay_req"):
        return True, []

    upgrades = savedata.get("Upgrades", {})
    all_met = True
    details = []

    # 1. Прямые зависимости по линиям древа
    for parent_id, req_val in reqs.items():
        parent_node = UPGRADE_TREE_NODES.get(parent_id)
        if not parent_node:
            continue
        parent_title = parent_node["title"]
        cur_lvl = upgrades.get(parent_id, 0)
        max_lvl = parent_node["max_lvl"]

        if req_val == "max":
            met = (cur_lvl >= max_lvl)
            details.append({
                "parent_id": parent_id,
                "title": parent_title,
                "req_str": f"{parent_title} (МАКС: {max_lvl} ур.)",
                "cur_lvl": cur_lvl,
                "max_lvl": max_lvl,
                "met": met,
                "is_meta": False
            })
        else:
            met = (cur_lvl >= req_val)
            details.append({
                "parent_id": parent_id,
                "title": parent_title,
                "req_str": f"{parent_title} ур. {req_val}",
                "cur_lvl": cur_lvl,
                "max_lvl": max_lvl,
                "met": met,
                "is_meta": False
            })
        if not met:
            all_met = False

    # 2. Мета-зависимости (без длинных линий, с быстрым переходом по клику)
    for parent_id, req_val in meta_reqs.items():
        parent_node = UPGRADE_TREE_NODES.get(parent_id)
        if not parent_node:
            continue
        parent_title = parent_node["title"]
        cur_lvl = upgrades.get(parent_id, 0)
        max_lvl = parent_node["max_lvl"]

        if req_val == "max":
            met = (cur_lvl >= max_lvl)
            details.append({
                "parent_id": parent_id,
                "title": parent_title,
                "req_str": f"{parent_title} (МАКС: {max_lvl} ур.)",
                "cur_lvl": cur_lvl,
                "max_lvl": max_lvl,
                "met": met,
                "is_meta": True
            })
        else:
            met = (cur_lvl >= req_val)
            details.append({
                "parent_id": parent_id,
                "title": parent_title,
                "req_str": f"{parent_title} ур. {req_val}",
                "cur_lvl": cur_lvl,
                "max_lvl": max_lvl,
                "met": met,
                "is_meta": True
            })
        if not met:
            all_met = False

    # 3. Особые игровые условия (прохождение волн, боссы, бестиарий, сбор кактусов)
    g_req = node.get("gameplay_req")
    if g_req:
        g_type = g_req.get("type")
        g_val = g_req.get("value", 1)
        g_desc = g_req.get("desc", "Игровое условие")
        met = False
        cur_val = 0

        if g_type == "wave":
            records = savedata.get("LevelsRecords", [0])
            cur_val = max(records) if records else 0
            met = (cur_val >= g_val)
        elif g_type == "map_wave":
            m_id = g_req.get("map_id", 0)
            records = savedata.get("LevelsRecords", [0])
            cur_val = records[m_id] if m_id < len(records) else 0
            met = (cur_val >= g_val)
        elif g_type == "bosses":
            cur_val = max(
                savedata.get("Stats", {}).get("bosses_defeated", 0),
                sum(w // 25 for w in savedata.get("LevelsRecords", []))
            )
            met = (cur_val >= g_val)
        elif g_type == "bestiary":
            cur_val = len(savedata.get("BestiaryDiscovered", []))
            met = (cur_val >= g_val)
        elif g_type in ("stars", "stars_scaling"):
            base_val = g_req.get("base", g_val)
            per_lvl = g_req.get("per_lvl", 0)
            cur_node_lvl = upgrades.get(node_id, 0)
            target_val = base_val + cur_node_lvl * per_lvl
            total_earned = max(
                savedata.get("Stats", {}).get("total_stellar_earned", 0),
                savedata.get("StellarCactuses", 0) + sum(upgrades.values())
            )
            cur_val = total_earned
            met = (cur_val >= target_val)
            g_val = target_val
            if per_lvl > 0:
                g_desc = f"Накопить от {target_val} Зв. кактусов (+{per_lvl} за лвл)"

        details.append({
            "parent_id": None,
            "title": g_desc,
            "req_str": g_desc,
            "cur_lvl": cur_val,
            "max_lvl": g_val,
            "met": met,
            "is_meta": False,
            "is_gameplay": True
        })
        if not met:
            all_met = False

    return all_met, details

def get_upgrade_node_cost(node_id, current_level, savedata=None):
    """Возвращает (stellar_cost, dark_cost, max_lvl) для заданного узла древа."""
    node = UPGRADE_TREE_NODES.get(node_id)
    if not node:
        return None, 0, 0
    max_lvl = node["max_lvl"]
    if current_level >= max_lvl:
        return None, 0, max_lvl

    costs = node.get("costs", [0])
    stellar_cost = costs[current_level] if current_level < len(costs) else costs[-1]

    dark_costs = node.get("dark_costs", [])
    if dark_costs:
        dark_cost = dark_costs[current_level] if current_level < len(dark_costs) else dark_costs[-1]
    elif node.get("currency") == "dark":
        dark_cost = stellar_cost
        stellar_cost = 0
    else:
        dark_cost = 0

    sdata = savedata if isinstance(savedata, dict) else globals().get("savedata", None)
    if sdata and isinstance(sdata, dict) and sdata.get("difficulty") == "hardcore":
        if stellar_cost:
            stellar_cost *= 2
        if dark_cost:
            dark_cost *= 2

    return stellar_cost, dark_cost, max_lvl

def get_upgrade_price(upgrade_id, current_level, savedata=None):
    cost, dark_cost, max_lvl = get_upgrade_node_cost(upgrade_id, current_level, savedata=savedata)
    return cost, max_lvl

# (Устаревший дубликат RELICS_DATA удален, актуальная система реликвий и пьедесталов находится ниже)

# -------------------------------------------------------------------------
# СИСТЕМА ДОСТИЖЕНИЙ
# -------------------------------------------------------------------------
ACHIEVEMENTS_DATA = [
    # -------------------------------------------------------------------------
    # 1. БОЙ И БОССЫ (COMBAT & BOSSES)
    # -------------------------------------------------------------------------
    {
        "id": "first_slime_click",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Тык!",
        "desc": "Кликните по любому слайму на карте",
        "reward": 1,
        "icon": mob1_img,
        "check": lambda s: s.get("Stats", {}).get("slime_clicks", 0) >= 1,
        "progress": lambda s: (min(1, s.get("Stats", {}).get("slime_clicks", 0)), 1)
    },
    {
        "id": "hundred_slime_clicks",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Пальцевый Пулемёт",
        "desc": "Кликните по слаймам 100 раз",
        "reward": 4,
        "icon": mob2_img,
        "check": lambda s: s.get("Stats", {}).get("slime_clicks", 0) >= 100,
        "progress": lambda s: (min(100, s.get("Stats", {}).get("slime_clicks", 0)), 100)
    },
    {
        "id": "slimes_100",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Первый Разгром",
        "desc": "Уничтожьте 100 слаймов",
        "reward": 2,
        "icon": mob1_img,
        "check": lambda s: s.get("Stats", {}).get("total_kills", 0) >= 100 or sum(s.get("LevelsRecords", [])) >= 5,
        "progress": lambda s: (min(100, max(s.get("Stats", {}).get("total_kills", 0), sum(s.get("LevelsRecords", [])) * 20)), 100)
    },
    {
        "id": "thousand_slimes",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Слаймовый Косильщик",
        "desc": "Уничтожьте 1,000 слаймов",
        "reward": 4,
        "icon": mob2_img,
        "check": lambda s: s.get("Stats", {}).get("total_kills", 0) >= 1000 or sum(s.get("LevelsRecords", [])) >= 40,
        "progress": lambda s: (min(1000, max(s.get("Stats", {}).get("total_kills", 0), sum(s.get("LevelsRecords", [])) * 25)), 1000)
    },
    {
        "id": "ten_thousand_slimes",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Гроза Слизепада",
        "desc": "Уничтожьте 5,000 слаймов",
        "reward": 8,
        "icon": mob3_img,
        "check": lambda s: s.get("Stats", {}).get("total_kills", 0) >= 5000 or sum(s.get("LevelsRecords", [])) >= 150,
        "progress": lambda s: (min(5000, max(s.get("Stats", {}).get("total_kills", 0), sum(s.get("LevelsRecords", [])) * 30)), 5000)
    },
    {
        "id": "twenty_five_thousand",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Легендарный Истребитель",
        "desc": "Уничтожьте 15,000 слаймов",
        "reward": 15,
        "icon": crown_upg_icon,
        "check": lambda s: s.get("Stats", {}).get("total_kills", 0) >= 15000 or sum(s.get("LevelsRecords", [])) >= 400,
        "progress": lambda s: (min(15000, max(s.get("Stats", {}).get("total_kills", 0), sum(s.get("LevelsRecords", [])) * 35)), 15000)
    },
    {
        "id": "ice_crit",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Холодный Расчёт",
        "desc": "Совершите 100 критических ударов",
        "reward": 2,
        "icon": sword_icon,
        "check": lambda s: s.get("Stats", {}).get("total_crits", 0) >= 100,
        "progress": lambda s: (min(100, s.get("Stats", {}).get("total_crits", 0)), 100)
    },
    {
        "id": "critical_master",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Мастер Критов",
        "desc": "Совершите 2,500 критических ударов",
        "reward": 4,
        "icon": damage_upg_icon,
        "check": lambda s: s.get("Stats", {}).get("total_crits", 0) >= 2500,
        "progress": lambda s: (min(2500, s.get("Stats", {}).get("total_crits", 0)), 2500)
    },
    {
        "id": "lethal_precision",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Смертоносная Точность",
        "desc": "Совершите 10,000 критических ударов",
        "reward": 8,
        "icon": crown_upg_icon,
        "check": lambda s: s.get("Stats", {}).get("total_crits", 0) >= 10000,
        "progress": lambda s: (min(10000, s.get("Stats", {}).get("total_crits", 0)), 10000)
    },
    {
        "id": "gold_hunter",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Золотая Лихорадка",
        "desc": "Уничтожьте 5 Золотых Слаймов",
        "reward": 3,
        "icon": gold_slime_img,
        "check": lambda s: s.get("Stats", {}).get("killed_golden", 0) >= 5,
        "progress": lambda s: (min(5, s.get("Stats", {}).get("killed_golden", 0)), 5)
    },
    {
        "id": "gold_slayer",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Золотой Жнец",
        "desc": "Уничтожьте 25 Золотых Слаймов",
        "reward": 6,
        "icon": bounty_upg_icon,
        "check": lambda s: s.get("Stats", {}).get("killed_golden", 0) >= 25,
        "progress": lambda s: (min(25, s.get("Stats", {}).get("killed_golden", 0)), 25)
    },
    {
        "id": "gold_magnate",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Золотой Клондайк",
        "desc": "Уничтожьте 60 Золотых Слаймов",
        "reward": 12,
        "icon": start_cacti_icon,
        "check": lambda s: s.get("Stats", {}).get("killed_golden", 0) >= 60,
        "progress": lambda s: (min(60, s.get("Stats", {}).get("killed_golden", 0)), 60)
    },
    {
        "id": "boss_slayer",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Первый Триумф",
        "desc": "Победите 1 босса (Царя-Слизня на 25-й волне)",
        "reward": 3,
        "icon": boss_img,
        "check": lambda s: s.get("Stats", {}).get("bosses_defeated", 0) >= 1 or any(w >= 25 for w in s.get("LevelsRecords", [])),
        "progress": lambda s: (min(1, max(s.get("Stats", {}).get("bosses_defeated", 0), 1 if any(w >= 25 for w in s.get("LevelsRecords", [])) else 0)), 1)
    },
    {
        "id": "boss_hunter",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Истребитель Боссов",
        "desc": "Победите суммарно 5 боссов",
        "reward": 5,
        "icon": boss_img,
        "check": lambda s: s.get("Stats", {}).get("bosses_defeated", 0) >= 5 or sum(w // 25 for w in s.get("LevelsRecords", [])) >= 5,
        "progress": lambda s: (min(5, max(s.get("Stats", {}).get("bosses_defeated", 0), sum(w // 25 for w in s.get("LevelsRecords", [])))), 5)
    },
    {
        "id": "boss_nemesis",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Гроза Боссов",
        "desc": "Победите суммарно 20 боссов",
        "reward": 9,
        "icon": crown_upg_icon,
        "check": lambda s: s.get("Stats", {}).get("bosses_defeated", 0) >= 20 or sum(w // 25 for w in s.get("LevelsRecords", [])) >= 20,
        "progress": lambda s: (min(20, max(s.get("Stats", {}).get("bosses_defeated", 0), sum(w // 25 for w in s.get("LevelsRecords", [])))), 20)
    },
    {
        "id": "boss_titan",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Владыка Арены",
        "desc": "Победите суммарно 40 боссов",
        "reward": 16,
        "icon": crown_upg_icon,
        "check": lambda s: s.get("Stats", {}).get("bosses_defeated", 0) >= 40 or sum(w // 25 for w in s.get("LevelsRecords", [])) >= 40,
        "progress": lambda s: (min(40, max(s.get("Stats", {}).get("bosses_defeated", 0), sum(w // 25 for w in s.get("LevelsRecords", [])))), 40)
    },
    {
        "id": "colossus_slayer",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Слизнебарон",
        "desc": "Одолейте Слизнебарона (босс 50-й волны)",
        "reward": 8,
        "icon": colossus_boss_img,
        "check": lambda s: s.get("Stats", {}).get("colossus_defeated", 0) >= 1 or any(w >= 50 for w in s.get("LevelsRecords", [])),
        "progress": lambda s: (1 if (s.get("Stats", {}).get("colossus_defeated", 0) >= 1 or any(w >= 50 for w in s.get("LevelsRecords", []))) else 0, 1)
    },
    {
        "id": "void_conqueror",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Теневой Исполин",
        "desc": "Одолейте Теневого Исполина (босс 75-й волны)",
        "reward": 12,
        "icon": void_boss_img,
        "check": lambda s: s.get("Stats", {}).get("void_defeated", 0) >= 1 or any(w >= 75 for w in s.get("LevelsRecords", [])),
        "progress": lambda s: (1 if (s.get("Stats", {}).get("void_defeated", 0) >= 1 or any(w >= 75 for w in s.get("LevelsRecords", []))) else 0, 1)
    },
    {
        "id": "void_lord_slayer",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Король Слаймов",
        "desc": "Раскатайте Короля Всех Слаймов (100-я волна)",
        "reward": 20,
        "icon": void_lord_boss_img,
        "check": lambda s: s.get("GameCompleted", False) or s.get("Stats", {}).get("void_lord_defeated", 0) >= 1 or any(w >= 100 for w in s.get("LevelsRecords", [])),
        "progress": lambda s: (1 if (s.get("GameCompleted", False) or s.get("Stats", {}).get("void_lord_defeated", 0) >= 1 or any(w >= 100 for w in s.get("LevelsRecords", []))) else 0, 1)
    },
    {
        "id": "meteor_hunter",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Звездопад",
        "desc": "Разбейте 1 Астральный Метеорит",
        "reward": 4,
        "icon": dark_cactus_img,
        "check": lambda s: s.get("Stats", {}).get("meteorites_destroyed", 0) >= 1 or s.get("DarkCactuses", 0) >= 1,
        "progress": lambda s: (min(1, max(s.get("Stats", {}).get("meteorites_destroyed", 0), 1 if s.get("DarkCactuses", 0) >= 1 else 0)), 1)
    },
    {
        "id": "meteor_crusher",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Космический Бурильщик",
        "desc": "Разбейте 5 Астральных Метеоритов",
        "reward": 10,
        "icon": dark_cactus_img,
        "check": lambda s: s.get("Stats", {}).get("meteorites_destroyed", 0) >= 5 or s.get("DarkCactuses", 0) >= 5,
        "progress": lambda s: (min(5, max(s.get("Stats", {}).get("meteorites_destroyed", 0), s.get("DarkCactuses", 0))), 5)
    },
    {
        "id": "bestiary_scholar",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Исследователь Слаймов",
        "desc": "Откройте 8 видов слаймов в Бестиарии",
        "reward": 4,
        "icon": trophy_icon,
        "check": lambda s: len(s.get("BestiaryDiscovered", [])) >= 8,
        "progress": lambda s: (min(8, len(s.get("BestiaryDiscovered", []))), 8)
    },
    {
        "id": "bestiary_master",
        "category": "combat",
        "cat_name": "Бой и Боссы",
        "title": "Полная Энциклопедия",
        "desc": "Откройте все 10 видов слаймов в Бестиарии",
        "reward": 8,
        "icon": crown_upg_icon,
        "check": lambda s: len(s.get("BestiaryDiscovered", [])) >= 10,
        "progress": lambda s: (min(10, len(s.get("BestiaryDiscovered", []))), 10)
    },

    # -------------------------------------------------------------------------
    # 2. БАШНИ И ЭКОНОМИКА (TOWERS & ECONOMY)
    # -------------------------------------------------------------------------
    {
        "id": "first_tower",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Первые Всходы",
        "desc": "Постройте первую защитную башню",
        "reward": 1,
        "icon": magic_tower_img,
        "check": lambda s: s.get("Stats", {}).get("total_towers_built", 0) >= 1,
        "progress": lambda s: (min(1, s.get("Stats", {}).get("total_towers_built", 0)), 1)
    },
    {
        "id": "architect",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Оазисный Архитектор",
        "desc": "Постройте суммарно 25 башен",
        "reward": 3,
        "icon": rock_tower_img,
        "check": lambda s: s.get("Stats", {}).get("total_towers_built", 0) >= 25,
        "progress": lambda s: (min(25, s.get("Stats", {}).get("total_towers_built", 0)), 25)
    },
    {
        "id": "grand_builder",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Великий Зодчий",
        "desc": "Постройте суммарно 100 башен",
        "reward": 6,
        "icon": start_lvl_icon,
        "check": lambda s: s.get("Stats", {}).get("total_towers_built", 0) >= 100,
        "progress": lambda s: (min(100, s.get("Stats", {}).get("total_towers_built", 0)), 100)
    },
    {
        "id": "tower_megapolis",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Кактусовый Мегаполис",
        "desc": "Постройте суммарно 250 башен за всё время",
        "reward": 12,
        "icon": crown_upg_icon,
        "check": lambda s: s.get("Stats", {}).get("total_towers_built", 0) >= 250,
        "progress": lambda s: (min(250, s.get("Stats", {}).get("total_towers_built", 0)), 250)
    },
    {
        "id": "high_level",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Вершина Мастерства",
        "desc": "Улучшите любую башню до 10 уровня",
        "reward": 3,
        "icon": magic_tower_img,
        "check": lambda s: s.get("Stats", {}).get("max_tower_level_reached", 0) >= 10,
        "progress": lambda s: (min(10, s.get("Stats", {}).get("max_tower_level_reached", 0)), 10)
    },
    {
        "id": "archmage",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Архимаг Оазиса",
        "desc": "Улучшите любую башню до 15 ур.",
        "reward": 4,
        "icon": magic_tower_img,
        "check": lambda s: s.get("Stats", {}).get("max_tower_level_reached", 0) >= 15,
        "progress": lambda s: (min(15, s.get("Stats", {}).get("max_tower_level_reached", 0)), 15)
    },
    {
        "id": "tower_ascension",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Абсолютная Мощь",
        "desc": "Улучшите башню до 25 уровня",
        "reward": 6,
        "icon": start_lvl_icon,
        "check": lambda s: s.get("Stats", {}).get("max_tower_level_reached", 0) >= 25,
        "progress": lambda s: (min(25, s.get("Stats", {}).get("max_tower_level_reached", 0)), 25)
    },
    {
        "id": "tower_zenith",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Зенит Эволюции",
        "desc": "Улучшите башню до 35 уровня",
        "reward": 10,
        "icon": crown_upg_icon,
        "check": lambda s: s.get("Stats", {}).get("max_tower_level_reached", 0) >= 35,
        "progress": lambda s: (min(35, s.get("Stats", {}).get("max_tower_level_reached", 0)), 35)
    },
    {
        "id": "tesla_master",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Повелитель Молний",
        "desc": "Постройте Башню Тесла в бою",
        "reward": 3,
        "icon": tesla_tower_img,
        "check": lambda s: s.get("Stats", {}).get("tesla_built", 0) >= 1,
        "progress": lambda s: (min(1, s.get("Stats", {}).get("tesla_built", 0)), 1)
    },
    {
        "id": "tesla_overload",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Грозовой Шторм",
        "desc": "Постройте 5 Башен Тесла за всё время",
        "reward": 5,
        "icon": tesla_tower_img,
        "check": lambda s: s.get("Stats", {}).get("tesla_built", 0) >= 5,
        "progress": lambda s: (min(5, s.get("Stats", {}).get("tesla_built", 0)), 5)
    },
    {
        "id": "barracks_master",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Казарменный Оплот",
        "desc": "Улучшите Палатку Воинов до 10 уровня",
        "reward": 4,
        "icon": tent_tower_img,
        "check": lambda s: s.get("Stats", {}).get("max_tent_level", 0) >= 10 or s.get("Stats", {}).get("max_tower_level_reached", 0) >= 10,
        "progress": lambda s: (min(10, max(s.get("Stats", {}).get("max_tent_level", 0), s.get("Stats", {}).get("max_tower_level_reached", 0))), 10)
    },
    {
        "id": "barracks_legion",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Несокрушимый Легион",
        "desc": "Улучшите Палатку Воинов до 20 уровня",
        "reward": 7,
        "icon": tent_tower_img,
        "check": lambda s: s.get("Stats", {}).get("max_tent_level", 0) >= 20 or s.get("Stats", {}).get("max_tower_level_reached", 0) >= 20,
        "progress": lambda s: (min(20, max(s.get("Stats", {}).get("max_tent_level", 0), s.get("Stats", {}).get("max_tower_level_reached", 0))), 20)
    },
    {
        "id": "farm_empire",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Агроном Оазиса",
        "desc": "Постройте Ферму Кактусов",
        "reward": 3,
        "icon": farm_tower_img,
        "check": lambda s: s.get("Stats", {}).get("max_farms_built", 0) >= 1,
        "progress": lambda s: (min(1, s.get("Stats", {}).get("max_farms_built", 0)), 1)
    },
    {
        "id": "farm_magnate",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Плантация Кактусов",
        "desc": "Постройте 3 фермы кактусов за время игры",
        "reward": 5,
        "icon": farm_tower_img,
        "check": lambda s: s.get("Stats", {}).get("max_farms_built", 0) >= 3,
        "progress": lambda s: (min(3, s.get("Stats", {}).get("max_farms_built", 0)), 3)
    },
    {
        "id": "tycoon",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Оазисный Магнат",
        "desc": "Накопите 5,000 кактусов за один бой",
        "reward": 3,
        "icon": bounty_upg_icon,
        "check": lambda s: s.get("Stats", {}).get("max_session_cacti", 0) >= 5000,
        "progress": lambda s: (min(5000, s.get("Stats", {}).get("max_session_cacti", 0)), 5000)
    },
    {
        "id": "millionaire",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Мультимиллионер",
        "desc": "Накопите 50,000 кактусов за один бой",
        "reward": 6,
        "icon": start_cacti_icon,
        "check": lambda s: s.get("Stats", {}).get("max_session_cacti", 0) >= 50000,
        "progress": lambda s: (min(50000, s.get("Stats", {}).get("max_session_cacti", 0)), 50000)
    },
    {
        "id": "billionaire",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Золотой Запас Оазиса",
        "desc": "Накопите 150,000 кактусов за один бой",
        "reward": 12,
        "icon": start_cacti_icon,
        "check": lambda s: s.get("Stats", {}).get("max_session_cacti", 0) >= 150000,
        "progress": lambda s: (min(150000, s.get("Stats", {}).get("max_session_cacti", 0)), 150000)
    },
    {
        "id": "stellar_treasury",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Звёздная Казна",
        "desc": "Накопите 50 Звёздных Кактусов",
        "reward": 5,
        "icon": stellar_cactus_img_s,
        "check": lambda s: s.get("StellarCactuses", 0) >= 50,
        "progress": lambda s: (min(50, s.get("StellarCactuses", 0)), 50)
    },
    {
        "id": "stellar_hoarder",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Сокровищница Небес",
        "desc": "Накопите 150 Звёздных Кактусов",
        "reward": 10,
        "icon": stellar_cactus_img_s,
        "check": lambda s: s.get("StellarCactuses", 0) >= 150,
        "progress": lambda s: (min(150, s.get("StellarCactuses", 0)), 150)
    },
    {
        "id": "dark_treasury",
        "category": "towers",
        "cat_name": "Башни и Экономика",
        "title": "Тёмный Резерв",
        "desc": "Соберите 5 Тёмных Кактусов",
        "reward": 8,
        "icon": dark_cactus_img,
        "check": lambda s: s.get("DarkCactuses", 0) >= 5 or s.get("Upgrades", {}).get("orbital_strike", 0) > 0,
        "progress": lambda s: (min(5, s.get("DarkCactuses", 0) + (3 if s.get("Upgrades", {}).get("orbital_strike", 0) > 0 else 0)), 5)
    },

    # -------------------------------------------------------------------------
    # 3. ОРАНЖЕРЕЯ И КАРТЫ (GREENHOUSE & MAPS)
    # -------------------------------------------------------------------------
    {
        "id": "greenhouse_opened",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Зелёный Дом",
        "desc": "Откройте Оранжерею Кактусов в Древе",
        "reward": 3,
        "icon": cactus_img,
        "check": lambda s: s.get("Upgrades", {}).get("greenhouse_unlock", 0) > 0,
        "progress": lambda s: (1 if s.get("Upgrades", {}).get("greenhouse_unlock", 0) > 0 else 0, 1)
    },
    {
        "id": "first_sprout",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Юный Садовод",
        "desc": "Соберите 3 саженца любых кактусов",
        "reward": 2,
        "icon": cactus_img,
        "check": lambda s: sum(c.get("sprouts", 0) + c.get("level", 0) for c in s.get("Greenhouse", {}).values()) >= 3,
        "progress": lambda s: (min(3, sum(c.get("sprouts", 0) + c.get("level", 0) for c in s.get("Greenhouse", {}).values())), 3)
    },
    {
        "id": "botanist_trio",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Ботаническое Трио",
        "desc": "Откройте 3 различных кактуса в Оранжерее",
        "reward": 4,
        "icon": cactus_img,
        "check": lambda s: sum(1 for c in s.get("Greenhouse", {}).values() if c.get("level", 0) > 0) >= 3,
        "progress": lambda s: (min(3, sum(1 for c in s.get("Greenhouse", {}).values() if c.get("level", 0) > 0)), 3)
    },
    {
        "id": "flora_collector",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Флорист Оазиса",
        "desc": "Откройте 5 различных кактусов в Оранжерее",
        "reward": 7,
        "icon": cactus_img,
        "check": lambda s: sum(1 for c in s.get("Greenhouse", {}).values() if c.get("level", 0) > 0) >= 5,
        "progress": lambda s: (min(5, sum(1 for c in s.get("Greenhouse", {}).values() if c.get("level", 0) > 0)), 5)
    },
    {
        "id": "greenhouse_master",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Великий Селекционер",
        "desc": "Откройте все 8 видов кактусов в Оранжерее",
        "reward": 15,
        "icon": crown_upg_icon,
        "check": lambda s: sum(1 for c in s.get("Greenhouse", {}).values() if c.get("level", 0) > 0) >= 8,
        "progress": lambda s: (min(8, sum(1 for c in s.get("Greenhouse", {}).values() if c.get("level", 0) > 0)), 8)
    },
    {
        "id": "cactus_cultivator",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Сила Селекции",
        "desc": "Прокачайте любой кактус в Оранжерее до 3 уровня",
        "reward": 5,
        "icon": cactus_img,
        "check": lambda s: any(c.get("level", 0) >= 3 for c in s.get("Greenhouse", {}).values()),
        "progress": lambda s: (min(3, max([c.get("level", 0) for c in s.get("Greenhouse", {}).values()] or [0])), 3)
    },
    {
        "id": "cactus_maximus",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Апогей Флоры",
        "desc": "Прокачайте любой кактус до максимального 5 уровня",
        "reward": 12,
        "icon": crown_upg_icon,
        "check": lambda s: any(c.get("level", 0) >= 5 for c in s.get("Greenhouse", {}).values()),
        "progress": lambda s: (min(5, max([c.get("level", 0) for c in s.get("Greenhouse", {}).values()] or [0])), 5)
    },
    {
        "id": "veteran",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Ветеран Обороны",
        "desc": "Достигните 25 волны на любой карте",
        "reward": 3,
        "icon": wave_upg_icon,
        "check": lambda s: any(r >= 25 for r in s.get("LevelsRecords", [])),
        "progress": lambda s: (min(25, max(s.get("LevelsRecords", [0]))), 25)
    },
    {
        "id": "wave_50",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Стойкий Защитник",
        "desc": "Преодолейте 50 волну на любой карте",
        "reward": 6,
        "icon": wave_upg_icon,
        "check": lambda s: any(r >= 50 for r in s.get("LevelsRecords", [])),
        "progress": lambda s: (min(50, max(s.get("LevelsRecords", [0]))), 50)
    },
    {
        "id": "wave_75",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Легенда Пустыни",
        "desc": "Преодолейте 75 волну на любой карте",
        "reward": 10,
        "icon": crown_upg_icon,
        "check": lambda s: any(r >= 75 for r in s.get("LevelsRecords", [])),
        "progress": lambda s: (min(75, max(s.get("LevelsRecords", [0]))), 75)
    },
    {
        "id": "wave_100",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Истинный Триумфатор",
        "desc": "Преодолейте 100 волну на любой карте",
        "reward": 15,
        "icon": crown_upg_icon,
        "check": lambda s: any(r >= 100 for r in s.get("LevelsRecords", [])),
        "progress": lambda s: (min(100, max(s.get("LevelsRecords", [0]))), 100)
    },
    {
        "id": "snow_survivor",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Полярный Страж",
        "desc": "Достигните 25 волны на карте Круговорот",
        "reward": 4,
        "icon": wave_upg_icon,
        "check": lambda s: len(s.get("LevelsRecords", [])) > 1 and s.get("LevelsRecords", [])[1] >= 25,
        "progress": lambda s: (min(25, s.get("LevelsRecords", [])[1] if len(s.get("LevelsRecords", [])) > 1 else 0), 25)
    },
    {
        "id": "sand_crossroad",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Владыка Песков",
        "desc": "Достигните 25 волны на карте Перекрёстки",
        "reward": 4,
        "icon": wave_upg_icon,
        "check": lambda s: len(s.get("LevelsRecords", [])) > 2 and s.get("LevelsRecords", [])[2] >= 25,
        "progress": lambda s: (min(25, s.get("LevelsRecords", [])[2] if len(s.get("LevelsRecords", [])) > 2 else 0), 25)
    },
    {
        "id": "magma_conqueror",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Покоритель Лавы",
        "desc": "Достигните 25 волны на карте Волны",
        "reward": 5,
        "icon": wave_upg_icon,
        "check": lambda s: len(s.get("LevelsRecords", [])) > 3 and s.get("LevelsRecords", [])[3] >= 25,
        "progress": lambda s: (min(25, s.get("LevelsRecords", [])[3] if len(s.get("LevelsRecords", [])) > 3 else 0), 25)
    },
    {
        "id": "space_traveler",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Космический Навигатор",
        "desc": "Достигните 25 волны на карте Змейка",
        "reward": 5,
        "icon": wave_upg_icon,
        "check": lambda s: len(s.get("LevelsRecords", [])) > 4 and s.get("LevelsRecords", [])[4] >= 25,
        "progress": lambda s: (min(25, s.get("LevelsRecords", [])[4] if len(s.get("LevelsRecords", [])) > 4 else 0), 25)
    },
    {
        "id": "abyss_final",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Спаситель Вселенной",
        "desc": "Одолейте 100 волну на финальной карте 9 («Разлом Бездны»)",
        "reward": 25,
        "icon": void_lord_boss_img,
        "check": lambda s: s.get("GameCompleted", False) or (len(s.get("LevelsRecords", [])) > 8 and s.get("LevelsRecords", [])[8] >= 100),
        "progress": lambda s: (1 if (s.get("GameCompleted", False) or (len(s.get("LevelsRecords", [])) > 8 and s.get("LevelsRecords", [])[8] >= 100)) else 0, 1)
    },
    {
        "id": "mastery_novice",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Первые Звёзды",
        "desc": "Соберите 5 звёзд мастерства на картах",
        "reward": 4,
        "icon": stellar_cactus_img_s,
        "check": lambda s: len(s.get("MasteryClaimed", {})) >= 5,
        "progress": lambda s: (min(5, len(s.get("MasteryClaimed", {}))), 5)
    },
    {
        "id": "mastery_champion",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Звёздный Чемпион",
        "desc": "Соберите 10 звёзд мастерства на картах",
        "reward": 7,
        "icon": stellar_cactus_img_s,
        "check": lambda s: len(s.get("MasteryClaimed", {})) >= 10,
        "progress": lambda s: (min(10, len(s.get("MasteryClaimed", {}))), 10)
    },
    {
        "id": "mastery_legend",
        "category": "greenhouse",
        "cat_name": "Оранжерея и Карты",
        "title": "Абсолютный Мастер",
        "desc": "Соберите 20 звёзд мастерства на картах",
        "reward": 15,
        "icon": crown_upg_icon,
        "check": lambda s: len(s.get("MasteryClaimed", {})) >= 20,
        "progress": lambda s: (min(20, len(s.get("MasteryClaimed", {}))), 20)
    },

    # -------------------------------------------------------------------------
    # 4. ДРЕВО ТАЛАНТОВ (TALENTS & SPECIALS)
    # -------------------------------------------------------------------------
    {
        "id": "first_talent",
        "category": "talents",
        "cat_name": "Таланты",
        "title": "Первая Искра",
        "desc": "Изучите 1 талант в Древе Прокачки",
        "reward": 1,
        "icon": start_lvl_icon,
        "check": lambda s: sum(1 for k, v in s.get("Upgrades", {}).items() if k != "oasis_core" and v > 0) >= 1,
        "progress": lambda s: (min(1, sum(1 for k, v in s.get("Upgrades", {}).items() if k != "oasis_core" and v > 0)), 1)
    },
    {
        "id": "talent_collector",
        "category": "talents",
        "cat_name": "Таланты",
        "title": "Учёный Оазиса",
        "desc": "Изучите 5 различных талантов в Древе",
        "reward": 2,
        "icon": cactus_img,
        "check": lambda s: sum(1 for k, v in s.get("Upgrades", {}).items() if k != "oasis_core" and v > 0) >= 5,
        "progress": lambda s: (min(5, sum(1 for k, v in s.get("Upgrades", {}).items() if k != "oasis_core" and v > 0)), 5)
    },
    {
        "id": "talent_master",
        "category": "talents",
        "cat_name": "Таланты",
        "title": "Магистр Знаний",
        "desc": "Изучите 15 различных талантов в Древе",
        "reward": 6,
        "icon": bounty_upg_icon,
        "check": lambda s: sum(1 for k, v in s.get("Upgrades", {}).items() if k != "oasis_core" and v > 0) >= 15,
        "progress": lambda s: (min(15, sum(1 for k, v in s.get("Upgrades", {}).items() if k != "oasis_core" and v > 0)), 15)
    },
    {
        "id": "talent_sage",
        "category": "talents",
        "cat_name": "Таланты",
        "title": "Мудрец Оазиса",
        "desc": "Изучите 25 талантов в Древе",
        "reward": 12,
        "icon": crown_upg_icon,
        "check": lambda s: sum(1 for k, v in s.get("Upgrades", {}).items() if k != "oasis_core" and v > 0) >= 25,
        "progress": lambda s: (min(25, sum(1 for k, v in s.get("Upgrades", {}).items() if k != "oasis_core" and v > 0)), 25)
    },
    {
        "id": "speed_demon",
        "category": "talents",
        "cat_name": "Таланты",
        "title": "Повелитель Времени",
        "desc": "Прокачайте Ускорение Времени до 3 ур. (5x)",
        "reward": 4,
        "icon": speed_upg_icon,
        "check": lambda s: s.get("Upgrades", {}).get("speed_limit", 0) >= 3,
        "progress": lambda s: (min(3, s.get("Upgrades", {}).get("speed_limit", 0)), 3)
    },
    {
        "id": "spawn_master",
        "category": "talents",
        "cat_name": "Таланты",
        "title": "Плотный Натиск",
        "desc": "Изучите хотя бы 1 ур. таланта Плотный Спавн",
        "reward": 3,
        "icon": speed_upg_icon,
        "check": lambda s: s.get("Upgrades", {}).get("spawn_rush", 0) >= 1,
        "progress": lambda s: (min(1, s.get("Upgrades", {}).get("spawn_rush", 0)), 1)
    },
    {
        "id": "drone_operator",
        "category": "talents",
        "cat_name": "Таланты",
        "title": "Кактусовый Дрон",
        "desc": "Изучите талант верного дрона-защитника",
        "reward": 5,
        "icon": cactus_img,
        "check": lambda s: s.get("Upgrades", {}).get("cactus_drone", 0) >= 1,
        "progress": lambda s: (min(1, s.get("Upgrades", {}).get("cactus_drone", 0)), 1)
    },
    {
        "id": "orbital_commander",
        "category": "talents",
        "cat_name": "Таланты",
        "title": "Орбитальный Удар",
        "desc": "Откройте космическую артиллерию Орбитальный Удар",
        "reward": 8,
        "icon": dark_cactus_img,
        "check": lambda s: s.get("Upgrades", {}).get("orbital_strike", 0) >= 1,
        "progress": lambda s: (min(1, s.get("Upgrades", {}).get("orbital_strike", 0)), 1)
    },
    {
        "id": "astral_pioneer",
        "category": "talents",
        "cat_name": "Таланты",
        "title": "Астральный Первопроходец",
        "desc": "Соберите хотя бы 1 Тёмный Кактус",
        "reward": 5,
        "icon": dark_cactus_img,
        "check": lambda s: s.get("DarkCactuses", 0) >= 1 or s.get("Upgrades", {}).get("orbital_strike", 0) > 0,
        "progress": lambda s: (min(1, s.get("DarkCactuses", 0) + (1 if s.get("Upgrades", {}).get("orbital_strike", 0) > 0 else 0)), 1)
    },
    {
        "id": "archivist",
        "category": "talents",
        "cat_name": "Таланты",
        "title": "Летописец Оазиса",
        "desc": "Создайте хотя бы 2 профиля сохранения",
        "reward": 3,
        "icon": trophy_icon,
        "check": lambda s: len(list_save_profiles()) >= 2,
        "progress": lambda s: (min(2, len(list_save_profiles())), 2)
    },
    {
        "id": "playtime_30m",
        "category": "talents",
        "cat_name": "Таланты",
        "title": "Первые Ростки",
        "desc": "Проведите 30 минут в игре",
        "reward": 3,
        "icon": sprout_icon,
        "check": lambda s: s.get("Stats", {}).get("play_time_seconds", 0) >= 1800,
        "progress": lambda s: (min(30, int(s.get("Stats", {}).get("play_time_seconds", 0) // 60)), 30)
    },
    {
        "id": "playtime_1h",
        "category": "talents",
        "cat_name": "Таланты",
        "title": "Закалённый Садовод",
        "desc": "Проведите 1 час в игре",
        "reward": 5,
        "icon": trophy_icon,
        "check": lambda s: s.get("Stats", {}).get("play_time_seconds", 0) >= 3600,
        "progress": lambda s: (min(60, int(s.get("Stats", {}).get("play_time_seconds", 0) // 60)), 60)
    },
    {
        "id": "playtime_5h",
        "category": "talents",
        "cat_name": "Таланты",
        "title": "Легенда Оазиса",
        "desc": "Проведите 5 часов в игре",
        "reward": 10,
        "icon": crown_upg_icon,
        "check": lambda s: s.get("Stats", {}).get("play_time_seconds", 0) >= 18000,
        "progress": lambda s: (min(300, int(s.get("Stats", {}).get("play_time_seconds", 0) // 60)), 300)
    },
    # -------------------------------------------------------------------------
]

# -------------------------------------------------------------------------
# 5. ГЛОБАЛЬНЫЕ ДОСТИЖЕНИЯ (GLOBAL PRESTIGE ACHIEVEMENTS)
# Хранятся ТОЛЬКО в saves/global_achievements.json и отображаются ТОЛЬКО в Главном Меню!
# -------------------------------------------------------------------------
GLOBAL_ACHIEVEMENTS_DATA = [
    # --- ОРАНЖЕРЕЯ ---
    {
        "id": "global_greenhouse_collector",
        "category": "global",
        "cat_name": "Глобальные",
        "title": "Флорист Оазиса",
        "desc": "Соберите и посадите все 8 сортов кактусов в Оранжерее",
        "reward": 0,
        "max_val": 8,
        "icon": sprout_icon,
        "check": lambda s: sum(1 for c in globals().get("GREENHOUSE_CACTI", []) if s.get("Greenhouse", {}).get(c["id"], {}).get("level", 0) >= 1) >= 8,
        "progress": lambda s: (min(8, sum(1 for c in globals().get("GREENHOUSE_CACTI", []) if s.get("Greenhouse", {}).get(c["id"], {}).get("level", 0) >= 1)), 8)
    },
    {
        "id": "global_greenhouse_master",
        "category": "global",
        "cat_name": "Глобальные",
        "title": "Владыка Оранжереи",
        "desc": "Прокачайте все 8 сортов кактусов до максимального 5 уровня",
        "reward": 0,
        "max_val": 8,
        "icon": sprout_icon,
        "check": lambda s: sum(1 for c in globals().get("GREENHOUSE_CACTI", []) if s.get("Greenhouse", {}).get(c["id"], {}).get("level", 0) >= 5) >= 8,
        "progress": lambda s: (min(8, sum(1 for c in globals().get("GREENHOUSE_CACTI", []) if s.get("Greenhouse", {}).get(c["id"], {}).get("level", 0) >= 5)), 8)
    },

    # --- РЕЛИКВИИ ---
    {
        "id": "global_relic_collector",
        "category": "global",
        "cat_name": "Глобальные",
        "title": "Хранитель Древностей",
        "desc": "Отыщите все 20 древних реликвий в Музее Археологии",
        "reward": 0,
        "max_val": 20,
        "icon": relic_icon,
        "check": lambda s: sum(1 for r in globals().get("RELICS_DATA", {}).values() if s.get("Relics", {}).get(r["id"], {}).get("level", 0) >= 1) >= 20,
        "progress": lambda s: (min(20, sum(1 for r in globals().get("RELICS_DATA", {}).values() if s.get("Relics", {}).get(r["id"], {}).get("level", 0) >= 1)), 20)
    },
    {
        "id": "global_relic_master",
        "category": "global",
        "cat_name": "Глобальные",
        "title": "Золотой Век Археологии",
        "desc": "Восстановите все 20 древних реликвий до максимального уровня",
        "reward": 0,
        "max_val": 20,
        "icon": relic_icon,
        "check": lambda s: sum(1 for r in globals().get("RELICS_DATA", {}).values() if s.get("Relics", {}).get(r["id"], {}).get("level", 0) >= 5) >= 20,
        "progress": lambda s: (min(20, sum(1 for r in globals().get("RELICS_DATA", {}).values() if s.get("Relics", {}).get(r["id"], {}).get("level", 0) >= 5)), 20)
    },

    # --- ДРЕВО ТАЛАНТОВ ---
    {
        "id": "global_tree_nodes_all",
        "category": "global",
        "cat_name": "Глобальные",
        "title": "Архитектор Древа",
        "desc": "Изучите абсолютно все 80 узлов в Древе улучшений Оазиса",
        "reward": 0,
        "max_val": 80,
        "icon": trophy_icon,
        "check": lambda s: sum(1 for nid in globals().get("UPGRADE_TREE_NODES", {}) if nid != "oasis_core" and s.get("Upgrades", {}).get(nid, 0) >= 1) >= 80,
        "progress": lambda s: (min(80, sum(1 for nid in globals().get("UPGRADE_TREE_NODES", {}) if nid != "oasis_core" and s.get("Upgrades", {}).get(nid, 0) >= 1)), 80)
    },
    {
        "id": "global_tree_levels_max",
        "category": "global",
        "cat_name": "Глобальные",
        "title": "Венец Эволюции",
        "desc": "Прокачайте все 80 улучшений Древа до абсолютного максимума",
        "reward": 0,
        "max_val": 256,
        "icon": crown_upg_icon,
        "check": lambda s: sum(min(n.get("max_lvl", 1), s.get("Upgrades", {}).get(nid, 0)) for nid, n in globals().get("UPGRADE_TREE_NODES", {}).items() if nid != "oasis_core") >= 256,
        "progress": lambda s: (min(256, sum(min(n.get("max_lvl", 1), s.get("Upgrades", {}).get(nid, 0)) for nid, n in globals().get("UPGRADE_TREE_NODES", {}).items() if nid != "oasis_core")), 256)
    },
    {
        "id": "global_bestiary_tier5",
        "category": "global",
        "cat_name": "Глобальные",
        "title": "Знаток Фауны",
        "desc": "Откройте как минимум 5-й тир бестиария у всех 18 существ оазиса",
        "reward": 0,
        "max_val": 18,
        "icon": trophy_icon,
        "check": lambda s: sum(1 for m in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 51, 52, 53, 777, 1000, 2000, 3000, 4000] if get_mob_bestiary_tier(m, s.get("BestiaryKills", {}).get(str(m), 0)) >= 5) >= 18,
        "progress": lambda s: (min(18, sum(1 for m in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 51, 52, 53, 777, 1000, 2000, 3000, 4000] if get_mob_bestiary_tier(m, s.get("BestiaryKills", {}).get(str(m), 0)) >= 5)), 18)
    },
    {
        "id": "global_bestiary_tier10",
        "category": "global",
        "cat_name": "Глобальные",
        "title": "Повелитель Бестиария",
        "desc": "Достигните максимального 10-го тира бестиария у всех 18 существ оазиса",
        "reward": 0,
        "max_val": 18,
        "icon": crown_upg_icon,
        "check": lambda s: sum(1 for m in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 51, 52, 53, 777, 1000, 2000, 3000, 4000] if get_mob_bestiary_tier(m, s.get("BestiaryKills", {}).get(str(m), 0)) >= 10) >= 18,
        "progress": lambda s: (min(18, sum(1 for m in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 51, 52, 53, 777, 1000, 2000, 3000, 4000] if get_mob_bestiary_tier(m, s.get("BestiaryKills", {}).get(str(m), 0)) >= 10)), 18)
    },

    # --- ПРОХОЖДЕНИЕ ИГРЫ ---
    {
        "id": "global_game_completed",
        "category": "global",
        "cat_name": "Глобальные",
        "title": "Триумф Оазиса",
        "desc": "Одолейте 100 волн и завершите Финал кампании",
        "reward": 0,
        "max_val": 100,
        "icon": crown_upg_icon,
        "check": lambda s: (s.get("LevelsRecords", [])[8] if len(s.get("LevelsRecords", [])) > 8 else 0) >= 100,
        "progress": lambda s: (min(100, s.get("LevelsRecords", [])[8] if len(s.get("LevelsRecords", [])) > 8 else 0), 100)
    },

    # --- ЖЁСТКИЕ ТРЕБОВАНИЯ ---
    {
        "id": "global_boss_slayer_100",
        "category": "global",
        "cat_name": "Глобальные",
        "title": "Истребитель Боссов",
        "desc": "Одолейте 100 боссов за всё время игры во всех битвах",
        "reward": 0,
        "max_val": 100,
        "icon": boss_img,
        "check": lambda s: s.get("Stats", {}).get("bosses_defeated", 0) >= 100,
        "progress": lambda s: (min(100, s.get("Stats", {}).get("bosses_defeated", 0)), 100)
    },
    {
        "id": "global_hardcore_conqueror",
        "category": "global",
        "cat_name": "Глобальные",
        "title": "Железная Воля",
        "desc": "Достигните 50 волны на сложности Хардкор",
        "reward": 0,
        "max_val": 50,
        "icon": void_boss_img,
        "check": lambda s: s.get("difficulty") == "hardcore" and max(s.get("LevelsRecords", [0]) or [0]) >= 50,
        "progress": lambda s: (min(50, max(s.get("LevelsRecords", [0]) or [0])) if s.get("difficulty") == "hardcore" else 0, 50)
    },
    {
        "id": "global_stellar_tycoon",
        "category": "global",
        "cat_name": "Глобальные",
        "title": "Звёздный Магнат",
        "desc": "Накопите суммарно 1 000 Звёздных кактусов",
        "reward": 0,
        "max_val": 1000,
        "icon": stellar_cactus_img,
        "check": lambda s: s.get("StellarCactuses", 0) >= 1000,
        "progress": lambda s: (min(1000, s.get("StellarCactuses", 0)), 1000)
    }
]

def update_global_achievements(savedata):
    """Обновляет статус 10 глобальных достижений в saves/global_achievements.json."""
    global_meta = load_global_achievements()
    changed = False

    # Удаляем старые неактуальные ключи, если они были сохранены
    valid_ids = {g["id"] for g in GLOBAL_ACHIEVEMENTS_DATA}
    keys_to_del = [k for k in global_meta if k not in valid_ids]
    if keys_to_del:
        for k in keys_to_del:
            del global_meta[k]
        changed = True

    for gach in GLOBAL_ACHIEVEMENTS_DATA:
        gid = gach["id"]
        entry = global_meta.setdefault(gid, {
            "unlocked": False,
            "progress": 0,
            "max": 1,
            "unlocked_at": ""
        })
        try:
            cur_p, max_p = gach["progress"](savedata)
            entry["max"] = max_p
            is_valid = gach["check"](savedata) or cur_p >= max_p

            if gid == "global_game_completed" and not is_valid:
                # Сбрасываем ошибочное открытие и завышенный прогресс от прошлых версий
                if entry.get("unlocked", False) or entry.get("progress", 0) > cur_p:
                    entry["unlocked"] = False
                    entry["unlocked_at"] = ""
                    entry["progress"] = cur_p
                    changed = True
            else:
                if cur_p > entry.get("progress", 0):
                    entry["progress"] = cur_p
                    changed = True
                if is_valid and not entry.get("unlocked", False):
                    entry["unlocked"] = True
                    entry["unlocked_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    changed = True
        except Exception:
            pass

    if changed:
        save_global_achievements(global_meta)
    return global_meta

def check_achievements(savedata):
    """Проверяет только локальные достижения текущего сейва."""
    unlocked_any = False
    ach_dict = savedata.setdefault("Achievements", {})

    for ach in ACHIEVEMENTS_DATA:
        aid = ach["id"]
        status = ach_dict.setdefault(aid, {"unlocked": False, "claimed": False})
        if not status["unlocked"]:
            if ach["check"](savedata):
                status["unlocked"] = True
                unlocked_any = True

    # Заодно синхронизируем прогресс глобальных достижений
    update_global_achievements(savedata)

    return unlocked_any

def has_unclaimed_achievements(savedata):
    check_achievements(savedata)
    valid_ids = {ach["id"] for ach in ACHIEVEMENTS_DATA}
    return any(
        st.get("unlocked", False) and not st.get("claimed", False)
        for aid, st in savedata.get("Achievements", {}).items()
        if aid in valid_ids
    )

def get_unclaimed_achievements_count(savedata):
    check_achievements(savedata)
    valid_ids = {ach["id"] for ach in ACHIEVEMENTS_DATA}
    return sum(
        1 for aid, st in savedata.get("Achievements", {}).items()
        if aid in valid_ids and st.get("unlocked", False) and not st.get("claimed", False)
    )

def get_tower_cost_multiplier(existing_count, difficulty="normal"):
    if existing_count <= 0:
        return 1.0
    mult = 1.0
    # Скейлинг цены на башню при покупке дубликатов того же типа:
    # На казуале: максимум x3.0
    # На нормале и хардкоре: x1.2, x1.2, x1.5, x1.5, x2, x3, x4 и дальше на 4 каждый раз
    if difficulty == "casual":
        steps = [1.2, 1.2, 1.5, 1.5, 2.0, 3.0]
        max_step = 3.0
    else:
        steps = [1.2, 1.2, 1.5, 1.5, 2.0, 3.0, 4.0]
        max_step = 4.0
    for i in range(existing_count):
        step_val = steps[i] if i < len(steps) else max_step
        mult *= step_val
    return mult

MAP_TOWER_PRICE_STEP = {
    0: 1.05,
    1: 1.055,
    2: 1.06,
    3: 1.065,
    4: 1.07,
    5: 1.075,
    6: 1.08,
    7: 1.09,
    8: 1.10,
    9: 1.10
}

def get_tower_build_cost(tower_type, towers, savedata=None, game_map=0, session_towers_bought=0):
    base_costs = {"magic": 100, "rock": 200, "freeze": 150, "tent": 220, "tesla": 250, "farm": 120, "sun": 200}
    base = base_costs.get(tower_type, 100)
    cnt = sum(1 for t in towers if t.type == tower_type)

    sdata = savedata if isinstance(savedata, dict) else globals().get("savedata", None)
    diff = sdata.get("difficulty", "normal") if sdata else "normal"

    # Модификатор цены за каждую покупку башни в текущем забеге (х1.05 на карте 0 .. х1.10 на карте 8/9)
    step = MAP_TOWER_PRICE_STEP.get(game_map, 1.05)
    session_mult = step ** max(0, session_towers_bought)

    cost = int(base * get_tower_cost_multiplier(cnt, difficulty=diff) * session_mult)
    # На сложности Казуальная: цены на башни на 20% ниже
    if diff == "casual":
        cost = int(cost * 0.8)

    if cnt == 0 and sdata and isinstance(sdata, dict):
        r_buffs = get_all_relic_buffs(sdata)
        disc = min(0.50, r_buffs.get("first_tower_discount", 0.0))
        if disc > 0:
            cost = max(10, int(cost * (1.0 - disc)))
    return max(10, cost)


# -------------------------------------------------------------------------
# СИСТЕМА ДРЕВНИХ РЕЛИКВИЙ (ARCHAEOLOGY & RELICS)
# -------------------------------------------------------------------------
RELICS_DATA = {
    # КАРТА 0: Оазис
    "ancient_urn": {
        "id": "ancient_urn",
        "map": 0,
        "name": "Древний Кувшин",
        "shape": [(0, 0), (1, 0)],
        "desc": "+10%/ур. к доходу Кактусовых Ферм",
        "icon_key": "relic",
        "formula": lambda lvl: {"farm_income_mult": 0.10 * lvl}
    },
    "fossil_needle": {
        "id": "fossil_needle",
        "map": 0,
        "name": "Окаменелая Игла",
        "shape": [(0, 0), (0, 1), (0, 2)],
        "desc": "+4%/ур. к дальности атаки всех башен",
        "icon_key": "relic",
        "formula": lambda lvl: {"range_mult": 0.04 * lvl}
    },

    # КАРТА 1: Каньон
    "sand_hammer": {
        "id": "sand_hammer",
        "map": 1,
        "name": "Песчаный Молот",
        "shape": [(0, 0), (1, 0), (0, 1)],
        "desc": "+8%/ур. к общему урону Огненной башни",
        "icon_key": "relic",
        "formula": lambda lvl: {"rock_damage_mult": 0.08 * lvl}
    },
    "pioneer_flask": {
        "id": "pioneer_flask",
        "map": 1,
        "name": "Фляга Первопроходца",
        "shape": [(0, 0)],
        "desc": "+2 HP базы на старте за каждый уровень",
        "icon_key": "relic",
        "formula": lambda lvl: {"base_hp_bonus": 2 * lvl}
    },

    # КАРТА 2: Шахты
    "magma_clot": {
        "id": "magma_clot",
        "map": 2,
        "name": "Магматический Сгусток",
        "shape": [(0, 0), (1, 0), (0, 1), (1, 1)],
        "desc": "+6%/ур. урона по замороженным врагам",
        "icon_key": "relic",
        "formula": lambda lvl: {"frozen_dmg_bonus": 0.06 * lvl}
    },
    "miner_token": {
        "id": "miner_token",
        "map": 2,
        "name": "Шахтёрский Жетон",
        "shape": [(0, 0), (1, 0)],
        "desc": "Скидка 10%/ур. на первую башню каждого типа",
        "icon_key": "relic",
        "formula": lambda lvl: {"first_tower_discount": 0.10 * lvl}
    },

    # КАРТА 3: Озеро
    "frost_rune": {
        "id": "frost_rune",
        "map": 3,
        "name": "Морозная Руна",
        "shape": [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],
        "desc": "+5%/ур. к длительности эффекта заморозки",
        "icon_key": "relic",
        "formula": lambda lvl: {"freeze_duration_mult": 0.05 * lvl}
    },
    "aquamarine_shard": {
        "id": "aquamarine_shard",
        "map": 3,
        "name": "Аквамариновый Осколок",
        "shape": [(0, 0), (1, 0), (1, 1)],
        "desc": "+4%/ур. урона по замедленным врагам от всех башен",
        "icon_key": "relic",
        "formula": lambda lvl: {"slowed_target_dmg_mult": 0.04 * lvl}
    },

    # КАРТА 4: Ореол
    "thunder_fang": {
        "id": "thunder_fang",
        "map": 4,
        "name": "Громовой Зуб",
        "shape": [(0, 0), (1, 0), (2, 0)],
        "desc": "Тесла цепляет +1 цель на 1 ур., +2 на 3 ур., +3 на 5 ур.",
        "icon_key": "relic",
        "formula": lambda lvl: {"tesla_extra_targets": 1 if lvl in (1, 2) else (2 if lvl in (3, 4) else (3 if lvl >= 5 else 0))}
    },
    "emerald_sprout": {
        "id": "emerald_sprout",
        "map": 4,
        "name": "Изумрудный Росток",
        "shape": [(0, 0), (0, 1)],
        "desc": "+15%/ур. к шансу выпадения ростков для Оранжереи",
        "icon_key": "relic",
        "formula": lambda lvl: {"sprout_drop_chance_mult": 0.15 * lvl}
    },

    # КАРТА 5: Лабиринт
    "optical_lens": {
        "id": "optical_lens",
        "map": 5,
        "name": "Оптический Прицел",
        "shape": [(0, 0), (1, 0), (2, 0), (1, 1)],
        "desc": "+2.5%/ур. к шансу критического удара всех башен",
        "icon_key": "relic",
        "formula": lambda lvl: {"crit_chance_bonus": 0.025 * lvl}
    },
    "shadow_compass": {
        "id": "shadow_compass",
        "map": 5,
        "name": "Теневой Компас",
        "shape": [(1, 0), (0, 1), (2, 1), (1, 2)],
        "desc": "+10%/ур. урона всех башен по Быстрым и Теневым слаймам",
        "icon_key": "relic",
        "formula": lambda lvl: {"fast_shadow_dmg_mult": 0.10 * lvl}
    },

    # КАРТА 6: Петля
    "spiked_carapace": {
        "id": "spiked_carapace",
        "map": 6,
        "name": "Шипастый Панцирь",
        "shape": [(0, 0), (1, 0), (0, 1), (1, 1)],
        "desc": "+10%/ур. HP воинов Палатки и +5%/ур. к их броне",
        "icon_key": "relic",
        "formula": lambda lvl: {"soldier_hp_mult": 0.10 * lvl, "soldier_armor_mult": 0.05 * lvl}
    },
    "vortex_bracelet": {
        "id": "vortex_bracelet",
        "map": 6,
        "name": "Вихревой Браслет",
        "shape": [(0, 0), (1, 0), (1, 1)],
        "desc": "+4%/ур. к скорости атаки всех башен",
        "icon_key": "relic",
        "formula": lambda lvl: {"atk_spd_mult": 0.04 * lvl}
    },

    # КАРТА 7: Вулкан
    "inferno_seal": {
        "id": "inferno_seal",
        "map": 7,
        "name": "Печать Инферно",
        "shape": [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],
        "desc": "+5%/ур. к радиусу сплэша взрыва Огненной башни",
        "icon_key": "relic",
        "formula": lambda lvl: {"rock_splash_mult": 0.05 * lvl}
    },
    "hardened_anvil": {
        "id": "hardened_anvil",
        "map": 7,
        "name": "Закалённая Наковальня",
        "shape": [(0, 0), (1, 0), (2, 0), (1, 1)],
        "desc": "Скидка 5%/ур. на любую прокачку башен в бою",
        "icon_key": "relic",
        "formula": lambda lvl: {"upgrade_cost_discount": 0.05 * lvl}
    },

    # КАРТА 8: Бездна
    "void_eye": {
        "id": "void_eye",
        "map": 8,
        "name": "Око Бездны",
        "shape": [(0, 0), (1, 0), (2, 0), (1, 1)],
        "desc": "+15%/ур. к критическому урону всех башен",
        "icon_key": "relic",
        "formula": lambda lvl: {"crit_dmg_bonus": 0.15 * lvl}
    },
    "conqueror_crown": {
        "id": "conqueror_crown",
        "map": 8,
        "name": "Корона Победителя",
        "shape": [(0, 0), (2, 0), (0, 1), (1, 1), (2, 1)],
        "desc": "+20%/ур. кактусов за победу над боссами",
        "icon_key": "relic",
        "formula": lambda lvl: {"boss_cacti_mult": 0.20 * lvl}
    },

    # КАРТА 9: Песочница
    "creator_mirror": {
        "id": "creator_mirror",
        "map": 9,
        "name": "Зеркало Творца",
        "shape": [(0, 0), (1, 0), (0, 1), (1, 1)],
        "desc": "+8%/ур. к стартовому запасу кактусов в игре",
        "icon_key": "relic",
        "formula": lambda lvl: {"start_cacti_mult": 0.08 * lvl}
    },
    "dimension_prism": {
        "id": "dimension_prism",
        "map": 9,
        "name": "Призма Измерений",
        "shape": [(1, 0), (0, 1), (1, 1), (2, 1)],
        "desc": "+10%/ур. к частоте метеоритов и получению Звезд",
        "icon_key": "relic",
        "formula": lambda lvl: {"meteor_magnet_mult": 0.10 * lvl}
    }
}

def get_relic_bonus_summary(rid, level):
    """Возвращает строку с точным текущим бонусом реликвии для заданного уровня."""
    if level <= 0:
        return "Нет активного бонуса"
    if rid == "ancient_urn":
        return f"+{10 * level}% доход Ферм"
    elif rid == "fossil_needle":
        return f"+{4 * level}% дальность башен"
    elif rid == "sand_hammer":
        return f"+{8 * level}% урон Огня"
    elif rid == "pioneer_flask":
        return f"+{2 * level} HP базы на старте"
    elif rid == "magma_clot":
        return f"+{6 * level}% урон по замороженным"
    elif rid == "miner_token":
        return f"Скидка {10 * level}% на 1-ю башню"
    elif rid == "frost_rune":
        return f"+{5 * level}% время заморозки"
    elif rid == "aquamarine_shard":
        return f"+{4 * level}% урон по замедленным"
    elif rid == "thunder_fang":
        extra = 1 if level in (1, 2) else (2 if level in (3, 4) else (3 if level >= 5 else 0))
        return f"+{extra} доп. цел. Теслы"
    elif rid == "emerald_sprout":
        return f"+{15 * level}% шанс ростков"
    elif rid == "optical_lens":
        val = round(2.5 * level, 1)
        val_str = f"{int(val)}" if val.is_integer() else f"{val}"
        return f"+{val_str}% шанс крита"
    elif rid == "shadow_compass":
        return f"+{10 * level}% по быстрым/теневым"
    elif rid == "spiked_carapace":
        return f"+{10 * level}% HP, +{5 * level}% брони"
    elif rid == "vortex_bracelet":
        return f"+{4 * level}% скор. атаки башен"
    elif rid == "inferno_seal":
        return f"+{5 * level}% радиус взрыва"
    elif rid == "hardened_anvil":
        return f"Скидка {5 * level}% на улучшение"
    elif rid == "void_eye":
        return f"+{15 * level}% крит. урон"
    elif rid == "conqueror_crown":
        return f"+{20 * level}% кактусов за боссов"
    elif rid == "creator_mirror":
        return f"+{8 * level}% стартовых кактусов"
    elif rid == "dimension_prism":
        return f"+{10 * level}% шанс метеоритов"
    return ""

def get_relic_max_level(savedata):
    return 1 + savedata.get("Upgrades", {}).get("relic_max_level", 0)

def get_relics_for_map(map_id):
    return [rid for rid, rdata in RELICS_DATA.items() if rdata.get("map") == map_id]

def are_map_relics_maxed(map_id, savedata):
    r_ids = get_relics_for_map(map_id)
    if not r_ids:
        return True
    max_cap = get_relic_max_level(savedata)
    relics_dict = savedata.get("Relics", {})
    return all(relics_dict.get(rid, {}).get("level", 0) >= max_cap for rid in r_ids)

def get_relic_upgrade_requirements(level, savedata=None):
    if level <= 1:
        base_req = 1
    else:
        base_req = 2 ** (level - 1)
    sdata = savedata if isinstance(savedata, dict) else globals().get("savedata", None)
    if sdata and isinstance(sdata, dict) and sdata.get("difficulty") == "hardcore":
        return base_req * 2
    return base_req

def add_relic_drop(relic_id, savedata, count=1):
    if "Relics" not in savedata:
        savedata["Relics"] = {}
    relic_entry = savedata["Relics"].setdefault(relic_id, {"level": 0, "finds": 0})
    max_cap = get_relic_max_level(savedata)
    cur_lvl = relic_entry.get("level", 0)

    if cur_lvl >= max_cap:
        return cur_lvl, False

    relic_entry["finds"] = relic_entry.get("finds", 0) + count
    lvl_up = False

    while cur_lvl < max_cap:
        req = get_relic_upgrade_requirements(cur_lvl + 1, savedata)
        if relic_entry["finds"] >= req:
            relic_entry["finds"] -= req
            cur_lvl += 1
            lvl_up = True
        else:
            break

    if cur_lvl >= max_cap:
        relic_entry["finds"] = 0

    relic_entry["level"] = cur_lvl
    savedata.setdefault("Stats", {})
    savedata["Stats"]["relics_excavated"] = savedata["Stats"].get("relics_excavated", 0) + count
    return cur_lvl, lvl_up

def get_max_relic_pedestals(savedata):
    return min(5, 2 + savedata.get("Upgrades", {}).get("relic_pedestals", 0))

def get_equipped_relics(savedata):
    max_slots = get_max_relic_pedestals(savedata)
    equipped = savedata.setdefault("EquippedRelics", [])
    relics_dict = savedata.get("Relics", {})
    valid = [rid for rid in equipped if rid in RELICS_DATA and relics_dict.get(rid, {}).get("level", 0) > 0]
    if len(valid) > max_slots:
        valid = valid[:max_slots]
    savedata["EquippedRelics"] = valid
    return valid

def equip_relic(savedata, relic_id):
    max_slots = get_max_relic_pedestals(savedata)
    equipped = get_equipped_relics(savedata)
    if relic_id in equipped:
        return True
    if len(equipped) >= max_slots:
        return False
    relics_dict = savedata.get("Relics", {})
    if relics_dict.get(relic_id, {}).get("level", 0) <= 0:
        return False
    equipped.append(relic_id)
    savedata["EquippedRelics"] = equipped
    return True

def unequip_relic(savedata, relic_id):
    equipped = get_equipped_relics(savedata)
    if relic_id in equipped:
        equipped.remove(relic_id)
        savedata["EquippedRelics"] = equipped
        return True
    return False

def get_all_relic_buffs(savedata):
    buffs = {
        "farm_income_mult": 0.0,
        "range_mult": 0.0,
        "rock_damage_mult": 0.0,
        "base_hp_bonus": 0,
        "frozen_dmg_bonus": 0.0,
        "first_tower_discount": 0.0,
        "freeze_duration_mult": 0.0,
        "slowed_target_dmg_mult": 0.0,
        "tesla_extra_targets": 0,
        "sprout_drop_chance_mult": 0.0,
        "crit_chance_bonus": 0.0,
        "fast_shadow_dmg_mult": 0.0,
        "soldier_hp_mult": 0.0,
        "soldier_armor_mult": 0.0,
        "atk_spd_mult": 0.0,
        "rock_splash_mult": 0.0,
        "upgrade_cost_discount": 0.0,
        "crit_dmg_bonus": 0.0,
        "boss_cacti_mult": 0.0,
        "start_cacti_mult": 0.0,
        "meteor_magnet_mult": 0.0,
    }
    relics_dict = savedata.get("Relics", {})
    active_relic_ids = get_equipped_relics(savedata)
    active_set = set(active_relic_ids)

    # 1. Экипированные реликвии (100% мощности на пьедесталах)
    for rid in active_relic_ids:
        rdata = RELICS_DATA.get(rid)
        if not rdata:
            continue
        lvl = relics_dict.get(rid, {}).get("level", 0)
        if lvl > 0 and "formula" in rdata:
            bonuses = rdata["formula"](lvl)
            for k, v in bonuses.items():
                if k in buffs:
                    buffs[k] += v
                else:
                    buffs[k] = v

    # 2. Тёмный Резонанс: пассивное действие неэкипированных реликвий (+5% за ранг, до 20%)
    dark_res_lvl = savedata.get("Upgrades", {}).get("dark_relic_resonance", 0)
    if dark_res_lvl > 0:
        passive_ratio = dark_res_lvl * 0.05
        for rid, rentry in relics_dict.items():
            if rid in active_set:
                continue
            rdata = RELICS_DATA.get(rid)
            if not rdata:
                continue
            lvl = rentry.get("level", 0) if isinstance(rentry, dict) else 0
            if lvl > 0 and "formula" in rdata:
                bonuses = rdata["formula"](lvl)
                for k, v in bonuses.items():
                    val = v * passive_ratio
                    if k in buffs:
                        buffs[k] += val
                    else:
                        buffs[k] = val

    # Округление целочисленных характеристик
    if "base_hp_bonus" in buffs:
        buffs["base_hp_bonus"] = int(round(buffs["base_hp_bonus"]))
    if "tesla_extra_targets" in buffs:
        buffs["tesla_extra_targets"] = int(round(buffs["tesla_extra_targets"]))

    return buffs

