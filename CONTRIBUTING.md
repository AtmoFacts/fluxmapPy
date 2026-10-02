

# Contributing to fluxmapPy

fluxmapPy is developed by AtmoFacts, LLC. It is in an early (0.6.0) phase in which behavior may still change between releases. Names and arguments are subject to change until they lock at the 1.0.0 version. Name changes from 0.6.0 to 1.0.0 could cause warnings to appear when using the package.

## What we welcome now

- Bug reports and questions through the issue forms.
- Documentation fixes (typos, broken links) as small pull requests.

## Code contributions

Until version 1.0, code changes are by invitation: open an issue describing the change; the package lead will reply and, if the change fits the roadmap, invite a pull request. Uninvited code pull requests may be closed without review.

## Semantic Versioning
fluxmappy version numbers are in MAJOR.MINOR.PATCH increments (i.e. 0.6.0)
MAJOR, when incompatible changes are made to the API permenantly.
MINOR, when new functionality is created rolled out in a backwards compatible manner.
PATCH, when a backwards compatible bug fix is made. 
Backwards compatible means that the functionality or bug fixes were made and the updated software works within the existing code without breakage. 
Incompatible changes mean physical changes to the public API that prevents older code or dependencies to work without being updated.

## Contributor License Agreement

Every code contribution is made under [CLA.md](CLA.md). Opening a pull request does not by itself constitute agreement. Before your first pull request is reviewed, post this comment on it, verbatim:

    I have read the Contributor License Agreement in CLA.md (version v0.1) and I agree to its terms.

The maintainer records your agreement in `.github/cla-signatures.md` (handle, pull request, timestamp, CLA version and commit) and locks the pull-request conversation after merge. One agreement covers all your later contributions. If you contribute on behalf of an employer or institution, an email from them confirming your authority is needed before merge. Contributions are accepted only through GitHub pull requests.

## Conventions

- Names follow the eddy4R terms(https://docs.google.com/spreadsheets/d/1QV0Rv1XKgOej6y8kNOeP-HS1ZdpHbBmLZL7Fk3pm1Mg/edit?usp=sharing) and wiki (https://github.com/NEONScience/eddy4R/wiki/Contributing-to-eddy4R#coding-style): 2 to 4 character terms joined by underscores; `def_` (definition), `wrap_` (wrapper), `modl_` (data structure) prefixes. One canonical name per function; no aliases.
- One concern per commit; run `pytest`, `ruff check .` and `pre-commit run --all-files` before pushing.
- Public functions carry a numpy-style docstring with a runnable Examples section (it is doctested and rendered in the docs).
- Never commit customer or site data, internal hostnames, buckets, or credentials.

## Command-line interface

There is no CLI yet. A `fluxmappy` console entry point is planned after 1.0 if there is demand; open an issue if you have a use case.
