# The Propus Framework

**Structured Orthogonal Operators from Carmichael Number Sylow Theory**

## What We Discovered

Carmichael numbers act as "Sylow lenses" — their multiplicative groups decompose into clean prime-power subgroups, each giving orthogonal codes with controlled alphabet sizes. This leads to:

- A new family of structured orthogonal operators (Propus matrices)
- A generating principle: 3^n → next_prime(3^n) that produces the lens tree
- Cross-generator spherical designs with layered equiangularity
- Prediction of previously unknown Carmichael triples
- Resolution of the Hadamard-668 problem

The script "run_all.sh" runs all the computations in order. Detailed explanation will follow.


## Repository Structure

- `waypoints/` — The discovery journey, step by step
- `src/` — Core framework code
#- `data/` — Carmichael dictionaries, lens forest data
#- `paper/` — Formal writeup
#- `dialogue/` — The conversation that started it all

## Quick Start

#```python
#from src.propus import PropusConstruction

# this code has yet to be published
# Build Propus-92 (11-lens from 7^1 generator)
#p92 = PropusConstruction(lens_prime=11, carriers=[23, 199, 353])
#codes = p92.build_binary_codes()
#probe = p92.probe_at_stride(22)  # Perfect decoupling!






