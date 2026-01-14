import React, { useState, useEffect, useRef } from 'react';
import ProcessingStepper from './ProcessingStepper';

interface Step {
  name: string;
  status: 'pending' | 'processing' | 'complete' | 'error';
  progress: number;
  result?: any;
  error?: string;
}

interface UploadSectionProps {
  onUploadComplete?: (result: any) => void;
}

const UploadSection: React.FC<UploadSectionProps> = ({ onUploadComplete }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [steps, setSteps] = useState<Step[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [overallProgress, setOverallProgress] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const sessionIdRef = useRef<string>('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const connectWebSocket = (sessionId: string) => {
    const ws = new WebSocket(`ws://localhost:8000/api/ws/${sessionId}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'progress') {
        setSteps(data.steps);
        setCurrentStep(data.current_step);
        setOverallProgress(data.overall_progress);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
    
    wsRef.current = ws;
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setProcessing(true);
    setError(null);
    
    // Generate session ID for WebSocket
    const sessionId = `session_${Date.now()}`;
    sessionIdRef.current = sessionId;
    
    // Connect WebSocket for real-time updates
    connectWebSocket(sessionId);
    
    // Initialize steps
    setSteps([
      { name: 'Vision Agent', status: 'pending', progress: 0 },
      { name: 'NLP Agent', status: 'pending', progress: 0 },
      { name: 'Fraud Agent', status: 'pending', progress: 0 },
      { name: 'Policy Agent', status: 'pending', progress: 0 },
      { name: 'Decision Agent', status: 'pending', progress: 0 },
    ]);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`http://localhost:8000/api/upload?session_id=${sessionId}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
      
      if (onUploadComplete) {
        onUploadComplete(data);
      }
      
      // Close WebSocket after completion
      setTimeout(() => {
        if (wsRef.current) {
          wsRef.current.close();
        }
      }, 1000);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
      setTimeout(() => setProcessing(false), 2000); // Keep showing completion for 2s
    }
  };

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Upload Form */}
      {!processing && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Upload Invoice</h2>
          
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
              <input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.jpg,.jpeg,.png"
                className="hidden"
                id="file-upload"
                disabled={uploading}
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center"
              >
                <svg
                  className="w-16 h-16 text-gray-400 mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                <span className="text-lg text-gray-600">
                  {file ? file.name : 'Click to select invoice file'}
                </span>
                <span className="text-sm text-gray-400 mt-2">
                  PDF, JPG, or PNG (max 10MB)
                </span>
              </label>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-700">{error}</p>
              </div>
            )}

            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-colors ${
                !file || uploading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {uploading ? 'Processing...' : 'Upload and Process'}
            </button>
          </div>
        </div>
      )}

      {/* Processing Stepper */}
      {processing && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <ProcessingStepper
            steps={steps}
            currentStep={currentStep}
            overallProgress={overallProgress}
          />
        </div>
      )}

      {/* Final Result */}
      {result && !processing && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-2xl font-bold mb-4">
            Processing Complete
          </h3>
          <div className={`p-6 rounded-lg border-2 ${
            result.decision === 'APPROVE' ? 'bg-green-50 border-green-500' :
            result.decision === 'REJECT' ? 'bg-red-50 border-red-500' :
            'bg-orange-50 border-orange-500'
          }`}>
            <p className="text-3xl font-bold mb-2">
              {result.decision === 'APPROVE' ? '✓ APPROVED' :
               result.decision === 'REJECT' ? '✗ REJECTED' :
               '⚠ ON HOLD'}
            </p>
            <p className="text-lg text-gray-700">
              Invoice ID: {result.invoice_id}
            </p>
            <button
              onClick={() => {
                setResult(null);
                setFile(null);
                setSteps([]);
                setCurrentStep(0);
                setOverallProgress(0);
              }}
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Process Another Invoice
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadSection;
