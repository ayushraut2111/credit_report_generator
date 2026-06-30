from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT

# Page layout
PAGE_SIZE = landscape(A4)
PAGE_W, PAGE_H = PAGE_SIZE
MARGIN = 15 * mm
HDR_H  = 14 * mm   # header band height from top
BODY_W = 297 * mm - 2 * MARGIN

# Colours
NAVY        = HexColor('#1E40AF')
L_BLUE      = HexColor('#4A9FD4')
OFF_WHT     = HexColor('#D6E4F0')
MUTED       = HexColor('#888888')
WM_CLR      = Color(0.55, 0.55, 0.55, alpha=0.07)
ALT_BG      = HexColor('#F2F7FB')
BORDER      = HexColor('#B0C4DE')
YELLOW      = HexColor('#FAD87A')
SUBTOTAL_BG = HexColor('#FFF5CC')
GREEN       = HexColor('#2E7D32')
RED         = HexColor('#C62828')

# Paragraph styles
_S = dict(
    section=ParagraphStyle('section', fontName='Helvetica-Bold',
                           fontSize=11, textColor=NAVY, spaceBefore=6*mm, spaceAfter=2*mm),
    banner=ParagraphStyle('banner', fontName='Helvetica-Bold',
                          fontSize=10, textColor=HexColor('#FFFFFF'), alignment=TA_CENTER),
    cell=ParagraphStyle('cell', fontName='Helvetica',
                        fontSize=8, leading=11),
    cell_sm=ParagraphStyle('cell_sm', fontName='Helvetica',
                           fontSize=7, leading=10, textColor=MUTED),
    cell_c=ParagraphStyle('cell_c', fontName='Helvetica',
                          fontSize=8, leading=11, alignment=TA_CENTER),
    cell_cb=ParagraphStyle('cell_cb', fontName='Helvetica-Bold',
                           fontSize=8, leading=11, alignment=TA_CENTER),
    cell_hdr=ParagraphStyle('cell_hdr', fontName='Helvetica-Bold',
                            fontSize=8, leading=11, textColor=NAVY, alignment=TA_LEFT),
    cell_b=ParagraphStyle('cell_b', fontName='Helvetica-Bold',
                          fontSize=8, leading=11),
    cell_num=ParagraphStyle('cell_num', fontName='Helvetica',
                            fontSize=8, leading=11, alignment=TA_RIGHT),
    cell_num_b=ParagraphStyle('cell_num_b', fontName='Helvetica-Bold',
                              fontSize=8, leading=11, alignment=TA_RIGHT),
    right=ParagraphStyle('right', fontName='Helvetica',
                         fontSize=7.5, leading=10, alignment=TA_RIGHT, textColor=MUTED),
    placeholder=ParagraphStyle('placeholder', fontName='Helvetica-Oblique',
                               fontSize=9, leading=13, alignment=TA_CENTER, textColor=MUTED),
    disc_heading=ParagraphStyle('disc_heading', fontName='Helvetica-Bold',
                                fontSize=14, leading=20, spaceBefore=8*mm, spaceAfter=4*mm),
    disc_marked=ParagraphStyle('disc_marked', fontName='Helvetica',
                               fontSize=10, leading=15, spaceAfter=6*mm),
    disc_body=ParagraphStyle('disc_body', fontName='Helvetica',
                             fontSize=9, leading=14, alignment=TA_JUSTIFY),
)
