import { useEffect, useState } from 'react'
import { Alert, AlertDescription, AlertTitle } from "../components/ui/alert"
import { MetricCard } from './performance/MetricCard'
import { ModelComparisonChart } from './performance/ModelComparisonChart'
import { AlertCircle } from 'lucide-react'
import { Card, CardHeader, CardContent, CardTitle } from "../components/ui/card"
import { FileUploader } from './performance/FileUploader'

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

const API_URL = 'http://localhost:8001/api/performance/overview'

export function PerformanceMetrics() {
  const [data, setData] = useState<PerformanceData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{
    type: 'success' | 'error' | null;
    message: string;
  }>({ type: null, message: '' });

  const handleUpload = async (files: File[], module: string, isFolder: boolean) => {
    const formData = new FormData();
    formData.append("module", module);
    formData.append("is_folder", String(isFolder));
    
    console.log("Files à uploader:", files);
  
    files.forEach(file => {
      formData.append("files", file);
      formData.append("paths", file.webkitRelativePath || file.name);
    });
  
    try {
      console.log("Envoi de la requête...");
      const response = await fetch("http://localhost:8001/api/performance/upload", {
        method: "POST",
        body: formData,
      });
  
      console.log("Réponse reçue:", response);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Échec de l\'upload');
      }
  
      const result = await response.json();
      console.log("Résultat:", result);
  
      setUploadStatus({
        type: 'success',
        message: `✅ ${files.length} fichier${files.length > 1 ? 's' : ''} uploadé${files.length > 1 ? 's' : ''} avec succès!`
      });
  
      await fetchPerformanceData();
    } catch (err) {
      console.error("Erreur lors de l'upload:", err);
      setUploadStatus({
        type: 'error',
        message: err instanceof Error ? `❌ ${err.message}` : '❌ Erreur inconnue'
      });
      throw err; // Propager l'erreur pour que le composant FileUploader puisse la gérer
    }
  };

  const fetchPerformanceData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(API_URL);
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
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Erreur</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (isLoading) {
    return <div className="text-center py-8">Chargement des performances...</div>
  }

  if (!data || !data.models_metrics?.length) {
    return <div className="text-center py-8">Aucune donnée de performance disponible</div>
  }

  return (
    <div className="space-y-8 p-4">

      <h2 className="text-lg font-bold">Performances</h2>
      {/* Détails par modèle */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {data.models_metrics.map((model) => (
          <Card key={model.model_name} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="text-lg font-semibold">
                {model.model_name}
              </CardTitle>
              <div className="text-sm text-gray-500">
                Mis à jour : {new Date(model.timestamp).toLocaleDateString('fr-FR')}
              </div>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-600">Score R²</p>
                  <p className="text-2xl font-bold text-primary">
                    {(model.r2_score * 100).toFixed(1)}%
                  </p>
                </div>
                
                <div>
                  <p className="text-sm font-medium text-gray-600">RMSE</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {model.rmse ? model.rmse.toFixed(2) : 'N/A'}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium text-gray-600">MAE</p>
                <p className="text-2xl font-bold text-green-600">
                  {model.mae ? model.mae.toFixed(2) : 'N/A'}
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

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
          value={new Date(data.last_update).toLocaleDateString('fr-FR', {
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
      <div className="bg-white dark:bg-slate-800 p-6 rounded-xl shadow-sm border">
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