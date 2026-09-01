from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///agentcart.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProductModel(Base):
    __tablename__ = "products"
    
    product_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False)
    description = Column(String)

def init_db():
    """Initializes the database and seeds initial inventory if empty."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(ProductModel).count() == 0:
        initial_products = [
            ProductModel(product_id="item_001", name="Superfast 65W Phone Charger", price=1299, stock=10, description="High-speed GaN charger compatible with all modern smartphones."),
            ProductModel(product_id="item_002", name="Type-C Braided Cable 2m", price=499, stock=25, description="Durable fast-charging and data transfer cable.")
        ]
        db.add_all(initial_products)
        db.commit()
    db.close()