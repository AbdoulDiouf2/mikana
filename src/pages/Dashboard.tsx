import { Box, Container, Typography, Paper, Grid, Card, CardContent, CardMedia, useTheme, useMediaQuery } from '@mui/material';
import { motion } from 'framer-motion';
import { Analytics, LocalShipping, Engineering, Psychology } from '@mui/icons-material';

const Dashboard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const features = [
    {
      icon: <Analytics />,
      title: "Prédiction Précise",
      description: "Anticipation des quantités de linge et optimisation des commandes grâce à l'IA"
    },
    {
      icon: <LocalShipping />,
      title: "Logistique Optimisée",
      description: "Planification intelligente des livraisons en tenant compte des conditions externes"
    },
    {
      icon: <Engineering />,
      title: "Maintenance Prédictive",
      description: "Anticipation de l'usure des machines pour une maintenance optimale"
    },
    {
      icon: <Psychology />,
      title: "Gestion RH Intelligente",
      description: "Prévision des besoins en ressources humaines"
    }
  ];

  const partners = [
    {
      name: "CHU de Rouen",
      image: "/Images/CHU_ROUEN.png",
      description: "Centre Hospitalier Universitaire"
    },
    {
      name: "ESIGELEC",
      image: "/Images/Logo_ESIGELEC.svg.png",
      description: "École d'Ingénieurs"
    },
    {
      name: "Aptar",
      image: "/Images/aptar.png",
      description: "Partenaire Industriel"
    }
  ];

  return (
    <Container maxWidth="xl">
      {/* Hero Section */}
      <Box
        component={motion.div}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        sx={{
          textAlign: 'center',
          py: 8,
          background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
          borderRadius: 2,
          color: 'white',
          mb: 6
        }}
      >
        <Box
          component="img"
          src="/Images/mikana.png"
          alt="Mikana Logo"
          sx={{
            width: isMobile ? '200px' : '300px',
            height: 'auto',
            mb: 4
          }}
        />
        <Typography variant="h2" component="h1" gutterBottom>
          Bienvenue sur Mikana
        </Typography>
        <Typography variant="h5" sx={{ maxWidth: '800px', mx: 'auto', px: 2 }}>
          L'intelligence artificielle au service de votre blanchisserie
        </Typography>
      </Box>

      {/* About Section */}
      <Paper elevation={3} sx={{ p: 4, mb: 6 }}>
        <Typography variant="h4" gutterBottom>
          À Propos de Mikana
        </Typography>
        <Typography variant="body1" paragraph>
          « Mikana » est une intelligence artificielle de pointe qui révolutionne la gestion des blanchisseries. Notre système utilise des algorithmes avancés pour :
        </Typography>
        <Typography variant="body1" component="ul" sx={{ pl: 2 }}>
          <li>Prédire avec précision les quantités de linge commandées</li>
          <li>Optimiser la planification des livraisons en tenant compte des conditions de circulation et météorologiques</li>
          <li>Anticiper l'usure des machines et planifier la maintenance préventive</li>
          <li>Gérer efficacement les ressources humaines</li>
          <li>Adapter les opérations en fonction des épidémies et des besoins spécifiques des services de soins</li>
        </Typography>
      </Paper>

      {/* Features Section */}
      <Grid container spacing={4} sx={{ mb: 6 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              component={motion.div}
              whileHover={{ scale: 1.05 }}
              sx={{ height: '100%' }}
            >
              <CardContent sx={{ textAlign: 'center' }}>
                <Box sx={{ color: 'primary.main', mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Partners Section */}
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        Nos Partenaires
      </Typography>
      <Grid container spacing={4} sx={{ mb: 6 }}>
        {partners.map((partner, index) => (
          <Grid item xs={12} sm={4} key={index}>
            <Card
              component={motion.div}
              whileHover={{ scale: 1.05 }}
              sx={{ height: '100%' }}
            >
              <CardMedia
                component="img"
                height="140"
                image={partner.image}
                alt={partner.name}
                sx={{ objectFit: 'contain', p: 2, background: '#f5f5f5' }}
              />
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {partner.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {partner.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Dashboard;