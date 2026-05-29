# Asset Distribution Tools v2.0

**by Ophar** - Aplikasi desktop untuk manajemen dan distribusi aset dengan multiple operasi Excel.

## 🎯 Fitur Utama

### ① Konsolidasi Multi-File
- Merge beberapa file Excel menjadi satu output
- VLOOKUP otomatis dari UNIT_MASTER
- Support format XLSX & CSV

### ② Split per UP3
- Split data berdasarkan mapping UNIT_MASTER
- Owner → UP3 mapping otomatis
- Deteksi unmapped owners

### ③ Advanced Split
- Split berdasarkan kolom custom
- Support UP3, ULP, SUBCLASS, dll
- Dynamic column detection

### ④ Rekap UP3
- Generate summary report per owner
- Configurable filtering (Mode 1 & 2)
- Detailed logging untuk SUBCLASS tidak ditemukan

## 📋 Requirements

- Python 3.8+
- pandas >= 1.3.0
- openpyxl >= 3.7.0
- xlrd >= 2.0.0

## 🚀 Installation

```bash
# Clone or extract repository
cd asset_tools

# Install dependencies
pip install -r requirements.txt

# Run aplikasi
python main.py