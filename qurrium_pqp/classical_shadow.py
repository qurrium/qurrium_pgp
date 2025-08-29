"""Qurrium PQP Crossroads - Classical Shadow Conversion Module
(:mod:`qurrium_pqp.classical_shadow`)

This module provides functions to transform
the output of Qurrium to the text file format in
Predicting Properties of Quantum Many-Body Systems,
which the example is in following:

.. code-block:: text

    [system size]
    [subsystem 1 size] [position of qubit 1] [position of qubit 2] ...
    [subsystem 2 size] [position of qubit 1] [position of qubit 2] ...

"""

from collections.abc import Sequence

from qurry import __version__
from qurry.qurrent.classical_shadow import ShadowUnveilExperiment
from qurry.process.classical_shadow.spreadout import spreadout

from .utils import QURRIUM_VERSION, check_pqp_result, convert_to_strnota


# qurrium to PGP transformation
def check_classical_shadow_exp(
    classical_shadow_exp: ShadowUnveilExperiment,
) -> tuple[dict[int, dict[int, int]], dict[int, int]]:
    """Check if the classical shadow experiment is valid for conversion,
    then return its random basis and registers mapping.

    Args:
        classical_shadow_exp (ShadowUnveil): The Qurrium experiment to convert.

    Raises:
        TypeError: If the input is not a ShadowUnveilExperiment.
        ValueError: If required attributes are missing or invalid.

    Returns:
        tuple[dict[int, dict[int, int]], dict[int, int]]:
            random_unitary_ids mapping from the experiment and registers mapping.
    """
    if not isinstance(classical_shadow_exp, ShadowUnveilExperiment):
        raise TypeError(
            "The input must be an instance of ShadowUnveilExperiment "
            "from qurry.qurrent.classical_shadow."
        )
    if classical_shadow_exp.args.unitary_located is None:
        raise ValueError("The unitary located must be specified in the experiment.")
    if classical_shadow_exp.args.qubits_measured is None:
        raise ValueError("The qubits measured must be specified in the experiment.")
    if classical_shadow_exp.args.registers_mapping is None:
        raise ValueError("The registers mapping must be specified in the experiment.")
    measured_qubits = set(classical_shadow_exp.args.qubits_measured)
    unitary_located = set(classical_shadow_exp.args.unitary_located)
    missing_qubits = measured_qubits - unitary_located
    if missing_qubits:
        raise ValueError(
            "All measured qubits must be part of the unitary located. "
            + f"Missing qubits: {sorted(missing_qubits)}"
        )

    if (0, 13, 0) < QURRIUM_VERSION:
        if classical_shadow_exp.args.random_basis is None:
            raise ValueError("The experiment must have 'random_basis' in args.")
        random_basis = classical_shadow_exp.args.random_basis
    else:
        if "random_unitary_ids" not in classical_shadow_exp.beforewards.side_product:
            raise ValueError("The experiment must have 'random_unitary_ids' in side products.")
        random_basis: dict[int, dict[int, int]] = classical_shadow_exp.beforewards.side_product[
            "random_unitary_ids"
        ]
    return random_basis, classical_shadow_exp.args.registers_mapping


def validate_counts_and_basis(
    idx: int,
    single_counts: dict[str, int],
    single_random_basis: dict[int, int],
) -> str:
    """Validate the single counts and random basis, then return bitstring.

    Args:
        idx (int): The index of the current counts and random basis
        single_counts (dict[str, int]): The counts of single-shot results.
        single_random_basis (dict[int, int]): Mapping of qubit indices to random basis.

    Returns:
        str: The validated bitstring.
    """
    bitstring = next(iter(single_counts.keys()))
    if len(bitstring) != len(single_random_basis):
        raise ValueError(
            "The length of the bitstring must match the number of qubits in single_random_basis. "
            + f"Bitstring and its length: '{bitstring}', {len(bitstring)}. "
            + f"Random basis and its length: '{single_random_basis}', {len(single_random_basis)}. "
            + f"Index: {idx}."
        )
    return bitstring


def combine_counts_and_basis_strnota(
    idx: int,
    single_counts: dict[str, int],
    single_random_basis: dict[int, int],
) -> list[str]:
    """Single counts processing for PQP string notation.

    Args:
        idx (int): The index of the current counts and random basis
        single_counts (dict[str, int]): The counts of single-shot results.
        single_random_basis (dict[int, int]): Mapping of qubit indices to random basis.

    Returns:
        list[str]: Single line of Predicting Quantum Properties result.
    """

    return [
        x
        for bases, bits in zip(
            single_random_basis.values(),
            reversed(validate_counts_and_basis(idx, single_counts, single_random_basis)),
        )
        for x in convert_to_strnota(bases, bits)
    ]


def qurrium_to_pqp_strnota(
    classical_shadow_exp: ShadowUnveilExperiment,
) -> tuple[Sequence[Sequence[str]], dict[int, int]]:
    """Convert a Qurrium experiment to Predicting Quantum Properties result in string notation.

    Args:
        classical_shadow_exp (ShadowUnveil): The Qurrium experiment to convert.

    Returns:
        tuple[Sequence[Sequence[str]], dict[int, int]]:
            The data in PQP format and the registers mapping.
    """
    random_basis, registers_mapping = check_classical_shadow_exp(classical_shadow_exp)
    _shots, singleshot_counts, singleshot_random_basis = spreadout(
        classical_shadow_exp.commons.shots, classical_shadow_exp.afterwards.counts, random_basis
    )

    result = [
        combine_counts_and_basis_strnota(idx, single_counts, single_random_basis)
        for (idx, single_random_basis), single_counts in zip(
            singleshot_random_basis.items(), singleshot_counts
        )
    ]

    check_pqp_result(result, len(registers_mapping))
    return result, registers_mapping


def combine_counts_and_basis_intnota(
    idx: int,
    single_counts: dict[str, int],
    single_random_basis: dict[int, int],
) -> tuple[list[int], list[int]]:
    """Single counts processing for PQP interger notation.

    Args:
        idx (int): The index of the current counts and random basis
        single_counts (dict[str, int]): The counts of single-shot results.
        single_random_basis (dict[int, int]): Mapping of qubit indices to random basis.

    Returns:
        tuple[list[int], list[int]]:
            A tuple containing pauli basis and spin outcomes.
    """

    return list(single_random_basis.values()), [
        int(bits) if bits == "1" else -1
        for bits in reversed(validate_counts_and_basis(idx, single_counts, single_random_basis))
    ]


def qurrium_to_pqp_intnota(
    classical_shadow_exp: ShadowUnveilExperiment,
) -> tuple[list[list[int]], list[list[int]]]:
    """Convert a Qurrium experiment to Predicting Quantum Properties result in integer notation.

    Args:
        classical_shadow_exp (ShadowUnveil): The Qurrium experiment to convert.

    Returns:
        tuple[list[list[int]], list[list[int]]]:
            A tuple containing a list of pauli basis and a list of spin outcomes
    """
    random_basis, _registers_mapping = check_classical_shadow_exp(classical_shadow_exp)
    _shots, singleshot_counts, singleshot_random_basis = spreadout(
        classical_shadow_exp.commons.shots, classical_shadow_exp.afterwards.counts, random_basis
    )

    results = [
        combine_counts_and_basis_intnota(idx, single_counts, single_random_basis)
        for (idx, single_random_basis), single_counts in zip(
            singleshot_random_basis.items(), singleshot_counts
        )
    ]

    pauli_basis, spin_outcome = map(list, zip(*results)) if results else ([], [])

    return pauli_basis, spin_outcome
