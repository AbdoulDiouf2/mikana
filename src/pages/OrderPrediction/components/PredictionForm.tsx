import React, { useState } from 'react';
import { Calendar, Building2, Package, CloudSun } from 'lucide-react';
import axios, { AxiosError } from 'axios';

interface FormData {
  dateType: 'single' | 'period';
  date: string;
  endDate?: string;
  establishment: string;
  linenType: string;
  factors: string[];
}

interface Prediction {
  date: string;
  prediction: number;
  intervalle_confiance: {
    min: number;
    max: number;
  };
  tendance: number;
  composante_hebdomadaire: number;
  composante_annuelle: number;
}

interface PredictionFormProps {
  onPredictionResult: (predictions: any[], formData: any) => void;
}

export default function PredictionForm({ onPredictionResult }: PredictionFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [establishments, setEstablishments] = useState<string[]>([]);
  const [linenTypes, setLinenTypes] = useState<string[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [formData, setFormData] = useState<FormData>({
    dateType: 'single',
    date: '',
    endDate: '',
    establishment: '',
    linenType: '',
    factors: [],
  });

  // Chargement des données au montage du composant
  React.useEffect(() => {
    const fetchData = async () => {
      try {
        const [establishmentsRes, linenTypesRes] = await Promise.all([
          axios.get('http://localhost:8000/api/establishments'),
          axios.get('http://localhost:8000/api/linen-types')
        ]);
        
        console.log('Établissements reçus:', establishmentsRes.data);
        console.log('Types de linge reçus:', linenTypesRes.data);
        
        setEstablishments(establishmentsRes.data.establishments);
        setLinenTypes(linenTypesRes.data.linenTypes);
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error);
      }
    };

    fetchData();
  }, []);

  const additionalFactors = [
    { id: 'weather', label: 'Météo', icon: <CloudSun className="w-4 h-4" /> },
    { id: 'season', label: 'Saison', icon: <Calendar className="w-4 h-4" /> },
    { id: 'events', label: 'Événements', icon: <Package className="w-4 h-4" /> },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      console.log("Submitting form with data:", formData); // Debug log
      const response = await axios.post('http://localhost:8000/api/predict', formData);
      console.log("API Response:", response.data); // Debug log
      
      // Log les données envoyées au parent
      console.log("Sending to parent:", {
        establishment: formData.establishment,
        linenType: formData.linenType
      });
      
      onPredictionResult(response.data.predictions, {
        establishment: formData.establishment,
        linenType: formData.linenType
      });
    } catch (error: unknown) {
      const axiosError = error as AxiosError<{ detail: string }>;
      console.error('Erreur lors de la prédiction:', error);
      alert(axiosError.response?.data?.detail || "Erreur lors de la prédiction. Veuillez réessayer.");
    } finally {
      setIsLoading(false);
    }
  };

  console.log('États actuels:', { establishments, linenTypes });

  return (
    <form onSubmit={handleSubmit} className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm space-y-6">
      <h2 className="text-xl font-semibold mb-6">Paramètres de Prédiction</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Type de Prédiction
          </label>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="single"
                checked={formData.dateType === 'single'}
                onChange={() => setFormData({ ...formData, dateType: 'single' as const })}
                className="mr-2"
              />
              Date unique
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="period"
                checked={formData.dateType === 'period'}
                onChange={() => setFormData({ ...formData, dateType: 'period' as const })}
                className="mr-2"
              />
              Période
            </label>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              {formData.dateType === 'single' ? 'Date de Prédiction' : 'Date de Début'} *
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="date"
                className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                required
              />
            </div>
          </div>

          {formData.dateType === 'period' && (
            <div>
              <label className="block text-sm font-medium mb-2">
                Date de Fin *
              </label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input
                  type="date"
                  className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={formData.endDate}
                  onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                  required
                />
              </div>
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Établissement (optionnel)
          </label>
          <select
            className="w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={formData.establishment}
            onChange={(e) => setFormData({ ...formData, establishment: e.target.value })}
          >
            <option value="">Tous les établissements</option>
            {establishments.map((est) => (
              <option key={est} value={est}>{est}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Type de Linge (optionnel)
          </label>
          <select
            className="w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={formData.linenType}
            onChange={(e) => setFormData({ ...formData, linenType: e.target.value })}
          >
            <option value="">Tous les types</option>
            {linenTypes.map((type) => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Facteurs Additionnels
          </label>
          <div className="space-y-2">
            {additionalFactors.map((factor) => (
              <label key={factor.id} className="flex items-center space-x-3 p-3 rounded-lg border border-slate-200 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  checked={formData.factors.includes(factor.id)}
                  onChange={(e) => {
                    const newFactors = e.target.checked
                      ? [...formData.factors, factor.id]
                      : formData.factors.filter(f => f !== factor.id);
                    setFormData({ ...formData, factors: newFactors });
                  }}
                />
                <div className="flex items-center space-x-2">
                  {factor.icon}
                  <span>{factor.label}</span>
                </div>
              </label>
            ))}
          </div>
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full mt-6 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
      >
        {isLoading ? (
          <>
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            <span>Génération en cours...</span>
          </>
        ) : (
          <span>Générer la Prédiction</span>
        )}
      </button>
    </form>
  );
}