from datetime import datetime
from typing import Optional

import click

from tagbiljett.tagbiljett import (
    find_journey,
    find_location_id,
    find_prices,
    get_locations,
    get_price_data,
    get_search_results,
    get_session,
    post_standard_search,
)


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Query current SJ ticket prices for a given journey",
)
@click.argument(
    "departure_date_time",
    metavar=r"%Y-%m-%dT%H:%M",
    type=click.DateTime(formats=[r"%Y-%m-%dT%H:%M"]),
)
@click.argument("departure_location_name", metavar="FROM", type=str)
@click.argument("arrival_location_name", metavar="TO", type=str)
@click.option(
    "-a",
    "--arrival",
    "arrival_date_time",
    metavar=r"%Y-%m-%dT%H:%M",
    type=click.DateTime(formats=[r"%Y-%m-%dT%H:%M"]),
    help="Arrival date and time.",
)
@click.option(
    "-n",
    "--changes",
    "num_changes",
    type=int,
    help="Exact number of changes.",
)
def cli(
    departure_date_time: datetime,
    departure_location_name: str,
    arrival_location_name: str,
    arrival_date_time: Optional[datetime],
    num_changes: Optional[int],
) -> None:
    try:
        cookies = get_session()
        locations = get_locations(cookies)
        departure_location_id = find_location_id(locations, departure_location_name)
        arrival_location_id = find_location_id(locations, arrival_location_name)
        timetable_token, pricing_token = post_standard_search(
            departure_date_time,
            departure_location_id,
            arrival_location_id,
            cookies,
        )
        timetable = get_search_results(timetable_token, cookies)
        journey_token = find_journey(
            timetable,
            departure_date_time,
            arrival_date_time=arrival_date_time,
            num_changes=num_changes,
        )
        price_data = get_price_data(pricing_token, journey_token, cookies)
        prices = find_prices(price_data["salesCategoryPrice"])
        for category, amount_or_status in prices.items():
            click.echo(f"{category}\t{amount_or_status}")
    except Exception as e:
        raise click.ClickException(str(e))


if __name__ == "__main__":
    cli()
