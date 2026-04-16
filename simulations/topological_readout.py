from __future__ import annotations

import cmath
import math
from collections import Counter
from dataclasses import dataclass
from statistics import fmean

try:
    from .bz_phase_lifted_conductance import SimulationResult, clamp
except ImportError:
    from bz_phase_lifted_conductance import SimulationResult, clamp


TWO_PI = 2.0 * math.pi


@dataclass(frozen=True)
class TopologicalReadoutConfig:
    grid_size: int = 17
    mass_scale: float = 1.42
    entropy_relief_gain: float = 0.95
    conductance_relief_gain: float = 1.10
    mass_floor: float = 0.15
    mass_ceiling: float = 3.50

    def __post_init__(self) -> None:
        if self.grid_size < 7:
            raise ValueError("grid_size must be at least 7")
        if self.mass_scale <= 0.0:
            raise ValueError("mass_scale must be positive")
        if self.entropy_relief_gain < 0.0 or self.conductance_relief_gain < 0.0:
            raise ValueError("readout gains must be nonnegative")
        if self.mass_floor <= 0.0 or self.mass_ceiling <= self.mass_floor:
            raise ValueError("mass bounds must be positive and ordered")


@dataclass
class TopologicalReadoutResult:
    label: str
    config: TopologicalReadoutConfig
    times: list[float]
    effective_mass: list[float]
    spectral_gap: list[float]
    chern_number: list[int]
    transition_margin: list[float]


def qzw_d_vector(kx: float, ky: float, mass: float) -> tuple[float, float, float]:
    return (
        math.sin(kx),
        math.sin(ky),
        mass - math.cos(kx) - math.cos(ky),
    )


def lower_band_eigenvector(kx: float, ky: float, mass: float) -> tuple[complex, complex]:
    dx, dy, dz = qzw_d_vector(kx, ky, mass)
    radius = math.sqrt(dx * dx + dy * dy + dz * dz)
    if radius <= 1e-12:
        raise ValueError("gapless point encountered in lower_band_eigenvector")
    if abs(dz + radius) >= abs(dz - radius):
        vector = (complex(-dx, dy), complex(dz + radius, 0.0))
    else:
        vector = (complex(dz - radius, 0.0), complex(dx, dy))
    norm = math.sqrt(abs(vector[0]) ** 2 + abs(vector[1]) ** 2)
    if norm <= 1e-12:
        raise ValueError("degenerate eigenvector norm in lower_band_eigenvector")
    return (vector[0] / norm, vector[1] / norm)


def inner_product(left: tuple[complex, complex], right: tuple[complex, complex]) -> complex:
    return left[0].conjugate() * right[0] + left[1].conjugate() * right[1]


def normalized_link(left: tuple[complex, complex], right: tuple[complex, complex]) -> complex:
    overlap = inner_product(left, right)
    magnitude = abs(overlap)
    if magnitude <= 1e-12:
        raise ValueError("vanishing overlap in normalized_link")
    return overlap / magnitude


def qzw_spectral_gap(mass: float, grid_size: int) -> float:
    minimum_radius = float("inf")
    for ix in range(grid_size):
        kx = -math.pi + TWO_PI * ix / grid_size
        for iy in range(grid_size):
            ky = -math.pi + TWO_PI * iy / grid_size
            dx, dy, dz = qzw_d_vector(kx, ky, mass)
            radius = math.sqrt(dx * dx + dy * dy + dz * dz)
            minimum_radius = min(minimum_radius, radius)
    return 2.0 * minimum_radius


def fhs_chern_number(mass: float, grid_size: int) -> int:
    eigenvectors: list[list[tuple[complex, complex]]] = []
    for ix in range(grid_size):
        kx = -math.pi + TWO_PI * ix / grid_size
        row: list[tuple[complex, complex]] = []
        for iy in range(grid_size):
            ky = -math.pi + TWO_PI * iy / grid_size
            row.append(lower_band_eigenvector(kx, ky, mass))
        eigenvectors.append(row)

    total_flux = 0.0
    for ix in range(grid_size):
        ix_next = (ix + 1) % grid_size
        for iy in range(grid_size):
            iy_next = (iy + 1) % grid_size
            u = eigenvectors[ix][iy]
            ux = normalized_link(u, eigenvectors[ix_next][iy])
            uy = normalized_link(u, eigenvectors[ix][iy_next])
            ux_y = normalized_link(eigenvectors[ix][iy_next], eigenvectors[ix_next][iy_next])
            uy_x = normalized_link(eigenvectors[ix_next][iy], eigenvectors[ix_next][iy_next])
            wilson_loop = ux * uy_x / (ux_y * uy)
            total_flux += cmath.phase(wilson_loop)

    return int(round(total_flux / TWO_PI))


def effective_mass_from_state(
    result: SimulationResult,
    index: int,
    config: TopologicalReadoutConfig,
) -> float:
    epsilon_value = result.epsilon_eff[index]
    intrinsic_mass = config.mass_scale / math.sqrt(max(1e-9, 1.0 - epsilon_value * epsilon_value))
    entropy_relief = config.entropy_relief_gain * max(0.0, result.entropy[index] - result.config.s_eq)
    reference_magnitude = max(result.magnitude[0], 1e-9)
    conductance_relief = config.conductance_relief_gain * max(0.0, 1.0 - result.magnitude[index] / reference_magnitude)
    return clamp(intrinsic_mass - entropy_relief - conductance_relief, config.mass_floor, config.mass_ceiling)


def transition_margin(mass: float) -> float:
    return min(abs(mass + 2.0), abs(mass), abs(mass - 2.0))


def simulate_topological_readout(
    result: SimulationResult,
    config: TopologicalReadoutConfig | None = None,
    *,
    label: str,
) -> TopologicalReadoutResult:
    resolved_config = config or TopologicalReadoutConfig()
    masses: list[float] = []
    gaps: list[float] = []
    chern_numbers: list[int] = []
    margins: list[float] = []
    for index, _ in enumerate(result.times):
        mass_value = effective_mass_from_state(result, index, resolved_config)
        masses.append(mass_value)
        gaps.append(qzw_spectral_gap(mass_value, resolved_config.grid_size))
        chern_numbers.append(fhs_chern_number(mass_value, resolved_config.grid_size))
        margins.append(transition_margin(mass_value))
    return TopologicalReadoutResult(
        label=label,
        config=resolved_config,
        times=result.times,
        effective_mass=masses,
        spectral_gap=gaps,
        chern_number=chern_numbers,
        transition_margin=margins,
    )


def dominant_chern_number(chern_numbers: list[int]) -> int:
    return Counter(chern_numbers).most_common(1)[0][0]


def window_average(times: list[float], values: list[float], start_time: float, end_time: float) -> float:
    selected = [value for time_value, value in zip(times, values) if start_time <= time_value <= end_time]
    return fmean(selected) if selected else values[-1]


def summarize_topological_readout(readout: TopologicalReadoutResult, reference: SimulationResult) -> dict[str, float]:
    center = reference.config.slip_center
    width = reference.config.slip_width
    nontrivial_fraction = sum(1 for value in readout.chern_number if abs(value) == 1) / len(readout.chern_number)
    return {
        "dominant_chern_number": float(dominant_chern_number(readout.chern_number)),
        "nontrivial_fraction": nontrivial_fraction,
        "min_spectral_gap": min(readout.spectral_gap),
        "damage_window_mean_gap": window_average(
            readout.times,
            readout.spectral_gap,
            center - width,
            center + width,
        ),
        "recovery_window_mean_gap": window_average(
            readout.times,
            readout.spectral_gap,
            center + 2.0 * width,
            center + 4.0 * width,
        ),
        "min_transition_margin": min(readout.transition_margin),
        "max_effective_mass": max(readout.effective_mass),
        "min_effective_mass": min(readout.effective_mass),
    }
