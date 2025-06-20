import os
import requests
from datetime import datetime

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "wall-of-shame"
README_FILE = "README.md"
SHA_FOLDER = "shames"

# Ensure shame folder exists
if not os.path.exists(SHA_FOLDER):
    os.makedirs(SHA_FOLDER)

def has_contributed_today():
    today = datetime.now(datetime.timezone.utc).date().isoformat()

    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    variables = {"login": GITHUB_USERNAME}
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    print(f"📅 Checking GraphQL contributions for {GITHUB_USERNAME} on {today}")
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=headers
    )

    if response.status_code != 200:
        print(f"⚠️ GraphQL API error: {response.status_code}")
        print(response.text)
        return False

    data = response.json()
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    for week in weeks:
        for day in week["contributionDays"]:
            if day["date"] == today and day["contributionCount"] > 0:
                print(f"✅ Contribution found on {today}")
                return True

    print(f"❌ No contributions found on {today}")
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
