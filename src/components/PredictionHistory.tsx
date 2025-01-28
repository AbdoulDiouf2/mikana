import React, { useState, useEffect, useCallback, forwardRef, useImperativeHandle } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Button,
  Box,
  Typography,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  PictureAsPdf as PdfIcon,
  TableChart as ExcelIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

interface PredictionRecord {
  id: number;
  date: string;
  article: string;
  quantity_ordered: number;
  quantity_predicted: number;
  delivery_rate: number;
  status: string;
  recommendation: string;
  created_at: string;
}

interface PredictionHistoryProps {
  handleRefresh: () => void;
}

interface PredictionHistoryRef {
  handleRefresh: () => void;
}

const PredictionHistory = forwardRef<PredictionHistoryRef, PredictionHistoryProps>((_props, ref) => {
  const [history, setHistory] = useState<PredictionRecord[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [loading, setLoading] = useState(false);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/history?limit=${rowsPerPage}&offset=${page * rowsPerPage}`);
      if (!response.ok) {
        throw new Error('Erreur lors de la récupération de l\'historique');
      }
      const data = await response.json();
      setHistory(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleExport = async (format: 'excel' | 'pdf') => {
    try {
      const response = await fetch(`http://localhost:8000/api/export/${format}`);
      if (!response.ok) throw new Error(`Erreur lors de l'export en ${format}`);
      
      // Récupérer le blob
      const blob = await response.blob();
      
      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `predictions_${format === 'excel' ? 'xlsx' : 'pdf'}`;
      document.body.appendChild(a);
      a.click();
      
      // Nettoyer
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Erreur lors de l\'export:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent':
        return '#4caf50';
      case 'good':
        return '#ff9800';
      case 'warning':
        return '#f44336';
      default:
        return '#2196F3';
    }
  };

  const handleRefresh = () => {
    fetchHistory();
  };

  useImperativeHandle(ref, () => ({
    handleRefresh: fetchHistory
  }));

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
          <CircularProgress />
        </div>
      ) : (
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Historique des prédictions</Typography>
          <Box>
            <Tooltip title="Exporter en Excel">
              <Button
                startIcon={<ExcelIcon />}
                onClick={() => handleExport('excel')}
                sx={{ mr: 1 }}
              >
                Excel
              </Button>
            </Tooltip>
            <Tooltip title="Exporter en PDF">
              <Button
                startIcon={<PdfIcon />}
                onClick={() => handleExport('pdf')}
              >
                PDF
              </Button>
            </Tooltip>
            <Button onClick={handleRefresh}>Rafraîchir</Button>
          </Box>
        </Box>
      )}
      {!loading && (
        <TableContainer sx={{ maxHeight: 440 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Date de livraison</TableCell>
                <TableCell>Article</TableCell>
                <TableCell align="right">Qté commandée</TableCell>
                <TableCell align="right">Qté prévue</TableCell>
                <TableCell align="right">Taux</TableCell>
                <TableCell>Statut</TableCell>
                <TableCell>Recommandation</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {history.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>
                    {format(new Date(row.date), 'dd/MM/yyyy', { locale: fr })}
                  </TableCell>
                  <TableCell>{row.article}</TableCell>
                  <TableCell align="right">{row.quantity_ordered}</TableCell>
                  <TableCell align="right">{row.quantity_predicted}</TableCell>
                  <TableCell align="right">
                    <Box
                      component="span"
                      sx={{
                        color: getStatusColor(row.status),
                        fontWeight: 'bold',
                      }}
                    >
                      {row.delivery_rate}%
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box
                      sx={{
                        backgroundColor: getStatusColor(row.status),
                        color: 'white',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        display: 'inline-block',
                      }}
                    >
                      {row.status}
                    </Box>
                  </TableCell>
                  <TableCell>{row.recommendation}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      {!loading && (
        <TablePagination
          rowsPerPageOptions={[10, 25, 100]}
          component="div"
          count={-1}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="Lignes par page"
        />
      )}
    </Paper>
  );
});

export default PredictionHistory;
