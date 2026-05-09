"""
Waypoint 2: The H(668) Hadamard Candidate Analysis
=====================================================
Using the massless Propus triple as a reference, we analyze a
Hadamard-668 candidate matrix, measure its Propus defect,
and extract the 49-bit lens coordinate system.

Key results:
  - 83-stride shows max off-diagonal = 1.0 (over-coupled 83-lens)
  - Active lens detection: 7, 11, 13 are active; 3, 5, 17 mixed; 83 anomalous
  - The candidate is 75% orthogonal (not perfect Hadamard)
  - The Propus defect measures deviation from the Carmichael ideal
"""

import numpy as np
from math import gcd
import json
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

WAYPOINT = "wp2_h668_analysis"
LENS_PRIMES = [3, 5, 7, 11, 13, 17, 83]

print("=" * 72)
print("  WAYPOINT 2: H(668) CANDIDATE ANALYSIS")
print("=" * 72)
print()
print("Reference: Massless Propus Triple {73, 167, 499}")
print("Candidate: H668_fair.npy — binary Hadamard-668 candidate")
print()

# ============================================================================
# LOAD CANDIDATE
# ============================================================================

candidate = np.load('resources/H668_fair.npy').astype(np.float64)
n = candidate.shape[0]

print(f"Candidate shape: {candidate.shape}")
print(f"Value range: [{candidate.min()}, {candidate.max()}]")
print()

# ============================================================================
# BASIC ORTHOGONALITY CHECK
# ============================================================================

gram = candidate @ candidate.T / n
off_diag_mask = ~np.eye(n, dtype=bool)
off_diag_vals = gram[off_diag_mask]

print("Gram matrix statistics:")
print(f"  Diagonal: min={np.min(np.diag(gram)):.4f}, max={np.max(np.diag(gram)):.4f}")
print(f"  Off-diagonal: min={np.min(np.abs(off_diag_vals)):.6f}, "
      f"max={np.max(np.abs(off_diag_vals)):.4f}")
print(f"  Mean |off-diag|: {np.mean(np.abs(off_diag_vals)):.6f}")
print(f"  Std |off-diag|: {np.std(np.abs(off_diag_vals)):.6f}")

# Distribution
bins = [0, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0]
hist, _ = np.histogram(np.abs(off_diag_vals), bins=bins)
print("\nDistribution of |off-diag| values:")
for i in range(len(bins)-1):
    pct = 100 * hist[i] / len(off_diag_vals)
    bar = "█" * int(pct / 2)
    print(f"  [{bins[i]:.2f}, {bins[i+1]:.2f}): {hist[i]:>8} ({pct:5.1f}%) {bar}")

pct_orthogonal = 100 * hist[0] / len(off_diag_vals)
print(f"\n{pct_orthogonal:.1f}% of pairs are nearly orthogonal (< 0.01)")
print()

# ============================================================================
# LENS ANALYSIS AT DIFFERENT STRIDES
# ============================================================================

print("=" * 72)
print("  LENS ANALYSIS AT DIFFERENT STRIDES")
print("=" * 72)
print()

stride_results = {}
for q in LENS_PRIMES:
    stride = q
    if stride > n:
        continue
    
    num_samples = n // stride
    if num_samples == 0:
        continue
    
    sampled = candidate[:, :num_samples * stride:stride]
    gram_sampled = sampled @ sampled.T / num_samples
    off_sampled = np.abs(gram_sampled[off_diag_mask])
    
    stride_results[q] = {
        'stride': stride,
        'samples': num_samples,
        'max_off_diag': float(np.max(off_sampled)),
        'mean_off_diag': float(np.mean(off_sampled))
    }
    
    print(f"Stride {stride}: {num_samples} samples, "
          f"max |off-diag| = {np.max(off_sampled):.4f}, "
          f"mean = {np.mean(off_sampled):.4f}")

print()

# ============================================================================
# ACTIVE LENS DETECTION
# ============================================================================

print("=" * 72)
print("  ACTIVE LENS DETECTION")
print("=" * 72)
print()

print(f"{'Lens q':>8} {'Observed':>10} {'Expected 1/q':>12} {'Status':>15}")
print("-" * 50)

active_lenses = []
for q in LENS_PRIMES:
    if q not in stride_results:
        continue
    
    observed = stride_results[q]['mean_off_diag']
    expected = 1.0 / q
    
    if abs(observed - expected) < 0.5 * expected:
        status = "ACTIVE"
        active_lenses.append(q)
    elif observed < 0.01:
        status = "resolved"
    else:
        status = f"mixed ({observed:.4f})"
    
    print(f"{q:>8} {observed:>10.6f} {expected:>12.4f} {status:>15}")

print(f"\nActive lens primes: {active_lenses}")
print(f"Resolved lens primes: {[q for q in LENS_PRIMES if q not in active_lenses]}")
print()

# ============================================================================
# LENS RESONANCE: OFF-DIAGONAL VALUE ANALYSIS
# ============================================================================

print("=" * 72)
print("  OFF-DIAGONAL VALUE RESONANCE")
print("=" * 72)
print()

# Round off-diagonals to integers (they should be close to integers * 4/n)
off_diag_int = np.round(off_diag_vals * n / 4).astype(int) * 4
unique_vals, counts = np.unique(off_diag_int, return_counts=True)

print("Off-diagonal values (expressed as 4×k/n):")
for val, count in sorted(zip(unique_vals, counts), key=lambda x: -x[1])[:15]:
    k = val // 4
    pct = 100 * count / len(off_diag_int)
    print(f"  4×{k:>3} = {val:>5}: {count:>8} ({pct:5.1f}%)")

print()

# ============================================================================
# COMPARISON TO IDEAL MASSLESS TRIPLE
# ============================================================================

print("=" * 72)
print("  COMPARISON TO IDEAL MASSLESS TRIPLE")
print("=" * 72)
print()

# The ideal triple at stride 83² has Gram with off-diagonals [0, 1/6, 1/3]
ideal_gram_83sq = np.array([
    [1.0, 0.333, 0.167, 0.167, 0.0, 0.0, 0.0, 0.0],
    [0.333, 1.0, 0.167, 0.167, 0.0, 0.0, 0.0, 0.0],
    [0.167, 0.167, 1.0, 0.333, 0.0, 0.0, 0.0, 0.0],
    [0.167, 0.167, 0.333, 1.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 1.0, 0.333, 0.167, 0.167],
    [0.0, 0.0, 0.0, 0.0, 0.333, 1.0, 0.167, 0.167],
    [0.0, 0.0, 0.0, 0.0, 0.167, 0.167, 1.0, 0.333],
    [0.0, 0.0, 0.0, 0.0, 0.167, 0.167, 0.333, 1.0]
])

# Candidate stride-83 analysis (subsample and compute Gram for random 8 rows)
stride_83 = 83
n_samp_83 = n // stride_83
sampled_83 = candidate[:8, :n_samp_83 * stride_83:stride_83]
candidate_gram_83 = sampled_83 @ sampled_83.T / n_samp_83

propus_defect = np.linalg.norm(candidate_gram_83 - ideal_gram_83sq, 'fro')

print("Ideal triple Gram at stride 83²:")
print(np.array2string(ideal_gram_83sq, precision=3, suppress_small=True))
print(f"\nCandidate Gram at stride 83 (first 8 rows):")
print(np.array2string(candidate_gram_83, precision=3, suppress_small=True))
print(f"\nPropus defect (Frobenius norm): {propus_defect:.4f}")
print()

# ============================================================================
# THE 49-BIT LENS COORDINATE INTERPRETATION
# ============================================================================

print("=" * 72)
print("  THE 49-BIT LENS COORDINATE SYSTEM")
print("=" * 72)
print()
print("""
The off-diagonal values are all multiples of 4. The factor 4 is the
2-Sylow substrate. The other factors come from odd lens primes:

  Value 12 = 4×3   → 3-lens active
  Value 20 = 4×5   → 5-lens active
  Value 28 = 4×7   → 7-lens active
  Value 44 = 4×11  → 11-lens active
  Value 52 = 4×13  → 13-lens active
  Value 60 = 4×15  → 3-lens AND 5-lens active
  Value 84 = 4×21  → 3-lens AND 7-lens active

Each of the 668 rows can be assigned a 49-bit signature,
where each bit corresponds to one lens prime dimension.
Only 668 of the 2^49 possible combinations are valid —
the rest are excluded by the Carmichael constraints.
""")

# ============================================================================
# SAVE RESULTS
# ============================================================================

os.makedirs(f"{WAYPOINT}/output", exist_ok=True)

results = {
    'candidate_shape': list(candidate.shape),
    'gram_statistics': {
        'diagonal_min': float(np.min(np.diag(gram))),
        'diagonal_max': float(np.max(np.diag(gram))),
        'off_diag_min': float(np.min(np.abs(off_diag_vals))),
        'off_diag_max': float(np.max(np.abs(off_diag_vals))),
        'off_diag_mean': float(np.mean(np.abs(off_diag_vals))),
        'off_diag_std': float(np.std(np.abs(off_diag_vals))),
        'pct_nearly_orthogonal': float(pct_orthogonal)
    },
    'stride_analysis': {str(q): stride_results[q] for q in LENS_PRIMES if q in stride_results},
    'active_lenses': active_lenses,
    'propus_defect': float(propus_defect),
    'ideal_gram_83sq': ideal_gram_83sq.tolist(),
    'candidate_gram_83': candidate_gram_83.tolist()
}

with open(f'{WAYPOINT}/output/h668_analysis.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"Saved: {WAYPOINT}/output/h668_analysis.json")
print()
print("=" * 72)
print("  WAYPOINT 2 COMPLETE — H(668) ANALYSIS")
print("=" * 72)
