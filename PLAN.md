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

## Implementation progress

- Articles 25, 53, 68, 68-A, 70, 78 to 78-F and 69, plus art. 22 n.º 1 for
  ordinary resident A/H returns, implemented for 2025; 27 test scopes pass with
  Catala 1.3.0 and the OCaml target builds.
- `cirs/irs_2025.catala_en` composes the full return: one entry per holder
  (including a zero-income spouse), per-holder A+H deductions, one art. 70 call
  per holder over combined gross, aggregation, rates, credits and settlement.
  Household totals, filing flags and credit-limit income are derived, not
  independently supplied. Split dependent/co-owned income and low-income
  monoparental returns are rejected (the latter because the low-level art. 70
  scope uses the ordinary €250 limit, not the €335 monoparental limit).
- Articles 25/53 take eligible expenses as inputs and operate per holder.
  Non-qualifying annuities require art. 54 and are rejected by the pension scope.
- Art. 22 aggregates net A/H income per holder after category deductions.
  Allocation under n.os 2/8 remains a caller responsibility; non-residents,
  special regimes and exempt income affecting the rate are rejected. Separate
  Python-driven Catala checks exercise these guards and invalid amounts/years.
- Art. 69 divides household taxable income by two, applies art. 68 and
  doubles the result. Tests cover bracket limits, odd cents, input guards
  and integration with art. 22. Eligibility for joint filing is caller-attested.
- Art. 70 keeps the literal formula. AT's published 2025 page shows the same
  ambiguous `Limite despesas gerais/Taxa 1.º escalão x 3,60` text, so nothing
  new was learned from it. An exact-rational reference test now checks six
  hand-worked cases against the scope. The a)/c) overlap between €7,218.61 and
  €12,180 is preserved as an explicit failure rather than hidden by an
  unwritten priority. Expected abatement values: €5,585.85 for a dependent with
  €13,000 gross and €4,462.15 deductions; zero for an ordinary holder at that
  income (L is €14,418.61 / €7,218.61 respectively — L is not the abatement).
- Exact rational oracles also cover the art. 68 bracket matrix (including
  exact limits), art. 69's provisional double rounding, and art. 68-A.
- Next: AT simulator comparisons and the rounding/bracket-limit questions
  below remain outstanding. A sweep over household profiles up to €500,000
  was attempted against the compiled OCaml target but was abandoned: the
  environment cannot link the generated runtime (missing libgmp linker
  alias), and a hand-copied reimplementation of the calculation would not
  exercise the real code. Also missing: the simulator-verified case set that
  milestone 1 requires (20+ cases).

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
- Art. 68 n.º 2 taxes income up to the last full bracket at the column B average rate, which the law rounds to three decimals. AT derives its "parcela a abater" table from column B, so the two methods agree to within a cent everywhere except at the bracket limits. When income equals a limit exactly, n.º 2 applies that bracket's own rounded column B rate and the parcela table doesn't, so the results differ by up to €0.27 (at €83,696). The parcela table is an independent check away from the limits. A plain marginal calculation differs by a few cents (third bracket: €950.91 from column B, €950.87 marginal), so it is not used as a reference.
- End-to-end cases are checked against AT's 2025 IRS simulator on Portal das Finanças.
- A sweep over a fixed set of household profiles computes net income at every euro up to €500,000 and flags any point where net income drops as gross income rises.

## Open questions

- Art. 68 at an exact bracket limit: the code follows n.º 2, which gives a different amount from AT's parcela table and makes the tax drop at some limits (€11,969.86 at €44,986.99, €11,969.69 at €44,987.00). Check what AT's simulator gives at €12,160, €44,987 and €83,696.
- Rounding: the law doesn't say how to round the result of art. 68. Under n.º 2, every whole-euro income in the second bracket gives an amount ending in half a cent (€8,059 × 12.5% = €1,007.375). Catala rounds half away from zero, and AT's parcela table gives one cent less. The simulator will show which rule AT applies.
- Art. 69 rounding: the current money-valued composition rounds RC / 2 to
  cents, applies art. 68 with its own cent rounding, then doubles that amount.
  The law does not prescribe these intermediate rounding steps. Check odd-cent
  incomes and bracket boundaries against AT before relying on the result;
  e.g. RC €0.07 currently gives quotient €0.04 and coleta €0.02.
- For 2026: n.º 2 still says "superior a 8059 €", but the 2026 table's first bracket ends at €8,342.

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

Two notes from setting this up on a machine without root apt access:

- The opam package `catala.1.3.0` includes both `catala` and `clerk`; there
  is no separate `clerk` package to install. `clerk` also needs `ninja` on PATH
  at runtime. `mise run setup` checks the existing shared 4.14.2 switch.
- `catala` depends on `zarith`, whose build needs the GMP headers (`libgmp-dev`).
  Without root, GMP (and `m4`, which GMP's `configure` needs) build from source
  into `~/.local`, with `C_INCLUDE_PATH`/`LIBRARY_PATH`/`LD_LIBRARY_PATH` pointing
  there. On that machine `mise.toml` pins `opam` and `ninja`, and its `test` task
  wires the opam switch in, so `mise run test` is the one-command way to run
  the tests.
