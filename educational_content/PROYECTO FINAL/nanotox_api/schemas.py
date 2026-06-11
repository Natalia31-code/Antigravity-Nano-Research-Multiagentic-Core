"""Schemas Pydantic para la API de predicción de nanotoxicidad."""
from pydantic import BaseModel, Field
from typing import Optional


class NanoParticleInput(BaseModel):
    """Propiedades fisicoquímicas de la nanopartícula a evaluar."""
    core_size_nm:          float = Field(..., gt=0,   description="Tamaño de núcleo en nm (ej. 25.0)")
    zeta_potential_mv:     float = Field(...,          description="Potencial zeta en mV (ej. -15.0)")
    surface_area_m2g:      float = Field(..., gt=0,   description="Área superficial en m²/g (ej. 45.0)")
    concentration_ug_ml:   float = Field(..., gt=0,   description="Concentración en µg/mL (ej. 50.0)")
    exposure_time_h:       float = Field(..., gt=0,   description="Tiempo de exposición en horas (ej. 24)")
    material:    Optional[str] = Field(None,           description="Material: ZnO, TiO2, Ag, Au, Fe3O4")
    cell_line:   Optional[str] = Field(None,           description="Línea celular: HeLa, A549, HepG2")


class ToxicityPrediction(BaseModel):
    """Resultado de la predicción de toxicidad."""
    nanoparticle_query:   str
    toxic:                bool
    probability_toxic:    float = Field(..., description="Probabilidad de ser tóxico (0.0–1.0)")
    risk_level:           str   = Field(..., description="BAJO | MODERADO | ALTO")
    model_used:           str
    recommendation:       str