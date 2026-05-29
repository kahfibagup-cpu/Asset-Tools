"""
Engine untuk Modul ② Split - Split per UP3 berdasarkan UNIT_MASTER.
Optimized dengan smart mapping dan memory management.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import pandas as pd
import gc

from core.base_engine import BaseEngine
from utils import clean_filename, find_column_index
from config.constants import COLUMNS


class SplitEngine(BaseEngine):
    """Engine untuk split file berdasarkan UP3 mapping."""
    
    OWNER_COLS = COLUMNS["OWNER_ASET"]
    UP3_COL = COLUMNS["NAME_UP3"][0]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._map = {}
    
    def load_master(self, master_path: str) -> None:
        """
        Load UNIT_MASTER dan build mapping.
        
        Args:
            master_path: Path ke file UNIT_MASTER
        
        Raises:
            ValueError: Jika kolom tidak ditemukan
        """
        self._log_ui("Membaca UNIT_MASTER...", "info")
        
        try:
            engine = "openpyxl" if master_path.endswith(".xlsx") else "xlrd"
            df = pd.read_excel(
                master_path,
                sheet_name=0,
                dtype=str,
                engine=engine
            )
            
            # Find owner column
            owner_col = None
            for col in self.OWNER_COLS:
                if col in df.columns:
                    owner_col = col
                    break
            
            if not owner_col:
                raise ValueError(f"Kolom owner tidak ditemukan ({self.OWNER_COLS})")
            
            if self.UP3_COL not in df.columns:
                raise ValueError(f"Kolom '{self.UP3_COL}' tidak ditemukan")
            
            # Build mapping
            valid = df[[owner_col, self.UP3_COL]].dropna()
            self._map = dict(zip(
                valid[owner_col].str.strip(),
                valid[self.UP3_COL].str.strip()
            ))
            
            self._flog(f"Master loaded: {len(self._map)} mappings from '{owner_col}'")
            self._log_ui(f"  ✓ {len(self._map):,} mapping", "success")
            self._cleanup_memory()
            
        except Exception as e:
            self._flog(f"ERROR loading master: {str(e)}", "error")
            raise
    
    def run(
        self,
        data_path: str,
        output_dir: str,
        selected_sheets: List[str],
        output_format: str = "xlsx"
    ) -> Dict[str, Any]:
        """
        Run split process.
        
        Returns: {total_files, total_rows, total_sheets, unmapped_count, elapsed}
        """
        self._start_timer()
        stats = {
            "total_files": 0,
            "total_rows": 0,
            "total_sheets": 0,
            "unmapped_count": 0,
            "elapsed": 0.0
        }
        
        try:
            self._flog(f"START Split | data={data_path} | sheets={selected_sheets}")
            
            # Read data
            self._log_ui("Membaca file data...", "info")
            all_sheets = pd.read_excel(data_path, sheet_name=None, dtype=str)
            sheets_to_process = {
                k: v for k, v in all_sheets.items()
                if not selected_sheets or k in selected_sheets
            }
            self._log_ui(f"  {len(sheets_to_process)} sheet diproses", "dim")
            self._update_progress(15)
            
            # Group by UP3
            groups: Dict = defaultdict(lambda: defaultdict(list))
            unmapped = set()
            
            for i, (sname, df) in enumerate(sheets_to_process.items()):
                if df.empty:
                    continue
                
                owner_col = None
                for col in self.OWNER_COLS:
                    if col in df.columns:
                        owner_col = col
                        break
                
                if not owner_col:
                    self._log_ui(
                        f"  [SKIP] '{sname}': no owner column",
                        "warning"
                    )
                    continue
                
                df = df.copy()
                df["__UP3__"] = df[owner_col].map(self._map)
                
                unm = df[df["__UP3__"].isna()]
                if not unm.empty:
                    unmapped.update(unm[owner_col].unique())
                    df.loc[df["__UP3__"].isna(), "__UP3__"] = "UNMAPPED"
                
                for up3, grp in df.groupby("__UP3__", observed=True):
                    groups[up3][sname].append(grp.drop(columns=["__UP3__"]))
                
                del df, unm
                self._cleanup_memory()
                self._update_progress(15 + int((i + 1) / len(sheets_to_process) * 55))
            
            if not groups:
                raise ValueError("Tidak ada data yang berhasil dimapping")
            
            stats["unmapped_count"] = len(unmapped)
            self._log_ui(
                f"  {len(groups)} grup UP3, {len(unmapped)} unmapped owners",
                "dim"
            )
            self._flog(f"Groups: {len(groups)}, unmapped: {len(unmapped)}")
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            self._update_progress(70)
            
            # Write output
            for fi, (up3, sdict) in enumerate(groups.items()):
                fname = f"{clean_filename(up3)}.{output_format}"
                fpath = Path(output_dir) / fname
                
                try:
                    rows = 0
                    if output_format == "csv":
                        combined_all = []
                        for sname, dfs in sdict.items():
                            combined_all.append(
                                pd.concat(dfs, ignore_index=True)
                            )
                        pd.concat(combined_all, ignore_index=True).to_csv(
                            fpath,
                            index=False
                        )
                        rows = sum(len(d) for d in combined_all)
                    else:
                        with pd.ExcelWriter(fpath, engine="openpyxl") as w:
                            for sname, dfs in sdict.items():
                                cdf = pd.concat(dfs, ignore_index=True)
                                cdf.to_excel(
                                    w,
                                    sheet_name=sname[:31],
                                    index=False
                                )
                                rows += len(cdf)
                                del cdf
                                self._cleanup_memory()
                    
                    stats["total_files"] += 1
                    stats["total_rows"] += rows
                    stats["total_sheets"] += len(sdict)
                    self._log_ui(
                        f"  ✓ {fname}: {len(sdict)} sheet, {rows:,} baris",
                        "success"
                    )
                    self._flog(f"  Saved: {fname} rows={rows}")
                
                except Exception as e:
                    self._log_ui(f"  ✗ {fname}: {e}", "error")
                    self._flog(f"  ERROR {fname}: {e}", "error")
                
                self._update_progress(70 + int((fi + 1) / len(groups) * 25))
            
            stats["elapsed"] = self._get_elapsed()
            self._flog(
                f"DONE Split: files={stats['total_files']} "
                f"rows={stats['total_rows']} elapsed={stats['elapsed']}s"
            )
            self._update_progress(100)
            self._cleanup_memory()
            
            return stats
        
        except Exception as e:
            self._flog(f"CRITICAL ERROR: {str(e)}", "error")
            raise