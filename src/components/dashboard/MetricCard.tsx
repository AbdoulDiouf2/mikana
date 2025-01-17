import React from 'react';
import { ArrowUp, ArrowDown } from 'lucide-react';
import type { MetricCard as MetricCardType } from '../../types';

export default function MetricCard({ title, value, change, icon: Icon }: MetricCardType) {
  const isPositive = change && change > 0;
  
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="w-12 h-12 rounded-lg bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
          {Icon}
        </div>
        {change && (
          <span className={`flex items-center text-sm ${
            isPositive ? 'text-green-500' : 'text-red-500'
          }`}>
            {isPositive ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
            {Math.abs(change)}%
          </span>
        )}
      </div>
      <h3 className="mt-4 text-sm text-slate-600 dark:text-slate-400">{title}</h3>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  );
}