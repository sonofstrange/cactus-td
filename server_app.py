# -*- coding: utf-8 -*-
"""
server_app.py - FastAPI сервер таблицы рекордов для Cactus TD.
"""
import os
import hmac
import hashlib
import sqlite3
import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "leaderboard.db")
SECRET_SALT = b"cactus_td_secret_salt_2026_stars_and_thorns"

app = FastAPI(title="Cactus TD Leaderboard API", version="1.0.0")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            player_id TEXT PRIMARY KEY,
            nickname TEXT NOT NULL,
            score REAL NOT NULL,
            waves INTEGER NOT NULL,
            star_cacti INTEGER NOT NULL,
            dark_cacti INTEGER NOT NULL,
            upgrades INTEGER NOT NULL,
            greenhouse INTEGER NOT NULL,
            relics INTEGER NOT NULL,
            playtime_min REAL NOT NULL,
            achievements INTEGER NOT NULL,
            bestiary INTEGER NOT NULL,
            credits_seen INTEGER NOT NULL,
            device_os TEXT NOT NULL DEFAULT 'unknown',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_score ON leaderboard(score DESC);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_waves ON leaderboard(waves DESC);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_stars ON leaderboard(star_cacti DESC);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_dark ON leaderboard(dark_cacti DESC);")
    conn.close()

init_db()

def compute_score(waves: int, star_cacti: int, dark_cacti: int, upgrades: int,
                  greenhouse: int, relics: int, playtime_min: float,
                  achievements: int, bestiary: int, credits_seen: bool) -> float:
    val = (
        (max(0, waves) + 1)**0.5 *
        (max(0, star_cacti) + 1)**0.25 *
        (max(0, dark_cacti) + 1)**0.33 *
        (max(0, upgrades) + 1)**0.4 *
        (max(0, greenhouse) + 1)**0.33 *
        (max(0, relics) + 1)**0.33 *
        (max(0.0, playtime_min) + 1)**0.1 *
        (max(0, achievements) + 1)**0.2 *
        (max(0, bestiary) + 1)**0.33 *
        (1.1 if credits_seen else 1.0)
    )
    return round(val, 1)

def verify_sig(data_str: str, sig: str) -> bool:
    expected = hmac.new(SECRET_SALT, data_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)

def sanitize_nickname(nick: str) -> str:
    if not nick:
        return "Кактусовый Боец"
    clean = nick.strip()
    if len(clean) < 2:
        return "Кактусовый Боец"
    return clean[:16]

class SubmitRequest(BaseModel):
    player_id: str
    nickname: str
    waves: int
    star_cacti: int
    dark_cacti: int
    upgrades: int
    greenhouse: int
    relics: int
    playtime_min: float
    achievements: int
    bestiary: int
    credits_seen: bool
    device_os: str = "windows"
    sig: str

class RenameRequest(BaseModel):
    player_id: str
    nickname: str
    sig: str

@app.get("/api/health")
def health():
    conn = get_db()
    c = conn.execute("SELECT COUNT(*) as cnt FROM leaderboard").fetchone()
    total = c["cnt"] if c else 0
    conn.close()
    return {"status": "ok", "total_records": total}

@app.post("/api/leaderboard/submit")
def submit_score(req: SubmitRequest):
    # Проверка HMAC подписи для защиты от ботов/ручного curl
    sig_payload = f"{req.player_id}:{req.waves}:{req.star_cacti}:{req.dark_cacti}:{req.upgrades}:{req.greenhouse}:{req.relics}:{int(req.playtime_min)}:{req.achievements}:{req.bestiary}:{1 if req.credits_seen else 0}"
    if not verify_sig(sig_payload, req.sig):
        raise HTTPException(status_code=400, detail="Invalid signature")

    nick = sanitize_nickname(req.nickname)
    calculated_score = compute_score(
        waves=req.waves,
        star_cacti=req.star_cacti,
        dark_cacti=req.dark_cacti,
        upgrades=req.upgrades,
        greenhouse=req.greenhouse,
        relics=req.relics,
        playtime_min=req.playtime_min,
        achievements=req.achievements,
        bestiary=req.bestiary,
        credits_seen=req.credits_seen
    )

    now_iso = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    with conn:
        conn.execute("""
        INSERT INTO leaderboard (
            player_id, nickname, score, waves, star_cacti, dark_cacti,
            upgrades, greenhouse, relics, playtime_min, achievements,
            bestiary, credits_seen, device_os, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(player_id) DO UPDATE SET
            nickname = excluded.nickname,
            score = MAX(leaderboard.score, excluded.score),
            waves = MAX(leaderboard.waves, excluded.waves),
            star_cacti = MAX(leaderboard.star_cacti, excluded.star_cacti),
            dark_cacti = MAX(leaderboard.dark_cacti, excluded.dark_cacti),
            upgrades = MAX(leaderboard.upgrades, excluded.upgrades),
            greenhouse = MAX(leaderboard.greenhouse, excluded.greenhouse),
            relics = MAX(leaderboard.relics, excluded.relics),
            playtime_min = MAX(leaderboard.playtime_min, excluded.playtime_min),
            achievements = MAX(leaderboard.achievements, excluded.achievements),
            bestiary = MAX(leaderboard.bestiary, excluded.bestiary),
            credits_seen = MAX(leaderboard.credits_seen, excluded.credits_seen),
            device_os = excluded.device_os,
            updated_at = excluded.updated_at
        """, (
            req.player_id, nick, calculated_score, req.waves, req.star_cacti, req.dark_cacti,
            req.upgrades, req.greenhouse, req.relics, req.playtime_min, req.achievements,
            req.bestiary, 1 if req.credits_seen else 0, req.device_os, now_iso
        ))

        # Вычисляем текущее место игрока по очкам
        row_rank = conn.execute(
            "SELECT COUNT(*) + 1 as rank FROM leaderboard WHERE score > (SELECT score FROM leaderboard WHERE player_id = ?)",
            (req.player_id,)
        ).fetchone()
        rank = row_rank["rank"] if row_rank else 1

    conn.close()
    return {
        "status": "ok",
        "score": calculated_score,
        "rank": rank,
        "nickname": nick
    }

@app.post("/api/leaderboard/rename")
def rename_player(req: RenameRequest):
    sig_payload = f"rename:{req.player_id}:{req.nickname}"
    if not verify_sig(sig_payload, req.sig):
        raise HTTPException(status_code=400, detail="Invalid signature")

    nick = sanitize_nickname(req.nickname)
    conn = get_db()
    with conn:
        conn.execute("UPDATE leaderboard SET nickname = ? WHERE player_id = ?", (nick, req.player_id))
    conn.close()
    return {"status": "ok", "nickname": nick}

@app.get("/api/leaderboard")
def get_leaderboard(
    category: str = Query("score", enum=["score", "waves", "stars", "dark"]),
    limit: int = Query(50, ge=1, le=100),
    player_id: Optional[str] = None
):
    col_map = {
        "score": "score",
        "waves": "waves",
        "stars": "star_cacti",
        "dark": "dark_cacti"
    }
    sort_col = col_map.get(category, "score")

    conn = get_db()
    cursor = conn.execute(f"""
        SELECT player_id, nickname, score, waves, star_cacti, dark_cacti,
               upgrades, greenhouse, relics, playtime_min, achievements,
               bestiary, credits_seen, device_os, updated_at
        FROM leaderboard
        ORDER BY {sort_col} DESC, updated_at ASC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()

    top_list = []
    for idx, r in enumerate(rows, start=1):
        top_list.append({
            "rank": idx,
            "player_id": r["player_id"],
            "nickname": r["nickname"],
            "score": r["score"],
            "waves": r["waves"],
            "star_cacti": r["star_cacti"],
            "dark_cacti": r["dark_cacti"],
            "upgrades": r["upgrades"],
            "greenhouse": r["greenhouse"],
            "relics": r["relics"],
            "playtime_min": r["playtime_min"],
            "achievements": r["achievements"],
            "bestiary": r["bestiary"],
            "credits_seen": bool(r["credits_seen"]),
            "device_os": r["device_os"],
            "updated_at": r["updated_at"]
        })

    player_stat = None
    if player_id:
        p_row = conn.execute("SELECT * FROM leaderboard WHERE player_id = ?", (player_id,)).fetchone()
        if p_row:
            p_rank = conn.execute(
                f"SELECT COUNT(*) + 1 as rank FROM leaderboard WHERE {sort_col} > ?",
                (p_row[sort_col],)
            ).fetchone()["rank"]
            player_stat = {
                "rank": p_rank,
                "player_id": p_row["player_id"],
                "nickname": p_row["nickname"],
                "score": p_row["score"],
                "waves": p_row["waves"],
                "star_cacti": p_row["star_cacti"],
                "dark_cacti": p_row["dark_cacti"],
                "upgrades": p_row["upgrades"],
                "greenhouse": p_row["greenhouse"],
                "relics": p_row["relics"],
                "playtime_min": p_row["playtime_min"],
                "achievements": p_row["achievements"],
                "bestiary": p_row["bestiary"],
                "credits_seen": bool(p_row["credits_seen"]),
                "device_os": p_row["device_os"],
                "updated_at": p_row["updated_at"]
            }

    conn.close()
    return {
        "category": category,
        "total_players": len(top_list),
        "top": top_list,
        "player": player_stat
    }
