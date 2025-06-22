import os
import requests
from datetime import datetime, timezone

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "wall-of-shame"
README_FILE = "README.md"
SHA_FOLDER = "shames"

# Ensure shame folder exists
if not os.path.exists(SHA_FOLDER):
    os.makedirs(SHA_FOLDER)

def has_contributed_today():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/events/public"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    print(f"📅 Checking recent GitHub activity for {GITHUB_USERNAME}")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"⚠️ GitHub API error: {response.status_code}")
        print(response.text)
        return False

    events = response.json()
    today = datetime.now(timezone.utc).date()

    for event in events:
        if event["type"] == "PushEvent":
            event_date = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ").date()
            if event_date == today:
                print(f"✅ Found a PushEvent today: {event['repo']['name']}")
                return True

    print("❌ No PushEvent found for today.")
    return False

def get_shame_stats():
    shame_files = sorted(
        f for f in os.listdir(SHA_FOLDER)
        if f.startswith("shame_") and f.endswith(".txt")
    )
    total = len(shame_files)
    last_shame = shame_files[-1].replace("shame_", "").replace(".txt", "") if shame_files else "Never"

    if shame_files:
        last_date = datetime.strptime(last_shame, "%Y-%m-%d").date()
        streak = (datetime.utcnow().date() - last_date).days
    else:
        streak = "🔥 Perfect Discipline!"

    return total, last_shame, streak

def create_shame_file():
    today_str = datetime.utcnow().date().isoformat()
    filename = os.path.join(SHA_FOLDER, f"shame_{today_str}.txt")
    with open(filename, "w") as f:
        f.write("You failed your discipline on " + today_str)

def update_readme(total, last_shame, streak):
    with open(README_FILE, "w") as f:
        f.write(f"""# 🧱 Wall of Shame

A repository that holds me accountable when I fail to push code daily.

---

## 😔 Total Shameful Days: **{total}**
## 🗓️ Last Shame: **{last_shame}**
## 🔥 Current Discipline Streak: **{streak} days**

---

If you're reading this, I either:
- Coded and pushed today 💪
- Or... this repo is calling me out 😤
""")

def main():
    if not has_contributed_today():
        print("❌ No contribution found today. Shame incoming.")
        create_shame_file()
    else:
        print("✅ Contribution found. No shame today.")

    total, last_shame, streak = get_shame_stats()
    update_readme(total, last_shame, streak)

if __name__ == "__main__":
    main()
