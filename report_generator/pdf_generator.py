from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, PageBreak, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from report_generator.schemas import SampleInputModel
from report_generator.styles import (
    PAGE_SIZE, PAGE_W, PAGE_H, MARGIN, HDR_H, BODY_W,
    NAVY, L_BLUE, OFF_WHT, MUTED, WM_CLR,
    ALT_BG, BORDER, YELLOW, SUBTOTAL_BG, GREEN, RED,
    _S,
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


class _BannerTable(Table):
    # for registering all the banners for inner content
    def __init__(self, data, toc_text='', **kwargs):
        super().__init__(data, **kwargs)
        self.toc_text = toc_text
        self.toc_level = 1


class _TocEntry(Paragraph):
    # it is for header with A,B,C
    def __init__(self, text, style, level=0):
        super().__init__(text, style)
        self.toc_text = text
        self.toc_level = level


class _CreditDocTemplate(SimpleDocTemplate):
    # wrapped simpledoctemplate class for triggerring auto table of content

    def afterFlowable(self, flowable):
        if getattr(flowable, 'toc_text', '') and hasattr(flowable, 'toc_level'):
            self.notify('TOCEntry', (flowable.toc_level,
                        flowable.toc_text, self.page))


class CreditPdfMaker:

    def __init__(self, data: SampleInputModel):
        self.data = data

    @staticmethod
    def _make_banner(title: str, toc: bool = True):
        data = [[Paragraph(title, _S['banner'])]]
        t = (_BannerTable(data, toc_text=title, colWidths=[BODY_W])
             if toc else Table(data, colWidths=[BODY_W]))
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
        # show only the most recent auditor; older years go to Annexure via _build_annexure
        auditors = self.data.sections.auditors
        if not auditors:
            return [Spacer(1, 4*mm), self._make_banner('AUDITORS - STANDALONE'),
                    Spacer(1, 6*mm), Paragraph('No auditor data available', _S['placeholder']),
                    Spacer(1, 4*mm)]
        recent = auditors[0]

        col_w = [28*mm, 38*mm, 40*mm, BODY_W - 106*mm]
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
        part_w = 60 * mm
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
        col_w = [25*mm, 22*mm, (BODY_W - 47*mm) / 2, (BODY_W - 47*mm) / 2]
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

    @staticmethod
    def _build_related_party_subtable(subtitle: str, entries: list, col_w: list, hdrs: list):
        hdr_row = [Paragraph(h, _S['cell_hdr']) for h in hdrs]
        table_rows = [hdr_row]
        cmds = [
            ('BACKGROUND',    (0, 0), (-1, 0),  YELLOW),
            ('BOX',           (0, 0), (-1, -1), 0.5, BORDER),
            ('INNERGRID',     (0, 0), (-1, -1), 0.5, BORDER),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ]
        n = len(hdrs)
        if not entries:
            table_rows.append([Paragraph('No data available', _S['placeholder'])] + [''] * (n - 1))
            cmds.append(('SPAN', (0, 1), (-1, 1)))
        else:
            for entry in entries:
                if isinstance(entry, dict):
                    name     = entry.get('name', '')    or ''
                    relation = entry.get('relation', '') or ''
                    details  = entry.get('details', {}) or {}
                else:
                    name     = entry.name     or ''
                    relation = entry.relation or ''
                    details  = entry.details  or {}
                details_text = '  '.join(f'{k}: {v}' for k, v in details.items()) if details else ''
                table_rows.append([
                    Paragraph(name,         _S['cell']),
                    Paragraph(relation,     _S['cell']),
                    Paragraph(details_text, _S['cell']),
                ])

        sub_hdr = Table([[Paragraph(subtitle, _S['cell_b'])]], colWidths=[BODY_W])
        sub_hdr.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), SUBTOTAL_BG),
            ('BOX',           (0, 0), (-1, -1), 0.5, BORDER),
            ('LEFTPADDING',   (0, 0), (-1, -1), 8),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        tbl = Table(table_rows, colWidths=col_w)
        tbl.setStyle(TableStyle(cmds))
        return [Spacer(1, 3*mm), sub_hdr, tbl]

    def _build_related_parties(self):
        rp = self.data.sections.related_parties
        if rp is None:
            return []

        col_w = [55*mm, 55*mm, BODY_W - 110*mm]
        hdrs  = ['Name', 'Relation', 'Details']

        flowables = [Spacer(1, 4*mm), self._make_banner('RELATED PARTIES')]
        if rp.period:
            flowables += [Spacer(1, 2*mm), Paragraph(f'Period: {rp.period}', _S['right'])]

        for subtitle, entries in [
            ('INDIVIDUALS', rp.individuals or []),
            ('COMPANIES',   rp.companies   or []),
            ('OTHERS',      rp.others      or []),
        ]:
            flowables += self._build_related_party_subtable(subtitle, entries, col_w, hdrs)

        return flowables

    def _build_annexure(self):
        ann = self.data.sections.annexure
        older_auditors = self.data.sections.auditors[1:]

        if ann is None and not older_auditors:
            return []

        flowables = []
        has_content = False

        # older auditor years
        if older_auditors:
            has_content = True
            col_w = [28*mm, 38*mm, 40*mm, BODY_W - 106*mm]
            hdr = [Paragraph(t, _S['cell_hdr']) for t in
                   ['Fiscal Year', 'Auditor Name', 'Auditor Firm Name', 'Address']]
            table_rows = [hdr]
            for a in older_auditors:
                name_cell = [
                    Paragraph(a.auditor_name, _S['cell']),
                    Paragraph(f'Membership No. {a.membership_no}', _S['cell_sm']),
                    Paragraph(f'PAN: {a.pan}', _S['cell_sm']),
                ]
                table_rows.append([
                    Paragraph(a.fiscal_year, _S['cell_c']),
                    name_cell,
                    Paragraph(a.firm_name,   _S['cell']),
                    Paragraph(a.address,     _S['cell']),
                ])
            cmds = [
                ('BACKGROUND',    (0, 0), (-1, 0),  YELLOW),
                ('BOX',           (0, 0), (-1, -1), 0.5, BORDER),
                ('INNERGRID',     (0, 0), (-1, -1), 0.5, BORDER),
                ('LEFTPADDING',   (0, 0), (-1, -1), 6),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
                ('TOPPADDING',    (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('VALIGN',        (0, 0), (-1, 0),  'MIDDLE'),
                ('VALIGN',        (0, 1), (-1, -1), 'TOP'),
            ]
            tbl = Table(table_rows, colWidths=col_w)
            tbl.setStyle(TableStyle(cmds))
            flowables += [Spacer(1, 3*mm), self._make_banner('AUDITORS - ANNEXURE'), Spacer(1, 3*mm), tbl]

        if ann is None:
            return flowables

        if ann.profit_and_loss:
            has_content = True
            flowables += self._build_financial_table(
                ann.profit_and_loss, 'PROFIT AND LOSS - ANNEXURE',
            )

        if ann.balance_sheet:
            has_content = True
            flowables += self._build_financial_table(
                ann.balance_sheet, 'BALANCE SHEET - ANNEXURE',
            )

        if ann.financial_ratios:
            has_content = True
            def fmt(row, i):
                val = row.values[i]       if row.values       and i < len(row.values)       else None
                gro = row.growth_pct[i]   if row.growth_pct   and i < len(row.growth_pct)   else None
                dlt = row.growth_delta[i] if row.growth_delta and i < len(row.growth_delta) else None
                return self._fmt_ratio_value(val, row.unit, gro, dlt)
            flowables += self._build_financial_table(
                ann.financial_ratios, 'FINANCIAL RATIOS - ANNEXURE',
                cell_formatter=fmt, show_currency_note=False,
            )

        if not has_content:
            flowables += [
                Spacer(1, 6*mm),
                Paragraph('No annexure data available', _S['placeholder']),
                Spacer(1, 4*mm),
            ]

        return flowables

    def _build_disclaimer(self):
        meta = self.data.report_meta
        name = meta.marked_to.name
        org  = meta.marked_to.organization
        marked_line = (
            f'Marked To: <b>{name}</b> from <b>{org}</b>'
        )
        return [
            PageBreak(),
            _TocEntry('C. Disclaimer and Confidentiality',
                      _S['disc_heading'], level=0),
            Paragraph(marked_line,                         _S['disc_marked']),
            Paragraph(meta.disclaimer_text,                _S['disc_body']),
        ]

    def _build_toc(self):
        toc = TableOfContents()
        toc.dotsMinLevel = 0
        toc.levelStyles = [
            ParagraphStyle('TOCLevel0', fontName='Helvetica-Bold', fontSize=10,
                           leftIndent=0, spaceBefore=5, spaceAfter=2, leading=14),
            ParagraphStyle('TOCLevel1', fontName='Helvetica', fontSize=9,
                           leftIndent=10*mm, spaceBefore=2, spaceAfter=1, leading=12,
                           textColor=MUTED),
        ]
        return [
            self._make_banner('TABLE OF CONTENTS', toc=False),
            Spacer(1, 4*mm),
            toc,
            PageBreak(),
        ]

    def build(self, output_path: Path):
        # this func will build the whole pdf by adding pages with header footer and bookmark to all the data
        doc = _CreditDocTemplate(
            str(output_path),
            pagesize=PAGE_SIZE,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=HDR_H + MARGIN,
            bottomMargin=MARGIN,
        )
        story = []

        # TOC must be first so multiBuild can populate it
        story += self._build_toc()

        # Section A: Financial Information
        story += [
            _TocEntry('A. Financial Information', _S['disc_heading'], level=0),
            Paragraph('STANDALONE FINANCIALS', _S['section']),
            Spacer(1, 2*mm),
        ]
        story += self._build_auditors()
        story += self._build_profit_loss_section()
        story += self._build_balance_sheet()
        story += self._build_auditor_comments()
        story += self._build_financial_ratios()
        story += self._build_cash_flow()
        story += self._build_related_parties()

        # Section B: Annexure (only if there is content to show)
        annexure = self._build_annexure()
        if annexure:
            story += [
                PageBreak(),
                _TocEntry('B. Annexure', _S['disc_heading'], level=0),
                Paragraph('STANDALONE FINANCIAL ANNEXURE', _S['section']),
            ]
            story += annexure

        # Section C: Disclaimer — has its own PageBreak
        story += self._build_disclaimer()

        doc.multiBuild(story, canvasmaker=_canvas_factory(self.data))


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
