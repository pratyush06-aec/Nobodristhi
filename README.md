<p align="center">
  <img src="assets/logo.png" alt="NoboDorshi Logo" width="250"/>
</p>

<h1 align="center">NoboDorshi - AI Powered News Control and Management System</h1>

<p align="center">
  A comprehensive news processing and verification backend API. The system handles raw reports, processes them with intelligent Machine Learning algorithms, performs reverse-image media verification, groups reports by geographical proximity, and provides robust administrative management capabilities.
</p>

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Snapshots & Application Previews](#snapshots--application-previews)
- [System Architecture](#system-architecture)
- [Database Schema](#database-schema)
- [Background ML Processing](#background-ml-processing)
- [API Endpoints Reference](#api-endpoints-reference)
- [Getting Started](#getting-started)
- [Development & Contribution](#development--contribution)

---

## 🎯 Project Overview

**NoboDorshi** serves as the intelligent core backend for a streamlined, secure news verification pipeline. 

It provides secure REST API endpoints for user member management, raw news submission (with precise geolocation and image payload capabilities), automatic background AI-based summarization and clustering, and administrative moderation to approve or reject processed news items into their final state.

---

## 📸 Snapshots & Application Previews

*Note: Since the backend is primarily a programmatic API interface, the "realtime execution" is best represented by the dashboard interfaces consuming the API and the active server console traces.*

### 1. Dashboard View
![Dashboard Snapshot](assets/dashboard.png)
*A sleek, modern web dashboard interface connected to the NoboDorshi API, displaying realtime report processing statuses, AI analysis metrics, and moderation queues.*

### 2. AI Processing Engine
![AI Processing Snapshot](assets/ai_processing.png)
*Visual representation of the background ML engine parsing a raw news article, highlighting entities, and compiling factual summaries.*

### 3. Realtime Server Execution Logs
![Server Logs Snapshot](assets/logs.png)
*A realtime trace log snapshot from a running NoboDorshi instance demonstrating the initialization of background processing threads and successful ML query optimizations.*

Alternatively, when you execute `python main.py`, your server will initialize its connection pools and spawn the worker threads as shown in this terminal snapshot block:

```bash
🔌 Initializing database connection pool...
✅ Database pool initialized

📊 Initializing database tables...
🔵 [INIT_TABLES] Initializing database tables
📊 [INIT_TABLES] Creating members table...
...
✅ [INIT_TABLES] All tables initialized successfully

🔄 Starting background processing task...
✅ Background task started

🚀 Starting Flask server on http://0.0.0.0:5000
 * Serving Flask app 'main'
 * Debug mode: on
```

---

## 🏗 System Architecture

NoboDorshi separates concerns into isolated components to guarantee stability and scalability:
- **Routes Layer (`/routes`)**: Contains Flask Blueprints (`admin`, `member`, `processed`, `raw`, `template`). Decoupled from heavy processing logic to ensure fast HTTP response times.
- **Handlers Layer (`/handlers`)**: The core business logic.
  - `ml.py`: Integration with the LLMs (query optimization, data summarization).
  - `process.py`: Centralized background daemon. Periodically checks for new reports and calculates geographic similarity.
  - `search.py`: Reverse image searches using external providers (SerpAPI) to authenticate report media.
- **Database Layer (`/database`)**: Built-in psycopg2-based connection pooler (`pool.py`) connecting to PostgreSQL. Files are stored and served publicly using Supabase Storage integration.

---

## 🗄 Database Schema

The system automatically initializes 5 primary tables in PostgreSQL:

1. **`members`**: Stores user authentication and role data.
2. **`raw_reports`**: Direct, unfiltered submissions holding text, `JSONB` location coordinates, reporter IDs, and external source information. 
3. **`processed_reports`**: Output of the Background ML processing queue. Contains AI-generated `summary`, `breaking` status, and `description`, along with verification results. Uses unique constraints linked to `raw_id`.
4. **`complete_news`**: The final truth-verified reports approved by the system administrators.
5. **`templates`**: System UI configurations.

---

## 🤖 Background ML Processing

One of NoboDorshi's standout features is its decoupled, non-blocking Processing Queue (`ProcessingTask` in `handlers/process.py`):

1. **Daemon Thread**: Automatically spins up a background thread that wakes up every `10` seconds.
2. **Batch Polling**: Selects pending items from `raw_reports` that haven't been processed.
3. **Geospatial Clustering**: Uses the **Haversine Formula** to determine if a new report occurred within a **50-meter radius** of an already processed report. If a match is found, the system intelligently optimizes and aggregates the new findings into the existing timeline.
4. **AI Generation**: Transforms raw text into `breaking` highlights, concise `summaries`, and full `descriptions`.
5. **Image Verification**: Extracted features trigger a reverse-image lookup to ensure media credibility.

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

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **PostgreSQL 12+** (Or a Supabase instance)
- API Keys: SerpAPI, OpenRouter (or equivalent LLM provider configured in `handlers/ml.py`)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kingmon6996/Nobodristhi.git
   cd Nobodristhi
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   PORT=5000
   DEBUG=True
   DATABASE_URL=postgresql://user:pass@localhost:5432/nobodorshi
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key
   ```

5. **Run the API server**:
   ```bash
   python main.py
   ```

---

## 👨‍💻 Development & Contribution

NoboDorshi welcomes contributions! Follow these steps to submit your changes:

1. Check out a feature branch: `git checkout -b feature/cool-new-idea`
2. Commit your code: `git commit -am 'Implemented intelligent image batching'`
3. Push to your fork/branch: `git push origin feature/cool-new-idea`
4. Submit a Pull Request describing your changes.

**Note:** Always ensure that `ProcessingTask` logic changes are thread-safe, and new API routes correctly instantiate and close database pool connections (`db.get_connection()`).

---

## 📄 License

This project is part of the NoboDorshi ecosystem. All rights reserved.
