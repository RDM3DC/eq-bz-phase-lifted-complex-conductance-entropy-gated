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

Canonical entropy-gated Phase-Lifted ARP conductance update. Single traceable boxed equation with 4 supporting definitions (all from Core + #3/#10). Entropy dynamics are 2nd-law safe; BZ ruler self-consistency feeds a uniform m_eff into QWZ preserving the single Chern jump.

## Assumptions

- \pi_a(k,t) from Core Eq. 10; weights in BZ average are uniform or occupation (user choice).
- Chern number via FHS lattice method; Phase-Lift supplies continuous \theta_R history and slip detection only.
- Entropy production uses Re(1/\tilde G) ≥ 0 for passive response (2nd-law safe).
- \varepsilon_{\mathrm{eff}} inversion assumes the cosine form \pi_a=\pi(1+\varepsilon\cos\lambda) and |\varepsilon_{\mathrm{eff}}|<1.

## Repository Structure

```
docs/         # Research reports and validation plans
images/       # Visualizations, plots, diagrams
derivations/  # Step-by-step derivations and proofs
simulations/  # Computational models and code
data/         # Numerical data, experimental results
notes/        # Research notes and references
```

## Key Documents

- **[Empirical Validation Plan](docs/validation-plan.md)** — Full research report: analytical reductions, 5 falsifiable predictions, simulation sketches, topolectrical circuit + photonics experimental protocols, timeline

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
