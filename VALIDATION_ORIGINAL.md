# Numerical validation

All 25 default notebook code cells were executed in order. The saved outputs include 16 figures and two animated GIFs. General-purpose numerical libraries are used; no CFD framework is called.

## Analytical checks at t=8

| Case | Method | Relative L2 error |
|---|---|---|
| couette | fd | 0.00028366 |
| couette | lbm | 0.00028914 |
| poiseuille | fd | 0.00036952 |
| poiseuille | lbm | 0.00104124 |

LBM Poiseuille refinement at t=12: N=16 error 0.00278768; N=32 error 0.000701778. Reduction factor about 3.97. This validates the simple plate profile, not the general cylinder boundary treatment.

## Geometry and projection checks

For none, rectangle, cylinder, rotated ellipse, and two cylinders: a real short run verified finite results, zero velocity inside the obstacle, maximum discrete divergence below 1e-9, and inlet/outlet flux difference below 1e-9. Short LBM runs checked Mach and density variation. See results/validation.json for actual measurements. These short runs are stability smoke checks, not final-state convergence tests.

## Long cylinder demonstration

Both methods ran to t≈18 at Re=100 on 360×60 cells, D=0.25, H=1, L=6 and target U=1. The CFD run uses centred transport, the LBM run uses BGK, inlet ramp t=2 and equilibrium reservoir open boundaries. Both show alternating vortices. The initial conditions/ramping differ, so oscillation phases are not expected to coincide.

Final LBM diagnostics: Mach_max=0.133542; max |rho-1|=0.007284; Q_in=1.000000; Q_out=1.018173.

The remaining flux difference and acoustic transients are relevant limits of the simple open-boundary implementation. No full cylinder grid-convergence study, drag/lift verification or DFG benchmark reproduction is claimed. Streamline plots are instantaneous fields. Pressure uses rho0=1 and outlet reference.

## CLI check

A real CLI run with LBM, a rotated ellipse, and --gif produced numerical arrays, a figure, diagnostics and an animated GIF. All Python files compile. The standalone notebook embeds its solver code and cached snapshots/animations.
