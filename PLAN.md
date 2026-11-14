# Plan: Portuguese IRS in Catala

## Goal

An executable formalisation of the Código do IRS (DL 442-A/88) in Catala. Each piece of code sits under the paragraph of law it implements, so someone who reads the law but not code can check one against the other.

## What gets formalised

Rules that reduce to arithmetic once the facts are known. Concepts that need judgement become inputs to the model instead of being decided by it: residency under art. 16 (the 183-day count is computable, "intenção de a manter" is not), which category an income belongs to, and the anti-abuse rules. Procedural rules such as deadlines and penalties under the RGIT are out of scope.

## Milestone 1: residents with category A and H income, tax year 2025

Scope: resident taxpayers with employment (A) and pension (H) income only, filing single or jointly.

Art. 68 comes first because it depends on no other article. The rest follow the order the calculation runs:

1. art. 68, general rates
2. art. 25 and 53, specific deductions for categories A and H
3. art. 22, aggregation and taxable income
4. art. 69, quociente conjugal for joint filing
5. art. 68-A, taxa adicional de solidariedade
6. art. 70, mínimo de existência
7. art. 78 to 78-F, deductions from tax

The milestone is done when:

- every article above has its law text and code under `cirs/`
- all tests pass under `clerk test`
- at least 20 hand-built cases give the same result as AT's 2025 IRS simulator, to the cent. The cases cover single and joint filing, A only, H only, A and H together, an income in each bracket, and incomes near the mínimo de existência.

## Later milestones

2. Categories B (simplified regime, art. 31), E, F and G, including capital gains (art. 43) and the special rates with the option to aggregate (art. 71, 72).
3. IRS Jovem (art. 12-B) and IFICI (EBF art. 58-A).
4. Tax year 2026 (Lei 73-A/2025 and later amendments).

## Conventions

- Catala 1.3.0 with the English surface syntax (`.catala_en`). Catala has no Portuguese syntax.
- One file per article. CIRS articles go in `cirs/`, EBF articles in `ebf/`. File names are zero-padded so they sort: `art_068.catala_en`, `art_068_a.catala_en`.
- Each file quotes the article's Portuguese text as Markdown, with the Catala code under the número or alínea it implements.
- Identifiers are in Portuguese without accents (`rendimento_coletavel`), matching the law's terms.
- Amounts use Catala's `money` type and rates use `decimal`. Where the law prescribes a method, the code follows it even when a simpler formula exists.
- Tax year is an input. Values that change by year are defined per year in the same file, with the amending law cited next to each one.

## Sources

- The 2025 law text comes from the version history on Diário da República and from the amending laws. Portal das Finanças shows only the current text, which already includes the 2026 changes.
- Art. 68 for 2025 is the table in Lei 55-A/2025 of 22 July. AT's leaflet "Taxas aplicáveis 2025" confirms it applies to all 2025 income.

## Testing

- Each article has unit tests with values worked out by hand.
- Art. 68 n.º 2 taxes income up to the last full bracket at the column B average rate, which the law rounds to three decimals. AT derives its "parcela a abater" table from column B, so the two methods agree to within a cent and the parcela table is an independent check. A plain marginal calculation differs by a few cents (third bracket: €950.91 from column B, €950.87 marginal), so it is not used as a reference.
- End-to-end cases are checked against AT's 2025 IRS simulator on Portal das Finanças.
- A sweep over a fixed set of household profiles computes net income at every euro up to €500,000 and flags any point where net income drops as gross income rises.

## Data

Test cases are synthetic. Real client returns need written client authorisation under YLD policy before they are used.

## Setup

Catala is installed through opam:

```sh
opam init -c 4.14.2 --shell-setup
eval $(opam env)
opam update && opam install catala.1.3.0
clerk --version
```

For the VS Code extension (`catalalang.catala`), also install `catala-lsp.1.3.0`.
