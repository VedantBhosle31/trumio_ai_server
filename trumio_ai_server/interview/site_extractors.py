# pip3 install httpx requests
import httpx
import requests


async def fetch_languages(client, url):
    """
    Asynchronously fetches programming languages data from the given URL using an HTTP client.

    Parameters:
    - client: An instance of an httpx.AsyncClient used to send the GET request.
    - url (str): The URL to fetch the programming languages data from.

    Returns:
    - list: A list containing the fetched programming languages data.
    """
    response = await client.get(url)
    res = list(response.json())
    return res

async def github_get_projects(username):
    """
    Asynchronously retrieves the non-forked GitHub repositories for a specific user along with the programming languages used in each repo.

    Parameters:
    - username (str): The GitHub username for which to retrieve repository data.

    Returns:
    - list: A list of dictionaries, each containing repository details, such as name and languages used.
    """
    try:
        user_url = f"https://api.github.com/users/{username}"
        # Fetch the user data with GitHub API version specified in the headers.
        user_data = requests.get(user_url, headers={"Accept": "application/vnd.github+json",
                                                    "X-GitHub-Api-Version": "2022-11-28"}).json()

        repo_url = user_data["repos_url"]
        # Fetch the list of repositories for the user.
        repo_list = requests.get(repo_url).json()

        async with httpx.AsyncClient() as client:
            tasks = []
            for repo in repo_list:
                if not repo["fork"]: # Filter out forked repositories.
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
        # Return an empty list in case of an exception.
        return []




def codeforce_get_contests(username):
    """
    Fetches the contest rank information for a Codeforces user.

    Parameters:
    - username (str): The Codeforces username for which to retrieve contest ranks.

    Returns:
    - list: A list containing past contest ranks for the provided Codeforces username.
    """
    # Fetch the contest history from Codeforces API.
    response = requests.get(f"https://codeforces.com/api/user.rating?handle={username}")
    data = response.json()["result"]
    # Extract the contest ranks from the fetched data.
    contest_ranks = [entry['rank'] for entry in data]
    return contest_ranks

def codeforce_get_info(username):
    """
    Fetches the basic information such as current rating and highest rank for a Codeforces user.

    Parameters:
    - username (str): The Codeforces username for which to retrieve user info.

    Returns:
    - dict: A dictionary containing rating and rank information of the provided Codeforces username.
    """
    try:
        # Fetch the user info data from Codeforces API.
        response = requests.get(f"https://codeforces.com/api/user.info?handles={username}")
        data = response.json()["result"][0]
        # Return a subset of the fetched data containing ratings and ranks.
        return {
            'rating': data['rating'], 
            'maxRating': data['maxRating'], 
            "rank" : data["rank"], 
            "maxRank" : data["maxRank"]
            }
    except Exception as e:
        # Return an empty dictionary in case of an exception.
        return {}


# await get_projects("RasagnyaG")
