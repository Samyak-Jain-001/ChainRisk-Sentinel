from typing import Tuple

# Simple, explainable rule-based risk engine.

LARGE_TX_THRESHOLD_ETH = 1.0
BURST_TX_THRESHOLD_COUNT = 5  # number of recent outgoing tx
RISKY_ADDRESSES = {
    # put any known "risky" addresses for demo, lowercase
    "0x000000000000000000000000000000000000dead",
}


def score_transaction(
    *,
    value_eth: float,
    from_address: str,
    to_address: str | None,
    outgoing_tx_count_window: int,
) -> Tuple[int, str, str]:
    """
    Returns (risk_score, risk_label, reasons)
    """
    from_addr = from_address.lower()
    to_addr = (to_address or "").lower()

    score = 0
    reasons: list[str] = []

    # Rule 1: large transfer
    if value_eth >= LARGE_TX_THRESHOLD_ETH:
        score += 40
        reasons.append(f"large_transfer_>=_{LARGE_TX_THRESHOLD_ETH}_ETH")

    # Rule 2: interacts with known risky addresses
    if from_addr in RISKY_ADDRESSES or to_addr in RISKY_ADDRESSES:
        score += 50
        reasons.append("interacts_with_risky_address")

    # Rule 3: burst of outgoing tx in recent window
    if outgoing_tx_count_window >= BURST_TX_THRESHOLD_COUNT:
        score += 30
        reasons.append(
            f"burst_of_outgoing_txs_>=_{BURST_TX_THRESHOLD_COUNT}_in_recent_window"
        )

    # Map score to label
    if score >= 70:
        label = "HIGH"
    elif score >= 30:
        label = "MEDIUM"
    else:
        label = "LOW"

    reasons_str = "; ".join(reasons) if reasons else "none"
    return score, label, reasons_str
