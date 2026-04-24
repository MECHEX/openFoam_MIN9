"""
compute_pod_of.py
-----------------
POD on real OpenFOAM midspan-slice VTP snapshots.

Usage (from repo root or toolkit_test/):
    python toolkit_test/compute_pod_of.py

Input:  postProcessing/midspan_slice/*/midspan.vtp  reachable via VTP_ROOT
Output: toolkit_test/results/pod_of/  (JSON + CSV, same structure as compute_pod.py)

Fields processed:
  - U_x, U_y  (velocity components in the midspan plane)
  - T          (temperature)

Note on physical interpretation
--------------------------------
run001 is STEADY (Re=100, Ri=1.26). The 10 snapshots (t=0.5..5 s) represent
the transient spin-up from the initial condition, not a periodic vortex-shedding
cycle. Mode 1 will capture the fully-developed steady state; modes 2-N capture
the convergence history. Physically meaningful POD requires Re > Re_crit with
a periodic wake. This script is designed to reuse for that future dataset.
"""

from __future__ import annotations

import base64
import csv
import json
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

# ─── paths ───────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = Path(__file__).resolve().parent / "results" / "pod_of"

# VTP snapshots: accessible from Windows through \\wsl.localhost\Ubuntu\...
VTP_ROOT = Path(r"\\wsl.localhost\Ubuntu\home\kik\of_runs\V4b_3D_run001\postProcessing\midspan_slice")


# ─── VTP reader ──────────────────────────────────────────────────────────────

def _decode_vtp_binary_array(text: str, dtype: np.dtype) -> np.ndarray:
    """Decode a base64-encoded VTK binary DataArray.

    VTK binary inline format: first 4 bytes = uint32 data-byte-count,
    then raw bytes of the actual data.
    """
    raw = base64.b64decode(text.strip())
    header_bytes = 4
    n_bytes = struct.unpack_from("<I", raw, 0)[0]
    data_raw = raw[header_bytes : header_bytes + n_bytes]
    return np.frombuffer(data_raw, dtype=dtype)


def read_vtp_snapshot(path: Path) -> dict[str, np.ndarray]:
    """Return dict with keys 'x', 'y', 'T', 'Ux', 'Uy', 'Uz', 'p_rgh'."""
    tree = ET.parse(path)
    root = tree.getroot()

    piece = root.find(".//Piece")

    # ── coordinates ──
    pts_da = piece.find("Points/DataArray")
    pts = _decode_vtp_binary_array(pts_da.text, np.float32).reshape(-1, 3)
    x = pts[:, 0].astype(np.float64)
    y = pts[:, 1].astype(np.float64)

    # ── point data ──
    out: dict[str, np.ndarray] = {"x": x, "y": y}

    for da in piece.findall("PointData/DataArray"):
        name = da.attrib["Name"]
        n_comp = int(da.attrib.get("NumberOfComponents", "1"))
        arr = _decode_vtp_binary_array(da.text, np.float32).astype(np.float64)
        if n_comp == 3:
            arr = arr.reshape(-1, 3)
            out[f"{name}x"] = arr[:, 0]
            out[f"{name}y"] = arr[:, 1]
            out[f"{name}z"] = arr[:, 2]
        else:
            out[name] = arr

    return out


def load_all_snapshots(vtp_root: Path) -> tuple[list[float], dict[str, np.ndarray]]:
    """Load all timestep subdirs sorted by time.

    Returns (times, fields) where fields[key] has shape (N_points, N_times).
    """
    dirs = sorted(
        [d for d in vtp_root.iterdir() if d.is_dir()],
        key=lambda d: float(d.name),
    )
    times: list[float] = []
    columns: dict[str, list[np.ndarray]] = {}
    coords: dict[str, np.ndarray] | None = None

    for d in dirs:
        vtp = d / "midspan.vtp"
        if not vtp.exists():
            continue
        snap = read_vtp_snapshot(vtp)
        t = float(d.name)
        times.append(t)
        if coords is None:
            coords = {"x": snap["x"], "y": snap["y"]}
        for key in ("Ux", "Uy", "T", "p_rgh"):
            columns.setdefault(key, []).append(snap.get(key, np.zeros_like(snap["x"])))

    fields: dict[str, np.ndarray] = {**coords}
    for key, cols in columns.items():
        fields[key] = np.column_stack(cols)  # shape (N_pts, N_times)

    return times, fields


# ─── POD core ────────────────────────────────────────────────────────────────

def compute_pod(snapshot_matrix: np.ndarray) -> dict:
    """SVD-based POD.  snapshot_matrix shape: (N_space, N_time)."""
    mean = snapshot_matrix.mean(axis=1, keepdims=True)
    X = snapshot_matrix - mean

    # Method of snapshots for N_time << N_space
    # C = X^T X,  eig(C) -> temporal modes -> spatial modes
    C = X.T @ X
    eigvals, V = np.linalg.eigh(C)          # ascending order
    eigvals = eigvals[::-1]                  # descending
    V = V[:, ::-1]

    # Normalise temporal modes
    sigma = np.sqrt(np.maximum(eigvals, 0.0))
    tol = sigma[0] * 1e-10 if sigma[0] > 0 else 1e-14
    active = int(np.sum(sigma > tol))

    # Spatial modes: U_i = X v_i / sigma_i
    spatial = X @ V[:, :active] / sigma[:active]

    energy = eigvals[:active] ** 2 if False else eigvals[:active]   # sigma^2 ∝ energy
    energy_frac = energy / energy.sum() if energy.sum() > 0 else energy
    cum_energy = np.cumsum(energy_frac)

    # Temporal coefficients: a_i(t) = sigma_i * V[:,i]
    temporal = np.diag(sigma[:active]) @ V[:, :active].T   # (n_modes, n_times)

    # Deterministic sign convention
    for i in range(active):
        pivot = int(np.argmax(np.abs(spatial[:, i])))
        if spatial[pivot, i] < 0:
            spatial[:, i] *= -1
            temporal[i, :] *= -1

    return {
        "mean": mean[:, 0],
        "spatial": spatial,
        "singular_values": sigma[:active],
        "energy_fraction": energy_frac,
        "cumulative_energy": cum_energy,
        "temporal": temporal,
        "active": active,
    }


# ─── writers ─────────────────────────────────────────────────────────────────

def _fmt(v: float) -> str:
    return f"{v:.10g}"


def write_singular_values_csv(path: Path, pod: dict, times: list[float]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["mode", "singular_value", "energy_fraction", "cumulative_energy", "active"])
        for i in range(len(pod["singular_values"])):
            active = "yes" if i < pod["active"] else "no"
            w.writerow([i+1, _fmt(pod["singular_values"][i]),
                        _fmt(pod["energy_fraction"][i]),
                        _fmt(pod["cumulative_energy"][i]), active])


def write_temporal_csv(path: Path, pod: dict, times: list[float]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["mode", *[f"t={t}" for t in times]])
        for i in range(pod["active"]):
            w.writerow([i+1, *[_fmt(v) for v in pod["temporal"][i]]])


def write_json_result(path: Path, field_name: str, pod: dict,
                      times: list[float], x: np.ndarray, y: np.ndarray) -> None:
    result = {
        "dataset": f"V4b_3D_run001_midspan_{field_name}",
        "field": field_name,
        "note": (
            "run001 is STEADY (Re=100). Snapshots t=0.5..5s show spin-up "
            "from IC. Mode 1 = steady state. Periodic POD requires Re>Re_crit."
        ),
        "times": times,
        "n_points": int(x.shape[0]),
        "mean_stats": {
            "min": float(pod["mean"].min()),
            "max": float(pod["mean"].max()),
            "mean": float(pod["mean"].mean()),
        },
        "singular_values": [float(v) for v in pod["singular_values"]],
        "energy_fraction": [float(v) for v in pod["energy_fraction"]],
        "cumulative_energy": [float(v) for v in pod["cumulative_energy"]],
        "active_mode_count": pod["active"],
        "spatial_modes": [
            {
                "mode": i+1,
                "energy_pct": float(pod["energy_fraction"][i] * 100),
                "max_abs": float(np.abs(pod["spatial"][:, i]).max()),
            }
            for i in range(pod["active"])
        ],
        "temporal_coefficients": [
            {
                "mode": i+1,
                "coefficients": [float(v) for v in pod["temporal"][i]],
            }
            for i in range(pod["active"])
        ],
    }
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")


def write_spatial_csv(path: Path, x: np.ndarray, y: np.ndarray,
                      pod: dict) -> None:
    """Write all spatial modes as columns alongside x,y coords."""
    n_modes = pod["active"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["x", "y", "mean", *[f"mode_{i+1}" for i in range(n_modes)]])
        for pt in range(x.shape[0]):
            row = [_fmt(x[pt]), _fmt(y[pt]), _fmt(pod["mean"][pt])]
            row += [_fmt(pod["spatial"][pt, i]) for i in range(n_modes)]
            w.writerow(row)


# ─── main ────────────────────────────────────────────────────────────────────

def run_field(field_name: str, times: list[float],
              fields: dict[str, np.ndarray]) -> dict:
    data = fields[field_name]       # shape (N_pts, N_times)
    pod = compute_pod(data)

    out_dir = RESULTS_DIR / field_name
    out_dir.mkdir(parents=True, exist_ok=True)

    write_singular_values_csv(out_dir / "singular_values.csv", pod, times)
    write_temporal_csv(out_dir / "temporal_coefficients.csv", pod, times)
    write_json_result(out_dir / "pod_result.json", field_name, pod,
                      times, fields["x"], fields["y"])
    write_spatial_csv(out_dir / "spatial_modes.csv",
                      fields["x"], fields["y"], pod)

    return pod


def main() -> None:
    print(f"Loading VTP snapshots from:\n  {VTP_ROOT}\n")
    times, fields = load_all_snapshots(VTP_ROOT)
    N_pts, N_t = fields["Ux"].shape
    print(f"  {N_t} snapshots at t={times}")
    print(f"  {N_pts} points per snapshot\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    for field_name in ("Ux", "Uy", "T"):
        print(f"--- POD: {field_name} ---")
        pod = run_field(field_name, times, fields)
        for i in range(pod["active"]):
            print(f"  Mode {i+1}: sv={pod['singular_values'][i]:.4g}  "
                  f"energy={pod['energy_fraction'][i]*100:.2f}%  "
                  f"cum={pod['cumulative_energy'][i]*100:.2f}%")
            summary_rows.append({
                "field": field_name,
                "mode": i+1,
                "singular_value": pod["singular_values"][i],
                "energy_pct": pod["energy_fraction"][i]*100,
                "cumulative_pct": pod["cumulative_energy"][i]*100,
            })
        print()

    # summary CSV
    with (RESULTS_DIR / "pod_of_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["field","mode","singular_value",
                                          "energy_pct","cumulative_pct"])
        w.writeheader()
        for row in summary_rows:
            w.writerow({k: _fmt(v) if isinstance(v, float) else v
                        for k, v in row.items()})

    print(f"Results written to: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
