# 🧳 Travel Readiness Sentinel (TRS)

**An automated "Pre-Flight" validation engine ensuring complete itinerary coverage before departure.**

## 🎉 What's New in v1.0.0

**Phase 1 Complete: FastAPI REST API Implementation**

The Travel Readiness Sentinel now offers **two ways to validate** your itineraries:

- ✅ **CLI Interface** - Original command-line tool (fully maintained)
- 🆕 **REST API** - New FastAPI microservice for web/mobile integration
  - 4 endpoints: `/`, `/health`, `/validate`, `/upload`
  - Interactive Swagger documentation at `/docs`
  - File upload support (Excel & YAML)
  - Structured JSON responses
  - Production-ready with CORS, error handling, and health checks

**No Breaking Changes** - All existing CLI functionality preserved!

---

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

## 🌐 API Usage (NEW!)

The Travel Readiness Sentinel is now available as a **REST API microservice** for integration with web applications, mobile apps, and other services.

### Starting the API Server

```bash
# Install dependencies (including FastAPI)
pip install -r requirements.txt

# Start the API server
uvicorn src.api:app --reload

# Server will be available at http://localhost:8000
# Interactive API docs at http://localhost:8000/docs
```

### API Endpoints

#### `GET /` - API Information
Returns API metadata and links to documentation.

```bash
curl http://localhost:8000/
```

#### `GET /health` - Health Check
Health check endpoint for monitoring and load balancers.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2025-04-10T12:00:00",
  "checks": {
    "api": "operational",
    "validation_engine": "operational"
  }
}
```

#### `POST /validate` - Validate JSON Itinerary
Validate a travel itinerary from JSON data.

```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "trip_details": {
      "destination": "Tokyo",
      "start_date": "2025-04-10",
      "end_date": "2025-04-17",
      "total_duration_days": 7
    },
    "flights": [
      {
        "type": "arrival",
        "flight_number": "NH110",
        "arrival_date": "2025-04-10"
      },
      {
        "type": "departure",
        "flight_number": "NH111",
        "departure_date": "2025-04-17"
      }
    ],
    "accommodation": {
      "hotel_name": "Park Hyatt Tokyo",
      "check_in": "2025-04-10",
      "check_out": "2025-04-17"
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "destination": "Tokyo",
  "total_checks": 3,
  "passed_checks": 3,
  "failed_checks": 0,
  "checks": [
    {
      "check_name": "Arrival Date Alignment",
      "passed": true,
      "message": "Flight arrival (2025-04-10) matches hotel check-in"
    },
    {
      "check_name": "Full Accommodation Coverage",
      "passed": true,
      "message": "Hotel covers full trip duration (7 nights >= 7 nights)"
    },
    {
      "check_name": "Exit Strategy Alignment",
      "passed": true,
      "message": "Departure flight (2025-04-17) matches trip end date"
    }
  ],
  "timestamp": "2025-04-10T12:00:00"
}
```

#### `POST /upload` - Upload and Validate File
Upload and validate an Excel or YAML file.

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@examples/excel/itinerary_template.xlsx"
```

Returns the same validation response format as `/validate`.

### Interactive API Documentation

Visit **http://localhost:8000/docs** for interactive Swagger UI documentation where you can:
- Explore all endpoints
- Test API calls directly from your browser
- View request/response schemas
- Download OpenAPI specification

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
