# Cloud CSV to JSON Converter

> A resilient, cloud-native data transformation microservice converting delimiter-separated tabular data into structured JSON with schema flexibility.

---

## 1. Project Overview

The **Cloud CSV to JSON Converter** is a container-ready web application and RESTful microservice engineered for high-throughput extract-transform-load (ETL) preprocessing in cloud ecosystems. Built with Python and Flask, it ingests CSV, TSV, and delimited text files through interactive drag-and-drop file streams or direct REST API requests, outputting structured JSON according to user-selected schema models.

Supporting multiple JSON topologies—including Arrays of Objects, Arrays of Arrays (matrix-style), and Key-Indexed Nested Dictionaries—the service handles real-world data intricacies such as character encoding autodetection, multiline quoted fields, customizable delimiters, and UTF-8 Byte Order Marks (BOM). It is optimized for zero-footprint containerized deployment on platforms such as Render, Railway, AWS App Runner, or Google Cloud Run.

---

## 2. Problem Statement

Tabular CSV files remain the dominant export format for legacy databases, enterprise CRM systems, spreadsheet tools, and financial ledgers. Conversely, modern distributed cloud architectures, serverless pipelines, NoSQL document stores (such as MongoDB, DynamoDB, and Firestore), and REST/GraphQL APIs exclusively consume JSON.

Manual format conversions or bloated desktop utilities create ingestion bottlenecks and introduce character corruption (such as encoding mismatches or unescaped delimiter splits). Operating a dedicated, stateless cloud transformation microservice eliminates integration friction by providing automated delimiter detection, consistent JSON normalization, schema enforcement, and instant API programmatic conversion for cloud storage pipelines.

---

## 3. Objectives

- Construct an enterprise-grade Python microservice providing stateless data transformation between delimited tables and JSON.
- Provide automatic format discovery including delimiter detection (`,`, `;`, `\t`, `|`) and character encoding detection via `chardet`.
- Implement multiple JSON schema paradigms: flat object collections, relational 2D arrays, and associative nested dictionary lookups.
- Expose RESTful endpoints supporting both direct JSON payload transfers and multipart file streams up to 5 MB.
- Deliver an interactive, green/emerald-themed single-page web dashboard offering live table previews, syntax-highlighted JSON rendering, and instant export downloads.
- Ensure reliability through automated test suites covering parser mechanics, encoding fallbacks, edge-case quoting, and API workflows with `pytest`.

---

## 4. Features

- **Robust Delimiter & Encoding Detection:**
  - Dynamic heuristic evaluation detecting `,`, `;`, `\t`, and `|`.
  - Automatic byte-level character encoding resolution (UTF-8, ASCII, ISO-8859-1, Windows-1252) preventing payload corruption.
- **Versatile Output Schema Formatting:**
  - **Array of Objects:** `[{"id": "1", "name": "Alice"}, ...]`
  - **Array of Arrays:** `[["id", "name"], ["1", "Alice"], ...]`
  - **Nested JSON Dictionary:** `{"user-1": {"name": "Alice", ...}}` indexed by a designated key column.
- **Interactive Web Interface:**
  - Dual ingestion modes: interactive raw text editor or drag-and-drop file upload.
  - Tabular data preview displaying the initial 10 rows prior to transformation.
  - Formatted JSON display area with syntax highlights and single-click clipboard copy.
- **RESTful File Streaming & Previews:**
  - Programmatic endpoints for automated cloud ETL pipeline integrations.
  - Direct file download generation preserving generated structure.
- **Defensive Data Handling:**
  - Clean parsing of internal line breaks within quoted fields.
  - Graceful rejection of invalid extensions, empty files, and payloads exceeding limits.

---

## 5. Cloud Computing Concepts Demonstrated

| Concept | Implementation in this Project |
| :--- | :--- |
| **Data Transformation Pipeline (ETL)** | Acts as the Extract-Transform stage converting raw storage objects into target document formats for cloud ingestion. |
| **Stateless Microservice** | Operates with no persistent state between requests, allowing horizontal scaling behind cloud load balancers. |
| **Containerization Ready** | Accompanied by standard `Procfile` and environment-based configuration for zero-friction container orchestration. |
| **API-First Design** | Core conversion logic is exposed as RESTful contracts consumable by Lambda functions, cloud queues, or web clients. |
| **Dynamic Resource Scaling** | Memory-conscious chunk reading and garbage-collected string buffers ensure minimal RAM consumption under concurrent cloud loads. |

---

## 6. Technology Stack

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Runtime** | Python | >= 3.9 | Backend programming runtime |
| **Framework** | Flask | ^3.0.0 | Lightweight WSGI web framework and routing |
| **WSGI Server** | Gunicorn | ^21.2.0 | Production-ready HTTP application server |
| **Encoding Analysis** | Chardet | ^5.2.0 | Universal character encoding detector |
| **CORS Support** | Flask-CORS | ^4.0.0 | Cross-origin resource sharing middleware |
| **Config Management**| Python-Dotenv | ^1.0.0 | 12-factor application environment loading |
| **Frontend** | HTML5 / CSS3 / ES6 | Native | Responsive emerald-themed interface |
| **Testing** | Pytest | ^7.4.3 | Automated test runner and assertion framework |

---

## 7. Architecture & Workflow

```
+--------------------------------------------------------------------------+
|                               Client Layer                               |
|        Web Interface (Drag & Drop)   OR   External Cloud Pipeline        |
+------------------------------------+-------------------------------------+
                                     |
                         HTTP POST (Multipart / JSON)
                                     v
+--------------------------------------------------------------------------+
|                               WSGI Server                                |
|                         (Gunicorn / Flask App)                           |
+------------------------------------+-------------------------------------+
                                     |
                                   app.py
                                     v
                         +-----------+-----------+
                         |  Input & File Guards  |
                         |  (utils/validators.py)|
                         +-----------+-----------+
                                     | Valid payload
                                     v
                         +-----------------------+
                         |   CSV Parser Service  |
                         | (services/csv_parser) |
                         | - detect_encoding()   |
                         | - detect_delimiter()  |
                         | - parse_csv()         |
                         +-----------+-----------+
                                     | Parsed records
                                     v
                         +-----------------------+
                         | JSON Formatter Service|
                         | (services/json_format)|
                         | - to_array_of_objects |
                         | - to_array_of_arrays  |
                         | - to_nested_json      |
                         +-----------+-----------+
                                     |
                               JSON Payload
                                     v
                           HTTP 200 OK Response
```

---

## 8. Folder Structure

```
project-2-csv-to-json/
├── .env.example              # Environment variable definitions template
├── .gitignore                # Exclusions for Python caches, venv, and logs
├── README.md                 # Complete service documentation
├── Procfile                  # Cloud process file for Gunicorn deployment
├── requirements.txt          # Production and testing Python dependencies
├── config.py                 # Centralized 12-Factor application configuration
├── app.py                    # Flask application endpoints and lifecycle
├── services/
│   ├── __init__.py           # Service package declaration
│   ├── csv_parser.py         # Parsing, dialect sniffing, and decoding logic
│   ├── file_handler.py       # File stream intake and download generator
│   └── json_formatter.py     # Schema formatting engines (Array, Matrix, Nested)
├── utils/
│   ├── __init__.py           # Utility package declaration
│   └── validators.py         # Payload bounds and extension verification
├── templates/
│   └── index.html            # User interface Jinja2 template
├── static/
│   ├── css/
│   │   └── styles.css        # Responsive layout and custom UI styling
│   └── js/
│       └── app.js            # Asynchronous client actions, preview, and copy
└── tests/
    ├── __init__.py           # Test package initialization
    ├── test_api.py           # Integration tests for Flask endpoints
    ├── test_csv_parser.py    # Unit tests for dialects, encodings, and quotes
    ├── test_file_handler.py  # Tests for upload constraints and size limits
    └── test_json_formatter.py# Tests for schema formats and serialization
```

---

## 9. Prerequisites

- **Python:** version `3.9` through `3.12`
- **pip:** package manager installed
- **Git:** version `2.x` or later

---

## 10. Installation & Local Setup

1. **Navigate to the project folder:**
   ```bash
   cd cloud-computing-projects/project-2-csv-to-json
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize environment settings:**
   ```bash
   cp .env.example .env
   ```

---

## 11. Environment Variable Configuration

| Variable | Description | Default Value | Required |
| :--- | :--- | :--- | :--- |
| `FLASK_ENV` | Runtime environment mode | `development` | No |
| `FLASK_DEBUG` | Enable debug logs and hot reload | `1` | No |
| `PORT` | Web server listening port | `5000` | No |
| `MAX_FILE_SIZE`| Maximum upload byte size | `5242880` (5MB) | No |
| `SECRET_KEY` | Session signing key | `dev-secret-key` | Production |

---

## 12. How to Run the Application

### Development Server:
```bash
python app.py
```

### Production WSGI Server (Gunicorn):
```bash
gunicorn app:app --bind 0.0.0.0:5000
```
*Expected Output:*
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:5000 (12345)
[INFO] Using worker: sync
[INFO] Booting worker with pid: 12346
```

Open `http://localhost:5000` in your web browser.

---

## 13. How to Test

Run the automated test suite using `pytest`:

```bash
pytest -v
```

*Expected Verification Output:*
```
tests/test_api.py::test_index_route PASSED
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_api_convert_json_payload PASSED
tests/test_api.py::test_api_convert_file_upload PASSED
tests/test_api.py::test_api_detect_delimiter PASSED
tests/test_api.py::test_api_preview PASSED
tests/test_api.py::test_api_convert_invalid_input PASSED
tests/test_csv_parser.py::test_parse_csv_basic_with_header PASSED
tests/test_csv_parser.py::test_parse_csv_without_header PASSED
tests/test_csv_parser.py::test_detect_delimiter_comma PASSED
tests/test_csv_parser.py::test_detect_delimiter_semicolon PASSED
tests/test_csv_parser.py::test_detect_delimiter_tab PASSED
tests/test_csv_parser.py::test_detect_delimiter_pipe PASSED
tests/test_csv_parser.py::test_detect_encoding PASSED
tests/test_csv_parser.py::test_quoted_fields_with_commas PASSED
tests/test_csv_parser.py::test_empty_rows_handling PASSED
tests/test_csv_parser.py::test_bom_character_handling PASSED
tests/test_file_handler.py::test_handle_upload_valid_csv PASSED
tests/test_file_handler.py::test_handle_upload_invalid_extension PASSED
tests/test_file_handler.py::test_handle_upload_empty PASSED
tests/test_json_formatter.py::test_to_array_of_objects PASSED
tests/test_json_formatter.py::test_to_array_of_arrays PASSED
tests/test_json_formatter.py::test_to_nested_json PASSED
tests/test_json_formatter.py::test_to_nested_json_missing_key PASSED
tests/test_json_formatter.py::test_format_output_pretty_and_compact PASSED
tests/test_json_formatter.py::test_format_output_empty PASSED

======================== 26 passed in 0.42s ========================
```

---

## 14. API Documentation

### 1. Convert CSV to JSON
- **Endpoint:** `POST /api/convert`
- **Content-Type:** `application/json` or `multipart/form-data`
- **JSON Request Body:**
  ```json
  {
    "text": "id,name,role\n1,Alice,Architect\n2,Bob,Engineer",
    "format": "array_of_objects",
    "delimiter": ",",
    "hasHeader": true,
    "prettyPrint": true
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "success": true,
    "jobId": "550e8400-e29b-41d4-a716-446655440000",
    "format": "array_of_objects",
    "rowCount": 2,
    "jsonString": "[\n  {\n    \"id\": \"1\",\n    \"name\": \"Alice\",\n    \"role\": \"Architect\"\n  },\n  {\n    \"id\": \"2\",\n    \"name\": \"Bob\",\n    \"role\": \"Engineer\"\n  }\n]"
  }
  ```

### 2. Auto-Detect Dialect & Encoding
- **Endpoint:** `POST /api/detect`
- **Request Body:** `{ "text": "city;temp;units\nParis;22;C\nTokyo;26;C" }`
- **Response (`200 OK`):**
  ```json
  {
    "delimiter": ";",
    "encoding": "utf-8",
    "sampleLines": 3
  }
  ```

### 3. Preview Tabular Data
- **Endpoint:** `POST /api/preview`
- **Request Body:** `{ "text": "id,val\n1,Alpha\n2,Beta", "hasHeader": true }`
- **Response (`200 OK`):**
  ```json
  {
    "totalRows": 2,
    "previewRows": 2,
    "delimiter": ",",
    "data": [{"id": "1", "val": "Alpha"}, {"id": "2", "val": "Beta"}]
  }
  ```

### 4. Download Converted File
- **Endpoint:** `GET /api/download/<job_id>`
- **Response (`200 OK`):** Attachment file stream named `converted_<job_id>.json`.

---

## 15. Cloud Deployment Instructions

### Deploy to Render (Web Service)
1. Fork or push this repository to GitHub as `cloud-csv-to-json-converter`.
2. In the [Render Dashboard](https://dashboard.render.com), create a new **Web Service**.
3. Connect your GitHub repository.
4. Configure service parameters:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Click **Create Web Service**. Render provisions the SSL certificate and issues a public `.onrender.com` URL.

### Deploy to Railway
1. Navigate to [Railway.app](https://railway.app) and create a **New Project**.
2. Select **Deploy from GitHub repo** and choose `cloud-csv-to-json-converter`.
3. Railway automatically detects `requirements.txt` and `Procfile` and builds the service.
4. In the service settings, click **Generate Domain** to access the live URL.

---

## 16. Verified Live Website URL

- **GitHub Repository:** https://github.com/nagavishwa-spidey/cloud-csv-to-json-converter
- **Live Deployment URL:** _To be updated after cloud provider deployment verification_

---

## 17. Screenshots & Visual Captures

To record documentation captures:
1. Open the web interface.
2. Load a sample CSV dataset using the Paste mode or Drag & Drop zone.
3. Click **Preview Table** to verify column alignment.
4. Click **Convert to JSON** and switch formats between Array of Objects and Nested JSON.
5. Save screenshots under `assets/screenshots/`:
   - `01-dropzone-and-input.png`: Input workspace showing drag-and-drop file target.
   - `02-table-preview.png`: 10-row tabular data preview card.
   - `03-json-output.png`: Formatted JSON result display with copy/download controls.

---

## 18. Limitations & Future Improvements

- **Streaming for Giant Files:** Files above 5 MB currently rejected; future iterations can implement chunked streaming via generator responses for multi-gigabyte datasets.
- **Direct S3/GCS Integration:** Support reading directly from pre-signed cloud storage URLs and writing transformed JSON back to cloud buckets.
- **Type Coercion Engine:** Auto-infer numerical integers, floating-point numbers, and ISO timestamps instead of storing all fields as strings.

---

## 19. License

This project is open-source software licensed under the **MIT License**.

---

## 20. Author

Developed by **nagavishwa-spidey** for Cloud Computing Engineering.
