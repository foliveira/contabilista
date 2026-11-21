<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
    <img src="assets/logo.svg" alt="contabilista logo" width="128" height="128">
  </picture>
</p>

# contabilista

Portugal's personal income tax law, the Código do IRS, written as a computer program.

Each file holds one article of the law. The law text is in Portuguese, and the code for that article sits right under it. You can read the law and the code side by side and check that they say the same thing. You can also run the code to work out how much tax a person owes.

The code is written in [Catala](https://catala-lang.org), a programming language made for turning laws into code.

> [!WARNING]
> This is a research project. Do not use it to file a tax return, and do not treat its results as tax advice. No result has been checked against the tax authority's (AT) own simulator yet.

## What it can do

It works for the 2025 tax year, for people who:

- live in Portugal for tax purposes (residents)
- earn money from a job (category A), a pension (category H), or both
- file alone or as a couple

For these people it works out the whole return. It takes the income, subtracts the allowed deductions, applies the tax rates and the extra solidarity tax on high incomes, and protects the minimum income that the law does not tax. Then it subtracts the tax credits for family, health, education, housing and invoices, and tells you if you have to pay more or will get money back.

Some facts you have to give it yourself, because the program does not decide them. For example, you say whether you can file as a couple and which of your expenses count.

Other kinds of income, other years and special tax regimes are not done yet. If you give the program something it does not support, it stops with an error. It never guesses.

These articles are done so far:

| Article | What it covers |
|---------|----------------|
| 22 (n.º 1) | Adding up job and pension income |
| 25 | Deductions from job income |
| 53 | Deductions from pension income |
| 68 | Tax rates |
| 68-A | Extra solidarity tax on high incomes |
| 69 | Couples who file together |
| 70 | The minimum income that is not taxed (mínimo de existência) |
| 78 to 78-F | Tax credits for family, health, education, housing and invoices |

## How to use it

### 1. Install Catala

You need Catala 1.3.0. Install it with opam, the OCaml package manager:

```sh
opam init -c 4.14.2 --shell-setup
eval $(opam env)
opam update && opam install catala.1.3.0
```

This also installs `clerk`, the tool that builds and runs Catala code.

### 2. Run the tests

From the top folder of this repository:

```sh
clerk test
```

All 27 tests should pass.

### 3. See a full tax return

```sh
clerk run tests/test_declaracao_2025.catala_en --scope=TesteDeclaracao0
```

This shows the result for one person who earned €20,000 from a job in 2025 and had €2,000 of tax taken from their pay. The tax due is €1,524.73, so they get €475.27 back.

### 4. Try your own numbers

1. Open `tests/test_declaracao_2025.catala_en`.
2. Copy the first example: every line from `` ```catala `` down to the closing `` ``` ``. Paste it at the end of the file.
3. In your copy, change the name `TesteDeclaracao0` to a new name, in both places it appears.
4. Change the amounts. The main ones are listed below.
5. Delete the `assertion` line. It checks the expected answer, and your numbers will give a different one.
6. Run it: `clerk run tests/test_declaracao_2025.catala_en --scope=YourNewName`

| Name in the code | What it means |
|------------------|---------------|
| `bruto_a` | Gross income from a job |
| `contribuicoes_a` | Social security paid on that job income |
| `bruto_h` | Gross income from pensions |
| `conjunta` | `true` if you file as a couple |
| `despesas` | Your expenses: `gerais` (general), `saude` (health), `educacao` (education), `rendas` (rent), and others |
| `retencoes` | Tax already taken from your pay during the year |

In the result, `imposto_devido` is the tax due, `a_pagar` is what you still have to pay, and `reembolso` is what you get back.

### Other checks

If you use [mise](https://mise.jdx.dev) and already have OCaml 4.14.2 and Catala 1.3.0 installed, `mise run setup` checks your tools and `mise run test` runs the tests. `mise run setup` does not install anything.

There are also Python tests. They check that the program refuses inputs it does not support, and they compare some articles with answers worked out by hand. You need Python 3.9 or newer and `catala` on your PATH:

```sh
python -m unittest discover -s tests -p 'test_*.py'
```

## What is in this repository

| Path | What it holds |
|------|---------------|
| `cirs/` | The articles of the Código do IRS, one file per article |
| `cirs/irs_2025.catala_en` | The full 2025 tax return, built from the articles |
| `tests/` | Tests and examples |
| `clerk.toml` | Settings for `clerk` |
| `PLAN.md` | The plan, the work left to do, and open questions |

## How the code is written

- The law text stays in Portuguese.
- Names in the code are Portuguese words without accents, like `rendimento_coletavel` (taxable income), so they match the words in the law.
- Catala keywords are in English, because Catala has no Portuguese version.
- The tax year is an input. Only 2025 works for now.
- When the law says how to work something out, the code does exactly that, even if a simpler formula would give almost the same number.

## Sources

The law text comes from the Diário da República and from AT's Portal das Finanças. The 2025 tax rates come from Lei n.º 55-A/2025, de 22 de julho.

## License

Copyright 2026 Fabio Oliveira. Licensed under the EUPL-1.2. The full text is in [LICENSE](LICENSE).
