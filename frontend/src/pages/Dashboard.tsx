import React, { useState } from 'react';
import UploadZone from '../components/ui/UploadZone';
import InvoiceResult from '../components/ui/InvoiceResult';

const Dashboard: React.FC = () => {
    const [result, setResult] = useState<any>(null);

    const handleUploadComplete = (data: any) => {
        setResult(data);
    };

    return (
        <div className="max-w-5xl mx-auto px-4 py-12">
            <header className="mb-12 text-center">
                <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-4">
                    InvoiceFlow <span className="text-blue-600">AI</span>
                </h1>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                    Enterprise-grade invoice processing powered by multi-agent collaboration.
                    Upload an invoice to see the agents in action.
                </p>
            </header>

            <div className="bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
                <UploadZone onUploadComplete={handleUploadComplete} />
            </div>

            {result && (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
                    <InvoiceResult data={result} />
                </div>
            )}
        </div>
    );
};

export default Dashboard;
