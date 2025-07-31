"""
Farmer-related models for the marketplace.

TODO: Contributors should implement:
- FarmerVerification for verification process
- FarmCertification for organic/sustainable certifications
- FarmLocation for detailed geographic data

"""

from .farmer import Farmer

from typing import List

__all__: List[str] = [
    "Farmer",
]
