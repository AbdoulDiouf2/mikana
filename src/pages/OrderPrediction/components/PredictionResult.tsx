import React from 'react';

interface PredictionResultProps {
  predictions: Array<{
    date: string;
    prediction: number;
    message?: string;
    intervalle_confiance?: {
      min: number;
      max: number;
    };
    statistiques?: {
      moyenne_historique: number;
      minimum_historique: number;
      maximum_historique: number;
      nombre_donnees: number;
      fiabilite: 'basse' | 'moyenne' | 'haute';
      tendance?: number;
      saisonnalite?: number;
    };
  }>;
  formData?: {
    establishment: string;
    linenType: string;
  };
}

export default function PredictionResult({ predictions, formData }: PredictionResultProps) {
  const hasPredictions = Array.isArray(predictions) && predictions.length > 0;
  const isPeriod = predictions && predictions.length > 1;

  const getFiabiliteColor = (fiabilite: string) => {
    switch (fiabilite) {
      case 'haute': return 'text-green-600 dark:text-green-400';
      case 'moyenne': return 'text-yellow-600 dark:text-yellow-400';
      case 'basse': return 'text-red-600 dark:text-red-400';
      default: return 'text-slate-600 dark:text-slate-400';
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
      <h2 className="text-xl font-semibold mb-6 text-gray-900 dark:text-gray-100">Résultats de la Prédiction</h2>
      
      {!hasPredictions ? (
        <p className="text-slate-500 dark:text-slate-400">
          Veuillez remplir le formulaire pour obtenir une prédiction
        </p>
      ) : (
        <div className="space-y-4">
          <div className="mb-4 p-3 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600">
            {formData?.establishment && (
              <div className="text-sm text-slate-600 dark:text-slate-300">
                Établissement: {formData.establishment}
              </div>
            )}
            {formData?.linenType && (
              <div className="text-sm text-slate-600 dark:text-slate-300">
                Type de linge: {formData.linenType}
              </div>
            )}
            {isPeriod && (
              <div className="text-sm text-slate-600 dark:text-slate-300 mt-2">
                Période: du {predictions[0].date} au {predictions[predictions.length - 1].date}
              </div>
            )}
          </div>

          {isPeriod && (
            <div className="p-4 border border-slate-200 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-700">
              <h3 className="font-medium mb-2 text-gray-900 dark:text-gray-100">Résumé de la période</h3>
              <div className="grid grid-cols-2 gap-4 text-sm text-slate-700 dark:text-slate-300">
                <div>
                  Moyenne des prédictions: {Math.round(predictions.reduce((acc, p) => acc + p.prediction, 0) / predictions.length)} unités
                </div>
                <div>
                  Nombre de jours: {predictions.length}
                </div>
                <div>
                  Min: {Math.min(...predictions.map(p => p.prediction))} unités
                </div>
                <div>
                  Max: {Math.max(...predictions.map(p => p.prediction))} unités
                </div>
              </div>
            </div>
          )}

          <div className={isPeriod ? "max-h-[400px] overflow-y-auto space-y-3 pr-2" : ""}>
            {predictions.map((pred, idx) => (
              <div key={idx} className="p-4 border border-slate-200 dark:border-slate-600 rounded-lg space-y-3 bg-white dark:bg-slate-700">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="text-sm text-slate-500 dark:text-slate-400">Date: {pred.date}</div>
                    <div className="text-2xl font-semibold mt-1 text-gray-900 dark:text-gray-100">
                      {pred.prediction} unités
                    </div>
                  </div>
                  {pred.statistiques && (
                    <div className={`text-sm ${getFiabiliteColor(pred.statistiques.fiabilite)}`}>
                      Fiabilité {pred.statistiques.fiabilite}
                    </div>
                  )}
                </div>

                {pred.message && (
                  <div className="text-sm text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-600 p-2 rounded">
                    {pred.message}
                  </div>
                )}

                {pred.intervalle_confiance && (
                  <div className="text-sm text-slate-500 dark:text-slate-400">
                    Intervalle de confiance: [{pred.intervalle_confiance.min} - {pred.intervalle_confiance.max}]
                  </div>
                )}

                {pred.statistiques && !isPeriod && (
                  <div className="text-sm grid grid-cols-2 gap-2 mt-2 text-slate-600 dark:text-slate-300">
                    <div>Moyenne historique: {pred.statistiques.moyenne_historique}</div>
                    <div>Nombre de données: {pred.statistiques.nombre_donnees}</div>
                    <div>Minimum historique: {pred.statistiques.minimum_historique}</div>
                    <div>Maximum historique: {pred.statistiques.maximum_historique}</div>
                    {pred.statistiques.tendance && (
                      <div>Tendance: {pred.statistiques.tendance > 0 ? '↗️' : '↘️'} {Math.abs(pred.statistiques.tendance)}%</div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}