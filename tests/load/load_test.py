from locust import HttpUser, task, between
import requests
import logging

# Configure le logger pour qu'il affiche tout
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class APIUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        token_url = "http://localhost/auth/realms/paye-ton-kawa/protocol/openid-connect/token"
        data = {
            "client_id": "gateway",
            "grant_type": "password",
            "username": "admin",
            "password": "admin"
        }

        logger.info("=== Tentative de récupération du token ===")
        logger.debug(f"POST {token_url} avec data={data}")

        try:
            response = requests.post(token_url, data=data)
            logger.debug(f"Réponse brute: {response.status_code} {response.text}")
            response.raise_for_status()
            token = response.json().get("access_token")

            if not token:
                logger.error("Pas de token dans la réponse !!!")
            else:
                logger.info("Token récupéré avec succès")
                logger.debug(f"Token={token[:50]}...")

            self.client.headers = {"Authorization": f"Bearer {token}"}

        except Exception as e:
            logger.exception("Erreur pendant la récupération du token")

    @task(2)
    def get_products(self):
        logger.info("GET /api/product/products")
        with self.client.get("/api/product/products", catch_response=True) as resp:
            if resp.status_code != 200:
                logger.error(f"GET products a échoué: {resp.status_code} {resp.text}")
                resp.failure("Erreur API")
            else:
                logger.info("GET products OK")

    @task(1)
    def get_customers(self):
        logger.info("GET /api/customer/customers")
        with self.client.get("/api/customer/customers", catch_response=True) as resp:
            if resp.status_code != 200:
                logger.error(f"GET customers a échoué: {resp.status_code} {resp.text}")
                resp.failure("Erreur API")
            else:
                logger.info("GET customers OK")

    @task(1)
    def create_order(self):
        payload = {"customer_id": 1, "items": [{"product_id": 1, "quantity": 2}]}
        logger.info(f"POST /api/order/orders payload={payload}")
        with self.client.post("/api/order/orders", json=payload, catch_response=True) as resp:
            if resp.status_code != 201:
                logger.error(f"POST order a échoué: {resp.status_code} {resp.text}")
                resp.failure("Erreur création order")
            else:
                logger.info("POST order OK")
