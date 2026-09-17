"""
config.py - Конфигурация, ресурсы, шрифты, звуки и данные биомов/карт.
"""

import io
import math
import os
# Качественное билинейное сглаживание при масштабировании GPU (устраняет пикселизацию)
os.environ["SDL_RENDER_SCALE_QUALITY"] = "1"

import random
import struct
import wave
import pygame

pygame.init()

import sys

IS_ANDROID = hasattr(sys, 'getandroidapilevel') or 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_PRIVATE' in os.environ
GAME_VERSION = "0.1.0"

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
elif IS_ANDROID:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Инициализация дисплея с поддержкой нативного полноэкранного масштабирования на Android
# Инициализация дисплея с поддержкой нативного полноэкранного масштабирования на Android
USE_NATIVE_SCALED = False

if IS_ANDROID:
    os.environ["SDL_RENDER_SCALE_QUALITY"] = "1"
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
        if screen is not None and screen.get_size() == (SCREEN_WIDTH, SCREEN_HEIGHT):
            real_screen = screen
            USE_NATIVE_SCALED = True
            print(f"[DISPLAY] Native GPU pygame.SCALED initialized successfully! Size: {screen.get_size()}", flush=True)
    except Exception as e:
        print(f"[DISPLAY] pygame.SCALED failed ({e}), using fast software scaler", flush=True)
        USE_NATIVE_SCALED = False

    if not USE_NATIVE_SCALED:
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        try:
            real_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        except Exception:
            real_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    _orig_flip = pygame.display.flip
    _orig_update = pygame.display.update

    _layout = {
        'win_w': SCREEN_WIDTH,
        'win_h': SCREEN_HEIGHT,
        'scale': 1.0,
        'scaled_w': SCREEN_WIDTH,
        'scaled_h': SCREEN_HEIGHT,
        'offset_x': 0,
        'offset_y': 0,
        'scaled_surface': None,
    }

    def _get_layout(recheck_surface=False):
        global real_screen, _layout
        try:
            win_w, win_h = pygame.display.get_window_size()
        except Exception:
            win_w, win_h = 0, 0

        if win_w <= 0 or win_h <= 0:
            if real_screen is not None:
                win_w, win_h = real_screen.get_size()
            else:
                win_w, win_h = SCREEN_WIDTH, SCREEN_HEIGHT

        if recheck_surface and real_screen is not None and not USE_NATIVE_SCALED:
            rw, rh = real_screen.get_size()
            if rw != win_w or rh != win_h:
                try:
                    real_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    win_w, win_h = real_screen.get_size()
                except Exception:
                    pass

        if win_w != _layout['win_w'] or win_h != _layout['win_h'] or _layout['scaled_surface'] is None:
            scale = min(win_w / float(SCREEN_WIDTH), win_h / float(SCREEN_HEIGHT))
            scaled_w = int(round(SCREEN_WIDTH * scale))
            scaled_h = int(round(SCREEN_HEIGHT * scale))
            offset_x = (win_w - scaled_w) // 2
            offset_y = (win_h - scaled_h) // 2

            try:
                surf = pygame.Surface((scaled_w, scaled_h)).convert()
            except Exception:
                surf = pygame.Surface((scaled_w, scaled_h))

            _layout = {
                'win_w': win_w,
                'win_h': win_h,
                'scale': scale,
                'scaled_w': scaled_w,
                'scaled_h': scaled_h,
                'offset_x': offset_x,
                'offset_y': offset_y,
                'scaled_surface': surf,
            }
        return _layout

    # Initial layout calculation
    _get_layout(recheck_surface=True)

    def _scaled_flip(*args, **kwargs):
        global real_screen
        if USE_NATIVE_SCALED:
            _orig_flip()
            return

        if real_screen is not None and real_screen != screen:
            layout = _get_layout(recheck_surface=True)
            sw = layout['scaled_w']
            sh = layout['scaled_h']
            ox = layout['offset_x']
            oy = layout['offset_y']
            dest_surf = layout['scaled_surface']

            # High-speed scale on Android CPU: 1.5ms instead of 50ms smoothscale!
            try:
                scaled = pygame.transform.scale(screen, (sw, sh), dest_surf)
            except Exception:
                scaled = pygame.transform.scale(screen, (sw, sh))

            rw, rh = real_screen.get_size()
            if ox > 0:
                real_screen.fill((0, 0, 0), (0, 0, ox, rh))
                real_screen.fill((0, 0, 0), (ox + sw, 0, rw - (ox + sw), rh))
            if oy > 0:
                real_screen.fill((0, 0, 0), (0, 0, rw, oy))
                real_screen.fill((0, 0, 0), (0, oy + sh, rw, rh - (oy + sh)))

            real_screen.blit(scaled, (ox, oy))
            _orig_flip()
        else:
            _orig_flip()

    pygame.display.flip = _scaled_flip
    pygame.display.update = _scaled_flip
else:
    real_screen = None
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.RESIZABLE)
    except Exception:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def _get_layout(*args, **kwargs):
        return {
            'win_w': SCREEN_WIDTH,
            'win_h': SCREEN_HEIGHT,
            'scale': 1.0,
            'scaled_w': SCREEN_WIDTH,
            'scaled_h': SCREEN_HEIGHT,
            'offset_x': 0,
            'offset_y': 0,
            'scaled_surface': None,
        }

# Прозрачный маппинг координат мыши/тача Android в виртуальные координаты игры
_last_virtual_mouse_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

def _map_coords(rx, ry):
    if USE_NATIVE_SCALED:
        return max(0, min(SCREEN_WIDTH - 1, int(rx))), max(0, min(SCREEN_HEIGHT - 1, int(ry)))
    if not (IS_ANDROID and real_screen is not None and real_screen != screen):
        return rx, ry
    layout = _get_layout(recheck_surface=False)
    scale = layout['scale']
    ox = layout['offset_x']
    oy = layout['offset_y']
    if scale <= 0:
        return rx, ry
    vx = int((rx - ox) / scale)
    vy = int((ry - oy) / scale)
    return max(0, min(SCREEN_WIDTH - 1, vx)), max(0, min(SCREEN_HEIGHT - 1, vy))

_orig_mouse_get_pos = pygame.mouse.get_pos
def _virtual_mouse_get_pos():
    if IS_ANDROID and real_screen is not None and real_screen != screen and not USE_NATIVE_SCALED:
        raw_x, raw_y = _orig_mouse_get_pos()
        if raw_x > 0 or raw_y > 0:
            return _map_coords(raw_x, raw_y)
        return _last_virtual_mouse_pos
    return _orig_mouse_get_pos()
pygame.mouse.get_pos = _virtual_mouse_get_pos

# Прозрачный маппинг кнопки "Назад" Android (K_AC_BACK) и touch-координат
_orig_event_get = pygame.event.get
def _cross_platform_event_get(*args, **kwargs):
    global _last_virtual_mouse_pos
    events = _orig_event_get(*args, **kwargs)
    new_events = []
    layout = _get_layout(recheck_surface=False) if (IS_ANDROID and not USE_NATIVE_SCALED) else None
    for ev in events:
        if ev.type == pygame.KEYDOWN and hasattr(pygame, 'K_AC_BACK') and ev.key == pygame.K_AC_BACK:
            ev.key = pygame.K_ESCAPE

        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
            try:
                pygame.display.toggle_fullscreen()
            except Exception:
                pass

        if IS_ANDROID:
            if not USE_NATIVE_SCALED and real_screen is not None and real_screen != screen and layout:
                if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                    vx, vy = _map_coords(ev.pos[0], ev.pos[1])
                    _last_virtual_mouse_pos = (vx, vy)
                    d = dict(ev.__dict__)
                    d['pos'] = (vx, vy)
                    ev = pygame.event.Event(ev.type, d)
                elif ev.type == pygame.MOUSEMOTION:
                    vx, vy = _map_coords(ev.pos[0], ev.pos[1])
                    _last_virtual_mouse_pos = (vx, vy)
                    d = dict(ev.__dict__)
                    d['pos'] = (vx, vy)
                    scale = layout['scale']
                    if 'rel' in d and scale > 0:
                        d['rel'] = (int(d['rel'][0] / scale), int(d['rel'][1] / scale))
                    ev = pygame.event.Event(ev.type, d)
                elif hasattr(pygame, 'FINGERDOWN') and ev.type in (pygame.FINGERDOWN, pygame.FINGERUP):
                    rx = int(ev.x * layout['win_w'])
                    ry = int(ev.y * layout['win_h'])
                    vx, vy = _map_coords(rx, ry)
                    _last_virtual_mouse_pos = (vx, vy)
                elif hasattr(pygame, 'FINGERMOTION') and ev.type == pygame.FINGERMOTION:
                    rx = int(ev.x * layout['win_w'])
                    ry = int(ev.y * layout['win_h'])
                    vx, vy = _map_coords(rx, ry)
                    _last_virtual_mouse_pos = (vx, vy)
            elif USE_NATIVE_SCALED:
                if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    _last_virtual_mouse_pos = ev.pos

        new_events.append(ev)
    return new_events
pygame.event.get = _cross_platform_event_get

# Пресеты графики: "normal" (полная волновая анимация фона с искажениями, частицы) и "optimized" (легкий дрейф фона, макс. FPS)
GRAPHICS_PRESET = "normal"

def get_graphics_preset():
    return GRAPHICS_PRESET

def set_graphics_preset(preset):
    global GRAPHICS_PRESET
    if preset in ("normal", "optimized"):
        GRAPHICS_PRESET = preset

try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.set_num_channels(32)
except Exception:
    pass

# Принудительная привязка иконки к процессу Windows (панель задач)
if sys.platform == 'win32' and not IS_ANDROID:
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('cactustd.remastered.game.1.0')
    except Exception:
        pass

# Иконка окна приложения (кактус)
try:
    for _sub in ["assets/textures", "assets", "_internal/assets/textures", "_internal/assets", "."]:
        _app_ico = os.path.join(BASE_DIR, _sub, "app_icon.png")
        _png = os.path.join(BASE_DIR, _sub, "Cactus.png")
        if os.path.exists(_app_ico):
            pygame.display.set_icon(pygame.image.load(_app_ico))
            break
        elif os.path.exists(_png):
            pygame.display.set_icon(pygame.image.load(_png))
            break
except Exception:
    pass

pygame.display.set_caption("Cactus Tower Defense: Remastered")

# Установка нативных чётких иконок Win32 без интерполяционного мыла (заголовок + панель задач)
try:
    _hwnd = pygame.display.get_wm_info().get("window") if (sys.platform == 'win32' and not IS_ANDROID) else None
    if _hwnd:
        import ctypes
        _WM_SETICON = 0x0080
        _ICON_SMALL = 0
        _ICON_BIG = 1
        _IMAGE_ICON = 1
        _LR_LOADFROMFILE = 0x0010
        _LR_DEFAULTCOLOR = 0x0000

        _ico_p = None
        for _sub in ["assets", "_internal/assets", "."]:
            _cand = os.path.join(BASE_DIR, _sub, "icon.ico")
            if os.path.exists(_cand):
                _ico_p = _cand
                break

        _h_sm = None
        _h_bg = None
        if _ico_p:
            _h_sm = ctypes.windll.user32.LoadImageW(0, _ico_p, _IMAGE_ICON, 16, 16, _LR_LOADFROMFILE)
            _h_bg = ctypes.windll.user32.LoadImageW(0, _ico_p, _IMAGE_ICON, 32, 32, _LR_LOADFROMFILE)

        if not _h_sm or not _h_bg:
            _h_mod = ctypes.windll.kernel32.GetModuleHandleW(None)
            if not _h_sm:
                _h_sm = ctypes.windll.user32.LoadImageW(_h_mod, 1, _IMAGE_ICON, 16, 16, _LR_DEFAULTCOLOR)
            if not _h_bg:
                _h_bg = ctypes.windll.user32.LoadImageW(_h_mod, 1, _IMAGE_ICON, 32, 32, _LR_DEFAULTCOLOR)

        if _h_sm:
            ctypes.windll.user32.SendMessageW(_hwnd, _WM_SETICON, _ICON_SMALL, _h_sm)
        if _h_bg:
            ctypes.windll.user32.SendMessageW(_hwnd, _WM_SETICON, _ICON_BIG, _h_bg)

        # Неблокирующее перемещение окна за заголовок (игра не замирает при перетаскивании)
        from ctypes import wintypes
        _user32 = ctypes.windll.user32

        _WM_NCLBUTTONDOWN = 0x00A1
        _WM_LBUTTONUP = 0x0202
        _WM_MOUSEMOVE = 0x0200
        _WM_CAPTURECHANGED = 0x0215
        _HTCAPTION = 2
        _GWLP_WNDPROC = -4

        _WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
        _user32.CallWindowProcW.argtypes = [ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        _user32.CallWindowProcW.restype = ctypes.c_longlong

        _is_dragging = False
        _drag_mouse_origin = wintypes.POINT()
        _drag_win_origin = wintypes.RECT()
        _old_wndproc = None

        def _smooth_drag_wndproc(h, msg, wp, lp):
            global _is_dragging
            if msg == _WM_NCLBUTTONDOWN and wp == _HTCAPTION:
                _user32.GetCursorPos(ctypes.byref(_drag_mouse_origin))
                _user32.GetWindowRect(h, ctypes.byref(_drag_win_origin))
                _user32.SetCapture(h)
                _is_dragging = True
                return 0
            elif msg == _WM_MOUSEMOVE and _is_dragging:
                cur = wintypes.POINT()
                _user32.GetCursorPos(ctypes.byref(cur))
                dx = cur.x - _drag_mouse_origin.x
                dy = cur.y - _drag_mouse_origin.y
                _user32.SetWindowPos(h, 0, _drag_win_origin.left + dx, _drag_win_origin.top + dy, 0, 0, 0x0015)
                return 0
            elif msg in (_WM_LBUTTONUP, _WM_CAPTURECHANGED) and _is_dragging:
                _is_dragging = False
                _user32.ReleaseCapture()
                return 0
            return _user32.CallWindowProcW(_old_wndproc, h, msg, wp, lp)

        _c_wndproc = _WNDPROC(_smooth_drag_wndproc)
        _GetWindowLongPtr = _user32.GetWindowLongPtrW
        _SetWindowLongPtr = _user32.SetWindowLongPtrW
        _GetWindowLongPtr.restype = ctypes.c_void_p
        _SetWindowLongPtr.restype = ctypes.c_void_p
        _SetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]

        _old_wndproc = _GetWindowLongPtr(_hwnd, _GWLP_WNDPROC)
        _SetWindowLongPtr(_hwnd, _GWLP_WNDPROC, ctypes.cast(_c_wndproc, ctypes.c_void_p))
except Exception:
    pass

clock = pygame.time.Clock()
FPS = 60

# -------------------------------------------------------------------------
# ЦВЕТОВАЯ ПАЛИТРА
# -------------------------------------------------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (235, 60, 60)
GREEN = (60, 215, 85)
DARK_GREEN = (25, 110, 45)
BLUE = (60, 130, 240)
LIGHT_BLUE = (120, 190, 255)
GRAY = (110, 120, 135)
DARK_GRAY = (35, 42, 54)
LIGHT_GRAY = (200, 210, 225)
YELLOW = (255, 220, 60)
ORANGE = (255, 140, 40)
GOLD = (255, 215, 0)
PURPLE = (175, 75, 245)
CYAN = (70, 225, 230)

BG_GRID_A = (155, 190, 155)
BG_GRID_B = (175, 208, 175)

# -------------------------------------------------------------------------
# ШРИФТЫ
# -------------------------------------------------------------------------
pygame.font.init()

class CachedFont:
    """Обертка над шрифтом Pygame с быстрым кэшированием отрендеренного текста."""
    def __init__(self, font_obj):
        self._font = font_obj
        self._cache = {}
        self._limit = 2500

    def render(self, text, antialias, color, background=None):
        if isinstance(text, str) and len(text) < 120:
            c_val = tuple(color) if hasattr(color, '__iter__') else color
            bg_val = tuple(background) if hasattr(background, '__iter__') and background is not None else background
            key = (text, bool(antialias), c_val, bg_val)
            surf = self._cache.get(key)
            if surf is not None:
                return surf
            surf = self._font.render(text, antialias, color, background)
            if len(self._cache) >= self._limit:
                self._cache.clear()
            self._cache[key] = surf
            return surf
        return self._font.render(text, antialias, color, background)

    def size(self, text):
        return self._font.size(text)

    def get_height(self):
        return self._font.get_height()

    def get_linesize(self):
        return self._font.get_linesize()

    def set_bold(self, val):
        if hasattr(self._font, 'set_bold'):
            self._font.set_bold(val)

    def __getattr__(self, name):
        return getattr(self._font, name)

def _create_font(size, bold=True):
    raw_font = None
    if IS_ANDROID:
        for path in [
            "/system/fonts/RobotoStatic-Regular.ttf",
            "/system/fonts/Roboto-Regular.ttf",
            "/system/fonts/MiSansVF.ttf",
            "/system/fonts/DroidSans.ttf",
        ]:
            if os.path.exists(path):
                try:
                    f = pygame.font.Font(path, size)
                    if bold and hasattr(f, 'set_bold'):
                        f.set_bold(True)
                    raw_font = f
                    break
                except Exception:
                    pass
    if raw_font is None:
        font_name = 'Arial'
        try:
            raw_font = pygame.font.SysFont(font_name, size, bold=bold)
        except Exception:
            raw_font = pygame.font.Font(None, size)

    return CachedFont(raw_font)

massive_font = _create_font(56, bold=True)
large_font = _create_font(34, bold=True)
font = _create_font(21, bold=True)
small_font = _create_font(15, bold=True)
tiny_font = _create_font(12, bold=True)
nav_font = _create_font(14, bold=True)

# -------------------------------------------------------------------------
# ЗАГРУЗКА И ПОДГОТОВКА ТЕКСТУР
# -------------------------------------------------------------------------
def load_texture(filename, target_size=None):
    for sub in ["assets/textures", "_internal/assets/textures", "."]:
        p = os.path.join(BASE_DIR, sub, filename)
        if os.path.exists(p):
            try:
                img = pygame.image.load(p).convert_alpha()
                if target_size:
                    img = pygame.transform.smoothscale(img, target_size)
                return img
            except Exception as e:
                print(f"Failed loading {filename}: {e}")
    s = pygame.Surface(target_size or (32, 32), pygame.SRCALPHA)
    return s

# Кактусы и валюта
cactus_img = load_texture("Cactus.png", target_size=(44, 44))
cactus_img_xl = load_texture("Cactus.png", target_size=(112, 112))
cactus_img_s = load_texture("Cactus.png", target_size=(22, 22))
stellar_cactus_img = load_texture("Stellar_Cactus.png", target_size=(48, 48))
stellar_cactus_img_m = load_texture("Stellar_Cactus.png", target_size=(36, 36))
stellar_cactus_img_s = load_texture("Stellar_Cactus.png", target_size=(24, 24))
stellar_cactus_img_xs = load_texture("Stellar_Cactus.png", target_size=(18, 18))
dark_cactus_img = load_texture("Dark_Cactus.png", target_size=(48, 48))
dark_cactus_img_m = load_texture("Dark_Cactus.png", target_size=(36, 36))
dark_cactus_img_s = load_texture("Dark_Cactus.png", target_size=(24, 24))
dark_cactus_img_xs = load_texture("Dark_Cactus.png", target_size=(18, 18))

# Статический оверлей паузы (во избежание аллокаций 3.68 МБ каждый кадр)
pause_overlay_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
pause_overlay_surf.fill((0, 0, 0, 160))

# Астральный метеорит
meteorite_img = pygame.Surface((52, 52), pygame.SRCALPHA)
pygame.draw.circle(meteorite_img, (40, 26, 56), (26, 26), 22)
pygame.draw.polygon(meteorite_img, (75, 45, 105), [(26, 6), (42, 14), (46, 32), (34, 46), (18, 46), (6, 32), (10, 14)])
pygame.draw.polygon(meteorite_img, (180, 70, 255), [(26, 6), (42, 14), (46, 32), (34, 46), (18, 46), (6, 32), (10, 14)], width=2)
pygame.draw.circle(meteorite_img, (225, 130, 255), (26, 26), 11)
pygame.draw.circle(meteorite_img, (255, 235, 160), (24, 23), 5)
pygame.draw.circle(meteorite_img, WHITE, (23, 21), 2)

# Башни
magic_tower_img = load_texture("magic_tower.png", target_size=(60, 60))
rock_tower_img = load_texture("rock_tower.png", target_size=(60, 60))
freeze_tower_img = load_texture("freeze_tower.png", target_size=(60, 60))
tent_tower_img = load_texture("tent_tower.png", target_size=(60, 60))
tesla_tower_img = load_texture("tesla_tower.png", target_size=(60, 60))
farm_tower_img = load_texture("farm_tower.png", target_size=(60, 60))
soldier_img = load_texture("soldier.png", target_size=(34, 34))
slot_img = load_texture("slot.png", target_size=(44, 44))

# Слаймы
mob1_img = load_texture("mob1.png", target_size=(38, 38))
mob2_img = load_texture("mob2.png", target_size=(42, 42))
mob3_img = load_texture("mob3.png", target_size=(46, 46))
mob4_img = load_texture("mob4.png", target_size=(40, 40))
mob5_img = load_texture("mob5.png", target_size=(44, 44))
mob6_img = load_texture("mob6.png", target_size=(42, 42))
mob7_img = load_texture("tiger_slime.png", target_size=(44, 44))       # Тигровый слайм (рывок)
mob8_img = load_texture("frost_jelly.png", target_size=(44, 44))       # Ледяное желе (иммунитет к льду)
mob9_img = load_texture("stacked_slimes.png", target_size=(44, 60))    # Слаймовая пирамида (раскол)
mob10_img = load_texture("black_slime.png", target_size=(44, 44))      # Теневой слайм (антимагия)
gold_slime_img = load_texture("gold_slime.png", target_size=(46, 46))
# Официальные текстуры 4 Больших Слаймов из Stardew Valley Wiki (Green, Blue, Red, Purple)
boss_img = load_texture("big_green_slime.png", target_size=(80, 80)) # Босс 25 волны (Зелёный Большой Слизень)
if boss_img.get_at((40, 40))[3] == 0:
    boss_img = load_texture("big_slime.png", target_size=(80, 80))
colossus_boss_img = load_texture("big_blue_slime.png", target_size=(84, 84)) # Босс 50 волны (Синий Большой Слизень)
void_boss_img = load_texture("big_red_slime.png", target_size=(88, 88)) # Босс 75 волны (Красный Большой Слизень)
void_lord_boss_img = load_texture("big_purple_slime.png", target_size=(96, 96)) # Босс 100 волны (Фиолетовый Большой Слизень)

# Иконка ростка / саженца для Оранжереи
def _create_sprout_icon(sz):
    s = pygame.Surface((sz, sz), pygame.SRCALPHA)
    hs = sz // 2
    # Терракотовый горшочек
    pygame.draw.polygon(s, (195, 95, 50), [(hs - 5, sz - 3), (hs + 5, sz - 3), (hs + 4, sz), (hs - 4, sz)])
    pygame.draw.rect(s, (220, 120, 70), (hs - 6, sz - 5, 12, 3), border_radius=1)
    # Зелёные листики ростка
    pygame.draw.ellipse(s, (60, 200, 85), (hs - 6, 2, 7, 9))
    pygame.draw.ellipse(s, (95, 235, 120), (hs, 3, 7, 8))
    return s

sprout_icon = _create_sprout_icon(22)
sprout_icon_s = _create_sprout_icon(16)
greenhouse_icon = load_texture("greenhouse_icon.png", target_size=(64, 64))

# Иконка лопаты / археологии
def _create_shovel_icon(sz):
    s = pygame.Surface((sz, sz), pygame.SRCALPHA)
    # Черенок лопаты (дерево)
    pygame.draw.line(s, (180, 130, 75), (sz - 5, 5), (sz // 2 - 2, sz // 2 + 2), max(2, sz // 10))
    # Рукоять
    pygame.draw.circle(s, (210, 160, 95), (sz - 4, 4), max(2, sz // 8), width=2)
    # Металлическое лезвие штыка
    blade_pts = [(sz // 2 - 1, sz // 2 + 1), (sz // 3, sz - 6), (5, sz - 3), (3, sz - 5), (6, sz // 3)]
    pygame.draw.polygon(s, (175, 190, 205), blade_pts)
    pygame.draw.polygon(s, (225, 235, 245), blade_pts, width=1)
    return s

shovel_icon = _create_shovel_icon(46)
shovel_icon_s = _create_shovel_icon(22)
relic_icon = load_texture("trophy_icon.png", target_size=(46, 46))
relic_icon_s = load_texture("trophy_icon.png", target_size=(24, 24))

# Текстуры кактусов Оранжереи
gh_cacti_textures = {
    "gh_saguaro": load_texture(os.path.join("greenhouse", "gh_saguaro.png"), target_size=(64, 64)),
    "gh_opuntia": load_texture(os.path.join("greenhouse", "gh_opuntia.png"), target_size=(64, 64)),
    "gh_fire_barrel": load_texture(os.path.join("greenhouse", "gh_fire_barrel.png"), target_size=(64, 64)),
    "gh_frost_aloe": load_texture(os.path.join("greenhouse", "gh_frost_aloe.png"), target_size=(64, 64)),
    "gh_thunder_echino": load_texture(os.path.join("greenhouse", "gh_thunder_echino.png"), target_size=(64, 64)),
    "gh_void_astrophytum": load_texture(os.path.join("greenhouse", "gh_void_astrophytum.png"), target_size=(64, 64)),
    "gh_stellar_queen": load_texture(os.path.join("greenhouse", "gh_stellar_queen.png"), target_size=(64, 64)),
    "gh_mammillaria": load_texture(os.path.join("greenhouse", "gh_mammillaria.png"), target_size=(64, 64)),
}

# Текстуры UI иконки
star_icon = load_texture("star_icon.png", target_size=(20, 20))
star_icon_s = load_texture("star_icon.png", target_size=(16, 16))
sword_icon = load_texture("sword_icon.png", target_size=(22, 22))
lock_icon = load_texture("lock_icon.png", target_size=(16, 16))
trophy_icon = load_texture("trophy_icon.png", target_size=(24, 24))

def _create_gear_icon(sz):
    s = pygame.Surface((sz, sz), pygame.SRCALPHA)
    hs = sz // 2
    pygame.draw.circle(s, (190, 220, 255), (hs, hs), max(2, hs - 2), width=2)
    pygame.draw.circle(s, (190, 220, 255), (hs, hs), max(1, hs // 3))
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        x1 = hs + math.cos(rad) * max(1, hs - 5)
        y1 = hs + math.sin(rad) * max(1, hs - 5)
        x2 = hs + math.cos(rad) * hs
        y2 = hs + math.sin(rad) * hs
        pygame.draw.line(s, (190, 220, 255), (int(x1), int(y1)), (int(x2), int(y2)), 2)
    return s

gear_icon = _create_gear_icon(20)

def _create_info_icon_fallback(sz):
    s = pygame.Surface((sz, sz), pygame.SRCALPHA)
    hs = sz // 2
    pygame.draw.circle(s, (16, 36, 62), (hs, hs), hs - 1)
    pygame.draw.circle(s, (70, 200, 255), (hs, hs), hs - 1, width=2)
    pygame.draw.circle(s, WHITE, (hs, max(3, int(sz * 0.28))), max(1, int(sz * 0.1)))
    sw = max(2, int(sz * 0.16))
    sh = max(4, int(sz * 0.36))
    pygame.draw.rect(s, WHITE, (hs - sw // 2, int(sz * 0.44), sw, sh), border_radius=1)
    return s

info_icon = load_texture("info_icon.png", target_size=(22, 22))
if info_icon.get_at((11, 11))[3] == 0:
    info_icon = _create_info_icon_fallback(22)

info_icon_s = load_texture("info_icon.png", target_size=(16, 16))
if info_icon_s.get_at((8, 8))[3] == 0:
    info_icon_s = _create_info_icon_fallback(16)

upgrade_dock_icon = load_texture("upgrade_dock_icon.png", target_size=(32, 32))
speed_upg_icon = load_texture("speed_upg_icon.png", target_size=(46, 46))
crown_upg_icon = load_texture("crown_upg_icon.png", target_size=(46, 46))
crown_upg_icon_s = load_texture("crown_upg_icon.png", target_size=(32, 32))
wave_upg_icon = load_texture("wave_upg_icon.png", target_size=(46, 46))
start_lvl_icon = load_texture("start_lvl_icon.png", target_size=(46, 46))
start_cacti_icon = load_texture("start_cacti_icon.png", target_size=(46, 46))
bounty_upg_icon = load_texture("bounty_upg_icon.png", target_size=(46, 46))
damage_upg_icon = load_texture("damage_upg_icon.png", target_size=(46, 46))
health_upg_icon = load_texture("health_upg_icon.png", target_size=(46, 46))
magnet_upg_icon = load_texture("magnet_upg_icon.png", target_size=(46, 46))

def _create_shovel_icon(sz):
    s = pygame.Surface((sz, sz), pygame.SRCALPHA)
    pygame.draw.line(s, (150, 100, 50), (int(sz * 0.25), int(sz * 0.25)), (int(sz * 0.7), int(sz * 0.7)), max(2, sz // 8))
    pygame.draw.circle(s, (180, 120, 60), (int(sz * 0.25), int(sz * 0.25)), max(2, sz // 6), width=max(1, sz // 10))
    poly = [
        (int(sz * 0.55), int(sz * 0.75)),
        (int(sz * 0.75), int(sz * 0.55)),
        (int(sz * 0.88), int(sz * 0.75)),
        (int(sz * 0.75), int(sz * 0.88)),
    ]
    pygame.draw.polygon(s, (190, 200, 210), poly)
    pygame.draw.polygon(s, (130, 140, 155), poly, width=1)
    return s

def _create_relic_icon(sz):
    s = pygame.Surface((sz, sz), pygame.SRCALPHA)
    hs = sz // 2
    pygame.draw.circle(s, (255, 215, 80), (hs, hs), hs - 2, width=1)
    poly = [
        (hs - sz // 5, hs - sz // 3),
        (hs + sz // 5, hs - sz // 3),
        (hs + sz // 3, hs),
        (hs + sz // 6, hs + sz // 3),
        (hs - sz // 6, hs + sz // 3),
        (hs - sz // 3, hs),
    ]
    pygame.draw.polygon(s, (240, 185, 45), poly)
    pygame.draw.polygon(s, (160, 115, 20), poly, width=1)
    pygame.draw.circle(s, (60, 220, 255), (hs, hs - 2), max(1, sz // 8))
    return s

shovel_icon = _create_shovel_icon(24)
shovel_icon_s = _create_shovel_icon(18)
relic_icon = _create_relic_icon(24)
relic_icon_s = _create_relic_icon(18)

# Сердечко жизней
heart_img = pygame.Surface((34, 28), pygame.SRCALPHA)
pygame.draw.polygon(heart_img, (235, 45, 65), [(17, 26), (4, 13), (4, 6), (10, 2), (17, 7), (24, 2), (30, 6), (30, 13)])
pygame.draw.polygon(heart_img, (140, 15, 25), [(17, 26), (4, 13), (4, 6), (10, 2), (17, 7), (24, 2), (30, 6), (30, 13)], width=2)
pygame.draw.ellipse(heart_img, (255, 170, 185), (7, 6, 7, 5))

# Снаряды
def create_bullet_surf(color, core_color):
    s = pygame.Surface((18, 18), pygame.SRCALPHA)
    pygame.draw.circle(s, color, (9, 9), 8)
    pygame.draw.circle(s, core_color, (9, 9), 4)
    pygame.draw.circle(s, WHITE, (8, 8), 2)
    return s

bullet_img = create_bullet_surf((170, 70, 240), (240, 160, 255))
earth_ball_img = create_bullet_surf((240, 70, 20), (255, 200, 60))
frost_ball_img = create_bullet_surf((60, 170, 250), (190, 240, 255))

# -------------------------------------------------------------------------
# ЗВУКОВОЙ ДВИЖОК И САУНДТРЕКИ
# -------------------------------------------------------------------------
class SoundDummy:
    def play(self, *args, **kwargs): return None
    def set_volume(self, *args, **kwargs): pass

class ManagedSound:
    """
    Интеллектуальный менеджер звуковых эффектов:
    1. Предотвращает звуковой хаос и перегрузку каналов при высокой скорости игры и толпах мобов.
    2. Ограничивает минимальный интервал между вызовами одного и того же звука (realtime cooldown).
    3. Ограничивает количество одновременно звучащих копий (polyphony limiting), предотвращая клиппинг.
    """
    def __init__(self, sound, min_interval_ms=75, max_polyphony=2, default_vol=1.0):
        self.sound = sound
        self.min_interval_ms = min_interval_ms
        self.max_polyphony = max_polyphony
        self.last_played = -99999
        self.active_channels = []
        if hasattr(self.sound, 'set_volume'):
            self.sound.set_volume(default_vol)

    def play(self, *args, **kwargs):
        try:
            now = pygame.time.get_ticks()
            if now - self.last_played < self.min_interval_ms:
                return None

            # Очистка завершившихся каналов
            self.active_channels = [ch for ch in self.active_channels if ch.get_busy()]
            if len(self.active_channels) >= self.max_polyphony:
                return None

            self.last_played = now
            if hasattr(self.sound, 'play'):
                ch = self.sound.play(*args, **kwargs)
                if ch:
                    self.active_channels.append(ch)
                return ch
        except Exception:
            pass
        return None

    def set_volume(self, vol):
        if hasattr(self.sound, 'set_volume'):
            self.sound.set_volume(vol)

def safe_load_sound(rel_path, vol=0.25):
    for sub in ["assets/sounds", "_internal/assets/sounds", "."]:
        p = os.path.join(BASE_DIR, sub, rel_path)
        if os.path.exists(p):
            try:
                snd = pygame.mixer.Sound(p)
                snd.set_volume(vol)
                return snd
            except Exception:
                pass
    return SoundDummy()

def synthesize_sound(notes, wave_type='warm', master_vol=0.14):
    """
    Создает мягкие, чистые и гармоничные звуковые эффекты (44100 Гц)
    с естественным экспоненциальным затуханием без щелчков и перегрузок.
    """
    try:
        if not pygame.mixer.get_init():
            return SoundDummy()
        buf = io.BytesIO()
        sample_rate = 44100
        with wave.open(buf, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sample_rate)
            frames = []
            for freq, dur, vol in notes:
                n_frames = int(sample_rate * dur)
                attack_frames = int(min(0.008 * sample_rate, n_frames * 0.15))
                for i in range(n_frames):
                    t = i / sample_rate
                    # Мягкая атака для устранения щелчка
                    if i < attack_frames:
                        env_attack = 0.5 * (1.0 - math.cos(math.pi * i / attack_frames))
                    else:
                        env_attack = 1.0

                    # Естественное экспоненциальное затухание
                    decay_progress = i / n_frames
                    env_decay = math.exp(-3.2 * decay_progress)
                    env = env_attack * env_decay

                    if wave_type == 'warm':
                        # Тёплый округлый тембр (основной тон + мягкие 2 и 3 гармоники)
                        raw = (0.75 * math.sin(2 * math.pi * freq * t) +
                               0.18 * math.sin(4 * math.pi * freq * t) +
                               0.07 * math.sin(6 * math.pi * freq * t))
                    elif wave_type == 'chime':
                        # Кристальный колокольчик
                        raw = (0.70 * math.sin(2 * math.pi * freq * t) +
                               0.22 * math.sin(5.5 * math.pi * freq * t) +
                               0.08 * math.sin(8.2 * math.pi * freq * t))
                    elif wave_type == 'thud':
                        # Мягкий басовый глухой удар (падающая частота)
                        inst_freq = max(35.0, freq * math.exp(-12.0 * t))
                        raw = 0.85 * math.sin(2 * math.pi * inst_freq * t) + 0.15 * math.sin(4 * math.pi * inst_freq * t)
                    elif wave_type == 'soft_zap':
                        # Мягкий высокотехнологичный искровой разряд без треска
                        mod = math.sin(2 * math.pi * 38.0 * t) * (freq * 0.35)
                        raw = 0.80 * math.sin(2 * math.pi * (freq + mod) * t) + 0.20 * math.sin(4 * math.pi * (freq + mod) * t)
                    elif wave_type == 'click':
                        raw = math.sin(2 * math.pi * freq * t)
                    else:
                        raw = math.sin(2 * math.pi * freq * t)

                    val = int(32767 * master_vol * vol * env * raw)
                    val = max(-32767, min(32767, val))
                    frames.append(struct.pack('<h', val))
            w.writeframes(b''.join(frames))
        buf.seek(0)
        return pygame.mixer.Sound(buf)
    except Exception:
        return SoundDummy()

# Тактильные, сбалансированные звуковые эффекты с ограничением частоты срабатывания:
sfx_click = ManagedSound(synthesize_sound([(760, 0.016, 1.0)], wave_type='click', master_vol=0.08), min_interval_ms=45, max_polyphony=2)
sfx_upgrade = ManagedSound(synthesize_sound([(523, 0.05, 0.9), (659, 0.05, 0.9), (784, 0.05, 1.0), (1046, 0.12, 1.0)], wave_type='warm', master_vol=0.14), min_interval_ms=75, max_polyphony=2)
sfx_sell = ManagedSound(synthesize_sound([(659, 0.05, 0.9), (523, 0.09, 1.0)], wave_type='warm', master_vol=0.12), min_interval_ms=75, max_polyphony=2)
sfx_star = ManagedSound(synthesize_sound([(1175, 0.04, 0.8), (1568, 0.08, 1.0)], wave_type='chime', master_vol=0.11), min_interval_ms=100, max_polyphony=2)
sfx_combo = ManagedSound(synthesize_sound([(170, 0.07, 1.0)], wave_type='thud', master_vol=0.10), min_interval_ms=110, max_polyphony=2)
sfx_tesla = ManagedSound(synthesize_sound([(680, 0.05, 0.9), (520, 0.04, 0.8)], wave_type='soft_zap', master_vol=0.09), min_interval_ms=90, max_polyphony=2)
sfx_heal = ManagedSound(synthesize_sound([(659, 0.05, 0.8), (880, 0.08, 1.0)], wave_type='chime', master_vol=0.09), min_interval_ms=250, max_polyphony=1)
sfx_boss_defeat = ManagedSound(synthesize_sound([(140, 0.12, 1.0), (90, 0.16, 1.0), (55, 0.25, 0.9)], wave_type='thud', master_vol=0.20), min_interval_ms=300, max_polyphony=1)
sfx_achievement = ManagedSound(synthesize_sound([(392, 0.06, 0.8), (523, 0.06, 0.9), (659, 0.06, 0.9), (784, 0.07, 1.0), (1046, 0.20, 1.0)], wave_type='warm', master_vol=0.15), min_interval_ms=200, max_polyphony=1)
sfx_boss_alarm = ManagedSound(synthesize_sound([(240, 0.16, 1.0), (180, 0.18, 1.0), (120, 0.35, 1.0)], wave_type='thud', master_vol=0.22), min_interval_ms=900, max_polyphony=1)
sfx_mortar_shot = ManagedSound(synthesize_sound([(130, 0.08, 1.0), (75, 0.14, 0.9)], wave_type='thud', master_vol=0.15), min_interval_ms=75, max_polyphony=3)
sfx_freeze_shot = ManagedSound(synthesize_sound([(1480, 0.04, 0.8), (1760, 0.06, 0.9), (2200, 0.08, 0.7)], wave_type='chime', master_vol=0.10), min_interval_ms=80, max_polyphony=3)
sfx_sprout_pickup = ManagedSound(synthesize_sound([(880, 0.04, 0.8), (1318, 0.08, 1.0)], wave_type='chime', master_vol=0.13), min_interval_ms=50, max_polyphony=3)
sfx_sprout_collect = sfx_sprout_pickup
sfx_dig_hit = ManagedSound(synthesize_sound([(520, 0.04, 0.9), (780, 0.07, 1.0)], wave_type='warm', master_vol=0.14), min_interval_ms=60, max_polyphony=2)
sfx_dig_miss = ManagedSound(synthesize_sound([(120, 0.06, 1.0), (80, 0.08, 0.8)], wave_type='thud', master_vol=0.11), min_interval_ms=60, max_polyphony=2)
sfx_relic_found = ManagedSound(synthesize_sound([(440, 0.08, 0.8), (554, 0.08, 0.9), (659, 0.08, 0.9), (880, 0.25, 1.0)], wave_type='chime', master_vol=0.18), min_interval_ms=250, max_polyphony=1)

raw_tower_built = safe_load_sound("mixkit-video-game-treasure-2066.wav", 0.14)
if isinstance(raw_tower_built, SoundDummy):
    raw_tower_built = synthesize_sound([(440, 0.04, 0.9), (880, 0.06, 1.0)], wave_type='warm', master_vol=0.12)
tower_built = ManagedSound(raw_tower_built, min_interval_ms=60, max_polyphony=2)

raw_laser = safe_load_sound("laser.mp3", 0.10)
if isinstance(raw_laser, SoundDummy):
    raw_laser = synthesize_sound([(540, 0.03, 1.0)], wave_type='warm', master_vol=0.07)
laser = ManagedSound(raw_laser, min_interval_ms=75, max_polyphony=2)

ALL_MANAGED_SOUNDS = [
    sfx_click, sfx_upgrade, sfx_sell, sfx_star, sfx_combo,
    sfx_tesla, sfx_heal, sfx_boss_defeat, sfx_achievement,
    sfx_boss_alarm, sfx_mortar_shot, sfx_freeze_shot, sfx_sprout_pickup,
    sfx_dig_hit, sfx_dig_miss, sfx_relic_found,
    tower_built, laser
]
sfx_freeze = sfx_freeze_shot

current_music_volume = 0.5

def apply_audio_settings(sdata):
    global current_music_volume
    if not isinstance(sdata, dict): return
    sets = sdata.get("Settings", {})
    sfx_v = max(0.0, min(1.0, sets.get("sfx_volume", 0.7)))
    mus_v = max(0.0, min(1.0, sets.get("music_volume", 0.5)))
    current_music_volume = mus_v
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(mus_v)
    except Exception:
        pass
    for s in ALL_MANAGED_SOUNDS:
        s.set_volume(sfx_v)

# -------------------------------------------------------------------------
# БИОМЫ КАРТ
# -------------------------------------------------------------------------
MAP_BIOMES_DATA = {
    0: {
        "name": "Старт",
        "sub": "Базовая карта",
        "diff_stars": 1,
        "diff_label": "Легко",
        "diff_color": (80, 210, 90),
        "soundtrack": ("Normal Realm", "main_music.ogg"),
        "bg_col_a": (155, 195, 155),
        "bg_col_b": (175, 215, 175),
        "road_col": (125, 110, 85),
        "road_border": (85, 70, 50),
        "particle_type": "pollen",
        "mutator_title": "Бонус старта",
        "mutator_badge": "+10% кактусов на старте",
        "mutator_desc": "+10% стартовых кактусов на защиту.",
        "hp_mult": 1.0,
        "spd_mult": 1.0,
        "stellar_mult": 1.00,
        "cacti_mult": 1.0,
        "lore_desc": "Мирный цветущий луг оазиса. Идеальное место для изучения базовых башен и построения первой обороны.",
        "wave_schedule": [
            ("Волны 1–10", [1, 4]),
            ("Волны 11–20", [1, 2, 4]),
            ("Волны 21–35", [2, 3, 5, 6]),
            ("Волна 25+", [1000])
        ]
    },
    1: {
        "name": "Круговорот",
        "sub": "Снежная спираль",
        "diff_stars": 2,
        "diff_label": "Средне",
        "diff_color": (80, 180, 255),
        "soundtrack": ("In The Snow", "in_the_snow.ogg"),
        "bg_col_a": (175, 205, 230),
        "bg_col_b": (195, 225, 245),
        "road_col": (160, 185, 205),
        "road_border": (115, 140, 165),
        "particle_type": "snow",
        "mutator_title": "Ледяной шторм",
        "mutator_badge": "Мороз +15% | Мобы +8%",
        "mutator_desc": "Заморозка +15% дольше, но мобы на +8% быстрее и имеют +10% маг. щита.",
        "hp_mult": 1.15,
        "spd_mult": 1.08,
        "stellar_mult": 1.15,
        "cacti_mult": 1.0,
        "lore_desc": "Ледяное плато с закрученной тропой. Холодный ветер усиливает Ледяные башни, но закаляет слаймов.",
        "wave_schedule": [
            ("Волны 1–10", [1, 4]),
            ("Волны 11–20", [1, 2, 4, 5]),
            ("Волны 21–35", [2, 3, 5, 6, 7]),
            ("Волна 25+", [1000])
        ]
    },
    2: {
        "name": "Перекрёстки",
        "sub": "Двойная петля",
        "diff_stars": 3,
        "diff_label": "Сложно",
        "diff_color": (245, 180, 40),
        "soundtrack": ("Desert", "desert.ogg"),
        "bg_col_a": (225, 200, 145),
        "bg_col_b": (238, 215, 165),
        "road_col": (185, 150, 100),
        "road_border": (145, 115, 70),
        "particle_type": "sand",
        "mutator_title": "Песчаная буря",
        "mutator_badge": "Сплэш +15% | Дальность -10%",
        "mutator_desc": "Песок слепит башни (дальность -10%), мобы +10% быстрее, но сплэш огня шире на +15%.",
        "hp_mult": 1.35,
        "spd_mult": 1.10,
        "stellar_mult": 1.25,
        "cacti_mult": 1.10,
        "lore_desc": "Знойные пустынные перекрестки. Ветер раздувает взрывы, но песчаная взвесь ограничивает видимость.",
        "wave_schedule": [
            ("Волны 1–10", [1, 2, 4]),
            ("Волны 11–20", [2, 3, 5]),
            ("Волны 21–35", [3, 5, 6, 7, 777]),
            ("Волна 25+", [1000, 2000])
        ]
    },
    3: {
        "name": "Волны",
        "sub": "Волнистая трасса",
        "diff_stars": 3,
        "diff_label": "Сложно",
        "diff_color": (245, 80, 50),
        "soundtrack": ("Inferno Valley", "inferno.ogg"),
        "bg_col_a": (65, 30, 35),
        "bg_col_b": (85, 40, 45),
        "road_col": (140, 45, 30),
        "road_border": (90, 20, 15),
        "particle_type": "ember",
        "mutator_title": "Магматический зной",
        "mutator_badge": "Огнеупорность +20% | Урон +5%",
        "mutator_desc": "Мобы закалены магмой (+20% защиты от огня), урон башен +5%.",
        "hp_mult": 1.60,
        "spd_mult": 1.12,
        "stellar_mult": 1.38,
        "cacti_mult": 1.0,
        "lore_desc": "Лавовый разлом с волнообразным серпантином. Высокая температура закаляет слаймов, увеличивая их живучесть.",
        "wave_schedule": [
            ("Волны 1–14", [1, 2, 4, 5]),
            ("Волны 15–30", [2, 3, 5, 6, 7]),
            ("Волны 31–50", [3, 5, 6, 51, 52]),
            ("Волна 25/50", [1000, 2000])
        ]
    },
    4: {
        "name": "Змейка",
        "sub": "Длинный зигзаг",
        "diff_stars": 4,
        "diff_label": "Мастер",
        "diff_color": (175, 85, 245),
        "soundtrack": ("Anti Realm", "anti_realm.ogg"),
        "bg_col_a": (28, 22, 50),
        "bg_col_b": (40, 32, 70),
        "road_col": (75, 50, 115),
        "road_border": (48, 30, 80),
        "particle_type": "cosmic",
        "mutator_title": "Аномалия",
        "mutator_badge": "Тесла +10% | Скорость +15%",
        "mutator_desc": "Дальность Теслы +10%, но мобы на поворотах на +15% быстрее.",
        "hp_mult": 1.90,
        "spd_mult": 1.15,
        "stellar_mult": 1.50,
        "cacti_mult": 1.0,
        "lore_desc": "Глубокий космический зигзаг с 12 слотами под башни. Идеальный плацдарм для цепных молний Башни Тесла.",
        "wave_schedule": [
            ("Волны 1–14", [2, 4, 5]),
            ("Волны 15–35", [3, 5, 6, 7, 777]),
            ("Волны 36–50", [5, 6, 51, 52]),
            ("Волна 25/50", [1000, 2000])
        ]
    },
    5: {
        "name": "Атака",
        "sub": "Штурмовой коридор",
        "diff_stars": 4,
        "diff_label": "Мастер",
        "diff_color": (235, 45, 85),
        "soundtrack": ("Grassland", "grassland.ogg"),
        "bg_col_a": (20, 18, 26),
        "bg_col_b": (34, 28, 42),
        "road_col": (95, 30, 55),
        "road_border": (60, 15, 35),
        "particle_type": "eclipse",
        "mutator_title": "Штурмовой натиск",
        "mutator_badge": "Элита чаще | Скорость +18%",
        "mutator_desc": "Мобы на +18% быстрее, элита выходит чаще (+20% шанс), награда элиты +20%.",
        "hp_mult": 2.25,
        "spd_mult": 1.18,
        "stellar_mult": 1.62,
        "cacti_mult": 1.15,
        "lore_desc": "Прямолинейный коридор штурма с 13 слотами. Быстрые волны и яростные элитные бойцы приносят повышенную добычу.",
        "wave_schedule": [
            ("Волны 1–15", [2, 3, 4, 5]),
            ("Волны 16–35", [3, 5, 6, 7, 51]),
            ("Волны 36–50", [6, 51, 52, 53]),
            ("Волна 25/50", [1000, 2000])
        ]
    },
    6: {
        "name": "Лабиринт",
        "sub": "Коридоры и углы",
        "diff_stars": 5,
        "diff_label": "Эксперт",
        "diff_color": (60, 225, 215),
        "soundtrack": ("Synthesis", "synthesis.ogg"),
        "bg_col_a": (18, 32, 42),
        "bg_col_b": (26, 48, 62),
        "road_col": (45, 105, 125),
        "road_border": (25, 68, 85),
        "particle_type": "crystal",
        "mutator_title": "Кристальный панцирь",
        "mutator_badge": "Броня +2 | Криты +8%",
        "mutator_desc": "Мобы получают +2 брони и +20% антимагии; крит-шанс башен +8%.",
        "hp_mult": 2.70,
        "spd_mult": 1.20,
        "stellar_mult": 1.75,
        "cacti_mult": 1.20,
        "lore_desc": "Лазурные кристаллические залы. Стены лабиринта резонируют с магией, усиливая критические удары башен.",
        "wave_schedule": [
            ("Волны 1–15", [2, 3, 5, 6]),
            ("Волны 16–35", [3, 5, 6, 7, 51, 52]),
            ("Волны 36–50", [51, 52, 53]),
            ("Волна 25/50/75", [1000, 2000, 3000])
        ]
    },
    7: {
        "name": "Петля",
        "sub": "Двойной проход",
        "diff_stars": 5,
        "diff_label": "Хардкор",
        "diff_color": (185, 240, 50),
        "soundtrack": ("Loop Tower", "loop_tower.ogg"),
        "bg_col_a": (24, 30, 20),
        "bg_col_b": (36, 44, 28),
        "road_col": (65, 85, 38),
        "road_border": (40, 55, 24),
        "particle_type": "toxic",
        "mutator_title": "Токсичный раж",
        "mutator_badge": "Ярость при <50% HP | Броня -15%",
        "mutator_desc": "Мобы при потере половины HP ускоряются на +20%; броня мобов разъедена (-15%).",
        "hp_mult": 3.25,
        "spd_mult": 1.22,
        "stellar_mult": 1.88,
        "cacti_mult": 1.0,
        "lore_desc": "Закольцованные террасы, где слаймы дважды проходят мимо одних и тех же башен. Токсичные испарения разъедают броню.",
        "wave_schedule": [
            ("Волны 1–20", [3, 5, 6, 7]),
            ("Волны 21–40", [5, 6, 7, 51, 52]),
            ("Волны 41–60", [51, 52, 53]),
            ("Волна 25/50/75", [1000, 2000, 3000])
        ]
    },
    8: {
        "name": "Финал",
        "sub": "Большой круг",
        "diff_stars": 5,
        "diff_label": "Абсолют",
        "diff_color": (255, 215, 0),
        "soundtrack": ("Void", "void.ogg"),
        "bg_col_a": (20, 16, 28),
        "bg_col_b": (34, 26, 48),
        "road_col": (115, 88, 38),
        "road_border": (75, 55, 22),
        "particle_type": "astral",
        "mutator_title": "Натиск Бездны",
        "mutator_badge": "HP x4.00 | Скорость +25%",
        "mutator_desc": "Мобы на +25% быстрее, устойчивее ко всем стихиям (+20%) и несокрушимы (HP x4.00).",
        "hp_mult": 4.00,
        "spd_mult": 1.25,
        "stellar_mult": 2.00,
        "cacti_mult": 1.0,
        "lore_desc": "Вершина вселенной кактусов. Огромное золотое кольцо с 14 слотами. Выдержите ли вы натиск Владыки Бездны?",
        "wave_schedule": [
            ("Волны 1–20", [3, 5, 6, 7, 8, 9, 10, 51]),
            ("Волны 21–45", [5, 6, 7, 8, 9, 10, 51, 52, 53]),
            ("Волны 46–100+", [51, 52, 53, 7, 8, 9, 10]),
            ("Волна 25/50/75/100+", [1000, 2000, 3000, 4000])
        ]
    },
    9: {
        "name": "Генератор",
        "sub": "Оазис Создателя",
        "diff_stars": 5,
        "diff_label": "Песочница",
        "diff_color": (255, 120, 220),
        "soundtrack": ("Star Realm", "star_realm.ogg"),
        "bg_col_a": (28, 22, 40),
        "bg_col_b": (45, 34, 65),
        "road_col": (120, 95, 160),
        "road_border": (75, 55, 110),
        "particle_type": "astral",
        "mutator_title": "Свой режим",
        "mutator_badge": "Полная кастомизация",
        "mutator_desc": "Процедурный путь по сиду, настройка сложности и бесконечный штурм!",
        "hp_mult": 1.5,
        "spd_mult": 1.0,
        "stellar_mult": 1.00,
        "cacti_mult": 1.0,
        "lore_desc": "Мистический полигон после победы над Бездной. Меняйте законы вселенной, вводите сиды и создавайте свои испытания!",
        "wave_schedule": [
            ("Волны 1–20", [1, 2, 3, 4, 5]),
            ("Волны 21–50", [5, 6, 7, 8, 9, 10, 51]),
            ("Волны 51–100+", [51, 52, 53, 7, 8, 9, 10]),
            ("Боссы", [1000, 2000, 3000, 4000])
        ]
    }
}

MAP_SOUNDTRACKS = {i: data["soundtrack"] for i, data in MAP_BIOMES_DATA.items()}
MAP_NAMES_LIST = [data["name"] for i, data in MAP_BIOMES_DATA.items()]

MAP_UNLOCK_REQS = {
    0: None,
    1: (0, 15),
    2: (1, 20),
    3: (2, 25),
    4: (3, 30),
    5: (4, 35),
    6: (5, 40),
    7: (6, 45),
    8: (7, 50),
    9: (8, 100),
}

def get_map_mastery_milestones(mid=0):
    """
    Возвращает список рубежей мастерства (волна, награда звёздных кактусов, ранг) для карты.
    Рубежи: 10, 25, 50, 75 волн (фиксированная награда 10, 15, 20 и 30 кактусов независимо от карты).
    """
    waves = [10, 25, 50, 75]
    rews = [10, 15, 20, 30]
    ranks = ["Бронза", "Серебро", "Золото", "Алмаз"]
    return [(w, rew, rank) for w, rew, rank in zip(waves, rews, ranks)]

MASTERY_MILESTONES = get_map_mastery_milestones(0)
OLD_MASTERY_REWARDS = {10: 10, 25: 15, 50: 20, 75: 30}
NEW_MASTERY_REWARDS = {10: 10, 25: 15, 50: 20, 75: 30}

# -------------------------------------------------------------------------
# ПРОЦЕДУРНЫЙ ГЕНЕРАТОР КАРТ ДЛЯ КАРТЫ 10 («ОАЗИС СОЗДАТЕЛЯ»)
# -------------------------------------------------------------------------
def generate_custom_map_path_and_slots(seed_val):
    """
    Генерирует сбалансированный проходимый путь и слоты под башни по числовому сиду.
    """
    try:
        s_int = int(seed_val)
    except Exception:
        s_int = sum(ord(c) for c in str(seed_val)) if seed_val else 777
    rng = random.Random(s_int)
    style = rng.choice(['snake', 'zigzag', 'sine', 'corners'])
    waypoints = [(0, rng.randint(220, 480))]

    if style == 'snake':
        cols = [rng.randint(180, 250), rng.randint(430, 500), rng.randint(680, 750), rng.randint(930, 990)]
        cur_y = waypoints[0][1]
        for idx, cx in enumerate(cols):
            target_y = 150 if (idx % 2 == 0) else 550
            waypoints.append((cx, cur_y))
            waypoints.append((cx, target_y))
            cur_y = target_y
        waypoints.append((1280, cur_y))
    elif style == 'sine':
        freq = rng.uniform(0.007, 0.012)
        amp = rng.uniform(110, 190)
        mid_y = rng.randint(330, 390)
        phase = rng.uniform(0, 3.14)
        for x in range(0, 1281, 40):
            y = int(mid_y + amp * math.sin(x * freq + phase))
            y = max(140, min(580, y))
            waypoints.append((x, y))
    elif style == 'zigzag':
        waypoints = [
            (0, 200), (rng.randint(240, 380), 200), (rng.randint(240, 380), 540),
            (rng.randint(560, 690), 540), (rng.randint(560, 690), 190),
            (rng.randint(860, 990), 190), (rng.randint(860, 990), 510), (1280, 510)
        ]
    else:
        waypoints = [
            (0, 360), (rng.randint(200, 300), 360), (rng.randint(200, 300), 150),
            (rng.randint(540, 660), 150), (rng.randint(540, 660), 560),
            (rng.randint(890, 1000), 560), (rng.randint(890, 1000), 360), (1280, 360)
        ]

    # Генерация слотов вокруг дороги
    slots = []
    def dist_to_segment(p, a, b):
        px, py = p; ax, ay = a; bx, by = b
        dx = bx - ax; dy = by - ay
        if dx == 0 and dy == 0: return math.hypot(px - ax, py - ay)
        t = max(0.0, min(1.0, ((px - ax)*dx + (py - ay)*dy) / (dx*dx + dy*dy)))
        return math.hypot(px - (ax + t*dx), py - (ay + t*dy))

    def min_dist_to_path(p):
        d = 999999
        for i in range(len(waypoints)-1):
            d = min(d, dist_to_segment(p, waypoints[i], waypoints[i+1]))
        return d

    candidates = []
    for i in range(len(waypoints)-1):
        ax, ay = waypoints[i]
        bx, by = waypoints[i+1]
        mx, my = (ax + bx)//2, (ay + by)//2
        dx, dy = bx - ax, by - ay
        leng = math.hypot(dx, dy)
        if leng > 1e-4:
            nx, ny = -dy / leng, dx / leng
            for offset in [80, -80]:
                sx = int(mx + nx * offset)
                sy = int(my + ny * offset)
                candidates.append((sx, sy))

    for gx in range(120, 1030, 85):
        for gy in range(130, 600, 85):
            candidates.append((gx + rng.randint(-12, 12), gy + rng.randint(-12, 12)))

    rng.shuffle(candidates)
    for cx, cy in candidates:
        if 80 <= cx <= 1020 and 110 <= cy <= 610:
            if 60 <= min_dist_to_path((cx, cy)) <= 150:
                if all(math.hypot(cx - sx, cy - sy) >= 80 for sx, sy in slots):
                    slots.append((cx, cy))
                    if len(slots) >= 14:
                        break

    if len(slots) < 10:
        # Резервные слоты, если сид плотный
        for rx, ry in [(180, 140), (320, 480), (520, 220), (680, 480), (840, 200), (980, 480), (450, 360), (750, 360), (220, 320), (920, 320)]:
            if all(math.hypot(rx - sx, ry - sy) >= 70 for sx, sy in slots):
                slots.append((rx, ry))

    return waypoints, slots

_init_p9, _init_s9 = generate_custom_map_path_and_slots(777)

# -------------------------------------------------------------------------
# ПУТИ И СЛОТЫ КАРТ
# -------------------------------------------------------------------------
path_list = [
    # 0: Старт
    [
        (0, 360), (100, 360), (100, 100), (600, 100),
        (600, 500), (1100, 500), (1100, 360), (1280, 360)
    ],
    # 1: Круговорот
    [
        (0, 300), (100, 300), (100, 100), (1000, 100), (1000, 250), (600, 250),
        (600, 400), (1000, 400), (1000, 550), (100, 550), (100, 350), (0, 350)
    ],
    # 2: Перекрёстки
    [
        (0, 450), (600, 450), (600, 100), (300, 100), (300, 350),
        (1000, 350), (1000, 100), (700, 100), (700, 450), (1280, 450)
    ],
    # 3: Волны
    [
        (i * 5, int(math.sin(i / 10) * 75 + 360)) for i in range(257)
    ],
    # 4: Змейка
    [
        (0, 160), (300, 160), (300, 540), (620, 540), (620, 180), (940, 180), (940, 520), (1280, 520)
    ],
    # 5: Атака
    [
        (0, 140), (420, 140), (420, 360), (220, 360), (220, 580), (860, 580), (860, 340), (640, 340), (640, 200), (1120, 200), (1120, 460), (1280, 460)
    ],
    # 6: Лабиринт
    [
        (0, 240), (260, 240), (260, 480), (520, 480), (520, 180), (780, 180), (780, 480), (1040, 480), (1040, 300), (1280, 300)
    ],
    # 7: Петля
    [
        (0, 500), (240, 500), (240, 220), (500, 220), (500, 500), (760, 500), (760, 220), (1020, 220), (1020, 500), (1280, 500)
    ],
    # 8: Финал
    [
        (0, 360), (180, 360), (180, 140), (560, 140), (560, 560), (820, 560), (820, 140), (1100, 140), (1100, 360), (940, 360), (940, 480), (360, 480), (360, 240), (1280, 240)
    ],
    # 9: Генератор (Карта 10)
    _init_p9
]

tower_slots_list = [
    # 0: Старт
    [
        (200, 150), (500, 150), (700, 250), (1000, 250),
        (150, 250), (550, 250), (650, 350), (1050, 350),
        (200, 350), (500, 350), (700, 450), (1000, 450)
    ],
    # 1: Круговорот
    [
        (150, 325), (150, 150), (550, 150), (950, 150), (950, 200), (650, 300), (650, 350), (950, 450), (950, 500),
        (550, 500), (150, 500)
    ],
    # 2: Перекрёстки
    [
        (200, 400), (450, 225), (850, 225), (1100, 400),
        (650, 200), (650, 400), (350, 400), (950, 400)
    ],
    # 3: Волны
    [
        (78.5 * i, 360) for i in range(1, 16, 2)
    ],
    # 4: Змейка (12 слотов)
    [
        (160, 250), (160, 450), (460, 260), (460, 440), (460, 350), (780, 260), (780, 440), (780, 350),
        (1110, 260), (1110, 440), (160, 350), (1110, 350)
    ],
    # 5: Атака (13 слотов)
    [
        (100, 250), (100, 460), (320, 250), (520, 250), (340, 470), (540, 470), (740, 470), (530, 140),
        (750, 250), (990, 270), (990, 470), (1220, 330), (1220, 560)
    ],
    # 6: Лабиринт (12 слотов)
    [
        (140, 360), (390, 260), (390, 400), (390, 560), (650, 260), (650, 400), (650, 560), (910, 260),
        (910, 400), (910, 560), (1160, 400), (1160, 220)
    ],
    # 7: Петля (13 слотов)
    [
        (120, 360), (370, 360), (370, 590), (370, 130), (630, 360), (630, 590), (630, 130), (890, 360),
        (890, 590), (890, 130), (1150, 360), (1150, 220), (120, 220)
    ],
    # 8: Финал (14 слотов)
    [
        (90, 260), (90, 460), (270, 360), (270, 560), (460, 360), (460, 570), (690, 360), (690, 400),
        (690, 50), (980, 50), (980, 570), (1030, 420), (1190, 140), (1190, 340)
    ],
    # 9: Генератор (Карта 10)
    _init_s9
]

current_playing_track = None

def play_soundtrack(filename):
    global current_playing_track
    if not pygame.mixer.get_init():
        return
    full_path = os.path.join(BASE_DIR, "assets", "sounds", filename)
    if full_path == current_playing_track:
        return
    if os.path.exists(full_path):
        try:
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(current_music_volume)
            pygame.mixer.music.play(-1)
            current_playing_track = full_path
        except Exception as e:
            print(f"Music error: {e}")
    else:
        print(f"Soundtrack not found: {full_path}")
