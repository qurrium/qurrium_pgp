"""Shadow Trace Calculation by Python. (:mod:`qurrium_pgp.shadow_trace`)"""

from typing import Sequence, Iterable, Literal
from functools import reduce
from itertools import combinations, batched
import multiprocessing as mp
import tqdm

# pylint:disable=no-name-in-module
from qurrium_pgp.shadow_trace_rust import (
    perform_trace_calculation as perform_trace_calculation_rust,
)


def rho_elt_process(rho_a_i: str, rho_b_i: str, rho_a_i1: str, rho_b_i1: str) -> float:
    """Calculate the trace of two classical shadows at a specific index.

    1. For random basis is not the same, the trace value will be `0.5`
    2. For random basis is the same,
    and the bitstring too, the trace value will be `5`
    3. For random basis is the same,
    but the bitstring is different, the trace value will be `-4`

    Args:
        rho_a_i (str): Element from the first classical shadow at index i.
        rho_b_i (str): Element from the second classical shadow at index i.
        rho_a_i1 (str): Element from the first classical shadow at index i+1.
        rho_b_i1 (str): Element from the second classical shadow at index i+1.

    Returns:
        float: The trace value calculated from the two shadows at the specified index.
    """
    return 0.5 if rho_a_i != rho_b_i else (5 if rho_a_i1 == rho_b_i1 else -4)


def get_trace(
    rho_a: Sequence[str], rho_b: Sequence[str], substring_index: list[int]
) -> float:
    """Calculate the trace of two classical shadows.

    .. code-block:: python

        if rho_a[i] != rho_b[i]:
            tr = 0.5
        else:
            if rho_a[i + 1] == rho_b[i + 1]:
                tr = 5
            else:
                tr = -4

    Args:
        rho_a (Sequence[str]): First classical shadow.
        rho_b (Sequence[str]): Second classical shadow.
        substring_index (list[int]): Subset of qubits to consider for trace calculation.
    Returns:
        float: The trace value calculated from the two shadows.
    """
    if len(substring_index) == 0:
        return 1.0

    return reduce(
        lambda x, y: x * y,
        [
            rho_elt_process(rho_a[i], rho_b[i], rho_a[i + 1], rho_b[i + 1])
            for i in substring_index
        ],
    )


def trace_calculation_unit(
    data_tmp: Sequence[Sequence[str]],
    subs_inner: Sequence[int],
    list_of_pairs: Iterable[tuple[int, int]],
) -> float:
    """Calculate the trace for all pairs of classical shadows.

    Args:
        data_tmp (Sequence[Sequence[str]]):
            2D array containing classical shadows.
        subs_inner (Sequence[int]):
            Subset of qubits to consider for trace calculation.
        list_of_pairs (Iterable[tuple[int, int]]):
            Pairs of indices for which to calculate the trace.

    Returns:
        float: The total trace value calculated from all pairs.
    """
    substring_index = [2 * i for i in subs_inner]

    return sum(
        get_trace(data_tmp[m1], data_tmp[m2], substring_index)
        for m1, m2 in list_of_pairs
    )


def batch_make(num_of_samples: int):
    """Create a batched list of combinations for multiprocessing.

    Args:
        num_of_samples (int): The number of samples to create combinations from.

    Returns:
        A tuple containing:
            - A batched iterable of combinations.
            - The total number of batches.
    """
    return (
        batched(combinations(range(num_of_samples), 2), num_of_samples),
        num_of_samples // 2,
    )


def trace_calculation_unit_wrapper(
    args: tuple[Sequence[Sequence[str]], Sequence[int], Iterable[tuple[int, int]]],
) -> float:
    """Wrapper function for multiprocessing to calculate trace.

    Args:
        args (tuple[Sequence[Sequence[str]], Sequence[int], Iterable[tuple[int, int]]]):
            Tuple containing:
            - data_tmp: 2D array containing classical shadows.
            - subs_inner: Subset of qubits to consider for trace calculation.
            - list_of_pairs: Pairs of indices for which to calculate the trace.
    Returns:
        float: The trace value calculated from the two shadows.
    """
    return trace_calculation_unit(*args)


def perform_trace_calculation_py(
    data: Sequence[Sequence[str]],
    subs: Sequence[int],
) -> float:
    """Perform the trace calculation for the given data and subs by Python

    Args:
        data (Sequence[Sequence[str]]): The measurement data.
        subs (Sequence[int]): The subset of qubits to consider for the trace calculation.

    Returns:
        float: The result of the trace calculation.
    """

    trace_m1_m2 = 0.0
    cpu_count = mp.cpu_count()

    all_combinations_split, all_combinations_split_num = batch_make(len(data))
    chunksize = all_combinations_split_num // cpu_count // 4

    with mp.Pool(cpu_count) as pool:
        print("Using", cpu_count, "processes for parallel computation.")
        # Using multiprocessing to parallelize the trace calculation
        results = pool.imap_unordered(
            trace_calculation_unit_wrapper,
            (
                (data, subs, sub_combination)
                for sub_combination in all_combinations_split
            ),
            chunksize=max(1, chunksize),
        )
        print("Calculating traces for all pairs of classical shadows...")
        trace_m1_m2 += sum(
            tqdm.tqdm(
                results, total=all_combinations_split_num, desc="Calculating traces"
            )
        )

    return trace_m1_m2


def perform_trace_calculation(
    data: Sequence[Sequence[str]],
    subs: Sequence[int],
    backend: Literal["Python", "Rust"] = "Rust",
) -> float:
    """Perform the trace calculation for the given data and subs by Python or Rust.

    Args:
        data (Sequence[Sequence[str]]): The measurement data.
        subs (Sequence[int]): The subset of qubits to consider for the trace calculation.
        backend (Literal["Python", "Rust"]): The backend to use for the calculation.

    Returns:
        float: The result of the trace calculation.
    """
    if backend == "Python":
        return perform_trace_calculation_py(data, subs)
    elif backend == "Rust":
        return perform_trace_calculation_rust(data, subs)
    else:
        raise ValueError(f"Unknown backend: {backend}")
