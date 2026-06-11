"""Carga el modelo entrenado desde model.pkl (singleton)."""
import pickle
from pathlib import Path

_bundle = None


def load_bundle() -> dict:
    """Carga el bundle {model, scaler, features} una sola vez."""
    global _bundle
    if _bundle is None:
        model_path = Path(__file__).parent / "model.pkl"
        if not model_path.exists():
            raise FileNotFoundError(
                f"model.pkl no encontrado en {model_path}. "
                "Ejecuta U6_DESPLIEGUE.ipynb primero."
            )
        with open(model_path, "rb") as f:
            _bundle = pickle.load(f)
    return _bundle