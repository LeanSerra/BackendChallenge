import os
import datetime
from selenium import webdriver
from dbmodels import Product
from dotenv import load_dotenv
from typing import Annotated, List
from contextlib import asynccontextmanager
from fastapi import BackgroundTasks, Depends, FastAPI
from sqlmodel import SQLModel, create_engine, Session, select
from crawler import scrapers_registry

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
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
            for website, (_, scrape_next) in scrapers_registry.items():
                background_tasks.add_task(
                    scrape_next,
                    f"https://www.{website}.com.ar/{keyword}?",
                    webdriver.Firefox(options=driver_options),
                    webdriver_timeout,
                    session,
                    timestamp,
                )

        return [product.model_dump() for product in products_from_db]
    else:
        for website, (scrape_first, scrape_next) in scrapers_registry.items():
            next_link = scrape_first(
                keyword,
                webdriver.Firefox(options=driver_options),
                webdriver_timeout,
                session,
                timestamp,
            )

            if next_link is not None:
                background_tasks.add_task(
                    scrape_next,
                    next_link,
                    webdriver.Firefox(options=driver_options),
                    webdriver_timeout,
                    session,
                    timestamp,
                )

        return [product.model_dump() for product in session.exec(query).all()]
