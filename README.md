# Planetary Diversity: Wilderness Compatibility

Parche de compatibilidad para Stellaris 4.5 que permite a los imperios **Wilderness**
usar el contenido de **Planetary Diversity** (zonas raras y superproyectos) sin romper
los nombres, trabajos ni distritos propios de Wilderness.

No modifica PD ni sus archivos originales: este mod carga al final y redefine o amplía
solo lo necesario.

## Requisitos

- Stellaris `v4.5.*`.
- **Planetary Diversity** (core) y **Planetary Diversity: Ascension Worlds**.
- Opcional: **Planetary Diversity: Exotic Worlds** (compatible, sin cambios).
- Orden de carga: PD core → Ascension Worlds → (Exóticos) → **este mod al final**.

## Instalación

1. Suscríbete a los mods de Planetary Diversity en Steam Workshop.
2. Descarga el repositorio (**Code → Download ZIP**) o clónalo en cualquier carpeta, y
   copia `pd_wilderness_compat/` y `pd_wilderness_compat.mod` dentro de:
   `C:\Users\<usuario>\Documents\Paradox Interactive\Stellaris\mod\`
   El `.mod` usa la ruta relativa `mod/pd_wilderness_compat`, así que ambos deben quedar
   directamente en `mod/`, no dentro de una subcarpeta del repositorio.
3. Activa **Planetary Diversity: Wilderness Compatibility** en el launcher, después de PD.
4. En multiplayer, todos los jugadores necesitan exactamente los mismos archivos.

## Qué hace

- **Zonas raras y poco comunes**: copias Wilderness con nombre, concepto y job propios
  (Ventheart, Rootspine, Ventsymbiont...). Los imperios no-Wilderness ven el contenido
  original de PD.
- **Superproyectos (Ascension Worlds)**: los tres tipos de mundo resultantes tienen
  nombre, descripción y adjetivo exclusivos de Wilderness:
  Coreheart / Harvestheart / Oremarrow
  (ES: Corazón del Núcleo / Corazón de la Cosecha / Médula de Mineral).
  Jobs, job swaps y distritos no cambian: se heredan de Wilderness.
- **Agriworld**: se corrige `tech_pd_planetary_agriworld` para que Wilderness pueda
  investigarlo e iniciar el superproyecto.

Detalles, limitaciones y pruebas en
[`pd_wilderness_compat/README.md`](pd_wilderness_compat/README.md) y
[`tools/WILDERNESS_SPLIT_HANDOFF.md`](tools/WILDERNESS_SPLIT_HANDOFF.md).

## Estructura del repositorio

```
pd_wilderness_compat/   Mod listo para usar (common/, localisation/, descriptor.mod)
pd_wilderness_compat.mod Descriptor del launcher (ruta relativa)
tools/                  Generador y validador del split (Python 3.11+)
```

## Regenerar y validar

Los scripts necesitan una copia del código fuente de PD en
`PlanetaryDiveristy-main/PlanetaryDiveristy-main/` (no se incluye en el repositorio).

```
python tools\generate_wilderness_split.py    # idempotente
python tools\validate_wilderness_split.py    # debe terminar en "validation passed"
```

El generador no toca decisiones, tecnología, clases planetarias, modificadores ni
triggers de superproyectos: eso se mantiene a mano y el validador lo comprueba contra
los archivos de PD (clases y modificadores línea a línea).

## Créditos y aviso

- Planetary Diversity es obra de **GatekeeperHaig** y colaboradores; este repositorio no
  incluye ni redistribuye sus archivos, solo código de compatibilidad que requiere tener
  PD instalado.
- Wilderness y Stellaris son propiedad de Paradox Interactive.
- Si el autor de PD solicita cambios o la retirada del parche, se atenderá.

Versión actual: **1.0.2**.
