import { useState } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import UploadZone from './components/UploadZone';
import PDFViewer from './components/PDFViewer';
import ResumeForm from './components/ResumeForm';
import { parseResume } from './services/api';
import { Loader2 } from 'lucide-react';

function App() {
  const [pdfFile, setPdfFile] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [parsingMethod, setParsingMethod] = useState('regex');

  const handleFileSelect = async (file) => {
    setPdfFile(file);
    setIsLoading(true);

    // Show loading toast with appropriate message
    const loadingMessage = parsingMethod === 'llm'
      ? 'Processing with AI... This may take a moment.'
      : 'Processing your resume...';
    const loadingToast = toast.loading(loadingMessage);

    try {
      const result = await parseResume(file, parsingMethod);
      setExtractedData(result);

      // Check if we got partial or empty data
      const hasContact = result.contact?.first_name || result.contact?.email || result.contact?.phone;
      const hasEducation = result.education?.length > 0;
      const hasExperience = result.work_experience?.length > 0;
      const hasSkills = result.skills?.length > 0;

      const extractedCount = [hasContact, hasEducation, hasExperience, hasSkills].filter(Boolean).length;

      if (extractedCount === 0) {
        // No data extracted at all
        toast(
          <div>
            <p className="font-semibold">No data extracted</p>
            <p className="text-sm mt-1">Please fill in the form manually</p>
          </div>,
          {
            id: loadingToast,
            duration: 4000,
            icon: '⚠️',
            style: {
              background: '#f59e0b',
              color: '#fff',
            },
          }
        );
      } else if (extractedCount < 3) {
        // Partial data extracted
        toast.success(
          <div>
            <p className="font-semibold">Partial data extracted</p>
            <p className="text-sm mt-1">Please review and fill in missing fields</p>
          </div>,
          {
            id: loadingToast,
            duration: 4000,
          }
        );
      } else {
        // Most/all data extracted successfully
        toast.success('Resume parsed successfully!', {
          id: loadingToast,
          duration: 3000,
        });
      }
    } catch (err) {
      // Show error toast with clear message
      const isValidationError = err.message.includes("doesn't appear to be a resume") ||
                                 err.message.includes("no extractable text");
      const isParsingFailure = err.message.includes("Failed to parse PDF") ||
                               err.message.includes("couldn't extract data");

      let errorTitle = 'PDF Parsing Failed';
      if (isValidationError) {
        errorTitle = 'Invalid Resume';
      } else if (isParsingFailure) {
        errorTitle = 'Extraction Failed';
      }

      toast.error(
        <div className="max-w-md">
          <p className="font-semibold">{errorTitle}</p>
          <p className="text-sm mt-1">{err.message}</p>
        </div>,
        {
          id: loadingToast,
          duration: 7000,
        }
      );

      setPdfFile(null);
      setExtractedData(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setPdfFile(null);
    setExtractedData(null);
    toast.success('Ready for new upload', { duration: 2000 });
  };

  // Show upload screen if no file is selected
  if (!pdfFile && !extractedData) {
    return (
      <>
        <Toaster
          position="top-center"
          toastOptions={{
            success: {
              style: {
                background: '#10b981',
                color: '#fff',
              },
              iconTheme: {
                primary: '#fff',
                secondary: '#10b981',
              },
            },
            error: {
              style: {
                background: '#ef4444',
                color: '#fff',
                maxWidth: '500px',
              },
              iconTheme: {
                primary: '#fff',
                secondary: '#ef4444',
              },
            },
            warning: {
              style: {
                background: '#f59e0b',
                color: '#fff',
                maxWidth: '500px',
              },
              iconTheme: {
                primary: '#fff',
                secondary: '#f59e0b',
              },
            },
            loading: {
              style: {
                background: '#3b82f6',
                color: '#fff',
              },
            },
          }}
        />
        <UploadZone
          onFileSelect={handleFileSelect}
          isLoading={isLoading}
          parsingMethod={parsingMethod}
          setParsingMethod={setParsingMethod}
        />
      </>
    );
  }

  // Show loading state
  if (isLoading) {
    return (
      <>
        <Toaster position="top-center" />
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
          <div className="text-center">
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {parsingMethod === 'llm' ? 'AI Processing Resume' : 'Processing Resume'}
            </h2>
            <p className="text-gray-600">
              {parsingMethod === 'llm'
                ? 'Using AI to extract information... This may take a minute.'
                : 'Extracting information from your PDF...'}
            </p>
          </div>
        </div>
      </>
    );
  }

  // Show main split view with PDF and Form
  return (
    <>
      <Toaster position="top-center" />
      <div className="h-screen flex flex-col">
        {/* Top Bar */}
        <div className="bg-black text-white px-6 py-3 flex items-center justify-between">
          <h1 className="text-xl font-bold">Smart Resume Parser</h1>
          <button
            onClick={handleReset}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
          >
            Upload New Resume
          </button>
        </div>

        {/* Split View */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Panel - PDF Viewer */}
          <div className="w-1/2 border-r border-gray-300">
            <PDFViewer file={pdfFile} />
          </div>

          {/* Right Panel - Form */}
          <div className="w-1/2">
            <ResumeForm data={extractedData} />
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
