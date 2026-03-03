import warnings


def suppress_warnings() -> None:
    # paramiko 3.x still references TripleDES which cryptography >= 42.0 has moved
    # to the `decrepit` subpackage. Suppress until paramiko ships a fix.
    warnings.filterwarnings(
        "ignore",
        message=".*TripleDES.*",
        category=Warning,
    )

