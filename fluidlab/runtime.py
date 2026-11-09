"""CPU affinity/quota-aware thread budgets and reproducible backend selection."""
import os,math,importlib.util
from pathlib import Path


def hardware():
    logical=os.cpu_count() or 1
    affinity=len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else logical
    quota=None
    try:
        limit,period=Path('/sys/fs/cgroup/cpu.max').read_text().split()
        if limit!='max':quota=max(1,int(int(limit)/int(period)))
    except (OSError,ValueError):pass
    return {'logical_cpus':logical,'affinity_cpus':affinity,'quota_cpus':quota,
            'usable_cpus':min(affinity,quota or affinity),'numba_available':importlib.util.find_spec('numba') is not None}


def configure(backend='auto',threads='auto',ny=64):
    info=hardware();available=info['usable_cpus']
    n=min(4,available) if str(threads)=='auto' else int(threads)
    if not 1<=n<=available:raise ValueError(f'Threads must be 1..{available} within the current CPU allocation.')
    actual=('numba' if info['numba_available'] else 'numpy') if backend=='auto' else backend
    if actual=='numba' and not info['numba_available']:raise ValueError('Install requirements-parallel.txt to use --backend numba.')
    # Set before importing Numba; BLAS does not compete with cell parallelism.
    os.environ.setdefault('NUMBA_NUM_THREADS',str(available))
    for key in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:
        os.environ[key]='1'
    if actual=='numba':
        import numba
        if n>numba.config.NUMBA_NUM_THREADS:raise ValueError('Requested threads exceed NUMBA_NUM_THREADS environment limit.')
        numba.set_num_threads(n)
    return actual,n,info
