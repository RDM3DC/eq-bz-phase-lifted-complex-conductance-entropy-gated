from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from statistics import fmean, pstdev


TWO_PI = 2.0 * math.pi


@dataclass(frozen=True)
class EntropyGatedConductanceConfig:
    dt: float = 0.05
    total_time: float = 18.0
    alpha_0: float = 1.15
    mu_0: float = 0.55
    s_eq: float = 0.90
    s_0: float = 0.90
    s_c: float = 1.28
    delta_s: float = 0.16
    kappa: float = 0.085
    gamma: float = 0.58
    temperature: float = 1.0
    current_base: float = 1.00
    current_modulation: float = 0.18
    slip_center: float = 6.0
    slip_width: float = 0.22
    slip_phase_amplitude: float = 10.00
    epsilon_base: float = 0.18
    epsilon_pulse: float = 0.52
    bz_sample_count: int = 21
    entropy_floor: float = 0.30
    conductance_floor: float = 0.10
    dissipation_gain: float = 0.08
    use_entropy_gating: bool = True

    def __post_init__(self) -> None:
        if self.dt <= 0.0 or self.total_time <= 0.0:
            raise ValueError("dt and total_time must be positive")
        if self.alpha_0 <= 0.0 or self.mu_0 <= 0.0:
            raise ValueError("alpha_0 and mu_0 must be positive")
        if self.s_eq <= 0.0 or self.s_0 <= 0.0:
            raise ValueError("s_eq and s_0 must be positive")
        if self.delta_s <= 0.0:
            raise ValueError("delta_s must be positive")
        if self.gamma <= 0.0 or self.temperature <= 0.0:
            raise ValueError("gamma and temperature must be positive")
        if self.kappa < 0.0:
            raise ValueError("kappa must be nonnegative")
        if self.bz_sample_count < 5:
            raise ValueError("bz_sample_count must be at least 5")
        if self.entropy_floor <= 0.0 or self.conductance_floor <= 0.0:
            raise ValueError("entropy_floor and conductance_floor must be positive")
        if self.dissipation_gain <= 0.0:
            raise ValueError("dissipation_gain must be positive")


@dataclass
class SimulationResult:
    config: EntropyGatedConductanceConfig
    times: list[float]
    mean_current: list[float]
    resolved_phase: list[float]
    conductance: list[complex]
    magnitude: list[float]
    entropy: list[float]
    alpha: list[float]
    mu: list[float]
    total_slips: list[int]
    epsilon_eff: list[float]
    inverse_pi_a_bz: list[float]
    phase_error: list[float]
    dissipation: list[float]


def gaussian_pulse(time_value: float, center: float, width: float) -> float:
    normalized_distance = (time_value - center) / max(width, 1e-9)
    return math.exp(-(normalized_distance * normalized_distance))


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def wrapped_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def circular_mean(angles: list[float], weights: list[float]) -> float:
    sine_sum = sum(weight * math.sin(angle) for angle, weight in zip(angles, weights))
    cosine_sum = sum(weight * math.cos(angle) for angle, weight in zip(angles, weights))
    return math.atan2(sine_sum, cosine_sum)


def bz_wavenumbers(sample_count: int) -> list[float]:
    return [(-math.pi + (2.0 * math.pi * index) / sample_count) for index in range(sample_count)]


def epsilon_profile(time_value: float, config: EntropyGatedConductanceConfig) -> float:
    slip_burst = gaussian_pulse(time_value, config.slip_center, config.slip_width)
    return clamp(config.epsilon_base + config.epsilon_pulse * slip_burst, -0.92, 0.92)


def pi_a_profile(k_values: list[float], time_value: float, config: EntropyGatedConductanceConfig) -> list[float]:
    epsilon_value = epsilon_profile(time_value, config)
    return [math.pi * (1.0 + epsilon_value * math.cos(k_value)) for k_value in k_values]


def spectral_current_bundle(
    k_values: list[float],
    time_value: float,
    config: EntropyGatedConductanceConfig,
) -> tuple[list[float], list[float]]:
    slip_burst = gaussian_pulse(time_value, config.slip_center, config.slip_width)
    amplitudes: list[float] = []
    raw_phases: list[float] = []
    for k_value in k_values:
        modulation = (
            1.0
            + config.current_modulation * math.cos(k_value - 0.35 * time_value)
            - 0.26 * slip_burst * math.sin(0.5 * k_value - 0.3)
        )
        amplitudes.append(max(0.08, config.current_base * modulation))
        raw_phases.append(
            0.30 * time_value
            + 0.50 * math.sin(k_value + 0.45 * time_value)
            + config.slip_phase_amplitude * slip_burst * math.exp(-1.35 * wrapped_angle(k_value - 2.70) ** 2)
            - 0.45 * slip_burst * math.exp(-1.10 * wrapped_angle(k_value + 2.35) ** 2)
        )
    return amplitudes, raw_phases


def phase_lift(raw_phase: float, previous_lifted: float, pi_a: float, previous_sheet: int) -> tuple[float, int, int]:
    if pi_a <= 0.0:
        raise ValueError("pi_a must be positive")
    nearest_sheet = round((previous_lifted - raw_phase) / TWO_PI)
    lifted = raw_phase + TWO_PI * nearest_sheet
    delta = lifted - previous_lifted
    sheet_jump = abs(nearest_sheet - previous_sheet)
    threshold_jump = 1 if abs(delta) > pi_a else 0
    return lifted, nearest_sheet, max(sheet_jump, threshold_jump)


def bz_average_inverse_pi_a(pi_a_values: list[float]) -> float:
    return fmean(1.0 / value for value in pi_a_values)


def epsilon_eff_from_bz_average(average_inverse_pi_a: float) -> float:
    if average_inverse_pi_a <= 0.0:
        raise ValueError("average_inverse_pi_a must be positive")
    ratio = clamp(1.0 / (math.pi * average_inverse_pi_a), -1.0, 1.0)
    return math.sqrt(max(0.0, 1.0 - ratio * ratio))


def alpha_g(entropy: float, config: EntropyGatedConductanceConfig) -> float:
    effective_entropy = entropy if config.use_entropy_gating else config.s_eq
    exponent = (effective_entropy - config.s_c) / config.delta_s
    return config.alpha_0 / (1.0 + math.exp(exponent))


def mu_g(entropy: float, config: EntropyGatedConductanceConfig) -> float:
    effective_entropy = entropy if config.use_entropy_gating else config.s_eq
    return config.mu_0 * max(effective_entropy / config.s_0, 1e-9)


def steady_state_conductance(
    *,
    alpha_value: float,
    mu_value: float,
    current_magnitude: float,
    phase: float,
) -> complex:
    if mu_value <= 0.0:
        raise ValueError("mu_value must be positive")
    return cmath.rect(alpha_value * current_magnitude / mu_value, phase)


def phase_error(conductance: complex, resolved_phase: float) -> float:
    if abs(conductance) <= 1e-12:
        return 0.0
    return abs(wrapped_angle(cmath.phase(conductance) - resolved_phase))


def passive_inverse_real(conductance: complex, config: EntropyGatedConductanceConfig) -> float:
    safe_conductance = conductance if abs(conductance) >= config.conductance_floor else complex(config.conductance_floor, 0.0)
    return max((1.0 / safe_conductance).real, 0.0)


def simulate_reference_scenario(config: EntropyGatedConductanceConfig) -> SimulationResult:
    step_count = int(round(config.total_time / config.dt))
    k_values = bz_wavenumbers(config.bz_sample_count)
    initial_currents, initial_raw_phases = spectral_current_bundle(k_values, 0.0, config)
    initial_pi_a = pi_a_profile(k_values, 0.0, config)
    lifted_phases = list(initial_raw_phases)
    sheets = [0 for _ in k_values]

    initial_drive = [
        amplitude * complex(math.cos(phase), math.sin(phase))
        for amplitude, phase in zip(initial_currents, lifted_phases)
    ]
    initial_bz_drive = sum(initial_drive) / len(initial_drive)
    entropy_value = config.s_eq
    conductance = steady_state_conductance(
        alpha_value=alpha_g(entropy_value, config),
        mu_value=mu_g(entropy_value, config),
        current_magnitude=abs(initial_bz_drive),
        phase=cmath.phase(initial_bz_drive),
    )

    times: list[float] = []
    mean_current: list[float] = []
    resolved_phase: list[float] = []
    conductance_values: list[complex] = []
    magnitude: list[float] = []
    entropy: list[float] = []
    alpha_values: list[float] = []
    mu_values: list[float] = []
    total_slips: list[int] = []
    epsilon_eff: list[float] = []
    inverse_pi_a_bz: list[float] = []
    phase_errors: list[float] = []
    dissipations: list[float] = []

    for step_index in range(step_count + 1):
        time_value = step_index * config.dt
        currents, raw_phases = spectral_current_bundle(k_values, time_value, config)
        pi_a_values = pi_a_profile(k_values, time_value, config)

        step_slips = 0
        updated_lifted_phases: list[float] = []
        updated_sheets: list[int] = []
        for raw_phase, previous_lifted, pi_a_value, previous_sheet in zip(
            raw_phases, lifted_phases, pi_a_values, sheets
        ):
            lifted, sheet, slip_count = phase_lift(raw_phase, previous_lifted, pi_a_value, previous_sheet)
            updated_lifted_phases.append(lifted)
            updated_sheets.append(sheet)
            step_slips += slip_count
        lifted_phases = updated_lifted_phases
        sheets = updated_sheets

        complex_drive_samples = [
            amplitude * complex(math.cos(phase), math.sin(phase))
            for amplitude, phase in zip(currents, lifted_phases)
        ]
        bz_drive = sum(complex_drive_samples) / len(complex_drive_samples)
        drive_magnitude = abs(bz_drive)
        resolved_angle = circular_mean(lifted_phases, currents)
        alpha_value = alpha_g(entropy_value, config)
        mu_value = mu_g(entropy_value, config)
        conductance = conductance + config.dt * (
            cmath.rect(alpha_value * drive_magnitude, resolved_angle) - mu_value * conductance
        )

        dissipation_value = config.dissipation_gain * (drive_magnitude * drive_magnitude / config.temperature) * passive_inverse_real(conductance, config)
        entropy_derivative = dissipation_value + config.kappa * step_slips - config.gamma * (entropy_value - config.s_eq)
        entropy_value = max(config.entropy_floor, entropy_value + config.dt * entropy_derivative)

        inverse_pi = bz_average_inverse_pi_a(pi_a_values)
        times.append(time_value)
        mean_current.append(drive_magnitude)
        resolved_phase.append(resolved_angle)
        conductance_values.append(conductance)
        magnitude.append(abs(conductance))
        entropy.append(entropy_value)
        alpha_values.append(alpha_value)
        mu_values.append(mu_value)
        total_slips.append(step_slips)
        epsilon_eff.append(epsilon_eff_from_bz_average(inverse_pi))
        inverse_pi_a_bz.append(inverse_pi)
        phase_errors.append(phase_error(conductance, resolved_angle))
        dissipations.append(dissipation_value)

    return SimulationResult(
        config=config,
        times=times,
        mean_current=mean_current,
        resolved_phase=resolved_phase,
        conductance=conductance_values,
        magnitude=magnitude,
        entropy=entropy,
        alpha=alpha_values,
        mu=mu_values,
        total_slips=total_slips,
        epsilon_eff=epsilon_eff,
        inverse_pi_a_bz=inverse_pi_a_bz,
        phase_error=phase_errors,
        dissipation=dissipations,
    )


def window_average(result: SimulationResult, start_time: float, end_time: float, values: list[float]) -> float:
    selected = [value for time_value, value in zip(result.times, values) if start_time <= time_value <= end_time]
    return fmean(selected) if selected else values[-1]


def summarize_result(result: SimulationResult) -> dict[str, float]:
    center = result.config.slip_center
    width = result.config.slip_width
    late_values = result.magnitude[max(1, len(result.magnitude) * 3 // 4) :]
    return {
        "peak_magnitude": max(result.magnitude),
        "final_magnitude": result.magnitude[-1],
        "peak_entropy": max(result.entropy),
        "min_alpha": min(result.alpha),
        "max_mu": max(result.mu),
        "total_slips": float(sum(result.total_slips)),
        "max_single_step_slips": float(max(result.total_slips)),
        "mean_phase_error": fmean(result.phase_error),
        "damage_window_mean_magnitude": window_average(
            result,
            center - width,
            center + width,
            result.magnitude,
        ),
        "recovery_window_mean_magnitude": window_average(
            result,
            center + 2.0 * width,
            center + 4.0 * width,
            result.magnitude,
        ),
        "late_time_magnitude_std": pstdev(late_values),
        "max_epsilon_eff": max(result.epsilon_eff),
    }
