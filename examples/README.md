# Travel Readiness Sentinel - Example Files

This directory contains example files demonstrating different scenarios for the Travel Readiness Sentinel system.

## 📁 Directory Structure

```
examples/
├── excel/          # Excel format examples
│   ├── itinerary_template.xlsx    # ✅ Perfect example (use this as starting point)
│   ├── itinerary_wrong.xlsx       # ❌ Business logic errors 
│   └── itinerary_invalid.xlsx     # ❌ Data validation errors
└── yaml/           # YAML format examples  
    ├── itinerary.yaml              # ✅ Perfect example
    ├── itinerary_wrong.yaml        # ❌ Business logic errors
    └── itinerary_invalid.yaml      # ❌ Data validation errors
```

## 📊 Excel Examples

### ✅ `itinerary_template.xlsx` - Perfect Template
- **Use this as your starting point!**
- Contains valid Tokyo trip data
- All validation checks pass
- Clear format guidance in notes column

**Run with:**
```bash
python main.py --itinerary examples/excel/itinerary_template.xlsx
```

**Expected output:**
```
🎉 TRSS Status: READY FOR DEPARTURE
```

### ❌ `itinerary_wrong.xlsx` - Business Logic Errors
- Valid data format but poor planning
- Demonstrates alignment and coverage issues:
  - Flight arrives **after** hotel check-in
  - Flight departs **before** trip ends  
  - Hotel doesn't cover full trip duration

**Run with:**
```bash
python main.py --itinerary examples/excel/itinerary_wrong.xlsx
```

**Expected output:**
```
❌ [FAIL] Arrival Date Alignment: Flight lands on 2025-05-11, but Hotel check-in is 2025-05-10
❌ [FAIL] Full Accommodation Coverage: Gap Detected! Trip is 7 nights, but hotel is only 5 nights.
❌ [FAIL] Exit Strategy Alignment: Visa Risk! Trip ends on 2025-05-17 but flight is 2025-05-16
🚨 TRSS Status: GROUNDED (3 Critical Errors Found)
```

### ❌ `itinerary_invalid.xlsx` - Data Validation Errors  
- Missing required fields and invalid values
- Demonstrates data integrity issues:
  - Missing total duration field
  - Flight number too short
  - Missing departure date

**Run with:**
```bash
python main.py --itinerary examples/excel/itinerary_invalid.xlsx
```

**Expected output:**
```
Error processing file: Missing required trip detail: total_duration_days
```

## 📄 YAML Examples

The YAML examples contain the same scenarios as Excel but in YAML format for users comfortable with structured text files.

## 🚀 Quick Start

1. **Copy the template**: `examples/excel/itinerary_template.xlsx`
2. **Edit the "Value" column** with your trip details
3. **Run validation**: `python main.py --itinerary your_itinerary.xlsx`
4. **Fix any issues** until you see `🎉 READY FOR DEPARTURE`

## 🎯 Learning Path

1. Start with `itinerary_template.xlsx` ✅
2. Try `itinerary_wrong.xlsx` to see business logic errors ❌  
3. Try `itinerary_invalid.xlsx` to see data validation errors ❌
4. Create your own itinerary using the template!