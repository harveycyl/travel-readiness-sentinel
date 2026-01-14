import yaml
import argparse
import sys
from pathlib import Path
from pydantic import ValidationError
from .core.model import Itinerary
from .core.validation import get_all_checks
from .ingestion.excel import ExcelIngestion
from .ingestion.yaml import YAMLIngestion

def load_itinerary(path: str) -> Itinerary:
    """Load itinerary from either Excel (.xlsx) or YAML (.yaml/.yml) file"""
    try:
        file_path = Path(path)
        
        if not file_path.exists():
            print(f"Error: File {path} not found.")
            sys.exit(1)
        
        # Determine file type and load accordingly
        if file_path.suffix.lower() == '.xlsx':
            print(f"📊 Reading Excel file: {path}")
            reader = ExcelIngestion()
            raw_data = reader.parse(path)
            print("✅ Excel file successfully parsed")
        elif file_path.suffix.lower() in ['.yaml', '.yml']:
            print(f"📄 Reading YAML file: {path}")
            reader = YAMLIngestion()
            raw_data = reader.parse(path)
        else:
            print(f"Error: Unsupported file type. Please use .xlsx, .yaml, or .yml files.")
            sys.exit(1)
        
        return Itinerary(**raw_data)
        
    except FileNotFoundError:
        print(f"Error: File {path} not found.")
        sys.exit(1)
    except ValidationError as e:
        print(f"Data Integrity Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Travel Readiness Sentinel")
    parser.add_argument('--itinerary', required=True, 
                       help="Path to trip file (Excel .xlsx or YAML .yaml/.yml)")
    parser.add_argument('--output', 
                       help="Output YAML file (only when input is Excel)")
    args = parser.parse_args()

    print("🔍 Ingesting Itinerary Data...")
    itinerary = load_itinerary(args.itinerary)
    
    print(f"✈️  Validating Trip to {itinerary.trip_details.destination}...")
    print("-" * 50)

    checks = get_all_checks()
    failures = 0

    for check in checks:
        result = check.run(itinerary)
        if result.passed:
            print(f"✅ [PASS] {result.check_name}")
        else:
            print(f"❌ [FAIL] {result.check_name}: {result.message}")
            failures += 1

    print("-" * 50)
    if failures == 0:
        print("🎉 TRSS Status: READY FOR DEPARTURE")
    else:
        print(f"🚨 TRSS Status: GROUNDED ({failures} Critical Errors Found)")
        sys.exit(1)

if __name__ == "__main__":
    main()