import aiohttp
from datetime import datetime, timezone
from dataclasses import dataclass, field

WEB_ID = "8b9b4dbf-1ff8-4ad2-8520-07a1ac7c0f8a"


@dataclass
class AggregatedWorkoutMetrics:
    numWorkouts: int
    weightLifted: int
    caloriesBurned: int
    activeMinutes: int


@dataclass
class UserProfile:
    subscription_type: str | None
    active: bool
    device_types: list = field(default_factory=list)


def format_datetime_as_iso8601(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


class Tempo:
    def __init__(self, username: str, password: str, session: aiohttp.ClientSession):
        self.username = username
        self.password = password
        self.session = session
        self.access_token = None
        self.access_token_expiry =None
        self.refresh_token = None
        self.refresh_expiry = None
        self.last_refresh = None

    async def login(self):
        test = await self.session.post(url="https://api.trainwithpivot.com/oauth/token", data={
            "client_id": WEB_ID,
            "grant_type": "password",
            "password": self.password,
            "username": self.username})
        resp = await test.json()
        self.access_token = "Bearer " + resp["access_token"]
        self.access_token_expiry = resp["expires_in"]
        self.refresh_token = resp["refresh_token"]
        self.refresh_expiry = resp["refresh_expires_in"]
        self.last_refresh = datetime.now()

    async def me(self):
        """Returns dict of exercise name → current weight recommendation."""
        resp = await self.session.get("https://api.trainwithpivot.com/v1/me", headers={"authorization": self.access_token})
        r = await resp.json()
        data = {}
        for exercise in r['data']["performance"]["exercises"].values():
            data[exercise["exercise_name"]] = exercise["progress"][-1]["weight"]["value"]
        return data

    async def profile(self) -> UserProfile:
        """Returns high-level account and subscription info."""
        resp = await self.session.get("https://api.trainwithpivot.com/v1/me", headers={"authorization": self.access_token})
        r = await resp.json()
        d = r.get("data", {})
        return UserProfile(
            subscription_type=d.get("subscription_type"),
            active=d.get("active", False),
            device_types=d.get("device_types", []),
        )

    async def get_streak(self) -> int:
        """Returns current workout streak (consecutive weeks with activity)."""
        graphql_data = {
            "query": "{ currentUser { streak } }"
        }
        resp = await self.session.post("https://api.trainwithpivot.com/v1/graphql", headers={"authorization": self.access_token}, json=graphql_data)
        j = await resp.json()
        return j["data"]["currentUser"].get("streak") or 0

    async def get_weekly_metrics(self) -> AggregatedWorkoutMetrics:
        """Returns aggregated workout metrics for the current week."""
        graphql_data = {
            "query": """
            {
                weeklyAchievementMetrics {
                    numWorkouts
                    weightLifted
                    caloriesBurned
                    activeMinutes
                }
            }
            """
        }
        resp = await self.session.post("https://api.trainwithpivot.com/v1/graphql", headers={"authorization": self.access_token}, json=graphql_data)
        j = await resp.json()
        data = j["data"]["weeklyAchievementMetrics"]
        return AggregatedWorkoutMetrics(
            numWorkouts=data["numWorkouts"],
            weightLifted=data["weightLifted"],
            caloriesBurned=data["caloriesBurned"],
            activeMinutes=data["activeMinutes"],
        )

    async def refresh(self):
        if (datetime.now() - self.last_refresh).total_seconds() > self.access_token_expiry / 2:
            resp = await self.session.post("https://api.trainwithpivot.com/oauth/token", data={
                "client_id": WEB_ID,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            })
            r = await resp.json()
            self.access_token = "Bearer " + r["access_token"]
            self.access_token_expiry = r["expires_in"]
            self.refresh_token = r["refresh_token"]
            self.refresh_expiry = r["refresh_expires_in"]
            self.last_refresh = datetime.now()

    async def get_stats(self, start:datetime,end: datetime):

        graphql_data = {
            "operationName": "getAggregatedWorkoutMetrics",
            "query": """
            query getAggregatedWorkoutMetrics($options: AggregatedWorkoutMetricsInput) {
                currentUser {
                    __typename
                    aggregatedWorkoutMetrics(options: $options) {
                        __typename
                        numWorkouts
                        weightLifted
                        caloriesBurned
                        activeMinutes
                    }
                }
            }
            """,
            "variables": {
                "options": {
                    "startDate": format_datetime_as_iso8601(start),
                    "endDate": format_datetime_as_iso8601(end),
                }
            }
        }

        resp = await self.session.post("https://api.trainwithpivot.com/v1/graphql", headers={"authorization": self.access_token},json=graphql_data)
        j = await resp.json()
        data = j["data"]["currentUser"]["aggregatedWorkoutMetrics"]
        return AggregatedWorkoutMetrics(numWorkouts=data["numWorkouts"], weightLifted=data["weightLifted"], activeMinutes=data["activeMinutes"], caloriesBurned=data["caloriesBurned"])
