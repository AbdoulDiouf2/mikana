import React from 'react';
import { Sun, Moon } from 'lucide-react';
// import { Search } from 'lucide-react';
// import { Bell, User } from 'lucide-react';

export default function Header({ toggleTheme, isDark }: { toggleTheme: () => void; isDark: boolean }) {
  return (
    <header className="h-16 fixed top-0 right-0 left-64 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 z-10">
      <div className="h-full px-6 flex items-center justify-between">
        {/* <div className="flex items-center flex-1">
          <div className="relative w-96">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Rechercher..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div> */}
        
        <div className="flex items-center space-x-4">
          <button onClick={toggleTheme} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700">
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
          {/* 
          <button className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 relative">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
          <div className="flex items-center space-x-3 border-l pl-4 border-slate-200 dark:border-slate-600">
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="text-sm">
              <p className="font-medium">Administrateur</p>
              <p className="text-slate-500 dark:text-slate-400">Administrateur</p>
            </div>
          </div>
          */}
        </div>
      </div>
    </header>
  );
}