import React from 'react';
import { 
  ShowerHead,
  Timer, 
  Truck, 
  Users,
  Activity
} from 'lucide-react';
import MetricCard from '../components/dashboard/MetricCard';

const metrics = [
  {
    title: 'Volume Quotidien Total',
    value: '2 547 kg',
    change: 12,
    icon: <ShowerHead className="w-6 h-6 text-blue-600" />
  },
  {
    title: 'Machines Actives',
    value: '18/20',
    change: -5,
    icon: <Timer className="w-6 h-6 text-blue-600" />
  },
  {
    title: 'Routes de Livraison',
    value: '8 Actives',
    change: 0,
    icon: <Truck className="w-6 h-6 text-blue-600" />
  },
  {
    title: 'Personnel en Service',
    value: '24',
    change: 4,
    icon: <Users className="w-6 h-6 text-blue-600" />
  }
];

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Vue d'Ensemble</h1>
          <p className="text-slate-600 dark:text-slate-400">Bienvenue sur le Tableau de Bord MIKANA</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          Générer Rapport
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <MetricCard key={index} {...metric} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">Prévision Volume de Linge</h2>
            <Activity className="w-5 h-5 text-blue-600" />
          </div>
          <div className="h-80 flex items-center justify-center border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-lg">
            Graphique à venir
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">État des Machines</h2>
            <Timer className="w-5 h-5 text-blue-600" />
          </div>
          <div className="h-80 flex items-center justify-center border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-lg">
            Grille d'état à venir
          </div>
        </div>
      </div>
    </div>
  );
}