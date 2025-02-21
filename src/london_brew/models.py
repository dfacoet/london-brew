from pydantic import BaseModel, HttpUrl

# TODO: What about different sections of the list?
# Extra field, or separate models?
# (e.g. closed breweries have empty link fields)


class Brewery(BaseModel):
    name: str
    location: str  # TODO: Area and postcode
    type: str
    website: HttpUrl | None = None
    twitter: HttpUrl | None = None
    facebook: HttpUrl | None = None
    instagram: HttpUrl | None = None
    taproom: tuple[str, HttpUrl] | None = None
    cask: str
    keg: str
    tank: str
    bottles: str
    cans: str
    branch: str  # TODO: enum
    comments: str
