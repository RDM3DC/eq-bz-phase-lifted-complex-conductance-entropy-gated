from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

try:
    from .bz_phase_lifted_conductance import (
        EntropyGatedConductanceConfig,
        SimulationResult,
        simulate_reference_scenario,
        summarize_result,
    )
    from .topological_readout import (
        TopologicalReadoutResult,
        simulate_topological_readout,
        summarize_topological_readout,
    )
except ImportError:
    from bz_phase_lifted_conductance import (
        EntropyGatedConductanceConfig,
        SimulationResult,
        simulate_reference_scenario,
        summarize_result,
    )
    from topological_readout import (
        TopologicalReadoutResult,
        simulate_topological_readout,
        summarize_topological_readout,
    )


EQUATION_ID = "eq-bz-phase-lifted-complex-conductance-entropy-gated"


def polyline_points(
    values: list[float],
    x0: float,
    y0: float,
    width: float,
    height: float,
    minimum: float | None = None,
    maximum: float | None = None,
) -> str:
    lower = min(values) if minimum is None else minimum
    upper = max(values) if maximum is None else maximum
    span = upper - lower if upper > lower else 1.0
    points: list[str] = []
    for index, value in enumerate(values):
        x_value = x0 + (index / max(1, len(values) - 1)) * width
        y_value = y0 + height - ((value - lower) / span) * height
        points.append(f"{x_value:.2f},{y_value:.2f}")
    return " ".join(points)


def axis_markup(title: str, x0: float, y0: float, width: float, height: float, damage_x: float) -> str:
    x_axis_y = y0 + height
    return "\n".join(
        [
            f'<text x="{x0:.0f}" y="{y0 - 12:.0f}" font-size="18" font-family="Georgia">{title}</text>',
            f'<line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x0:.0f}" y2="{x_axis_y:.0f}" stroke="#1f2937" stroke-width="1.5"/>',
            f'<line x1="{x0:.0f}" y1="{x_axis_y:.0f}" x2="{x0 + width:.0f}" y2="{x_axis_y:.0f}" stroke="#1f2937" stroke-width="1.5"/>',
            f'<line x1="{damage_x:.2f}" y1="{y0:.0f}" x2="{damage_x:.2f}" y2="{x_axis_y:.0f}" stroke="#b45309" stroke-width="1.2" stroke-dasharray="6 6"/>',
            f'<text x="{damage_x + 8:.2f}" y="{y0 + 16:.0f}" font-size="12" fill="#92400e" font-family="Georgia">slip burst</text>',
        ]
    )


def write_trace_csv(path: Path, baseline: SimulationResult, gated: SimulationResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "time",
                "mean_current",
                "resolved_phase",
                "epsilon_eff",
                "slips",
                "baseline_magnitude",
                "gated_magnitude",
                "baseline_entropy",
                "gated_entropy",
                "gated_alpha",
                "gated_mu",
            ]
        )
        for index, time_value in enumerate(gated.times):
            writer.writerow(
                [
                    f"{time_value:.4f}",
                    f"{gated.mean_current[index]:.6f}",
                    f"{gated.resolved_phase[index]:.6f}",
                    f"{gated.epsilon_eff[index]:.6f}",
                    str(gated.total_slips[index]),
                    f"{baseline.magnitude[index]:.6f}",
                    f"{gated.magnitude[index]:.6f}",
                    f"{baseline.entropy[index]:.6f}",
                    f"{gated.entropy[index]:.6f}",
                    f"{gated.alpha[index]:.6f}",
                    f"{gated.mu[index]:.6f}",
                ]
            )


def comparison_summary(baseline: SimulationResult, gated: SimulationResult) -> dict[str, float]:
    baseline_summary = summarize_result(baseline)
    gated_summary = summarize_result(gated)
    return {
        "peak_magnitude_shift": gated_summary["peak_magnitude"] - baseline_summary["peak_magnitude"],
        "peak_entropy_shift": gated_summary["peak_entropy"] - baseline_summary["peak_entropy"],
        "damage_window_magnitude_shift": gated_summary["damage_window_mean_magnitude"] - baseline_summary["damage_window_mean_magnitude"],
        "recovery_window_magnitude_shift": gated_summary["recovery_window_mean_magnitude"] - baseline_summary["recovery_window_mean_magnitude"],
        "late_time_std_shift": gated_summary["late_time_magnitude_std"] - baseline_summary["late_time_magnitude_std"],
        "mean_phase_error_shift": gated_summary["mean_phase_error"] - baseline_summary["mean_phase_error"],
    }


def write_summary_json(path: Path, baseline: SimulationResult, gated: SimulationResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "equation_id": EQUATION_ID,
        "generated_by": "simulations/run_reference_simulation.py",
        "scenarios": {
            "fixed_rate_baseline": {
                "config": asdict(baseline.config),
                "metrics": summarize_result(baseline),
            },
            "entropy_gated_phase_lifted": {
                "config": asdict(gated.config),
                "metrics": summarize_result(gated),
            },
        },
        "comparison": comparison_summary(baseline, gated),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_topological_trace_csv(
    path: Path,
    baseline: TopologicalReadoutResult,
    gated: TopologicalReadoutResult,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "time",
                "baseline_effective_mass",
                "gated_effective_mass",
                "baseline_gap",
                "gated_gap",
                "baseline_chern",
                "gated_chern",
                "baseline_transition_margin",
                "gated_transition_margin",
            ]
        )
        for index, time_value in enumerate(gated.times):
            writer.writerow(
                [
                    f"{time_value:.4f}",
                    f"{baseline.effective_mass[index]:.6f}",
                    f"{gated.effective_mass[index]:.6f}",
                    f"{baseline.spectral_gap[index]:.6f}",
                    f"{gated.spectral_gap[index]:.6f}",
                    str(baseline.chern_number[index]),
                    str(gated.chern_number[index]),
                    f"{baseline.transition_margin[index]:.6f}",
                    f"{gated.transition_margin[index]:.6f}",
                ]
            )


def write_topological_summary_json(
    path: Path,
    baseline_reference: SimulationResult,
    gated_reference: SimulationResult,
    baseline_readout: TopologicalReadoutResult,
    gated_readout: TopologicalReadoutResult,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    baseline_summary = summarize_topological_readout(baseline_readout, baseline_reference)
    gated_summary = summarize_topological_readout(gated_readout, gated_reference)
    payload = {
        "equation_id": EQUATION_ID,
        "generated_by": "simulations/run_reference_simulation.py",
        "readout_type": "FHS/QWZ effective topological readout",
        "baseline_fixed_rate": baseline_summary,
        "entropy_gated_phase_lifted": gated_summary,
        "comparison": {
            "damage_window_gap_shift": gated_summary["damage_window_mean_gap"] - baseline_summary["damage_window_mean_gap"],
            "recovery_window_gap_shift": gated_summary["recovery_window_mean_gap"] - baseline_summary["recovery_window_mean_gap"],
            "min_gap_shift": gated_summary["min_spectral_gap"] - baseline_summary["min_spectral_gap"],
            "min_transition_margin_shift": gated_summary["min_transition_margin"] - baseline_summary["min_transition_margin"],
        },
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_topological_svg(
    path: Path,
    baseline: TopologicalReadoutResult,
    gated: TopologicalReadoutResult,
    slip_center: float,
    total_time: float,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 940
    height = 620
    panel_x = 80
    panel_width = 780
    panel_height = 170
    top_y = 90
    bottom_y = 340
    damage_x = panel_x + (slip_center / total_time) * panel_width

    mass_min = min(min(baseline.effective_mass), min(gated.effective_mass))
    mass_max = max(max(baseline.effective_mass), max(gated.effective_mass))
    gap_min = min(min(baseline.spectral_gap), min(gated.spectral_gap), min(baseline.chern_number), min(gated.chern_number))
    gap_max = max(max(baseline.spectral_gap), max(gated.spectral_gap), max(baseline.chern_number), max(gated.chern_number))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">FHS/QWZ topological readout for the entropy-gated conductance model</title>
  <desc id="desc">Effective mass, spectral gap, and Chern-number readout derived from the simulated conductance trajectory.</desc>
  <rect width="100%" height="100%" fill="#f8fafc"/>
  <text x="80" y="42" font-size="28" font-family="Georgia" fill="#0f172a">Topological Readout</text>
  <text x="80" y="66" font-size="14" font-family="Georgia" fill="#334155">FHS readout of an effective QWZ Hamiltonian driven by the BZ ruler, entropy, and conductance trajectories.</text>
  {axis_markup("Effective mass", panel_x, top_y, panel_width, panel_height, damage_x)}
  <polyline fill="none" stroke="#9a3412" stroke-width="2.5" points="{polyline_points(baseline.effective_mass, panel_x, top_y, panel_width, panel_height, mass_min, mass_max)}"/>
  <polyline fill="none" stroke="#065f46" stroke-width="2.5" points="{polyline_points(gated.effective_mass, panel_x, top_y, panel_width, panel_height, mass_min, mass_max)}"/>
  <text x="640" y="108" font-size="13" font-family="Georgia" fill="#9a3412">fixed-rate baseline mass</text>
  <text x="640" y="126" font-size="13" font-family="Georgia" fill="#065f46">entropy-gated mass</text>
  {axis_markup("Spectral gap and Chern number", panel_x, bottom_y, panel_width, panel_height, damage_x)}
  <polyline fill="none" stroke="#1d4ed8" stroke-width="2.4" points="{polyline_points(baseline.spectral_gap, panel_x, bottom_y, panel_width, panel_height, gap_min, gap_max)}"/>
  <polyline fill="none" stroke="#7c3aed" stroke-width="2.4" points="{polyline_points(gated.spectral_gap, panel_x, bottom_y, panel_width, panel_height, gap_min, gap_max)}"/>
  <polyline fill="none" stroke="#b45309" stroke-width="2.0" stroke-dasharray="7 5" points="{polyline_points([float(value) for value in gated.chern_number], panel_x, bottom_y, panel_width, panel_height, gap_min, gap_max)}"/>
  <text x="640" y="358" font-size="13" font-family="Georgia" fill="#1d4ed8">baseline gap</text>
  <text x="640" y="376" font-size="13" font-family="Georgia" fill="#7c3aed">gated gap</text>
  <text x="640" y="394" font-size="13" font-family="Georgia" fill="#b45309">gated Chern number</text>
</svg>
'''
    path.write_text(svg, encoding="utf-8")


def write_svg(path: Path, baseline: SimulationResult, gated: SimulationResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 940
    height = 860
    panel_x = 80
    panel_width = 780
    panel_height = 170
    top_y = 90
    middle_y = 340
    bottom_y = 590
    damage_x = panel_x + (gated.config.slip_center / gated.config.total_time) * panel_width

    magnitude_min = min(min(baseline.magnitude), min(gated.magnitude))
    magnitude_max = max(max(baseline.magnitude), max(gated.magnitude))
    gate_min = min(min(gated.entropy), min(gated.alpha), min(gated.mu))
    gate_max = max(max(gated.entropy), max(gated.alpha), max(gated.mu))
    max_slips = max(1, max(gated.total_slips))
    normalized_slips = [value / max_slips for value in gated.total_slips]
    bz_min = min(min(gated.epsilon_eff), min(normalized_slips))
    bz_max = max(max(gated.epsilon_eff), max(normalized_slips))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">BZ phase-lifted entropy-gated conductance reference simulation</title>
  <desc id="desc">Comparison between a fixed-rate baseline and the entropy-gated conductance law under a synthetic Brillouin-zone slip burst.</desc>
  <rect width="100%" height="100%" fill="#f8fafc"/>
  <text x="80" y="42" font-size="28" font-family="Georgia" fill="#0f172a">Reference Simulation</text>
  <text x="80" y="66" font-size="14" font-family="Georgia" fill="#334155">Synthetic BZ current bundle with phase lifting, sheet slips, and entropy feedback.</text>
  {axis_markup("Conductance magnitude", panel_x, top_y, panel_width, panel_height, damage_x)}
  <polyline fill="none" stroke="#9a3412" stroke-width="2.5" points="{polyline_points(baseline.magnitude, panel_x, top_y, panel_width, panel_height, magnitude_min, magnitude_max)}"/>
  <polyline fill="none" stroke="#065f46" stroke-width="2.5" points="{polyline_points(gated.magnitude, panel_x, top_y, panel_width, panel_height, magnitude_min, magnitude_max)}"/>
  <text x="640" y="108" font-size="13" font-family="Georgia" fill="#9a3412">fixed-rate baseline</text>
  <text x="640" y="126" font-size="13" font-family="Georgia" fill="#065f46">entropy-gated law</text>
  {axis_markup("Entropy and rate gates", panel_x, middle_y, panel_width, panel_height, damage_x)}
  <polyline fill="none" stroke="#1d4ed8" stroke-width="2.4" points="{polyline_points(gated.entropy, panel_x, middle_y, panel_width, panel_height, gate_min, gate_max)}"/>
  <polyline fill="none" stroke="#7c3aed" stroke-width="2.4" points="{polyline_points(gated.alpha, panel_x, middle_y, panel_width, panel_height, gate_min, gate_max)}"/>
  <polyline fill="none" stroke="#b45309" stroke-width="2.4" points="{polyline_points(gated.mu, panel_x, middle_y, panel_width, panel_height, gate_min, gate_max)}"/>
  <text x="640" y="358" font-size="13" font-family="Georgia" fill="#1d4ed8">entropy</text>
  <text x="640" y="376" font-size="13" font-family="Georgia" fill="#7c3aed">alpha_G(S)</text>
  <text x="640" y="394" font-size="13" font-family="Georgia" fill="#b45309">mu_G(S)</text>
  {axis_markup("BZ observables", panel_x, bottom_y, panel_width, panel_height, damage_x)}
  <polyline fill="none" stroke="#0f766e" stroke-width="2.4" points="{polyline_points(gated.epsilon_eff, panel_x, bottom_y, panel_width, panel_height, bz_min, bz_max)}"/>
  <polyline fill="none" stroke="#dc2626" stroke-width="2.4" points="{polyline_points(normalized_slips, panel_x, bottom_y, panel_width, panel_height, bz_min, bz_max)}"/>
  <text x="640" y="608" font-size="13" font-family="Georgia" fill="#0f766e">epsilon_eff</text>
  <text x="640" y="626" font-size="13" font-family="Georgia" fill="#dc2626">normalized slip activity</text>
</svg>
'''
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    baseline = simulate_reference_scenario(EntropyGatedConductanceConfig(use_entropy_gating=False))
    gated = simulate_reference_scenario(EntropyGatedConductanceConfig())
    baseline_topology = simulate_topological_readout(baseline, label="fixed_rate_baseline")
    gated_topology = simulate_topological_readout(gated, label="entropy_gated_phase_lifted")
    write_trace_csv(root / "data" / "reference_trace.csv", baseline, gated)
    write_summary_json(root / "data" / "reference_summary.json", baseline, gated)
    write_svg(root / "images" / "reference_trace.svg", baseline, gated)
    write_topological_trace_csv(root / "data" / "topological_readout_trace.csv", baseline_topology, gated_topology)
    write_topological_summary_json(
        root / "data" / "topological_readout_summary.json",
        baseline,
        gated,
        baseline_topology,
        gated_topology,
    )
    write_topological_svg(
        root / "images" / "topological_readout.svg",
        baseline_topology,
        gated_topology,
        gated.config.slip_center,
        gated.config.total_time,
    )


if __name__ == "__main__":
    main()
