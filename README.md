# 🧳 Travel Readiness Sentinel (TRS)

**An automated "Pre-Flight" validation engine ensuring complete itinerary coverage before departure.**

> **Note to Hiring Managers:** This repository is a semantic re-skin of a production **Data Readiness System** I architected at my company.
>
> I have mapped the domain concepts to **Travel Logic** to demonstrate how I solve data integrity problems:
> * **Audit Period Completeness** $\rightarrow$ **Hotel Duration Coverage**
> * **Cut-off Testing (Dates)** $\rightarrow$ **Flight/Hotel Alignment**
> * **Evidence Validation** $\rightarrow$ **Ticket Validity Checks**
>
> The underlying architecture uses **Pydantic** for strict data modeling and the **Strategy Pattern** for modular validation rules.

## 🎯 The Problem
Planning a complex trip involves multiple disjointed data sources (Air tickets, Hotel bookings, Calendar blocks). A single misalignment—like a hotel booking ending one day before your flight—can ruin a trip (or an audit).

## 🏗 System Architecture
The system follows a **Validation Pipeline** pattern:

1.  **Ingestion:** Loads raw itinerary data from `itinerary.yaml`.
2.  **Modeling:** Enforces strict types using `src/models.py` (Pydantic).
3.  **Validation:** Runs a suite of "Readiness Checks" defined in `src/validators.py`.
4.  **Reporting:** Outputs a Pass/Fail report with actionable error messages.

## 🚀 Key Logic Implemented
1.  **Arrival Alignment:** Ensures you don't land in Tokyo on the 10th but book the hotel for the 11th.
2.  **Gap Analysis:** Verifies the hotel booking covers *every single night* of the trip duration.
3.  **Exit Strategy:** Confirms the return flight aligns exactly with the trip end date.

## 🛠 How to Run
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the Sentinel with YAML
python main.py --itinerary examples/yaml/itinerary.yaml

# 3. Run with Excel (easier for non-technical users!)
python main.py --itinerary examples/excel/itinerary_template.xlsx
```

## 📁 Examples Directory
All example files are organized in the `examples/` directory:
- `examples/excel/` - Excel format examples (.xlsx)
- `examples/yaml/` - YAML format examples (.yaml)

See [examples/README.md](examples/README.md) for detailed documentation.

## 📈 Excel Support
For users who prefer Excel over YAML:

1. **Use the template**: `examples/excel/itinerary_template.xlsx` 
2. **Fill in your details** in the "Value" column
3. **Run validation** directly on the Excel file

The system automatically detects file type and converts Excel to the internal format.

## 🧪 Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## 📁 Example Files
- **`itinerary_template.xlsx`** - 📊 **Excel template** for easy data entry 
- **`itinerary.yaml`** - Perfect trip example (Tokyo, all validations pass)
- **`itinerary_wrong.yaml`** - Business logic errors (misaligned dates, gaps)  
- **`itinerary_invalid.yaml`** - Data validation errors (missing fields, invalid values)

## 🚨 Error Examples

### Business Logic Errors
```bash
python main.py --itinerary examples/excel/itinerary_wrong.xlsx
# or
python main.py --itinerary examples/yaml/itinerary_wrong.yaml
```
Output:
```
❌ [FAIL] Arrival Date Alignment: Flight lands on 2025-05-11, but Hotel check-in is 2025-05-10
❌ [FAIL] Full Accommodation Coverage: Gap Detected! Trip is 7 nights, but hotel is only 5 nights.
❌ [FAIL] Exit Strategy Alignment: Visa Risk! Trip ends on 2025-05-17 but flight is 2025-05-16
🚨 TRSS Status: GROUNDED (3 Critical Errors Found)
```

### Data Validation Errors  
```bash
python main.py --itinerary examples/excel/itinerary_invalid.xlsx
# or  
python main.py --itinerary examples/yaml/itinerary_invalid.yaml
```
Output:
```
Data Integrity Error: 3 validation errors for Itinerary
trip_details.total_duration_days
  Field required
flights.0.flight_number
  Value error, Invalid Flight Number  
flights.1
  Value error, Departure flights must have departure_date
```
