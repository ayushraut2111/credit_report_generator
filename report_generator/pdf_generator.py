from pathlib import Path
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from schemas import SampleInputModel

PAGE_SIZE = landscape(A4)
PAGE_W, PAGE_H = PAGE_SIZE
MARGIN = 15 * mm
HDR_H  = 14 * mm   # header band height from top

# colour pallete
NAVY    = HexColor('#1E40AF')
L_BLUE  = HexColor('#4A9FD4')
OFF_WHT = HexColor('#D6E4F0')
MUTED   = HexColor('#888888')
WM_CLR  = Color(0.55, 0.55, 0.55, alpha=0.07)

BODY_W = 297 * mm - 2 * MARGIN
ALT_BG = HexColor('#F2F7FB')
BORDER = HexColor('#B0C4DE')
YELLOW = HexColor('#FAD87A')
SUBTOTAL_BG = HexColor('#FFF5CC')
GREEN = HexColor('#2E7D32')
RED = HexColor('#C62828')

_S = dict(
    section=ParagraphStyle('section',  fontName='Helvetica-Bold',
                           fontSize=11, textColor=NAVY, spaceBefore=6*mm, spaceAfter=2*mm),
    banner=ParagraphStyle('banner',   fontName='Helvetica-Bold',
                          fontSize=10, textColor=HexColor('#FFFFFF'), alignment=TA_CENTER),
    cell=ParagraphStyle('cell',     fontName='Helvetica',
                        fontSize=8,  leading=11),
    cell_sm=ParagraphStyle('cell_sm',  fontName='Helvetica',
                           fontSize=7,  leading=10, textColor=MUTED),
    cell_c=ParagraphStyle('cell_c',   fontName='Helvetica',
                          fontSize=8,  leading=11, alignment=TA_CENTER),
    cell_cb=ParagraphStyle('cell_cb',  fontName='Helvetica-Bold',
                           fontSize=8,  leading=11, alignment=TA_CENTER),
    cell_hdr=ParagraphStyle('cell_hdr',  fontName='Helvetica-Bold',
                            fontSize=8,  leading=11, textColor=NAVY, alignment=TA_LEFT),
    cell_b=ParagraphStyle(
        'cell_b',    fontName='Helvetica-Bold', fontSize=8,  leading=11),
    cell_num=ParagraphStyle('cell_num',  fontName='Helvetica',
                            fontSize=8,  leading=11, alignment=TA_RIGHT),
    cell_num_b=ParagraphStyle(
        'cell_num_b', fontName='Helvetica-Bold', fontSize=8,  leading=11, alignment=TA_RIGHT),
    right=ParagraphStyle('right',     fontName='Helvetica',
                         fontSize=7.5, leading=10, alignment=TA_RIGHT, textColor=MUTED),
    placeholder=ParagraphStyle('placeholder', fontName='Helvetica-Oblique',
                               fontSize=9, leading=13, alignment=TA_CENTER, textColor=MUTED),
)


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

    def _draw_chrome(self, page_num: int, total: int):
        self._draw_watermark()
        self._draw_header()
        self._draw_footer(page_num, total)

    def _draw_header(self):
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

    def _draw_footer(self, page_num: int, total: int):
        self.setFont('Helvetica', 7)
        self.setFillColor(MUTED)
        self.drawRightString(PAGE_W - MARGIN, 6, f'Page {page_num} of {total}')

    def _draw_watermark(self):
        self.saveState()
        self.setFillColor(WM_CLR)
        self.translate(PAGE_W / 2, PAGE_H / 2)
        self.rotate(35)
        self.setFont('Helvetica-Bold', 72)
        self.drawCentredString(0, 0, 'Credhive')
        self.restoreState()



class CreditPdfMaker:

    def __init__(self, data: SampleInputModel):
        self.data = data

    @staticmethod
    def _make_banner(title: str):
        t = Table([[Paragraph(title, _S['banner'])]], colWidths=[BODY_W])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), NAVY),
            ('TOPPADDING',    (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING',   (0, 0), (-1, -1), 8),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ]))
        return t

    @staticmethod
    def _fmt_value(val, growth):
        if val is None:
            return ''
        txt = f'{val:.2f}'
        if growth is None:
            return txt
        if growth >= 0:
            return f'{txt} <font color="#2E7D32">↑{growth:.1f}%</font>'
        return f'{txt} <font color="#C62828">↓{abs(growth):.1f}%</font>'

    def _build_auditors(self):
        recent = self.data.sections.auditors[0]

        col_w = [50*mm, 55*mm, 55*mm, 107*mm]
        hdr = [Paragraph(t, _S['cell_hdr']) for t in
               ['Fiscal Year', 'Auditor Name', 'Auditor Firm Name', 'Address']]

        name_cell = [
            Paragraph(recent.auditor_name, _S['cell']),
            Paragraph(f'Membership No. {recent.membership_no}', _S['cell_sm']),
            Paragraph(f'PAN: {recent.pan}', _S['cell_sm']),
        ]
        row = [
            Paragraph(recent.fiscal_year, _S['cell_c']),
            name_cell,
            Paragraph(recent.firm_name,   _S['cell']),
            Paragraph(recent.address,     _S['cell']),
        ]

        cmds = [
            ('BACKGROUND',    (0, 0), (-1, 0),  YELLOW),
            ('BOX',           (0, 0), (-1, -1), 0.5, BORDER),
            ('INNERGRID',     (0, 0), (-1, -1), 0.5, BORDER),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
            ('TOPPADDING',    (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('VALIGN',        (0, 1), (-1, -1), 'TOP'),
        ]

        tbl = Table([hdr, row], colWidths=col_w)
        tbl.setStyle(TableStyle(cmds))
        return [Spacer(1, 4*mm), self._make_banner('AUDITORS - STANDALONE'), Spacer(1, 3*mm), tbl]

    def _build_financial_table(self, section, banner_title: str,cell_formatter=None, show_currency_note=True):
        periods = section.periods
        n = len(periods)
        part_w = 75 * mm
        val_w  = (BODY_W - part_w) / n
        col_w  = [part_w] + [val_w] * n

        if cell_formatter is None:
            def cell_formatter(row, i):
                val = row.values[i]     if row.values     and i < len(row.values)     else None
                gro = row.growth_pct[i] if row.growth_pct and i < len(row.growth_pct) else None
                return self._fmt_value(val, gro)

        hdr = [Paragraph('Particulars', _S['cell_hdr'])]
        for p in periods:
            hdr.append(Paragraph(p, _S['cell_hdr']))

        table_rows = [hdr]
        cmds = [
            ('BACKGROUND',    (0, 0), (-1, 0),  YELLOW),
            ('BOX',           (0, 0), (-1, -1), 0.5, BORDER),
            ('INNERGRID',     (0, 0), (-1, -1), 0.5, BORDER),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
            ('TOPPADDING',    (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ]

        for group in section.groups:
            if group.title:
                ri = len(table_rows)
                table_rows.append([Paragraph(group.title, _S['cell_b'])] + [''] * n)
                cmds += [
                    ('BACKGROUND', (0, ri), (-1, ri), SUBTOTAL_BG),
                    ('SPAN',       (0, ri), (-1, ri)),
                ]

            for row in group.rows:
                ri = len(table_rows)
                p_sty = _S['cell_b']     if row.is_subtotal else _S['cell']
                v_sty = _S['cell_num_b'] if row.is_subtotal else _S['cell_num']

                cells = [Paragraph(row.particular, p_sty)]
                for i in range(n):
                    cells.append(Paragraph(cell_formatter(row, i), v_sty))

                table_rows.append(cells)
                if row.is_subtotal:
                    cmds.append(('BACKGROUND', (0, ri), (-1, ri), SUBTOTAL_BG))

        tbl = Table(table_rows, colWidths=col_w)
        tbl.setStyle(TableStyle(cmds))

        flowables = [Spacer(1, 4*mm), self._make_banner(banner_title), Spacer(1, 2*mm)]
        if show_currency_note:
            currency_unit = self.data.report_meta.currency_unit
            flowables += [Paragraph(f'(Amount in {currency_unit})', _S['right']), Spacer(1, 1*mm)]
        flowables.append(tbl)
        return flowables

    def _build_profit_loss_section(self):
        return self._build_financial_table(
            self.data.sections.profit_and_loss,
            'PROFIT AND LOSS - STANDALONE',
        )

    def _build_balance_sheet(self):
        return self._build_financial_table(
            self.data.sections.balance_sheet,
            'BALANCE SHEET - STANDALONE',
        )

    def _build_auditor_comments(self):
        comments = self.data.sections.auditor_comments
        col_w = [40*mm, 30*mm, 98.5*mm, 98.5*mm]
        hdr = [Paragraph(t, _S['cell_hdr']) for t in [
            'Financial Year', 'Has Adverse Remarks',
            'Auditor Report Disclosure', 'Director Report Disclosure',
        ]]

        table_rows = [hdr]
        for c in comments:
            remarks_color = '#C62828' if c.has_adverse_remarks.upper() == 'YES' else '#2E7D32'
            remarks_cell = Paragraph(
                f'<font color="{remarks_color}"><b>{c.has_adverse_remarks}</b></font>',
                _S['cell_c'],
            )
            table_rows.append([
                Paragraph(c.financial_year,             _S['cell_c']),
                remarks_cell,
                Paragraph(c.auditor_report_disclosure,  _S['cell']),
                Paragraph(c.director_report_disclosure, _S['cell']),
            ])

        cmds = [
            ('BACKGROUND',    (0, 0), (-1, 0),  YELLOW),
            ('BOX',           (0, 0), (-1, -1), 0.5, BORDER),
            ('INNERGRID',     (0, 0), (-1, -1), 0.5, BORDER),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('VALIGN',        (0, 0), (-1, 0),  'MIDDLE'),
        ]

        tbl = Table(table_rows, colWidths=col_w)
        tbl.setStyle(TableStyle(cmds))
        return [Spacer(1, 4*mm), self._make_banner('AUDITOR COMMENTS'), Spacer(1, 3*mm), tbl]

    @staticmethod
    def _fmt_ratio_value(val, unit, growth_pct, growth_delta):
        if val is None:
            return ''
        if unit == 'percent':
            txt = f'{val:.2f}%'
        elif unit == 'days':
            txt = f'{int(round(val))} days'
        else:
            txt = f'{val:.2f}x'

        if unit == 'days' and growth_delta is not None:
            d = int(round(growth_delta))
            color = '#C62828' if d > 0 else '#2E7D32'
            sign  = '+' if d > 0 else ''
            return f'{txt} <font color="{color}">{sign}{d} days</font>'
        if growth_pct is not None:
            if growth_pct >= 0:
                return f'{txt} <font color="#2E7D32">↑{growth_pct:.1f}%</font>'
            return f'{txt} <font color="#C62828">↓{abs(growth_pct):.1f}%</font>'
        return txt

    def _build_financial_ratios(self):
        # for financial ratio the formatter is change, in this we have to take care of it by units in the data
        def fmt(row, i):
            val = row.values[i]       if row.values       and i < len(row.values)       else None
            gro = row.growth_pct[i]   if row.growth_pct   and i < len(row.growth_pct)   else None
            dlt = row.growth_delta[i] if row.growth_delta and i < len(row.growth_delta) else None
            return self._fmt_ratio_value(val, row.unit, gro, dlt)

        return self._build_financial_table(
            self.data.sections.financial_ratios,
            'FINANCIAL RATIOS',
            cell_formatter=fmt,
            show_currency_note=False,
        )

    def _build_cash_flow(self):
        cf = self.data.sections.cash_flow
        if cf is None or not cf.available:
            return [
                Spacer(1, 4*mm),
                self._make_banner('CASH FLOW - STANDALONE'),
                Spacer(1, 6*mm),
                Paragraph('Cash Flow Statement Not Available',
                          _S['placeholder']),
                Spacer(1, 4*mm),
            ]
        return self._build_financial_table(cf, 'CASH FLOW - STANDALONE')

    def build(self, output_path: Path):
        # this func will build the whole pdf by adding pages with header footer and bookmark to all the data
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=PAGE_SIZE,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=HDR_H + MARGIN,
            bottomMargin=MARGIN,
        )
        story = []
        story += self._build_auditors()
        story += self._build_profit_loss_section()
        story += self._build_balance_sheet()
        story += self._build_auditor_comments()
        story += self._build_financial_ratios()
        story += self._build_cash_flow()
        doc.build(story, canvasmaker=_canvas_factory(self.data))


def _canvas_factory(data: SampleInputModel):
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
    CreditPdfMaker(data).build(output_path)
