import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import UploadSection from './components/UploadSection';
import { FileUp, BarChart3 } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState<'upload' | 'dashboard'>('upload');

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">InvoiceFlow AI</h1>
              <p className="text-sm text-gray-600">Multi-Agent Invoice Processing System</p>
            </div>
            
            {/* Navigation Tabs */}
            <nav className="flex gap-2">
              <button
                onClick={() => setActiveTab('upload')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'upload'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <FileUp className="w-5 h-5" />
                Upload
              </button>
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'dashboard'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <BarChart3 className="w-5 h-5" />
                Dashboard
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8">
        {activeTab === 'upload' ? (
          <UploadSection onUploadComplete={() => setActiveTab('dashboard')} />
        ) : (
          <Dashboard />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-4 text-center text-sm text-gray-600">
          <p>
            Powered by Vision Agent, NLP Agent, Fraud Agent, Policy Agent & Decision Agent
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
