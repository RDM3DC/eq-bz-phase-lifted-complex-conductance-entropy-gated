import cmath
import unittest

from simulations.bz_phase_lifted_conductance import (
    EntropyGatedConductanceConfig,
    alpha_g,
    epsilon_eff_from_bz_average,
    mu_g,
    phase_lift,
    simulate_reference_scenario,
    steady_state_conductance,
    summarize_result,
)


class BZPhaseLiftedConductanceTests(unittest.TestCase):
    def test_phase_lift_counts_sheet_jump(self) -> None:
        lifted, sheet, slip_count = phase_lift(raw_phase=-3.05, previous_lifted=3.00, pi_a=1.10, previous_sheet=0)
        self.assertEqual(sheet, 1)
        self.assertEqual(slip_count, 1)
        self.assertGreater(lifted, 3.0)

    def test_entropy_gates_are_monotone(self) -> None:
        config = EntropyGatedConductanceConfig()
        self.assertGreater(alpha_g(0.8, config), alpha_g(1.6, config))
        self.assertLess(mu_g(0.8, config), mu_g(1.6, config))

    def test_steady_state_matches_expected_magnitude_and_phase(self) -> None:
        conductance = steady_state_conductance(
            alpha_value=0.82,
            mu_value=0.55,
            current_magnitude=1.10,
            phase=0.35,
        )
        self.assertAlmostEqual(abs(conductance), 0.82 * 1.10 / 0.55)
        self.assertAlmostEqual(cmath.phase(conductance), 0.35)

    def test_epsilon_eff_is_bounded(self) -> None:
        epsilon_eff = epsilon_eff_from_bz_average(1.0 / 3.25)
        self.assertGreaterEqual(epsilon_eff, 0.0)
        self.assertLess(epsilon_eff, 1.0)

    def test_reference_simulation_keeps_entropy_positive(self) -> None:
        result = simulate_reference_scenario(
            EntropyGatedConductanceConfig(
                total_time=8.0,
                dt=0.1,
                slip_center=3.5,
                slip_phase_amplitude=7.0,
                slip_width=0.35,
            )
        )
        self.assertTrue(all(value > 0.0 for value in result.entropy))
        self.assertGreater(max(result.total_slips), 0)
        self.assertGreater(max(result.magnitude), 0.0)
        summary = summarize_result(result)
        self.assertIn("peak_entropy", summary)

    def test_entropy_gating_reduces_damage_window_magnitude_against_baseline(self) -> None:
        baseline = simulate_reference_scenario(
            EntropyGatedConductanceConfig(total_time=12.0, dt=0.1, use_entropy_gating=False)
        )
        gated = simulate_reference_scenario(EntropyGatedConductanceConfig(total_time=12.0, dt=0.1))
        baseline_summary = summarize_result(baseline)
        gated_summary = summarize_result(gated)
        self.assertLess(
            gated_summary["damage_window_mean_magnitude"],
            baseline_summary["damage_window_mean_magnitude"],
        )
        self.assertGreater(gated_summary["peak_entropy"], gated.config.s_eq)


if __name__ == "__main__":
    unittest.main()