# Reproducing the exact finite checks

Use Python 3.10 or newer. The verifier requires only the standard library.
Assertions must be enabled: do not use Python's -O or -OO option.

~~~sh
python verify.py --help
python verify.py --out-dir reproduced_results
~~~

The second command runs the full historical test specification and writes to a
new directory. It can take substantial time. No full-suite runtime was measured
for this edition. --random 0 disables only the broad generated cases: it still
runs the entire exhaustive portion and is not a small smoke test.

| Family | Historical reported count |
|---|---:|
| Products checked against direct monomial enumeration | 341 |
| All nonempty partitions with at most 15 cells | 683 |
| Zero rook polynomials among those partitions | 358 |
| Positive multisets, lengths 2–8, entries 1–12 | 125,957 |
| First-difference vectors, lengths 1–8, entries 0–8 | 24,309 |
| Distinct one-coordinate increments of those multisets | 102,960 |
| Broad nested-box pairs, dimensions 1–24, outer entries 0–99 | 50,000 |
| Additional large one-coordinate comparisons | 10,000 |

These numbers and reported passes are archived results. The complete suite was
not rerun for this edition. Earlier records lack sufficient independent execution
metadata to certify that every historical assertion was executed.

results/board_cases.json contains arrays
[partition, a_vector, coefficient_vector], ordered by increasing board size and
then the recursive partition order in verify.py. Polynomial coefficients are
ordered by increasing q-degree. results/examples.json contains boundary
examples and the first 20 broad cases, with complete coefficients.

The broad cases use SplitMix64 with seed 139105; the complete generator is
defined in verify.py. Its randbelow(n) is reduction modulo n. The first 10,000
broad cases consume one extra generator value for the coordinate used by the
adjacent-increment test.

Each stream digest in results/verification.json hashes compact ASCII JSON
records, each followed by a single LF byte, in the loop order in the source:

| Stream | Record |
|---|---|
| Independent coefficient engine | [u, P_u] |
| Literal rook boards | [lambda, a, R_(ell-1)] |
| Near-full multisets | [a, product[a_i+1]-product[a_i]] |
| First-difference vectors | [u, g_u] |
| Adjacent comparisons | [u, coordinate_index, g_u, g_(u+e_j)] |
| General nested boxes | [u, v, P_u-P_v] |

Coordinates are zero-indexed. Products retain trailing zeros; the literal rook
oracle normalizes trailing zeros. Compare the resulting parsed JSON reports and
canonical stream hashes against the archived report. Physical file line endings
can depend on the operating system; SHA256SUMS describes this distributed
edition, not every future machine's output files.

## Build the manuscript

Use an existing LaTeX installation with the packages named in proof.tex:

~~~sh
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error proof.tex
pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error proof.tex
~~~

A finite verification run does not replace the proof in the manuscript.
