import pytest

from intelligence.protected_assets import ProtectedAssetSigner, watermark_label


def test_asset_grant_is_bound_expires_and_watermarks_without_raw_account_id():
    signer = ProtectedAssetSigner(b"x" * 32)
    token = signer.issue(asset_id="report-7", account_id="acct-private", tier="premium", now=100, ttl_seconds=60)
    grant = signer.verify(token, expected_account_id="acct-private", now=159)
    assert grant.asset_id == "report-7"
    assert "acct-private" not in watermark_label(grant, rendered_at=120)
    with pytest.raises(ValueError):
        signer.verify(token, expected_account_id="other", now=159)
    with pytest.raises(ValueError):
        signer.verify(token, expected_account_id="acct-private", now=160)


def test_asset_grant_rejects_tampering():
    signer = ProtectedAssetSigner(b"x" * 32)
    token = signer.issue(asset_id="report-7", account_id="acct", tier="premium", now=100)
    with pytest.raises(ValueError):
        signer.verify(token[:-1] + ("A" if token[-1] != "A" else "B"), expected_account_id="acct", now=101)
