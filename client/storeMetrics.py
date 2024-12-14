import datetime

from sqlalchemy import create_engine, Column, Integer, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import client_config

Base = declarative_base()


class SystemMetrics(Base):
    __tablename__ = 'system_metrics'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    cpu_usage = Column(Float)
    ram_usage = Column(Float)
    disk_usage = Column(Float)
    uptime = Column(Float)
    temperature = Column(Float)


class StoreMetrics:
    def __init__(self):
        engine_url = f"{client_config.POSTGRES_PROTOCOL}://{client_config.POSTGRES_USERNAME}:{client_config.POSTGRES_PASSWORD}@{client_config.POSTGRES_HOSTNAME}:{client_config.POSTGRES_PORT}/{client_config.POSTGRES_METRICS_DB}"
        temp_engine_url = "postgresql://postgres:admin@postgres_server:5432/metrics_db"
        engine = create_engine(engine_url)
        Session = sessionmaker(bind=engine)
        self.session = Session()

        Base.metadata.create_all(engine)

    def store_metrics(self, metrics):
        try:
            print("Received metrics:", metrics)
            metric = SystemMetrics(
                cpu_usage=metrics["cpu_usage"],
                ram_usage=metrics["ram_usage"],
                disk_usage=metrics["disk_usage"],
                uptime=metrics["device_uptime"],
                temperature=metrics["device_temperature"]
            )
            self.session.add(metric)
            self.session.commit()
            print("Metrics saved to DB.")
        except Exception as e:
            print(f"Error saving to the database: {e}")
            self.session.rollback()
        finally:
            self.session.close()
