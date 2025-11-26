# Smart Resume Parser

An intelligent resume parsing application that extracts structured information from PDF resumes using both traditional pattern matching and AI-powered LLM extraction.

## Key Features

- **One-command Docker setup** - Automatic model download and configuration
- PDF resume upload and parsing
- Dual parsing methods:
  - **Regex-based**: Fast pattern matching for standard resume formats
  - **LLM-based**: AI-powered extraction using Ollama for complex or non-standard resumes
- Automatic extraction of:
  - Contact information (name, email, phone, location, LinkedIn, etc.)
  - Education history (degrees, institutions, dates, GPA)
  - Work experience (companies, positions, dates, descriptions)
  - Skills and technologies
- Real-time parsing with progress indicators
- Interactive PDF viewer
- Confidence scoring for extracted data
- RESTful API with automatic documentation

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Python 3.11+**: Core language
- **uv**: Fast Python package manager
- **Ollama**: Local LLM inference (gemma3:4b model)
- **Kreuzberg**: PDF parsing library
- **Pydantic**: Data validation and settings

### Frontend
- **React 19**: UI framework
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **react-pdf**: PDF rendering
- **Lucide React**: Icon library

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## Prerequisites

### For Docker Setup (Recommended)
- Docker Desktop (includes Docker and Docker Compose)
- At least 8GB RAM available for Docker
- 10GB free disk space (for models)

### For Local Development
- Python 3.11 or higher
- Node.js 18+ and npm/yarn
- Ollama installed locally
- Git

## Quick Start

### Option 1: Docker (Recommended)

The fastest way to get started is using Docker:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "document extracter"
   ```

2. **Create environment file** (optional)
   ```bash
   cp .env.example .env
   # Edit .env if you want to customize settings
   ```

3. **Start Ollama service**
   ```bash
   docker compose -f docker-compose.ollama.yml up -d
   ```

   **Note:** The gemma3:4b model (~3.3GB) will be automatically downloaded on first startup. This may take several minutes depending on your internet connection.

   Monitor the download progress:
   ```bash
   docker compose -f docker-compose.ollama.yml logs -f
   ```

   Wait for the message: "Ollama initialization complete!"

4. **Start the application**
   ```bash
   docker compose up --build
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Ollama API: http://localhost:11434

**Note:** Use `docker compose` (two words) not `docker-compose` (hyphenated). The hyphenated version is deprecated.

For detailed Docker instructions, see [DOCKER_README.md](./DOCKER_README.md).

### Option 2: Local Development

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Install dependencies using uv**
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. **Set up environment variables**
   ```bash
   cp ../.env.example .env
   # Edit .env if needed
   ```

4. **Start Ollama**
   ```bash
   # Install Ollama from https://ollama.ai
   ollama serve

   # In a new terminal, pull the model
   ollama pull gemma3:4b
   ```

5. **Run the backend server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure API URL**
   ```bash
   # Create .env.local file
   echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/docs

## Project Structure

```
document-extracter/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints and routes
│   │   │   ├── resume.py     # Resume parsing endpoints
│   │   │   ├── health.py     # Health check endpoints
│   │   │   └── router.py     # Main API router
│   │   ├── models/           # Pydantic models
│   │   │   ├── resume.py     # Resume data models
│   │   │   └── extraction.py # Extraction models
│   │   ├── services/         # Business logic
│   │   │   ├── pdf_parser.py           # PDF text extraction
│   │   │   ├── extraction_pipeline.py  # Main extraction pipeline
│   │   │   ├── contact_extractor.py    # Contact info extraction
│   │   │   ├── education_extractor.py  # Education extraction
│   │   │   ├── experience_extractor.py # Work experience extraction
│   │   │   ├── skills_extractor.py     # Skills extraction
│   │   │   ├── section_detector.py     # Resume section detection
│   │   │   └── nlp_service.py          # LLM integration
│   │   ├── utils/            # Utility functions
│   │   │   ├── exceptions.py   # Custom exceptions
│   │   │   ├── text_utils.py   # Text processing utilities
│   │   │   ├── date_utils.py   # Date parsing utilities
│   │   │   └── patterns.py     # Regex patterns
│   │   ├── config.py         # Application configuration
│   │   └── main.py           # FastAPI application entry
│   └── pyproject.toml        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── App.jsx           # Main application component
│   │   └── main.jsx          # Application entry point
│   ├── public/               # Static assets
│   └── package.json          # Node dependencies
├── docker-compose.yml        # Main Docker Compose config
├── docker-compose.ollama.yml # Ollama Docker Compose config
├── .env.example              # Environment variables template
├── DOCKER_README.md          # Docker setup guide
├── OLLAMA_SETUP.md           # Ollama setup guide
└── README.md                 # This file
```

## Configuration

The application can be configured using environment variables. Copy `.env.example` to `.env` and customize as needed:

### Backend Configuration
```bash
# Debug and Logging
DEBUG=True
LOG_LEVEL=INFO
API_PREFIX=/api/v1

# LLM Configuration
LLM_BASE_URL=http://localhost:11434    # Ollama server URL
LLM_MODEL_NAME=gemma3:4b               # Model to use
LLM_TIMEOUT=60                         # Request timeout (seconds)
LLM_TEMPERATURE=0.1                    # Model temperature

# File Upload Limits
MAX_FILE_SIZE_MB=10                    # Maximum file size
MAX_PAGES=5                            # Maximum pages to process
```

### Frontend Configuration
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

## Usage

### Parsing a Resume

1. Open the application in your browser (http://localhost:5173)
2. Click "Choose File" or drag and drop a PDF resume
3. Select parsing method:
   - **Regex**: Fast, works well for standard resume formats
   - **LLM**: More accurate, handles non-standard formats (requires Ollama)
4. Click "Parse Resume"
5. View extracted information on the right panel
6. Review the original PDF on the left

### Using the API

The API is available at `http://localhost:8000/api/v1`

#### Parse Resume
```bash
curl -X POST "http://localhost:8000/api/v1/resume/parse" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/resume.pdf" \
  -F "use_llm=true"
```

#### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

### Running Tests

Backend tests:
```bash
cd backend
pytest
```

Frontend tests:
```bash
cd frontend
npm test
```

### Code Formatting

Backend:
```bash
cd backend
black .
ruff check .
```

Frontend:
```bash
cd frontend
npm run lint
```

### Building for Production

Backend:
```bash
cd backend
uv pip install -e .
```

Frontend:
```bash
cd frontend
npm run build
```

## Troubleshooting

### Common Issues

#### LLM parsing is slow or times out
- Increase the `LLM_TIMEOUT` value in `.env`
- Consider using a smaller model or the regex method for faster results
- Ensure your machine has enough RAM (8GB+ recommended)

#### Ollama connection errors
- Verify Ollama container is running: `docker ps | grep ollama`
- Check container logs: `docker compose -f docker-compose.ollama.yml logs -f`
- Check Ollama is accessible: `curl http://localhost:11434/api/tags`
- Verify the model is downloaded: `docker exec ollama-standalone ollama list` should show gemma3:4b
- If model is missing, restart: `docker compose -f docker-compose.ollama.yml restart`

#### Model download issues
If the automatic model download fails or is interrupted:

1. **Check the download progress:**
   ```bash
   docker compose -f docker-compose.ollama.yml logs -f
   ```

2. **Restart the container to retry download:**
   ```bash
   docker compose -f docker-compose.ollama.yml restart
   ```

3. **For a clean restart, remove the volume and start fresh:**
   ```bash
   docker compose -f docker-compose.ollama.yml down -v
   docker compose -f docker-compose.ollama.yml up -d
   ```
   Note: This will re-download the entire model (~3.3GB)

4. **Manual model pull (if automatic fails):**
   ```bash
   docker exec -it ollama-standalone ollama pull gemma3:4b
   ```

#### PDF parsing errors
- Ensure the PDF is not password-protected
- Check file size is within limits (MAX_FILE_SIZE_MB)
- Verify the PDF contains extractable text (not scanned images)

#### Port already in use
- Change ports in `docker-compose.yml` or stop conflicting services
- Default ports: 5173 (frontend), 8000 (backend), 11434 (Ollama)

### Getting Help

For more detailed troubleshooting:
- Docker issues: See [DOCKER_README.md](./DOCKER_README.md)
- Ollama setup: See [OLLAMA_SETUP.md](./OLLAMA_SETUP.md)
- Technical details: See [TECHNICAL_BLUEPRINT.md](./TECHNICAL_BLUEPRINT.md)

## Architecture

The application follows a clean architecture pattern:

1. **API Layer** (`app/api/`): Handles HTTP requests and responses
2. **Service Layer** (`app/services/`): Contains business logic
3. **Model Layer** (`app/models/`): Defines data structures
4. **Utils Layer** (`app/utils/`): Shared utilities and helpers

### Parsing Pipeline

1. **PDF Upload**: Frontend sends PDF to backend
2. **Text Extraction**: PDF is converted to plain text
3. **Section Detection**: Resume is split into sections (contact, education, experience, skills)
4. **Information Extraction**:
   - **Regex Method**: Pattern matching for standard formats
   - **LLM Method**: AI-powered extraction using Ollama
5. **Confidence Scoring**: Each extracted field receives a confidence score
6. **Response**: Structured JSON data returned to frontend

## Performance

### Benchmarks (Average)
- **Regex parsing**: 1-3 seconds
- **LLM parsing**: 15-30 seconds (depends on resume complexity and hardware)
- **PDF processing**: 1-2 seconds

### Resource Usage
- **Backend**: ~200MB RAM (idle), ~500MB (processing)
- **Frontend**: ~100MB RAM
- **Ollama**: ~4GB RAM (with gemma3:4b model loaded)

## Security Considerations

- File upload validation (size, type, content)
- CORS configuration for API access
- No sensitive data persistence (files processed in memory)
- Input sanitization for all extracted text
- Rate limiting recommended for production

## Roadmap

- [ ] Support for additional document formats (DOCX, TXT)
- [ ] Batch processing for multiple resumes
- [ ] Resume comparison and ranking
- [ ] Export to various formats (JSON, CSV, Excel)
- [ ] User authentication and saved parses
- [ ] Advanced search and filtering
- [ ] Resume quality scoring
- [ ] Integration with ATS systems

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - Frontend library
- [Ollama](https://ollama.ai/) - Local LLM inference
- [Vite](https://vitejs.dev/) - Next generation frontend tooling
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
