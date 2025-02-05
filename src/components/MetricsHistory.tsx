import React from 'react';
import { Card, CardHeader, CardContent, CardTitle } from "../components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableRow, TableContainer, Paper } from '@mui/material';

interface MetricsHistoryItem {
  id: number;
  model_name: string;
  r2_score: number | null;
  mae: number | null;
  rmse: number | null;
  training_date: string;
  additional_info: string | null;
}

interface MetricsHistoryProps {
  metricsHistory: MetricsHistoryItem[];
}

const MetricsHistory: React.FC<MetricsHistoryProps> = ({ metricsHistory }) => {
  return (
    <Card className="w-full mb-8">
      <CardHeader>
        <CardTitle>Historique des performances</CardTitle>
      </CardHeader>
      <CardContent>
        <TableContainer component={Paper} sx={{ maxHeight: 440 }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell>Modèle</TableCell>
                <TableCell>Date d'entraînement</TableCell>
                <TableCell align="right">Score R²</TableCell>
                <TableCell align="right">MAE</TableCell>
                <TableCell align="right">RMSE</TableCell>
                <TableCell>Info supplémentaire</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {metricsHistory.map((metric) => (
                <TableRow key={metric.id} hover>
                  <TableCell>{metric.model_name}</TableCell>
                  <TableCell>
                    {new Date(metric.training_date).toLocaleDateString('fr-FR', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </TableCell>
                  <TableCell align="right">{metric.r2_score !== null ? `${(metric.r2_score * 100).toFixed(1)}%` : 'N/A'}</TableCell>
                  <TableCell align="right">{metric.mae !== null ? metric.mae.toFixed(2) : 'N/A'}</TableCell>
                  <TableCell align="right">{metric.rmse !== null ? metric.rmse.toFixed(2) : 'N/A'}</TableCell>
                  <TableCell>{metric.additional_info || '-'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

export default MetricsHistory;