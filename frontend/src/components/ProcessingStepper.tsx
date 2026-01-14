import React from 'react';
import { CheckCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';

interface Step {
  name: string;
  status: 'pending' | 'processing' | 'complete' | 'error';
  progress: number;
  result?: any;
  error?: string;
}

interface ProcessingStepperProps {
  steps: Step[];
  currentStep: number;
  overallProgress: number;
}

const ProcessingStepper: React.FC<ProcessingStepperProps> = ({
  steps,
  currentStep,
  overallProgress
}) => {
  const getStepIcon = (step: Step, index: number) => {
    if (step.status === 'complete') {
      return <CheckCircle className="w-8 h-8 text-green-500" />;
    } else if (step.status === 'processing') {
      return <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />;
    } else if (step.status === 'error') {
      return <AlertCircle className="w-8 h-8 text-red-500" />;
    } else {
      return <Clock className="w-8 h-8 text-gray-300" />;
    }
  };

  const getStepColor = (step: Step) => {
    if (step.status === 'complete') return 'border-green-500 bg-green-50';
    if (step.status === 'processing') return 'border-blue-500 bg-blue-50';
    if (step.status === 'error') return 'border-red-500 bg-red-50';
    return 'border-gray-300 bg-gray-50';
  };

  const getConnectorColor = (index: number) => {
    if (index < currentStep) return 'bg-green-500';
    if (index === currentStep) return 'bg-blue-500';
    return 'bg-gray-300';
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      {/* Overall Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-semibold text-gray-700">Processing Invoice</h3>
          <span className="text-sm font-medium text-gray-600">{Math.round(overallProgress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${overallProgress}%` }}
          />
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-4">
        {steps.map((step, index) => (
          <div key={index} className="relative">
            {/* Connector Line */}
            {index < steps.length - 1 && (
              <div
                className={`absolute left-8 top-16 w-1 h-12 ${getConnectorColor(index)} transition-colors duration-300`}
              />
            )}

            {/* Step Card */}
            <div
              className={`flex items-start gap-4 p-4 rounded-lg border-2 transition-all duration-300 ${getStepColor(step)}`}
            >
              {/* Icon */}
              <div className="flex-shrink-0 mt-1">
                {getStepIcon(step, index)}
              </div>

              {/* Content */}
              <div className="flex-grow">
                <div className="flex items-center justify-between">
                  <h4 className="text-lg font-semibold text-gray-800">{step.name}</h4>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      step.status === 'complete'
                        ? 'bg-green-100 text-green-800'
                        : step.status === 'processing'
                        ? 'bg-blue-100 text-blue-800'
                        : step.status === 'error'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {step.status.charAt(0).toUpperCase() + step.status.slice(1)}
                  </span>
                </div>

                {/* Progress Bar for Current Step */}
                {step.status === 'processing' && (
                  <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${step.progress}%` }}
                    />
                  </div>
                )}

                {/* Result Data */}
                {step.status === 'complete' && step.result && (
                  <div className="mt-2 text-sm text-gray-600">
                    {step.name === 'Vision Agent' && (
                      <div className="space-y-1">
                        <p>✓ Extracted {step.result.text_length} characters</p>
                        <p>✓ Confidence: {(step.result.confidence * 100).toFixed(0)}%</p>
                      </div>
                    )}
                    {step.name === 'NLP Agent' && (
                      <div className="space-y-1">
                        <p>✓ Invoice: {step.result.invoice_number}</p>
                        <p>✓ Vendor: {step.result.vendor}</p>
                        <p>✓ Amount: ${step.result.amount?.toFixed(2)}</p>
                      </div>
                    )}
                    {step.name === 'Fraud Agent' && (
                      <div className="space-y-1">
                        <p className={step.result.is_suspicious ? 'text-red-600' : 'text-green-600'}>
                          {step.result.is_suspicious ? '⚠' : '✓'} Risk Level: {step.result.risk_level}
                        </p>
                        <p>Risk Score: {(step.result.risk_score * 100).toFixed(0)}%</p>
                        {step.result.flags_count > 0 && (
                          <p className="text-orange-600">⚠ {step.result.flags_count} flag(s) detected</p>
                        )}
                      </div>
                    )}
                    {step.name === 'Policy Agent' && (
                      <div className="space-y-1">
                        <p className={step.result.compliant ? 'text-green-600' : 'text-red-600'}>
                          {step.result.compliant ? '✓' : '✗'} {step.result.compliant ? 'Compliant' : 'Non-compliant'}
                        </p>
                        <p>Approval: {step.result.approval_level?.replace('_', ' ')}</p>
                        {step.result.violations_count > 0 && (
                          <p className="text-red-600">✗ {step.result.violations_count} violation(s)</p>
                        )}
                      </div>
                    )}
                    {step.name === 'Decision Agent' && (
                      <div className="space-y-1">
                        <p className={`font-bold ${
                          step.result.decision === 'APPROVE' ? 'text-green-600' :
                          step.result.decision === 'REJECT' ? 'text-red-600' :
                          'text-orange-600'
                        }`}>
                          {step.result.decision === 'APPROVE' ? '✓' :
                           step.result.decision === 'REJECT' ? '✗' : '⚠'} {step.result.decision}
                        </p>
                        <p>Confidence: {(step.result.confidence * 100).toFixed(0)}%</p>
                        <p className="text-xs text-gray-500 mt-1">{step.result.reason}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Error Message */}
                {step.status === 'error' && step.error && (
                  <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                    <p className="font-semibold">Error:</p>
                    <p>{step.error}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProcessingStepper;
