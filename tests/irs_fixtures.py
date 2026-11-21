"""Synthetic integration inputs and Catala rendering; no personal data."""
from decimal import Decimal


def money(value):
    value = Decimal(str(value))
    return ("-" if value < 0 else "") + "$" + format(abs(value), ".2f")


def holder(a=0, h=0, dependent=False, **overrides):
    return {"dependente": dependent, "bruto_a": a, "bruto_h": h,
            "contribuicoes_a": 0, "indemnizacoes": 0, "sindicato_a": 0,
            "ordens": 0, "contribuicoes_h": 0, "sindicato_h": 0,
            "pensoes_elegiveis": True, **overrides}


EXPENSES = ("gerais", "saude", "educacao", "rendas_estudante", "rendas", "juros",
            "iva_servicos", "iva_transportes", "iva_medicamentos_veterinarios",
            "iva_publicacoes", "iva_desporto")


def case(name, holders, **overrides):
    return {"id": name, "ano": 2025, "residente": True,
            "apenas_regime_geral_a_h": True, "apenas_creditos_implementados": True,
            "titulares_integrais": True, "conjunta": False,
            "elegivel_conjunta": True, "separada": False, "monoparental": False,
            "titulares": holders, "dependentes": [], "ascendentes": 0,
            "ascendentes_partilhados": 0, "despesas": {}, "consignar_iva": False,
            "retencoes": 0, "pagamentos_por_conta": 0, **overrides}


def record(name, values):
    return name + " { " + " ".join(f"-- {k}: {v}" for k, v in values.items()) + " }"


def scalar(value):
    return str(value).lower() if isinstance(value, bool) else str(value)


def render(c, scope="Check", assertion="", annotated=False):
    fields = {k: scalar(c[k]) for k in (
        "ano", "residente", "apenas_regime_geral_a_h", "apenas_creditos_implementados",
        "titulares_integrais", "conjunta", "elegivel_conjunta", "separada", "monoparental",
        "ascendentes", "ascendentes_partilhados", "consignar_iva")}
    fields["titulares"] = "[" + "; ".join(record("Irs_2025.Titular", {
        k: scalar(v) if isinstance(v, bool) else money(v) for k, v in t.items()
    }) for t in c["titulares"]) + "]"
    fields["dependentes"] = "[" + "; ".join(record("Art_078_a.Dependente", {
        k: scalar(v) for k, v in d.items()}) for d in c["dependentes"]) + "]"
    fields["despesas"] = record("Irs_2025.Despesas", {
        k: money(c["despesas"].get(k, 0)) for k in EXPENSES})
    fields.update({k: money(c[k]) for k in ("retencoes", "pagamentos_por_conta")})
    return ("\n```catala\n" + ("#[test]\n" if annotated else "")
            + f"declaration scope {scope}:\n  output resultado content Irs_2025.Declaracao\n"
            + f"scope {scope}:\n  definition resultado equals output of Irs_2025.Declaracao with {{\n"
            + "\n".join(f"    -- {k}: {v}" for k, v in fields.items()) + "\n  }\n"
            + (f"  assertion ({assertion})\n" if assertion else "") + "```\n")
