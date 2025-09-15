# Documentation Utilisateur – Projet Microservices **PayeTonKawa**

Ce document fournit les instructions nécessaires pour **déployer, utiliser, tester, surveiller et maintenir** l’écosystème de microservices du projet **PayeTonKawa**.
L’ensemble de l’application est orchestré via **Docker Compose**.

---

## 1️⃣ Architecture Microservices

Le projet est composé des services suivants :

* **Traefik** : Reverse proxy qui expose les services sur un point d’entrée unique et gère le routage.
* **Keycloak** : Fournisseur d’identité pour la gestion des utilisateurs, des rôles et de l’authentification.
* **jwt-auth** : Service de validation des tokens JWT (utilisé par Traefik comme Forward Auth) pour sécuriser les APIs.
* **RabbitMQ** : Broker de messages pour la communication asynchrone entre les services.
* **Prometheus** : Outil de monitoring et d’alerting pour collecter les métriques des services.
* **APIs** :

  * `customer-api` : Gère les données des clients.
  * `product-api` : Gère le catalogue des produits.
  * `order-api` : Gère les commandes.
* **Bases de données** : Chaque API possède sa propre base de données PostgreSQL isolée.

---

## 2️⃣ Prérequis

Avant de commencer, assurez-vous d’avoir installé :

* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

---

## 3️⃣ Lancement de l’Application

L’ensemble de l’écosystème est orchestré via un unique fichier `docker-compose.yml` situé dans le répertoire `CI-CD`.

**Important** : Les autres fichiers `docker-compose.yml` présents dans les répertoires de chaque service sont uniquement destinés aux tests unitaires et **ne doivent pas être utilisés pour le déploiement global**.

### ⚠️ Étape 1 – Créer le réseau externe sur chaque machine

Sur chaque machine hôte (Linux, macOS ou Windows), **un réseau externe doit être créé localement** avant la première exécution de `docker compose up`.
Le fichier `.env` définit bien `DOCKER_NETWORK_NAME=mspr`, mais si le réseau n’existe pas, Compose s’arrête avec l’erreur :

```
network mspr declared as external, but could not be found
```

Dans le dossier `CI-CD` (là où se trouve `docker-compose.yml`), exécutez :

```bash
# 1) Vérifier si le réseau existe
docker network ls | grep mspr        # Linux / macOS
docker network ls | findstr mspr     # Windows PowerShell ou CMD

# 2) Le créer s’il n’existe pas
docker network create --driver bridge --attachable mspr

# 3) Vérifier
docker network inspect mspr | grep Name   # ou Select-String Name sous Windows
```

💡 **Astuce** : si vous clonez ou déplacez ce projet sur plusieurs machines, **répétez cette étape sur chacune** avant le premier démarrage.

---

### ⚠️ Étape 2 – Créer le fichier `.env` à partir de `env.example`

Dans le dossier `CI-CD/`, copiez le fichier d’exemple et renommez-le :

```bash
cd CI-CD
cp env.example .env        # Linux / macOS
copy env.example .env      # Windows PowerShell ou CMD
```

Ouvrez ensuite le fichier `.env` nouvellement créé et **complétez ou adaptez** les variables si besoin.
Exemple minimal :

```env
DOCKER_NETWORK_NAME=mspr
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin
RABBITMQ_URL=amqp://app:app@rabbitmq:5672/%2F
PRODUCT_POSTGRES_USER=product
PRODUCT_POSTGRES_PASSWORD=product
```

> ⚠️ Ne modifiez pas `env.example` directement : seul le fichier `.env` est lu par `docker compose`.

---

### Étape 3 – Lancer l’écosystème

Depuis le dossier `CI-CD` :

```bash
docker compose up -d --build
```

---

## 4️⃣ Accès aux Services

Une fois les conteneurs démarrés, les services sont accessibles via le reverse proxy Traefik sur `http://localhost`.

### Interfaces Web

| Service                               | URL via Traefik               |
| ------------------------------------- | ----------------------------- |
| **Dashboard Traefik**                 | `http://localhost:8083`       |
| **Console d’administration Keycloak** | `http://localhost/auth`       |
| **Interface de gestion RabbitMQ**     | `http://localhost:15672`      |
| **Interface Prometheus**              | `http://localhost/prometheus` |

### APIs exposées

| Service          | URL de base                     |
| ---------------- | ------------------------------- |
| **Customer API** | `http://localhost/api/customer` |
| **Product API**  | `http://localhost/api/product`  |
| **Order API**    | `http://localhost/api/order`    |

> Les routes de documentation (ex: `/api/customer/docs`) sont publiques.
> Toutes les autres routes sont sécurisées et nécessitent un **token JWT**.

---

## 5️⃣ Endpoints des APIs

### 🛍️ Product API (`/api/product`)

* `POST /products/` : Créer un nouveau produit.
* `GET /products/` : Lister les produits avec filtres et pagination.
* `GET /products/{product_id}` : Obtenir les détails d’un produit par son ID.
* `PUT /products/{product_id}` : Mettre à jour un produit.
* `DELETE /products/{product_id}` : Supprimer un produit.
* `GET /products/sku/{sku}` : Obtenir les détails d’un produit par son SKU.
* `PATCH /products/{product_id}/stock` : Ajuster le stock d’un produit.
* `PATCH /products/{product_id}/active` : Activer ou désactiver un produit.

### 🧑‍🤝‍🧑 Customer API (`/api/customer`)

* `POST /customers/` : Créer un nouveau client.
* `GET /customers/` : Lister les clients avec filtres et pagination.
* `GET /customers/{customer_id}` : Obtenir les détails d’un client par son ID.
* `PUT /customers/{customer_id}` : Mettre à jour un client.
* `DELETE /customers/{customer_id}` : Supprimer un client.
* `GET /customers/email/{email}` : Rechercher un client par son adresse e-mail.

### 🛒 Order API (`/api/order`)

* `POST /orders/` : Créer une nouvelle commande.
* `GET /orders/` : Lister les commandes.
* `GET /orders/{order_id}` : Obtenir les détails d’une commande par son ID.
* `DELETE /orders/{order_id}` : Supprimer une commande.
* `PUT /orders/{order_id}/status` : Mettre à jour le statut d’une commande.

---

## 6️⃣ Authentification et Sécurité

* **Keycloak** gère les utilisateurs, les rôles et l’émission des tokens JWT.
* Exemple pour obtenir un token :

```bash
curl -X POST \
     -d "client_id=<client_id>" \
     -d "username=<user>" \
     -d "password=<password>" \
     -d "grant_type=password" \
     http://localhost/auth/realms/paye-ton-kawa/protocol/openid-connect/token
```

* Exemple d’appel sécurisé :

```bash
curl -H "Authorization: Bearer <token>" http://localhost/api/product/products
```

---

## 7️⃣ Tests et Postman

Pour tester et documenter les APIs, l’équipe utilise **Postman**.

* **Collections** : regroupent toutes les requêtes (URL, headers, body).
* **Workspaces** : espaces collaboratifs partagés.
* **Desktop Agent** : permet d’envoyer les requêtes vers `localhost` et Docker.

Un workspace nommé *PayeTonKawa* contient déjà toutes les requêtes (JWT, Produits, Commandes).

### Partager la collection

1. **Exporter en JSON** (clic droit → Export → format v2.1 → fichier `.json`).
   → Les testeurs importent ce fichier dans Postman.

2. **Partager un lien Postman Cloud** (clic droit → Share collection → Get public link ou Invite to workspace).
   → Les membres rejoignent le workspace et accèdent aux requêtes en temps réel.

💡 Astuce : chaque requête peut aussi être convertie en **cURL, Python, JS** via le menu **Code**.

---

## 8️⃣ Monitoring & Maintenance

* **Prometheus** : métriques disponibles sur `http://localhost/prometheus`.
* **Traefik logs** et `docker logs` : diagnostic des services.
* **RabbitMQ UI** : gestion des files d’attente sur `http://localhost:15672`.

### Sauvegarde et restauration des bases

```bash
docker exec product-db pg_dump -U product productdb > backup.sql
docker exec -i product-db psql -U product productdb < backup.sql
```

### Mise à jour

```bash
docker compose pull
docker compose build
docker compose up -d
```

---

## 9️⃣ Arrêt de l’Application

Pour arrêter proprement tous les services :

```bash
docker compose down
```

Pour un arrêt complet incluant la suppression des volumes :

```bash
docker compose down -v
```

---

## 🔟 Structure du Projet

* `/CI-CD` : configuration Docker Compose pour l’orchestration globale (point d’entrée).
* `/{customer-api, product-api, order-api}` : code source des microservices.
* `/jwt-auth` : service d’authentification Forward Auth.
* `/keycloak` : configuration du realm Keycloak.
* `/*-action` : actions GitHub pour l’intégration et le déploiement continus (CI/CD).

---

## ✅ Points à ajouter pour une documentation optimale

* **Captures d’écran** : Traefik, Keycloak, Prometheus, RabbitMQ.
* **Schémas d’architecture** : réseaux, pipeline CI/CD.
* **Collection Postman exportée** en `.json` jointe au dépôt.
* **Description des pipelines CI/CD** (GitHub Actions ou autre).
* **Plan de sauvegarde automatisée** et stratégie de restauration.
* **Note sur la mise en production sécurisée (HTTPS avec Traefik)**.

---

## Auteurs

GIRARD Anthony, FIACSAN Nicolas, QUACH Simon, PRUJA Benjamin
Projet MSPR TPRE814 — EPSI 2024-2025
