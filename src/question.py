from openai import OpenAI
from datetime import datetime, timedelta
import json
import requests
import random
import os


def get_random_question(top_n=25):
    if not os.path.exists("data/openai.json"):
        return None

    with open("data/openai.json", "r") as f:
        cfg = json.load(f)

    if "api_key" not in cfg or len(cfg["api_key"]) == 0:
        return None

    client = OpenAI(api_key=cfg["api_key"])

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0"}

    # Get the current Wikipedia namespaces that we want to ignore (for example user accounts or the search)
    query = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&meta=siteinfo&siprop=namespaces%7Cnamespacealiases&formatversion=2&format=json",
                         headers=headers).json()["query"]
    namespaces = []
    for ns in query["namespaces"]:
        namespaces.append(query["namespaces"][ns]["name"])
    for na in query["namespacealiases"]:
        namespaces.append(na["alias"])

    topics = []
    for days in range(0, 5):
        # Get the most viewed articles `days` days ago
        date = (datetime.now() - timedelta(days)).strftime("%Y/%m/%d")
        response = requests.get(f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/" + date,
                                headers=headers)
        if response.status_code != 200:
            continue

        articles = response.json()["items"][0]["articles"]
        for a in articles:
            title = a["article"].replace("_", " ")
            # Main page usually has most views
            is_article = title != "Main Page" and not any(
                title.startswith(ns + ":") for ns in namespaces)
            if is_article:
                topics.append(title)

    # Pick from the n-th most viewed article a title as our topic
    topic = random.choice(topics)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are given a topic and should pick one and write a challenging question." +
                "Keep it very short and concise. Provide it as JSON with keys question and answer."
            },
            {
                "role": "user",
                "content": topic
            },
        ],
        n=1,
        temperature=1,
        max_tokens=256
    )

    choice = response.choices[0].message.content
    response = json.loads(choice)

    return (response["question"], response["answer"])
