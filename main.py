"""
Asset Distribution Tools v2.0 by Ophar
Main entry point untuk aplikasi.
"""

import sys
import warnings
from ui.app import run_app

# Suppress warnings
warnings.filterwarnings("ignore")

def main():
    """Main entry point."""
    try:
        run_app()
    except KeyboardInterrupt:
        print("\n[INFO] Aplikasi ditutup oleh user.")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
