"""Shadow Trace Calculation by Rust. (:mod:`qurrium_pgp.shadow_trace_rust`)

This file is type information for the Rust implementation of shadow trace calculations.
"""

from typing import Sequence

# pylint:disable=unused-argument
def perform_trace_calculation(data: Sequence[Sequence[str]], subs: Sequence[int]) -> float:
    """Perform the trace calculation for the given data and subs.

    Args:
        data (Sequence[Sequence[str]]): The measurement data.
        subs (Sequence[int]): The subset of qubits to consider for the trace calculation.

    Returns:
        float: The result of the trace calculation.
    """
