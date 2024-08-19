"""Param Grid Models."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from itertools import product


class ParamGrid(BaseModel):
    """Parameter Grid Model."""

    model: str = Field(
        description="The name of the model (e.g., 'TradeRule', 'ExecutionRule')."
    )
    params: Dict[str, List[Any]] = Field(
        description="Dictionary of parameter names and list of possible values."
    )

    def generate_combinations(self):
        """Generate all combinations of the parameter grid."""
        keys, values = zip(*self.params.items())
        for combination in product(*values):
            yield dict(zip(keys, combination))
