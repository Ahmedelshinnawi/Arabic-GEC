# Arabic Text Correction (GEC)

A modern, AI-powered web application for correcting Arabic text using advanced machine learning models. Built with FastAPI and powered by Hugging Face transformers.

![Arabic Text Correction](https://img.shields.io/badge/Language-Arabic-green)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

### Core Functionality

- **AI-Powered Correction**: Uses the `alnnahwi/gemma-3-1b-arabic-gec-v1` model for high-quality Arabic text correction
- **Real-time Processing**: Fast text correction with GPU acceleration and CPU fallback
- **History Management**: Complete correction history with database persistence
- **Bilingual Support**: Full Arabic UI with RTL (Right-to-Left) layout support

### Technical Features

- **REST API**: Comprehensive RESTful API with FastAPI
- **Web Interface**: Modern, responsive web application
- **Database Integration**: Supabase integration for data persistence
- **GPU Optimization**: Optimized for NVIDIA RTX 2060 with intelligent fallback
- **Health Monitoring**: Built-in health checks and logging
- **Character Limits**: Configurable text length limits (up to 5000 characters)

### User Interface

- **Modern Dark Theme**: Beautiful dark theme with gradient accents
- **Responsive Design**: Mobile-first responsive design with Bootstrap 5
- **Arabic Typography**: Custom Arabic fonts (Cairo) for optimal readability
- **Real-time Feedback**: Loading states, character counters, and copy functionality
- **Toast Notifications**: User-friendly success/error notifications

## Architecture

```
GEC/
├── app/
│   ├── api/                # REST API routes
│   │   └── routes.py       # API endpoints (/gec/*)
│   ├── models/             # Data models and schemas
│   │   └── schema.py       # Pydantic models
│   ├── services/           # Business logic
│   │   ├── correction_service.py  # AI model management
│   │   └── database_service.py    # Database operations
│   ├── templates/          # Jinja2 HTML templates
│   │   ├── base.html       # Base template with RTL support
│   │   ├── index.html      # Home page
│   │   ├── correction.html # Results page
│   │   └── history.html    # History page
│   ├── web/                # Web interface routes
│   │   └── routes.py       # Web endpoints (/, /correct, /history)
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connection
│   └── main.py             # FastAPI app setup
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css       # Modern dark theme with RTL support
│   └── js/
│       └── main.js         # Frontend interactivity
├── logger.py               # Logging configuration
├── run.py                  # Application entry point
└── pyproject.toml          # Dependencies and metadata
```

## Quick Start

### Prerequisites

- **Python 3.12+**
- **CUDA-capable GPU** (recommended, RTX 2060 or better)
- **Supabase account** for database

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd GEC
   ```

2. **Install dependencies**

   ```bash
   # Using uv (recommended)
   pip install uv
   uv sync

   # Or using pip
   pip freeze > requirements.txt
   pip install -r requirements.txt
   ```

3. **Environment setup**

   Create a `.env` file in the project root:

   ```env
   # Supabase Configuration
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key

   # Application Configuration
   DEBUG=false
   HOST=0.0.0.0
   PORT=8000

   # Model Configuration
   MODEL_NAME=alnnahwi/gemma-3-1b-arabic-gec-v1
   MAX_TEXT_LENGTH=5000
   ```

4. **Database setup (Supabase Free Tier)**

   Follow these steps to set up your Supabase database:

   **Step 4.1: Create Supabase Account**

   1. Go to [supabase.com](https://supabase.com) and sign up for free
   2. Click "New Project" and fill in:
      - **Project Name**: `arabic-text-correction` (or your preferred name)
      - **Database Password**: Generate a strong password (save it!)
      - **Region**: Choose the closest to your users
      - **Pricing Plan**: Free tier (2 projects, 500MB database, 2GB bandwidth/month)

   **Step 4.2: Get Connection Details**

   1. Go to **Settings** > **API** in your Supabase dashboard
   2. Copy these values for your `.env` file:
      - **Project URL**: `https://your-project-id.supabase.co`
      - **Anon Public Key**: `eyJ...` (starts with eyJ)

   **Step 4.3: Create Database Table**

   1. Go to **SQL Editor** in your Supabase dashboard
   2. Click **New Query** and run this SQL:

   ```sql
   -- Create the corrections table
   CREATE TABLE corrections (
     id BIGSERIAL PRIMARY KEY,
     original_text TEXT NOT NULL,
     corrected_text TEXT NOT NULL,
     created_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- Create an index for better performance on history queries
   CREATE INDEX corrections_created_at_idx ON corrections(created_at DESC);
   ```

   **Step 4.4: Verify Setup**

   1. Go to **Table Editor** in Supabase
   2. You should see the `corrections` table
   3. The table structure should show: `id`, `original_text`, `corrected_text`, `created_at`

5. **Run the application**
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:8000`

## API Documentation

### Endpoints Overview

| Method | Endpoint           | Description                   |
| ------ | ------------------ | ----------------------------- |
| GET    | `/`                | Web interface home page       |
| POST   | `/correct`         | Web form submission           |
| GET    | `/history`         | Web interface history page    |
| GET    | `/gec/health`      | API health check              |
| POST   | `/gec/correct`     | API text correction           |
| GET    | `/gec/all`         | API get all corrections       |
| DELETE | `/gec/delete/{id}` | API delete correction         |
| GET    | `/docs`            | Interactive API documentation |

### API Usage Examples

#### Health Check

```http
GET /api/health
```

Returns the current status of the API and model loading state.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000",
  "model_loaded": true
}
```

#### Text Correction

```http
POST /api/corrections
```

Corrects grammatical errors in Arabic text and saves to database.

**Request Body:**

```json
{
  "text": "كيف حالكي اليوم ؟"
}
```

**Response:**

```json
{
  "id": 1,
  "original_text": "كيف حالكي اليوم ؟",
  "corrected_text": "كيف حالك اليوم؟",
  "timestamp": "2025-01-08T12:00:00"
}
```

### Get All Corrections

```http
GET /api/corrections
```

Retrieves all correction records from database (sorted by newest first).

**Response:**

```json
[
  {
    "id": 1,
    "original_text": "كيف حالكي اليوم ؟",
    "corrected_text": "كيف حالك اليوم؟",
    "created_at": "2025-01-08T12:00:00"
  }
]
```

### Delete Correction

```http
DELETE /api/corrections/{correction_id}
```

Deletes a specific correction record by ID.

**Response:** `204 No Content`

## Development

### Code Formatting

```bash
# Format code
uv run black .

# Sort imports
uv run isort .

# Lint code
uv run ruff check .
```

### Development Server

```bash
# Run with auto-reload
python run.py  # DEBUG=true in .env for auto-reload
```

## Configuration

### Environment Variables

| Variable          | Description          | Default                             |
| ----------------- | -------------------- | ----------------------------------- |
| `SUPABASE_URL`    | Supabase project URL | Required                            |
| `SUPABASE_KEY`    | Supabase anon key    | Required                            |
| `DEBUG`           | Enable debug mode    | `false`                             |
| `HOST`            | Server host          | `0.0.0.0`                           |
| `PORT`            | Server port          | `8000`                              |
| `MODEL_NAME`      | Hugging Face model   | `alnnahwi/gemma-3-1b-arabic-gec-v1` |
| `MAX_TEXT_LENGTH` | Maximum input length | `5000`                              |

### GPU Configuration

The application is optimized for NVIDIA RTX 2060 and similar cards:

- **Float16 precision** for memory efficiency
- **Eager attention** mechanism for stability
- **Automatic CPU fallback** if GPU fails
- **CUDA memory optimization** for better performance

## Web Interface

### Pages

1. **Home Page** (`/`)

   - Text input form with character counter
   - Real-time validation and feedback
   - Modern dark theme with Arabic typography

2. **Correction Result** (`/correct`)

   - Side-by-side comparison of original vs corrected text
   - Copy-to-clipboard functionality
   - Navigation to history and new correction

3. **History** (`/history`)
   - Paginated list of all corrections
   - Delete functionality with confirmation
   - Copy corrected text directly

### Features

- **RTL Support**: Full right-to-left layout for Arabic text
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Loading States**: Visual feedback during processing
- **Error Handling**: User-friendly error messages
- **Accessibility**: Proper ARIA labels and semantic HTML

## AI Model

### Model Details

- **Model**: `alnnahwi/gemma-3-1b-arabic-gec-v1`
- **Type**: Transformer-based Arabic grammar error correction
- **Size**: ~1.5B parameters
- **Framework**: Hugging Face Transformers
- **Performance**: Optimized for common Arabic grammar errors

### Model Features

- **Grammar Correction**: Fixes common Arabic grammatical errors
- **Punctuation**: Corrects punctuation and diacritics
- **Spelling**: Identifies and corrects spelling mistakes
- **Context Awareness**: Considers context for accurate corrections

## Monitoring & Logging

### Health Checks

The application provides comprehensive health monitoring:

```bash
GET /gec/health
```

Returns:

- Application status
- Model loading status
- Current timestamp

### Logging

Structured logging with different levels:

```python
# Logger configuration in logger.py
logging.INFO    # General information
logging.ERROR   # Error conditions
logging.DEBUG   # Detailed debugging (when DEBUG=true)
```

Log format:

```
[2024-01-01 12:00:00] [INFO] app.services.correction_service: Model loaded successfully!
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints for all functions
- Write comprehensive docstrings
- Include tests for new features
- Update documentation as needed

## License

### Application Code

This application code is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### AI Model License

This application uses the **alnnahwi/gemma-3-1b-arabic-gec-v1** model, which is based on Google's Gemma and licensed under the **Gemma License**.

- **Model**: [alnnahwi/gemma-3-1b-arabic-gec-v1](https://huggingface.co/alnnahwi/gemma-3-1b-arabic-gec-v1)
- **Base Model**: Google Gemma (Gemma License)
- **Fine-tuning**: Arabic Grammar Error Correction by alnnahwi

### Combined Usage

Both the MIT License (application) and Gemma License (model) allow:

- **Commercial Use**: You can use this for business purposes
- **Modification**: You can modify and adapt the code/model
- **Distribution**: You can share and redistribute
- **Private Use**: You can use privately without restrictions

**Important**: When distributing this application, ensure you comply with both licenses by including proper attribution for both the application code and the AI model.

## Acknowledgments

- **AI Model**: [alnnahwi/gemma-3-1b-arabic-gec-v1](https://huggingface.co/alnnahwi/gemma-3-1b-arabic-gec-v1) - Fine-tuned Gemma model for Arabic GEC
- **Base Model**: [Google Gemma](https://ai.google.dev/gemma) - Gemma family of lightweight, state-of-the-art open models
- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for Python
- **Database**: [Supabase](https://supabase.com/) - Open-source Firebase alternative
- **ML Library**: [Hugging Face Transformers](https://huggingface.co/transformers/) - State-of-the-art NLP models
