#!/usr/bin/env python3
"""Exact standard-library tests accompanying the near-full q-rook proof.
The infinite proof does not depend on these tests. Coefficients are in ascending
q-degree. Run: python verify.py --out-dir results
Use --random 0 for just the exhaustive tests. Random inputs use the explicitly
specified SplitMix64 below; the script does not use random.Random or floating point.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable, Sequence


def at(p: Sequence[int], k: int) -> int:
    return p[k] if 0 <= k < len(p) else 0


def normalize(p: Sequence[int]) -> list[int]:
    q = list(p)
    while len(q) > 1 and q[-1] == 0:
        q.pop()
    return q or [0]


def mul_interval(p: Sequence[int], length: int) -> list[int]:
    """Multiply by 1+q+...+q**(length-1), with an exact sliding sum."""
    if length < 0:
        raise ValueError('Negative interval length')
    if length == 0:
        return [0]
    ans, acc = [], 0
    for k in range(len(p) + length - 1):
        acc += at(p, k) - at(p, k-length)
        ans.append(acc)
    return ans


def box(exponents: Sequence[int]) -> list[int]:
    p = [1]
    for u in exponents:
        if u < 0:
            raise ValueError('Nonnegative box exponents required')
        p = mul_interval(p, u+1)
    return p


def naive_box(exponents: Sequence[int]) -> list[int]:
    """Independent small-case engine: enumerate individual monomials."""
    p = [0] * (sum(exponents)+1)
    for point in itertools.product(*(range(u+1) for u in exponents)):
        p[sum(point)] += 1
    return p


def diff(u: Sequence[int], v: Sequence[int]) -> list[int]:
    if len(u) != len(v) or any(a < b or b < 0 for a,b in zip(u,v)):
        raise ValueError('Require coordinatewise 0 <= v <= u')
    p, r = box(u), box(v)
    return [x-at(r,k) for k,x in enumerate(p)]


def nearfull(a: Sequence[int]) -> list[int]:
    if any(x < 0 for x in a):
        return [0]
    return box(a) if 0 in a else diff(a, [x-1 for x in a])


def gvec(u: Sequence[int]) -> list[int]:
    p = box(u)
    return [p[k]-at(p,k-1) for k in range(sum(u)//2+1)]


def is_unimodal(p: Sequence[int]) -> bool:
    falling = False
    for x,y in zip(p,p[1:]):
        if y < x:
            falling = True
        elif y > x and falling:
            return False
    return True


def assert_g_properties(g: Sequence[int]) -> None:
    assert g[0] == 1 and min(g) >= 0, ('g nonnegative',g)
    zero_seen = False
    for x in g:
        if x == 0:
            zero_seen = True
        else:
            assert not zero_seen, ('g internal zero',g)
    assert all(g[k]**2 >= g[k-1]*g[k+1] for k in range(1,len(g)-1)), ('g logconcavity',g)


def assert_shifted_ratio(u: Sequence[int], j: int, g: Sequence[int] | None = None) -> list[int]:
    g = gvec(u) if g is None else g
    v = list(u)
    v[j] += 1
    h = gvec(v)
    for k in range(max(len(g),len(h))):
        if at(g,k) == 0:
            assert at(h,k+1) == 0, ('support inclusion',u,j,k)
        assert at(h,k+2)*at(g,k) <= at(h,k+1)*at(g,k+1), ('shifted ratio',u,j,k)
    return h


def partitions(total: int, cap: int | None = None) -> Iterable[tuple[int,...]]:
    if total == 0:
        yield ()
        return
    cap = total if cap is None else min(cap,total)
    for first in range(cap,0,-1):
        for tail in partitions(total-first,first):
            yield (first,)+tail


def literal_nearfull(lam: Sequence[int]) -> list[int]:
    """Enumerate each omitted row, then cancel individual cells literally."""
    ell = len(lam)
    cells = [(i,j) for i,length in enumerate(lam) for j in range(length)]
    ans = [0]*(len(cells)+1)
    for omitted in range(ell):
        rows = [i for i in range(ell) if i != omitted]
        def dfs(step: int, occupied: set[int], rooks: list[tuple[int,int]]) -> None:
            if step == len(rows):
                inv = sum(not any((j == b and i <= a) or (i == a and j <= b)
                                  for a,b in rooks) for i,j in cells)
                ans[inv] += 1
                return
            row = rows[step]
            for col in range(lam[row]):
                if col not in occupied:
                    occupied.add(col)
                    rooks.append((row,col))
                    dfs(step+1,occupied,rooks)
                    rooks.pop()
                    occupied.remove(col)
        dfs(0,set(),[])
    return normalize(ans)


class Records:
    """SHA256 of compact ASCII JSON arrays plus LF, in enumeration order."""
    def __init__(self) -> None:
        self.count = 0
        self.sha = hashlib.sha256()
    def add(self, record: object) -> None:
        data = json.dumps(record,separators=(',',':'),ensure_ascii=True)+'\n'
        self.sha.update(data.encode('ascii'))
        self.count += 1
    def report(self) -> dict[str,object]:
        return {'records':self.count,'sha256_canonical_jsonl':self.sha.hexdigest()}


class SplitMix64:
    """Exact input generator; randbelow(n) intentionally uses reduction modulo n."""
    MASK = (1 << 64)-1
    def __init__(self,seed: int) -> None:
        self.state = seed & self.MASK
    def next(self) -> int:
        self.state = (self.state+0x9E3779B97F4A7C15) & self.MASK
        z = self.state
        z = ((z ^ (z >> 30))*0xBF58476D1CE4E5B9) & self.MASK
        z = ((z ^ (z >> 27))*0x94D049BB133111EB) & self.MASK
        return z ^ (z >> 31)
    def randbelow(self,n: int) -> int:
        if n <= 0:
            raise ValueError('Positive modulus required')
        return self.next() % n


def main(out_dir: Path, random_cases: int) -> dict[str,object]:
    out_dir.mkdir(parents=True,exist_ok=True)
    report: dict[str,object] = {'arithmetic':'Python exact integers',
        'record_encoding':'compact ASCII JSON array + LF; SHA256; deterministic loop order',
        'proof_dependency':'None; these are finite checks, not the infinite proof.'}
    independent = Records()
    for n in range(5):
        for u in itertools.product(range(4),repeat=n):
            p = box(u)
            assert p == naive_box(u), ('coefficient engine',u)
            independent.add([u,p])
    report['independent_coefficient_engine'] = independent.report()
    print('Independent coefficient engine:',independent.count,flush=True)

    rook_records, rook_data, zeros = Records(), [], 0
    for total in range(1,16):
        for lam in partitions(total):
            a = [b-i for i,b in enumerate(reversed(lam))]
            actual, expected = literal_nearfull(lam), normalize(nearfull(a))
            assert actual == expected, ('rook identity',lam,a,actual,expected)
            assert is_unimodal(actual), ('rook unimodality',lam,actual)
            zeros += actual == [0]
            record = [lam,a,actual]
            rook_records.add(record)
            rook_data.append(record)
    assert rook_records.count == 683 and zeros == 358
    report['literal_rook_boards'] = {**rook_records.report(),'max_cells':15,
                                     'zero_polynomials':zeros,'all_agree':True}
    (out_dir/'board_cases.json').write_text(json.dumps(rook_data,separators=(',',':'))+'\n')
    print('Literal rook cancellation:',rook_records.count,flush=True)

    near_records = Records()
    for n in range(2,9):
        for a in itertools.combinations_with_replacement(range(1,13),n):
            d = nearfull(a)
            assert min(d) >= 0 and is_unimodal(d), ('nearfull',a,d)
            near_records.add([a,d])
    assert near_records.count == 125957
    report['nearfull_multisets'] = {**near_records.report(),'lengths_inclusive':[2,8],
                                   'entries_inclusive':[1,12],'all_unimodal':True}
    print('Near-full multisets:',near_records.count,flush=True)

    lemma_records, adj_records = Records(), Records()
    for n in range(1,9):
        for u in itertools.combinations_with_replacement(range(9),n):
            g = gvec(u)
            assert_g_properties(g)
            base,m = u[:-1],u[-1]
            h,S = gvec(base),sum(base)
            for k in range(sum(u)//2+4):
                rec = sum(at(h,i) for i in range(k-m,min(k,S-k)+1))
                assert rec == at(g,k), ('g recurrence',u,k)
            lemma_records.add([u,g])
            for value in sorted(set(u)):
                j = u.index(value)
                gp = assert_shifted_ratio(u,j,g)
                adj_records.add([u,j,g,gp])
    assert lemma_records.count == 24309
    report['g_logconcavity_and_recurrence'] = {**lemma_records.report(),
        'lengths_inclusive':[1,8],'entries_inclusive':[0,8],'all_pass':True}
    report['one_coordinate_shifted_ratios'] = {**adj_records.report(),'all_pass':True}
    print('g-vectors and adjacent increments:',lemma_records.count,adj_records.count,flush=True)

    rng = SplitMix64(139105)
    random_records, random_adj, sample = Records(), Records(), []
    for it in range(random_cases):
        n = 1+rng.randbelow(24)
        u = [rng.randbelow(100) for _ in range(n)]
        v = [rng.randbelow(x+1) for x in u]
        d = diff(u,v)
        assert min(d) >= 0 and is_unimodal(d), ('general theorem',it,u,v,d)
        gu,gv = gvec(u),gvec(v)
        delta = sum(u)-sum(v)
        for s in range(len(gv)):
            if gv[s] == 0:
                assert at(gu,s+delta) == 0
            assert at(gu,s+delta+1)*at(gv,s) <= at(gu,s+delta)*at(gv,s+1), ('global ratio',it,s)
        random_records.add([u,v,d])
        if it < 10000:
            j = rng.randbelow(n)
            assert_g_properties(gu)
            gp = assert_shifted_ratio(u,j,gu)
            random_adj.add([u,j,gu,gp])
        if it < 20:
            sample.append({'index':it,'u':u,'v':v,'coefficients':d})
        if (it+1) % 10000 == 0:
            print('General nested boxes:',it+1,flush=True)
    report['general_nested_boxes'] = {**random_records.report(),'seed':139105,
        'generator':'SplitMix64 defined in verify.py; randbelow uses modulo',
        'lengths_inclusive':[1,24],'u_entries_inclusive':[0,99],
        'v_entries':'independent randbelow(u_i+1)','all_pass':True}
    report['random_adjacent_ratios_and_g_logconcavity'] = {**random_adj.report(),'all_pass':True}
    examples = {'coefficient_order':'ascending powers of q',
        'nearfull_examples':[{'a':a,'coefficients':nearfull(a)} for a in
             ([1],[1,1],[1,3],[2,2,2],[3,3,3],[0,2,2],[1,1,4],[2,4,100])],
        'general_examples':[{'u':u,'v':v,'coefficients':diff(u,v)} for u,v in
             (([0,0],[0,0]),([4],[1]),([1,4],[0,2]),([2,5,3],[1,1,0]))],
        'random_sample':sample}
    (out_dir/'examples.json').write_text(json.dumps(examples,indent=2)+'\n')
    (out_dir/'verification.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True),flush=True)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,default=Path('results'))
    parser.add_argument('--random',type=int,default=50000)
    args = parser.parse_args()
    if args.random < 0:
        parser.error('--random must be nonnegative')
    main(args.out_dir,args.random)
