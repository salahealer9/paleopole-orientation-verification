"""
geometry.py
===========

Spherical-geometry primitives for the pre-registered paleopole orientation
verification analysis.

This module is imported by all analysis scripts that need to compute
great-circle / meridian intersections from raw (latitude, longitude,
bearing) triples. Centralising these primitives means the geometry is
defined once, tested once, and used consistently across scripts.

Conventions
-----------
- Latitudes in degrees, range [-90, +90].
- Longitudes in degrees, range [-180, +180]. East is positive.
- Bearings in degrees, measured clockwise from local north. Range
  unrestricted, but for this project bearings are folded into [-45, +45]
  (the data owner's "northernface" convention).
- The "great-circle pole vector" of a great circle is the unit vector
  perpendicular to the plane containing the circle, expressed in
  Earth-centered Cartesian coordinates with the z-axis through the
  north pole, the x-axis through (lat 0, lon 0), and the y-axis through
  (lat 0, lon 90E).

Conventions adopted from the data owner (see analysis log 2026-05-17):
- "No Intersect 47.1W" = northern-hemisphere filter: intersections with
  latitude < 0 are operationally excluded from the analysis. This module
  computes the geometric intersection without filtering; the filter is
  applied at the analysis layer.
- Pole-passing case: when a great circle passes through both geographic
  poles, the intersection with any meridian is geometrically at BOTH
  ±90° simultaneously. By convention this module returns +90° (the
  northern pole), matching the data owner's convention and consistent
  with the northern-hemisphere focus of the proposed paleopoles.

Pre-registration: https://doi.org/10.5281/zenodo.20258204
License:          MIT
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Great-circle pole vector from (lat, lon, bearing)
# ---------------------------------------------------------------------------


def lat_lon_bearing_to_great_circle_pole(
    lat_deg: np.ndarray,
    lon_deg: np.ndarray,
    bearing_deg: np.ndarray,
) -> np.ndarray:
    """Return the unit pole vector of the great circle through (lat, lon)
    with the given initial bearing.

    Parameters
    ----------
    lat_deg, lon_deg, bearing_deg : array-like, broadcastable to the same shape.

    Returns
    -------
    pole : array of shape (..., 3)
        Unit pole vectors in Earth-centered Cartesian coordinates.
        Rows where the input is invalid (NaN) propagate NaN.
    """
    lat = np.deg2rad(lat_deg)
    lon = np.deg2rad(lon_deg)
    beta = np.deg2rad(bearing_deg)

    # Position vector r at (lat, lon) on the unit sphere.
    r_x = np.cos(lat) * np.cos(lon)
    r_y = np.cos(lat) * np.sin(lon)
    r_z = np.sin(lat)

    # Local east and north unit vectors at (lat, lon).
    east_x = -np.sin(lon)
    east_y = np.cos(lon)
    # east_z = 0 (omitted from product below)

    north_x = -np.sin(lat) * np.cos(lon)
    north_y = -np.sin(lat) * np.sin(lon)
    north_z = np.cos(lat)

    # Tangent vector in the direction of the bearing.
    # Bearing β is clockwise from local north:
    #   t̂ = cos(β) · north + sin(β) · east
    t_x = np.cos(beta) * north_x + np.sin(beta) * east_x
    t_y = np.cos(beta) * north_y + np.sin(beta) * east_y
    t_z = np.cos(beta) * north_z  # east_z = 0

    # Pole n̂ = r × t̂  (normalised).
    n_x = r_y * t_z - r_z * t_y
    n_y = r_z * t_x - r_x * t_z
    n_z = r_x * t_y - r_y * t_x

    norm = np.sqrt(n_x**2 + n_y**2 + n_z**2)
    norm = np.where(norm < 1e-12, np.nan, norm)
    return np.stack([n_x / norm, n_y / norm, n_z / norm], axis=-1)


# ---------------------------------------------------------------------------
# Great-circle / meridian intersection latitude
# ---------------------------------------------------------------------------


def great_circle_meridian_intersection_lat(
    pole: np.ndarray,
    target_lon_deg: float,
) -> np.ndarray:
    """Compute the latitude where a great circle (specified by its pole
    vector) crosses the meridian at longitude *target_lon_deg*.

    A point on the meridian λ₀ has the form:
        u(φ) = (cos φ cos λ₀, cos φ sin λ₀, sin φ)

    The intersection condition u · n̂ = 0 gives:
        tan φ = -(n_x cos λ₀ + n_y sin λ₀) / n_z

    Latitude φ is bounded by ±90°, so ``arctan`` (range (-π/2, π/2)) is
    the correct inverse — NOT ``arctan2``, which would occasionally place
    the answer on the antipodal half-meridian.

    Special cases:
      - Degenerate (great circle coincides with target meridian): NaN.
      - Pole-passing (denominator → 0 but numerator ≠ 0): returns +90°
        by convention (see module docstring).

    Parameters
    ----------
    pole : array of shape (..., 3)
    target_lon_deg : float

    Returns
    -------
    lat_deg : array of shape (...)
    """
    lam = np.deg2rad(target_lon_deg)

    n_x = pole[..., 0]
    n_y = pole[..., 1]
    n_z = pole[..., 2]

    numerator = -(n_x * np.cos(lam) + n_y * np.sin(lam))
    denominator = n_z

    degenerate = (np.abs(numerator) < 1e-10) & (np.abs(denominator) < 1e-10)
    pole_passing = (np.abs(denominator) < 1e-10) & ~degenerate

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = numerator / denominator
        lat = np.rad2deg(np.arctan(ratio))

    lat = np.where(pole_passing, 90.0, lat)
    invalid = np.isnan(n_x) | np.isnan(n_y) | np.isnan(n_z)
    lat = np.where(degenerate | invalid, np.nan, lat)
    return lat


# ---------------------------------------------------------------------------
# End-to-end convenience
# ---------------------------------------------------------------------------


def compute_intersection_lat(
    lat_deg: np.ndarray,
    lon_deg: np.ndarray,
    bearing_deg: np.ndarray,
    target_lon_deg: float,
) -> np.ndarray:
    """End-to-end: from (lat, lon, bearing) compute the latitude where
    the great circle crosses *target_lon_deg*.

    Returns NaN for degenerate cases (great circle coincides with target).
    """
    pole = lat_lon_bearing_to_great_circle_pole(lat_deg, lon_deg, bearing_deg)
    return great_circle_meridian_intersection_lat(pole, target_lon_deg)


# ---------------------------------------------------------------------------
# Self-tests (runnable as `python -m analysis.geometry` or via test runner)
# ---------------------------------------------------------------------------


def run_self_tests() -> None:
    """Run a small set of analytically-known test cases. Raises
    AssertionError on failure.
    """
    cases = [
        # (lat, lon, bearing, expected, tol, description)
        (0.0, -47.1, 0.0, None, 0.0, "On-meridian, bearing 0 — degenerate"),
        (45.0, -47.1, 0.0, None, 0.0, "On-meridian at lat 45, bearing 0 — degenerate"),
        (0.0, -47.1, -45.0, 0.0, 1e-6, "On-meridian, bearing -45 — intersection at site"),
        (0.0, -30.0, 90.0, 0.0, 1e-6, "Equator at bearing 90 — traces equator"),
        (30.0, -40.0, -30.0, 39.356, 0.01, "Hand-computed: (30, -40), bearing -30"),
        (20.4476, -97.3779, 0.0, 90.0, 1e-6, "Pole-passing case 1: bearing 0"),
        (36.4222, 9.2183, 0.0, 90.0, 1e-6, "Pole-passing case 2: bearing 0"),
    ]

    target = -47.1
    failures = []
    for lat, lon, bearing, expected, tol, description in cases:
        result = compute_intersection_lat(
            np.atleast_1d(lat), np.atleast_1d(lon), np.atleast_1d(bearing), target
        )[0]
        if expected is None:
            if not np.isnan(result):
                failures.append(f"{description}: expected NaN, got {result}")
        else:
            if np.isnan(result) or abs(result - expected) > tol:
                failures.append(
                    f"{description}: expected {expected}, got {result}, tol={tol}"
                )

    if failures:
        raise AssertionError(
            "Geometry self-tests failed:\n  " + "\n  ".join(failures)
        )
    return len(cases)


if __name__ == "__main__":
    n = run_self_tests()
    print(f"geometry.py: {n} self-tests passed.")
