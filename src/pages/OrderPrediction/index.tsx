import React, { useState, useRef } from 'react';
import PageHeader from '../../components/common/PageHeader';
import PredictionForm from './components/PredictionForm';
import PredictionStats from './components/PredictionStats';
import PredictionResult from './components/PredictionResult';
import LineChart from '../../components/charts/LineChart';
import HeatMap from '../../components/charts/HeatMap';
import axios from 'axios';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import * as XLSX from 'xlsx';
import WeatherImpact from '../../components/charts/WeatherImpact';

interface ModelStats {
  accuracy: number;
  mape?: number;
  rmse?: number;
  mae?: number;
  confidence_level?: number;
  sample_size?: number;
  trend_direction?: 'up' | 'down' | 'stable';
  trend_strength?: number;
}

interface PredictionHistory {
  date: string;  // Date de la prédiction
  establishment: string;
  linenType: string;
  predictions: {
    date: string;  // Date prédite
    value: number; // Valeur prédite
  }[];
}

interface HistoricalComparison {
  date: string;
  prediction: number;
  historical2024: number;
  historical2023: number;
}

interface ExportData {
  predictions: any[];
  historicalComparisons: HistoricalComparison[];
  stats: ModelStats | undefined;
  charts: {
    historicalChart: HTMLCanvasElement | null;
    seasonalChart: HTMLCanvasElement | null;
  };
}

export default function OrderPrediction() {
  const [predictions, setPredictions] = useState<any[]>([]);
  const [modelStats, setModelStats] = useState<ModelStats | undefined>();
  const [currentFormData, setCurrentFormData] = useState<{
    establishment: string;
    linenType: string;
  }>({ establishment: '', linenType: '' });
  
  // Initialiser l'historique depuis le localStorage
  const [predictionHistory, setPredictionHistory] = useState<PredictionHistory[]>(() => {
    const savedHistory = localStorage.getItem('predictionHistory');
    return savedHistory ? JSON.parse(savedHistory) : [];
  });

  const [historicalComparisons, setHistoricalComparisons] = useState<HistoricalComparison[]>([]);
  const [isExporting, setIsExporting] = useState(false);
  const historicalChartRef = useRef<HTMLDivElement>(null);
  const seasonalChartRef = useRef<HTMLDivElement>(null);

  const handlePredictionResult = async (predictionData: any[], formData: any) => {
    setPredictions(predictionData);
    setCurrentFormData({
      establishment: formData.establishment,
      linenType: formData.linenType
    });

    // S'assurer que establishment et linenType sont bien passés
    console.log("Form data:", formData);

    // Récupérer les données historiques avec les bons paramètres
    const predictedDates = predictionData.map(pred => pred.predicted_date || pred.date);
    const historicalData = await fetchHistoricalData(
      predictedDates,
      formData.establishment,  // Passer l'établissement
      formData.linenType      // Passer le type de linge
    );

    // Combiner les prédictions avec les données historiques
    const comparisons = predictionData.map((pred, index) => ({
      date: pred.predicted_date || pred.date,
      prediction: Number(pred.prediction || pred.predicted_value),
      historical2024: historicalData[index]?.value2024 || 0,
      historical2023: historicalData[index]?.value2023 || 0
    }));

    setHistoricalComparisons(comparisons);

    // Créer un tableau de prédictions avec leurs dates
    const predictionsArray = predictionData.map((pred: any) => ({
      date: pred.predicted_date || pred.date,
      value: Number(pred.prediction || pred.predicted_value || 0)
    }));

    const newHistoryEntry: PredictionHistory = {
      date: new Date().toISOString(),
      establishment: formData.establishment,
      linenType: formData.linenType,
      predictions: predictionsArray
    };
    
    // Mettre à jour l'historique en gardant les 10 dernières prédictions
    const updatedHistory = [newHistoryEntry, ...predictionHistory].slice(0, 10);
    setPredictionHistory(updatedHistory);
    
    // Sauvegarder dans le localStorage pour la persistance
    localStorage.setItem('predictionHistory', JSON.stringify(updatedHistory));

    // Récupérer les statistiques du modèle depuis la réponse de l'API
    if (predictionData && predictionData.length > 0 && predictionData[0].model_stats) {
      setModelStats(predictionData[0].model_stats);
    }
  };

  const clearPredictionHistory = () => {
    setPredictionHistory([]);
    localStorage.removeItem('predictionHistory');
  };

  const fetchHistoricalData = async (dates: string[], establishment: string, linenType: string) => {
    try {
      console.log("Fetching historical data for:", { establishment, linenType, dates });
      
      const promises = dates.map(async (date) => {
        const dateObj = new Date(date);
        const month = dateObj.getMonth() + 1;
        const day = dateObj.getDate();

        const response = await axios.get(`http://localhost:8000/api/historical-data`, {
          params: {
            establishment: establishment,  // S'assurer que ces valeurs sont passées
            linenType: linenType,
            month,
            day
          }
        });

        return response.data;
      });

      const historicalData = await Promise.all(promises);
      console.log("Historical data received:", historicalData);
      return historicalData;
    } catch (error) {
      console.error('Erreur lors de la récupération des données historiques:', error);
      return [];
    }
  };

  // Préparer les données pour le graphique
  const chartData = {
    labels: historicalComparisons.map(comp => new Date(comp.date).toLocaleDateString('fr-FR')),
    datasets: [
      {
        label: '2025 (Prédiction)',
        data: historicalComparisons.map(comp => comp.prediction),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: false
      },
      {
        label: '2024',
        data: historicalComparisons.map(comp => comp.historical2024),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: false
      },
      {
        label: '2023',
        data: historicalComparisons.map(comp => comp.historical2023),
        borderColor: 'rgb(245, 158, 11)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        fill: false
      }
    ]
  };

  const handleExport = async (format: 'pdf' | 'excel' | 'csv') => {
    setIsExporting(true);
    try {
      const data: ExportData = {
        predictions,
        historicalComparisons,
        stats: modelStats,
        charts: {
          historicalChart: historicalChartRef.current?.querySelector('canvas') || null,
          seasonalChart: seasonalChartRef.current?.querySelector('canvas') || null
        }
      };

      switch (format) {
        case 'pdf':
          await exportToPDF(data);
          break;
        case 'excel':
          exportToExcel(data);
          break;
        case 'csv':
          exportToCSV(data);
          break;
      }
    } catch (error) {
      console.error('Erreur lors de l\'export:', error);
      alert('Une erreur est survenue lors de l\'export');
    } finally {
      setIsExporting(false);
    }
  };

  const exportToPDF = async (data: ExportData) => {
    const pdf = new jsPDF('p', 'mm', 'a4');
    let yOffset = 10;

    // Titre principal
    pdf.setFontSize(20);
    pdf.text('Rapport de Prédictions', 105, yOffset, { align: 'center' });
    yOffset += 20;

    // Informations de base
    pdf.setFontSize(14);
    pdf.text(`Établissement: ${currentFormData.establishment || 'Tous'}`, 10, yOffset);
    yOffset += 10;
    pdf.text(`Type de Linge: ${currentFormData.linenType || 'Tous'}`, 10, yOffset);
    yOffset += 20;

    // Statistiques du modèle
    if (data.stats) {
      pdf.setFontSize(16);
      pdf.text('Statistiques du Modèle', 10, yOffset);
      yOffset += 10;
      pdf.setFontSize(12);
      Object.entries(data.stats).forEach(([key, value]) => {
        pdf.text(`${key}: ${value}`, 15, yOffset);
        yOffset += 7;
      });
      yOffset += 10;
    }

    // Prédictions actuelles
    pdf.setFontSize(16);
    pdf.text('Prédictions Actuelles', 10, yOffset);
    yOffset += 10;
    pdf.setFontSize(12);
    predictions.forEach((pred, index) => {
      const date = new Date(pred.predicted_date || pred.date).toLocaleDateString('fr-FR');
      const value = Number(pred.prediction || pred.predicted_value).toFixed(2);
      pdf.text(`${date}: ${value} kg`, 15, yOffset);
      yOffset += 7;
    });
    yOffset += 10;

    // Graphique de comparaison historique
    if (data.charts.historicalChart) {
      pdf.addPage();
      yOffset = 10;
      pdf.setFontSize(16);
      pdf.text('Comparaison Historique', 10, yOffset);
      yOffset += 20;
      const historicalCanvas = await html2canvas(data.charts.historicalChart);
      pdf.addImage(
        historicalCanvas.toDataURL('image/png'),
        'PNG',
        10,
        yOffset,
        190,
        100
      );
      yOffset += 110;
    }

    // Tableau de comparaison détaillée
    pdf.addPage();
    yOffset = 10;
    pdf.setFontSize(16);
    pdf.text('Comparaison Détaillée', 10, yOffset);
    yOffset += 15;
    pdf.setFontSize(12);

    // En-têtes du tableau
    const headers = ['Date', '2025 (Prédiction)', '2024', '2023'];
    const columnWidth = 45;
    headers.forEach((header, index) => {
      pdf.text(header, 10 + index * columnWidth, yOffset);
    });
    yOffset += 10;

    // Données du tableau
    historicalComparisons.forEach((comp) => {
      const date = new Date(comp.date).toLocaleDateString('fr-FR');
      pdf.text(date, 10, yOffset);
      pdf.text(`${comp.prediction.toFixed(2)} kg`, 10 + columnWidth, yOffset);
      pdf.text(`${comp.historical2024.toFixed(2)} kg`, 10 + columnWidth * 2, yOffset);
      pdf.text(`${comp.historical2023.toFixed(2)} kg`, 10 + columnWidth * 3, yOffset);
      yOffset += 7;
    });

    // Graphique des tendances saisonnières
    if (data.charts.seasonalChart) {
      pdf.addPage();
      yOffset = 10;
      pdf.setFontSize(16);
      pdf.text('Tendances Saisonnières', 10, yOffset);
      yOffset += 20;
      const seasonalCanvas = await html2canvas(data.charts.seasonalChart);
      pdf.addImage(
        seasonalCanvas.toDataURL('image/png'),
        'PNG',
        10,
        yOffset,
        190,
        100
      );
    }

    // Historique des prédictions
    if (predictionHistory.length > 0) {
      pdf.addPage();
      yOffset = 10;
      pdf.setFontSize(16);
      pdf.text('Historique des Prédictions', 10, yOffset);
      yOffset += 15;
      pdf.setFontSize(12);

      predictionHistory.forEach((history) => {
        pdf.text(`Date: ${new Date(history.date).toLocaleString('fr-FR')}`, 15, yOffset);
        yOffset += 7;
        pdf.text(`Établissement: ${history.establishment}`, 15, yOffset);
        yOffset += 7;
        pdf.text(`Type de Linge: ${history.linenType}`, 15, yOffset);
        yOffset += 7;
        pdf.text('Prédictions:', 15, yOffset);
        yOffset += 7;

        history.predictions.forEach((pred) => {
          const date = new Date(pred.date).toLocaleDateString('fr-FR');
          pdf.text(`  ${date}: ${pred.value} kg`, 20, yOffset);
          yOffset += 7;
        });
        yOffset += 10;

        // Nouvelle page si nécessaire
        if (yOffset > 250) {
          pdf.addPage();
          yOffset = 20;
        }
      });
    }

    pdf.save('rapport-complet-predictions.pdf');
  };

  const exportToExcel = (data: ExportData) => {
    const wb = XLSX.utils.book_new();

    // Feuille des prédictions
    const predictionsWS = XLSX.utils.json_to_sheet(data.predictions);
    XLSX.utils.book_append_sheet(wb, predictionsWS, 'Prédictions');

    // Feuille des comparaisons historiques
    const historicalWS = XLSX.utils.json_to_sheet(data.historicalComparisons);
    XLSX.utils.book_append_sheet(wb, historicalWS, 'Comparaisons Historiques');

    // Feuille des statistiques
    if (data.stats) {
      const statsWS = XLSX.utils.json_to_sheet([data.stats]);
      XLSX.utils.book_append_sheet(wb, statsWS, 'Statistiques');
    }

    XLSX.writeFile(wb, 'rapport-predictions.xlsx');
  };

  const exportToCSV = (data: ExportData) => {
    const ws = XLSX.utils.json_to_sheet(data.predictions);
    const csv = XLSX.utils.sheet_to_csv(ws);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'predictions.csv';
    link.click();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <PageHeader
          title="Prévision des Commandes"
          subtitle="Système de prévision basé sur l'IA pour la gestion du volume de linge"
        />
        <div className="relative">
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-2"
            onClick={() => document.getElementById('exportMenu')?.classList.toggle('hidden')}
          >
            {isExporting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Export en cours...</span>
              </>
            ) : (
              <>
                <span>Exporter</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </>
            )}
          </button>
          <div id="exportMenu" className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg hidden z-10">
            <div className="py-1">
              <button
                onClick={() => handleExport('pdf')}
                className="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
              >
                Exporter en PDF
              </button>
              <button
                onClick={() => handleExport('excel')}
                className="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
              >
                Exporter en Excel
              </button>
              <button
                onClick={() => handleExport('csv')}
                className="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
              >
                Exporter en CSV
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PredictionForm onPredictionResult={handlePredictionResult} />
        <PredictionResult predictions={predictions} formData={currentFormData} />
      </div>

      <PredictionStats modelStats={modelStats} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div ref={historicalChartRef}>
          <LineChart 
            title="Comparaison Historique"
            subtitle="Évolution sur les années précédentes"
            chartData={chartData}
          />
        </div>
        <div className="bg-white shadow-lg rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-2">Comparaison Détaillée</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">2025 (Prédiction)</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">2024</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">2023</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {historicalComparisons.map((comp, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                      {new Date(comp.date).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-blue-600">
                      {comp.prediction.toFixed(2)} kg
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                      {comp.historical2024.toFixed(2)} kg
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                      {comp.historical2023.toFixed(2)} kg
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div ref={seasonalChartRef}>
        <HeatMap 
          title="Tendances Saisonnières"
          subtitle="Visualisation annuelle"
          establishment={currentFormData.establishment}
          linenType={currentFormData.linenType}
        />
      </div>

      <div className="grid grid-cols-1 gap-6">
        <WeatherImpact 
          title="Analyse de l'Impact Météorologique"
          subtitle="Corrélation entre conditions météo et volume de linge"
          establishment={currentFormData.establishment}
          linenType={currentFormData.linenType}
        />
      </div>

      <div className="mt-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Historique des Prédictions</h2>
          <button
            onClick={clearPredictionHistory}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors duration-200"
          >
            Effacer l'historique
          </button>
        </div>
        <div className="bg-white shadow-lg rounded-lg overflow-hidden border border-gray-200">
          {predictionHistory.length > 0 ? (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">Date de prédiction</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">Établissement</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">Type de Linge</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600 uppercase tracking-wider">Prédictions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {predictionHistory.map((history, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(history.date).toLocaleString('fr-FR')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {history.establishment}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {history.linenType}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <div className="space-y-1">
                        {history.predictions.map((pred, pidx) => (
                          <div key={pidx} className="flex items-center space-x-2">
                            <span className="text-gray-600">
                              {new Date(pred.date).toLocaleDateString('fr-FR')}:
                            </span>
                            <span className="font-medium text-blue-600">
                              {pred.value} kg
                            </span>
                          </div>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-gray-500">
              Aucun historique de prédiction disponible
            </div>
          )}
        </div>
      </div>
    </div>
  );
}