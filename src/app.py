import logging
import uvicorn
from typing import Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from kamatera.Kamatera_cloud_management import KamateraCloudManagement
from kamatera.auth_kamatera import get_kamatera_token
import asyncio
import os
from contextlib import asynccontextmanager
from logger import configure_logging, get_logger

# Configure logging early using our central helper (reads LOG_LEVEL env var)
configure_logging()
logger = get_logger(__name__)

# mount static files (expects `static/` next to this file)
templates = Jinja2Templates(directory="template")


async def _token_refresher_loop(interval_seconds: int = 55 * 60) -> None:
    """Background loop that refreshes Kamatera token every `interval_seconds`.

    It reads `KAMATERA_CLIENT_ID` and `KAMATERA_SECRET` from env. If present,
    it calls `get_kamatera_token` and writes the returned token to
    `KAMATERA_API_KEY` in the process environment so route handlers can
    read it via getenv.
    """
    while True:
        try:
            client_id: str = os.getenv("KAMATERA_CLIENT_ID")
            secret: str = os.getenv("KAMATERA_SECRET")
            if client_id and secret:
                logger.info("Refreshing Kamatera token via client_id/secret")
                try:
                    auth: dict[str, str] = get_kamatera_token(client_id=client_id, secret=secret)
                    token: str = auth.get("token")
                    if token:
                        os.environ["KAMATERA_API_KEY"] = token
                        logger.info("KAMATERA_API_KEY refreshed and set in environment")
                    else:
                        logger.warning("Token not returned by get_kamatera_token: %s", auth)
                except Exception as exc:
                    logger.exception("Error while fetching Kamatera token: %s", exc)
            else:
                # Use WARNING so the absence of credentials is visible at normal log levels
                logger.warning(
                    "KAMATERA_CLIENT_ID/KAMATERA_SECRET not set; token refresh skipped. "
                    "Either set KAMATERA_API_KEY or provide KAMATERA_CLIENT_ID and KAMATERA_SECRET."
                )
        except Exception:
            logger.exception("Unexpected error in token refresher loop")

        await asyncio.sleep(interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan manager that starts/stops the token refresher task.

    Starts an asyncio task that refreshes the Kamatera token periodically and
    stores it in the process environment. The task is cancelled on shutdown.
    """
    task: Optional[asyncio.Task] = None

    def _has_kamatera_credentials() -> bool:
        """Return True if the process has sufficient Kamatera credentials.

        Sufficient credentials are either:
        - an existing ``KAMATERA_API_KEY`` environment variable, or
        - both ``KAMATERA_CLIENT_ID`` and ``KAMATERA_SECRET`` environment variables.
        """
        api = os.getenv("KAMATERA_API_KEY")
        client = os.getenv("KAMATERA_CLIENT_ID")
        secret = os.getenv("KAMATERA_SECRET")
        return bool(api or (client and secret))
    try:
        # Fail fast: if we don't have any Kamatera credentials, stop startup so
        # the operator notices and provides proper configuration. Do not log
        # actual credential values (avoid leaking secrets).
        if not _has_kamatera_credentials():
            logger.error(
                "Missing Kamatera credentials: please set KAMATERA_API_KEY or "
                "KAMATERA_CLIENT_ID and KAMATERA_SECRET in the environment."
            )
            # Raising here prevents the application from starting silently without creds
            raise RuntimeError(
                "Kamatera credentials missing: set KAMATERA_API_KEY or KAMATERA_CLIENT_ID/KAMATERA_SECRET"
            )

        task = asyncio.create_task(_token_refresher_loop())
        logger.info("Started Kamatera token refresher task (lifespan)")
        yield
    finally:
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info("Token refresher task cancelled (lifespan)")
                raise


# Create app with lifespan manager
app = FastAPI(title="Kamatera Cloud IHM", lifespan=lifespan)

# mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")

# include API routers (serve JSON endpoints under /api)
from route.list_route import router as list_router
from route.control_route import router as control_router

app.include_router(list_router, prefix="/api")
app.include_router(control_router, prefix="/api")


@app.get(
    "/",
    response_class=HTMLResponse,
    description="Affiche une page HTML conviviale listant les serveurs Kamatera."
    )
async def ui_list_servers(request: Request):
    """Render a user-friendly HTML page showing Kamatera servers.

    The template is rendered without server-side API calls. The front-end
    JavaScript will fetch `/api/servers` and populate the page dynamically.
    """
    return templates.TemplateResponse("index.html", {"request": request, "servers": None, "error": None})


@app.get(
    "/health",
    response_class=JSONResponse,
    description="Vérifie que l'API est opérationnelle."
)
async def health_check():
    # Report basic app health plus whether Kamatera credentials are available.
    has_api = bool(os.getenv("KAMATERA_API_KEY"))
    has_client = bool(os.getenv("KAMATERA_CLIENT_ID") and os.getenv("KAMATERA_SECRET"))
    auth_method = None
    if has_api:
        auth_method = "api_key"
    elif has_client:
        auth_method = "client_credentials"

    return {
        "status": "Up",
        "kamatera": {
            "credentials_present": has_api or has_client,
            "auth_method": auth_method,
        },
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
