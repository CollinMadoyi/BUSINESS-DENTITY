from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps
import reportlab
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


CARD_SIZE = (3.5 * inch, 2 * inch)
ACCENTS = {
    'BUSINESS_ID': '#d9f27b',
    'PORTFOLIO_ID': '#9bb8ff',
    'STUDENT_ID': '#79ddd0',
    'COMPANY_ID': '#f2a16d',
    'STAFF_ID': '#b9dc7b',
    'PROFESSIONAL_ID': '#91c2e5',
}

FONT_DIR = Path(reportlab.__file__).resolve().parent / 'fonts'
pdfmetrics.registerFont(TTFont('CardSans', str(FONT_DIR / 'Vera.ttf')))
pdfmetrics.registerFont(TTFont('CardSans-Bold', str(FONT_DIR / 'VeraBd.ttf')))


def _draw_fitted_text(pdf, value, x, y, width, size, color, bold=False, minimum=6):
    if not value:
        return
    font = 'CardSans-Bold' if bold else 'CardSans'
    while size > minimum and pdfmetrics.stringWidth(value, font, size) > width:
        size -= 0.25
    pdf.setFillColor(color)
    pdf.setFont(font, size)
    pdf.drawString(x, y, value)


def _draw_detail(pdf, label, value, y, x, value_x, width, ink, muted):
    if not value:
        return
    _draw_fitted_text(pdf, label.upper(), x, y, value_x - x - 4, 5, muted, bold=True, minimum=4)
    _draw_fitted_text(pdf, str(value), value_x, y, width, 6.5, ink, minimum=4.5)


def _image_data(image_field, pixel_size, crop):
    if not image_field:
        return None
    try:
        with image_field.open('rb'):
            with Image.open(image_field.file) as source:
                image = ImageOps.exif_transpose(source)
                if image.mode in ('RGBA', 'LA') or 'transparency' in image.info:
                    rgba = image.convert('RGBA')
                    background = Image.new('RGBA', rgba.size, '#ffffff')
                    background.alpha_composite(rgba)
                    image = background.convert('RGB')
                else:
                    image = image.convert('RGB')
                if crop:
                    image = ImageOps.fit(image, (pixel_size, pixel_size), method=Image.Resampling.LANCZOS)
                else:
                    image.thumbnail((pixel_size, pixel_size), Image.Resampling.LANCZOS)
                output = BytesIO()
                image.save(output, format='PNG')
                return output.getvalue(), image.size
    except (OSError, ValueError):
        return None


def _draw_image(pdf, image_field, x, y, size, crop=False):
    pixel_size = round(size / 72 * 300)
    prepared = _image_data(image_field, pixel_size, crop)
    if not prepared:
        return False
    data, (width, height) = prepared
    draw_width = size if crop else size * width / max(width, height)
    draw_height = size if crop else size * height / max(width, height)
    pdf.drawImage(
        ImageReader(BytesIO(data)),
        x + (size - draw_width) / 2,
        y + (size - draw_height) / 2,
        width=draw_width,
        height=draw_height,
        mask='auto',
    )
    return True


def render_profile_card(profile):
    width, height = CARD_SIZE
    margin = 14
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=CARD_SIZE, pageCompression=0)
    accent = HexColor(ACCENTS.get(profile.profile_type, '#d9f27b'))
    dark = HexColor('#111a16')
    ink = HexColor('#18231d')
    muted = HexColor('#68756d')

    pdf.setTitle(f'{profile.display_name} printable card')
    pdf.setFillColor(HexColor('#f5f7f2'))
    pdf.rect(0, 0, width, height, stroke=0, fill=1)
    pdf.setFillColor(dark)
    pdf.rect(0, height - 54, width, 54, stroke=0, fill=1)
    pdf.setFillColor(accent)
    pdf.rect(0, 0, 4, height, stroke=0, fill=1)

    image_size = 38
    has_photo = _draw_image(
        pdf,
        profile.profile_photo,
        margin,
        height - margin - image_size,
        image_size,
        crop=True,
    )
    text_x = margin + image_size + 8 if has_photo else margin
    text_width = width - margin - text_x - 68
    _draw_fitted_text(pdf, profile.display_name, text_x, height - 27, text_width, 13, HexColor('#f7f8f5'), bold=True, minimum=8)
    _draw_fitted_text(
        pdf,
        ' · '.join(value for value in (profile.title, profile.department) if value),
        text_x,
        height - 42,
        text_width,
        6.5,
        HexColor('#bac5bd'),
        minimum=5,
    )

    organization = profile.organization
    organization_name = organization.name if organization else ''
    logo = profile.organization_logo or (organization.logo if organization else None)
    logo_size = 24
    logo_x = margin
    if _draw_image(pdf, logo, margin, 65, logo_size):
        logo_x += logo_size + 5
    _draw_fitted_text(pdf, organization_name, logo_x, 75, 148 - logo_x, 7, ink, bold=True, minimum=5)

    value_x = 54
    detail_width = 148 - value_x
    _draw_detail(pdf, 'Phone', profile.phone, 64, margin, value_x, detail_width, ink, muted)
    _draw_detail(pdf, 'Email', profile.email, 53, margin, value_x, detail_width, ink, muted)
    _draw_detail(pdf, 'Website', profile.website, 42, margin, value_x, detail_width, ink, muted)
    _draw_detail(pdf, 'Address', profile.address, 31, margin, value_x, detail_width, ink, muted)
    _draw_fitted_text(pdf, 'PROFILE ID', margin, 17, 36, 5, muted, bold=True, minimum=4)
    _draw_fitted_text(pdf, profile.unique_id, 54, 16, detail_width, 7, ink, bold=True, minimum=5)

    if profile.qr_code:
        qr_x, qr_y, qr_size = width - margin - 66, 17, 58
        pdf.setFillColor(HexColor('#ffffff'))
        pdf.roundRect(qr_x, qr_y, 66, 67, 2, stroke=0, fill=1)
        _draw_image(pdf, profile.qr_code, qr_x + 4, qr_y + 8, qr_size - 8, crop=True)
        _draw_fitted_text(pdf, 'SCAN PROFILE', qr_x + 5, qr_y + 2, qr_size - 10, 5, muted, bold=True, minimum=4.5)
    else:
        _draw_fitted_text(pdf, 'QR UNAVAILABLE', width - margin - 66, 48, 66, 5, muted, bold=True, minimum=4)

    pdf.setStrokeColor(HexColor('#dce2dc'))
    pdf.setLineWidth(0.5)
    pdf.rect(margin, margin, width - 2 * margin, height - 2 * margin, stroke=1, fill=0)
    pdf.showPage()
    pdf.save()
    output.seek(0)
    return output