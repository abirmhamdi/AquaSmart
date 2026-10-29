"""
Approach 4/4 -- Federated Learning + SMPC (secure aggregation).

Adds a simplified SMPC layer on top of FedAvg via PAIRWISE ADDITIVE MASKING
(a lightweight form of additive secret sharing, matching the subject's
"secret sharing simplifie ou masquage additif" requirement, section 4.5):

For every pair of clients (i, j) in a round, both sides derive the same
random mask vector m_ij (in the real world via a Diffie-Hellman-style key
agreement; here simulated with a deterministic seed shared out-of-band).
  - client i adds   +m_ij   to its weighted contribution (n_i/N) * w_i
  - client j adds   -m_ij   to its weighted contribution (n_j/N) * w_j
So each individual message the server receives is dominated by random
masks (std 10 vs. a true contribution of ~0.07), YET the masks cancel out
(to floating-point precision) once every client's message is summed -- the
server recovers the correct global model without ever seeing an individual
client's real update. This is the concrete mechanism behind the subject's
requirement: "montrer que le serveur d'agregation peut obtenir le modele
global sans acceder directement aux mises a jour individuelles."

Reuses fl_smpc/experiments/federated.py::run() end-to-end and only replaces
the aggregation step, so FL and FL+SMPC are trained identically otherwise --
any metric difference between them is due to masking overhead alone, not to
a different training procedure.
"""
from __future__ import annotations

import time
import numpy as np

from fl_smpc.experiments import federated
from fl_smpc.common import N_FEATURES, PARAM_BYTES

SEED_BYTES = 16  # bytes exchanged per pairwise key-agreement handshake
# Mask scale. A client's real (weighted) contribution is ~0.05-0.1 in magnitude,
# so masks with std 10 dominate each message by ~2 orders of magnitude: the server
# cannot read an individual update from what it receives. They still cancel in the
# sum (each +r_ij is matched by a -r_ij), up to floating-point rounding (~1e-14).
MASK_STD = 10.0


def run(clients: dict, n_rounds: int = 15, test_frac: float = 0.2, seed: int = 42) -> dict:
    names = list(clients.keys())
    n = len(names)
    handshake_messages_per_round = n * (n - 1) // 2
    extra_handshake_bytes = handshake_messages_per_round * SEED_BYTES
    extra_mask_time = 0.0

    round_counter = [0]
    distortions, agg_errors = [], []

    def masked_aggregator(updates):
        nonlocal extra_mask_time
        t0 = time.time()
        round_counter[0] += 1
        # Deterministic per-round seed (stands in for the pairwise key agreement)
        rng = np.random.default_rng(seed * 1_000_003 + round_counter[0])
        total_n = sum(u[1] for u in updates)
        ids = [u[2] for u in updates]

        true_contrib = {u[2]: (u[1] / total_n) * u[0] for u in updates}   # never leaves the client
        messages = {k: v.copy() for k, v in true_contrib.items()}          # what the server receives

        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                mask = rng.normal(0, MASK_STD, size=N_FEATURES + 1)        # shared by clients a and b
                messages[ids[a]] += mask
                messages[ids[b]] -= mask

        # --- server side: only the masked messages are summed ---
        masked_global = sum(messages.values())

        # evidence for the report (simulation-time checks, not available to a real server)
        distortions.append(float(np.mean([
            np.linalg.norm(messages[k] - true_contrib[k]) / (np.linalg.norm(true_contrib[k]) + 1e-12)
            for k in ids])))
        agg_errors.append(float(np.max(np.abs(masked_global - sum(true_contrib.values())))))

        extra_mask_time += time.time() - t0
        return masked_global

    result = federated.run(clients, n_rounds=n_rounds, test_frac=test_frac, seed=seed,
                            aggregator=masked_aggregator)

    result["approach"] = "Federated Learning + SMPC"
    result["confidentiality"] = "High"
    result["confidentiality_note"] = (
        "Server only ever sees pairwise-masked updates that are individually "
        "indistinguishable from noise; masks cancel exactly in the weighted "
        "sum so the global model is unaffected."
    )
    result["time_sec"] += extra_mask_time
    result["smpc_overhead_sec"] = extra_mask_time
    # how much each individual message differs from the real update it hides (relative L2),
    # and how far the securely-summed global model is from the plain FedAvg one
    result["smpc_mean_message_distortion"] = float(np.mean(distortions))
    result["smpc_max_aggregate_error"] = float(np.max(agg_errors))
    result["n_messages"] += n_rounds * handshake_messages_per_round
    result["comm_bytes"] += n_rounds * extra_handshake_bytes
    result["smpc_handshake_messages"] = n_rounds * handshake_messages_per_round
    result["smpc_handshake_bytes"] = n_rounds * extra_handshake_bytes
    return result
