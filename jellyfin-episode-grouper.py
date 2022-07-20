#!/usr/bin/env python3

import sys
import requests
import re

from typing import List

try:
    base_url = sys.argv[1]
except:
    print("please provide a url to jellyfin!")
    exit(1)

try:
    api_key = sys.argv[2]
except:
    print("please provide an api key!")
    exit(1)

headers = {"X-Emby-Authorization": f"MediaBrowser Token={api_key}"}

try:
    user_name = sys.argv[3]
except:
    print("please provide a username!")
    exit(1)


def get_user_id(name: str):
    response = requests.get(
        f"{base_url}/Users",
        headers=headers,
    )
    if response.status_code != 200:
        print("Could not fetch user id, check your api key and/or jellyfin url!")
        exit(1)
    user_list = response.json()
    correct_users = [user["Id"] for user in user_list if user["Name"] == name]
    if len(correct_users) < 1:
        print(f"Name: '{name}' not present on server!")
        exit(1)
    user = correct_users[0]
    return user


user_id = get_user_id(user_name)


def list_series():
    response = requests.get(
        f"{base_url}/Users/{user_id}/Items?SortBy=SortName&SortOrder=Ascending&IncludeItemTypes=Series&Recursive=true&StartIndex=0",
        headers=headers,
    )
    if response.status_code != 200:
        print("Could not fetch series list, is jellyfin available?")
        exit(1)
    response_body = response.json()
    series = response_body["Items"]
    return series


def list_seasons(series_id: str):
    response = requests.get(
        f"{base_url}/Shows/{series_id}/Seasons?userId={user_id}",
        headers=headers,
    )
    if response.status_code != 200:
        print("Could not list seasons, is jellyfin available?")
        exit(1)
    response_body = response.json()
    seasons = response_body["Items"]
    return seasons


def list_episodes(season_id: str, series_id: str):
    response = requests.get(
        f"{base_url}/Shows/{series_id}/Episodes?seasonId={season_id}&userId={user_id}",
        headers=headers,
    )
    if response.status_code != 200:
        print("Could not list episodes, is jellyfin available?")
        exit(1)
    response_body = response.json()
    episodes = response_body["Items"]
    return episodes


def get_episode(episode_id: str):
    response = requests.get(
        f"{base_url}/Users/{user_id}/Items/{episode_id}",
        headers=headers,
    )
    if response.status_code != 200:
        print("Could not get episode, is jellyfin available?")
        exit(1)
    episode = response.json()
    return episode


def group_episodes(episode_ids: List[str]):
    response = requests.post(
        f"{base_url}/Videos/MergeVersions?Ids={','.join(episode_ids)}",
        headers=headers,
    )
    if response.status_code != 204:
        print("Could not group episodes, is jellyfin available?")
        exit(1)


series_list = list_series()

for series in series_list:
    series_id = series["Id"]
    seasons = list_seasons(series_id)
    for season in seasons:
        season_id = season["Id"]
        episodes = list_episodes(season_id, series_id)
        episode_imdb_map = {}
        for ep in episodes:
            episode_id = ep["Id"]
            episode = get_episode(episode_id)
            episode_name = episode["Name"]
            if "Imdb" in episode["ProviderIds"]:
                provider_id = episode["ProviderIds"]["Imdb"]
            elif "Tvdb" in episode["ProviderIds"]:
                provider_id = episode["ProviderIds"]["Tvdb"]
            else:
                provider_id = re.sub(r" - [\w]+$", "", episode_name)

            if not provider_id in episode_imdb_map:
                episode_imdb_map[provider_id] = []
            episode_imdb_map[provider_id].append(
                {
                    "name": episode_name,
                    "id": episode_id,
                }
            )

        for episodes in episode_imdb_map.values():
            if len(episodes) > 1:
                episode_ids = [episode["id"] for episode in episodes]
                group_episodes(episode_ids)
