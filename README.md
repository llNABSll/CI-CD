# CI-CD (Orchestrateur local)

Ce dépôt lance une **plateforme locale** pour le projet MSPR :

* **RabbitMQ** (broker d’événements – UI d’admin incluse)
* **customer-db** (PostgreSQL pour l’API Customer)
* **customer-api** (image Docker pré-buildée)

---

## Prérequis

* Docker Desktop / Docker Engine
* Docker Compose v2 (`docker compose version`)

---

## Démarrage rapide

```bash
# depuis la racine du dépôt CI-CD
docker compose up -d
```

**Endpoints :**

* **Swagger Customer API** : [http://localhost:8000/docs](http://localhost:8000/docs)
* **RabbitMQ UI** : [http://localhost:15672](http://localhost:15672) (login : `guest` / pass : `guest`)

---

## Services (vue d’ensemble)

| Service        | Image                   | Ports (host)                | Rôle                     |
| -------------- | ----------------------- | --------------------------- | ------------------------ |
| `rabbitmq`     | `rabbitmq:3-management` | `5672` (AMQP), `15672` (UI) | Message broker central   |
| `customer-db`  | `postgres:15`           | — (interne réseau compose)  | Base de données Customer |
| `customer-api` | `mspr/customer-api:dev` | `8000`                      | API REST Customer        |

**Variables injectées dans `customer-api` :**

* `POSTGRES_USER=postgres`
* `POSTGRES_PASSWORD=postgres`
* `POSTGRES_DB=customerdb`
* `POSTGRES_SERVER=customer-db` *(nom du service compose)*
* `POSTGRES_PORT=5432`
* `RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/%2F`

> Le healthcheck Postgres garantit que l’API démarre **après** que la DB soit prête.

---

## Tests rapides (API + DB + Broker)

### 1) CRUD API

```bash
# Lister (peut être vide)
curl -sS http://localhost:8000/api/clients | jq .

# Créer (déclenche un event "customer.created")
curl -sS -X POST http://localhost:8000/api/clients \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com"}' | jq .

# Récupérer par id (remplace <ID>)
curl -sS http://localhost:8000/api/clients/<ID> | jq .

# Mettre à jour (déclenche "customer.updated")
curl -sS -X PUT http://localhost:8000/api/clients/<ID> \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice Updated","email":"alice.updated@example.com"}' | jq .

# Supprimer (déclenche "customer.deleted")
curl -sS -X DELETE http://localhost:8000/api/clients/<ID> | jq .
```

### 2) Vérifier RabbitMQ

* Ouvrir l’UI : [http://localhost:15672](http://localhost:15672) (guest/guest)
* **Exchanges** → tu dois voir **`customer_events`** (créé lors du premier publish).

*(Optionnel – voir le contenu des messages)*

1. **Queues** → *Add a new queue* → `debug.customer` (durable)
2. **Exchanges → customer\_events → Bindings** → *Add binding* vers `debug.customer`
3. Refaire un POST/PUT/DELETE → **Queues → debug.customer → Get messages**

---

## Cycle de vie

```bash
# Démarrer en arrière-plan
docker compose up -d

# Suivre les logs d’un service
docker compose logs -f customer-api

# Arrêter & supprimer les ressources
docker compose down

# Réinitialiser la DB (supprime le volume)
docker compose down -v
```

---

## Étapes suivantes (évolution de la plateforme)

* Ajouter **product-api** et **order-api** sur le même modèle :

  * 1 DB Postgres par API
  * Toutes connectées au **même** RabbitMQ (`RABBITMQ_URL` identique)
  * Exchanges dédiés (`product_events`, `order_events`, …)
* **Publier les images** sur un registre (ex. GHCR) pour que les autres puissent lancer la stack sans builder.
* **CI/CD** : pipeline GitHub Actions pour *build & push* des images à chaque push/tag.

---

## Auteurs

PRUJA Benjamin, GIRARD Anthony, FIACSAN Nicolas, QUACH Simon
MSPR TPRE814 — EPSI 2024-2025
