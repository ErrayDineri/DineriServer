import requests
from datetime import datetime, timedelta, timezone

API_URL = "https://graphql.anilist.co/"

QUERY = """
query (
    $dayStart: Int,
    $dayEnd: Int,
    $page: Int,
){
    Page(page: $page) {
        pageInfo {
            hasNextPage
            total
        }
        airingSchedules(
            airingAt_greater: $dayStart
            airingAt_lesser: $dayEnd
        ) {
            id
            episode
            airingAt
            media {
                id
                idMal
                title {
                    romaji
                    native
                    english
                }
                startDate {
                    year
                    month
                    day
                }
                endDate {
                    year
                    month
                    day
                }
                status
                season
                format
                genres
                synonyms
                duration
                popularity
                episodes
                source(version: 2)
                countryOfOrigin
                hashtag
                averageScore
                siteUrl
                description
                bannerImage
                isAdult
                coverImage {
                    extraLarge
                    color
                }
                trailer {
                    id
                    site
                    thumbnail
                }
                externalLinks {
                    site
                    icon
                    color
                    url
                }
                rankings {
                    rank
                    type
                    season
                    allTime
                }
                studios(isMain: true) {
                    nodes {
                        id
                        name
                        siteUrl
                    }
                }
                relations {
                    edges {
                        relationType(version: 2)
                        node {
                            id
                            title {
                                romaji
                                native
                                english
                            }
                            siteUrl
                        }
                    }
                }
            }
        }
    }
}
"""

def date_to_unix_range(date_str):
    """
    Convert a date string YYYY-MM-DD to start and end Unix timestamps (UTC) for that day.
    """
    dt_start = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    dt_end = dt_start + timedelta(days=1) - timedelta(seconds=1)
    return int(dt_start.timestamp()), int(dt_end.timestamp())

def fetch_airing_schedules_for_day(date_str, page=1):
    day_start, day_end = date_to_unix_range(date_str)

    variables = {
        "dayStart": day_start,
        "dayEnd": day_end,
        "page": page,
    }

    response = requests.post(API_URL, json={"query": QUERY, "variables": variables})
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    date = "2025-06-05"  # change this to the date you want to check
    data = fetch_airing_schedules_for_day(date)

    page_info = data["data"]["Page"]["pageInfo"]
    print(f"Airing schedules on {date}: {page_info['total']} found.")

    for schedule in data["data"]["Page"]["airingSchedules"]:
        media = schedule["media"]
        print(f"Episode {schedule['episode']} of '{media['title']['romaji']}' airs at Unix time {schedule['airingAt']}")
