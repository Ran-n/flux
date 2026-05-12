[//]: # ( ---------------------------------------------------------------------- )
[//]: # (+ Authors: 	Ran# <ran.hash@proton.me> )
[//]: # (+ Created: 	2026/05/12 15:50:26.758941 )
[//]: # (+ Revised: 	2026/05/12 15:50:26.758941 )
[//]: # ( ---------------------------------------------------------------------- )

# Contributing to flux

Thank you for your interest in contributing.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Reporting Bugs](#reporting-bugs)
3. [Suggesting Features](#suggesting-features)
4. [Submitting Changes](#submitting-changes)
5. [Commit Style](#commit-style)
6. [License](#license)

---

## Code of Conduct

Be respectful. No harassment, discrimination, or bad-faith behaviour of any kind.

---

## Reporting Bugs

Open an issue with:

- A clear, descriptive title
- Step-by-step reproduction steps
- Expected behaviour vs. actual behaviour
- Environment details (OS, Python version, PyQt6 version)

---

## Suggesting Features

Open an issue with:

- The problem you are trying to solve
- Your proposed solution
- Alternatives you considered

---

## Submitting Changes

1. Fork the repository
2. Branch from `main`
3. Make your change
4. Commit following the style below
5. Open a pull request against `main`
6. Describe *why* the change is needed, not just what it does

One concern per PR. Do not bundle unrelated changes.

---

## Commit Style

Title uses a bracketed prefix followed by a short imperative phrase:

```
[A] add eye-toggle animation
[F] fix QR copy on Linux when xclip is missing
```

| Bracket | Type     |
|---------|----------|
| `[A]`   | feat     |
| `[R]`   | refactor |
| `[F]`   | fix      |
| `[D]`   | docs     |
| `[T]`   | test     |
| `[C]`   | chore    |
| `[P]`   | perf     |
| `[B]`   | build    |
| `[S]`   | style    |

Body follows Conventional Commits lowercase imperative style. Scope is optional.
Breaking changes: use `feat!`/`fix!` in the body or a `BREAKING CHANGE:` footer.

Rules:

- Do NOT repeat the type word in the title (e.g. `[F] fix: …` is wrong)
- One logical change per commit
- No `Co-Authored-By` lines

---

## License

This project is licensed under the [PayBack License (PBL)](LICENSE) — free for personal, academic, and non-commercial use. Commercial use requires a revenue-share agreement with the author.

Contributing to this project does **not** transfer copyright. Non-trivial contributions may entitle contributors to a revenue share, subject to listing in the CONTRIBUTORS file and a quorum vote of existing ownership holders, as defined in the license.

Any AI-generated portions of a contribution must be disclosed at submission time per the license terms.
