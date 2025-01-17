import React from 'react';
import { Brain } from 'lucide-react';

export default function Logo() {
  return (
    <div className="flex items-center space-x-3">
      <div className="w-8 h-8">
        <Brain className="w-full h-full text-blue-500" />
      </div>
      <span className="text-2xl font-bold">MIKANA</span>
    </div>
  );
}