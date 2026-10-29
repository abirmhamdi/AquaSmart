"""
Runs all four approaches required by the subject (section 5/7/8) and saves
a comparison table + full FL/FL+SMPC round-by-round history to
fl_smpc/results/comparison_results.json, which the Streamlit dashboard
(dashboard/app.py) reads.

Usage:
    python -m fl_smpc.run_experiments
    python -m fl_smpc.run_experiments --sample-cap 5000 --rounds 20
"""
from __future__ import annotations

import argparse
import json
import os
import time

from fl_smpc.data import load_all_clients
from fl_smpc.experiments import centralized, local, federated, smpc

RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "comparison_results.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-cap", type=int, default=5000, help="max rows kept per pond/client")
    ap.add_argument("--rounds", type=int, default=15, help="FL / FL+SMPC communication rounds")
    ap.add_argument("--test-frac", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    print(f"Loading & labelling the {11}-pond real dataset (cap={args.sample_cap} rows/pond)...")
    t0 = time.time()
    clients = load_all_clients(sample_cap=args.sample_cap)
    print(f"  {len(clients)} clients, {sum(len(d) for d in clients.values())} total rows "
          f"({time.time()-t0:.1f}s)\n")

    results = {}
    print("[1/4] Centralized ML ...")
    results["centralized"] = centralized.run(clients, test_frac=args.test_frac, seed=args.seed)

    print("[2/4] Local ML ...")
    results["local"] = local.run(clients, test_frac=args.test_frac, seed=args.seed)

    print("[3/4] Federated Learning (FedAvg) ...")
    results["federated"] = federated.run(clients, n_rounds=args.rounds, test_frac=args.test_frac, seed=args.seed)

    print("[4/4] Federated Learning + SMPC ...")
    results["smpc"] = smpc.run(clients, n_rounds=args.rounds, test_frac=args.test_frac, seed=args.seed)

    results["_meta"] = {
        "n_clients": len(clients),
        "client_sizes": {k: len(v) for k, v in clients.items()},
        "sample_cap": args.sample_cap,
        "rounds": args.rounds,
        "test_frac": args.test_frac,
    }

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 78)
    print(f"{'Approach':<28}{'MAE':>8}{'RMSE':>8}{'R2':>8}{'Time(s)':>10}{'Msgs':>8}{'KB':>10}  Confidentiality")
    print("=" * 78)
    for key in ("centralized", "local", "federated", "smpc"):
        r = results[key]
        m = r["metrics"]
        print(f"{r['approach']:<28}{m['mae']:>8.3f}{m['rmse']:>8.3f}{m['r2']:>8.3f}"
              f"{r['time_sec']:>10.3f}{r['n_messages']:>8}{r['comm_bytes']/1024:>10.1f}  {r['confidentiality']}")
    print("=" * 78)
    print(f"\nSaved -> {RESULTS_PATH}")


if __name__ == "__main__":
    main()
