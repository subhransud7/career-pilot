from app.core.logger import DailyLogger


def test_daily_log_folder_and_append(tmp_path):
    logger = DailyLogger(root=str(tmp_path / "logs"))
    logger.run("line1")
    logger.run("line2")

    folders = list((tmp_path / "logs").glob("logs-*"))
    assert len(folders) == 1
    run_log = folders[0] / "run.log"
    assert run_log.exists()
    text = run_log.read_text(encoding="utf-8")
    assert "line1" in text
    assert "line2" in text
