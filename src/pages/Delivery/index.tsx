import React from 'react';
import { MapPin } from 'lucide-react';
import PageHeader from '../../components/common/PageHeader';

export default function Delivery() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Delivery Planning"
        subtitle="Route optimization and delivery tracking"
        action={
          <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
            <MapPin className="w-4 h-4" />
            <span>Track Routes</span>
          </button>
        }
      />
      
      <div className="bg-white dark:bg-slate-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4">Delivery Dashboard</h2>
        <p className="text-slate-600 dark:text-slate-400">Coming soon...</p>
      </div>
    </div>
  );
}