#!/usr/bin/env python3
"""
TikTok 每日账号监控脚本
每次运行时，抓取 accounts.json 中所有账号的最新视频数量，
并将结果追加到 data/records.json。
"""

import json
import os
import re
import time
from datetime import datetime, timezone, timedelta
import requests

# ── 配置 ──────────────────────────────────────────────────────────────────────
ACCOUNTS_FILE = "accounts.json"
RECORDS_FILE  = "data/records.json"
MAX_RECORDS   = 2000

BJT = timezone(timedelta(hours=8))

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_video_count(username: str) -> dict:
    url = f"https://www.tiktok.com/@{username}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        html = resp.text

        match = re.search(r'"videoCount"\s*:\s*(\d+)', html)
        if match:
            return {"total_videos": int(match.group(1)), "status": "ok", "error_msg": ""}

        match2 = re.search(r'"itemCount"\s*:\s*(\d+)', html)
        if match2:
            return {"total_videos": int(match2.group(1)), "status": "ok", "error_msg": ""}

        return {"total_videos": None, "status": "unknown", "error_msg": "无法解析视频数量"}
    except Exception as e:
        return {"total_videos": None, "status": "error", "error_msg": str(e)[:120]}

def main():
    now_bjt = datetime.now(BJT)
    date_str     = now_bjt.strftime("%Y-%m-%d")
    datetime_str = now_bjt.strftime("%Y-%m-%d %H:%M")

    accounts_cfg = load_json(ACCOUNTS_FILE, {"accounts": []})
    accounts = accounts_cfg.get("accounts", [])
    if not accounts:
        print("⚠️  accounts.json 中没有账号，退出。")
        return

    db = load_json(RECORDS_FILE, {
        "accounts": accounts,
        "records": [],
        "summary": {"total_new_videos": 0, "total_runs": 0}
    })
    old_records = db.get("records", [])
    summary     = db.get("summary", {"total_new_videos": 0, "total_runs": 0})

    last_known: dict = {}
    for r in old_records:
        acc = r.get("account")
        tv  = r.get("total_videos")
        if acc and tv is not None:
            last_known[acc] = tv

    new_records = []
    run_new_videos = 0

    for username in accounts:
        print(f"  检查 @{username} …", end=" ")
        result = get_video_count(username)
        total  = result["total_videos"]
        prev   = last_known.get(username)

        if total is not None and prev is not None:
            new_v = max(0, total - prev)
        else:
            new_v = 0

        run_new_videos += new_v

        rec = {
            "date":         date_str,
