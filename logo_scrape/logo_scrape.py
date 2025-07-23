#!/usr/bin/env python3

import os
import re
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

from colorama import Fore
from InquirerPy import prompt
from InquirerPy.validator import EmptyInputValidator, ValidationError, Validator
from PIL import Image
from playwright.sync_api import sync_playwright

LOGO_DIR: Path
LOGO_DIR_STR: str = os.environ.get("LOGO_DIR", "")
if not LOGO_DIR_STR:
    LOGO_DIR = Path.home() / "Pictures" / "logo_scrape"
else:
    LOGO_DIR = Path(LOGO_DIR_STR)
LOGO_DIR.mkdir(0o764, parents=True, exist_ok=True)


class URLValidator(Validator):
    def validate(self, document):
        url = document.text
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValidationError(
                message="Invalid URL, it must have format http(s)://... ", cursor_position=len(document.text)
            )


class SizeValidator(Validator):
    def validate(self, document):
        size = document.text
        if not re.match(r"^\d+x\d+$", size):
            raise ValidationError(message="Use format NxM, for example: 640x480", cursor_position=len(document.text))


QUESTIONS = [
    {"type": "input", "name": "url", "message": "Enter company page URL:", "validate": URLValidator()},
    {"type": "input", "name": "selector", "message": "Enter CSS selector:", "validate": EmptyInputValidator()},
    {
        "type": "input",
        "name": "size",
        "message": "Enter desired size(format 100x100) of logo:",
        "validate": SizeValidator(),
    },
]


def get_logo(url: str, selector: str, size: tuple[int, int]) -> Image.Image:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector(selector)

        element = page.query_selector(selector)
        if element is not None:
            img_bytes = element.screenshot(type="png")

        browser.close()

    with Image.open(BytesIO(img_bytes)) as img:
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            background = Image.new("RGBA", img.size, (255, 255, 255, 255))
            background.paste(img, mask=img.getchannel("A"))
            img = background.convert("RGB")
        else:
            img = img.convert("RGB")

        target_size = size

        img.thumbnail(target_size, Image.Resampling.LANCZOS)

        final_im = Image.new("RGB", target_size, (255, 255, 255))

        paste_x = (target_size[0] - img.width) // 2
        paste_y = (target_size[1] - img.height) // 2

        final_im.paste(img, (paste_x, paste_y))

        return final_im


def main():
    answers = prompt(QUESTIONS)

    url: str = answers["url"] if isinstance(answers["url"], str) else "https://thinkeasy.cz"
    selector: str = answers["selector"] if isinstance(answers["selector"], str) else "header img"
    size: str = answers["size"] if isinstance(answers["size"], str) else "100x100"

    target_size: list[str] = size.split("x")

    logo_path = LOGO_DIR / f"{urlparse(url).netloc}_logo.png"
    image = get_logo(url, selector, (int(target_size[0]), int(target_size[1])))
    image.save(LOGO_DIR / f"{logo_path}", "PNG")

    print(Fore.GREEN + f"\nLogo has been saved into <{logo_path}>.")
    print(Fore.YELLOW + "Good bye and have a good luck!")


if __name__ == "__main__":
    main()
