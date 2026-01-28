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
├── articulo.docx
└── articulo.html
```
