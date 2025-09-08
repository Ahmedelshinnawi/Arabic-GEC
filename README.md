# Arabic Text Correction Web Application (GEC)

A modern, full-stack web application for correcting Arabic text using AI-powered Grammar Error Correction (GEC) models. This application features both a beautiful web interface with Jinja2 templates and a comprehensive REST API, powered by FastAPI and Supabase database.

## Features

### **Modern Web Interface**

- **Beautiful Dark Theme**: Modern glassmorphism UI with smooth animations
- **RTL Support**: Fully optimized for Arabic text display and input
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Real-time Feedback**: Instant text correction with visual feedback

### **AI-Powered Correction**

- **Fine-tuned Model**: Uses `alnnahwi/gemma-3-1b-arabic-gec-v1` specifically trained for Arabic GEC
- **Multi-Device Support**: Auto-detects and utilizes CUDA, MPS, or CPU
- **Smart Fallback**: Graceful degradation from GPU to CPU for stability

### **Modern Architecture**

- **Modular Design**: Clean separation of concerns with services, models, and routes
- **Database Integration**: Supabase PostgreSQL for persistent storage
- **Dual Interface**: Both web UI and REST API available
- **Production Ready**: Comprehensive error handling, logging, and validation

### **Advanced Features**

- **Correction History**: View, manage, and delete past corrections
- **Export Capabilities**: Easy copying and sharing of corrected text
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## Prerequisites

### System Requirements

- **Python**: 3.12 or higher
- **GPU**: CUDA-compatible GPU (optional, but recommended for better performance)
- **UV** package manager (recommended) or pip

### Hardware Recommendations

**Minimum:**

- CPU: 4 cores
- RAM: 8GB
- Storage: 5GB free space

**Recommended:**

- CPU: 8+ cores
- RAM: 16GB+
- GPU: NVIDIA RTX 2060 or better with 6GB+ VRAM
- Storage: 10GB+ free space (SSD recommended)

## Database Setup (Supabase Cloud)

We'll use Supabase's free tier which is perfect for hobby projects and provides:

- 500MB database storage
- 2GB bandwidth per month
- 50MB file storage
- Up to 50,000 monthly active users
- Community support

### 1. Create Supabase Account & Project

1. **Sign Up**

   - Visit [supabase.com](https://supabase.com)
   - Click "Start your project"
   - Sign up with GitHub, Google, or email

2. **Create New Project**

   - Click "New Project"
   - Choose your organization (or create one)
   - Fill in project details:
     - **Name**: `Arabic-GEC` (or your preferred name)
     - **Database Password**: Generate a strong password (save it!)
     - **Region**: Choose closest to your location
     - **Plan**: Free tier (automatically selected)
   - Click "Create new project"

3. **Wait for Setup**

### 2. Get Your Credentials

Once your project is ready:

1. **Go to Project Settings**

   - Click the gear icon in the sidebar
   - Navigate to "API" section

2. **Copy Your Credentials**

   ```
   Project URL: https://your-project-ref.supabase.co
   anon (public) key: eyJhbGci...your-anon-key
   service_role key: eyJhbGci...your-service-role-key  # Keep this secret!
   ```

   **Important**: Use the **anon key** for this application, not the service_role key.

### 3. Create Database Schema

1. **Open SQL Editor**

   - In your Supabase dashboard, click "SQL Editor" in the sidebar
   - Click "New query"

2. **Run Schema Creation**

   Copy and paste this SQL code:

   ```sql
   -- Create corrections table
   CREATE TABLE corrections (
     id BIGSERIAL PRIMARY KEY,
     original_text TEXT NOT NULL,
     corrected_text TEXT NOT NULL,
     created_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- Create an index for better performance
   CREATE INDEX corrections_created_at_idx ON corrections(created_at DESC);
   ```

3. **Execute the Query**
   - Click "RUN" button
   - You should see "Success. No rows returned" message

### 4. Verify Setup

1. **Check Table Creation**

   - Go to "Table Editor" in the sidebar
   - You should see your `corrections` table
   - Click on it to view the structure and sample data

2. **Test Connection**
   - The table should have columns: `id`, `original_text`, `corrected_text`, `created_at`
   - Sample rows should be visible if you added them

## Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/Ahmedelshinnawi/Arabic-GEC.git
cd GEC
```

### 2. Install Python Dependencies

```bash
# Using UV (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root using your Supabase credentials:

```env
# Supabase Configuration (from your project dashboard)
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-key-from-dashboard

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Model Configuration
MODEL_NAME=alnnahwi/gemma-3-1b-arabic-gec-v1
MAX_TEXT_LENGTH=5000
```

### 4. Run the Application

```bash
# Using the runner script
python run.py

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## Web Interface

The application provides a modern, user-friendly web interface:

### Main Features

- **Home Page** (`/`): Text input form with real-time character counting
- **Correction Results** (`/correct`): Side-by-side comparison of original vs corrected text
- **History Page** (`/history`): Browse, search, and manage all past corrections
- **Responsive Design**: Optimized for all screen sizes and devices

### Modern UI Elements

- **Dark Theme**: Elegant glassmorphism design with smooth transitions
- **RTL Layout**: Proper Arabic text direction and layout
- **Interactive Elements**: Hover effects, loading states, and visual feedback
- **Accessibility**: Keyboard navigation and screen reader support

## API Endpoints

The REST API provides programmatic access to all functionality:

### Health Check

```http
GET /api/health
```

Returns the current status of the API and model loading state.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-01-08T12:00:00",
  "model_loaded": true
}
```

### Create Text Correction

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

## Architecture

### Project Structure

```
GEC/
├── app/                               # Main application package
│   ├── main.py                        # FastAPI application entry point
│   ├── config.py                      # Configuration management
│   ├── database.py                    # Supabase client setup
│   │
│   ├── models/                        # Data models
│   │   └── schema.py                  # Pydantic schemas
│   │
│   ├── services/                      # Business logic
│   │   ├── correction_service.py      # AI model handling
│   │   └── database_service.py        # Database operations
│   │
│   ├── api/                          # REST API routes
│   │   ├── __init__.py
│   │   └── routes.py                 # API endpoints
│   │
│   ├── web/                          # Web interface routes
│   │   └── routes.py                 # Web page handlers
│   │
│   └── templates/                    # Jinja2 templates
│       ├── base.html                 # Base template
│       ├── index.html                # Home page
│       ├── correction.html           # Correction results
│       └── history.html              # Correction history
│
├── static/                           # Static assets
│   ├── css/
│   │   └── style.css                # Modern dark theme styles
│   └── js/
│       └── main.js                  # Frontend JavaScript
│
│
├── .env                            # Environment variables
├── run.py                           # Application runner
├── pyproject.toml                   # Project dependencies
├── uv.lock                          # Dependency lock file
└── README.md                        # This documentation
```

### Key Components

#### **Core Application (`app/main.py`)**

- FastAPI application setup and configuration
- Router integration (API + Web)
- Static file serving
- Application lifecycle management
- CORS and middleware configuration

#### **Configuration (`app/config.py`)**

- Environment variable management
- Pydantic Settings for type safety
- Development/Production configuration
- Database and model settings

#### **Database Layer (`app/database.py` + `app/services/database_service.py`)**

- Supabase client initialization
- CRUD operations for corrections
- Database connection management
- Error handling and retries

#### **AI Service (`app/services/correction_service.py`)**

- Hugging Face Transformers integration
- GPU/CPU device management
- Model loading and optimization
- Text correction logic with fallbacks

#### **Data Models (`app/models/schema.py`)**

- Pydantic models for request/response validation
- Type safety and automatic documentation
- Input validation and sanitization

#### **API Layer (`app/api/routes.py`)**

- RESTful API endpoints
- JSON request/response handling
- HTTP status codes and error handling
- API documentation and validation

#### **Web Interface (`app/web/routes.py` + `app/templates/`)**

- Jinja2 template rendering
- Form handling and validation
- Session management
- User-friendly error pages

#### **Frontend Assets (`static/`)**

- Modern CSS with dark theme
- Responsive design components
- JavaScript for interactivity
- RTL support for Arabic text

### GPU Optimization

The application includes specific optimizations for various GPU configurations:

- **Float16 Precision**: Memory-efficient computation for modern GPUs
- **Flash Attention Disabled**: Compatibility with RTX 2060 and similar cards
- **Conservative Token Limits**: Prevents CUDA out-of-memory errors
- **CPU Fallback**: Automatic graceful degradation for stability
- **Device Auto-detection**: Supports CUDA, MPS (Apple Silicon), and CPU

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/feature_name`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/feature_name`)
5. Open a Pull Request

### Code Style Guidelines

- **Python**: Follow PEP 8, use type hints, write docstrings
- **JavaScript**: Use modern ES6+ features, comment complex logic
- **CSS**: Use consistent naming, leverage CSS variables
- **HTML**: Semantic markup, accessibility considerations

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

You are free to use, modify, and distribute this software for any purpose, including commercial use.

## Acknowledgments

### Core Technologies

- **AI Model**: [alnnahwi/gemma-3-1b-arabic-gec-v1](https://huggingface.co/alnnahwi/gemma-3-1b-arabic-gec-v1) - Fine-tuned Gemma model for Arabic GEC
- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for Python
- **Database**: [Supabase](https://supabase.com/) - Open-source Firebase alternative
- **ML Library**: [Hugging Face Transformers](https://huggingface.co/transformers/) - State-of-the-art NLP models
- **Package Manager**: [UV](https://docs.astral.sh/uv/) - Fast Python package manager

### UI & Design

- **CSS Framework**: [Bootstrap 5](https://getbootstrap.com/) - Responsive web components
- **Typography**: [Cairo Font](https://fonts.google.com/specimen/Cairo) - Beautiful Arabic typography
- **Icons**: Modern emoji icons for enhanced UX

### Development Tools

- **Code Quality**: Black, Ruff, MyPy, isort
- **Type Checking**: Pydantic for runtime validation

### About This Project

This application demonstrates modern full-stack development with:

- **Clean Architecture**: Separation of concerns and modular design
- **Modern UI/UX**: Dark theme with glassmorphism and smooth animations
- **Type Safety**: Full TypeScript-like safety in Python with Pydantic
- **Production Ready**: Comprehensive error handling, logging, and monitoring
- **Developer Experience**: Hot reload, comprehensive documentation, easy setup

**Perfect for**: Arabic language processing, educational tools, content creation, and accessibility applications.

---

**Note**: This application is specifically optimized for Arabic text correction and may not work optimally with other languages. The AI model is trained specifically on Arabic grammar patterns and linguistic rules.
