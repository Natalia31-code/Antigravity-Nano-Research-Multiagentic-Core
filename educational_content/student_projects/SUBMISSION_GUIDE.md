# 🎓 Guía de Entrega de Proyectos Finales

**Versión**: 1.0  
**Fecha**: Junio 2026  
**Curso**: IA Aplicada a Nanotecnología  
**Instructor**: Mtro. Luis José Yudico Anaya ([@ljyudico](https://github.com/ljyudico))

---

## 🎯 ¿Por qué Archivar tu Proyecto?

Al completar la Unidad 6, tu proyecto será **archivado permanentemente** en este repositorio institucional con:

✅ **Preservación garantizada**: Tu código permanecerá accesible por 20+ años  
✅ **DOI académico**: Identificador único para citarlo en CV, LinkedIn, papers  
✅ **Portfolio verificable**: Prueba oficial de tus habilidades técnicas  
✅ **Atribución clara**: Commits firmados con tu nombre/email  
✅ **Backup institucional**: Aunque borres tu repo personal, esto permanece  

**Ejemplo de citación que podrás usar:**

> Pérez, N. (2026). *NanoTox AI: Multi-Agent System for Nanoparticle Toxicity Prediction*.  
> Antigravity Nano Research - Student Projects Collection.  
> DOI: 10.5281/zenodo.7654321

---

## 📋 Checklist Pre-Entrega

Antes de enviar tu Pull Request, verifica:

### ✅ **Código Completo**
- [ ] Todo el código fuente en `/src/` (Python files)
- [ ] Notebooks en `/notebooks/` (con outputs guardados)
- [ ] Archivo `requirements.txt` con todas las dependencias
- [ ] Archivo `.gitignore` (no subir `__pycache__`, `.env`, datos grandes)

### ✅ **Documentación**
- [ ] `README.md` completo (ver template)
- [ ] Docstrings en todas las funciones
- [ ] `metadata.json` con tus datos (ver template)
- [ ] Licencia elegida (MIT, Apache-2.0, o GPL-3.0)

### ✅ **Calidad del Código**
- [ ] Código ejecutable sin errores
- [ ] Nombres de variables descriptivos (no `x`, `temp`, `data2`)
- [ ] Comentarios explicativos en secciones complejas
- [ ] Formato consistente (idealmente con `black` o `autopep8`)

### ✅ **Contenido Académico**
- [ ] Archivos JSON de la Unidad 6 completados:
  - `mi_proyecto_propuesta.json`
  - `mi_proyecto_plan_tecnico.json`
  - `mi_proyecto_reporte_final.json`
  - `mi_reflexion_final.json`

---

## 🚀 Proceso de Entrega (Paso a Paso)

### **Paso 1: Preparar tu Repositorio Local**

#### **Opción A: Ya tienes un repositorio de GitHub**

```bash
# 1. Clona tu repositorio si no lo tienes local
git clone https://github.com/TU-USUARIO/tu-proyecto.git
cd tu-proyecto

# 2. Limpia archivos innecesarios
git rm -r __pycache__ .env *.pyc  # Si existen
echo "__pycache__/
*.pyc
.env
data/raw/*
!data/raw/.gitkeep" > .gitignore

# 3. Asegúrate de tener README.md y metadata.json
# (Usa los templates de este repositorio)

# 4. Commit final
git add .
git commit -m "🎓 Versión final para entrega académica"
git push origin main
```

#### **Opción B: Solo tienes archivos locales (sin Git)**

```bash
# 1. Inicializa Git en tu carpeta de proyecto
cd /ruta/a/tu/proyecto
git init
git add .
git commit -m "🎓 Proyecto final - Versión para entrega"

# 2. Crea un repositorio en GitHub (público)
# Ir a: https://github.com/new
# Nombre sugerido: tu-proyecto-nombre

# 3. Conecta y sube
git remote add origin https://github.com/TU-USUARIO/tu-proyecto.git
git branch -M main
git push -u origin main
```

---

### **Paso 2: Fork del Repositorio Principal**

```bash
# 1. Haz fork del repositorio institucional
# Ir a: https://github.com/Multiagent-AI-Lab/Antigravity-Nano-Research-Multiagentic-Core
# Click en "Fork" (arriba derecha)

# 2. Clona TU fork
git clone https://github.com/TU-USUARIO/Antigravity-Nano-Research-Multiagentic-Core.git
cd Antigravity-Nano-Research-Multiagentic-Core

# 3. Crea una rama para tu entrega
git checkout -b student/tu-nombre-proyecto
```

---

### **Paso 3: Copiar tu Proyecto a la Estructura**

```bash
# 1. Copia el template
cp -r educational_content/student_projects/templates/project_template \
      educational_content/student_projects/2026_generation/tu-proyecto-nombre

# 2. Copia TU código al template
# Estructura objetivo:
# educational_content/student_projects/2026_generation/tu-proyecto-nombre/
# ├── README.md          ← Adapta el template con tu info
# ├── LICENSE            ← Elige MIT, Apache-2.0 o GPL-3.0
# ├── requirements.txt   ← Copia el tuyo
# ├── metadata.json      ← Completa con tus datos (ver template)
# ├── src/               ← Copia tu código fuente aquí
# ├── notebooks/         ← Copia tus notebooks aquí
# ├── data/              ← Solo datos de ejemplo (< 10MB)
# ├── tests/             ← Si tienes tests
# └── docs/              ← Documentación adicional

# 3. Copia tus archivos (ejemplo)
cp -r ~/mi-proyecto/src/* educational_content/student_projects/2026_generation/tu-proyecto-nombre/src/
cp -r ~/mi-proyecto/notebooks/* educational_content/student_projects/2026_generation/tu-proyecto-nombre/notebooks/
cp ~/mi-proyecto/requirements.txt educational_content/student_projects/2026_generation/tu-proyecto-nombre/
```

---

### **Paso 4: Completar Metadata**

Edita `educational_content/student_projects/2026_generation/tu-proyecto-nombre/metadata.json`:

```json
{
  "project": {
    "name": "tu-proyecto-nombre",
    "title": "Título Completo del Proyecto",
    "generation": "2026",
    "submission_date": "2026-06-12"
  },
  "author": {
    "name": "Tu Nombre Completo",
    "github": "tu-usuario-github",
    "email": "tu-email@university.edu",
    "student_id": "20230123",
    "orcid": "0000-0002-XXXX-XXXX"
  },
  "academic": {
    "course": "IA Aplicada a Nanotecnología",
    "university": "Universidad XYZ",
    "advisor": "Mtro. Luis José Yudico Anaya",
    "grade": null,
    "evaluation_date": null
  },
  "technical": {
    "primary_language": "Python",
    "frameworks": ["PyTorch", "LangChain", "FastAPI"],
    "ml_models": ["Graph Neural Networks", "Random Forest"],
    "agent_framework": "LangChain"
  },
  "research": {
    "area": "Nanotoxicología",
    "keywords": ["nanoparticles", "toxicity prediction", "GNN"],
    "abstract": "Breve resumen del proyecto (max 300 palabras)",
    "doi": null,
    "paper_url": null
  },
  "repository": {
    "original": "https://github.com/TU-USUARIO/tu-proyecto",
    "institutional_fork": null,
    "archive_commit": null,
    "license": "MIT"
  }
}
```

**Campos importantes:**
- `author.email`: Usa tu email institucional
- `author.orcid`: Opcional, pero recomendado (obtén uno gratis en https://orcid.org)
- `technical.frameworks`: Lista todas las librerías principales
- `research.abstract`: Resume qué hace tu proyecto y por qué es importante
- `repository.original`: URL de TU repositorio personal

---

### **Paso 5: Actualizar README del Proyecto**

Edita `educational_content/student_projects/2026_generation/tu-proyecto-nombre/README.md` usando el template proporcionado. Debe incluir:

- Descripción del proyecto (2-3 párrafos)
- Instrucciones de instalación paso a paso
- Ejemplos de uso con código
- Resultados con métricas
- Estructura del proyecto
- Licencia y contacto

---

### **Paso 6: Commit y Push**

```bash
# 1. Verificar qué archivos agregaste
git status

# 2. Agregar todo
git add educational_content/student_projects/2026_generation/tu-proyecto-nombre/

# 3. Commit con mensaje descriptivo
git commit -m "🎓 Proyecto Final: [Nombre del Proyecto] - [Tu Nombre]

- Implementación completa de [describe funcionalidad principal]
- Stack: Python, PyTorch, LangChain, FastAPI
- Incluye notebooks de análisis y documentación completa
- Metadata JSON completado
- Repositorio original: https://github.com/TU-USUARIO/tu-proyecto"

# 4. Push a TU fork
git push origin student/tu-nombre-proyecto
```

---

### **Paso 7: Abrir Pull Request**

1. **Ir a tu fork en GitHub**:  
   `https://github.com/TU-USUARIO/Antigravity-Nano-Research-Multiagentic-Core`

2. **Verás un banner**: "tu-nombre-proyecto had recent pushes"  
   → Click en **"Compare & pull request"**

3. **Completar el formulario del PR**:

**Título**:
```
🎓 Proyecto Final: [Nombre del Proyecto] - [Tu Nombre]
```

**Descripción**:
```markdown
## 📋 Información del Proyecto

- **Nombre del proyecto**: [Nombre]
- **Autor**: [Tu nombre completo]
- **GitHub**: [@tu-usuario](https://github.com/tu-usuario)
- **Email**: tu-email@university.edu
- **Generación**: 2026

---

## 🎯 Resumen del Proyecto

[2-3 párrafos explicando qué hace tu proyecto, qué problema resuelve, y por qué es interesante]

---

## 🛠️ Stack Tecnológico

- Python 3.11
- [Framework ML]: PyTorch / scikit-learn / TensorFlow
- [Framework Agentes]: LangChain / CrewAI / AutoGen
- [Deployment]: FastAPI + Docker
- [Otras herramientas importantes]

---

## 📊 Resultados Destacados

- Métrica 1: [Ej: Accuracy 87%]
- Métrica 2: [Ej: Latencia < 200ms]
- Métrica 3: [Ej: API desplegada en Render]

---

## 🔗 Enlaces

- **Repositorio original**: https://github.com/TU-USUARIO/tu-proyecto
- **Demo (si aplica)**: https://tu-proyecto.render.com
- **Video demo (opcional)**: https://youtube.com/...

---

## ✅ Checklist de Entrega

- [x] Código completo en `/src/`
- [x] Notebooks en `/notebooks/`
- [x] `README.md` completo
- [x] `metadata.json` completado
- [x] `requirements.txt` actualizado
- [x] Licencia incluida
- [x] Archivos JSON de Unidad 6
- [x] Código ejecutable sin errores

---

## 🙏 Agradecimientos

Agradezco al Mtro. Luis José Yudico Anaya por la mentoría durante el desarrollo de este proyecto.
```

4. **Labels**: Agregar etiqueta `student-project`

5. **Click en "Create pull request"**

---

## ⏳ ¿Qué Pasa Después?

### **Revisión (1-3 días hábiles)**

El instructor revisará:
- ✅ Calidad del código
- ✅ Documentación completa
- ✅ Cumplimiento de objetivos de la Unidad 6
- ✅ Formato y estructura

### **Después del Merge**

1. **Tu proyecto está archivado**: Visible en  
   `https://github.com/Multiagent-AI-Lab/.../student_projects/2026_generation/`

2. **Recibirás calificación**: El instructor actualiza `metadata.json` con tu `grade`

3. **Al final del semestre**: Se crea un **Release** con DOI de Zenodo  
   → Recibirás notificación con tu DOI personal

---

## 🆘 Solución de Problemas Comunes

### **Error: "Permission denied" al hacer push**

```bash
# Asegúrate de estar en TU fork, no en el repo original
git remote -v
# Debe mostrar: origin  https://github.com/TU-USUARIO/Antigravity-Nano...

# Si no es así:
git remote set-url origin https://github.com/TU-USUARIO/Antigravity-Nano-Research-Multiagentic-Core.git
```

### **No sé qué licencia elegir**

- **MIT**: La más permisiva, permite uso comercial sin restricciones
- **Apache-2.0**: Similar a MIT pero con protección de patentes
- **GPL-3.0**: Requiere que trabajos derivados también sean open-source

**Recomendación**: MIT (es la más usada en proyectos académicos)

### **Mi proyecto tiene datos grandes (> 50MB)**

```bash
# NO subas datasets completos
# En su lugar:

# 1. Agrega a .gitignore
echo "data/raw/*.csv
data/processed/*.pkl" >> .gitignore

# 2. Incluye solo archivos de ejemplo pequeños
mkdir -p data/sample
cp data/raw/ejemplo.csv data/sample/  # Solo 100 filas

# 3. En README.md documenta dónde obtener los datos completos
```

---

## 📚 Recursos Adicionales

- **Template completo**: `educational_content/student_projects/templates/project_template/`
- **Guía de Git/GitHub**: https://docs.github.com/es/get-started
- **Markdown Cheatsheet**: https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet

---

## 📧 Contacto

**Dudas sobre el proceso de entrega:**  
Mtro. Luis José Yudico Anaya  
Email: ljyudico@ucemich.edu.mx  
GitHub: [@ljyudico](https://github.com/ljyudico)

---

<div align="center">
  <sub>🎓 Guía de Entrega - Antigravity Nano Research - Generación 2026</sub>
</div>
