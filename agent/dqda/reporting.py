from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from agent.utils.config import Config
from agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class DQDAReportExporter:
    """Export DQDA scoring dashboard to JSON/CSV/Excel."""

    def __init__(self, output_dir: Optional[Path] = None, config: Optional[Config] = None):
        self.config = config or Config()
        self.config.validate()
        self.output_dir = output_dir or self.config.OUTPUT_DIR
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def export(
        self,
        report: Dict[str, Any],
        *,
        format: str = 'json',
        filename: Optional[str] = None,
    ) -> str:
        fmt = format.lower()
        if not filename:
            startup_name = str(report.get('startup_name', 'startup')).strip().replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"dqda_{startup_name}_{timestamp}"

        if fmt in {'xlsx', 'excel'}:
            output_path = Path(self.output_dir) / f"{filename}.xlsx"
        else:
            output_path = Path(self.output_dir) / f"{filename}.{fmt}"

        if fmt == 'json':
            self._export_json(report, output_path)
        elif fmt == 'csv':
            self._export_csv(report, output_path)
        elif fmt in {'xlsx', 'excel'}:
            self._export_excel(report, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return str(output_path)

    def _dashboard_row(self, report: Dict[str, Any]) -> Dict[str, Any]:
        def dump(value: Any) -> str:
            return json.dumps(value, ensure_ascii=False, sort_keys=True)

        return {
            'startup_name': report.get('startup_name'),
            'collection_timestamp': report.get('collection_timestamp'),
            'founder_score': report.get('founder_score'),
            'market_analysis': dump(report.get('market_analysis', {})),
            'competition': dump(report.get('competition', {})),
            'token_utility': dump(report.get('token_utility', {})),
            'weaknesses': dump(report.get('weaknesses', [])),
            'investor_fit': dump(report.get('investor_fit', {})),
        }

    def _export_json(self, report: Dict[str, Any], path: Path) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def _export_csv(self, report: Dict[str, Any], path: Path) -> None:
        df = pd.DataFrame([self._dashboard_row(report)])
        df.to_csv(path, index=False, encoding='utf-8')

    def _export_excel(self, report: Dict[str, Any], path: Path) -> None:
        dashboard_df = pd.DataFrame([self._dashboard_row(report)])

        # Optional detailed rows for data points
        datapoint_rows = []
        for group, points in (report.get('data_points') or {}).items():
            for p in points:
                datapoint_rows.append(
                    {
                        'collector_group': group,
                        'source_type': p.get('source_type'),
                        'source_url': p.get('source_url'),
                        'confidence_score': p.get('confidence_score'),
                        'collection_timestamp': p.get('collection_timestamp'),
                        'structured_data': json.dumps(p.get('structured_data', {}), ensure_ascii=False),
                        'errors': json.dumps(p.get('errors', []), ensure_ascii=False),
                    }
                )

        datapoints_df = pd.DataFrame(datapoint_rows)

        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            dashboard_df.to_excel(writer, sheet_name='Dashboard', index=False)
            if not datapoints_df.empty:
                datapoints_df.to_excel(writer, sheet_name='DataPoints', index=False)

            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            max_length = max(max_length, len(str(cell.value)) if cell.value is not None else 0)
                        except Exception:
                            pass
                    worksheet.column_dimensions[column_letter].width = min(max_length + 2, 60)
