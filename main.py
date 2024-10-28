import os
import datetime
from selenium import webdriver
from dbmodels import Product
from dotenv import load_dotenv
from typing import Annotated, List
from contextlib import asynccontextmanager
from fastapi import BackgroundTasks, Depends, FastAPI
from sqlmodel import SQLModel, create_engine, Session, select
from crawler import crawl_search_term_carrefour, crawl_remaining_pages_carrefour

load_dotenv()

app = FastAPI()
driver_options = webdriver.FirefoxOptions()
driver_options.add_argument("--headless")
webdriver_timeout = 20

POSTGRES_URI = os.getenv("POSTGRES_URI")
engine = create_engine(POSTGRES_URI)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


@app.get("/product/{keyword}")
def query_product(
    keyword: str, session: SessionDep, background_tasks: BackgroundTasks
) -> List[Product]:
    query = select(Product).where(Product.name.ilike(f"%{keyword}%"))
    products_from_db = session.exec(query).all()
    timestamp = datetime.datetime.now()

    if len(products_from_db) > 0:
        print("returning from db")
        print(len(products_from_db))
        one_week_delta = timestamp - datetime.timedelta(days=7)
        first = products_from_db[0]
        if first.last_updated < one_week_delta:
            print("lastupdated", first.last_updated)
            print("delta", one_week_delta)
            background_tasks.add_task(
                crawl_remaining_pages_carrefour,
                f"https://www.carrefour.com.ar/{keyword}?",
                webdriver.Firefox(options=driver_options),
                webdriver_timeout,
                session,
                timestamp,
            )

        return [product.model_dump() for product in products_from_db]
    else:
        print("returning from selenium")
        next_link = crawl_search_term_carrefour(
            keyword,
            webdriver.Firefox(options=driver_options),
            webdriver_timeout,
            timestamp,
        )

        if next_link is not None:
            background_tasks.add_task(
                crawl_remaining_pages_carrefour,
                next_link,
                webdriver.Firefox(options=driver_options),
                webdriver_timeout,
                session,
                timestamp,
            )

        return [product.model_dump() for product in session.exec(query).all()]
