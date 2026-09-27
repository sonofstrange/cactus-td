import pygame
pygame.init()
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GOLD, small_font, font, large_font, tiny_font, massive_font
from game_data import BESTIARY_DATA, get_mob_bestiary_tier, get_mob_bestiary_progress, ROMAN_TIERS, get_slime_texture

def wrap_text_to_lines(text, f_obj, max_width):
    lines = []
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        words = paragraph.split(" ")
        cur_line = ""
        for w in words:
            test_line = cur_line + (" " if cur_line else "") + w
            if f_obj.size(test_line)[0] <= max_width:
                cur_line = test_line
            else:
                if cur_line:
                    lines.append(cur_line)
                cur_line = w
        if cur_line:
            lines.append(cur_line)
    return lines

surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
surf.fill((16, 20, 28))

# Test with King Slime (id: 1000)
slime = next(s for s in BESTIARY_DATA if s['id'] == 1000)
savedata = {
    'BestiaryKills': {'1000': 3},
    'Upgrades': {'bestiary_damage': 5, 'bestiary_cacti': 4, 'bestiary_stars': 3},
    'BestiaryClaimed': {}
}

dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
dim_surf.fill((0, 0, 0, 215))
surf.blit(dim_surf, (0, 0))

modal_w, modal_h = 840, 560
modal_rect = pygame.Rect((SCREEN_WIDTH - modal_w) // 2, (SCREEN_HEIGHT - modal_h) // 2, modal_w, modal_h)

is_boss = slime.get('is_boss', False)
bd_col = (220, 100, 255) if is_boss else (70, 180, 255)

pygame.draw.rect(surf, (16, 22, 34), modal_rect, border_radius=16)
pygame.draw.rect(surf, bd_col, modal_rect, width=2, border_radius=16)

# Header
t_col = (255, 225, 75) if is_boss else WHITE
nm_surf = large_font.render(slime['name'], True, t_col)
surf.blit(nm_surf, (modal_rect.left + 28, modal_rect.top + 16))

sub_col = (230, 160, 255) if is_boss else (140, 205, 255)
sub_surf = font.render(f"[{slime.get('title', '').upper()}]", True, sub_col)
surf.blit(sub_surf, (modal_rect.left + 36 + nm_surf.get_width(), modal_rect.top + 20))

pygame.draw.line(surf, (45, 60, 85), (modal_rect.left + 24, modal_rect.top + 58), (modal_rect.right - 24, modal_rect.top + 58), 1)

# Left Column: Sprite & Combat parameters
spr_box = pygame.Rect(modal_rect.left + 24, modal_rect.top + 72, 236, 175)
pygame.draw.rect(surf, (12, 16, 26), spr_box, border_radius=10)
pygame.draw.rect(surf, bd_col, spr_box, width=1, border_radius=10)

raw_tex = get_slime_texture(slime['img_key'])
scaled_tex = pygame.transform.scale(raw_tex, (100, 100))
surf.blit(scaled_tex, (spr_box.centerx - 50, spr_box.centery - 55))

badge_txt = font.render('БОСС 25-Й ВОЛНЫ' if is_boss else 'МОБ ОАЗИСА', True, GOLD if is_boss else (100, 220, 255))
surf.blit(badge_txt, (spr_box.centerx - badge_txt.get_width() // 2, spr_box.bottom - 30))

stats_box = pygame.Rect(modal_rect.left + 24, modal_rect.top + 260, 236, 225)
pygame.draw.rect(surf, (14, 20, 30), stats_box, border_radius=10)
pygame.draw.rect(surf, (45, 60, 80), stats_box, width=1, border_radius=10)

st_hdr = font.render('ХАРАКТЕРИСТИКИ', True, GOLD)
surf.blit(st_hdr, (stats_box.left + 14, stats_box.top + 10))

hp_val = slime.get('base_hp', 1)
rows = [
    ('Здоровье (HP):', f"{hp_val:,}", (255, 120, 120)),
    ('Скорость:', f"{slime.get('speed', 'Обычная')}", (255, 185, 90)),
    ('Урон базе:', f"{slime.get('base_damage', 1)}", (255, 100, 100)),
    ('Награда:', f"+{max(1, hp_val // 3)} какт.", (120, 245, 140)),
    ('Дроп звёзд:', '100% (Гарант)' if is_boss else '~5-15%', (255, 230, 80)),
]
ry = stats_box.top + 38
for lbl, val, val_c in rows:
    l_surf = tiny_font.render(lbl, True, (170, 185, 205))
    v_surf = tiny_font.render(val, True, val_c)
    surf.blit(l_surf, (stats_box.left + 14, ry))
    surf.blit(v_surf, (stats_box.right - 14 - v_surf.get_width(), ry))
    ry += 24

if is_boss:
    b_tag = tiny_font.render('Иммунитет к заморозке/стану', True, (240, 160, 255))
    surf.blit(b_tag, (stats_box.centerx - b_tag.get_width() // 2, stats_box.bottom - 26))

# Right Column: Special, Lore, Bestiary Progress
rx = modal_rect.left + 276
rw = modal_w - 300

# Box 1: Special
spec_box = pygame.Rect(rx, modal_rect.top + 72, rw, 140)
pygame.draw.rect(surf, (20, 16, 28) if is_boss else (16, 24, 36), spec_box, border_radius=10)
pygame.draw.rect(surf, (160, 70, 210) if is_boss else (55, 110, 175), spec_box, width=1, border_radius=10)

sp_hdr = font.render('✦ ОСОБЕННОСТИ И СПОСОБНОСТИ', True, (240, 170, 255) if is_boss else (110, 220, 255))
surf.blit(sp_hdr, (spec_box.left + 16, spec_box.top + 10))

sp_lines = wrap_text_to_lines(slime.get('special', 'Нет особых способностей'), small_font, rw - 32)
sy = spec_box.top + 36
for line in sp_lines:
    l_s = small_font.render(line, True, (240, 245, 255))
    surf.blit(l_s, (spec_box.left + 16, sy))
    sy += 22

# Box 2: Lore
lore_box = pygame.Rect(rx, modal_rect.top + 224, rw, 105)
pygame.draw.rect(surf, (18, 22, 32), lore_box, border_radius=10)
pygame.draw.rect(surf, (45, 60, 85), lore_box, width=1, border_radius=10)

lr_hdr = font.render('✦ ОПИСАНИЕ И ЛОР', True, (255, 215, 110))
surf.blit(lr_hdr, (lore_box.left + 16, lore_box.top + 10))

lr_lines = wrap_text_to_lines(slime.get('desc', ''), tiny_font, rw - 32)
ly = lore_box.top + 36
for line in lr_lines:
    l_s = tiny_font.render(line, True, (200, 215, 230))
    surf.blit(l_s, (lore_box.left + 16, ly))
    ly += 20

# Box 3: Bestiary Progress & Talents
prog_box = pygame.Rect(rx, modal_rect.top + 341, rw, 144)
pygame.draw.rect(surf, (16, 26, 32), prog_box, border_radius=10)
pygame.draw.rect(surf, (50, 130, 95), prog_box, width=1, border_radius=10)

pr_hdr = font.render('✦ БЕСТИАРИЙ И БОНУСЫ ТАЛАНТОВ', True, (110, 245, 160))
surf.blit(pr_hdr, (prog_box.left + 16, prog_box.top + 10))

kills = savedata.get('BestiaryKills', {}).get(str(slime['id']), 0)
tier, in_t, needed, ratio = get_mob_bestiary_progress(slime['id'], kills)

tier_txt = font.render(f"ТИР {ROMAN_TIERS[tier]} ({tier}/10)", True, GOLD if tier == 10 else (120, 240, 255))
surf.blit(tier_txt, (prog_box.left + 16, prog_box.top + 34))

k_txt = tiny_font.render(f"Убито в боях: {kills:,}", True, (220, 230, 245))
surf.blit(k_txt, (prog_box.right - 16 - k_txt.get_width(), prog_box.top + 36))

# Bar
bar_rect = pygame.Rect(prog_box.left + 16, prog_box.top + 58, rw - 32, 14)
pygame.draw.rect(surf, (12, 16, 22), bar_rect, border_radius=4)
fill_w = int(bar_rect.width * ratio)
if fill_w > 0:
    pygame.draw.rect(surf, GOLD if tier == 10 else (75, 220, 135), (bar_rect.left, bar_rect.top, fill_w, 14), border_radius=4)
pygame.draw.rect(surf, (50, 80, 70), bar_rect, width=1, border_radius=4)
p_str = 'МАКСИМАЛЬНЫЙ ТИР' if tier == 10 else f"{in_t} / {needed} до следующего тира"
p_surf = tiny_font.render(p_str, True, WHITE)
surf.blit(p_surf, (bar_rect.centerx - p_surf.get_width() // 2, bar_rect.centery - p_surf.get_height() // 2))

# Active Bonuses
b_dmg = tier * savedata['Upgrades'].get('bestiary_damage', 0)
b_cacti = tier * savedata['Upgrades'].get('bestiary_cacti', 0)
b_stars = tier * savedata['Upgrades'].get('bestiary_stars', 0)

b1 = tiny_font.render(f"• Анатомия Слаймов: +{b_dmg}% урона по этому виду", True, (255, 140, 140) if b_dmg > 0 else (140, 155, 170))
b2 = tiny_font.render(f"• Охотничья Премия: +{b_cacti}% кактусов за убийство", True, (120, 245, 140) if b_cacti > 0 else (140, 155, 170))
b3 = tiny_font.render(f"• Звёздный Трофей: +{b_stars}% к шансу Звёздного кактуса", True, (255, 230, 80) if b_stars > 0 else (140, 155, 170))
surf.blit(b1, (prog_box.left + 16, prog_box.top + 78))
surf.blit(b2, (prog_box.left + 16, prog_box.top + 98))
surf.blit(b3, (prog_box.left + 16, prog_box.top + 118))

# Bottom Bar
close_btn = pygame.Rect(modal_rect.centerx - 90, modal_rect.bottom - 46, 180, 36)
pygame.draw.rect(surf, (180, 45, 45), close_btn, border_radius=8)
pygame.draw.rect(surf, WHITE, close_btn, width=1, border_radius=8)
c_txt = font.render('ЗАКРЫТЬ [ESC]', True, WHITE)
surf.blit(c_txt, (close_btn.centerx - c_txt.get_width() // 2, close_btn.centery - c_txt.get_height() // 2))

pygame.image.save(surf, 'test_bestiary_inspect_modal.png')
print('Modal saved successfully!')
