"""
PCIF Final 200 Scenarios Generator Script
==========================================
Assembles all 200 locked scenarios and outputs docs/evaluation/datasets/pcif_final_200.jsonl.
"""

import json
from pathlib import Path

from .gen_nutrition import get_nutrition_scenarios
from .gen_mental_wellness import get_mental_wellness_scenarios
from .gen_mixed_context import get_mixed_context_scenarios
from .gen_longitudinal_change import get_longitudinal_change_scenarios
from .gen_conflicting_information import get_conflicting_information_scenarios
from .gen_irrelevant_history import get_irrelevant_history_scenarios
from .gen_sparse_and_no_history import get_sparse_and_no_history_scenarios
from .gen_provenance_sensitive import get_provenance_sensitive_scenarios

def generate_all_200_scenarios():
    scenarios = []
    
    # 1. Nutrition: 30 (001 - 030)
    scenarios.extend(get_nutrition_scenarios())
    
    # 2. Mental Wellness: 30 (031 - 060)
    scenarios.extend(get_mental_wellness_scenarios())
    
    # 3. Mixed Context: 30 (061 - 090)
    scenarios.extend(get_mixed_context_scenarios())
    
    # 4. Longitudinal Change: 30 (091 - 120)
    scenarios.extend(get_longitudinal_change_scenarios())
    
    # 5. Conflicting Information: 25 (121 - 145)
    scenarios.extend(get_conflicting_information_scenarios())
    
    # 6. Irrelevant History: 20 (146 - 165)
    scenarios.extend(get_irrelevant_history_scenarios())
    
    # 7 & 8. Sparse History (12) + No History (8): 20 (166 - 185)
    scenarios.extend(get_sparse_and_no_history_scenarios())
    
    # 9. Provenance Sensitive: 15 (186 - 200)
    scenarios.extend(get_provenance_sensitive_scenarios())
    
    return scenarios

def main():
    scenarios = generate_all_200_scenarios()
    
    assert len(scenarios) == 200, f"Expected 200 scenarios, got {len(scenarios)}"
    
    # Verify IDs
    for i, s in enumerate(scenarios, 1):
        expected_id = f"SCN-FINAL-{i:03d}"
        assert s["scenario_id"] == expected_id, f"Index {i} mismatch: {s['scenario_id']} != {expected_id}"
        assert s["split"] == "final", f"Split mismatch in {s['scenario_id']}"
        
    out_path = Path(__file__).resolve().parent / "pcif_final_200.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for s in scenarios:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
            
    print(f"Successfully generated {len(scenarios)} scenarios to {out_path}")

if __name__ == "__main__":
    main()
