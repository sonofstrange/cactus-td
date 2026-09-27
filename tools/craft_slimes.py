import os
import pygame

def recolor_and_decorate_slimes():
    pygame.init()
    base_img = pygame.image.load("assets/textures/mob1.png")
    w, h = base_img.get_size()

    # Functional categories in mob1.png:
    # Shadow: c.a < 200
    # Outline: (18, 33, 4)
    # Eyes: (36, 42, 42) or (35, 36, 40) or (25 <= x <= 45 and 37 <= y <= 44 and c.r < 45)
    # Body shades:
    # 0: dark bottom (r < 30)
    # 1: med-dark (30 <= r < 48)
    # 2: med base (48 <= r < 60)
    # 3: light base (60 <= r < 70)
    # 4: bright rim (70 <= r < 100)
    # 5: specular glint (r >= 100)

    def get_shade_idx(r, g, b):
        if r >= 100: return 5
        if r >= 70: return 4
        if r >= 60: return 3
        if r >= 48: return 2
        if r >= 30: return 1
        return 0

    palettes = {
        "prism_slime.png": {
            "outline": (22, 18, 48),
            "shades": [
                (55, 40, 95),    # dark
                (75, 70, 150),   # med-dark
                (50, 160, 200),  # med cyan
                (110, 205, 235), # light cyan
                (185, 235, 255), # highlight
                (245, 220, 255)  # specular magenta-white
            ],
            "eye_color": (32, 28, 55)
        },
        "mana_devourer_slime.png": {
            "outline": (24, 10, 42),
            "shades": [
                (55, 16, 92),
                (85, 25, 138),
                (128, 42, 195),
                (168, 70, 235),
                (210, 115, 255),
                (245, 190, 255)
            ],
            "eye_color": (35, 12, 50)
        },
        "obsidian_slime.png": {
            "outline": (16, 16, 20),
            "shades": [
                (32, 33, 38),
                (48, 50, 58),
                (66, 68, 78),
                (90, 92, 102),
                (122, 126, 138),
                (165, 170, 185)
            ],
            "eye_color": (255, 95, 20)  # glowing lava eyes!
        },
        "steam_slime.png": {
            "outline": (42, 28, 18),
            "shades": [
                (85, 55, 38),
                (135, 90, 62),
                (178, 128, 92),
                (212, 168, 135),
                (238, 208, 182),
                (255, 245, 235)
            ],
            "eye_color": (45, 32, 24)
        },
        "kamikaze_slime.png": {
            "outline": (50, 12, 10),
            "shades": [
                (115, 22, 14),
                (168, 40, 18),
                (218, 65, 24),
                (252, 105, 32),
                (255, 155, 48),
                (255, 225, 120)
            ],
            "eye_color": (38, 15, 15)
        },
        "protector_slime.png": {
            "outline": (14, 24, 42),
            "shades": [
                (28, 48, 80),
                (42, 72, 118),
                (62, 105, 168),
                (92, 140, 208),
                (135, 180, 240),
                (210, 230, 255)
            ],
            "eye_color": (20, 32, 50)
        },
        "phantom_slime.png": {
            "outline": (12, 32, 38),
            "shades": [
                (22, 60, 72),
                (38, 98, 118),
                (62, 148, 168),
                (100, 198, 215),
                (158, 232, 240),
                (225, 252, 255)
            ],
            "eye_color": (15, 42, 50)
        },
        "burrower_slime.png": {
            "outline": (32, 20, 10),
            "shades": [
                (65, 38, 18),
                (98, 60, 32),
                (138, 88, 48),
                (178, 120, 68),
                (210, 155, 98),
                (240, 200, 155)
            ],
            "eye_color": (36, 24, 16)
        }
    }

    for fname, pdata in palettes.items():
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(h):
            for x in range(w):
                c = base_img.get_at((x, y))
                if c.a == 0:
                    continue
                if c.a < 200:
                    # Shadow: keep shadow color & alpha
                    surf.set_at((x, y), (17, 17, 17, c.a))
                    continue

                # Check if eye
                if (25 <= x <= 45 and 37 <= y <= 44) and (c.r < 45 and c.g < 45 and c.b < 45):
                    surf.set_at((x, y), (*pdata["eye_color"], 255))
                    continue

                # Check if outline
                if c.r < 25 and c.g < 40 and c.b < 15:
                    surf.set_at((x, y), (*pdata["outline"], 255))
                    continue

                # Body shade
                s_idx = get_shade_idx(c.r, c.g, c.b)
                new_col = pdata["shades"][s_idx]
                surf.set_at((x, y), (*new_col, 255))

        # --- Draw Authentic Pixel-Art Decorations ---
        if fname == "prism_slime.png":
            # Crystal shard protruding from head
            # Base (30..34, 18..25)
            c_light = (220, 245, 255)
            c_mid = (130, 220, 250)
            c_dark = (60, 90, 180)
            c_edge = (30, 35, 80)
            for cy in range(12, 26):
                half_w = max(0, 3 - abs(cy - 18) // 3)
                for cx in range(32 - half_w, 33 + half_w):
                    if cx < 32: surf.set_at((cx, cy), (*c_light, 255))
                    elif cx == 32: surf.set_at((cx, cy), (*c_mid, 255))
                    else: surf.set_at((cx, cy), (*c_dark, 255))
            surf.set_at((32, 11), (*c_edge, 255))

        elif fname == "mana_devourer_slime.png":
            # Curved magic horn on forehead
            horn_col = (255, 215, 255)
            horn_edge = (80, 20, 110)
            for hy in range(14, 25):
                hx = 32 + (24 - hy) // 3
                surf.set_at((hx, hy), (*horn_col, 255))
                surf.set_at((hx + 1, hy), (*horn_edge, 255))
                surf.set_at((hx - 1, hy), (*horn_edge, 255))
            surf.set_at((35, 13), (*horn_edge, 255))
            # Arcane forehead sigil
            surf.set_at((32, 28), (255, 230, 255, 255))
            surf.set_at((31, 29), (210, 120, 255, 255))
            surf.set_at((33, 29), (210, 120, 255, 255))
            surf.set_at((32, 30), (255, 230, 255, 255))

        elif fname == "obsidian_slime.png":
            # Fiery magma veins across body
            lava_hot = (255, 230, 100)
            lava_mid = (255, 120, 20)
            veins = [
                (20, 30), (21, 31), (22, 32), (23, 31), (24, 30), (25, 31), (26, 32),
                (38, 28), (39, 29), (40, 30), (41, 31), (42, 32), (43, 31),
                (30, 48), (31, 49), (32, 48), (33, 47), (34, 48), (35, 49)
            ]
            for vx, vy in veins:
                surf.set_at((vx, vy), (*lava_hot, 255))
                for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if surf.get_at((vx+ox, vy+oy)).a == 255 and (vx+ox, vy+oy) not in veins:
                        surf.set_at((vx+ox, vy+oy), (*lava_mid, 255))

        elif fname == "steam_slime.png":
            # Fluffy steam puffs rising from head
            steam_white = (255, 255, 255)
            steam_shade = (210, 220, 230)
            clouds = [
                (28, 14, 4), (34, 12, 5), (40, 15, 4)
            ]
            for cx, cy, rad in clouds:
                for py in range(cy - rad, cy + rad + 1):
                    for px in range(cx - rad, cx + rad + 1):
                        d = (px - cx)**2 + (py - cy)**2
                        if d <= rad**2:
                            col = steam_white if py < cy else steam_shade
                            surf.set_at((px, py), (*col, 240))

        elif fname == "kamikaze_slime.png":
            # Twisted bomb fuse on top of head with spark
            fuse_col = (140, 105, 55)
            fuse_pts = [(32, 22), (32, 20), (33, 18), (34, 16), (33, 14)]
            for fx, fy in fuse_pts:
                surf.set_at((fx, fy), (*fuse_col, 255))
                surf.set_at((fx+1, fy), (60, 40, 20, 255))
            # Spark at tip
            surf.set_at((33, 13), (255, 245, 120, 255))
            surf.set_at((32, 13), (255, 140, 20, 255))
            surf.set_at((34, 13), (255, 140, 20, 255))
            surf.set_at((33, 12), (255, 255, 255, 255))

        elif fname == "protector_slime.png":
            # Steel knight brow crest / visor
            metal_hi = (210, 225, 245)
            metal_mid = (130, 150, 175)
            metal_edge = (40, 50, 65)
            for vx in range(23, 43):
                surf.set_at((vx, 33), (*metal_edge, 255))
                surf.set_at((vx, 34), (*(metal_hi if vx % 2 == 0 else metal_mid), 255))
                surf.set_at((vx, 35), (*metal_mid, 255))
                surf.set_at((vx, 36), (*metal_edge, 255))

        elif fname == "phantom_slime.png":
            # Ghostly aura whisps at top
            wisp_hi = (230, 255, 255)
            wisp_mid = (120, 215, 235)
            wisp_pts = [(32, 13), (32, 14), (31, 15), (31, 16), (32, 17), (32, 18)]
            for wx, wy in wisp_pts:
                surf.set_at((wx, wy), (*wisp_hi, 230))
                surf.set_at((wx - 1, wy), (*wisp_mid, 180))
                surf.set_at((wx + 1, wy), (*wisp_mid, 180))

        elif fname == "burrower_slime.png":
            # Miner helmet on top & glowing round headlamp
            helm_gold = (230, 175, 45)
            helm_shade = (145, 95, 22)
            helm_edge = (55, 32, 12)
            for hy in range(21, 28):
                hw = 12 - (27 - hy)
                for hx in range(32 - hw, 33 + hw):
                    if hx in (32 - hw, 32 + hw) or hy == 21:
                        surf.set_at((hx, hy), (*helm_edge, 255))
                    elif hy < 24:
                        surf.set_at((hx, hy), (*helm_gold, 255))
                    else:
                        surf.set_at((hx, hy), (*helm_shade, 255))
            # Glowing lantern in center of helmet
            surf.set_at((32, 24), (255, 255, 200, 255))
            surf.set_at((31, 24), (255, 210, 60, 255))
            surf.set_at((33, 24), (255, 210, 60, 255))
            surf.set_at((32, 23), (255, 210, 60, 255))
            surf.set_at((32, 25), (255, 210, 60, 255))

        out_path = os.path.join("assets/textures", fname)
        pygame.image.save(surf, out_path)
        print(f"Saved authentic Stardew-style slime texture: {out_path} ({w}x{h})")

if __name__ == "__main__":
    recolor_and_decorate_slimes()
