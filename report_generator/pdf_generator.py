from pathlib import Path
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Spacer

from schemas import SampleInputModel

PAGE_SIZE = landscape(A4)
PAGE_W, PAGE_H = PAGE_SIZE
MARGIN = 15 * mm
HDR_H  = 14 * mm   # header band height from top

# colour pallete
NAVY    = HexColor('#1A3A5C')
L_BLUE  = HexColor('#4A9FD4')
OFF_WHT = HexColor('#D6E4F0')
MUTED   = HexColor('#888888')
WM_CLR  = Color(0.55, 0.55, 0.55, alpha=0.07)


class _PageCanvas(canvas.Canvas):
    # draw header,footer and watermark on every page

    def __init__(self, filename, company_name='', generated_at=None, marked_to_org='', **kwargs):
        super().__init__(filename, **kwargs)
        self._saved_page_states = []
        self._company_name  = company_name
        self._generated_at  = generated_at
        self._marked_to_org = marked_to_org

    # track record of every page
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    # here in every page add header footer and page number
    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_chrome(self._pageNumber, total)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    # add chrome pieces in every page

    def _draw_chrome(self, page_num: int, total: int) -> None:
        self._draw_watermark()
        self._draw_header()
        self._draw_footer(page_num, total)

    def _draw_header(self) -> None:
        band_y = PAGE_H - HDR_H

        # Navy band
        self.setFillColor(NAVY)
        self.rect(0, band_y, PAGE_W, HDR_H, fill=1, stroke=0)

        text_y  = band_y + 4 * mm
        sq_x    = MARGIN - 1 * mm

        # brand square (light blue)
        self.setFillColor(L_BLUE)
        self.rect(sq_x, band_y + 3 * mm, 8 * mm, 8 * mm, fill=1, stroke=0)

        # credhive name
        self.setFillColor(HexColor('#FFFFFF'))
        self.setFont('Helvetica-Bold', 9.5)
        self.drawString(sq_x + 10 * mm, text_y, 'credhive')

        # Company name (centred)
        self.setFont('Helvetica-Bold', 8.5)
        self.drawCentredString(PAGE_W / 2, text_y, self._company_name)

        # generated_at (right-aligned)
        self.setFillColor(OFF_WHT)
        self.setFont('Helvetica', 7.5)
        ts = self._generated_at.strftime('%d %b %Y, %H:%M') if self._generated_at else ''
        self.drawRightString(PAGE_W - MARGIN, text_y, ts)

    def _draw_footer(self, page_num: int, total: int) -> None:
        self.setFont('Helvetica', 7)
        self.setFillColor(MUTED)
        self.drawRightString(PAGE_W - MARGIN, 6, f'Page {page_num} of {total}')

    def _draw_watermark(self) -> None:
        self.saveState()
        self.setFillColor(WM_CLR)
        self.translate(PAGE_W / 2, PAGE_H / 2)
        self.rotate(35)
        self.setFont('Helvetica-Bold', 72)
        self.drawCentredString(0, 0, 'Credhive')
        self.restoreState()


def _canvas_factory(data: SampleInputModel):
    # return a subclass pre-loaded with report metadata
    class _C(_PageCanvas):
        def __init__(self, filename, **kwargs):
            super().__init__(
                filename,
                company_name=data.company.name,
                generated_at=data.report_meta.generated_at,
                marked_to_org=data.report_meta.marked_to.organization,
                **kwargs,
            )
    return _C


def generate_pdf(data: SampleInputModel, output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=PAGE_SIZE,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=HDR_H + MARGIN,
        bottomMargin=MARGIN,
    )
    # placeholder body — sections added incrementally
    story = [Spacer(1, 10)]
    doc.build(story, canvasmaker=_canvas_factory(data))
