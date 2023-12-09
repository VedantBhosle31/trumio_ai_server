import httpx
import requests


async def fetch_languages(client, url):
    response = await client.get(url)
    res = list(response.json())
    return res

async def github_get_projects(username):
    try:
        user_url = f"https://api.github.com/users/{username}"
        user_data = requests.get(user_url, headers={"Accept": "application/vnd.github+json",
                                                    "X-GitHub-Api-Version": "2022-11-28"}).json()

        repo_url = user_data["repos_url"]
        repo_list = requests.get(repo_url).json()

        async with httpx.AsyncClient() as client:
            tasks = []
            for repo in repo_list:
                if not repo["fork"]:
                    languages_url = repo["languages_url"]
                    languages = await fetch_languages(client, languages_url)
                    project_data = {
                        "name": repo["name"],
                        "languages": languages
                    }
                    tasks.append(project_data)

            print(tasks)

        return tasks
    except Exception as e:
        return []




def codeforce_get_contests( username):
    response = requests.get(f"https://codeforces.com/api/user.rating?handle={username}")
    data = response.json()["result"]
    contest_ranks = [entry['rank'] for entry in data]
    return contest_ranks

def codeforce_get_info(username):
    try:
        response = requests.get(f"https://codeforces.com/api/user.info?handles={username}")
        data = response.json()["result"][0]
        return {'rating': data['rating'], 'maxRating': data['maxRating'], "rank" : data["rank"], "maxRank" : data["maxRank"]}
    except Exception as e:
        return {}


# await get_projects("RasagnyaG")