"""Qurrium PQP Crossroads - Utilities (:mod:`qurrium_quam_libs.utils`)"""

from typing import Sequence
from pathlib import Path

from qurry import __version__


def get_version_info() -> tuple[int, int, int]:
    """Get the version information of the Qurrium package.

    Returns:
        tuple[int, int, int]: The major, minor, and patch version numbers.
    """
    version_parts = __version__.split(".")[:3]
    version_parts += ["0"] * (3 - len(version_parts))
    return tuple(map(int, version_parts))  # type: ignore


QURRIUM_VERSION = get_version_info()
"""The current version of Qurrium."""


def convert_to_strnota(bases: int, bits: str) -> tuple[str, str]:
    """Convert bases and bits to string notation.

    Args:
        bases (int): The basis index (0: X, 1: Y, 2: Z).
        bits (str): The measurement outcome ("1" or "-1").

    Returns:
        tuple[str, str]: The string notation representation.
    """
    return (chr(88 + bases), bits if bits == "1" else "-1")


def validate_single_counts(single_counts) -> bool:
    """Validate the single counts dictionary.

    Args:
        single_counts (dict[str, int]): The single counts dictionary to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not isinstance(single_counts, dict):
        return False
    if not all(isinstance(k, str) and isinstance(v, int) for k, v in single_counts.items()):
        return False
    return True


VALID_RANDOM_BASIS = {"X", "Y", "Z"}
"""Valid random basis for measurements."""
VALID_BITS = {"-1", "1"}
"""Valid bits for measurement outcomes."""


def check_pqp_result_per_row(row: Sequence[str], len_row: int, row_index: int):
    """Validate a single row of the PQP result data.

    Args:
        row (Sequence[str]): The row to validate.
        len_row (int): The length of row, which is the number of qubits multiplied by 2.
        row_index (int): The row index (0-based) for error reporting.

    Raises:
        ValueError: If the row is invalid.
    """
    if len(row) != len_row:
        raise ValueError(
            f"Invalid line length at line index {row_index}. "
            f"Expected: {len_row}, Got: {len(row)}"
        )

    pauli_values = row[0::2]
    invalid_pauli = set(pauli_values) - VALID_RANDOM_BASIS
    if invalid_pauli:
        raise ValueError(f"Invalid Pauli operator at row index {row_index}: {invalid_pauli}")

    outcome_values = row[1::2]
    invalid_outcomes = set(outcome_values) - VALID_BITS
    if invalid_outcomes:
        raise ValueError(
            f"Invalid measurement outcome at row index {row_index}: {invalid_outcomes}"
        )


def check_pqp_result(data: Sequence[Sequence[str]], system_size: int):
    """Check the PQP result data with vectorized operations.

    Args:
        data (Sequence[Sequence[str]]): The measurement data.
        system_size (int): The size of the quantum system, which is the number of qubits.

    Raises:
        ValueError: If the data is invalid.
    """
    expect_length = system_size * 2
    for i, row in enumerate(data):
        check_pqp_result_per_row(row, expect_length, i)


def pqp_result_export(
    data: Sequence[Sequence[str]], system_size: int, filename: str | Path
) -> None:
    """Export the PQP result to a text file.

    Args:
        data (Sequence[Sequence[str]]): The measurement data.
        system_size (int): The size of the quantum system, which is the number of qubits.
        filename (str | Path): The path to the output file.
    """
    check_pqp_result(data, system_size)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{system_size}\n")
        f.writelines(f"{' '.join(line)}\n" for line in data)


def pqp_result_read(filename: str | Path) -> tuple[list[list[str]], int]:
    """Read the PQP result from a text file.

    Args:
        filename (str | Path): The path to the input file.

    Returns:
        tuple[list[list[str]], int]: A tuple containing the measurement data and the system size.
    """
    data = []

    with open(filename, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()  # This will iterate first line.
        if not first_line:
            raise ValueError("The input file is empty.")

        system_size = int(first_line)
        expect_length = system_size * 2

        for row_num, line in enumerate(f):  # So here begins from second line.
            row = line.strip().split()
            check_pqp_result_per_row(row, expect_length, row_num)
            data.append(row)

    return data, system_size
