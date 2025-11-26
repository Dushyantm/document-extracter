import { useState } from 'react';
import { Upload, FileText, Settings, ChevronDown, ChevronUp } from 'lucide-react';

export default function UploadZone({ onFileSelect, isLoading, parsingMethod, setParsingMethod }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type === 'application/pdf') {
      onFileSelect(files[0]);
    }
  };

  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="w-full max-w-2xl p-8">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <FileText className="w-12 h-12 text-blue-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Smart Resume Parser
          </h1>
          <p className="text-gray-600">
            Upload your resume to automatically extract and populate form fields
          </p>
        </div>

        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            border-3 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer
            ${isDragging
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 bg-white hover:border-blue-400 hover:bg-blue-50/50'
            }
            ${isLoading ? 'opacity-50 pointer-events-none' : ''}
          `}
        >
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileInput}
            className="hidden"
            id="file-upload"
            disabled={isLoading}
          />

          <label htmlFor="file-upload" className="cursor-pointer">
            <div className="flex flex-col items-center">
              <div className={`
                w-20 h-20 rounded-full flex items-center justify-center mb-4
                ${isDragging ? 'bg-blue-100' : 'bg-gray-100'}
              `}>
                <Upload className={`w-10 h-10 ${isDragging ? 'text-blue-600' : 'text-gray-400'}`} />
              </div>

              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {isLoading ? 'Processing...' : 'Drop your resume here'}
              </h3>

              <p className="text-gray-500 mb-4">
                or click to browse
              </p>

              <p className="text-sm text-gray-400">
                Supports PDF files up to 10MB
              </p>
            </div>
          </label>
        </div>

        {/* Collapsible Settings Section */}
        <div className="mt-6">
          <button
            onClick={() => setIsSettingsOpen(!isSettingsOpen)}
            disabled={isLoading}
            className="flex items-center gap-2 text-gray-700 hover:text-gray-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mx-auto"
          >
            <Settings className="w-4 h-4" />
            <span className="text-sm font-medium">Settings</span>
            {isSettingsOpen ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>

          {isSettingsOpen && (
            <div className="mt-3 bg-white rounded-lg border border-gray-200 p-3 shadow-sm transition-all duration-200 ease-in-out max-w-xs mx-auto">
              <select
                id="parsing-method"
                value={parsingMethod}
                onChange={(e) => setParsingMethod(e.target.value)}
                disabled={isLoading}
                className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-transparent bg-white disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="regex">Regex (Fast)</option>
                <option value="llm">LLM (Slower)</option>
              </select>
            </div>
          )}
        </div>

        <div className="mt-4 text-center text-sm text-gray-500">
          <p>Your data is processed securely and never stored</p>
        </div>
      </div>
    </div>
  );
}
