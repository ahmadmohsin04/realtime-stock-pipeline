from pydantic import BaseModel, field_validator
from datetime import datetime

class PriceTick(BaseModel):
    ticker:str
    timestamp:datetime
    open : float
    high:float
    low:float
    close:float
    volume:float

    @field_validator("close")
    @classmethod
    def close_must_be_positive(cls,v):
        if v<=0:
            raise ValueError("close price must be positive")
        return v