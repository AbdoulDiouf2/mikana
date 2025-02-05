-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : mysql:3306
-- Généré le : mer. 05 fév. 2025 à 07:50
-- Version du serveur : 8.0.40
-- Version de PHP : 8.2.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `mikana_db`
--

-- --------------------------------------------------------

--
-- Structure de la table `metrics_history`
--

CREATE TABLE `metrics_history` (
  `id` int NOT NULL,
  `model_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `r2_score` float DEFAULT NULL,
  `mae` float DEFAULT NULL,
  `rmse` float DEFAULT NULL,
  `training_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `additional_info` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `metrics_history`
--

INSERT INTO `metrics_history` (`id`, `model_name`, `r2_score`, `mae`, `rmse`, `training_date`, `additional_info`) VALUES
(1, 'Gestion RH', 0.897, 22.7107, 29.0421, '2025-02-05 05:18:32', 'Migration initiale des données'),
(2, 'Prédiction Commandes', 0.95, 0.000000275871, 0.000000283249, '2025-02-04 12:29:28', 'Migration initiale des données'),
(3, 'Planification Livraisons', 0.96566, 55.8941, 209.468, '2025-01-27 23:04:20', 'Migration initiale des données');

-- --------------------------------------------------------

--
-- Structure de la table `prediction_history`
--

CREATE TABLE `prediction_history` (
  `id` bigint DEFAULT NULL,
  `date` datetime NOT NULL,
  `article` varchar(255) NOT NULL,
  `quantity_ordered` decimal(10,2) NOT NULL,
  `quantity_predicted` decimal(10,2) NOT NULL,
  `delivery_rate` decimal(5,2) NOT NULL,
  `status` varchar(50) NOT NULL,
  `recommendation` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `prediction_history`
--

INSERT INTO `prediction_history` (`id`, `date`, `article`, `quantity_ordered`, `quantity_predicted`, `delivery_rate`, `status`, `recommendation`, `created_at`) VALUES
(1, '2025-02-06 00:00:00', 'ALESE CARREE', 3097.00, 3215.32, 103.82, 'excellent', 'Livraison optimale prévue', '2025-01-28 00:34:33'),
(2, '2025-02-06 00:00:00', 'ALESE CARREE', 3097.00, 3215.32, 103.82, 'excellent', 'Livraison optimale prévue', '2025-01-28 00:35:42'),
(3, '2025-02-06 00:00:00', 'ALESE CARREE', 3097.00, 3215.32, 103.82, 'excellent', 'Livraison optimale prévue', '2025-01-28 00:38:46'),
(4, '2025-02-06 00:00:00', 'LAVETTE', 9519.00, 8862.90, 93.11, 'good', 'Bonne livraison prévue', '2025-01-28 00:42:34'),
(5, '2025-02-06 00:00:00', 'LAVETTE', 9519.00, 8862.90, 93.11, 'good', 'Bonne livraison prévue', '2025-01-28 00:46:14'),
(6, '2025-02-11 00:00:00', 'TORCHON', 345.00, 281.99, 81.74, 'warning', 'Risque de sous-livraison, considérer l\'ajustement de la commande', '2025-01-28 00:47:50'),
(7, '2025-02-26 00:00:00', 'GANT DE TOILETTE', 6639.00, 6311.66, 95.07, 'excellent', 'Livraison optimale prévue', '2025-01-28 01:07:53'),
(8, '2025-02-06 00:00:00', 'ALESE CARREE', 3097.00, 3215.32, 103.82, 'excellent', 'Livraison optimale prévue', '2025-01-31 05:57:50'),
(9, '2025-02-06 00:00:00', 'ALESE CARREE', 3079.00, 3215.32, 104.43, 'excellent', 'Livraison optimale prévue', '2025-01-31 13:32:11'),
(10, '2025-02-06 00:00:00', 'ALESE CARREE', 3097.00, 3215.32, 103.82, 'excellent', 'Livraison optimale prévue', '2025-01-31 14:48:11'),
(NULL, '2025-02-09 23:00:00', 'ALESE CARREE', 3096.00, 3215.32, 103.85, 'excellent', 'Livraison optimale prévue', '2025-02-04 22:55:25');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `metrics_history`
--
ALTER TABLE `metrics_history`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `metrics_history`
--
ALTER TABLE `metrics_history`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
