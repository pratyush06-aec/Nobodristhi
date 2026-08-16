<p align="center">
  <img src="assets/logo.png" alt="NoboDorshi Logo" width="250"/>
</p>

<h1 align="center">NoboDorshi - AI Powered News Control & Management System</h1>

<p align="center">
  A comprehensive news processing and verification backend API. The system handles raw reports, processes them with intelligent Machine Learning algorithms, performs reverse-image media verification, groups reports by geographical proximity, and provides robust administrative management capabilities.
</p>

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Snapshots & Application Previews](#-snapshots--application-previews)
3. [Tech Stack & Dependencies](#-tech-stack--dependencies)
4. [System Architecture & Workflow](#-system-architecture--workflow)
5. [Directory Structure](#-directory-structure)
6. [Database Schema](#-database-schema)
7. [API Endpoints Reference](#-api-endpoints-reference)
8. [Developer Guide (Getting Started)](#-developer-guide-getting-started)
9. [Contribution Guidelines](#-contribution-guidelines)

---

## 🎯 Project Overview

**NoboDorshi** serves as the intelligent core backend for a streamlined, secure news verification pipeline. 

It provides secure REST API endpoints for user/member management, raw news submission (with precise geolocation and image payload capabilities), automatic background AI-based summarization and clustering, and administrative moderation to approve or reject processed news items into their final state.

---

## 📸 Snapshots & Application Previews

<div align="center">
  <img src="assets/preview_1.png" alt="Preview 1" width="800"/>
  <br/><br/>
  <img src="assets/preview_2.png" alt="Preview 2" width="400"/>
  <img src="assets/preview_3.png" alt="Preview 3" width="400"/>
  <br/><br/>
  <img src="assets/preview_4.png" alt="Preview 4" width="400"/>
  <img src="assets/preview_5.png" alt="Preview 5" width="400"/>
  <br/><br/>
  <img src="assets/preview_6.png" alt="Preview 6" width="800"/>
</div>

---

## 🛠 Tech Stack & Dependencies

The project relies on a robust and modern stack. For development, ensure your environment matches these versions:

### Core Frameworks
- **Python**: `3.8+` (Recommended: `3.10+`)
- **Flask**: Lightweight WSGI web application framework.
- **Flask-CORS**: Handling Cross-Origin Resource Sharing for API consumption.

### Database & Storage
- **PostgreSQL**: `12.0+` (Relational database for storing reports and users).
- **psycopg2-binary**: PostgreSQL database adapter for Python.
- **Supabase**: Used for public file storage/buckets (specifically media and voice files). 

### External Services & APIs
- **OpenRouter API**: Routes LLM requests. Uses models like `gpt-oss-120b:free` or `google/gemma-4-31b-it:free`. Handles text summarization, extraction, and semantic similarity checking.
- **SerpAPI**: Used for automated reverse-image searches to verify media authenticity based on AI-generated headlines.
- **Requests**: HTTP library used to communicate with OpenRouter and SerpAPI.

---

## 🏗 System Architecture & Workflow

The architecture is fully decoupled, isolating fast API routes from heavy background AI tasks.

### 1. The HTTP Routing Layer (`/routes`)
When a client makes a request, it hits the Flask Blueprints. These routes (`admin`, `member`, `processed`, `raw`, `template`) do **no heavy lifting**. They simply validate the payload, insert/fetch from the database, and return a fast JSON response. 
- Example: A user posts a news report. The `/raw` route saves it to the `raw_reports` table and returns `200 OK` instantly.

### 2. The Background Daemon (`ProcessingTask`)
To prevent blocking HTTP requests, the core processing runs on an independent daemon thread that wakes up every **10 seconds**.
1. **Polling**: It fetches all unprocessed reports from the `raw_reports` table.
2. **Geospatial Clustering**: Uses the **Haversine Formula** to check if the new report is within a **50-meter radius** of an existing recently processed report.
3. **Semantic Similarity**: If the location matches, it queries the LLM to verify if the context is the same (`check_similarity`).
4. **AI Generation**: 
   - *New Event*: Generates a `breaking` headline, `summary`, and `description`.
   - *Existing Event*: Appends the new facts to the existing AI summaries.
5. **Media Verification**: If no image was attached, the system hits SerpAPI to scrape a relevant authentic image using the generated headline.
6. **Queueing**: Saves the enriched data into `processed_reports` awaiting admin approval.

### 3. Moderation & Final Ledger
Administrators query the `processed_reports` table via the `/admin` routes. Upon approval, the report is securely migrated to the `complete_news` table, making it available for public consumption.

---

## 📁 Directory Structure

```text
NoboDorshi/
├── assets/                 # Static assets (logos, screenshots)
├── database/               # DB connection layer
│   └── pool.py             # Custom Threaded PostgreSQL connection pooler
├── handlers/               # Core business logic
│   ├── ml.py               # OpenRouter LLM integration & query optimization
│   ├── process.py          # Background processing daemon & clustering logic
│   ├── search.py           # SerpAPI reverse-image search logic
│   └── voice.py            # Audio/Voice processing utilities
├── routes/                 # Flask Blueprints (REST API)
│   ├── admin.py            # Admin moderation endpoints
│   ├── member.py           # Authentication & session endpoints
│   ├── processed.py        # Processed reports queue endpoints
│   ├── raw.py              # Raw report submission endpoints
│   └── template.py         # UI Template configurations
├── tokens.json             # (Gitignored) Array of OpenRouter tokens for rotation
├── main.py                 # Application entrypoint & server initialization
└── requirements.txt        # Python dependencies
```

---

## 🗄 Database Schema

The system automatically initializes 5 primary tables in PostgreSQL on startup:

1. **`members`**: Stores user authentication and role data.
2. **`raw_reports`**: Direct, unfiltered submissions holding text, `JSONB` location coordinates, reporter IDs, and external source information. 
3. **`processed_reports`**: Output of the Background ML processing queue. Contains AI-generated `summary`, `breaking` status, and `description`. Linked to `raw_id`.
4. **`complete_news`**: The final truth-verified reports approved by the system administrators.
5. **`templates`**: System UI configurations.

---

## 🌐 API Endpoints Reference

**Base URL:** `http://localhost:5000`

### 📝 Raw Reports (`/raw`)
- **`POST /raw/report`**: Submit a new report. Expects `multipart/form-data` including `text`, `latitude`, `longitude`, `reporterid`. Optionally uploads an `image` payload directly to Supabase Storage buckets.
- **`GET /raw/`**: Returns all unmoderated raw reports.
- **`POST /raw/delete`**: Drops a report by its `raw_id`.

### 🧠 Processed Reports (`/processed`)
- **`GET /processed/`**: Retrieve all processed (but unapproved) reports waiting in the moderation queue.
- **`POST /processed/report`**: Fetch a specific processed report by its `processed_id`.
- **`POST /processed/delete`**: Clear a processed report.

### 🛡 Admin (`/admin`)
- **`POST /admin/approve`**: Mark a processed report as verified, migrating it to the `complete_news` public ledger.

### 👥 Members (`/member`)
- **`POST /member/login`** & **`POST /member/delete`**: User session and access management.

*(Refer to individual files in `/routes/` for comprehensive payload requirements and JSON response shapes).*

---

## 👨‍💻 Developer Guide (Getting Started)

Follow these instructions to set up your local development environment.

### 1. Prerequisites
- **Python 3.8+** installed.
- **PostgreSQL 12+** running locally (or a Supabase DB instance).
- API Keys required: 
  - [OpenRouter](https://openrouter.ai/)
  - [SerpAPI](https://serpapi.com/)
  - [Supabase](https://supabase.com/)

### Quick Start

Clone the repository and navigate into it:
```bash
git clone https://github.com/kingmon6996/Nobodristhi.git
cd Nobodristhi
```

Create and activate a Python virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root of the project:
```env
PORT=5000
DEBUG=True

# Database Configuration (Local or Supabase)
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/nobodorshi

# Supabase Storage Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# SerpAPI Configuration
SERPAPI_KEY=your_serpapi_key
```

Create a `tokens.json` file in the root of the project. The system uses this array to cycle through OpenRouter tokens to avoid rate limits:
```json
[
  { "token": "sk-or-v1-your-openrouter-key-1" },
  { "token": "sk-or-v1-your-openrouter-key-2" }
]
```

### 4. Running the Server

Start the application:
```bash
python main.py
```

*Upon startup, the server will automatically connect to PostgreSQL, execute the `init_tables()` schema migration, spawn the `ProcessingTask` daemon thread, and expose the Flask REST API.*

---

## 🤝 Contribution Guidelines

NoboDorshi welcomes contributions! To contribute:

1. Fork the repository and create your feature branch: `git checkout -b feature/amazing-feature`.
2. Ensure any new API routes properly request and release database connections using the `db.get_connection()` and `db.return_connection(conn)` pattern.
3. If modifying the ML processing queue (`handlers/process.py`), ensure your changes are thread-safe and non-blocking.
4. Commit your changes: `git commit -m 'Add amazing feature'`.
5. Push to the branch: `git push origin feature/amazing-feature`.
6. Open a Pull Request for review.

**Note:** Always ensure that `ProcessingTask` logic changes are thread-safe, and new API routes correctly instantiate and close database pool connections (`db.get_connection()`).

---

## 📄 License

This project is part of the NoboDorshi ecosystem. All rights reserved.
