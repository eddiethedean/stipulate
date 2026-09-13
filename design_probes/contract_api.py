"""Import guard for a static API declaration probe; no validator exists here."""

raise RuntimeError(
    "contract_api.pyi is a typing probe, not an implemented Stipulate validator."
)
