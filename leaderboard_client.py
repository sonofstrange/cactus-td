# -*- coding: utf-8 -*-
"""
leaderboard_client.py - Клиент онлайн таблицы лидеров для Cactus TD.
Выполняет все сетевые запросы в фоновых потоках без блокировки FPS игры.
"""
import hmac
import hashlib
import json
import urllib.request
import urllib.error
import threading
import time
from typing import Callable, Optional, Dict, Any
from config import IS_ANDROID

SERVER_URL = "http://185.176.94.10:8095"
SECRET_SALT = b"cactus_td_secret_salt_2026_stars_and_thorns"
REQUEST_TIMEOUT = 5.0  # секунды

# Локальный кэш последнего успешного ответа
_CACHE = {
    "score": None,
    "waves": None,
    "stars": None,
    "dark": None,
    "last_fetched": 0.0,
    "is_fetching": False,
    "last_error": None,
    "last_submit_status": None,
}

def _make_sig(payload: str) -> str:
    return hmac.new(SECRET_SALT, payload.encode('utf-8'), hashlib.sha256).hexdigest()

def _http_post(endpoint: str, data: dict, timeout=REQUEST_TIMEOUT) -> Optional[dict]:
    url = f"{SERVER_URL}{endpoint}"
    req_body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=req_body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status == 200:
            return json.loads(resp.read().decode('utf-8'))
    return None

def _http_get(endpoint: str, timeout=REQUEST_TIMEOUT) -> Optional[dict]:
    url = f"{SERVER_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "CactusTD-Client/1.0"},
        method="GET"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        if resp.status == 200:
            return json.loads(resp.read().decode('utf-8'))
    return None

_LAST_SUBMIT_TIME = 0.0

def async_submit_score(savedata: dict, on_complete: Optional[Callable[[bool, Any], None]] = None, force: bool = False):
    """
    Асинхронно отправляет текущие показатели сейва на сервер.
    Никогда не крашит игру и не подвешивает FPS.
    """
    global _LAST_SUBMIT_TIME
    now = time.time()
    if not force and (now - _LAST_SUBMIT_TIME < 20.0):
        return  # Не спамим сервер чаще чем раз в 20 секунд при обычных сохранениях

    _LAST_SUBMIT_TIME = now

    def _worker():
        try:
            from game_data import calculate_account_score, get_account_id, get_account_nickname
            player_id = get_account_id()
            nickname = get_account_nickname(fallback=savedata.get("PlayerName", "Игрок"))
            score, details = calculate_account_score(savedata)

            waves = details["waves"]
            star_cacti = details["star_cacti"]
            dark_cacti = details["dark_cacti"]
            upgrades = details["upgrades"]
            greenhouse = details["greenhouse"]
            relics = details["relics"]
            playtime_min = details["playtime_min"]
            achievements = details["achievements"]
            bestiary = details["bestiary"]
            credits_seen = details["credits_seen"]
            diff_val = details.get("difficulty", "normal")

            device_os = "android" if IS_ANDROID else "windows"

            # HMAC подпись включает :diff_val
            sig_payload = f"{player_id}:{waves}:{star_cacti}:{dark_cacti}:{upgrades}:{greenhouse}:{relics}:{int(playtime_min)}:{achievements}:{bestiary}:{1 if credits_seen else 0}:{diff_val}"
            sig = _make_sig(sig_payload)

            payload = {
                "player_id": player_id,
                "nickname": nickname,
                "waves": waves,
                "star_cacti": star_cacti,
                "dark_cacti": dark_cacti,
                "upgrades": upgrades,
                "greenhouse": greenhouse,
                "relics": relics,
                "playtime_min": playtime_min,
                "achievements": achievements,
                "bestiary": bestiary,
                "credits_seen": credits_seen,
                "difficulty": diff_val,
                "device_os": device_os,
                "sig": sig
            }

            res = _http_post("/api/leaderboard/submit", payload)
            _CACHE["last_submit_status"] = "ok"
            _CACHE["last_error"] = None
            if on_complete:
                on_complete(True, res)
        except Exception as e:
            _CACHE["last_submit_status"] = "error"
            _CACHE["last_error"] = str(e)
            if on_complete:
                on_complete(False, str(e))

    t = threading.Thread(target=_worker, daemon=True)
    t.start()

def async_rename_player(player_id: str, new_nickname: str, on_complete: Optional[Callable[[bool, Any], None]] = None):
    """
    Асинхронно обновляет никнейм игрока в базе сервера.
    """
    def _worker():
        try:
            sig_payload = f"rename:{player_id}:{new_nickname}"
            sig = _make_sig(sig_payload)
            payload = {
                "player_id": player_id,
                "nickname": new_nickname,
                "sig": sig
            }
            res = _http_post("/api/leaderboard/rename", payload)
            if on_complete:
                on_complete(True, res)
        except Exception as e:
            if on_complete:
                on_complete(False, str(e))

    t = threading.Thread(target=_worker, daemon=True)
    t.start()

def async_fetch_leaderboard(category: str = "score", player_id: Optional[str] = None, force: bool = False, on_complete: Optional[Callable[[bool, Any], None]] = None):
    """
    Асинхронно запрашивает топ-50 по выбранной категории (score, waves, stars, dark).
    При успешном ответе обновляет локальный кэш.
    """
    now = time.time()
    # Если данные уже есть и прошло меньше 10 секунд - не спамим запросами, если не force
    if not force and _CACHE.get(category) is not None and (now - _CACHE["last_fetched"] < 10.0):
        if on_complete:
            on_complete(True, _CACHE[category])
        return

    if _CACHE["is_fetching"]:
        return

    _CACHE["is_fetching"] = True

    def _worker():
        try:
            url_path = f"/api/leaderboard?category={category}&limit=50"
            if player_id:
                url_path += f"&player_id={player_id}"
            data = _http_get(url_path)
            if data and data.get("top") is not None:
                _CACHE[category] = data
                _CACHE["last_fetched"] = time.time()
                _CACHE["last_error"] = None
                if on_complete:
                    on_complete(True, data)
            else:
                raise Exception("Пустой ответ от сервера")
        except Exception as e:
            _CACHE["last_error"] = str(e)
            if on_complete:
                on_complete(False, str(e))
        finally:
            _CACHE["is_fetching"] = False

    t = threading.Thread(target=_worker, daemon=True)
    t.start()

def get_cached_leaderboard(category: str = "score") -> Optional[dict]:
    return _CACHE.get(category)

def is_fetching() -> bool:
    return _CACHE.get("is_fetching", False)

def get_last_error() -> Optional[str]:
    return _CACHE.get("last_error")
