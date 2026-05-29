"""
Engine untuk Modul ① Konsolidasi - Merge multi-file Excel.
Optimized dengan parallel reading dan smart caching.
"""

import os
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import gc

from core.base_engine import BaseEngine
from utils import get_file_size_mb, find_column_index
from config.constants import COLUMNS, MAX_WORKERS


class KonsolidasiEngine(BaseEngine):
    """Engine untuk merge multiple Excel files."""
    
    MASTER_SHEET = COLUMNS["UNIT_MASTER"]
    OWNER_ASET_COL = "OWNER_ASET"
    NAME_UP3_COL = COLUMNS["NAME_UP3"][0]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}
        self._lookup = {}
    
    def _read_one_file(self, path: str) -> tuple:
        """
        Read single Excel file with error handling.
        Returns: (path, sheets_dict)
        """
        try:
            size = get_file_size_mb(path)
            self._flog(f"Reading {Path(path).name} ({size:.2f}MB)")
            
            engine = "openpyxl" if path.lower().endswith(".xlsx") else "xlrd"
            sheets = pd.read_excel(path, sheet_name=None, dtype=str, engine=engine)
            return (path, sheets)
        except Exception as e:
            self._flog(f"ERROR reading {Path(path).name}: {str(e)}", "error")
            raise
    
    def _read_parallel(self, paths: List[str]) -> List[tuple]:
        """
        Read multiple files in parallel.
        """
        results = []
        workers = min(MAX_WORKERS, len(paths))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(self._read_one_file, p): p for p in paths}
            
            for idx, future in enumerate(concurrent.futures.as_completed(futures)):
                try:
                    result = future.result()
                    results.append(result)
                    self._update_progress(int((idx + 1) / len(paths) * 55))
                except Exception as e:
                    self._log_ui(f"[SKIP] {Path(futures[future]).name}: {e}", "warning")
        
        return results
    
    def _build_lookup(self, master: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """
        Build VLOOKUP table dari UNIT_MASTER.
        Returns: {OWNER_CODE: NAME_UP3}
        """
        if self.MASTER_SHEET not in master:
            raise ValueError(f"Sheet '{self.MASTER_SHEET}' tidak ada di Master Induk")
        
        um = master[self.MASTER_SHEET]
        
        # Find owner column
        owner_col = None
        for col in COLUMNS["OWNER_ASET"]:
            if col in um.columns:
                owner_col = col
                break
        
        if not owner_col:
            raise ValueError(f"Kolom owner tidak ditemukan di UNIT_MASTER")
        
        if self.NAME_UP3_COL not in um.columns:
            raise ValueError(f"Kolom '{self.NAME_UP3_COL}' tidak ditemukan")
        
        # Build lookup
        valid = um[[owner_col, self.NAME_UP3_COL]].dropna()
        lookup = dict(zip(valid[owner_col], valid[self.NAME_UP3_COL]))
        
        self._flog(f"Lookup built: {len(lookup)} entries")
        return lookup
    
    def _process_sheet(
        self,
        master_df: pd.DataFrame,
        frames: List[pd.DataFrame],
        lookup: Dict[str, str]
    ) -> Optional[pd.DataFrame]:
        """Process dan combine sheet data."""
        if not frames:
            return None
        
        combined = pd.concat(frames, ignore_index=True)
        
        # Add missing columns from master
        mcols = list(master_df.columns)
        for col in set(mcols) - set(combined.columns):
            combined[col] = pd.NA
        
        combined = combined[mcols]
        
        # Apply VLOOKUP
        if self.OWNER_ASET_COL in combined.columns:
            combined["UP3"] = combined[self.OWNER_ASET_COL].map(lookup)
        
        combined.dropna(how="all", inplace=True)
        return combined if not combined.empty else None
    
    def run(
        self,
        master_path: str,
        source_paths: List[str],
        output_path: str,
        output_format: str = "xlsx"
    ) -> Dict[str, Any]:
        """
        Run konsolidasi process.
        
        Returns: {total_files, total_rows, total_sheets, elapsed}
        """
        self._start_timer()
        stats = {
            "total_files": len(source_paths),
            "total_rows": 0,
            "total_sheets": 0,
            "elapsed": 0.0
        }
        
        try:
            self._flog(f"START Konsolidasi | files={len(source_paths)}")
            
            # Load master
            self._log_ui("Membaca UNIT_MASTER...", "info")
            master_sheets = pd.read_excel(master_path, sheet_name=None, dtype=str)
            lookup = self._build_lookup(master_sheets)
            self._update_progress(10)
            
            # Read source files
            self._log_ui("Membaca file sumber...", "info")
            file_data = self._read_parallel(source_paths)
            self._update_progress(60)
            
            # Process per sheet
            self._log_ui("Menggabungkan data...", "info")
            all_frames = {}  # sheet_name -> list of dfs
            
            for path, sheets in file_data:
                for sname, df in sheets.items():
                    if df.empty:
                        continue
                    all_frames.setdefault(sname, []).append(df)
            
            # Combine and process
            master_df = master_sheets.get(self.MASTER_SHEET, pd.DataFrame())
            if master_df.empty:
                raise ValueError(f"Sheet '{self.MASTER_SHEET}' kosong atau tidak ada")
            
            output_dfs = {}
            for sname, frames in all_frames.items():
                processed = self._process_sheet(master_df, frames, lookup)
                if processed is not None and not processed.empty:
                    output_dfs[sname] = processed
                    stats["total_rows"] += len(processed)
                    stats["total_sheets"] += 1
            
            if not output_dfs:
                raise ValueError("Tidak ada data yang berhasil diproses")
            
            # Write output
            self._log_ui(f"Menulis {len(output_dfs)} sheet ke {output_path}", "info")
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            if output_format == "csv":
                combined = pd.concat(output_dfs.values(), ignore_index=True)
                combined.to_csv(output_path, index=False)
            else:
                with pd.ExcelWriter(output_path, engine="openpyxl") as w:
                    for sname, df in output_dfs.items():
                        df.to_excel(w, sheet_name=sname[:31], index=False)
            
            stats["elapsed"] = self._get_elapsed()
            self._flog(f"DONE Konsolidasi: rows={stats['total_rows']} elapsed={stats['elapsed']}s")
            self._update_progress(100)
            self._cleanup_memory()
            
            return stats
        
        except Exception as e:
            self._flog(f"CRITICAL ERROR: {str(e)}", "error")
            raise