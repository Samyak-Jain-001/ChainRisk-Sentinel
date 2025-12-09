from app.risk import score_transaction


def test_large_transfer_high_risk():
    score, label, reasons = score_transaction(
        value_eth=10.0,
        from_address="0x123",
        to_address="0x456",
        outgoing_tx_count_window=10,
    )
    assert score >= 70
    assert label == "HIGH"
    assert "large_transfer" in reasons


def test_small_transfer_low_risk():
    score, label, reasons = score_transaction(
        value_eth=0.01,
        from_address="0x123",
        to_address="0x456",
        outgoing_tx_count_window=0,
    )
    assert label == "LOW"
