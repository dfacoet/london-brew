from typing import cast

import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from pydantic import HttpUrl

from london_brew.config import CAMRA_URL
from london_brew.models import Brewery


class BreweryScraper:
    """Scrapes brewery information from CAMRA's London brewery list."""

    def __init__(self):
        self.url = CAMRA_URL

    def _fetch_page(self) -> str:
        """Fetch the HTML content from the CAMRA page."""
        response = requests.get(self.url)
        response.raise_for_status()
        return response.text

    def _extract_social_links(
        self, cell: Tag
    ) -> tuple[HttpUrl | None, HttpUrl | None, HttpUrl | None, HttpUrl | None]:
        """Extract social media links from a cell."""
        links = cell.find_all("a")
        website = twitter = facebook = instagram = None

        for link in links:
            if not isinstance(link, Tag):
                continue
            href = link.get("href")
            if not href:
                continue
            href_str = str(href)  # Cast to str to satisfy type checker
            if "twitter.com" in href:
                twitter = HttpUrl(href_str)
            elif "facebook.com" in href:
                facebook = HttpUrl(href_str)
            elif "instagram.com" in href:
                instagram = HttpUrl(href_str)
            else:
                website = HttpUrl(href_str)

        return website, twitter, facebook, instagram

    def _parse_taproom(self, cell: Tag) -> tuple[str, HttpUrl] | None:
        """Parse taproom information."""
        link = cell.find("a")
        if not link or not isinstance(link, Tag):
            return None
        href = link.get("href")
        if not href:
            return None
        return (cell.get_text(strip=True), HttpUrl(str(href)))  # Cast to str here too

    def _parse_row(self, row: Tag) -> Brewery:
        """Parse a table row into a Brewery object."""
        cells = cast(ResultSet[Tag], row.find_all("td"))

        # Basic info
        name = cells[0].get_text(strip=True)
        location = cells[1].get_text(strip=True)
        brewery_type = cells[2].get_text(strip=True)

        # Social media and website
        website, twitter, facebook, instagram = self._extract_social_links(cells[3])

        # Taproom info
        taproom = self._parse_taproom(cells[4])

        # Production info
        cask = cells[5].get_text(strip=True)
        keg = cells[6].get_text(strip=True)
        tank = cells[7].get_text(strip=True)
        bottles = cells[8].get_text(strip=True)
        cans = cells[9].get_text(strip=True)

        # Branch and comments
        branch = cells[10].get_text(strip=True)
        comments = cells[11].get_text(strip=True) if len(cells) > 11 else ""

        return Brewery(
            name=name,
            location=location,
            type=brewery_type,
            website=website,
            twitter=twitter,
            facebook=facebook,
            instagram=instagram,
            taproom=taproom,
            cask=cask,
            keg=keg,
            tank=tank,
            bottles=bottles,
            cans=cans,
            branch=branch,
            comments=comments,
        )

    def scrape(self) -> list[Brewery]:
        """Scrape the brewery list and return a list of Brewery objects."""
        html = self._fetch_page()
        soup = BeautifulSoup(html, "html.parser")

        # Find the main table
        table = soup.find("table")
        if not table or not isinstance(table, Tag):
            raise ValueError("Could not find brewery table on page")

        # Skip header row
        rows = cast(ResultSet[Tag], table.find_all("tr")[1:])

        breweries = []
        for row in rows:
            try:
                brewery = self._parse_row(row)
                breweries.append(brewery)
            except Exception as e:
                print(f"Error parsing row: {e}")
                continue

        return breweries
