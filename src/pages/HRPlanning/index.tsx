import React from 'react';
import { UserPlus } from 'lucide-react';
import PageHeader from '../../components/common/PageHeader';

export default function HRPlanning() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="HR Planning"
        subtitle="Staff management and scheduling"
        action={
          <button className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
            <UserPlus className="w-4 h-4" />
            <span>Add Staff</span>
          </button>
        }
      />
      
      <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4">HR Dashboard</h2>
        <p className="text-slate-600 dark:text-slate-400">Coming soon...</p>
      </div>
    </div>
  );
}