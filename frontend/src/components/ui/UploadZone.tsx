import React, { useCallback, useState } from 'react';
import { Upload, AlertCircle, Loader2 } from 'lucide-react';
import { uploadInvoice } from '../../services/api';
import clsx from 'clsx'; // Assuming clsx is installed, or use standard string interpolation

interface UploadZoneProps {
    onUploadComplete?: (data: any) => void;
}

const UploadZone: React.FC<UploadZoneProps> = ({ onUploadComplete }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = useCallback(async (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        setError(null);

        const files = e.dataTransfer.files;
        if (files.length === 0) return;

        const file = files[0];
        if (file.type !== 'application/pdf' && !file.type.startsWith('image/')) {
            setError('Please upload a PDF or Image file.');
            return;
        }

        await processUpload(file);
    }, []);

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setError(null);
            await processUpload(e.target.files[0]);
        }
    };

    const processUpload = async (file: File) => {
        setIsUploading(true);
        try {
            const result = await uploadInvoice(file);
            console.log('Upload result:', result);
            if (onUploadComplete) {
                onUploadComplete(result);
            }
        } catch (err: any) {
            console.error(err);
            setError('Failed to upload invoice. Is the backend running?');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div
            className={clsx(
                "border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer",
                isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400",
                isUploading ? "opacity-50 pointer-events-none" : ""
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-upload')?.click()}
        >
            <input
                type="file"
                id="file-upload"
                className="hidden"
                accept="application/pdf,image/*"
                onChange={handleFileSelect}
            />

            <div className="flex flex-col items-center justify-center space-y-4">
                {isUploading ? (
                    <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
                ) : (
                    <Upload className="w-12 h-12 text-gray-400" />
                )}

                <div className="text-lg font-medium text-gray-700">
                    {isUploading ? "Agents are processing..." : "Drop your invoice here"}
                </div>

                <p className="text-sm text-gray-500">
                    Supports PDF, JPG, PNG
                </p>

                {error && (
                    <div className="flex items-center space-x-2 text-red-500 mt-4">
                        <AlertCircle className="w-4 h-4" />
                        <span>{error}</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default UploadZone;
