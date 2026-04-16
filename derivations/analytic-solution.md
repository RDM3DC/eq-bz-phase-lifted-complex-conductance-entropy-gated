# Analytic Solution for the Entropy-Gated Conductance Update

## Compact Form

Write the conductance law as

$$
\frac{d\tilde G_{ij}}{dt} = F_{ij}(t) - \mu_G\bigl(S(t)\bigr)\tilde G_{ij}(t),
$$

with

$$
F_{ij}(t) = \alpha_G\bigl(S(t)\bigr)\,|I_{ij}(t)|\,e^{i\theta_{R,ij}(t)}.
$$

The BZ averaging and phase-lift logic live upstream of this equation: they determine the effective magnitude `|I_ij|` and resolved phase `theta_R,ij`, while the conductance update itself remains linear in `\tilde G_ij` once those inputs are fixed.

## General Time-Dependent Solution

Using the integrating factor

$$
\mathcal I(t) = \exp\!\left(\int_0^t \mu_G\bigl(S(u)\bigr)\,du\right),
$$

the exact mild solution is

$$
\tilde G_{ij}(t)
= e^{-\int_0^t \mu_G(S(u))\,du}\,\tilde G_{ij}(0)
+ \int_0^t e^{-\int_\tau^t \mu_G(S(u))\,du}\,F_{ij}(\tau)\,d\tau.
$$

This immediately shows two structural facts.

1. The law is a stable linear filter whenever `mu_G(S) > 0`.
2. All of the interesting physics and numerics enter through the source term `F_ij`, not through a nonlinear self-interaction in `\tilde G_ij`.

## Frozen-Coefficient Regime

If `S`, `|I_ij|`, and `theta_R,ij` vary slowly on a short window, then `F_ij` and `mu_G` are approximately constant and the solution reduces to

$$
\tilde G_{ij}(t)
= \tilde G_{ij}^{\ast}
+ \bigl(\tilde G_{ij}(0) - \tilde G_{ij}^{\ast}\bigr)e^{-\mu_G t},
$$

with the quasi-static fixed point

$$
\tilde G_{ij}^{\ast}
= \frac{\alpha_G(S)}{\mu_G(S)}\,|I_{ij}|\,e^{i\theta_{R,ij}}.
$$

This is the main closed-form prediction that a reference simulator should recover at late time whenever the source changes slowly enough.

## Magnitude and Phase Separation

From the frozen-coefficient fixed point,

$$
|\tilde G_{ij}^{\ast}| = \frac{\alpha_G(S)}{\mu_G(S)}\,|I_{ij}|,
\qquad
\arg\!\bigl(\tilde G_{ij}^{\ast}\bigr) = \theta_{R,ij}.
$$

So the entropy gates act only on the equilibrium amplitude. The preferred complex phase is inherited directly from the lifted resolved phase.

## Entropy-Gated Rates

The recorded rate laws are

$$
\alpha_G(S) = \frac{\alpha_0}{1 + \exp\!\left(\frac{S - S_c}{\Delta S}\right)},
\qquad
\mu_G(S) = \mu_0\frac{S}{S_0}.
$$

Substituting them into the frozen fixed point gives

$$
\tilde G_{ij}^{\ast}
= \frac{\alpha_0 S_0}{\mu_0 S\left(1 + \exp\!\left(\frac{S - S_c}{\Delta S}\right)\right)}
|I_{ij}|e^{i\theta_{R,ij}}.
$$

That formula makes the intended control mechanism explicit: as entropy rises, the numerator is logisticly suppressed while the damping grows linearly.

## Limiting Cases

### Low-Entropy Limit

For `S << S_c`,

$$
\alpha_G(S) \approx \alpha_0,
\qquad
\mu_G(S) \approx \mu_0\frac{S}{S_0},
$$

so the source term is nearly unsuppressed and the amplitude is limited mostly by the baseline damping scale.

### High-Entropy Limit

For `S >> S_c`,

$$
\alpha_G(S) \approx \alpha_0\,e^{-\frac{S-S_c}{\Delta S}},
\qquad
\mu_G(S) \propto S,
$$

which drives the steady-state conductance magnitude rapidly downward. That is the self-quenching regime the simulator should reveal after a slip burst or sustained dissipative loading.

## What This Derivation Does and Does Not Prove

These formulas prove that the conductance update itself is analytically tame. They do not prove that any downstream Hamiltonian, circuit Laplacian, or BZ-derived effective parameter is globally stable. They do give the correct benchmark for testing code: once the BZ phase-lift preprocessing is fixed, the conductance state should relax exponentially toward the lifted-phase fixed point determined by the entropy gates.
