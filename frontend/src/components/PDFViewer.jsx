import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut } from 'lucide-react';

// Set up the worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

export default function PDFViewer({ file }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.0);

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
  }

  const goToPrevPage = () => {
    setPageNumber((prev) => Math.max(prev - 1, 1));
  };

  const goToNextPage = () => {
    setPageNumber((prev) => Math.min(prev + 1, numPages));
  };

  const zoomIn = () => {
    setScale((prev) => Math.min(prev + 0.2, 2.0));
  };

  const zoomOut = () => {
    setScale((prev) => Math.max(prev - 0.2, 0.6));
  };

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="bg-black px-4 py-3 border-b border-gray-800">
        <h2 className="text-white font-semibold">Resume Preview</h2>
      </div>

      {/* PDF Display */}
      <div className="flex-1 overflow-auto bg-gray-800 p-4">
        <div className="flex justify-center">
          <Document
            file={file}
            onLoadSuccess={onDocumentLoadSuccess}
            className="shadow-2xl"
          >
            <Page
              pageNumber={pageNumber}
              scale={scale}
              className="border border-gray-700"
            />
          </Document>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-black px-4 py-3 border-t border-gray-800">
        <div className="flex items-center justify-between">
          {/* Page Navigation */}
          <div className="flex items-center gap-2">
            <button
              onClick={goToPrevPage}
              disabled={pageNumber <= 1}
              className="p-2 rounded hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed text-white"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="text-white text-sm">
              Page {pageNumber} of {numPages || '?'}
            </span>
            <button
              onClick={goToNextPage}
              disabled={pageNumber >= numPages}
              className="p-2 rounded hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed text-white"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          {/* Zoom Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={zoomOut}
              disabled={scale <= 0.6}
              className="p-2 rounded hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed text-white"
            >
              <ZoomOut className="w-5 h-5" />
            </button>
            <span className="text-white text-sm w-12 text-center">
              {Math.round(scale * 100)}%
            </span>
            <button
              onClick={zoomIn}
              disabled={scale >= 2.0}
              className="p-2 rounded hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed text-white"
            >
              <ZoomIn className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
