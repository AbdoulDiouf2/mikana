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
  useTheme,
  alpha,
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
  const theme = useTheme();
  const [history, setHistory] = useState<PredictionRecord[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [loading, setLoading] = useState(false);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/history?limit=${String(rowsPerPage)}&offset=${String(page * rowsPerPage)}`);
      const data = await response.json();
      console.log("History data received:", data);
      setHistory(data.data || []);
    } catch (error) {
      console.error("Error fetching history:", error);
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
    const colors = {
      excellent: theme.palette.success.main,
      good: theme.palette.warning.main,
      warning: theme.palette.error.main,
      default: theme.palette.info.main
    };
    return colors[status as keyof typeof colors] || colors.default;
  };

  const handleRefresh = () => {
    fetchHistory();
  };

  useImperativeHandle(ref, () => ({
    handleRefresh: fetchHistory
  }));

  return (
    <Paper 
      sx={{ 
        width: '100%', 
        overflow: 'hidden',
        bgcolor: theme.palette.mode === 'dark' ? 'background.paper' : '#fff',
      }}
    >
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Box sx={{ 
          p: 2, 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderBottom: 1,
          borderColor: 'divider'
        }}>
          <Typography variant="h6" color="text.primary">Historique des prédictions</Typography>
          <Box>
            <Tooltip title="Exporter en Excel">
              <Button
                variant="outlined"
                startIcon={<ExcelIcon />}
                onClick={() => handleExport('excel')}
                sx={{ mr: 1 }}
              >
                Excel
              </Button>
            </Tooltip>
            <Tooltip title="Exporter en PDF">
              <Button
                variant="outlined"
                startIcon={<PdfIcon />}
                onClick={() => handleExport('pdf')}
                sx={{ mr: 1 }}
              >
                PDF
              </Button>
            </Tooltip>
            <Button 
              variant="contained" 
              onClick={handleRefresh}
              sx={{
                bgcolor: theme.palette.mode === 'dark' ? 'primary.dark' : 'primary.main',
                '&:hover': {
                  bgcolor: theme.palette.mode === 'dark' ? 'primary.main' : 'primary.dark',
                }
              }}
            >
              Rafraîchir
            </Button>
          </Box>
        </Box>
      )}
      {!loading && (
        <TableContainer sx={{ maxHeight: 440 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell sx={{ bgcolor: theme.palette.mode === 'dark' ? 'background.paper' : 'background.default' }}>
                  Date de livraison
                </TableCell>
                <TableCell sx={{ bgcolor: theme.palette.mode === 'dark' ? 'background.paper' : 'background.default' }}>
                  Article
                </TableCell>
                <TableCell align="right" sx={{ bgcolor: theme.palette.mode === 'dark' ? 'background.paper' : 'background.default' }}>
                  Qté commandée
                </TableCell>
                <TableCell align="right" sx={{ bgcolor: theme.palette.mode === 'dark' ? 'background.paper' : 'background.default' }}>
                  Qté prévue
                </TableCell>
                <TableCell align="right" sx={{ bgcolor: theme.palette.mode === 'dark' ? 'background.paper' : 'background.default' }}>
                  Taux
                </TableCell>
                <TableCell sx={{ bgcolor: theme.palette.mode === 'dark' ? 'background.paper' : 'background.default' }}>
                  Statut
                </TableCell>
                <TableCell sx={{ bgcolor: theme.palette.mode === 'dark' ? 'background.paper' : 'background.default' }}>
                  Recommandation
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {history.map((row) => (
                <TableRow 
                  key={row.id}
                  sx={{ 
                    '&:nth-of-type(odd)': {
                      bgcolor: theme.palette.mode === 'dark' 
                        ? alpha(theme.palette.common.white, 0.05)
                        : alpha(theme.palette.common.black, 0.05),
                    },
                    '&:hover': {
                      bgcolor: theme.palette.mode === 'dark'
                        ? alpha(theme.palette.common.white, 0.1)
                        : alpha(theme.palette.common.black, 0.1),
                    },
                  }}
                >
                  <TableCell>
                    {format(new Date(row.date.split(' ')[0]), 'dd/MM/yyyy', { locale: fr })}
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
                        color: theme.palette.getContrastText(getStatusColor(row.status)),
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
          sx={{
            borderTop: 1,
            borderColor: 'divider',
            color: 'text.primary'
          }}
        />
      )}
    </Paper>
  );
});

export default PredictionHistory;
