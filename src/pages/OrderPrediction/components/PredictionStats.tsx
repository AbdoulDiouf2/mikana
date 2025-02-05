import React from 'react';
import { Percent, TrendingUp, AlertCircle, BarChart } from 'lucide-react';

interface PredictionStatsProps {
  modelStats?: {
    accuracy: number;
    mape?: number;
    rmse?: number;
    mae?: number;
    confidence_level?: number;
    sample_size?: number;
    trend_direction?: 'up' | 'down' | 'stable';
    trend_strength?: number;
  };
}

export default function PredictionStats({ modelStats }: PredictionStatsProps) {
  if (!modelStats) {
    return (
      <div className="bg-white dark:bg-slate-800 p-6 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700">
        <p className="text-slate-500 dark:text-slate-400 text-center">
          Les statistiques seront affichées après la génération des prédictions
        </p>
      </div>
    );
  }

  const stats = [
    {
      label: 'Précision du Modèle',
      value: `${(modelStats.accuracy * 100).toFixed(1)}%`,
      icon: <Percent className="w-5 h-5 text-green-500 dark:text-green-400" />,
      tooltip: 'Pourcentage global de précision du modèle'
    },
    {
      label: 'MAPE',
      value: modelStats.mape ? `${modelStats.mape.toFixed(2)}%` : 'N/A',
      icon: <AlertCircle className="w-5 h-5 text-yellow-500 dark:text-yellow-400" />,
      tooltip: 'Erreur Moyenne Absolue en Pourcentage'
    },
    {
      label: 'Tendance',
      value: modelStats.trend_direction ? 
        `${modelStats.trend_direction === 'up' ? '↗️' : modelStats.trend_direction === 'down' ? '↘️' : '→'} ${modelStats.trend_strength?.toFixed(1)}%` : 
        'N/A',
      icon: <TrendingUp className="w-5 h-5 text-blue-500 dark:text-blue-400" />,
      tooltip: 'Direction et force de la tendance'
    },
    {
      label: 'Taille Échantillon',
      value: modelStats.sample_size?.toString() || 'N/A',
      icon: <BarChart className="w-5 h-5 text-purple-500 dark:text-purple-400" />,
      tooltip: 'Nombre de données utilisées pour l\'entraînement'
    }
  ];

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Performances du Modèle</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <div 
            key={index} 
            className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700"
            title={stat.tooltip}
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-100 dark:bg-slate-700 rounded-lg">
                {stat.icon}
              </div>
              <div>
                <p className="text-sm text-slate-600 dark:text-slate-400">{stat.label}</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Métriques détaillées */}
      <div className="mt-6 bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700">
        <h4 className="text-sm font-semibold mb-3 text-gray-900 dark:text-gray-100">Métriques Détaillées</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-600 dark:text-slate-400">RMSE:</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">{modelStats.rmse?.toFixed(2) || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600 dark:text-slate-400">MAE:</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">{modelStats.mae?.toFixed(2) || 'N/A'}</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-600 dark:text-slate-400">Niveau de Confiance:</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">{modelStats.confidence_level ? `${(modelStats.confidence_level * 100).toFixed(1)}%` : 'N/A'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}