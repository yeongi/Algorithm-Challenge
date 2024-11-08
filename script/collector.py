import os
import time
import requests

# GitHub API 관련 설정
GITHUB_TOKEN = os.getenv('ACCESS_TOKEN')
OWNER = "0chnxxx"
REPOSITORY = "Algorithm-Challenge"

# Github API 설정
HOST = f"https://api.github.com/repos/{OWNER}/{REPOSITORY}"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-Github-Api-Version": "2022-11-28"
}

def fetch_contributors(retry=5, delay=3):
    for attempt in range(retry):
        try:
            response = requests.get(f"{HOST}/stats/contributors", headers=headers)
            response_json = response.json()

            print(response_json)

            if response_json == {}:
                raise ValueError("Empty response received, retrying...")

            return [
                {
                    "total": data["total"],
                    "login": data["author"]["login"],
                    "avatar_url": data["author"]["avatar_url"],
                    "html_url": data["author"]["html_url"]
                }
                for data in response_json
            ]
        except (ValueError, requests.exceptions.RequestException) as e:
            print(f"Attempt {attempt + 1}/{retry} failed: {e}")

            if attempt < retry - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All retries failed.")
                return []


def update_readme(contributors):
    if not contributors:
        return

    readme_path = "../README.md"

    with open(readme_path, "r", encoding="utf-8") as file:
        readme_content = file.readlines()

    content = "### 참여도 TOP 5\n"
    content += "<table>\n<tr>\n"

    for contributor in contributors:
        content += (
            "<td align='center'>\n"
            f"<img src='{contributor['avatar_url']}' width='100' height='100'><br>\n"
            f"<a href='{contributor['html_url']}'>{contributor['login']}</a><br>\n"
            f"<span>{contributor['total']} commits</span>\n"
            "</td>\n"
        )

    content += "</tr>\n</table>\n"

    start_tag = "<!-- BEGIN TOP CONTRIBUTORS -->\n"
    end_tag = "<!-- END TOP CONTRIBUTORS -->\n"

    start_index = readme_content.index(start_tag) + 1
    end_index = readme_content.index(end_tag)

    updated_content = (
            readme_content[:start_index] +
            [content] +
            readme_content[end_index:]
    )

    with open(readme_path, "w", encoding="utf-8") as file:
        file.writelines(updated_content)


def main():
    if GITHUB_TOKEN is None:
        print("token is not set")
    else:
        print("token is set")

    total_contributors = fetch_contributors()
    filtered_contributors = [contributor for contributor in total_contributors if contributor["author"]["login"] != 'github-actions[bot]']
    best_contributors = sorted(filtered_contributors, key=lambda x: x["total"], reverse=True)[:5]

    print(best_contributors)

    update_readme(best_contributors)


if __name__ == "__main__":
    main()
