# """Qurrium PQP Crossroads - Classical Shadow Conversion Module
# (:mod:`qurrium_pqp.classical_shadow`)

# This module provides functions to transform
# the output of Qurrium to the text file format in
# Predicting Properties of Quantum Many-Body Systems,
# which the example is in following:

# .. code-block:: text

#     [system size]
#     [subsystem 1 size] [position of qubit 1] [position of qubit 2] ...
#     [subsystem 2 size] [position of qubit 1] [position of qubit 2] ...

# """

# from typing import Literal, Any
# from collections.abc import Sequence
# from pathlib import Path

# from qiskit import QuantumCircuit

# from qurry import __version__
# from qurry.qurrent.classical_shadow import ShadowUnveilExperiment
# from qurry.process.classical_shadow.spreadout import spreadout

# from .utils import QURRIUM_VERSION


# # qurrium to PGP transformation
# def check_classical_shadow_exp(
#     classical_shadow_exp: ShadowUnveilExperiment,
# ) -> tuple[dict[int, dict[int, int]], dict[int, int]]:
#     """Check if the classical shadow experiment is valid for conversion,
#     then return its random basis and registers mapping.

#     Args:
#         classical_shadow_exp (ShadowUnveilExperiment):
#             The Qurry experiment to check.

#     Raises:
#         TypeError: If the input is not a ShadowUnveilExperiment.
#         ValueError: If required attributes are missing or invalid.

#     Returns:
#         tuple[dict[int, dict[int, int]], dict[int, int]]:
#             random_unitary_ids mapping from the experiment and registers mapping.
#     """
#     if not isinstance(classical_shadow_exp, ShadowUnveilExperiment):
#         raise TypeError(
#             "The input must be an instance of ShadowUnveilExperiment "
#             "from qurry.qurrent.classical_shadow."
#         )
#     if classical_shadow_exp.args.unitary_located is None:
#         raise ValueError("The unitary located must be specified in the experiment.")
#     if classical_shadow_exp.args.qubits_measured is None:
#         raise ValueError("The qubits measured must be specified in the experiment.")
#     if classical_shadow_exp.args.registers_mapping is None:
#         raise ValueError("The registers mapping must be specified in the experiment.")
#     measured_qubits = set(classical_shadow_exp.args.qubits_measured)
#     unitary_located = set(classical_shadow_exp.args.unitary_located)
#     missing_qubits = measured_qubits - unitary_located
#     if missing_qubits:
#         raise ValueError(
#             "All measured qubits must be part of the unitary located. "
#             + f"Missing qubits: {sorted(missing_qubits)}"
#         )

#     if (0, 13, 0) < QURRIUM_VERSION:
#         if classical_shadow_exp.args.random_basis is None:
#             raise ValueError("The experiment must have 'random_basis' in args.")
#         random_basis = classical_shadow_exp.args.random_basis
#     else:
#         if "random_unitary_ids" not in classical_shadow_exp.beforewards.side_product:
#             raise ValueError("The experiment must have 'random_unitary_ids' in side products.")
#         random_basis: dict[int, dict[int, int]] = classical_shadow_exp.beforewards.side_product[
#             "random_unitary_ids"
#         ]
#     return random_basis, classical_shadow_exp.args.registers_mapping


# def get_gate_indices(random_basis: dict[int, int], registers_mapping: dict[int, int]) -> list[int]:
#     """Get the gate indices for the QuaLibs format.

#     Args:
#         random_basis (dict[int, int]):
#             Mapping of qubit indices to random basis.
#         registers_mapping (dict[int, int]):
#             Mapping of qubit indices and classical registers.
#     Returns:
#         list[int]: A list of gate indices corresponding to the qubits.
#     """
#     return [random_basis[qi] for qi in registers_mapping.keys()]


# def single_counts_processing(
#     single_counts: dict[str, int],
#     single_random_basis: dict[int, int],
#     registers_mapping: dict[int, int],
# ) -> tuple[dict[str, int], list[int]]:
#     """Single counts processing for QuaLibs format.

#     Args:
#         single_single_counts (dict[str, int]):
#             The counts of single-shot results.
#         single_random_basis (dict[int, int]):
#             Mapping of qubit indices to random basis.
#         registers_mapping (dict[int, int]):
#             Mapping of qubit indices and classical registers.

#     Returns:
#         tuple[dict[str, int], list[int]]:
#             A tuple containing the bitstring and the corresponding gate indices.
#     """

#     return (
#         {k[: len(registers_mapping)]: v for k, v in single_counts.items()},
#         get_gate_indices(single_random_basis, registers_mapping),
#     )


# def qurrium_to_pqp_result(
#     classical_shadow_exp: ShadowUnveilExperiment,
# ) -> Sequence[Sequence[str]]:
#     """Convert a Qurrium experiment to Predicting Quantum Properties result.

#     Args:
#         classical_shadow_exp (ShadowUnveil): The Qurrium experiment to convert.

#     Returns:
#         Sequence[Sequence[str]]: The data in PQP format.
#     """
#     random_basis, registers_mapping = check_classical_shadow_exp(classical_shadow_exp)
#     shots, singleshot_counts, random_basis = spreadout(
#         classical_shadow_exp.commons.shots, classical_shadow_exp.afterwards.counts, random_basis
#     )

#     result = [
#         multiple_shots_processing(single_counts, single_random_unitary_id, registers_mapping)
#         for (idx, single_random_unitary_id), single_counts in zip(
#             random_basis.items(), classical_shadow_exp.afterwards.counts
#         )
#     ]
#     return result
