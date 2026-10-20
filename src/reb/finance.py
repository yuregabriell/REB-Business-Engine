"""Deterministic financial calculations. NOT financial advice or revenue predictions."""
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from .errors import REBError


def money(value, *, allow_negative: bool = True) -> Decimal:
    if isinstance(value, bool):
        raise REBError("Valor monetário inválido.")
    try:
        d = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise REBError("Valor monetário inválido.") from None
    if not d.is_finite() or (not allow_negative and d < 0):
        raise REBError("Valor monetário deve ser finito e não-negativo.")
    return d


def financial_scenario(price, variable_cost, fixed_cost, units, cash="0", customer_acquisition_cost="0") -> dict:
    """One period, single service/product; CAC is a cost per sold unit for this model."""
    p = money(price, allow_negative=False)
    v = money(variable_cost, allow_negative=False)
    f = money(fixed_cost, allow_negative=False)
    c = money(cash, allow_negative=False)
    cac = money(customer_acquisition_cost, allow_negative=False)
    if isinstance(units, bool) or not isinstance(units, int) or units < 0:
        raise REBError("Quantidade deve ser um inteiro não negativo.")
    if units > 10**9:
        raise REBError("Quantidade fora de limite suportado.")
    contribution = p - v - cac
    revenue = p * units
    variable_total = (v + cac) * units
    total_cost = variable_total + f
    operating_result = revenue - total_cost
    breakeven = int((f / contribution).to_integral_value(rounding=ROUND_CEILING)) if contribution > 0 else None
    runway = (c / f) if f > 0 else None
    return {
        "currency": "EUR (valores nominais; altere moeda por contexto)",
        "price": str(p), "variable_cost": str(v), "customer_acquisition_cost": str(cac),
        "fixed_cost": str(f), "units": units, "revenue": str(revenue),
        "total_cost": str(total_cost), "operating_result": str(operating_result),
        "contribution_per_unit": str(contribution), "breakeven_units": breakeven,
        "contribution_margin": str((contribution / p * 100).quantize(Decimal("0.01"))) if p else None,
        "runway_periods_without_sales": str(runway.quantize(Decimal("0.01"))) if runway is not None else None,
        "warnings": ["Cenário, não previsão. Não inclui impostos, IVA, depreciação, reembolsos, juros ou sazonalidade."] + (["Margem unitária não-positiva; não há ponto de equilíbrio finito com estas premissas."] if contribution <= 0 else []),
    }


def investment_gate(project_budget, proposed_cost, evidence_count: int, *, action_type: str = "spend", approved: bool = False) -> dict:
    budget = money(project_budget, allow_negative=False)
    proposed = money(proposed_cost, allow_negative=False)
    if evidence_count < 0:
        raise REBError("Contagem de evidências inválida.")
    reasons = []
    if proposed > budget:
        reasons.append("Investimento superior ao orçamento registado.")
    if evidence_count == 0:
        reasons.append("Sem evidências registadas: testar pressupostos antes de gastar.")
    if action_type in {"spend", "publish", "contact", "contract", "hire"} and not approved:
        reasons.append("Ação externa exige autorização explícita do utilizador.")
    return {"allowed": not reasons, "reasons": reasons, "remaining_if_approved": str(budget - proposed), "estimated_cost": str(proposed), "action_type": action_type}
