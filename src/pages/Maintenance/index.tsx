import React from 'react';
import { AlertTriangle } from 'lucide-react';
import PageHeader from '../../components/common/PageHeader';

export default function Maintenance() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Machine Maintenance"
        subtitle="Equipment monitoring and maintenance scheduling"
        action={
          <button className="flex items-center space-x-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors">
            <AlertTriangle className="w-4 h-4" />
            <span>Report Issue</span>
          </button>
        }
      />
      
      <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4">Maintenance Dashboard</h2>
        <p className="text-slate-600 dark:text-slate-400">Coming soon...</p>
      </div>
    </div>
  );
}