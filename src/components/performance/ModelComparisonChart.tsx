// components/performance/ModelComparisonChart.tsx
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList, Legend } from "recharts"
import { useState } from "react"

interface ModelMetrics {
  name: string
  r2_score: number
  rmse: number
  mae: number
}

interface ModelComparisonChartProps {
  data: ModelMetrics[]
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-lg border dark:border-gray-700">
        <p className="font-bold mb-2 dark:text-white">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }} className="text-sm dark:text-white">
            {entry.name}: {entry.name === "Score R²" 
              ? `${(entry.value * 100).toFixed(1)}%` 
              : entry.value.toFixed(2)}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export function ModelComparisonChart({ data }: ModelComparisonChartProps) {
  const [activeMetrics, setActiveMetrics] = useState({
    r2_score: true,
    rmse: true,
    mae: true
  });

  const handleLegendClick = (entry: any) => {
    setActiveMetrics(prev => ({
      ...prev,
      [entry.dataKey]: !prev[entry.dataKey as keyof typeof prev]
    }));
  };

  return (
    <Card className="w-full dark:text-white">
      <CardHeader>
        <CardTitle className="dark:text-white">Comparaison des Modèles</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart 
              data={data} 
              margin={{ top: 20, right: 30, left: 50, bottom: 5 }}
              animationDuration={1000}
              animationBegin={0}
            >
              <XAxis 
                dataKey="name" 
                stroke="currentColor"
                tick={{ fill: 'currentColor' }}
              />
              <YAxis 
                label={{ 
                  value: 'Valeurs des métriques', 
                  angle: -90, 
                  position: 'insideLeft',
                  style: { fill: 'currentColor' }
                }}
                stroke="currentColor"
                tick={{ fill: 'currentColor' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                onClick={handleLegendClick}
                wrapperStyle={{ color: 'currentColor' }}
              />
              {activeMetrics.r2_score && (
                <Bar dataKey="r2_score" fill="#3b82f6" name="Score R²" animationDuration={1500}>
                  <LabelList dataKey="r2_score" position="top" formatter={(value: number) => `${(value * 100).toFixed(1)}%`} />
                </Bar>
              )}
              {activeMetrics.rmse && (
                <Bar dataKey="rmse" fill="#10b981" name="RMSE" animationDuration={1500}>
                  <LabelList dataKey="rmse" position="top" formatter={(value: number) => value.toFixed(2)} />
                </Bar>
              )}
              {activeMetrics.mae && (
                <Bar dataKey="mae" fill="#6366f1" name="MAE" animationDuration={1500}>
                  <LabelList dataKey="mae" position="top" formatter={(value: number) => value.toFixed(2)} />
                </Bar>
              )}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}