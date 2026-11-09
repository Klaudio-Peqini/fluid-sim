"""Mësimi 2: Poiseuille — ekzekutoni këtë skedar me Python.

Ndryshoni parametrat në terminal, p.sh.:
    python 02_poiseuille.py --nu 0.05 --duration 12 --output results/poiseuille_nu005
Animacioni: python 02_poiseuille.py --gif --frames 100
Algoritmet janë në fluidlab/conventional.py dhe fluidlab/lbm.py.
"""
# %% Importi i mjeteve. Kjo shenjë lejon edhe ekzekutimin me seksione në VS Code/Spyder.
from lesson_tools import plate_lesson

# %% Ekzekutimi: nuk nevojiten qeliza të një notebook-u ose ndryshore nga skedarë të tjerë.
if __name__ == '__main__':
    plate_lesson('poiseuille')
