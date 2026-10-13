# Unimodality of nested-box differences and near-full q-rook polynomials

Aurantium · 13 October 2026

For nonnegative integer vectors v <= u coordinatewise, this manuscript proves
that P_u(q) - P_v(q) has nonnegative unimodal coefficients, where
P_u(q) = product_i (1 + q + ... + q**u_i).
The result applies to the near-full q-rook polynomial of every nonempty Ferrers
board, with any number of rows, including cases with no near-full placement.

Read proof.pdf and its editable source proof.tex. The proof includes the
rook reduction, interval-sum inequalities, lower-half first differences,
shifted ratio comparisons, symmetric chain decomposition, and all boundary cases.

The product-difference reduction and monomial Hilbert-series interpretation
originated in unpublished preliminary research notes. They are derived in full
in the manuscript. The question and relevant literature are credited in
REFERENCES.md and the manuscript.

## Status and scope

This is an AI-assisted manuscript. It has not undergone independent expert
peer review or formal proof checking. No exhaustive literature-priority claim
is made.

The proof establishes coefficient unimodality, including the stated
characteristic-independent Hilbert-function corollary. It does not assert
log-concavity of near-full rook polynomials, unimodality at arbitrary rook
rank, any weak or strong Lefschetz property, or resolution of other related
conjectures.

The records in results/ are historical computation artifacts. The complete
large enumeration was not rerun for this edition. Its counts and hashes are
provided for reproducibility, not as independent certification of the historical
execution or as premises of the infinite proof.

## Files

- proof.tex and proof.pdf: manuscript.
- verify.py: standalone exact-integer verifier using the Python standard library.
- results/: archived counts, stream hashes, board coefficients, and examples.
- REPRODUCIBILITY.md: commands, exact enumeration and hashing conventions.
- REFERENCES.md and RIGHTS.md: attribution and distribution scope.
- PUBLIC_FILES.txt and SHA256SUMS: public file list and checksums.
