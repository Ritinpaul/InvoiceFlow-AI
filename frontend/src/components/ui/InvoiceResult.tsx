import React from 'react';
import { Check, X, AlertTriangle, Shield, FileText, Brain } from 'lucide-react';
import clsx from 'clsx';

interface ResultProps {
    data: any;
}

const InvoiceResult: React.FC<ResultProps> = ({ data }) => {
    if (!data || !data.result) return null;

    const { extraction, fraud_check, policy_check, final_decision } = data.result;

    return (
        <div className="space-y-6 mt-8">
            {/* Header / Decision Badge */}
            <div className={clsx(
                "p-6 rounded-xl border-l-8 shadow-sm flex items-center justify-between",
                final_decision.decision === "APPROVE" ? "bg-green-50 border-green-500" : "bg-red-50 border-red-500"
            )}>
                <div>
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        {final_decision.decision === "APPROVE" ? (
                            <Check className="w-8 h-8 text-green-600" />
                        ) : (
                            <X className="w-8 h-8 text-red-600" />
                        )}
                        <span className={final_decision.decision === "APPROVE" ? "text-green-800" : "text-red-800"}>
                            {final_decision.decision}D
                        </span>
                    </h2>
                    <p className="text-gray-600 mt-1">{final_decision.reason}</p>
                </div>
                <div className="text-right">
                    <div className="text-sm text-gray-500 uppercase tracking-wide">Confidence</div>
                    <div className="text-3xl font-bold text-gray-800">
                        {(final_decision.confidence * 100).toFixed(0)}%
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Extraction Card */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex items-center gap-2 mb-4 text-blue-600">
                        <FileText className="w-5 h-5" />
                        <h3 className="font-semibold">Extracted Data</h3>
                    </div>
                    <div className="space-y-2 text-sm">
                        <Row label="Vendor" value={extraction.vendor} />
                        <Row label="Date" value={extraction.date} />
                        <Row label="Invoice #" value={extraction.invoice_number} />
                        <Row label="Total" value={`${extraction.currency} ${extraction.total_amount}`} />
                    </div>
                </div>

                {/* Fraud Check Card */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex items-center gap-2 mb-4 text-purple-600">
                        <Shield className="w-5 h-5" />
                        <h3 className="font-semibold">Fraud Check</h3>
                    </div>
                    {fraud_check.is_suspicious ? (
                        <div className="text-red-600 flex items-start gap-2">
                            <AlertTriangle className="w-5 h-5 shrink-0" />
                            <div>
                                <div className="font-bold">Suspicious Activity</div>
                                <ul className="list-disc pl-4 mt-1 text-sm text-gray-700">
                                    {fraud_check.flags.map((flag: string, i: number) => (
                                        <li key={i}>{flag}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    ) : (
                        <div className="text-green-600 flex items-center gap-2">
                            <Check className="w-5 h-5" />
                            <span>No anomalies detected</span>
                        </div>
                    )}
                </div>

                {/* Policy Check Card */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex items-center gap-2 mb-4 text-orange-600">
                        <Brain className="w-5 h-5" />
                        <h3 className="font-semibold">Policy Check</h3>
                    </div>
                    {policy_check.compliant ? (
                        <div className="text-green-600 flex items-center gap-2">
                            <Check className="w-5 h-5" />
                            <span>Policy Compliant</span>
                        </div>
                    ) : (
                        <div className="text-red-600 flex items-start gap-2">
                            <X className="w-5 h-5 shrink-0" />
                            <div>
                                <div className="font-bold">Violations Found</div>
                                <ul className="list-disc pl-4 mt-1 text-sm text-gray-700">
                                    {policy_check.violations.map((v: string, i: number) => (
                                        <li key={i}>{v}</li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

const Row = ({ label, value }: { label: string, value: string | number }) => (
    <div className="flex justify-between border-b border-gray-50 pb-1 last:border-0">
        <span className="text-gray-500">{label}</span>
        <span className="font-medium text-gray-900">{value || "N/A"}</span>
    </div>
);

export default InvoiceResult;
