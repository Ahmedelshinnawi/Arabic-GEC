# Arabic Text Correction API (GEC)

A FastAPI-based web service for correcting Arabic text using AI-powered Grammar Error Correction (GEC) models. This API leverages the `alnnahwi/gemma-3-1b-arabic-gec-v1` model to automatically detect and correct grammatical errors in Arabic text.

## Features

- **AI-Powered Correction**: Uses a fine-tuned Gemma model specifically trained for Arabic grammar error correction
- **RESTful API**: Clean and well-documented API endpoints with automatic OpenAPI documentation
- **Multi-Device Support**: Automatically detects and utilizes available hardware (CUDA, MPS, or CPU)
- **Robust Error Handling**: Comprehensive error handling with fallback mechanisms
- **Request History**: Stores and manages correction history with CRUD operations
- **GPU Optimization**: Optimized for RTX 2060 and similar GPUs with stability enhancements
- **Production Ready**: Includes proper logging, validation, and error responses

## Quick Start

### Prerequisites

- Python 3.12 or higher
- CUDA-compatible GPU (optional, but recommended for better performance)
- UV package manager (recommended) or pip

### Installation

1. **Clone the repository**

   ```bash
   git clone <https://github.com/Ahmedelshinnawi/Arabic-GEC.git>
   cd GEC
   ```

2. **Install dependencies using UV (recommended)**

   ```bash
   uv sync
   ```

3. **Run the application**

   ```bash
   uvicorn main:app --reload

   # Or using Python directly
   python -m uvicorn main:app --reload
   ```

4. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## API Endpoints

### Health Check

```http
GET /health
```

Returns the current status of the API and model loading state.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "model_loaded": true
}
```

### Correct Arabic Text

```http
POST /gec/correct
```

Corrects grammatical errors in Arabic text.

**Request Body:**

```json
{
  "text": "كيف حالكي اليوم ؟"
}
```

**Response:**

```json
{
  "original_text": "كيف حالكي اليوم ؟",
  "corrected_text": "كيف حالك اليوم؟",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Get All Corrections

```http
GET /gec/all
```

Retrieves all previously corrected texts.

**Response:**

```json
[
  {
    "id": 1,
    "input text": "كيف حالكي اليوم ؟",
    "corrected text": "كيف حالك اليوم؟"
  }
]
```

### Delete Correction

```http
DELETE /gec/delete/{text_id}
```

Deletes a specific correction record by ID.

## Architecture

### Project Structure

```
GEC/
├── main.py                    # FastAPI application and API endpoints
├── extract_model_response.py  # Model initialization and text correction logic
├── logger.py                  # Custom logging configuration
├── outputs.json              # Correction history storage
├── pyproject.toml            # Project dependencies and configuration
├── uv.lock                   # Dependency lock file
└── README.md                 # This file
```

### Key Components

1. **FastAPI Application (`main.py`)**

   - REST API endpoints
   - Request/response models using Pydantic
   - Error handling and validation
   - Application lifecycle management

2. **Model Handler (`extract_model_response.py`)**

   - Hugging Face Transformers pipeline
   - GPU/CPU fallback mechanisms
   - Text preprocessing and postprocessing
   - Model response extraction

3. **Logger (`logger.py`)**
   - Centralized logging configuration
   - Structured log formatting

## Configuration

### GPU Optimization

The application includes specific optimizations for RTX 2060 and similar GPUs:

- Uses `float16` precision for memory efficiency
- Disables Flash Attention for compatibility
- Implements conservative token limits
- Includes CPU fallback for stability

## Development

### Development Dependencies

The project includes development tools configured in `pyproject.toml`:

- **MyPy**: Static type checking
- **Black**: Code formatting
- **Ruff**: Fast Python linter
- **isort**: Import sorting

### Setting up Development Environment

1. **Install development dependencies**

   ```bash
   uv sync
   ```

2. **Run code formatting**

   ```bash
   uv run black .
   uv run isort .
   ```

3. **Run linting**

   ```bash
   uv run ruff check .
   ```

## Performance

### Hardware Requirements

**Minimum:**

- CPU: 4 cores
- RAM: 8GB
- Storage: 5GB free space

**Recommended:**

- CPU: 8+ cores
- RAM: 16GB+
- GPU: NVIDIA RTX 2060 or better with 6GB+ VRAM
- Storage: 10GB+ free space (SSD recommended)

### Performance Metrics

- **Model Loading Time**: 30-60 seconds (depending on hardware)
- **Inference Time**:
  - GPU: 100-300ms per request
  - CPU: 1-3 seconds per request
- **Memory Usage**: 4-8GB (depending on device and batch size)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/feature_name`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/feture_name`)
5. Open a Pull Request

### Code Style Guidelines

- Follow PEP 8 style guidelines
- Use type hints for all functions
<!-- - Write descriptive docstrings
- Maintain test coverage above 80% -->

## Troubleshooting

### Common Issues

1. **Model Loading Fails**

   - Ensure you have sufficient RAM/VRAM
   - Check internet connection for model download
   - Try running with CPU-only mode

2. **CUDA Out of Memory**

   - Reduce batch size or max token length
   - Enable CPU fallback mode
   - Close other GPU-intensive applications

3. **Slow Performance**
   - Ensure GPU drivers are up to date
   - Check if CUDA is properly installed
   - Monitor system resources

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Model**: [alnnahwi/gemma-3-1b-arabic-gec-v1](https://huggingface.co/alnnahwi/gemma-3-1b-arabic-gec-v1)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ML Library**: [Hugging Face Transformers](https://huggingface.co/transformers/)
- **Package Manager**: [UV](https://docs.astral.sh/uv/)

**Note**: This API is designed for Arabic text correction and may not work optimally with other languages. The model is specifically trained on Arabic grammar patterns and corrections.
