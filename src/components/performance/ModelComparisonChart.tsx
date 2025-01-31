// components/performance/ModelComparisonChart.tsx
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"

interface ModelMetrics {
  name: string
  r2_score: number
  rmse: number
  mae: number
}

interface ModelComparisonChartProps {
  data: ModelMetrics[]
}

export function ModelComparisonChart({ data }: ModelComparisonChartProps) {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Comparaison des Modèles</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="r2_score" fill="#3b82f6" name="Score R²" />
              <Bar dataKey="rmse" fill="#10b981" name="RMSE" />
              <Bar dataKey="mae" fill="#6366f1" name="MAE" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}