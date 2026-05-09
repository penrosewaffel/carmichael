#!/bin/bash
# ============================================================================
# Propus Framework — Run All Waypoints
# ============================================================================
# Executes each waypoint script in order.
# Requires: Python 3, NumPy
# Run from the repository root: bash waypoints/run_all.sh
# ============================================================================

echo "=============================================="
echo "  PROPUS FRAMEWORK — RUNNING ALL WAYPOINTS"
echo "=============================================="
echo ""

SCRIPTS=(
    "wp1_massless_triple/propus_massless_triple.py"
    "wp2_h668_analysis/propus_h668_analysis.py"
    "wp3_3n_generator/threen_generator.py"
    "wp4_7k_generator/seven_k_generator.py"
    "wp5_uniform_28/uniform_28_structure.py"
    "wp6_81lens_synthesis/eightyone_lens.py"
    "wp7_cross_generator/cross_generator.py"
)

for script in "${SCRIPTS[@]}"; do
    echo "----------------------------------------------"
    echo "  RUNNING: waypoints/$script"
    echo "----------------------------------------------"
    python3 "waypoints/$script"
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: $script failed. Stopping."
        exit 1
    fi
    echo ""
done

echo "=============================================="
echo "  ALL WAYPOINTS COMPLETE"
echo "=============================================="
