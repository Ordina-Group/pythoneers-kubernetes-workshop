from typing import Optional

import pydantic


class Item(pydantic.BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
