"""Transactional storage of forecasting records and audit entries."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2

from acme_data.platform.persistence import Repository


class DomainRepository(Repository):
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        super().__init__('forecasting', sessions)

    async def save_demand_forecast(self, tenant: str, record: forecasting_v1_forecasting_pb2.DemandForecast) -> None:
        await self.save(tenant, 'DemandForecast', record.demand_forecast_id,
                        record.SerializeToString(deterministic=True))

    async def save_forecast_model(self, tenant: str, record: forecasting_v1_forecasting_pb2.ForecastModel) -> None:
        await self.save(tenant, 'ForecastModel', record.forecast_model_id,
                        record.SerializeToString(deterministic=True))

    async def save_scenario(self, tenant: str, record: forecasting_v1_forecasting_pb2.Scenario) -> None:
        await self.save(tenant, 'Scenario', record.scenario_id,
                        record.SerializeToString(deterministic=True))
