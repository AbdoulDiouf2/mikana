import React, { useState, useEffect, useRef } from 'react';
import { DatePicker } from '@mui/x-date-pickers';
import { Button, Select, MenuItem, FormControl, InputLabel, CircularProgress, Alert, Paper, Grid, Typography, Box } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import { fr } from 'date-fns/locale';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import PredictionHistory from '../../components/PredictionHistory';
import DeliveryCharts from '../../components/DeliveryCharts';

interface PredictionResult {
  predicted_quantity: number;
  delivery_rate: number;
  prediction_error: number;
  prediction_accuracy: number;
  recommendation: string;
  status: 'excellent' | 'good' | 'warning';
}

type HistoryRefType = {
  handleRefresh: () => void;
};

const DeliveryPrediction: React.FC = () => {
  const [date, setDate] = useState<Date | null>(null);
  const [article, setArticle] = useState('');
  // const [quantity, setQuantity] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [articles, setArticles] = useState<string[]>([]);
  const [loadingArticles, setLoadingArticles] = useState(true);
  const [predictedQuantity, setPredictedQuantity] = useState<number | null>(null);
  const historyRef = useRef<HistoryRefType | null>(null);

  // Charger la liste des articles au démarrage
  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/articles');
        if (!response.ok) {
          throw new Error('Erreur lors de la récupération des articles');
        }
        const data = await response.json();
        setArticles(data.articles);
      } catch (err) {
        console.error('❌ Erreur lors du chargement des articles:', err);
        setError('Impossible de charger la liste des articles');
      } finally {
        setLoadingArticles(false);
      }
    };

    fetchArticles();
  }, []);

  // const handleSubmit = async (e: React.FormEvent) => {
  //   e.preventDefault();
  //   if (!date || !article || !quantity) {
  //     setError('Veuillez remplir tous les champs');
  //     console.error('❌ Formulaire incomplet:', { date, article, quantity });
  //     return;
  //   }
  // 
  //   setLoading(true);
  //   setError('');
  //   console.log('🚀 Début de la prédiction:', {
  //     date: date.toISOString(),
  //     article,
  //     quantity: parseFloat(quantity)
  //   });
  // 
  //   try {
  //     const response = await fetch('http://localhost:8000/api/predict-delivery', {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json',
  //       },
  //       body: JSON.stringify({
  //         date: date.toISOString(),
  //         article,
  //         quantity: parseFloat(quantity),
  //       }),
  //     });
// 
  //     if (!response.ok) {
  //       const errorData = await response.text();
  //       console.error('❌ Erreur API:', errorData);
  //       throw new Error(errorData || 'Erreur lors de la prédiction');
  //     }
// 
  //     const data = await response.json();
  //     console.log('✅ Prédiction réussie:', data);
  //     setResult(data);
  //     // Rafraîchir l'historique après une prédiction réussie
  //     const currentHistory = historyRef.current;
  //     if (currentHistory?.handleRefresh) {
  //       setTimeout(() => {
  //         currentHistory.handleRefresh();
  //       }, 1000); // Attendre 1 seconde pour laisser le temps à la base de données de se mettre à jour
  //     }
  //   } catch (err) {
  //     console.error('❌ Erreur:', err);
  //     setError(err instanceof Error ? err.message : 'Une erreur est survenue lors de la prédiction');
  //   } finally {
  //     setLoading(false);
  //   }
  // };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!date || !article) {
      setError('Veuillez remplir la date et l\'article');
      return;
    }
 
    setLoading(true);
    setError('');
 
    try {
      // 1. Prédiction de la quantité commandée
      const predictionResponse = await fetch('http://localhost:8000/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dateType: 'single',
          date: date.toISOString(),
          linenType: article,
          factors: []
        })
      });
 
      if (!predictionResponse.ok) throw new Error('Erreur de prédiction des commandes');
      const predictionData = await predictionResponse.json();
      const quantity = predictionData.predictions[0].quantity;
      setPredictedQuantity(quantity);
 
      // 2. Prédiction de livraison avec la quantité prédite
      const deliveryResponse = await fetch('http://localhost:8000/api/predict-delivery', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          date: date.toISOString(),
          article: article,
          quantity: quantity
        })
      });
 
      if (!deliveryResponse.ok) throw new Error('Erreur de prédiction de livraison');
      const result = await deliveryResponse.json();
      setResult(result);
 
      // Rafraîchir l'historique
      const currentHistory = historyRef.current;
      if (currentHistory?.handleRefresh) {
        setTimeout(() => currentHistory.handleRefresh(), 1000);
      }
 
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  const statusColors = {
    excellent: '#4CAF50', // Vert
    good: '#2196F3',
    warning: '#FF9800'
  };

  // Fonction pour obtenir la couleur selon le taux
  const getColorByRate = (rate: number) => {
    if (rate > 100) return '#2196F3'; // Bleu pour les dépassements
    if (rate >= 95) return statusColors.excellent;
    if (rate >= 85) return statusColors.good;
    return statusColors.warning;
  };

  // Données pour le graphique circulaire
  const getPieData = () => {
    if (!result || !predictedQuantity) return [];
    const delivered = result.predicted_quantity;
    
    if (delivered > predictedQuantity) {
      return [
        { name: 'Quantité commandée', value: predictedQuantity },
        { name: 'Dépassement', value: delivered - predictedQuantity }
      ];
    }
    return [
      { name: 'Quantité prévue', value: delivered },
      { name: 'Reste à livrer', value: predictedQuantity - delivered }
    ];
  };

  // Fonction pour formater le message de quantité
  const getQuantityMessage = () => {
    if (!result || !predictedQuantity) return '';
    const delivered = result.predicted_quantity;
    
    if (delivered > predictedQuantity) {
      return `Quantité prévue : ${delivered} (dépassement de ${(delivered - predictedQuantity).toFixed(2)}) sur ${predictedQuantity} commandés`;
    }
    return `Quantité prévue : ${delivered} sur ${predictedQuantity} commandés`;
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, margin: '0 auto' }}>
     <Typography variant="h4" gutterBottom>Prédiction de Livraison</Typography>

     <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
       <form onSubmit={handleSubmit}>
         <Grid container spacing={3}>
           <Grid item xs={12} md={6}>
             <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={fr}>
               <DatePicker
                 label="Date de livraison*"
                 value={date}
                 onChange={setDate}
                 slotProps={{
                   textField: { fullWidth: true, required: true }
                 }}
               />
             </LocalizationProvider>
           </Grid>
           <Grid item xs={12} md={6}>
             <FormControl fullWidth required>
               <InputLabel>Article</InputLabel>
               <Select
                 value={article}
                 label="Article"
                 onChange={(e) => setArticle(e.target.value)}
                 disabled={loadingArticles}
               >
                 {loadingArticles ? (
                   <MenuItem disabled>Chargement des articles...</MenuItem>
                 ) : (
                   articles.map((item) => (
                     <MenuItem key={item} value={item}>{item}</MenuItem>
                   ))
                 )}
               </Select>
             </FormControl>
           </Grid>
           <Grid item xs={12}>
             <Button
               variant="contained"
               color="primary"
               type="submit"
               disabled={loading}
               fullWidth
             >
               {loading ? <CircularProgress size={24} /> : 'Prédire la livraison'}
             </Button>
           </Grid>
         </Grid>
       </form>
     </Paper>

     {error && (
       <Alert severity="error" sx={{ mb: 3 }}>
         {error}
       </Alert>
     )}

      {(result || (error && date && article)) && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <Grid container spacing={3}>
            {/* Prédiction de quantité */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom align="center">
                Quantité prédite
              </Typography>
              <Box sx={{ textAlign: 'center', mt: 2 }}>
                <Typography variant="h4" component="div">
                  {result?.predicted_quantity || '---'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  unités
                </Typography>
              </Box>
            </Grid>

            {/* Graphique de comparaison quantités */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom align="center">
                Répartition des quantités
              </Typography>
              {result && (
                <Typography variant="subtitle2" align="center" sx={{ mb: 2 }}>
                  {getQuantityMessage()}
                </Typography>
              )}
              {result ? (
                <Box sx={{ width: '100%', height: 200 }}>
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie
                        data={getPieData()}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                      >
                        <Cell fill={getColorByRate(result.delivery_rate)} />
                        <Cell fill="#f5f5f5" />
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box sx={{ 
                  height: 200, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  bgcolor: '#f5f5f5',
                  borderRadius: 1
                }}>
                  <Typography color="text.secondary">
                    Impossible d'afficher les résultats
                  </Typography>
                </Box>
              )}
            </Grid>

            {/* Recommandation */}
            <Grid item xs={12}>
              {result && (
                <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 2 }}>
                  <Grid container spacing={2}>
                    {/* Taux de livraison */}
                    <Grid item xs={12} md={6}>
                      <Box sx={{ textAlign: 'center', mb: 3 }}>
                        <Typography variant="h6" gutterBottom>
                          Taux de livraison
                        </Typography>
                        <Typography 
                          variant="h3" 
                          sx={{ 
                            color: statusColors[result.status],
                            mt: 2
                          }}
                        >
                          {result.delivery_rate.toFixed(2)}%
                        </Typography>
                      </Box>
                    </Grid>

                    {/* Métriques de prédiction */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" gutterBottom>
                        Métriques de prédiction
                      </Typography>
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body1" gutterBottom>
                          <strong>Quantité prévue :</strong> {result.predicted_quantity.toFixed(2)}
                        </Typography>
                        <Typography variant="body1" gutterBottom>
                          <strong>Erreur de prédiction :</strong> {result.prediction_error.toFixed(2)}%
                        </Typography>
                        <Typography variant="body1" gutterBottom>
                          <strong>Précision du modèle :</strong> {result.prediction_accuracy.toFixed(2)}%
                        </Typography>
                        <Alert
                          icon={result.status === 'warning' ? <WarningIcon /> : <CheckCircleIcon />}
                          severity={result.status === 'warning' ? 'warning' : 'success'}
                          sx={{ mt: 2 }}
                        >
                          {result.recommendation}
                        </Alert>
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              )}
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Historique des prédictions */}
      <Box sx={{ mt: 4 }}>
        <PredictionHistory 
          ref={historyRef}
          handleRefresh={() => {
            historyRef.current?.handleRefresh();
          }}
        />
      </Box>
      {/* Graphiques de livraison */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          Analyses des livraisons
        </Typography>
        <DeliveryCharts />
      </Box>
    </Box>
  );
};

export default DeliveryPrediction;