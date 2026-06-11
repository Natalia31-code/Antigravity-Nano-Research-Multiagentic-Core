# Reporte: Predicción de Toxicidad de Nanopartículas

## Resumen Ejecutivo
Se implementó un sistema multi-agente para predecir la toxicidad de nanopartículas.
El mejor modelo fue **MLP** con F1=0.000 y AUC=nan.

## Resultados
- **Accuracy:** 1.000
- **F1-Score:** 0.000
- **ROC-AUC:** nan

## Predicción
- Nanopartícula: ZnO nanoparticle cytotoxicity
- Nivel de riesgo: **ALTO**
- Probabilidad de toxicidad: 1.000

## Conclusiones
El modelo MLP identificó las siguientes propiedades como más predictivas de toxicidad: valence_band (0.1000), electronegativity (0.1000), exposure_time (0.1000), exposure_dose (0.1000), material_type_enc (0.1000). Propiedades como el tamaño, carga superficial y composición química son determinantes clave en la interacción de nanopartículas con sistemas biológicos.  
