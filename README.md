# BZ-Averaged Phase-Lifted Complex Conductance Update (Entropy-Gated)

**ID:** `eq-bz-phase-lifted-complex-conductance-entropy-gated`  
**Tier:** derived  
**Score:** 97  
**Units:** OK  
**Theory:** PASS-WITH-ASSUMPTIONS  

## Equation

$$
\frac{d\tilde{G}_{ij}}{dt} = \alpha_G(S)\;|I_{ij}(t)|\,e^{i\theta_{R,ij}(t)} - \mu_G(S)\;\tilde{G}_{ij}(t)
$$

## Description

Canonical entropy-gated phase-lifted conductance update written as a stable complex first-order filter whose source amplitude is suppressed as entropy rises. The law couples three ingredients that are each experimentally meaningful:

- a BZ-averaged resolved phase built from lifted current phases,
- a complex conductance state that relaxes toward that lifted phase,
- and an entropy channel that adds both dissipative and slip-count contributions.

The point of this repository is not to claim a new topological invariant by itself. The point is to turn the boxed law into a falsifiable research object with closed-form reductions, a reproducible synthetic BZ reference simulation, committed artifacts, and regression tests.

## What This Repository Now Contains

- Closed-form solutions for the time-dependent and frozen-coefficient conductance update.
- Proof notes for entropy gating monotonicity, passivity-compatible entropy production, and local stability.
- A pure-Python synthetic BZ phase-lift simulator with explicit sheet jumps and entropy feedback.
- Committed CSV, JSON, and SVG artifacts comparing the full entropy-gated law against a fixed-rate baseline.
- An FHS/QWZ topological readout layer that converts the conductance trajectory into a time-resolved effective mass, spectral gap, and Chern-number diagnostic.
- A small unittest suite covering the phase-lift rule, gate monotonicity, steady-state algebra, and reference behavior.

## Assumptions

- `pi_a(k,t)` stays positive across the sampled BZ so the phase-lift threshold remains meaningful.
- The phase-lift routine uses integer `2 pi` sheet jumps and treats `pi_a(k,t)` as the local admissible jump bound.
- Entropy production uses `Re(1 / \tilde G) >= 0` as the passive-response branch; negative values are projected away in the reference simulator.
- The BZ ruler inversion uses the cosine form `pi_a = pi (1 + epsilon cos lambda)` with `|epsilon| < 1`, so `epsilon_eff` stays real.

## Quick Start

Run the committed reference simulation:

```bash
python simulations/run_reference_simulation.py
```

Run the tests:

```bash
python -m unittest discover -s tests
```

## Key Documents

- [derivations/analytic-solution.md](derivations/analytic-solution.md) - integrating-factor solution, frozen-coefficient steady state, and phase alignment.
- [derivations/entropy-gating-and-passivity.md](derivations/entropy-gating-and-passivity.md) - monotonicity, entropy positivity conditions, and local stability notes.
- [docs/validation-plan.md](docs/validation-plan.md) - falsifiable predictions, staged validation program, and near-term hardware path.
- [simulations/run_reference_simulation.py](simulations/run_reference_simulation.py) - reproducible CLI that regenerates the committed artifacts.
- [data/reference_summary.json](data/reference_summary.json) - scenario-level metrics for the fixed-rate and entropy-gated reference runs.
- [images/reference_trace.svg](images/reference_trace.svg) - conductance, entropy, and phase-lift observables for the reference run.
- [data/topological_readout_summary.json](data/topological_readout_summary.json) - FHS/QWZ topological-gap and Chern-number summary for the baseline and gated trajectories.
- [images/topological_readout.svg](images/topological_readout.svg) - effective mass, spectral gap, and topological readout comparison.

## Current Readout

The committed synthetic BZ reference now produces an explicit eight-slip burst with a maximum of three slips in a single step. Against the fixed-rate baseline, the entropy-gated law lowers the damage-window mean conductance magnitude by about `0.123` and the recovery-window mean by about `0.120`, while slightly improving mean phase alignment and reducing late-time variance. The new FHS readout keeps both trajectories in the same nontrivial phase with dominant Chern number `1`, but the entropy-gated path maintains a wider minimum spectral gap, raising it from about `0.701` to `0.813`, and improves the damage-window mean gap by about `0.134`.

## Repository Structure

```text
docs/         validation notes and experimental framing
images/       committed SVG artifacts
derivations/  analytic reductions and proof notes
simulations/  pure-Python reference model and artifact generator
data/         committed CSV and JSON outputs
notes/        scratch space for future research notes
```

## Links

- [TopEquations Leaderboard](https://rdm3dc.github.io/TopEquations/leaderboard.html)
- [TopEquations Main Repo](https://github.com/RDM3DC/TopEquations)
- [Certificates](https://rdm3dc.github.io/TopEquations/certificates.html)

---
*Part of the [TopEquations](https://github.com/RDM3DC/TopEquations) project.*

## Contributing

You can add images, derivations, simulations, data, or notes to this repo:

| Folder | What goes here |
|--------|---------------|
| `images/` | Plots, diagrams, phase portraits, animations (.png, .jpg, .mp4, ...) |
| `derivations/` | Step-by-step derivations and proofs (.tex, .md, .pdf) |
| `simulations/` | Computational models and code (.py, .ipynb, .jl, .m) |
| `data/` | Numerical results, experimental measurements (.csv, .hdf5, .npy) |
| `notes/` | Research notes, lit reviews, references (.md, .bib, .txt) |
| `docs/` | Formal documents, validation plans (.md, .pdf) |

**Three ways to contribute:**
1. **GitHub Issue** — click [New Issue](../../issues/new?template=artifact_submission.yml) and attach your file
2. **Pull Request** — fork, add files, open a PR
3. **CLI** — `python tools/push_to_equation_repo.py --equation-id eq-bz-phase-lifted-complex-conductance-entropy-gated --file <path> --folder <folder>`

All submissions are content-moderated. See the [full contributing guide](https://github.com/RDM3DC/TopEquations/blob/main/CONTRIBUTING.md).
