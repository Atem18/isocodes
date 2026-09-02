# Changelog

## 2026.9.2

### Breaking

- **Python 3.9 and 3.10 are no longer supported**; the minimum is now 3.11.
  Both are past or within weeks of end of life, and together they accounted for
  0.34% of downloads. Dropping them removes the last version-conditional import,
  which is what stopped a single test run from reaching full coverage.

- **`find()` now honours every keyword.** It previously returned on the first
  indexed field that matched and ignored the rest, so
  `find(alpha_2="US", name="Nonsense")` wrongly returned the United States.

- **`search()` ignores word order and ranks its results.** ISO stores many names
  inverted, so `search(name="Republic of Korea")` used to return nothing; it now
  returns `Korea, Republic of` first. Exact matches rank above prefixes, which
  rank above substrings.

- **The obsolete catalogue filenames are no longer shipped**: `iso_3166.mo`,
  `iso_3166_2.mo`, `iso_639.mo`, `iso_639_3.mo` and `iso_639_5.mo`. Upstream
  installs these as symlinks to the current names, but a wheel turns them into
  full copies, which was doubling the package. Every language is still included,
  and the old domain names still work through `translate()` and `translator()`.
  Only a raw `gettext.translation("iso_3166", ...)` call needs updating, to
  `"iso_3166-1"`.

### Added

- `translate()`, `translator()` and `available_languages()` for reading the
  gettext catalogues, replacing the raw `gettext` recipe in the README.
- `isocodes locales` to list the installed languages and remove unwanted ones,
  for trimming container images. It previews by default and needs `--yes` to
  delete anything.
- `search_fuzzy()` and a `--fuzzy` CLI flag, for queries containing typos, built
  on `difflib` so there is still no dependency. `search()` is unchanged and
  never guesses: the approximate pass runs only when an ordinary search finds
  nothing, so a correctly spelled query can never come back with an approximate
  answer.

### Changed

- The six near-identical CLI search handlers are now one table-driven handler,
  and the subcommand parsers are built from the same table. `cli.py` is about a
  hundred lines shorter, and the CLI no longer loads every dataset at import, so
  `isocodes --help` and `isocodes locales` parse no data at all. The command
  line interface is unchanged apart from the new `--fuzzy` flag.
- **The wheel is 8.1 MB, down from 15 MB**, with all 163 languages still
  included. The saving is entirely the duplicated catalogues described above.
- Data updated to iso-codes **v4.20.1** (was v4.18.0). Six currencies were
  withdrawn upstream — `BGN`, `HRK`, `ANG`, `CUC`, `SLL` and `ZWL` — and three
  added: `XCG`, `ZWG` and `XAD`. Bulgaria and Croatia now use the euro.
- Datasets load on first use instead of at import. `import isocodes` drops from
  ~145 ms and ~15 MB to ~29 ms and ~3 MB.
- `get()` is around 180x faster. Its substring matching is unchanged.
- `update.sh` rewritten for meson; upstream dropped autotools in 4.19.0. It now
  needs `git`, `meson` and `ninja`, and takes an optional version tag.
- Python 3.14 is supported and tested, including the free-threaded build.

### Removed

- Unreachable code in the CLI: `format_output`'s single-record branches, which
  no caller could trigger since every call site passes a list, and the six
  "Please specify search criteria" branches, which argparse's required argument
  group already prevents.

### Fixed

- **`--format json` and `--format csv` emitted `No results found.` when there
  were no matches**, which is neither valid JSON nor valid CSV and broke any
  caller parsing the output. They now return `[]` and an empty string; `table`
  still prints the message.
- **`--fields` was ignored by `--format json`**, which returned every field
  regardless. Table and CSV already honoured it. JSON now returns only the
  requested fields, in the order given.
- Package metadata declared both LGPL-2.1 and MIT. The bundled data comes from
  Debian's iso-codes, which is LGPL-2.1-or-later, so that is now declared as a
  single SPDX `License-Expression`. The conflict caused some license scanners to
  reject the package.
- The wheel ignored the configured `package-data` globs and shipped whatever was
  in the tree, because `include-package-data` defaults to true.
