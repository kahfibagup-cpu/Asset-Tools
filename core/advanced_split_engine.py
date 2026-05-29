"""
Engine untuk Modul ③ Advanced Split - Split by custom column.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import pandas as pd

from core.base_engine import BaseEngine
from utils import clean_filename


class AdvancedSplitEngine(BaseEngine):
    """Engine untuk split file berdasarkan custom column."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_columns(self, data_path: str, sheet: str) -> List[str]:
        """Get column list dari sheet."""
        try:
            df = pd.read_excel(
                data_path,
                sheet_name=sheet,
                nrows=0,
                dtype=str
            )
            return list(df.columns)
        except Exception as e:
            self._flog(f"ERROR getting columns: {str(e)}", "error")
            return []
    
    def run(
        self,
        data_path: str,
        output_dir: str,
        split_col: str,
        selected_sheets: List[str],
        output_format: str = "xlsx"
    ) -> Dict[str, Any]:
        """
        Run advanced split.
        
        Returns: {total_files, total_rows, total_sheets, elapsed}
        """
        self._start_timer()
        stats = {
            "total_files": 0,
            "total_rows": 0,
            "total_sheets": 0,
            "elapsed": 0.0
        }
        
        try:
            self._flog(f"START AdvSplit | col={split_col} | sheets={selected_sheets}")
            
            # Read data
            self._log_ui("Membaca file data...", "info")
            all_sheets = pd.read_excel(data_path, sheet_name=None, dtype=str)
            to_process = {
                k: v for k, v in all_sheets.items()
                if not selected_sheets or k in selected_sheets
            }
            self._log_ui(
                f"  {len(to_process)} sheet, split kolom: '{split_col}'",
                "dim"
            )
            self._update_progress(15)
            
            # Group by column value
            groups: Dict = defaultdict(lambda: defaultdict(list))
            
            for i, (sname, df) in enumerate(to_process.items()):
                if df.empty:
                    continue
                
                if split_col not in df.columns:
                    self._log_ui(
                        f"  [SKIP] '{sname}': kolom '{split_col}' tidak ada",
                        "warning"
                    )
                    continue
                
                for val, grp in df.groupby(split_col, dropna=False, observed=True):
                    key = str(val).strip() if pd.notna(val) else "BLANK"
                    groups[key][sname].append(grp)
                
                self._update_progress(15 + int((i + 1) / len(to_process) * 55))
            
            if not groups:
                raise ValueError(f"Tidak ada data untuk kolom '{split_col}'")
            
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            self._flog(f"Groups: {len(groups)}")
            self._update_progress(70)
            
            # Write output
            for fi, (val, sdict) in enumerate(groups.items()):
                fname = f"{clean_filename(val)}.{output_format}"
                fpath = Path(output_dir) / fname
                
                try:
                    rows = 0
                    if output_format == "csv":
                        combined = pd.concat(
                            [pd.concat(dfs, ignore_index=True) for dfs in sdict.values()],
                            ignore_index=True
                        )
                        combined.to_csv(fpath, index=False)
                        rows = len(combined)
                    else:
                        with pd.ExcelWriter(fpath, engine="openpyxl") as w:
                            for sname, dfs in sdict.items():
                                cdf = pd.concat(dfs, ignore_index=True)
                                cdf.to_excel(w, sheet_name=sname[:31], index=False)
                                rows += len(cdf)
                    
                    stats["total_files"] += 1
                    stats["total_rows"] += rows
                    stats["total_sheets"] += len(sdict)
                    self._log_ui(f"  ✓ {fname}: {rows:,} baris", "success")
                    self._flog(f"  Saved {fname} rows={rows}")
                
                except Exception as e:
                    self._log_ui(f"  ✗ {fname}: {e}", "error")
                    self._flog(f"  ERROR {fname}: {e}", "error")
                
                self._update_progress(70 + int((fi + 1) / len(groups) * 25))
            
            stats["elapsed"] = self._get_elapsed()
            self._flog(f"DONE AdvSplit: files={stats['total_files']} elapsed={stats['elapsed']}s")
            self._update_progress(100)
            self._cleanup_memory()
            
            return stats
        
        except Exception as e:
            self._flog(f"CRITICAL ERROR: {str(e)}", "error")
            raise