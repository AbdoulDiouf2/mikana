import React, { useEffect, useRef, useState } from 'react';
import Chart from 'chart.js/auto';
import axios from 'axios';

interface HeatMapProps {
  title: string;
  subtitle: string;
  establishment?: string;
  linenType?: string;
}

interface HeatMapData {
  year: number;
  values: number[];
}

export default function HeatMap({ title, subtitle, establishment, linenType }: HeatMapProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [establishment, linenType]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/seasonal-trends', {
        params: { establishment, linenType }
      });

      const monthNames = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'];
      const data = response.data;

      if (chartRef.current) {
        if (chartInstance.current) {
          chartInstance.current.destroy();
        }

        const ctx = chartRef.current.getContext('2d');
        if (!ctx) return;

        // Définir des couleurs distinctes pour chaque année
        const colors: { [key: string]: { border: string; background: string } } = {
          '2022': { border: 'rgb(59, 130, 246)', background: 'rgba(59, 130, 246, 0.2)' }, // Bleu
          '2023': { border: 'rgb(16, 185, 129)', background: 'rgba(16, 185, 129, 0.2)' }, // Vert
          '2024': { border: 'rgb(245, 158, 11)', background: 'rgba(245, 158, 11, 0.2)' }  // Orange
        };

        // Convertir les valeurs en milliers pour une meilleure lisibilité
        const datasets = data.data.map((yearData: HeatMapData) => ({
          label: yearData.year.toString(),
          data: yearData.values.map((value, monthIndex) => ({
            x: monthIndex,
            y: value / 1000 // Convertir en milliers
          })),
          borderColor: colors[yearData.year]?.border || `hsl(${yearData.year % 360}, 70%, 50%)`,
          backgroundColor: colors[yearData.year]?.background || `hsla(${yearData.year % 360}, 70%, 50%, 0.2)`,
          fill: false,
          tension: 0.4
        }));

        chartInstance.current = new Chart(ctx, {
          type: 'line',
          data: {
            labels: monthNames,
            datasets: datasets
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              x: {
                title: {
                  display: true,
                  text: 'Mois'
                }
              },
              y: {
                title: {
                  display: true,
                  text: 'Volume (milliers de kg)'
                },
                beginAtZero: true
              }
            },
            plugins: {
              legend: {
                position: 'top',
                title: {
                  display: true,
                  text: 'Années'
                }
              },
              tooltip: {
                callbacks: {
                  label: (context) => {
                    const value = context.parsed.y * 1000; // Reconvertir en kg pour l'affichage
                    return `${context.dataset.label}: ${value.toLocaleString('fr-FR')} kg`;
                  }
                }
              }
            },
            interaction: {
              intersect: false,
              mode: 'index'
            }
          }
        });
      }
    } catch (error) {
      console.error('Erreur lors de la récupération des données:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm">
      <div className="mb-4">
        <h3 className="text-lg font-semibold">{title}</h3>
        {subtitle && <p className="text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>}
      </div>
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
  );
}