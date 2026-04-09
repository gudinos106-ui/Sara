from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class Transaccion(BaseModel):
    """
    Modelo de datos para validar cada fila del estado de cuenta.
    Esto asegura que no entren datos basura al sistema.
    """
    fecha: str = Field(..., description="Fecha de la transacción")
    descripcion: str = Field(..., description="Concepto o comercio")
    monto: float = Field(..., gt=0, description="El monto debe ser mayor a cero")
    categoria: Optional[str] = "❓ Otros"
    
    @validator('monto')
    def validar_monto(cls, v):
        # Aquí Pydantic asegura que el monto sea un número real
        return round(v, 2)

class ResumenFinanciero(BaseModel):
    """Modelo para el resumen total del dashboard"""
    total_gastos: float
    cantidad_transacciones: int
    fecha_proceso: datetime = Field(default_factory=datetime.now)
