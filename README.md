# DOCX to HTML para Revistas Científicas (OJS Friendly)

Este proyecto convierte artículos científicos escritos en **Microsoft Word (.docx)** a **HTML estructurado y estilizado**, manteniendo:

- Orden real del documento (párrafos + tablas)
- Títulos en español e inglés
- Autores y afiliaciones
- Resumen y Abstract
- Negritas, cursivas e hipervínculos
- Tablas en la posición correcta
- Listas numeradas y con viñetas
- Estilos CSS incrustados compatibles con OJS e índices académicos

Debes de cambiarle el formato al texto que quieres que resalte en el HTMl, en word deberas de Usar Titulos, Subtitulois y Heading 2 para que el script pueda identificarlo y convertirlo a HTML, las tablas y las vinetas se identifican automaticamente.

Coloca tus archivos `.docx` dentro de la carpeta `docx/`. Al ejecutar el script, se generará un `.html` por cada documento dentro de la carpeta `html/`, con el mismo nombre de archivo.

Si un artículo no usa los estilos de Word "Título", "Subtítulo" y "Encabezado" (por ejemplo, solo tiene texto en negrita), el script no podrá identificar el título, autores ni secciones. Antes de convertir, ejecuta:

```
python3 normalize_docx_styles.py
```

Esto revisa cada `.docx` en `docx/` y aplica automáticamente los estilos correctos (Título al primer párrafo, Subtítulo al segundo, y Heading 2 a encabezados como RESUMEN, ABSTRACT, INTRODUCCIÓN, MÉTODOS, RESULTADOS, DISCUSIÓN, CONCLUSIONES y REFERENCIAS) sin modificar el resto del contenido.

## 🖥️ App de escritorio

También hay una app de escritorio (`desktop_app.py`) que hace lo mismo de forma visual: seleccionas uno o varios `.docx` desde cualquier carpeta, la app los copia a `docx/`, los normaliza y los convierte, y muestra una vista previa del HTML resultante dentro de la misma ventana (el estilo/CSS de la revista es exactamente el mismo que genera `script.py`, no se toca).

```
python3 desktop_app.py
```

Requiere `pywebview` (incluido en `requirements.txt`).

🐍 Requisitos

Python 3.9 o superior

pip

Para correr el script deberas de tener instalado python y la libreria python-docx, puedes instalarla con el comando: pip install python-docx o usar el archivo requirements.txt
pip install -r requirements.txt

El HTML generado puede subirse directamente a **OJS** o utilizarse como versión HTML del artículo.

---

## 📁 Estructura del proyecto

```text
.
├── script.py
├── README.md
├── docx/
│   └── articulo.docx
└── html/
    └── articulo.html
```
