#!/usr/bin/env python3
from datetime import datetime
from typing import Any, Optional

import pandas as pd
import requests


def get_session() -> dict[str, str]:
    url = "https://www.sj.se/cms/configuration"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    cookies = {
        data["cookie"]["session"]["name"]: data["cookie"]["session"]["token"],
        data["cookie"]["service"]["name"]: data["cookie"]["service"]["token"],
    }
    return cookies


def get_locations(cookies: dict[str, str]) -> pd.DataFrame:
    url = "https://www.sj.se/v19/rest/travels/travelreferencedata?locations=true"
    r = requests.get(url, cookies=cookies)
    r.raise_for_status()
    data = r.json()
    locations = pd.DataFrame(
        data=[
            {
                "id": location["location"]["id"],
                "name": location["location"]["name"],
            }
            for location in data["locations"]
        ]
    )
    return locations


def find_location_id(locations: pd.DataFrame, location_name: str) -> str:
    locations = locations[locations["name"] == location_name]
    if locations.empty:
        raise ValueError(f"Location '{location_name}' not found")
    if len(locations.index) > 1:
        raise ValueError(f"Multiple locations found for '{location_name}'")
    location_id: str = locations.iloc[0]["id"]
    return location_id


def post_standard_search(
    departure_date_time: datetime,
    departure_location_id: str,
    arrival_location_id: str,
    cookies: dict[str, str],
) -> tuple[str, str]:
    url = "https://www.sj.se/v19/rest/travels/searchdata"
    payload = {
        "journeyDate": {"date": departure_date_time.strftime(r"%Y-%m-%d")},
        "departureLocation": {"id": departure_location_id},
        "arrivalLocation": {"id": arrival_location_id},
        "consumers": [{"consumerCategory": {"id": "VU"}}],
    }
    r = requests.post(url, json=payload, cookies=cookies)
    r.raise_for_status()
    data = r.json()
    timetable_token = data["timetableToken"]
    standard_pricing_token = data["pricingTokens"]["STANDARD"]["token"]
    return timetable_token, standard_pricing_token


def get_search_results(timetable_token: str, cookies: dict[str, str]) -> pd.DataFrame:
    url = f"https://www.sj.se/v19/rest/travels/timetables/{timetable_token}"
    r = requests.get(url, cookies=cookies)
    r.raise_for_status()
    data = r.json()
    timetable = pd.DataFrame(
        data=[
            {
                "departure_date": journey["departureDate"]["date"],
                "departure_time": journey["departureTime"]["time"],
                "arrival_date": journey["arrivalDate"]["date"],
                "arrival_time": journey["arrivalTime"]["time"],
                "num_changes": len(journey["itineraries"]) - 1,
                "journey_token": journey["journeyToken"],
            }
            for journey in data["journeys"]
        ]
    )
    return timetable


def find_journey(
    timetable: pd.DataFrame,
    departure_date_time: datetime,
    arrival_date_time: Optional[datetime] = None,
    num_changes: Optional[int] = None,
) -> str:
    departure_date = departure_date_time.strftime(r"%Y-%m-%d")
    departure_time = departure_date_time.strftime(r"%H:%M")
    timetable = timetable[timetable["departure_date"] == departure_date]
    timetable = timetable[timetable["departure_time"] == departure_time]
    if arrival_date_time is not None:
        arrival_date = arrival_date_time.strftime(r"%Y-%m-%d")
        arrival_time = arrival_date_time.strftime(r"%H:%M")
        timetable = timetable[timetable["arrival_date"] == arrival_date]
        timetable = timetable[timetable["arrival_time"] == arrival_time]
    if num_changes is not None:
        timetable = timetable[timetable["num_changes"] == num_changes]
    if timetable.empty:
        raise ValueError("No matching trains found")
    if len(timetable) > 1:
        raise ValueError("Multiple matching trains found")
    journey_token: str = timetable.iloc[0]["journey_token"]
    return journey_token


def get_price_data(
    pricing_token: str, journey_token: str, cookies: dict[str, str]
) -> dict[str, Any]:
    url = f"https://www.sj.se/v19/rest/travels/prices/{pricing_token}/{journey_token}"
    price_request = requests.get(url, cookies=cookies)
    price_request.raise_for_status()
    price_data: dict[str, Any] = price_request.json()
    return price_data


def find_prices(price_data: dict[str, Any], _category: str = "") -> dict[str, float]:
    prices = {}
    for key, item in price_data.items():
        if key == "totalPrice":
            prices[_category] = item["amount"]
        elif isinstance(item, dict):
            if key in ("journeyPriceDescription",):
                child_category = _category
            else:
                child_category = f"{_category}/{key}"
            prices.update(find_prices(item, _category=child_category))
    return prices
