from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from . import healthcheck

router = APIRouter(prefix="", tags=["compatibility"], redirect_slashes=False)


@router.get("/latest/", deprecated=True)
def redirect_latest():
    return RedirectResponse(healthcheck.router.url_path_for("latest"))
