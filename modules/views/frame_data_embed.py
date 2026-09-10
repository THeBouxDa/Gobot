import random

from discord import Colour
from discord.embeds import Embed

from modules.resources.configs import commands_config, scraping_config
from modules.utils.logging_utils import get_logger
from modules.utils.parsing_utils import sanitize

logger = get_logger(__name__)


def frame_data_builder(data: dict[str, str]) -> list[Embed]:
    """Builds a list of embeds based on move data"""

    hue = random.random()  # Fully random hue
    saturation = random.uniform(0.5, 0.95)  # Saturation randomized from 50% to 95%
    value = random.uniform(0.4, 0.9)  # Value(brightness) randomized from 40% to 90%

    move_input = data["input"]
    input_safe = sanitize(move_input)
    char_name = data["char_name"]
    char_safe = sanitize(char_name)
    move_name = data["name"] or move_input
    # move_safe = sanitize(move_name)
    images = data["images"]
    image_url = data["hitboxes"] or images
    startup = data["startup"] or "--"
    active = data["active"] or "--"
    recovery = data["recovery"] or "--"
    damage = data["damage"]
    invuln = data["invuln"]
    guard = data["guard"].replace("\n", " ")
    on_block = data["onBlock"].replace("\n", " ")
    on_hit = data["onHit"].replace("\n", " ")

    image_url = image_url.strip()
    if image_url == "":
        image_urls = [random.choice(commands_config["move_placeholders"])]
    else:
        image_urls = list(image_url.split(";")[:4])

        image_url = image_urls[0]

    title_url = (
        scraping_config["move_link_template"].format(char_safe, input_safe).strip()
    )

    main_embed = Embed(
        colour=Colour.from_hsv(h=hue, s=saturation, v=value),
        url=title_url,
        title=f"{char_name} - {move_name}",
    )

    main_embed.set_image(url=image_url)

    main_embed.add_field(name="Startup", value=startup, inline=True)
    main_embed.add_field(name="Active", value=active, inline=True)
    main_embed.add_field(name="Recovery", value=recovery, inline=True)

    damage_field: str = "Damage" if damage else ""
    invuln_field: str = "Invuln" if damage else ""

    main_embed.add_field(name=damage_field, value=damage, inline=True)
    main_embed.add_field(name="", value="", inline=True)
    main_embed.add_field(name=invuln_field, value=invuln, inline=True)

    guard_field = f"Guard: {guard}"
    on_block_field = f"On Block: {on_block}"
    on_hit_field = f"On Hit: {on_hit}"

    main_embed.set_footer(text=f"{guard_field}  |  {on_block_field}  |  {on_hit_field}")

    result = [main_embed]
    extra = [Embed(url=title_url).set_image(url=url) for url in image_urls[1:4]]
    result.extend(extra)

    return result
