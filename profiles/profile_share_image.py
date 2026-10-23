from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
import reportlab

from .card_pdf import ACCENTS


IMAGE_SIZE = (1200, 630)
FONT_DIR = Path(reportlab.__file__).resolve().parent / 'fonts'
FONT_REGULAR = FONT_DIR / 'Vera.ttf'
FONT_BOLD = FONT_DIR / 'VeraBd.ttf'


def _font(size, bold=False):
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size=size)


def _read_image(image_field):
    if not image_field:
        return None
    try:
        with image_field.open('rb'):
            with Image.open(image_field.file) as source:
                return ImageOps.exif_transpose(source).convert('RGBA')
    except (OSError, ValueError):
        return None


def _fit_image(image, size, crop=False):
    if crop:
        return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
    image.thumbnail(size, Image.Resampling.LANCZOS)
    return image


def _draw_fitted_text(draw, text, position, max_width, font_size, fill, bold=False, min_size=20):
    font = _font(font_size, bold)
    while font_size > min_size and draw.textbbox((0, 0), text, font=font)[2] > max_width:
        font_size -= 2
        font = _font(font_size, bold)
    draw.text(position, text, font=font, fill=fill)


def _draw_asset(canvas, image_field, box, crop=False, rounded=False):
    image = _read_image(image_field)
    if image is None:
        return False
    x, y, width, height = box
    image = _fit_image(image, (width, height), crop=crop)
    if crop:
        mask = Image.new('L', (width, height), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, height - 1), radius=16, fill=255)
        canvas.paste(image, (x, y), mask)
    else:
        canvas.alpha_composite(image, (x + (width - image.width) // 2, y + (height - image.height) // 2))
    return True


def render_profile_share_image(profile):
    width, height = IMAGE_SIZE
    accent = ACCENTS.get(profile.profile_type, '#d9f27b')
    canvas = Image.new('RGBA', IMAGE_SIZE, '#f2f4ee')
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((0, 0, width, 345), fill='#111a16')
    draw.rectangle((0, 0, 8, height), fill=accent)
    for x in range(30, 900, 40):
        draw.line((x, 0, x, 345), fill='#1b2720', width=1)
    for y in range(20, 346, 40):
        draw.line((8, y, 900, y), fill='#1b2720', width=1)

    profile_photo = _read_image(profile.profile_photo)
    text_x = 72
    if profile_photo:
        profile_photo = _fit_image(profile_photo, (170, 170), crop=True)
        mask = Image.new('L', (170, 170), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 169, 169), radius=18, fill=255)
        canvas.paste(profile_photo, (72, 72), mask)
        text_x = 274

    draw.text((text_x, 76), 'DIGITAL IDENTITY  /  PUBLIC PROFILE', font=_font(18, bold=True), fill=accent)
    _draw_fitted_text(draw, profile.display_name, (text_x, 122), 810 - text_x, 58, '#f7f8f5', bold=True, min_size=34)
    role = profile.title or profile.department
    if role:
        _draw_fitted_text(draw, role, (text_x, 204), 810 - text_x, 28, '#c2ccc4', min_size=20)

    organization = profile.organization
    organization_name = organization.name if organization else ''
    logo = profile.organization_logo or (organization.logo if organization else None)
    if _draw_asset(canvas, logo, (text_x, 261, 52, 52)):
        org_x = text_x + 68
    else:
        org_x = text_x
    if organization_name:
        _draw_fitted_text(draw, organization_name, (org_x, 276), 650 - org_x, 25, '#f7f8f5', bold=True, min_size=18)

    draw.text((72, 397), 'PROFILE ID', font=_font(16, bold=True), fill='#647169')
    _draw_fitted_text(draw, profile.unique_id, (72, 429), 650, 30, '#18231d', bold=True, min_size=20)
    draw.text((72, 500), 'SCAN TO OPEN THE FULL PROFILE', font=_font(16, bold=True), fill='#647169')
    draw.rectangle((72, 548, 430, 552), fill=accent)

    if profile.qr_code:
        draw.rounded_rectangle((915, 356, 1147, 588), radius=18, fill='#ffffff', outline='#dce2dc', width=2)
        _draw_asset(canvas, profile.qr_code, (934, 375, 194, 194), crop=True)
        draw.text((959, 574), 'SCAN PROFILE', font=_font(13, bold=True), fill='#647169')

    output = BytesIO()
    canvas.convert('RGB').save(output, format='PNG', optimize=True)
    return output.getvalue()