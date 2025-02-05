import { useEffect, useState } from 'react'
import { Alert, AlertDescription, AlertTitle } from "../components/ui/alert"
import { MetricCard } from './performance/MetricCard'
import { ModelComparisonChart } from './performance/ModelComparisonChart'
import { AlertCircle } from 'lucide-react'
import { Card, CardHeader, CardContent, CardTitle } from "../components/ui/card"
import { FileUploader } from './performance/FileUploader'
import { Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material'

interface ModelMetrics {
  model_name: string;
  r2_score: number;
  rmse?: number;
  mae?: number;
  timestamp: string;
}

interface PerformanceData {
  overall_performance: number;
  models_metrics: ModelMetrics[];
  last_update: string;
}

type MetricsHistory = {
  id: number;
  model_name: string;
  r2_score: number | null;
  mae: number | null;
  rmse: number | null;
  training_date: string;
  additional_info: string | null;
}[];

const API_URL = 'http://localhost:8001/api/performance'

export function PerformanceMetrics() {
  const [data, setData] = useState<PerformanceData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });
  const [trainingStatus, setTrainingStatus] = useState<{
    [key: string]: { status: 'idle' | 'training' | 'success' | 'error', message: string }
  }>({});
  const [metricsHistory, setMetricsHistory] = useState<MetricsHistory>([]);
  const [showHistory, setShowHistory] = useState(false);

  const handleUpload = async (files: File[], module: string, isFolder: boolean) => {
    const formData = new FormData();
    formData.append("module", module);
    formData.append("is_folder", String(isFolder));
    
    files.forEach(file => {
      formData.append("files", file);
      formData.append("paths", file.webkitRelativePath || file.name);
    });
  
    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Échec de l\'upload');
      }
  
      const result = await response.json();
  
      setUploadStatus({
        type: 'success',
        message: `✅ ${files.length} fichier${files.length > 1 ? 's' : ''} uploadé${files.length > 1 ? 's' : ''} avec succès!`
      });
  
      await fetchPerformanceData();
    } catch (err) {
      setUploadStatus({
        type: 'error',
        message: err instanceof Error ? `❌ ${err.message}` : '❌ Erreur inconnue'
      });
      throw err;
    }
  };

  const handleTrainModel = async (modelName: string) => {
    setTrainingStatus(prev => ({
      ...prev,
      [modelName]: { status: 'training', message: 'Entraînement en cours...' }
    }));

    let endpoint = '';
    switch (modelName) {
      case 'Prédiction Commandes':
        endpoint = `${API_URL}/train-commandes`;
        break;
      case 'Planification Livraisons':
        endpoint = `${API_URL}/train-livraisons`;
        break;
      case 'Gestion RH':
        endpoint = `${API_URL}/train-rh`;
        break;
      default:
        setTrainingStatus(prev => ({
          ...prev,
          [modelName]: { status: 'error', message: 'Modèle non reconnu' }
        }));
        return;
    }

    try {
      const response = await fetch(endpoint, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error('Erreur lors de l\'entraînement');
      }

      setTrainingStatus(prev => ({
        ...prev,
        [modelName]: { status: 'success', message: 'Entraînement réussi!' }
      }));

      await Promise.all([
        fetchPerformanceData(),
        fetchMetricsHistory()
      ]);
    } catch (error) {
      setTrainingStatus(prev => ({
        ...prev,
        [modelName]: { 
          status: 'error', 
          message: error instanceof Error ? error.message : 'Erreur lors de l\'entraînement' 
        }
      }));
    }
  };

  const fetchPerformanceData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/overview`);
      if (!response.ok) throw new Error('Erreur réseau');
      const data = await response.json();
      
      setData({
        ...data,
        models_metrics: data.models_metrics.map((m: any) => ({
          ...m,
          rmse: m.rmse ?? undefined,
          mae: m.mae ?? undefined
        }))
      });
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchMetricsHistory = async () => {
    try {
      const response = await fetch(`${API_URL}/metrics-history`);
      if (!response.ok) throw new Error('Erreur réseau');
      const { success, data } = await response.json();
      if (success) {
        setMetricsHistory(data);
      } else {
        throw new Error('Erreur lors de la récupération des données');
      }
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'historique:', error);
      setError(error instanceof Error ? error.message : 'Erreur inconnue');
    }
  };

  useEffect(() => {
    fetchPerformanceData();
  }, []);

  useEffect(() => {
    if (uploadStatus.type) {
      const timer = setTimeout(() => {
        setUploadStatus({ type: null, message: '' });
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [uploadStatus]);

  if (error) {
    return (
      <Alert variant="destructive" className="dark:bg-red-900/50 dark:text-red-200 dark:border-red-800">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Erreur</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (isLoading) {
    return <div className="text-center py-8 dark:text-white">Chargement des performances...</div>
  }

  if (!data || !data.models_metrics?.length) {
    return <div className="text-center py-8 dark:text-white">Aucune donnée de performance disponible</div>
  }

  return (
    <div className="space-y-8 p-4 dark:bg-gray-900 dark:text-white">
      {/* En-tête avec titre et bouton d'historique */}
      <div className="flex justify-between items-center">
        <h2 className="text-4xl font-bold dark:text-white">Performances</h2>
        <button
          onClick={() => {
            if (!showHistory) {
              fetchMetricsHistory();
            }
            setShowHistory(!showHistory);
          }}
          className="px-4 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 bg-white dark:bg-gray-800 border border-blue-600 dark:border-blue-400 rounded-md hover:bg-blue-50 dark:hover:bg-gray-700"
        >
          {showHistory ? "Masquer l'historique" : "Voir l'historique"}
        </button>
      </div>

      {/* Détails par modèle */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {data.models_metrics.map((model) => (
          <Card key={model.model_name} className="hover:shadow-lg transition-shadow dark:border-gray-700">
            <CardHeader>
              <CardTitle className="text-lg font-semibold dark:text-white">
                {model.model_name}
              </CardTitle>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Mis à jour : {new Date(model.timestamp).toLocaleString('fr-FR', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Score R²</p>
                  <p className="text-2xl font-bold text-primary dark:text-blue-400">
                    {(model.r2_score * 100).toFixed(1)}%
                  </p>
                </div>
                
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-300">RMSE</p>
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {model.rmse ? model.rmse.toFixed(2) : 'N/A'}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-300">MAE</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {model.mae ? model.mae.toFixed(2) : 'N/A'}
                </p>
              </div>

              <div className="mt-4">
                <button
                  onClick={() => handleTrainModel(model.model_name)}
                  disabled={trainingStatus[model.model_name]?.status === 'training'}
                  className={`w-full px-4 py-2 text-sm font-medium text-white rounded-md transition-colors ${
                    trainingStatus[model.model_name]?.status === 'training'
                      ? 'bg-gray-400 dark:bg-gray-600 cursor-not-allowed'
                      : 'bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600'
                  }`}
                >
                  {trainingStatus[model.model_name]?.status === 'training' ? (
                    'Entraînement en cours...'
                  ) : (
                    'Entrainer le modèle'
                  )}
                </button>

                {trainingStatus[model.model_name] && (
                  <p className={`mt-2 text-sm ${
                    trainingStatus[model.model_name].status === 'success' 
                      ? 'text-green-600' 
                      : trainingStatus[model.model_name].status === 'error'
                      ? 'text-red-600'
                      : 'text-gray-600'
                  }`}>
                    {trainingStatus[model.model_name].message}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Historique des métriques */}
      {showHistory && (
        <Card className="w-full dark:bg-gray-800 dark:border-gray-700">
          <CardHeader>
            <CardTitle className="dark:text-white">Historique des performances</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell className="dark:text-gray-300">Modèle</TableCell>
                  <TableCell className="dark:text-gray-300">Date d'entraînement</TableCell>
                  <TableCell className="dark:text-gray-300">Score R²</TableCell>
                  <TableCell className="dark:text-gray-300">MAE</TableCell>
                  <TableCell className="dark:text-gray-300">RMSE</TableCell>
                  <TableCell className="dark:text-gray-300">Info supplémentaire</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {metricsHistory.map((metric) => (
                  <TableRow key={metric.id} className="dark:hover:bg-gray-700">
                    <TableCell className="font-medium dark:text-white">{metric.model_name}</TableCell>
                    <TableCell className="dark:text-gray-300">
                      {new Date(metric.training_date).toLocaleDateString('fr-FR', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </TableCell>
                    <TableCell className="dark:text-gray-300">{metric.r2_score !== null ? `${(metric.r2_score * 100).toFixed(1)}%` : 'N/A'}</TableCell>
                    <TableCell className="dark:text-gray-300">{metric.mae !== null ? metric.mae.toFixed(2) : 'N/A'}</TableCell>
                    <TableCell className="dark:text-gray-300">{metric.rmse !== null ? metric.rmse.toFixed(2) : 'N/A'}</TableCell>
                    <TableCell className="text-sm text-gray-500 dark:text-gray-400">{metric.additional_info || '-'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Métriques principales */}
      <div className="grid gap-4 grid-cols-1 md:grid-cols-3">
        <MetricCard
          title="Performance Globale"
          value={data.overall_performance * 100}
          unit="%"
          description="Score moyen R² de tous les modèles"
        />
        
        <MetricCard
          title="Nombre de Modèles"
          value={data.models_metrics.length}
          description="Modèles en production"
        />
        
        <MetricCard
          title="Dernière Mise à Jour"
          value={new Date(Math.max(...data.models_metrics.map(m => new Date(m.timestamp).getTime()))).toLocaleString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}
          description="Date de dernière évaluation"
          unit=""
        />
      </div>

      {/* Section Upload */}
      <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border dark:border-gray-700">
        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
          Importer des données
        </h2>
        <FileUploader onUpload={handleUpload} />
      </div>

      {/* Comparaison des modèles */}
      <ModelComparisonChart
        data={data.models_metrics.map(m => ({
          name: m.model_name,
          r2_score: m.r2_score,
          rmse: m.rmse ?? 0,
          mae: m.mae ?? 0
        }))}
      />
    </div>
  )
}