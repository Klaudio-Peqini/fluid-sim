"""Cilindër Re=100: vorbullat kërkojnë një kohë të gjatë zhvillimi.

Ekzekutimi i zakonshëm:
    python 05_cilindri_re100.py
Për metodën tjetër:
    python 05_cilindri_re100.py --method lbm
Për parametrat e mundshëm:
    python 05_cilindri_re100.py --help
"""
# %% Parametrat e eksperimentit. Ndryshojini këtu OSE përdorni opsionet e terminalit.
METHOD = 'cfd'           # 'cfd': Navier–Stokes; 'lbm': D2Q9/BGK
SHAPE = 'cylinder'
REYNOLDS = 100
NY = 60                 # Nx = 6*Ny për qeliza katrore
DURATION = 18.0          # Koha e modelit; jo koha e pritjes në kompjuter
ANGLE = 0.0             # Gradë; vetëm për drejtkëndëshin/elipsin
GAP = 0.6               # Largësia midis qendrave për dy cilindra
ADVECTION = 'central'   # Zbatohet vetëm për metodën CFD
SAVE_GIF = True

# %% Algoritmet përkatëse gjenden në dosjen fluidlab/.
from lesson_tools import flow_lesson

if __name__ == '__main__':
    flow_lesson(shape=SHAPE, re=REYNOLDS, method=METHOD, ny=NY, duration=DURATION,
                angle=ANGLE, gap=GAP, advection=ADVECTION, gif=SAVE_GIF)
