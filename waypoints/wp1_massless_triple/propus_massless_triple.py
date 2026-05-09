"""
Waypoint 1: The Massless Propus Triple
========================================
Carriers: {73, 167, 499}
From Carmichael quintuple: 135439162657849 = 73 × 167 × 499 × 4649 × 4789

This is the foundational Propus construction. Two carriers (167, 499)
share the 83-lens, creating a "chiral pair" that decouples perfectly
at stride 83². The third carrier (73) provides the 3² lens without
sharing the 83-lens — the "massless" condition.

Key results:
  - 8 perfectly orthogonal binary codes, length 5,952,096
  - At stride 83² = 6889: Gram splits into two decoupled 4×4 blocks
  - Probe space: 864 dimensions = 2⁵ × 3³
  - Cross-block coupling: exactly ZERO (massless)

The 8 codes are the "generators" of the Propus-668 operator.
"""

import numpy as np
from math import gcd
import json
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

CARMICHAEL_N = 135439162657849
FULL_CARRIERS = [73, 167, 499, 4649, 4789]  # the complete quintuple
CARRIERS = [73, 167, 499]                    # the triple subset
LENS_PRIME = 83                               # shared by 167 and 499
WAYPOINT = "wp1_massless_triple"
STRIDE_83SQ = 83 * 83      # = 6889 — resolves both 83-lenses
STRIDE_83 = 83             # = 83   — resolves one 83-lens
STRIDE_MOD = 32 * 9        # = 288  — modulation substrate only

# ============================================================================
# FACTORIZATION UTILITIES
# ============================================================================

def factorize(n):
    """Return dict of {prime: exponent} for n."""
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

def v2(n):
    """2-adic valuation."""
    count = 0
    while n % 2 == 0:
        n //= 2
        count += 1
    return count

# ============================================================================
# LENS STRUCTURE ANALYSIS
# ============================================================================

print("=" * 72)
print("  WAYPOINT 1: THE MASSLESS PROPUS TRIPLE")
print("=" * 72)
print()
print(f"From Carmichael quintuple: {CARMICHAEL_N}")
print(f"  = {' × '.join(str(p) for p in FULL_CARRIERS)}")
print(f"Using triple: {' × '.join(str(p) for p in CARRIERS)}")
print()

print("Lens structure of each carrier:")
for p in CARRIERS:
    pm1 = p - 1
    facts = factorize(pm1)
    v = facts.get(2, 0)
    odd = [(q, e) for q, e in sorted(facts.items()) if q > 2]
    odd_str = ", ".join(f"{q}^{e}" if e > 1 else str(q) for q, e in odd)
    fact_str = " × ".join(f"{q}^{e}" if e > 1 else str(q) for q, e in sorted(facts.items()))
    print(f"  p={p:3d}: p-1 = {pm1:3d} = {fact_str}")
    print(f"        2-Sylow: C_{2**v}, odd lenses: {odd_str}")

print()
print(f"2-Sylow: C_8 × C_2 × C_2")
print(f"2-torsion: C_2 × C_2 × C_2 → 8 binary codes")
print(f"Chiral pair: 167 and 499 BOTH carry the 83-lens")
print(f"Third carrier: 73 provides 3² lens (no other carrier shares it)")
print(f"Massless condition: no odd lens shared by all three carriers")
print()

# ============================================================================
# GRID DIMENSIONS
# ============================================================================

phi_values = [p-1 for p in CARRIERS]
active = int(np.prod(phi_values))
grid_size = int(np.prod(CARRIERS))

print(f"Grid: {'×'.join(str(p) for p in CARRIERS)} = {grid_size:,} positions")
print(f"Active: {'×'.join(str(phi) for phi in phi_values)} = {active:,} positions")
print(f"Zeros: {grid_size - active:,} (structured at non-unit CRT positions)")
print(f"Dense array size: 8 × {active:,} bytes = {8*active/1024**2:.1f} MB")
print()

# ============================================================================
# BUILD BINARY CODES
# ============================================================================

def binary_coordinate(p):
    """Legendre symbol: 0 for +1, 1 for -1."""
    exp = (p - 1) // 2
    return {x: 0 if pow(x, exp, p) == 1 else 1
            for x in range(1, p) if gcd(x, p) == 1}

print("Computing binary coordinates...")
coords = [binary_coordinate(p) for p in CARRIERS]

# Pre-compute sign arrays for streaming
signs = []
for i, p in enumerate(CARRIERS):
    s = np.array([1 if coords[i][x] == 0 else -1 
                  for x in range(1, p) if gcd(x, p) == 1], dtype=np.int8)
    signs.append(s)
    plus = np.sum(s == 1)
    minus = np.sum(s == -1)
    print(f"  mod {p}: +1={plus}, -1={minus} (balanced: {plus == minus})")

# Stream through all unit positions
print(f"\nBuilding dense codes by streaming ({active:,} positions)...")
dense = np.zeros((8, active), dtype=np.int8)
col = 0

for s1 in signs[0]:
    for s2 in signs[1]:
        for s3 in signs[2]:
            dense[0, col] = 1                    # (0,0,0) — DC
            dense[4, col] = s1                   # (1,0,0) — χ_73
            dense[2, col] = s2                   # (0,1,0) — χ_167
            dense[6, col] = s1 * s2              # (1,1,0)
            dense[1, col] = s3                   # (0,0,1) — χ_499
            dense[5, col] = s1 * s3              # (1,0,1)
            dense[3, col] = s2 * s3              # (0,1,1)
            dense[7, col] = s1 * s2 * s3         # (1,1,1) — all three
            col += 1
        if col % 1000000 == 0:
            print(f"  Progress: {col:,} / {active:,} ({100*col/active:.1f}%)")

dense = dense.astype(np.float64)
print(f"  Complete: {col:,} positions")
print()

# ============================================================================
# VERIFY PERFECT ORTHOGONALITY
# ============================================================================

gram_full = dense @ dense.T / active
max_off = np.max(np.abs(gram_full - np.eye(8)))
is_orth = max_off < 1e-10

print("Full Gram matrix (should be identity):")
print(np.array2string(gram_full, precision=3, suppress_small=True))
print(f"\nMax off-diagonal: {max_off:.2e}")
print(f"Perfectly orthogonal: {is_orth}")
print(f"All entries ±1: {np.all(np.abs(dense) == 1)}")
print()

# ============================================================================
# PROBES AT DIFFERENT RESOLUTIONS
# ============================================================================

print("-" * 72)
print("  PROBES AT DIFFERENT RESOLUTIONS")
print("-" * 72)
print()

# Stride 83²: resolves both 83-lenses → clean decoupling
probe_83sq = dense[:, ::STRIDE_83SQ]
n_83sq = probe_83sq.shape[1]
gram_83sq = probe_83sq @ probe_83sq.T / n_83sq

print(f"Stride {STRIDE_83SQ} (83²): {n_83sq} samples = {factorize(n_83sq)}")
print("Gram matrix (block-diagonal, two 4×4 blocks):")
print(np.array2string(gram_83sq, precision=3, suppress_small=True))

# Block analysis
block1 = probe_83sq[:4]
block2 = probe_83sq[4:]
cross = np.max(np.abs(block1 @ block2.T))
print(f"\nCross-block coupling: {cross:.2e} (should be 0 for massless triple)")
print(f"Block 1 eigenvalues: {np.linalg.eigh(block1 @ block1.T / n_83sq)[0]}")
print()

# Stride 83: resolves one 83-lens → partial coupling
probe_83 = dense[:, ::STRIDE_83]
n_83 = probe_83.shape[1]
gram_83 = probe_83 @ probe_83.T / n_83
print(f"Stride {STRIDE_83}: {n_83:,} samples")
print("Gram matrix (emerging 3-lens coupling):")
print(np.array2string(gram_83, precision=4, suppress_small=True))
print()

# Stride 288: modulation substrate → full coupling
probe_mod = dense[:, ::STRIDE_MOD]
n_mod = probe_mod.shape[1]
gram_mod = probe_mod @ probe_mod.T / n_mod
print(f"Stride {STRIDE_MOD} (32×9): {n_mod:,} samples")
print("Gram matrix (full coupling):")
print(np.array2string(gram_mod, precision=4, suppress_small=True))
print()

# ============================================================================
# SAVE RESULTS
# ============================================================================

# Create output directory
os.makedirs(f"{WAYPOINT}/output", exist_ok=True)

# Save dense codes (compressed)
np.savez_compressed(f'{WAYPOINT}/output/dense_8.npz', dense=dense)

# Save probes
np.save(f'{WAYPOINT}/output/probe_83sq.npy', probe_83sq)
np.save(f'{WAYPOINT}/output/probe_83.npy', probe_83)
np.save(f'{WAYPOINT}/output/probe_mod.npy', probe_mod)

# Save metadata
metadata = {
    'waypoint': 'wp1_massless_triple',
    'carmichael_n': CARMICHAEL_N,
    'carriers': CARRIERS,
    'lens_prime': LENS_PRIME,
    'chiral_pair': [167, 499],
    'massless': True,
    'n_codes': 8,
    'active_positions': active,
    'grid_size': grid_size,
    'perfectly_orthogonal': bool(is_orth),
    'probes': {
        'stride_83sq': {'stride': STRIDE_83SQ, 'samples': n_83sq, 
                        'factorization': {str(q): e for q, e in factorize(n_83sq).items()},
                        'cross_block_coupling': float(cross)},
        'stride_83': {'stride': STRIDE_83, 'samples': n_83},
        'stride_288': {'stride': STRIDE_MOD, 'samples': n_mod}
    }
}

with open(f'{WAYPOINT}/output/metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print("=" * 72)
print("  SAVED OUTPUTS")
print("=" * 72)
print(f"  {WAYPOINT}/output/dense_8.npz     — 8 binary codes ({dense.shape})")
print(f"  {WAYPOINT}/output/probe_83sq.npy  — stride 83² probe ({probe_83sq.shape})")
print(f"  {WAYPOINT}/output/probe_83.npy    — stride 83 probe ({probe_83.shape})")
print(f"  {WAYPOINT}/output/probe_mod.npy   — stride 288 probe ({probe_mod.shape})")
print(f"  {WAYPOINT}/output/metadata.json   — full metadata")
print()
print("=" * 72)
print("  WAYPOINT 1 COMPLETE — MASSLESS PROPUS TRIPLE")
print("=" * 72)
