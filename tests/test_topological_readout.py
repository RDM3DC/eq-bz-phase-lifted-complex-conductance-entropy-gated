import unittest

from simulations.bz_phase_lifted_conductance import EntropyGatedConductanceConfig, simulate_reference_scenario
from simulations.topological_readout import (
    TopologicalReadoutConfig,
    fhs_chern_number,
    qzw_spectral_gap,
    simulate_topological_readout,
    summarize_topological_readout,
)


class TopologicalReadoutTests(unittest.TestCase):
    def test_fhs_chern_number_is_nontrivial_in_qwz_window(self) -> None:
        self.assertEqual(abs(fhs_chern_number(1.0, 17)), 1)

    def test_fhs_chern_number_is_trivial_outside_qwz_window(self) -> None:
        self.assertEqual(fhs_chern_number(3.0, 17), 0)

    def test_qzw_gap_stays_positive_away_from_transition(self) -> None:
        self.assertGreater(qzw_spectral_gap(1.2, 17), 0.0)

    def test_topological_readout_matches_reference_length(self) -> None:
        reference = simulate_reference_scenario(EntropyGatedConductanceConfig(total_time=4.0, dt=0.1))
        readout = simulate_topological_readout(reference, TopologicalReadoutConfig(grid_size=13), label="test")
        self.assertEqual(len(readout.times), len(reference.times))
        self.assertTrue(all(value > 0.0 for value in readout.spectral_gap))

    def test_entropy_gating_improves_damage_window_gap(self) -> None:
        baseline_reference = simulate_reference_scenario(
            EntropyGatedConductanceConfig(total_time=18.0, dt=0.1, use_entropy_gating=False)
        )
        gated_reference = simulate_reference_scenario(EntropyGatedConductanceConfig(total_time=18.0, dt=0.1))
        baseline = simulate_topological_readout(
            baseline_reference,
            TopologicalReadoutConfig(grid_size=13),
            label="baseline",
        )
        gated = simulate_topological_readout(
            gated_reference,
            TopologicalReadoutConfig(grid_size=13),
            label="gated",
        )
        baseline_summary = summarize_topological_readout(baseline, baseline_reference)
        gated_summary = summarize_topological_readout(gated, gated_reference)
        self.assertGreater(gated_summary["damage_window_mean_gap"], baseline_summary["damage_window_mean_gap"])
        self.assertGreaterEqual(gated_summary["nontrivial_fraction"], 0.95)


if __name__ == "__main__":
    unittest.main()