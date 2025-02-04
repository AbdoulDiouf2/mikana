import React, { useState, useEffect } from 'react';
import { Paper, Typography, Grid, Box, CircularProgress } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
         BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

interface YearlyData {
year: number;
delivered: number;
}

interface MonthlyData {
month: string;
year2022: number;
year2023: number;
year2024: number;
}

interface ArticleData {
name: string;
value: number;
}

interface ComparisonData {
year: number;
ordered: number;
delivered: number;
}

const DeliveryCharts = () => {
    const [yearlyData, setYearlyData] = useState<YearlyData[]>([]);
    const [monthlyData, setMonthlyData] = useState<MonthlyData[]>([]);
    const [articleData, setArticleData] = useState<ArticleData[]>([]);
    const [comparisonData, setComparisonData] = useState<ComparisonData[]>([]);
    const [loading, setLoading] = useState(true);
  
    // Fonction pour formater les grands nombres
    const formatYAxis = (value: any, index: number): string => {
      if (typeof value !== 'number') return String(value);
      if (value >= 1000000) {
        return `${(value / 1000000).toFixed(1)}M`;
      }
      if (value >= 1000) {
        return `${(value / 1000).toFixed(0)}k`;
      }
      return String(value);
    };
  
    // Fonction pour formater les valeurs du tooltip
    const formatTooltipValue = (value: number) => {
      return new Intl.NumberFormat('fr-FR').format(value);
    };
  
    useEffect(() => {
      const fetchData = async () => {
        try {
          const response = await fetch('http://localhost:8000/api/delivery-stats');
          const data = await response.json();
          
          setYearlyData(data.yearlyTrend);
          setMonthlyData(data.monthlyComparison);
          setArticleData(data.articleDistribution);
          setComparisonData(data.orderDeliveryComparison);
        } catch (error) {
          console.error('Error fetching delivery stats:', error);
        } finally {
          setLoading(false);
        }
      };
  
      fetchData();
    }, []);
  
    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];
  
    if (loading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
          <CircularProgress />
        </Box>
      );
    }
  
    const CustomTooltip = ({ active, payload, label }: any) => {
      if (active && payload && payload.length) {
        return (
          <Paper sx={{ p: 1 }}>
            <Typography variant="body2">{label}</Typography>
            {payload.map((pld: any, index: number) => (
              <Typography key={index} variant="body2" sx={{ color: pld.color }}>
                {`${pld.name}: ${formatTooltipValue(pld.value)}`}
              </Typography>
            ))}
          </Paper>
        );
      }
      return null;
    };
  
    return (
      <Grid container spacing={3}>
        {/* Tendance annuelle des livraisons */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Tendance annuelle des livraisons
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={yearlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis tickFormatter={formatYAxis} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Line type="monotone" dataKey="delivered" stroke="#8884d8" name="Quantité livrée" />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>
  
        {/* Comparaison mensuelle des livraisons */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Comparaison mensuelle des livraisons
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis tickFormatter={formatYAxis} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Bar dataKey="year2022" fill="#8884d8" name="2022" />
                  <Bar dataKey="year2023" fill="#82ca9d" name="2023" />
                  <Bar dataKey="year2024" fill="#ffc658" name="2024" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>
  
        {/* Distribution des articles */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Distribution des articles
            </Typography>
            <Box sx={{ height: 500 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={articleData}
                    cx="50%"
                    cy="50%"
                    innerRadius={0}
                    outerRadius={180}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ value }) => formatTooltipValue(value)}
                  >
                    {articleData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={formatTooltipValue} />
                  <Legend layout="vertical" align="right" verticalAlign="middle" />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>
  
        {/* Comparaison commandes/livraisons */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Comparaison commandes/livraisons
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={comparisonData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis tickFormatter={formatYAxis} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Bar dataKey="ordered" fill="#8884d8" name="Commandé" />
                  <Bar dataKey="delivered" fill="#82ca9d" name="Livré" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    );
  };
  
  export default DeliveryCharts;