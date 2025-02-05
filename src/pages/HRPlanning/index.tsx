import React, { useState, useEffect, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Calendar, Users } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';

interface Prediction {
  period: string;
  predicted: number;
  lower: number;
  upper: number;
}

interface PredictionResponse {
  period: string;
  predicted_presences: number;
  confidence_interval: [number, number];
}

const HRDashboard = () => {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [weeks, setWeeks] = useState(30);
  const [loading, setLoading] = useState(false);

  const fetchPredictions = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/predict-sarima', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ weeks }),
      });
      const data = await response.json();
      const formattedData = data.predictions.map((p: PredictionResponse) => ({
        period: p.period,
        predicted: p.predicted_presences,
        lower: p.confidence_interval[0],
        upper: p.confidence_interval[1],
      }));
      setPredictions(formattedData);
    } catch (error) {
      console.error('Error fetching predictions:', error);
    } finally {
      setLoading(false);
    }
  }, [weeks]);

  useEffect(() => {
    fetchPredictions();
  }, [fetchPredictions]);

  return (
    <div className="space-y-6 my-8">
      <div className="grid grid-cols-2 gap-4 max-w-2xl mx-auto">
        <Card className="bg-white dark:bg-gray-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-900 dark:text-gray-100">Personnel Total</CardTitle>
            <Users className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {predictions.length > 0 
                ? Math.round(predictions[0].predicted)
                : '-'
              }
            </div>
            {predictions.length > 0 && (
              <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <p>Min: {Math.round(predictions[0].lower)}</p>
                <p>Max: {Math.round(predictions[0].upper)}</p>
              </div>
            )}
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">Présences prévues - Semaine actuelle</p>
          </CardContent>
        </Card>

        <Card className="bg-white dark:bg-gray-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-900 dark:text-gray-100">Période de Prévision</CardTitle>
            <Calendar className="h-4 w-4 text-green-600 dark:text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{weeks} semaines</div>
            <p className="text-xs text-gray-500 dark:text-gray-400">Horizon de prédiction</p>
          </CardContent>
        </Card>

        <Card className="bg-white dark:bg-gray-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-900 dark:text-gray-100">Personnel Semaine +1</CardTitle>
            <Users className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {predictions.length > 1 
                ? Math.round(predictions[1].predicted)
                : '-'
              }
            </div>
            {predictions.length > 1 && (
              <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <p>Min: {Math.round(predictions[1].lower)}</p>
                <p>Max: {Math.round(predictions[1].upper)}</p>
              </div>
            )}
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">Présences prévues - Semaine prochaine</p>
          </CardContent>
        </Card>

        <Card className="bg-white dark:bg-gray-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-900 dark:text-gray-100">Personnel Semaine +2</CardTitle>
            <Users className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {predictions.length > 2 
                ? Math.round(predictions[2].predicted)
                : '-'
              }
            </div>
            {predictions.length > 2 && (
              <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <p>Min: {Math.round(predictions[2].lower)}</p>
                <p>Max: {Math.round(predictions[2].upper)}</p>
              </div>
            )}
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">Présences prévues - Dans 2 semaines</p>
          </CardContent>
        </Card>
      </div>

      <Card className="col-span-4 mx-8 mb-8 bg-white dark:bg-gray-800">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-gray-900 dark:text-gray-100">Prévisions de Présence</CardTitle>
            <div className="flex items-center space-x-2">
              <Select value={weeks.toString()} onValueChange={(value) => setWeeks(parseInt(value))}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Sélectionner la période" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="12">12 semaines</SelectItem>
                  <SelectItem value="24">24 semaines</SelectItem>
                  <SelectItem value="30">30 semaines</SelectItem>
                  <SelectItem value="52">52 semaines</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={fetchPredictions} disabled={loading}>
                {loading ? 'Chargement...' : 'Actualiser'}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="rounded-md border border-gray-200 dark:border-gray-700">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-900">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Période
                      </th>
                      <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Prédiction
                      </th>
                      <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Limite Inférieure
                      </th>
                      <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Limite Supérieure
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {predictions.map((prediction, index) => (
                      <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                          {prediction.period}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">
                          {prediction.predicted.toFixed(1)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">
                          {prediction.lower.toFixed(1)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900 dark:text-gray-100">
                          {prediction.upper.toFixed(1)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={predictions} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
                  <XAxis dataKey="period" className="text-gray-600 dark:text-gray-400" />
                  <YAxis className="text-gray-600 dark:text-gray-400" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgb(var(--background))',
                      borderColor: 'rgb(var(--border))',
                      color: 'rgb(var(--foreground))'
                    }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="predicted" name="Prédiction" stroke="#4f46e5" strokeWidth={2} />
                  <Line type="monotone" dataKey="lower" name="Limite Inf." stroke="#94a3b8" strokeDasharray="3 3" />
                  <Line type="monotone" dataKey="upper" name="Limite Sup." stroke="#94a3b8" strokeDasharray="3 3" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default HRDashboard;