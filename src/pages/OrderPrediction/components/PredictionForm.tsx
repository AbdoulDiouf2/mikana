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
      <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-200 mb-6">Paramètres de Prédiction</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
            Type de Prédiction
          </label>
          <div className="flex space-x-4">
            <label className="flex items-center text-gray-700 dark:text-gray-200">
              <input
                type="radio"
                value="single"
                checked={formData.dateType === 'single'}
                onChange={() => setFormData({ ...formData, dateType: 'single' as const })}
                className="mr-2 text-blue-600 dark:text-blue-400 focus:ring-blue-500 dark:focus:ring-blue-400"
              />
              Date unique
            </label>
            <label className="flex items-center text-gray-700 dark:text-gray-200">
              <input
                type="radio"
                value="period"
                checked={formData.dateType === 'period'}
                onChange={() => setFormData({ ...formData, dateType: 'period' as const })}
                className="mr-2 text-blue-600 dark:text-blue-400 focus:ring-blue-500 dark:focus:ring-blue-400"
              />
              Période
            </label>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
              {formData.dateType === 'single' ? 'Date de Prédiction' : 'Date de Début'} *
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-300 w-5 h-5" />
              <input
                type="date"
                className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                required
              />
            </div>
          </div>

          {formData.dateType === 'period' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
                Date de Fin *
              </label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-300 w-5 h-5" />
                <input
                  type="date"
                  className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                  value={formData.endDate}
                  onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                  required
                />
              </div>
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
            Établissement (optionnel)
          </label>
          <select
            className="w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
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
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
            Type de Linge (optionnel)
          </label>
          <select
            className="w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
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
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
            Facteurs Additionnels
          </label>
          <div className="space-y-2">
            {additionalFactors.map((factor) => (
              <label key={factor.id} className={`flex items-center space-x-3 p-3 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 ${formData.factors.includes(factor.id) ? '' : 'opacity-50 cursor-not-allowed'}`}>
                <input
                  type="checkbox"
                  className="rounded border-slate-300 dark:border-slate-500 text-blue-600 dark:text-blue-400 focus:ring-blue-500 dark:focus:ring-blue-400"
                  checked={formData.factors.includes(factor.id)}
                  onChange={(e) => {
                    if (!formData.factors.includes(factor.id)) return;
                    const newFactors = e.target.checked
                      ? [...formData.factors, factor.id]
                      : formData.factors.filter(f => f !== factor.id);
                    setFormData({ ...formData, factors: newFactors });
                  }}
                  disabled={!formData.factors.includes(factor.id)}
                />
                <div className="flex items-center space-x-2 text-gray-700 dark:text-gray-200">
                  {factor.icon}
                  <span>{factor.label}</span>
                </div>
                {!formData.factors.includes(factor.id) && (
                  <span className="text-red-500 dark:text-red-400 text-sm">Fonctionnalité indisponible pour le moment</span>
                )}
              </label>
            ))}
          </div>
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full mt-6 px-4 py-3 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
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