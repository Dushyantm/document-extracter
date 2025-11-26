# Smart Resume Parser - Frontend

A clean, modern React application for parsing PDF resumes and displaying extracted information in an editable form.

## Features

- 📄 **PDF Upload**: Drag-and-drop or click to upload resume PDFs
- 👁️ **PDF Viewer**: View your resume in the left panel with zoom and navigation controls
- 📝 **Editable Form**: Automatically populated form fields from extracted data
- 🎨 **Clean UI**: Black and blue accent theme with Tailwind CSS
- ⚡ **Real-time Processing**: Instant feedback with loading states

## Tech Stack

- **React 19** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **react-pdf** - PDF rendering
- **Axios** - HTTP client for API calls
- **Lucide React** - Beautiful icon library

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` if your backend is running on a different URL.

### Running the Application

Start the development server:
```bash
npm run dev
```

The application will open at `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` folder.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── UploadZone.jsx      # File upload component
│   │   ├── PDFViewer.jsx       # PDF display with controls
│   │   └── ResumeForm.jsx      # Editable form sections
│   ├── services/
│   │   └── api.js              # API communication
│   ├── App.jsx                 # Main application logic
│   ├── App.css                 # Minimal custom styles
│   ├── index.css               # Tailwind imports
│   └── main.jsx                # Application entry point
├── tailwind.config.js          # Tailwind configuration
└── vite.config.js              # Vite configuration
```

## API Integration

The frontend communicates with the backend via the `/api/v1/parse` endpoint:

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: PDF file

**Response:**
```json
{
  "contact": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "city": "San Francisco",
    "state": "CA"
  },
  "education": [...],
  "work_experience": [...],
  "skills": [...]
}
```

## Customization

### Theme Colors

Edit `tailwind.config.js` to customize the blue accent colors.

### API URL

Update `.env` to point to your backend:
```
VITE_API_URL=https://your-backend-url.com/api/v1
```
