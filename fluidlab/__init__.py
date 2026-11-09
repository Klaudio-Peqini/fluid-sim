"""Transparent teaching solvers: finite differences and D2Q9 lattice Boltzmann."""
from .geometry import channel_geometry
from .conventional import ProjectionFlow, plate_fd
from .lbm import LatticeFlow, plate_lbm
from .plotting import plot_flow, animate_flow
