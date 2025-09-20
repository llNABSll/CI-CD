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

## Schéma d'architecture
![Schéma d’architecture PayeTonKawa](assets/images/architecture.png)

---

## 2️⃣ Prérequis

Avant de commencer, assurez-vous d’avoir installé :

* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)
* [Postman](https://www.postman.com/downloads/)

---

## 3️⃣ Lancement de l’Application

L’ensemble de l’écosystème est orchestré via un unique fichier `docker-compose.yml` situé dans le répertoire `CI-CD`.

**Important** : Les autres fichiers `docker-compose.yml` présents dans les répertoires de chaque service sont uniquement destinés aux tests unitaires et **ne doivent pas être utilisés pour le déploiement global**.

### Étape 1 – Créer le fichier `.env` à partir de `env.example`

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

> Ne modifiez pas `env.example` directement : seul le fichier `.env` est lu par `docker compose`.

---

### Étape 2 – Lancer l’écosystème

Depuis le dossier `CI-CD` :

```bash
docker compose up -d 
```

---

## 4️⃣ Accès aux Services

Une fois les conteneurs démarrés, les services sont accessibles via le reverse proxy Traefik sur `http://localhost`.

### Interfaces Web

| Service                               | URL via Traefik               |
| ------------------------------------- | ----------------------------- |
| **Dashboard Traefik**                 | `http://localhost/dashboard/#`|
| **Console d’administration Keycloak** | `http://localhost/auth`       |
| **Interface de gestion RabbitMQ**     | `http://localhost/rabbitmq`   |
| **Interface Prometheus**              | `http://localhost/prometheus` |
| **Interface Grafana**                 | `http://localhost/grafana`    |

### APIs exposées

| Service          | URL de base                     |
| ---------------- | ------------------------------- |
| **Customer API** | `http://localhost/api/customer` |
| **Product API**  | `http://localhost/api/product`  |
| **Order API**    | `http://localhost/api/order`    |

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

* Contenu global du json d'import:

Realm: paye-ton-kawa (token 30 min) • Clients (public): gateway, product-api, order-api, customer-api

Import: Keycloak → Add Realm → Import → keycloak/realm-paye-ton-kawa.json

Users (démo) : admin/admin (tous droits), dev/dev (read-only), demo/demo (read + write commandes/clients)

Démo locale uniquement (changer/désactiver hors démo).

Note : admin/admin, dev/dev, demo/demo sont des utilisateurs du realm (démo locale), pas le compte admin serveur Keycloak.


* Exemple pour obtenir un token :

```bash
curl -X POST \
     -d "client_id=gateway" \
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

## 7️⃣ Tests

Pour effectuer des test automatisés, notamment nos tests unitaires, recettes et intégration,
nous avons utilisés pytest ainsi que behave (plus orienté recette pour ce dernier)

Exemple de commande à lancer dans un terminal:

```bash
pytest --cov=app --cov-report=term-missing
```

Pour vérifier manuellement le bon fonctionnement des APIs, nous utilisons Postman :

* **Collections** : regroupent les requêtes HTTP (URL, en-têtes, corps).
* **Workspaces** : espaces collaboratifs partagés.
* **Desktop Agent** : permet d’exécuter les requêtes locales vers localhost ou les conteneurs.

## 8️⃣ Postman

Un workspace nommé *PayeTonKawa* contient déjà toutes les requêtes utiles (authentification JWT, Produits, Clients, Commandes).

Fichier de collection fourni

Une collection Postman prête à l’emploi est fournie dans le dépôt :

* [CI-CD/postman/PayeTonKawa.postman_collection.json](CI-CD/postman/PayeTonKawa.postman_collection.json)

Importez-la directement dans Postman (**File → Import → Upload Files**) pour retrouver toutes les requêtes prêtes à l’emploi (authentification JWT, APIs Produits/Clients/Commandes…).

Commencer par récupérer le JWT en renseignant correctement le body (pour tester tous les endpoints sans restriction préférez username: admin & password: admin)

Une fois le JWT obtenu il est stocké dans une variable {{ACCESS_TOKEN}} qui est réutilisé par les autres requêtes (afin de ne pas saisir le token à chaque appel)

---

## 9️⃣ Monitoring & Maintenance

* **Prometheus** : métriques disponibles sur `http://localhost/prometheus` (chaque API expose /health et /metrics pour la surveillance).
* **Grafana** : accessible sur `http://localhost/grafana` (login admin/admin par défaut).
  → Importer le dashboard Prometheus fourni (`grafana/dashboard.json`).
* **Traefik logs** et `docker logs` : diagnostic des services.
* **RabbitMQ UI** : gestion des files d’attente sur `http://localhost/rabbitmq`.

Si vous utilisez RabbitMQ derrière Traefik avec un sous-chemin (`/rabbitmq`), ajoutez dans `docker-compose.yml` :
RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS: "-rabbitmq_management path_prefix \"/rabbitmq\""
Sinon, accédez directement à l’UI via [http://localhost:15672](http://localhost:15672).

* **(Optionnel)**
* Alertmanager

Alertmanager complète Prometheus en envoyant des alertes (Slack, e-mail…) lors d’anomalies.

L’UI est disponible sur [http://localhost:9093](http://localhost/9093).

Configuration : observability/alertmanager.yml.

* Tests de montée en charge (Locust)

Locust est intégré pour tester la performance et la scalabilité.

UI : [http://localhost:8089](http://localhost:8089).

Exemple : lancer 100 utilisateurs virtuels avec un ramp-up de 5/s pour simuler du trafic.

Les scénarios de test se trouvent dans tests/load/load_test.py.

### Mise à jour

```bash
docker compose pull
docker compose up -d 
```
Utilisez `docker compose build` seulement si vous modifiez le code ou les Dockerfile locaux.
---

## 🔟  Arrêt de l’Application

Pour arrêter proprement tous les services :

```bash
docker compose down
```

Pour un arrêt complet incluant la suppression des volumes :

```bash
docker compose down -v
```

---

## Structure du Projet

* `/CI-CD` : configuration Docker Compose pour l’orchestration globale (point d’entrée).
* `/{customer-api, product-api, order-api}` : code source des microservices.
* `/jwt-auth` : service d’authentification Forward Auth.
* `/keycloak` : configuration du realm Keycloak.
* `/*-action` : actions GitHub pour l’intégration et le déploiement continus (CI/CD).

---

## Points à ajouter pour une documentation optimale

* **Pipelines CI/CD** : exécuter les tests (`pytest`), calculer la couverture, builder et pousser les images Docker sur GHCR, puis déployer automatiquement (optionnel).

---

## Auteurs

GIRARD Anthony, FIACSAN Nicolas, QUACH Simon, PRUJA Benjamin
Projet MSPR TPRE814 — EPSI 2024-2025
