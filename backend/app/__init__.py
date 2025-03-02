import azure.functions as func
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .controller import Controller
from .schemas import Account, SpendingSummary, Test, Transaction

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


con = Controller()


@app.get("/test")
async def test() -> Test:
    return con.test()


@app.get("/accounts")
async def accounts() -> list[Account]:
    return con.get_accounts()


@app.get("/transactions")
async def transactions() -> list[Transaction]:
    return con.get_transactions()


@app.get("/spending_summary")
async def spending_summary() -> SpendingSummary:
    return con.spending_summary()


async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return await func.AsgiMiddleware(app).handle_async(req, context)
