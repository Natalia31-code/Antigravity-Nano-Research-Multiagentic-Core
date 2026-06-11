# NanoTox Predictor API

API REST para predicción de toxicidad de nanopartículas mediante Machine Learning.  
**Proyecto Integrador** — Curso de Nanotecnología + IA.

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecutar el servidor

```bash
python app.py
# → http://localhost:8000/docs
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servicio y modelo cargado |
| POST | `/predict` | Predice toxicidad de una nanopartícula |
| GET | `/docs` | Swagger UI interactivo |

## Ejemplo de predicción

```bash
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "core_size_nm": 25.0,
    "zeta_potential_mv": -15.0,
    "surface_area_m2g": 45.0,
    "concentration_ug_ml": 50.0,
    "exposure_time_h": 24.0,
    "material": "ZnO",
    "cell_line": "HeLa"
  }'
```

## Respuesta esperada

```json
{
  "nanoparticle_query": "ZnO (25.0 nm, 50.0 µg/mL)",
  "toxic": false,
  "probability_toxic": 0.23,
  "risk_level": "BAJO",
  "model_used": "RandomForest",
  "recommendation": "Nanopartícula con bajo riesgo de toxicidad."
}
```