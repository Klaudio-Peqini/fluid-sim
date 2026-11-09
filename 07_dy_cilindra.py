"""Dy cilindra: gap është largësia midis qendrave, jo hapësira midis sipërfaqeve.

Ekzekutimi i zakonshëm:
    python 07_dy_cilindra.py
Për metodën tjetër:
    python 07_dy_cilindra.py --method lbm
Për parametrat e mundshëm:
    python 07_dy_cilindra.py --help
"""
# %% Parametrat e eksperimentit. Ndryshojini këtu OSE përdorni opsionet e terminalit.
METHOD = 'cfd'           # 'cfd': Navier–Stokes; 'lbm': D2Q9/BGK
SHAPE = 'two_cylinders'
REYNOLDS = 20
NY = 40                 # Nx = 6*Ny për qeliza katrore
DURATION = 4.0          # Koha e modelit; jo koha e pritjes në kompjuter
ANGLE = 0.0             # Gradë; vetëm për drejtkëndëshin/elipsin
GAP = 0.6               # Largësia midis qendrave për dy cilindra
ADVECTION = 'upwind'   # Zbatohet vetëm për metodën CFD
SAVE_GIF = False

# %% Algoritmet përkatëse gjenden në dosjen fluidlab/.
from lesson_tools import flow_lesson

if __name__ == '__main__':
    flow_lesson(shape=SHAPE, re=REYNOLDS, method=METHOD, ny=NY, duration=DURATION,
                angle=ANGLE, gap=GAP, advection=ADVECTION, gif=SAVE_GIF)
