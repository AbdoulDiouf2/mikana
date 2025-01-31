import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import Dashboard from './pages/Dashboard';
import OrderPrediction from './pages/OrderPrediction';
import Maintenance from './pages/Maintenance';
import Delivery from './pages/Delivery';
import HRPlanning from './pages/HRPlanning';
import PerformanceCenter from './pages/PerformanceCenter';

function App() {
  const [isDark, setIsDark] = useState(false);

  const toggleTheme = () => {
    setIsDark(!isDark);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <Router>
      <div className={`${isDark ? 'dark' : ''}`}>
        <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white">
          <Sidebar />
          <Header toggleTheme={toggleTheme} isDark={isDark} />
          <main className="ml-64 pt-16 p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/prediction" element={<OrderPrediction />} />
              <Route path="/maintenance" element={<Maintenance />} />
              <Route path="/delivery" element={<Delivery />} />
              <Route path="/hr" element={<HRPlanning />} />
              <Route path="/performance" element={<PerformanceCenter/>} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;