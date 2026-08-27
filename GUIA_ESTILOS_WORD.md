# 📋 Guía de Estilos en Word para el Script de Conversión a HTML

Esta guía describe cómo preparar un documento Word (`.docx`) para que el script `script.py` detecte correctamente cada sección y genere el HTML esperado.

> **Importante:** El script lee los **estilos de Word** (los que aparecen en la barra de estilos de la pestaña "Inicio"), **no** el formato visual (tamaño de fuente, negrita manual, etc.).

---

## Orden y Estilos Requeridos

| Sección | Estilo de Word a aplicar | Notas |
|---------|--------------------------|-------|
| **Título en español** | `Title` (Título) | Debe ser el primer bloque con este estilo |
| **Título en inglés** | `Subtitle` (Subtítulo) | Va inmediatamente después del Title |
| **Autores** | `Normal` (sin `@` ni `orcid`) | Todo párrafo Normal entre el Subtitle y el primer Heading se toma como autor |
| **Afiliaciones** | `Normal` (con `@` o `orcid` en el texto) | Si el texto contiene `@` o la palabra `orcid`, se clasifica como afiliación |
| **RESUMEN** | `Heading 1/2/3` (cualquier nivel) | El texto debe contener la palabra **"RESUMEN"** |
| **Contenido del resumen** | `Normal` | Párrafos normales después del heading RESUMEN |
| **ABSTRACT** | `Heading 1/2/3` (cualquier nivel) | El texto debe contener la palabra **"ABSTRACT"** |
| **Contenido del abstract** | `Normal` | Párrafos normales después del heading ABSTRACT |
| **Secciones del cuerpo** | `Heading 1`, `Heading 2`, etc. | Cualquier heading que NO diga RESUMEN ni ABSTRACT |
| **Párrafos del cuerpo** | `Normal` | Texto estándar del artículo |
| **Listas con viñetas** | Usar viñetas de Word (`List Bullet` o la herramienta de viñetas) | Se convierte a `<ul>` |
| **Listas numeradas** | Usar numeración de Word (`List Number` o la herramienta de numeración) | Se convierte a `<ol>` |
| **Tablas** | Insertar tabla normal de Word | Se convierte automáticamente a `<table>` |
| **Negritas / Itálicas** | Formato de carácter normal (**B** / *I*) | Se convierten a `<strong>` / `<em>` |
| **Hipervínculos** | Insertar hipervínculo de Word (Ctrl+K / Cmd+K) | Se convierte a `<a href="..." target="_blank">` |
| **Imágenes** | — | Se ignoran intencionalmente, no se incluyen en el HTML |

---

## Resumen Visual del Flujo

```
📄 Word Document
├── [Title]      → "Título del artículo en español"
├── [Subtitle]   → "Article title in English"
├── [Normal]     → "Autor 1, Autor 2"              ← autores
├── [Normal]     → "correo@email.com, ORCID..."     ← afiliación (tiene @ / orcid)
├── [Heading]    → "RESUMEN"                        ← activa sección resumen
├── [Normal]     → "Texto del resumen..."
├── [Heading]    → "ABSTRACT"                       ← activa sección abstract
├── [Normal]     → "Abstract text..."
├── [Heading]    → "INTRODUCCIÓN"                   ← sección del cuerpo
├── [Normal]     → "Texto del cuerpo..."
├── [Table]      → tabla automática
└── [Heading]    → "REFERENCIAS"
```

---

## ⚠️ Errores Comunes a Evitar

### 1. No aplicar los estilos "a mano"
Si solo cambias el tamaño de fuente y pones negrita en vez de usar el estilo `Heading 1` desde la barra de estilos, el script **no lo detectará** como heading.

### 2. El orden importa
El script espera esta secuencia:

```
Title → Subtitle → Autores/Afiliaciones → RESUMEN → ABSTRACT → Cuerpo
```

Si se altera el orden, las secciones pueden clasificarse incorrectamente.

### 3. No renombrar las secciones clave
- El heading debe contener exactamente la palabra **"RESUMEN"** (no "Resúmen", "Resume", etc.)
- El heading debe contener exactamente la palabra **"ABSTRACT"** (no "Summary", etc.)
- No importan mayúsculas/minúsculas, pero sí la palabra exacta.

### 4. Autores van ANTES del primer Heading
Todo lo que esté en estilo `Normal` entre el `Subtitle` y el primer `Heading` se captura como autor o afiliación. Si pones autores después del primer heading, se perderán.

### 5. Afiliaciones se detectan por contenido
Un párrafo en la zona de autores se clasifica como **afiliación** si contiene:
- El carácter `@` (correo electrónico)
- La palabra `orcid` (en cualquier combinación de mayúsculas/minúsculas)

Si no contiene ninguno de los dos, se clasifica como **nombre de autor**.

---

## Cómo Aplicar Estilos en Word

1. Selecciona el texto o párrafo
2. Ve a la pestaña **Inicio** (Home)
3. En el grupo **Estilos**, selecciona el estilo correspondiente:
   - `Title` para el título principal
   - `Subtitle` para el subtítulo
   - `Heading 1`, `Heading 2`, etc. para secciones
   - `Normal` para párrafos de contenido
4. Para listas, usa los botones de **viñetas** o **numeración** en la barra de herramientas

> **Tip:** Si no ves todos los estilos, haz clic en la flecha pequeña en la esquina inferior derecha del grupo "Estilos" para ver el panel completo.
