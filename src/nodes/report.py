# src/nodes/report.py
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class ReportWriter:
    """
    Handles writing audit reports to disk in structured directories:
    - report_onself_generated/
    - report_onpeer_generated/
    - report_bypeer_received/
    """

    def __init__(self, base_dir: str = "audit"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Ensure subdirectories exist
        for sub in ["report_onself_generated", "report_onpeer_generated", "report_bypeer_received"]:
            (self.base_dir / sub).mkdir(exist_ok=True)

    def _get_timestamped_filename(self, prefix: str, extension: str = ".md") -> str:
        now = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        return f"{prefix}_{now}{extension}"

    def write_report(
        self,
        report_json: Dict[str, Any],
        report_md: str,
        report_type: str = "onself",  # onself, onpeer, bypeer
        peer_id: Optional[str] = None
    ) -> Path:
        """
        Writes both JSON and Markdown to disk under the appropriate directory.

        Args:
            report_json: Structured audit report
            report_md: Markdown representation
            report_type: "onself", "onpeer", "bypeer"
            peer_id: Optional peer identifier for filenames

        Returns:
            Path to the Markdown file written
        """
        if report_type == "onself":
            dir_path = self.base_dir / "report_onself_generated"
        elif report_type == "onpeer":
            dir_path = self.base_dir / "report_onpeer_generated"
        elif report_type == "bypeer":
            dir_path = self.base_dir / "report_bypeer_received"
        else:
            raise ValueError(f"Unknown report_type: {report_type}")

        dir_path.mkdir(parents=True, exist_ok=True)

        prefix = f"audit_{peer_id}" if peer_id else "audit"
        md_filename = self._get_timestamped_filename(prefix, extension=".md")
        json_filename = self._get_timestamped_filename(prefix, extension=".json")

        md_path = dir_path / md_filename
        json_path = dir_path / json_filename

        # Write Markdown
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report_md)

        # Write JSON
        import json
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_json, f, indent=2)

        return md_path
