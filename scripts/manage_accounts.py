import json, os, sys

ACCOUNTS_FILE = "data/accounts.json"

def load():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"accounts": []}

def save(data):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

action = os.environ.get("ACTION", "")
account = os.environ.get("ACCOUNT", "").strip().lstrip("@")

if not account:
    print("No account specified")
    sys.exit(0)

data = load()
accounts = data.get("accounts", [])

if action == "add_account":
    if account not in accounts:
        accounts.append(account)
        data["accounts"] = accounts
        save(data)
        print("Added: @" + account)
    else:
        print("Already exists: @" + account)

elif action == "remove_account":
    if account in accounts:
        accounts.remove(account)
        data["accounts"] = accounts
        save(data)
        print("Removed: @" + account)
    else:
        print("Not found: @" + account)
