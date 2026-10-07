# Extensiones de IngeTrazo · IngeTrazo extensions

**[Español](#español) · [English](#english) · [Português](#português)**

El catálogo que se ve en **https://ingetrazo.com/extensiones**.
The catalog shown at **https://ingetrazo.com/extensiones**.

---

## Español

Esto es un **directorio**, no una tienda. El código de cada extensión vive en
el repositorio de su autor. Aquí solo hay una **ficha** por extensión
(`extensions/<id>.toml`): nombre, descripción, licencia, enlace y la huella
(SHA-256) del archivo exacto que se instala.

### Publicar tu extensión

No hace falta saber Git. Desde el navegador:

1. Publica tu extensión en tu propio repositorio (GitHub, Codeberg, GitLab…)
   con una licencia libre, y crea una **etiqueta** (por ejemplo `v1.0`).
2. Aquí, abre [`TEMPLATE.toml`](TEMPLATE.toml), copia su contenido y pulsa
   **Add file ▸ Create new file** dentro de la carpeta `extensions/`. Ponle
   de nombre `<id>.toml` (por ejemplo `escaleras.toml`) y pega la plantilla.
3. Rellena los campos. Para `sha256`:
   `sha256sum mi_extension.py` (Linux/Mac) o
   `certutil -hashfile mi_extension.py SHA256` (Windows). Si te equivocas,
   la revisión automática te dirá el valor correcto.
4. Opcional: sube una captura a `screenshots/` (png, jpg o webp, menos de
   600 KB, unos 1200×750).
5. Pulsa **Propose changes** y luego **Create pull request**.

Un robot revisa la ficha en un minuto: campos completos, licencia libre,
huella correcta y que el archivo tenga `setup(app)` o una herramienta.
**Lee el código, nunca lo ejecuta.** Si algo falla, el mensaje explica qué
corregir. Después la aprueba una persona que mantiene IngeTrazo y la página
se actualiza sola en unos minutos.

**Nueva versión:** otra pull request cambiando `version`, `download` y
`sha256`. Si la envía la misma cuenta de GitHub que figura en `author_url`,
toca solo tu ficha (y su captura) y la revisión automática no encuentra nada
que leer, **se publica sola**, sin esperar a nadie. Sale como «Comunidad»
hasta que alguien lea el archivo nuevo.

¿Cómo se escribe una extensión? Mira la
[guía de complementos](https://github.com/ingelibre/ingetrazo/blob/main/docs/plugins.md)
y los ejemplos que trae IngeTrazo (*Extensiones ▸ Extensiones de ejemplo*).

### «Revisada» y «Comunidad»

Una extensión es código Python con el mismo acceso a tu computadora que
IngeTrazo, igual que en Blender.

- **Revisada**: alguien que mantiene IngeTrazo leyó **ese archivo exacto**
  (su huella está en `reviewed.toml`). Si sale una versión nueva, vuelve a
  «Comunidad» hasta que alguien la lea.
- **Comunidad**: pasó la revisión automática y se aprobó su ficha, pero
  nadie leyó el código a fondo. Instálala si confías en su autor.

### Para quienes mantienen el catálogo

- **Aprobar una ficha:** abre la pull request, mira el informe del robot
  (pestaña *Checks*: lista lo que usa la red, ejecuta programas o borra
  archivos) y pulsa **Merge**. Listo.
- **Marcarla como revisada:** después de leer el código, añade a
  `reviewed.toml` su `sha256` (un commit directo en la web).
- **Quitar una extensión:** borra su ficha.

---

## English

This is a **directory**, not a store. Each extension's code lives in its
author's repository; here there is one **entry** per extension
(`extensions/<id>.toml`): name, description, licence, link and the
fingerprint (SHA-256) of the exact file that gets installed.

### Listing your extension

No Git needed. From the browser:

1. Publish your extension in your own repository under a free licence and
   create a **tag** (e.g. `v1.0`).
2. Here, copy [`TEMPLATE.toml`](TEMPLATE.toml), then **Add file ▸ Create new
   file** in `extensions/`, named `<id>.toml`, and paste it.
3. Fill it in. For `sha256`: `sha256sum my_extension.py` (Linux/Mac) or
   `certutil -hashfile my_extension.py SHA256` (Windows). If it is wrong, the
   check tells you the right value.
4. Optional: a screenshot in `screenshots/` (png, jpg or webp, under 600 KB).
5. **Propose changes** ▸ **Create pull request**.

A bot checks the entry within a minute: complete fields, free licence,
matching fingerprint, and a `setup(app)` or a tool in the file. **It reads
the code and never runs it.** Then a maintainer approves it and the page
updates by itself within minutes. A new version is a new pull request
changing `version`, `download` and `sha256`; when it comes from the GitHub
account in `author_url`, touches only your entry (and its screenshot) and
the check finds nothing to read, **it is published by itself** — as
«Community» until a maintainer reads the new file.

Writing an extension: see the
[plugin guide](https://github.com/ingelibre/ingetrazo/blob/main/docs/plugins.md).

**Reviewed** means a maintainer read that exact file (its hash is in
`reviewed.toml`); a new version goes back to **Community** until read
again. **Community** entries passed the automatic check, but nobody read the
code in depth. An extension is Python code with the same access to your
computer as IngeTrazo itself.

---

## Português

Um **diretório**, não uma loja: o código fica no repositório do autor. Para
publicar, copie [`TEMPLATE.toml`](TEMPLATE.toml) para `extensions/<id>.toml`
pelo navegador (**Add file ▸ Create new file**), preencha e abra um pull
request. Um robô verifica a ficha (sem executar o código) e um mantenedor a
aprova. **Revisada** = um mantenedor leu esse arquivo exato; **Comunidade** =
passou na verificação automática. Uma **nova versão** enviada pela conta do
GitHub que está em `author_url`, que só altera a sua ficha e passa limpa na
verificação, **é publicada sozinha**, como «Comunidade».

---

The entries and `catalog.json` are dedicated to the public domain (CC0-1.0);
`tools/` is GPL-3.0-or-later. Each extension keeps its own licence.
