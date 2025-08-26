"""Qurrium PQP Crossroads - Utilities (:mod:`qurrium_quam_libs.utils`)"""

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
