<p align="center">
  <img src="assets/logo.png" alt="NoboDorshi Logo" width="200"/>
</p>

<h1 align="center">Nobodristhi - AI Powered News Control and Management System</h1>

<p align="center">
  A comprehensive news processing and verification backend API. The system handles raw reports, processes them with ML algorithms, performs image verification, and provides admin management capabilities.
</p>

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Snapshots](#snapshots)
- [Features](#features)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Development & Contribution](#development--contribution)
- [License](#license)

## 🎯 Project Overview

Nobodristhi is the backend core designed to streamline news verification and processing. It provides robust API endpoints for member management, raw report submission, AI-based text processing, and administrative controls to approve or reject processed news items.

## 📸 Snapshots

### Dashboard View
![Dashboard Snapshot](assets/dashboard.png)
*A sleek, modern web dashboard for an AI Powered News Management System, displaying report statuses and AI analysis metrics.*

### AI Processing
![AI Processing Snapshot](assets/ai_processing.png)
*Visual representation of the AI engine processing a news article, highlighting entities and summarizing facts.*

## ✨ Features

- **Member Management**: Create, authenticate, and manage users with role-based access.
- **Raw Report Submission**: Accept text reports with optional image attachments and geolocation data.
- **Intelligent Report Processing**: ML-powered pipeline for analyzing and summarizing reports via background tasks.
- **Image Verification**: Integrates with search services for media authenticity verification.
- **Admin Operations**: Dashboard-ready endpoints to approve/reject reports and manage news templates.

## 📁 Repository Structure

```
Nobodristhi/
├── main.py              # Flask app entry point & configuration
├── requirements.txt     # Python dependencies
├── database/            # Database connection pooling
├── handlers/            # Business logic (ML, processing, search)
├── routes/              # API endpoint blueprints
├── assets/              # Logos and snapshot images
└── README.md            # This documentation file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- External API keys configured (e.g., OpenRouter, SerpAPI)

### Quick Start

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/kingmon6996/Nobodristhi.git
   cd Nobodristhi
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   # Activate on Windows:
   venv\Scripts\activate
   # Activate on macOS/Linux:
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
   DATABASE_URL=postgresql://username:password@localhost:5432/nobodristhi
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

5. **Run the API server**:
   ```bash
   python main.py
   ```
   The server will start on `http://0.0.0.0:5000`.

## 🌐 API Endpoints

**Base URL:** `http://localhost:5000`

- `GET /` - Health Check
- `POST /member/login` - Authenticate member
- `POST /raw/report` - Submit raw report
- `GET /processed/reports` - Get all processed reports
- `POST /admin/approve` - Approve a processed news report
- `GET /template/list` - Fetch templates

*(For complete details, refer to the route definitions in the `routes/` directory).*

## 👨‍💻 Development & Contribution

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and commit: `git commit -am 'Add new feature'`
3. Push to the branch: `git push origin feature/your-feature`
4. Submit a Pull Request.

Make sure your code aligns with the existing architecture where routes are decoupled from handlers, and heavy ML processing happens asynchronously.

## 📄 License

This project is part of the Nobodristhi system. All rights reserved.
