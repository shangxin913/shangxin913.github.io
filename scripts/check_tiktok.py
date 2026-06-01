import json
import os
import re
import time
from datetime import datetime, timezone, timedelta
import requests

ACCOUNTS_FILE = "accounts.json"
RECORDS_FILE = "data/records.json"
MAX_RECORDS = 2000
BJT = timezone(timedelta(hours=8))
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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

def get_video_count(username):
    url = "https://www.tiktok.com/@" + username
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
        return {"total_videos": None, "status": "unknown", "error_msg": "cannot parse"}
    except Exception as e:
        return {"total_videos": None, "status": "error", "error_msg": str(e)[:120]}

def main():
    now_bjt = datetime.now(BJT)
    date_str = now_bjt.strftime("%Y-%m-%d")
    datetime_str = now_bjt.strftime("%Y-%m-%d %H:%M")

    accounts_cfg = load_json(ACCOUNTS_FILE, {"accounts": []})
    accounts = accounts_cfg.get("accounts", [])
    if not accounts:
        print("no accounts")
        return

    db = load_json(RECORDS_FILE, {"accounts": accounts, "records": [], "summary": {"total_new_videos": 0, "total_runs": 0}})
    old_records = db.get("records", [])
    summary = db.get("summary", {"total_new_videos": 0, "total_runs": 0})

    last_known = {}
    for r in old_records:
        acc = r.get("account")
        tv = r.get("total_videos")
        if acc and tv is not None:
            last_known[acc] = tv

    new_records = []
    run_new_videos = 0

    for username in accounts:
        print("checking @" + username)
        result = get_video_count(username)
        total = result["total_videos"]
        prev = last_known.get(username)
        new_v = max(0, total - prev) if (total is not None and prev is not None) else 0
        run_new_videos += new_v
        new_records.append({
            "date": date_str,
            "checked_at": datetime_str,
            "account": username,
            "new_videos": new_v,
            "total_videos": total,
            "prev_videos": prev,
            "status": result["status"],
            "error_msg": result["error_msg"],
        })
        print("total=" + str(total) + " new=" + str(new_v) + " status=" + result["status"])
        time.sleep(2)

    summary["total_new_videos"] = summary.get("total_new_videos", 0) + run_new_videos
    summary["total_runs"] = summary.get("total_runs", 0) + 1
    summary["last_run"] = datetime_str

    all_records = (new_records + old_records)[:MAX_RECORDS]
    save_json(RECORDS_FILE, {"accounts": accounts, "records": all_records, "summary": summary})
    print("done. new=" + str(run_new_videos) + " total_runs=" + str(summary["total_runs"]))

if __name__ == "__main__":
    main()
