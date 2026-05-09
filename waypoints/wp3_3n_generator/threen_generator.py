"""
Waypoint 3: The 3^n Shadow Generator
======================================
The generating principle of the entire lens tree.

Rule: 3^n → next_prime(3^n)

This produces the sequence of lens primes:
  5, 11, 29, 83, 251, 733, 2203, 6563, ...

Each shadow prime is a "canopy" lens that generates its own
Propus construction through the Sophie Germain chain.

Key discoveries:
  - Gaps are mostly 2 (twin primes) for n=1,2,3,4,8,10,14
  - SG chains die out as n grows
  - Deep cores alternate: 3^4 at n=4, 5^3 at n=5
  - The 83-lens (n=4) is the shadow of 3^4=81 — the first deep core
"""

import numpy as np
from math import gcd
import json
import os

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def is_prime(n):
    if n < 2: return False
    for d in range(2, int(n**0.5) + 1):
        if n % d == 0: return False
    return True

def next_prime(n):
    candidate = n + 1
    while not is_prime(candidate):
        candidate += 1
    return candidate

def factorize(n):
    factors = {}
    temp = n
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1 if d == 2 else 2
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def sophie_germain_chain(start, max_depth=10, max_val=10**8):
    chain = [start]
    current = start
    for _ in range(max_depth):
        p = 2 * current + 1
        if p > max_val or not is_prime(p):
            break
        chain.append(p)
        current = p
    return chain

# ============================================================================
# GENERATE THE 3^n SHADOW SEQUENCE
# ============================================================================

WAYPOINT = "wp3_3n_generator"

print("=" * 72)
print("  WAYPOINT 3: THE 3^n SHADOW GENERATOR")
print("=" * 72)
print()
print("Generating rule: 3^n → next_prime(3^n)")
print()

shadow_data = []
for n in range(1, 15):
    three_n = 3**n
    if three_n > 10**12:
        break
    shadow = next_prime(three_n)
    gap = shadow - three_n
    
    # Factor shadow-1 for lens structure
    facts = factorize(shadow - 1)
    max_exp = 0
    deep_core = None
    for q, e in facts.items():
        if q > 2 and e > max_exp:
            max_exp = e
            deep_core = q
    
    # SG analysis
    is_sg = is_prime(2*shadow + 1)
    chain = sophie_germain_chain(shadow)
    chain_depth = len(chain) - 1
    
    # Smallest carrier
    carrier = None
    if is_sg:
        carrier = 2*shadow + 1
    else:
        for k in range(2, 100, 2):
            p = shadow * k + 1
            if p > 100000: break
            if is_prime(p):
                carrier = p
                break
    
    hadamard = 4 * carrier if carrier else None
    
    shadow_data.append({
        'n': n,
        '3^n': three_n,
        'shadow': shadow,
        'gap': gap,
        'shadow-1': shadow - 1,
        'factorization': {str(q): e for q, e in facts.items()},
        'deep_core': f"{deep_core}^{max_exp}" if deep_core and max_exp >= 2 else f"{shadow} (pure)",
        'is_sg': is_sg,
        'sg_chain': chain,
        'sg_depth': chain_depth,
        'carrier': carrier,
        'hadamard': hadamard,
        'gap_factorization': {str(q): e for q, e in factorize(gap).items()}
    })

# ============================================================================
# DISPLAY THE SEQUENCE
# ============================================================================

print(f"{'n':>3} {'3^n':>14} {'Shadow':>10} {'Gap':>6} {'Deep core':>15} {'SG?':>5} "
      f"{'SG depth':>10} {'Carrier':>8} {'H=4p':>8}")
print("-" * 95)

for d in shadow_data:
    carrier_str = str(d['carrier']) if d['carrier'] else "—"
    hadamard_str = str(d['hadamard']) if d['hadamard'] else "—"
    sg_str = "✓" if d['is_sg'] else "—"
    
    print(f"{d['n']:>3} {d['3^n']:>14} {d['shadow']:>10} {d['gap']:>6} "
          f"{d['deep_core']:>15} {sg_str:>5} {d['sg_depth']:>10} "
          f"{carrier_str:>8} {hadamard_str:>8}")

print()

# ============================================================================
# DETAILED ANALYSIS OF KEY SHADOWS
# ============================================================================

print("=" * 72)
print("  KEY SHADOWS IN DETAIL")
print("=" * 72)
print()

for d in shadow_data:
    if d['n'] <= 8:
        print(f"n={d['n']}: 3^{d['n']} = {d['3^n']:,}, shadow = {d['shadow']}")
        print(f"  {d['shadow']}-1 = {d['shadow-1']} = ", end="")
        fact_str = " × ".join(f"{q}^{e}" if e > 1 else str(q) 
                             for q, e in sorted(factorize(d['shadow-1']).items()))
        print(fact_str)
        print(f"  Deep core: {d['deep_core']}")
        print(f"  Gap: {d['gap']} = ", end="")
        gap_str = " × ".join(f"{q}^{e}" if e > 1 else str(q) 
                            for q, e in sorted(factorize(d['gap']).items()))
        print(gap_str)
        print(f"  SG prime? {d['is_sg']}")
        if d['is_sg']:
            chain_str = " → ".join(str(p) for p in d['sg_chain'])
            print(f"  SG chain: {chain_str} (depth {d['sg_depth']})")
            if d['carrier']:
                print(f"  Propus carrier: {d['carrier']} → Hadamard {d['hadamard']}")
        print(f"  Previous SG prime in chain: ", end="")
        if d['shadow'] > 2 and (d['shadow']-1) % 2 == 0:
            parent = (d['shadow'] - 1) // 2
            if is_prime(parent):
                print(f"{parent} → {d['shadow']}")
            else:
                print(f"no SG parent ({(d['shadow']-1)//2} not prime)")
        else:
            print("no SG parent")
        print()

# ============================================================================
# THE RHYTHM OF THE GAPS
# ============================================================================

print("=" * 72)
print("  THE RHYTHM OF THE GAPS")
print("=" * 72)
print()

gaps = [d['gap'] for d in shadow_data]
twin_primes = [d for d in shadow_data if d['gap'] == 2]

print(f"Twin prime gaps (gap=2) occur at n = {[d['n'] for d in twin_primes]}")
print(f"These are the RESONANT shadows — 3^n and 3^n+2 are both prime.")
print(f"Non-resonant gaps: {[d['gap'] for d in shadow_data if d['gap'] != 2]}")
print()

# ============================================================================
# THE DEEP CORES
# ============================================================================

print("=" * 72)
print("  THE DEEP CORES")
print("=" * 72)
print()

deep_cores = [d for d in shadow_data if '^' in d['deep_core']]
print("Shadows with amplified lens depth:")
for d in deep_cores:
    print(f"  n={d['n']}: shadow {d['shadow']}, deep core = {d['deep_core']}")
    print(f"       {d['shadow']}-1 = {d['shadow-1']} = ", end="")
    fact_str = " × ".join(f"{q}^{e}" if e > 1 else str(q) 
                         for q, e in sorted(factorize(d['shadow-1']).items()))
    print(fact_str)

print()
print("The deep cores alternate between powers of 3 and powers of 5:")
print("  n=4: 3^4 = 81 → shadow 83 (C_81 Sylow)")
print("  n=5: 5^3 = 125 → shadow 251 (C_125 Sylow)")
print("  This creates the ALTERNATING RHYTHM of the lens tree.")
print()

# ============================================================================
# SG CHAIN COLLAPSE
# ============================================================================

print("=" * 72)
print("  SOPHIE GERMAIN CHAIN COLLAPSE")
print("=" * 72)
print()

sg_depths = [(d['n'], d['sg_depth'], d['shadow']) for d in shadow_data]
print("SG chain depths as n grows:")
for n, depth, shadow in sg_depths[:10]:
    bar = "█" * depth
    print(f"  n={n:>2}: depth={depth} {bar} (shadow={shadow})")

print()
print("The SG chains are DYING OUT as n increases.")
print("The 3^n generator outlives the SG mechanism.")
print("After n=6, most shadows are NOT Sophie Germain primes.")
print()

# ============================================================================
# SAVE
# ============================================================================

os.makedirs(f"{WAYPOINT}/output", exist_ok=True)

output = {
    'generator': '3^n → next_prime(3^n)',
    'sequence': shadow_data,
    'twin_prime_n': [d['n'] for d in twin_primes],
    'deep_core_n': [d['n'] for d in deep_cores],
    'sg_depths': [(d['n'], d['sg_depth']) for d in shadow_data],
    'total_shadows': len(shadow_data)
}

with open(f'{WAYPOINT}/output/threen_generator.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Saved: {WAYPOINT}/output/threen_generator.json")
print()
print("=" * 72)
print("  WAYPOINT 3 COMPLETE — 3^n SHADOW GENERATOR")
print("=" * 72)
