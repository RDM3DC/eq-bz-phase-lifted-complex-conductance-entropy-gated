# Entropy Gating, Passivity, and Local Stability Notes

## Operating Regime

The statements below use the following conditions.

- `alpha_0 > 0`, `mu_0 > 0`, `S_0 > 0`, `Delta S > 0`.
- `S(t) > 0`, so `mu_G(S)` stays positive.
- `Re(1 / \tilde G_ij) >= 0` on the passive branch used by the entropy balance.
- `kappa >= 0` and `gamma > 0` in the entropy equation.
- Slip counts `|Delta w_ij|` are nonnegative integers produced by the phase-lift rule.

These are exactly the assumptions used by the reference simulator.

## Proposition 1: Monotonicity of the Entropy Gates

The rate laws are

$$
\alpha_G(S) = \frac{\alpha_0}{1 + \exp\!\left(\frac{S - S_c}{\Delta S}\right)},
\qquad
\mu_G(S) = \mu_0\frac{S}{S_0}.
$$

Differentiating gives

$$
\frac{d\alpha_G}{dS}
= -\frac{\alpha_0}{\Delta S}
\frac{\exp\!\left(\frac{S-S_c}{\Delta S}\right)}{
\left(1 + \exp\!\left(\frac{S-S_c}{\Delta S}\right)\right)^2}
< 0,
$$

and

$$
\frac{d\mu_G}{dS} = \frac{\mu_0}{S_0} > 0.
$$

So higher entropy always weakens the source term and always strengthens the damping term.

## Proposition 2: Passivity-Compatible Entropy Production Is Nonnegative Before Relaxation

The entropy law is

$$
\frac{dS}{dt}
= \sum_{ij}\frac{|I_{ij}|^2}{T_{ij}}\operatorname{Re}\!\left(\frac{1}{\tilde G_{ij}}\right)
+ \kappa\sum_{ij}|\Delta w_{ij}|
- \gamma(S-S_{\rm eq}).
$$

Under `T_ij > 0`, `Re(1 / \tilde G_ij) >= 0`, and `kappa >= 0`, the first two terms are nonnegative. That means the only term capable of decreasing entropy is the explicit relaxation term `-gamma (S - S_eq)`.

This is the right structure for a reference law: irreversible dissipation and sheet slips add entropy, while the environment relaxes it back toward an equilibrium level.

## Proposition 3: Positivity of the Entropy State

If `S(0) > 0` and the simulator enforces the passive branch of `Re(1 / \tilde G)`, then at `S = 0` the derivative satisfies

$$
\left.\frac{dS}{dt}\right|_{S=0}
= \sum_{ij}\frac{|I_{ij}|^2}{T_{ij}}\operatorname{Re}\!\left(\frac{1}{\tilde G_{ij}}\right)
+ \kappa\sum_{ij}|\Delta w_{ij}|
+ \gamma S_{\rm eq}
> 0.
$$

So zero is a repelling boundary and the continuous-time model pushes the entropy state back into the positive half-line.

## Proposition 4: Local Linear Stability of the Conductance Subsystem

Holding `S`, `|I|`, and `theta_R` fixed,

$$
\frac{d\tilde G}{dt} = F - \mu_G(S)\tilde G
$$

has perturbation equation

$$
\frac{d}{dt}(\delta \tilde G) = -\mu_G(S)\,\delta \tilde G.
$$

Because `mu_G(S) > 0`, every perturbation decays exponentially. The entropy channel changes the fixed point location and the decay rate, but it does not destroy local linear stability of the conductance update.

## Proposition 5: Slip Events Enter Only Through the Entropy Channel

The integer sheet changes `Delta w_ij` do not appear directly in the conductance ODE. They affect the conductance state indirectly by changing `S`, which then changes `alpha_G` and `mu_G`.

That separation matters. It means a slip event does not force a discontinuous jump in `\tilde G` itself; instead it injects entropy and lets the gates suppress conductance continuously afterward.

## Practical Consequence for Validation

The easiest falsifiable check is not a full topological experiment. It is this chain:

1. detect a localized burst of sheet slips,
2. verify that entropy rises at the same time,
3. verify that `alpha_G` drops and `mu_G` rises,
4. verify that the conductance magnitude is temporarily suppressed,
5. verify that the conductance phase still relaxes toward the resolved lifted phase.

If that chain fails, the law is not doing what its own algebra claims.
