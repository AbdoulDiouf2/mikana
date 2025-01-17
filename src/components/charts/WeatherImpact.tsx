import React, { useEffect, useRef, useState } from 'react';
import Chart from 'chart.js/auto';
import axios from 'axios';

interface WeatherImpactProps {
  title: string;
  subtitle: string;
  establishment?: string;
  linenType?: string;
}

export default function WeatherImpact({ title, subtitle, establishment, linenType }: WeatherImpactProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const [loading, setLoading] = useState(true);
  const [weatherData, setWeatherData] = useState<any>(null);

  useEffect(() => {
    fetchWeatherImpact();
  }, [establishment, linenType]);

  const fetchWeatherImpact = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/weather-impact', {
        params: { establishment, linenType }
      });

      const data = response.data;
      setWeatherData(data);

      if (chartRef.current) {
        const ctx = chartRef.current.getContext('2d');
        if (!ctx) return;

        new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['Température', 'Précipitations', 'Humidité'],
            datasets: [
              {
                label: 'Impact sur le Volume',
                data: [
                  data.temperature.impact,
                  data.precipitation.impact,
                  data.humidity.impact
                ],
                backgroundColor: [
                  'rgba(255, 99, 132, 0.5)',
                  'rgba(54, 162, 235, 0.5)',
                  'rgba(75, 192, 192, 0.5)'
                ],
                borderColor: [
                  'rgb(255, 99, 132)',
                  'rgb(54, 162, 235)',
                  'rgb(75, 192, 192)'
                ],
                borderWidth: 1
              }
            ]
          },
          options: {
            responsive: true,
            plugins: {
              tooltip: {
                callbacks: {
                  afterBody: (tooltipItems) => {
                    const factor = tooltipItems[0].dataIndex;
                    const factors = ['temperature', 'precipitation', 'humidity'];
                    const factorData = data[factors[factor]].values;
                    return factorData.map(v => 
                      `${v.condition}: ${v.volume.toFixed(2)} kg`
                    );
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Coefficient de Corrélation'
                }
              }
            }
          }
        });
      }
    } catch (error) {
      console.error('Erreur lors de la récupération des données météo:', error);
    } finally {
      setLoading(false);
    }
  };

  const getImpactDescription = (impact: number) => {
    if (impact >= 0.7) return { text: 'Fort impact positif', color: 'text-green-600' };
    if (impact >= 0.3) return { text: 'Impact positif modéré', color: 'text-green-500' };
    if (impact >= -0.3) return { text: 'Impact faible', color: 'text-gray-600' };
    if (impact >= -0.7) return { text: 'Impact négatif modéré', color: 'text-red-500' };
    return { text: 'Fort impact négatif', color: 'text-red-600' };
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
      <div className="mb-4">
        <h3 className="text-lg font-semibold">{title}</h3>
        {subtitle && <p className="text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="h-96">
            {loading ? (
              <div className="h-full flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
              </div>
            ) : (
              <canvas ref={chartRef} />
            )}
          </div>
        </div>
        <div className="bg-gray-50 dark:bg-slate-700 rounded-lg p-4">
          <h4 className="font-semibold mb-4">Résumé de l'Impact</h4>
          {weatherData && !loading ? (
            <div className="space-y-4">
              <div>
                <h5 className="font-medium mb-2">Température</h5>
                <div className={`${getImpactDescription(weatherData.temperature.impact).color}`}>
                  {getImpactDescription(weatherData.temperature.impact).text}
                  <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                    Corrélation: {(weatherData.temperature.impact * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
              <div>
                <h5 className="font-medium mb-2">Précipitations</h5>
                <div className={`${getImpactDescription(weatherData.precipitation.impact).color}`}>
                  {getImpactDescription(weatherData.precipitation.impact).text}
                  <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                    Corrélation: {(weatherData.precipitation.impact * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
              <div>
                <h5 className="font-medium mb-2">Humidité</h5>
                <div className={`${getImpactDescription(weatherData.humidity.impact).color}`}>
                  {getImpactDescription(weatherData.humidity.impact).text}
                  <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                    Corrélation: {(weatherData.humidity.impact * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
              <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  Ces données sont basées sur l'analyse des corrélations entre les conditions météorologiques et les volumes de linge traités.
                </p>
              </div>
            </div>
          ) : (
            <div className="text-gray-500">Chargement des données...</div>
          )}
        </div>
      </div>
    </div>
  );
} 