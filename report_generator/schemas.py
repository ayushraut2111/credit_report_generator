from __future__ import annotations
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel


class CompanyModel(BaseModel):
    name: str
    cin: str


class MarkedToModel(BaseModel):
    name: str
    organization: str


class ReportMetaModel(BaseModel):
    generated_at: datetime
    marked_to: MarkedToModel
    currency_unit: str
    disclaimer_text: str


class AuditorModel(BaseModel):
    fiscal_year: str
    auditor_name: str
    membership_no: str
    pan: str
    firm_name: str
    address: str
    firm_reg_no: Optional[str] = None


class RowModel(BaseModel):
    particular: str
    values: Optional[List[Optional[float]]] = None
    growth_pct: Optional[List[Optional[float]]] = None
    growth_delta: Optional[List[Optional[float]]] = None
    is_subtotal: bool
    unit: Optional[str] = None


class GroupModel(BaseModel):
    title: Optional[str]
    rows: List[RowModel]


class ProfitAndLossModel(BaseModel):
    periods: List[str]
    groups: List[GroupModel]


class BalanceSheetModel(BaseModel):
    periods: List[str]
    groups: List[GroupModel]


class AuditorCommentModel(BaseModel):
    financial_year: str
    has_adverse_remarks: str
    auditor_report_disclosure: str
    director_report_disclosure: str


class FinancialRatiosModel(BaseModel):
    periods: List[str]
    groups: List[GroupModel]


class RelatedPartyModel(BaseModel):
    name: Optional[str] = None
    relation: Optional[str] = None
    details: Optional[dict] = None


class AnnexureModel(BaseModel):
    profit_and_loss: Optional[ProfitAndLossModel] = None
    balance_sheet: Optional[BalanceSheetModel] = None
    financial_ratios: Optional[FinancialRatiosModel] = None
    others: Optional[dict] = None


class RelatedPartiesSectionModel(BaseModel):
    period: Optional[str] = None
    individuals: Optional[List[Any]] = None
    companies: Optional[List[Any]] = None
    others: Optional[List[Any]] = None


class CashFlowModel(BaseModel):
    available: bool = True
    periods: Optional[List[str]] = None
    groups: Optional[List[GroupModel]] = None


class SectionsModel(BaseModel):
    auditors: List[AuditorModel]
    profit_and_loss: ProfitAndLossModel
    balance_sheet: BalanceSheetModel
    auditor_comments: List[AuditorCommentModel]
    financial_ratios: FinancialRatiosModel
    cash_flow: Optional[CashFlowModel] = None
    related_parties: Optional[RelatedPartiesSectionModel] = None
    annexure: Optional[AnnexureModel] = None


class SampleInputModel(BaseModel):
    company: CompanyModel
    report_meta: ReportMetaModel
    sections: SectionsModel
