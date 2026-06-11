"""
diagnostico_ia_nano.py
Ejecutar con: conda run -n ia_nano python diagnostico_ia_nano.py
"""
import sys
import subprocess
print(f"Python: {sys.version[:30]}")
print(f"Ejecutable: {sys.executable}")
results = []

# ── matplotlib ──────────────────────────────────────
try:
    import importlib, matplotlib
    # Verificar que scale.py funciona (el que falla)
    from matplotlib import scale as _scale
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(); plt.close(fig)  # smoke test
    results.append(('matplotlib', 'OK', matplotlib.__version__))
except Exception as e:
    err = str(e)[:70]
    results.append(('matplotlib', 'FALLA', err))
    # Intentar auto-reparar
    print(f"  [AUTO-FIX] Intentando instalar matplotlib==3.9.4...")
    r = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '-q', '--force-reinstall', 'matplotlib==3.9.4'],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        print("  [AUTO-FIX] matplotlib reinstalado. Reinicia el kernel Jupyter.")
    else:
        print(f"  [AUTO-FIX] Error: {r.stderr[-100:]}")

# ── langgraph ───────────────────────────────────────
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph.message import add_messages
    # langgraph 1.x no tiene __version__ en el modulo raiz
    import importlib.metadata
    ver = importlib.metadata.version('langgraph')
    results.append(('langgraph', 'OK', ver))
except Exception as e:
    results.append(('langgraph', 'FALLA', str(e)[:70]))

# ── langchain ───────────────────────────────────────
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
    import langchain
    results.append(('langchain', 'OK', langchain.__version__))
except Exception as e:
    results.append(('langchain', 'FALLA', str(e)[:70]))

# ── neo4j ───────────────────────────────────────────
try:
    from neo4j import GraphDatabase
    import importlib.metadata
    ver = importlib.metadata.version('neo4j')
    results.append(('neo4j', 'OK', ver))
except Exception as e:
    results.append(('neo4j', 'FALLA', str(e)[:70]))

# ── scikit-learn ────────────────────────────────────
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import SVC
    from sklearn.neural_network import MLPClassifier
    import sklearn
    results.append(('scikit-learn', 'OK', sklearn.__version__))
except Exception as e:
    results.append(('scikit-learn', 'FALLA', str(e)[:70]))

# ── shap ────────────────────────────────────────────
try:
    import shap
    import importlib.metadata
    ver = importlib.metadata.version('shap')
    results.append(('shap', 'OK', ver))
except Exception as e:
    results.append(('shap', 'FALLA', str(e)[:70]))

# ── chromadb ────────────────────────────────────────
try:
    import chromadb
    results.append(('chromadb', 'OK', chromadb.__version__))
except Exception as e:
    results.append(('chromadb', 'FALLA', str(e)[:70]))

# ── pandas ──────────────────────────────────────────
try:
    import pandas
    results.append(('pandas', 'OK', pandas.__version__))
except Exception as e:
    results.append(('pandas', 'FALLA', str(e)[:70]))

# ── langsmith ───────────────────────────────────────
try:
    import langsmith
    import importlib.metadata
    ver = importlib.metadata.version('langsmith')
    results.append(('langsmith', 'OK', ver))
except Exception as e:
    results.append(('langsmith', 'FALLA', str(e)[:70]))

# ── Mostrar resultados ──────────────────────────────
print()
print('=' * 58)
print('  RESULTADO DEL DIAGNOSTICO — ENTORNO ia_nano')
print('=' * 58)
ok_count = 0
for name, status, info in results:
    icon = '✓ OK  ' if status == 'OK' else '✗ FALLA'
    print(f'  [{icon}] {name:<20} {info}')
    if status == 'OK':
        ok_count += 1
print('=' * 58)
print(f'  {ok_count}/{len(results)} paquetes funcionando correctamente')
if ok_count == len(results):
    print('  ✓ ENTORNO LISTO — puedes ejecutar los notebooks')
else:
    print('  ⚠ Algunos paquetes fallan. Reinicia Jupyter Kernel y reintenta.')
print('=' * 58)
