from typing import TypedDict


class Secrets(TypedDict):
    token: str
    test_guild_ids: dict[str, int]
    authorized_users: dict[str, int]


class Parser(TypedDict):
    broken_chars: str
    raw_section_pattern: str
    raw_group_pattern: str
    raw_property_pattern: str
    ignored_sections: list[str]
    excluded_moves: list[str]
    db_bound_keys: list[str]


class RPS(TypedDict):
    emoji_list: dict[str, str]
    rps_result: dict[str, str]
    rps_match: dict[str, list[tuple[str, str]]]


class ScraperSettings(TypedDict):
    headers: dict[str, str]
    domain_url: str
    homepage_url: str
    image_url_prefix: str
    character_data_url: str
