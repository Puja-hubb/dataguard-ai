import runpy
from dataguard import seed


def test_seed_main_resets_database_and_prints_summary(monkeypatch, capsys):
    calls = []

    expected_summary = {
        "revenue": 5500.0,
        "orders": 100,
    }

    def fake_reset_database():
        calls.append("reset")

    def fake_revenue_summary():
        calls.append("summary")
        return expected_summary

    monkeypatch.setattr(seed, "reset_database", fake_reset_database)
    monkeypatch.setattr(seed, "revenue_summary", fake_revenue_summary)

    seed.main()

    captured = capsys.readouterr()

    assert calls == ["reset", "summary"]
    assert "Seeded synthetic raw_orders table." in captured.out
    assert str(expected_summary) in captured.out

def test_main_resets_database_and_prints_revenue(monkeypatch, capsys):
    from dataguard import seed

    calls = []

    monkeypatch.setattr(
        seed,
        "reset_database",
        lambda: calls.append("reset"),
    )
    monkeypatch.setattr(
        seed,
        "revenue_summary",
        lambda: {"revenue": 123.45},
    )

    seed.main()

    captured = capsys.readouterr()

    assert calls == ["reset"]
    assert "Seeded synthetic raw_orders table." in captured.out
    assert "{'revenue': 123.45}" in captured.out


def test_seed_module_runs_as_main(monkeypatch, capsys):
    import runpy
    from dataguard import warehouse

    calls = []

    monkeypatch.setattr(
        warehouse,
        "reset_database",
        lambda: calls.append("reset"),
    )
    monkeypatch.setattr(
        warehouse,
        "revenue_summary",
        lambda: {"revenue": 5500.0},
    )

    runpy.run_module("dataguard.seed", run_name="__main__")

    captured = capsys.readouterr()

    assert calls == ["reset"]
    assert "Seeded synthetic raw_orders table." in captured.out
    assert "{'revenue': 5500.0}" in captured.out
