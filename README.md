 # Fluid Flows Framework — complete installation and user guide                                                           

**English edition.** The equivalent Albanian guide is [README_Albanian.md](README_Albanian.md).

This package teaches airflow and viscous-fluid simulation through Couette and Poiseuille flow, channel obstacles, NACA airfoils, and a prescribed-load rotor model. It runs as ordinary python3 code. Jupyter, a graphical interface, and external CFD frameworks are not required.

**Recommended route:** complete Sections 1–6 first. They take you from an extracted ZIP to a small verified run. Then choose the experiments and animation options you need. Run commands in a terminal, not at the python3 `>>>` prompt. Do not copy shell prompt characters such as `$`.

## 1. Extract the package and find the correct folder

Extract the **entire ZIP**, rather than running individual files inside the archive. Open the extracted `Fluid_Flows_Framework` folder. It must contain `flow.py`, both requirements files, and the `fluidlab` and `configs` folders.

| Item | Purpose |
|---|---|
| `flow.py` | Recommended interface for simulations, help, animations, and parallel studies |
| `fluidlab/` | Numerical algorithms and supporting modules; keep this folder beside `flow.py` |
| `configs/` | Editable JSON examples and a custom polygon CSV |
| `01_*.py` through `09_*.py` | Earlier lesson scripts, retained with their original options |
| `requirements.txt` | Basic numerical and plotting dependencies |
| `requirements-parallel.txt` | Basic dependencies plus optional Numba acceleration |
| `examples/v2/` | Computed examples, saved snapshots, and GIFs you can inspect immediately |
| `verification/` | Recorded numerical checks and timing measurements |
| `TESTED_V2.md` | What was tested and the limits of that evidence |
| `LESSONS.md`, `FIZIKA_DHE_ALGORITMET.md`, `AIRFOIL.md` | Earlier teaching explanations and airfoil notes |

Open a terminal in this folder. For example, on Linux/macOS, if extraction produced a folder directly under Downloads:

```bash
cd ~/Downloads/Fluid_Flows_Framework
```

Your extraction location may differ. On Windows, open Command Prompt or PowerShell in the extracted folder, or use `cd "C:\your\actual\path\Fluid_Flows_Framework"`. Replace that example path with your own. Paths containing spaces should be enclosed in quotes.

Check that you are in the right folder:

```bash
python3 -c "from pathlib import Path; print(Path.cwd()); print(Path('flow.py').is_file())"
```

Before creating the environment, use `python3` instead of `python` on systems where that is the available command. The last line should print `True`. If it prints `False`, change folder before continuing.

## 2. Check python3 and create a virtual environment

python3 3.10 or newer is the intended baseline; **python3 3.12 is the recommended starting version because the package was tested with it**. Availability of Numba wheels depends on the python3 version and operating system. If acceleration cannot be installed, the basic NumPy backend remains usable.

A virtual environment keeps this project's installed dependencies separate from other python3 projects. Create it once; activate it whenever you open a new terminal for this project. The commands below name it `.venv`.

### Linux and macOS — bash or zsh

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
```

If several python3 versions are installed and you specifically want python3 3.12, use `python3.12 -m venv .venv` for creation.

### Windows — Command Prompt

With the python3 launcher and python3 3.12 installed:

```bat
py -3.12 --version
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
```

If you use a different supported installation, select its interpreter when creating the environment. Do not substitute a version number that is not installed.

### Windows — PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, you can invoke the environment's interpreter directly without changing execution policy:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-parallel.txt
.\.venv\Scripts\python.exe flow.py --help
```

In this approach, replace `python` in subsequent commands with `.\.venv\Scripts\python.exe`.

### Confirm which interpreter is running

After activation:

```bash
python3 -c "import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)"
python3 -m pip --version
```

The interpreter and pip paths should refer to `.venv`; the Boolean check should print `True`. A `(.venv)` prompt is helpful, but checking the interpreter is more reliable.

Do not put your source code inside `.venv`, and do not distribute or move that environment with the ZIP. Recreate it on another machine. Your simulation results belong in `results/`.

## 3. Install dependencies

For the recommended accelerated setup:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-parallel.txt
```

`requirements-parallel.txt` includes the basic requirements automatically. You do not need to install both files separately.

For a basic installation without Numba:

```bash
python3 -m pip install -r requirements.txt
```

Use `--backend numpy` for this setup, or let `auto` select the available backend. Installing `requirements.txt` does not uninstall Numba if it was already installed in the environment.

Check installation:

```bash
python3 -m pip check
python3 -c "import numpy, scipy, matplotlib, PIL, threadpoolctl; print('Core imports OK')"
```

A healthy dependency installation should report `No broken requirements found.` and `Core imports OK`. For the accelerated setup, also check:

```bash
python3 -c "import numba; print('Numba version:', numba.__version__)"
```

Use `python3 -m pip`, so installation goes through the same interpreter that runs the simulations. Installation normally requires network access; routine simulations and local GIF generation do not.

## 4. First checks: interface, hardware, and a plan

These commands do not advance a simulation:

```bash
python3 flow.py --help
python3 flow.py help run
python3 flow.py help animate
python3 flow.py objects
python3 flow.py hardware
```

`hardware` reports logical CPUs, usable affinity/quota limits, and whether a Numba installation is discoverable. This is a configuration check, not a performance benchmark.

Prepare a small plan:

```bash
python3 flow.py plan --case couette --duration 0.2 --backend numpy --threads 1
```

The output lists resolved parameters and an approximate array-memory requirement. Pressure-factorization storage, compilation, and rendering can require additional memory. `plan` checks configuration and geometry; it does not prove stability or convergence of a complete calculation.

## 5. Your first simulation and GIF

Use a fresh output folder:

```bash
python3 flow.py run --case couette --backend numpy --duration 0.2 --frames 6 --gif velocity --velocity-style vectors --fps 4 --output results/first_check
```

This deliberately short run checks execution and file creation. It is **not** intended to reach steady Couette flow. It should finish with a message beginning `Completed:`.

Inspect these files:

| File in `results/first_check/` | What to check |
|---|---|
| `summary.json` | `status` should be `PASS` after the complete workflow succeeds |
| `config.json` | The parameters should match your command |
| `overview.png` | A saved plot should exist; a separate graphics window is not expected |
| `animations/velocity_vectors.gif` | Open in a GIF-capable browser or image viewer |
| `snapshots.npz` | Saved evolution for making new GIFs without rerunning the solver |
| `history.csv` | Recorded model times and diagnostics |

You can read the completion status from the terminal:

```bash
python3 -c "import json; print(json.load(open('results/first_check/summary.json'))['status'])"
```

If you repeat the same command, the existing nonempty folder is protected. Choose a new name, such as `results/first_check_2`. Only use `--overwrite` when you intentionally want to replace a generated result folder; it removes that folder's contents. Unmarked arbitrary folders are rejected.

## 6. Run the numerical checks

```bash
python3 validate.py
python3 verify_features.py
```

`validate.py` repeats analytical plate-flow comparisons, a plate refinement example, and short obstacle-flow checks. Successful completion prints `ALL CHECKS PASSED` and writes `results/validation.json`.

`verify_features.py` checks geometries, NumPy/Numba equivalence when Numba is installed, rotor force/torque normalization, 3D pressure projection, and slice coordinates. It writes `verification/features.json` and prints a JSON report with `status: PASS`. If Numba is unavailable, its accelerated-backend checks are explicitly marked as skipped.

Run these scripts normally, without Python's `-O` option, because their checks use assertions. They may take longer than the first tiny simulation, especially during initial JIT compilation. A successful numerical check is not experimental validation of an airfoil or rotor. `TESTED_V2.md` explains what the recorded checks establish.

## 7. Returning tomorrow, stopping, and using an IDE

After the initial installation, you usually only need to change into the project folder and reactivate the environment. On Linux/macOS:

```bash
cd ~/Downloads/Fluid_Flows_Framework
source .venv/bin/activate
python3 flow.py --help
```

Use the Windows activation command from Section 2 on Windows. Packages normally need reinstalling only if you create a new environment or change dependencies.

Type `deactivate` to leave the environment. This does not delete code or results. To interrupt a long run, use Ctrl+C in the terminal; partial files may remain and should not be interpreted as a completed successful run.

In VS Code, Spyder, or PyCharm, select the `.venv` interpreter and use the project folder as the working directory. A terminal that activates one interpreter and an IDE that selects another can give different import results. Printing `sys.executable` helps identify this mismatch.

## 8. Flexible commands and available objects

The recommended command structure is:

```text
python3 flow.py SUBCOMMAND OPTIONS
```

| Subcommand | Purpose |
|---|---|
| `run` | Compute a simulation and optionally create GIFs |
| `plan` | Resolve parameters and inspect geometry/memory estimates |
| `animate` | Use saved snapshots to create GIFs |
| `sweep` | Run independent parameter combinations in parallel |
| `benchmark` | Measure NumPy/Numba stepping speed and numerical differences |
| `hardware` | Inspect CPU allocation and optional acceleration availability |
| `objects` | List cases and their dimensionality |

Both `python3 flow.py help run` and `python3 flow.py run --help` display help. Options after a subcommand can be reordered. `run --gif ...` and `animate --fields ...` are intentionally different option names.

Cases are `couette`, `poiseuille`, `none`, `rectangle`, `cylinder`, `ellipse`, `two_cylinders`, `airfoil`, `polygon`, and `rotor`. `none` means an unobstructed channel. `--object` is an alias for `--case`.

Common examples:

```bash
python3 flow.py run --case cylinder --method lbm --re 20 --ny 64 --duration 4 --threads auto --gif all
python3 flow.py run --case rectangle --method cfd --re 20 --gif velocity pressure
python3 flow.py run --case ellipse --angle 30 --method cfd --duration 3
python3 flow.py run --case two_cylinders --gap 0.8 --duration 3
python3 flow.py run --case none --method cfd --duration 2
python3 flow.py run --case couette --nu 0.05 --duration 8 --gif all --fps 4
python3 flow.py run --case poiseuille --acceleration 0.2 --duration 8 --gif all
```

Without `--output`, every simulation gets a new automatically named folder in `results/`. The unified plate time histories use `--method cfd` and the small serial 1D equation; the older plate scripts also retain final LBM comparisons.

## 9. Parameters, grids, and physical interpretation

| Option | Meaning |
|---|---|
| `--duration` | Target simulated time, not computer waiting time |
| `--frames` | Requested snapshot sampling; 2–300; actual saved times are recorded |
| `--fps` | GIF playback rate; 1–60 frames/s; default 12 |
| `--ny`, `--nx` | 2D grid counts; omit Nx for automatic sizing |
| `--length`, `--height` | 2D channel dimensions |
| `--diameter` / `--chord` | Reference length D; chord for an airfoil |
| `--mean-speed` | Mean channel-inlet velocity U |
| `--re` | Reynolds number U D / nu for channel objects |
| `--nu` | Kinematic viscosity for the reduced plate-flow equation |
| `--angle` | Object angle in degrees; airfoil convention is described below |
| `--gap` | Centre-to-centre distance for two cylinders |
| `--center-x`, `--center-y` | Object location; quarter-chord location for an airfoil |
| `--advection` | CFD transport: `upwind` or `central` |
| `--lattice-speed` | LBM reference speed in lattice units |
| `--backend` | `auto`, `numpy`, or `numba` |
| `--threads` | Requested CPU threads or `auto` |

Use square 2D cells: `length/nx = height/ny`. If the automatic Nx is incompatible with your dimensions, choose a consistent ratio or explicit Nx. In channel examples the inlet is parabolic, with a centreline speed about 1.5 times its mean. Inlet Reynolds number uses the **mean** speed. For the ellipse, D is its minor-axis length.

Changing D while holding Re and U fixed also changes nu = U D / Re. For the plate equation, `--nu` is used directly. Parameters are case-specific: for example, `--grid` sets the rotor's 3D grid, whereas `--ny` sets a channel/plate grid. Read `plan` output before a large run.

The 2D teaching cases use consistent reference units; do not assume their default dimensions represent a particular real tube or wing. State your chosen length, velocity, and time scales before comparing them with measurements. Rotor inputs use SI units: metres, seconds, kilograms, newtons, and pascals; RPM means revolutions per minute.

The last 2D step may slightly exceed the target duration. A very short target can also produce fewer snapshots than requested because a solver cannot save intermediate states it did not compute. GIF titles use the actual saved times. Increasing `--frames` does not refine the numerical grid or timestep.

## 10. GIF fields, slower playback, and regeneration

Create all animations during a run:

```bash
python3 flow.py run --case airfoil --gif all --velocity-style both --fps 4
```

The standard 2D names in `animations/` are:

| File | Display |
|---|---|
| `velocity_vectors.gif` | Speed magnitude with velocity arrows |
| `velocity_streamlines.gif` | Speed magnitude with instantaneous streamlines |
| `pressure.gif` | Pressure relative to the pressure reference |
| `vorticity.gif` | 2D vorticity |

Velocity styles are `vectors`, `streamlines`, and `both`. `--no-gif` skips GIF generation but keeps numerical snapshots. Colour scales remain fixed across the frames of each animation.

**To make playback slower, lower FPS.** At 12 frames/s, 60 frames play for roughly 5 seconds; at 4 frames/s, they play for roughly 15 seconds. A viewer may round GIF timing. Changing FPS changes playback, not the computed physics.

Regenerate existing GIFs at a slower rate:

```bash
python3 flow.py animate results/first_check --fields all --velocity-style both --fps 4
python3 flow.py animate examples/v2/airfoil --fields all --fps 4
```

These commands need `snapshots.npz` and `config.json` in the result folder. They do **not** recompute the flow. They replace the corresponding generated GIF/PNG exports in the animation output folder. Choose a separate export folder if you want to retain both playback versions:

```bash
python3 flow.py animate examples/v2/airfoil --fields all --fps 4 --output results/airfoil_slow_gifs
```

`results/first_check` contains only a short startup. The supplied airfoil example contains a longer evolution. `animate` cannot create a longer physical history than the snapshots contain.

Streamlines are tangent to the instantaneous velocity field; they are not particle trajectories in unsteady flow. Pressure is constant in Couette's reduced model. Poiseuille's imposed gradient is constant in time. Little or no field change in their pressure GIFs is therefore expected.

## 11. Airfoils and custom objects

```bash
python3 flow.py run --case airfoil --naca 2412 --angle 8 --gif all
python3 flow.py run --case airfoil --naca 0012 --angle 0 --output results/symmetric_wing
python3 flow.py run --case airfoil --ny 192 --output results/finer_wing
python3 flow.py run --config configs/polygon.json --gif all
```

An airfoil's positive angle means nose-up: its leading edge lies above its trailing edge, with clockwise rotation of the leading-edge-to-trailing-edge chord in this drawing. The pivot is at quarter chord. NACA codes are text; use `"0012"` in JSON to retain the leading zeros.

The airfoil model is a **2D section in a channel**, not a finite 3D wing. The quick default grid gives only about nine cells across maximum thickness. Refinement and boundary studies are needed for quantitative results. Lift and drag coefficients are not computed.

For a polygon, supply a CSV with header `x,y` and at least three local-coordinate vertices. The code rotates/translates it to the selected centre. `configs/triangle.csv` is a working example. Choose `--diameter` to define the Reynolds reference length of your object. Saved custom-object results include a source polygon copy so their configuration can be replayed.

## 12. Drone rotor: 3D fields and useful slices

```bash
python3 flow.py run --case rotor --threads auto --gif all --output results/my_rotor
```

Default illustrative inputs are one horizontal rotor, R=0.1 m, RPM=1800, thrust 0.5 N, and torque 0.008 N m. Air starts at rest; z points upward and the force on air points downward. The default display is an xz plane at y=0.

| Rotor option | Meaning |
|---|---|
| `--grid 40 40 48` | 3D grid counts |
| `--radius`, `--rpm` | Rotor radius and rotation rate |
| `--thrust`, `--torque` | Prescribed per-rotor thrust and torque |
| `--rotor-count 1` / `4` | Supported single-rotor or quad layout |
| `--payload-mass`, `--vehicle-mass` | Payload and aircraft-plus-battery masses; supply both |
| `--epsilon` | Force regularization width; must be resolved and fit inside the domain |
| `--domain-scale` | Scale the outer computational box |
| `--max-dt`, `--blade-step` | Additional timestep/blade-motion limits |

The solver uses **3D rotating actuator lines with prescribed loads**, not resolved solid blade surfaces. RPM controls rotation of force lines; thrust and torque are independent inputs. No turbulence closure, fuselage, ground, or aerodynamic blade-load prediction is included. Tip Mach above 0.3 is rejected.

After computing `results/my_rotor`, show a horizontal slice above and below the default rotor:

```bash
python3 flow.py animate results/my_rotor --fields velocity pressure --plane xy --position 0.1 --fps 4
python3 flow.py animate results/my_rotor --fields velocity pressure --plane xy --position -0.1 --fps 4
```

For `xy`, `position` means z; for `xz`, it means y; for `yz`, it means x. Positions must lie within the saved cell-centre coordinates. 3D animation filenames include the plane and position. Velocity colour shows the full 3D speed; arrows/streamlines use the in-plane components. The plotted curl is an oriented in-plane component, not total vorticity magnitude. Dashed rotor outlines indicate disk locations or projections.

The optional quad preset is:

```bash
python3 flow.py plan --config configs/quad_4kg_payload.json
python3 flow.py run --config configs/quad_4kg_payload.json --no-gif
```

It uses **4 kg payload plus an explicitly assumed 3 kg aircraft and battery**, four rotors, R=0.2811 m, RPM=2640, and illustrative torque 0.429 N m per rotor. Required steady total thrust is 7 × 9.80665 = 68.64655 N, distributed over four rotors. Startup loads are ramped, so they are initially smaller. Supply your actual vehicle mass and operating measurements. This preset is not identification or validation of your drone. When specifying both masses, do not also specify thrust.

## 13. Parallel execution and measured performance

For 2D channel cases, `auto` uses Numba when installed. CPU availability respects affinity and supported cgroup quota information. `auto` selects up to four threads; requesting more than the allocation is rejected.

| Work | Parallel implementation and limits |
|---|---|
| LBM | Compiled parallel cell kernels for collision, streaming, and reservoirs |
| 2D CFD | Parallel momentum predictor; sparse pressure LU stays serial |
| 3D rotor | Multithreaded SciPy pressure transforms; NumPy momentum/forcing |
| 1D plate flow | Small serial solve; use independent runs for parallel studies |
| GIF generation | Separate processes for independent exports |
| Parameter studies | Separate processes for independent simulations |

For the 1D/2D NumPy reference backend, effective solver threads are reported as one. Extra threads do not make those array stencils parallel. There is no GPU backend or MPI domain decomposition across cluster nodes.

For GIF export parallelism, use `--render-jobs 2` during a run, or `animate --jobs 2`. This speeds independent exports, not fluid stepping. Use these values only if at least two CPUs are available.

Measure your machine:

```bash
python3 flow.py benchmark --ny 96 --steps 200 --threads 1 2 4 --output benchmark_my_machine.json
```

If fewer CPUs are allocated, shorten the list, for example `--threads 1 2` or `--threads 1`. The recorded preparation benchmark measured about 5.6× faster LBM and 1.4× faster CFD against NumPy at four Numba threads. Those gains combine compilation and threading; moving from one to four Numba threads alone gave about 2.2× and 1.07×. Initial compilation, setup, and plotting are excluded. Results are hardware-dependent.

For a study of several angles:

```bash
python3 flow.py sweep --config configs/sweep_angles.json --jobs 2 --threads 2 --output results/angle_study
```

This needs at least four allocated CPUs because `jobs × threads` must fit the CPU budget. A serial smoke test that works on a single CPU is:

```bash
python3 flow.py sweep --config configs/sweep_quick.json --jobs 1 --threads 1 --output results/quick_study
```

The sweep JSON has `base` parameters and lists under `vary`; their Cartesian combinations are separate cases. Each gets a result folder and log. `sweep_summary.json` records process success. Nested rendering uses one process per case to avoid oversubscription.

## 14. JSON configuration and reproducibility

```bash
python3 flow.py plan --config configs/airfoil.json
python3 flow.py run --config configs/airfoil.json --angle 12 --output results/wing12
python3 flow.py run --config results/wing12/config.json --angle 0 --output results/wing0
```

Explicit terminal options override JSON values, which override the case defaults. JSON uses underscore keys such as `mean_speed` or `velocity_style`; command-line options use hyphens such as `--mean-speed` or `--velocity-style`. Use standard JSON: double-quoted strings, no comments, and lowercase `true`/`false`.

`config.json` stores reusable `parameters` as well as execution metadata. Replay uses the parameter section. Set a new output folder for a new experiment. Change one physical parameter at a time when interpreting results. To record an installed environment, save `python3 -m pip freeze > environment_installed.txt`; recreate environments from appropriate dependency files rather than copying `.venv`.

## 15. Are the older numbered scripts still valid?

**Yes, with their original options.** Their command interface is separate from `flow.py`.

| Script | Lesson |
|---|---|
| `01_couette.py` | Couette startup and final FD/LBM comparison |
| `02_poiseuille.py` | Poiseuille flow and analytical comparison |
| `03_pengesa_drejtkendore.py` | Rectangular obstacle |
| `04_cilindri_re20.py` | Cylinder at Re=20 |
| `05_cilindri_re100.py` | Longer cylinder run at Re=100 |
| `06_elipsa.py` | Rotated ellipse |
| `07_dy_cilindra.py` | Two-cylinder interaction |
| `08_krahasimi_cfd_lbm.py` | Plot comparisons from original or selected data |
| `09_profili_i_krahut.py` | Original 2D NACA airfoil lesson |

```bash
python3 01_couette.py --help
python3 01_couette.py --gif --frames 100 --output results/legacy_couette
python3 04_cilindri_re20.py --method lbm --gif --output results/legacy_cylinder
```

The original channel scripts produce a vorticity GIF; the original plate scripts produce `velocity.gif`. They do not accept every new `flow.py` option. For pressure GIFs, velocity styles, playback FPS, parallel backends, and rotor cases, use the unified interface. In particular, the legacy `run_case.py` is distinct from `flow.py run`. Read `LESSONS.md` for the earlier interface.

## 16. Reading results and understanding limits

`summary.json` records completion, selected backend, effective threads, timings, diagnostic extrema where recorded, and final quantities. `PASS` means the implemented workflow and numerical gates passed. It is not a certificate of physical accuracy.

`snapshots.npz` contains times and field evolution; `fields.npz` contains final fields. Simulation arithmetic is float64; saved fields are float32. For 2D, pressure is expressed for reference density 1, effectively p/rho0. Rotor pressure is in pascals. `history.csv` can be inspected with ordinary spreadsheet or plotting tools.

The 2D models are laminar and use stepped Cartesian walls. Upwind advection adds numerical diffusion; central advection needs tighter timestep control. LBM is weakly compressible and uses simple equilibrium reservoir inlet/outlet conditions, not Zou–He. The cylinder geometry is not the exact DFG benchmark. Full grid/time/domain independence and laboratory comparison remain necessary for quantitative project claims.

## 17. Troubleshooting

| Symptom | What to do |
|---|---|
| `can't open file flow.py` | Change to the extracted `Fluid_Flows_Framework` folder; check `Path('flow.py').is_file()` |
| `No module named ...` | Check `sys.executable`, activate the intended environment, and install through its `python3 -m pip` |
| Missing `venv` / `ensurepip` | Ensure the selected python3 installation includes virtual-environment support; on managed machines ask the administrator to provide it |
| Numba import/install failure | Use a compatible interpreter, preferably the tested python3 3.12, or use the basic requirements with `--backend numpy` |
| `unrecognized arguments` | Check the specific command's `--help`; legacy and unified scripts have different options |
| Output folder is not empty | Choose a new `--output`; only deliberately replace a marked result folder with `--overwrite` |
| No graphics window opens | Open the generated PNG/GIF files; plotting is saved to disk |
| GIF plays too fast | Regenerate with `animate ... --fps 4` or `--fps 2` |
| GIF shows a short startup only | The saved simulation was short; run a longer `--duration` if a longer physical history is needed |
| Pressure GIF looks constant for plates | This is expected for the imposed reduced-model pressure field |
| Invalid grid / thin airfoil | Use square cells and increase resolution to represent the body |
| Too many threads/jobs | Read `hardware` output and fit within the allocation |
| LBM Mach/density or projection gate failure | Treat the run as failed; review the reported parameters, timestep restrictions, resolution, and model regime |
| Slow first accelerated run | Numba compiles on first use; compare warmed-up runs or use `benchmark` |

On a remote compute node, copy the desired result images/GIFs to your local computer for viewing. A graphical desktop is not required on the compute node. Do not add threads beyond the scheduler allocation.

## 18. Suggested first teaching session

First confirm the environment, run the small Couette check, and view its GIF. Then run `validate.py`. Inspect the already computed airfoil animations before starting a longer new calculation. Finally, change one parameter, retain its configuration and diagnostics, and explain the physical result in a few sentences.

Official environment references: [python3 venv](https://docs.python.org/3/library/venv.html), [python3 Packaging installation guide](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/), and [pip check](https://pip.pypa.io/en/stable/cli/pip_check/). Project commands and model descriptions were checked against the supplied source. A fresh Linux/python3 3.12 environment passed dependency installation, the first Couette run, GIF regeneration, and both numerical check scripts. See `verification/readme_installation.json` for the recorded versions and checks. Windows/macOS activation examples follow their documented shell syntax and were not executed here.
