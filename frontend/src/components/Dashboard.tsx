import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Clock, FileText } from 'lucide-react';

interface Stats {
  total_invoices: number;
  decisions: {
    approved: number;
    rejected: number;
    on_hold: number;
  };
  fraud: {
    suspicious: number;
    clean: number;
  };
  approval_levels: {
    auto_approve: number;
    requires_review: number;
  };
}

interface Invoice {
  id: number;
  filename: string;
  invoice_number: string;
  vendor_name: string;
  total_amount: number;
  currency: string;
  uploaded_at: string;
  processed_at: string;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentInvoices, setRecentInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/stats');
      if (!response.ok) throw new Error('Failed to fetch stats');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stats');
    }
  };

  const fetchRecentInvoices = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/invoices?limit=5');
      if (!response.ok) throw new Error('Failed to fetch invoices');
      const data = await response.json();
      setRecentInvoices(data.invoices);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load invoices');
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchRecentInvoices()]);
      setLoading(false);
    };

    loadData();

    // Refresh stats every 10 seconds
    const interval = setInterval(() => {
      fetchStats();
      fetchRecentInvoices();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 m-6">
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

  if (!stats) return null;

  const approvalRate = stats.total_invoices > 0
    ? (stats.decisions.approved / stats.total_invoices) * 100
    : 0;

  const fraudRate = stats.total_invoices > 0
    ? (stats.fraud.suspicious / stats.total_invoices) * 100
    : 0;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-600 mt-1">Real-time invoice processing analytics</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Invoices */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Invoices</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{stats.total_invoices}</p>
            </div>
            <FileText className="w-12 h-12 text-blue-500" />
          </div>
        </div>

        {/* Approved */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Approved</p>
              <p className="text-3xl font-bold text-green-600 mt-2">{stats.decisions.approved}</p>
              <p className="text-xs text-gray-500 mt-1">{approvalRate.toFixed(1)}% approval rate</p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-500" />
          </div>
        </div>

        {/* Rejected */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Rejected</p>
              <p className="text-3xl font-bold text-red-600 mt-2">{stats.decisions.rejected}</p>
              <p className="text-xs text-gray-500 mt-1">Policy/fraud violations</p>
            </div>
            <AlertTriangle className="w-12 h-12 text-red-500" />
          </div>
        </div>

        {/* On Hold */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">On Hold</p>
              <p className="text-3xl font-bold text-orange-600 mt-2">{stats.decisions.on_hold}</p>
              <p className="text-xs text-gray-500 mt-1">Pending review</p>
            </div>
            <Clock className="w-12 h-12 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Fraud Detection */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Fraud Detection</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-600">Clean Invoices</span>
                <span className="text-sm font-semibold text-green-600">{stats.fraud.clean}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-green-500 h-3 rounded-full"
                  style={{ width: `${(stats.fraud.clean / Math.max(stats.total_invoices, 1)) * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-600">Suspicious Invoices</span>
                <span className="text-sm font-semibold text-red-600">{stats.fraud.suspicious}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-red-500 h-3 rounded-full"
                  style={{ width: `${fraudRate}%` }}
                />
              </div>
            </div>
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm text-gray-600">
                Fraud Detection Rate: <span className="font-bold text-gray-800">{fraudRate.toFixed(1)}%</span>
              </p>
            </div>
          </div>
        </div>

        {/* Approval Levels */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Approval Workflow</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-600">Auto-Approved</span>
                <span className="text-sm font-semibold text-blue-600">{stats.approval_levels.auto_approve}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-blue-500 h-3 rounded-full"
                  style={{ width: `${(stats.approval_levels.auto_approve / Math.max(stats.total_invoices, 1)) * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-600">Requires Review</span>
                <span className="text-sm font-semibold text-orange-600">{stats.approval_levels.requires_review}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-orange-500 h-3 rounded-full"
                  style={{ width: `${(stats.approval_levels.requires_review / Math.max(stats.total_invoices, 1)) * 100}%` }}
                />
              </div>
            </div>
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm text-gray-600">
                Automation Rate: <span className="font-bold text-gray-800">
                  {((stats.approval_levels.auto_approve / Math.max(stats.total_invoices, 1)) * 100).toFixed(1)}%
                </span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Invoices */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Recent Invoices</h3>
          <button
            onClick={() => {
              fetchStats();
              fetchRecentInvoices();
            }}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Refresh
          </button>
        </div>
        
        {recentInvoices.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No invoices processed yet</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Invoice #</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Vendor</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Amount</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Date</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">File</th>
                </tr>
              </thead>
              <tbody>
                {recentInvoices.map((invoice) => (
                  <tr key={invoice.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 text-sm text-gray-800">{invoice.invoice_number || 'N/A'}</td>
                    <td className="py-3 px-4 text-sm text-gray-800">{invoice.vendor_name || 'Unknown'}</td>
                    <td className="py-3 px-4 text-sm text-gray-800">
                      {invoice.currency} {invoice.total_amount?.toFixed(2) || '0.00'}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {invoice.processed_at ? new Date(invoice.processed_at).toLocaleDateString() : 'Processing...'}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">{invoice.filename}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
