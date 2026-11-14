# contabilista

The Portuguese personal income tax code (Código do IRS) written as a program in [Catala](https://catala-lang.org).

Each file holds the text of one article of the law, in Portuguese, with the code for that article right under it. You can run the tax calculation, test it, and check each line of code against the law it comes from.

## Status

This project has just started.

- Article 68 (the general tax rates) for income earned in 2025 is written, with tests.
- The code has not been compiled yet.
- No result has been compared with the tax authority's (AT) simulator yet.

Do not use this to file a tax return or to give tax advice.

The plan, the scope and the open questions are in [PLAN.md](PLAN.md).

## What is in this repository

| Path | What it holds |
|------|---------------|
| `cirs/` | Articles of the Código do IRS, one file per article |
| `tests/` | Tests for each article |
| `clerk.toml` | Settings for `clerk`, the Catala build tool |
| `PLAN.md` | The plan and the open questions |

## How to run it

You need Catala 1.3.0. It installs through opam, the OCaml package manager:

```sh
opam init -c 4.14.2 --shell-setup
eval $(opam env)
opam update && opam install catala.1.3.0
```

Then, in this folder, run all the tests:

```sh
clerk test
```

To see the numbers from one test:

```sh
clerk run tests/test_art_068.catala_en --scope=TesteValores2025
```

## How the code is written

- The law text stays in Portuguese.
- Names in the code are Portuguese words without accents, such as `rendimento_coletavel`, so they match the words in the law.
- Catala keywords are in English, because Catala has no Portuguese version.
- The tax year is an input. Only 2025 exists so far. Any other year stops with an error instead of giving a wrong number.
- When the law says how to work something out, the code does exactly that, even when a simpler formula gives almost the same number.

## Sources

The law text comes from the Diário da República and from AT's Portal das Finanças. The 2025 tax rates come from Lei n.º 55-A/2025, de 22 de julho.

## License

Copyright 2026 Fabio Oliveira

Licensed under the EUPL

The full text of the licence (EUPL-1.2) is in [LICENSE](LICENSE).
