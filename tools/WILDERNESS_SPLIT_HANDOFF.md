# Handoff — Split de zonas y jobs exclusivos de Wilderness

Fecha: 2026-11-18
Alcance: opción C completa (zonas + jobs + conceptos + swaps + localización EN/ES).

## Qué se hizo

Planetary Diversity comparte las zonas de especialización y sus jobs `_drone` entre todos
los imperios, y la localización de Stellaris no admite triggers. Para que Wilderness vea
nombres propios sin cambiar los de los demás imperios, se duplicó el contenido:

| Contenido | Original | Copia Wilderness |
|---|---|---|
| Zonas | `zone_pd_*` (51, gate `is_wilderness_empire = no`) | `zone_pd_*_wilderness` (51, gate `= yes`) |
| Jobs | `pd_*_drone` (PD, intactos) | `pd_*_drone_wilderness` (51 stubs, `possible = { always = no }`) |
| Swaps | 7 archivos `zzz_pd_*` con la entrada original gateada a no-Wilderness | entrada extra con `weight = 300` y el job `_wilderness` |
| Conceptos | `concept_zone_pd_*` (PD) | `concept_zone_pd_*_wilderness` (51, mismo icono) |
| Loc | claves de PD intactas | 459 claves nuevas `_wilderness` por idioma |

Reglas respetadas:

- Los 12 `guild`/`resort` no se duplican ni se renombran; siguen cerrados a Wilderness por
  `country_uses_consumer_goods = yes` / `is_gestalt = no`. Solo se ampliaron sus checks
  `num_zones` para contar ambos IDs.
- Las 3 decisiones de Ascension Worlds y el tech de Agriworld se sobrescriben en archivos
  aparte (ver “Corrección Agriworld”); el resto de decisiones de PD no se toca.
- Exotic Worlds no se toca.
- Los 15 nombres `[B]` se conservan literalmente.
- No se sobrescribe ninguna clave de localización original de PD.

## Archivos generados

```
pd_wilderness_compat/common/zones/zzz_pd_wilderness_rare_zones.txt        54 + 51 bloques
pd_wilderness_compat/common/zones/zzz_pd_wilderness_uncommon_zones.txt     9 +  9 bloques
pd_wilderness_compat/common/inline_scripts/zones/pd_rare_zone_common.txt                 (base, intacto)
pd_wilderness_compat/common/inline_scripts/zones/pd_rare_zone_common_nonwilderness.txt  (gate no)
pd_wilderness_compat/common/inline_scripts/zones/pd_rare_zone_common_wilderness.txt     (gate yes)
pd_wilderness_compat/common/pop_jobs/zzz_pd_wilderness_jobs.txt            51 stubs
pd_wilderness_compat/common/pop_jobs/zzz_pd_*_drone.txt                    7 overrides
pd_wilderness_compat/common/game_concepts/zzz_pd_wilderness_concepts.txt   51 conceptos
pd_wilderness_compat/common/decisions/zzz_pd_aw_wilderness_decisions.txt  3 decisiones con rama Wilderness
pd_wilderness_compat/common/technology/zzz_pd_aw_wilderness_technology.txt tech_pd_planetary_agriworld corregido
pd_wilderness_compat/common/planet_classes/zzz_pd_aw_wilderness_planet_classes.txt      3 copias _wilderness
pd_wilderness_compat/common/static_modifiers/zzz_pd_aw_wilderness_static_modifiers.txt  3 modificadores _wilderness
pd_wilderness_compat/common/scripted_triggers/zzz_pd_aw_wilderness_scripted_triggers.txt pd_aw_is_superproject_class con ambos sets
pd_wilderness_compat/localisation/english/zzz_pd_wilderness_names_l_english.yml   459 claves
pd_wilderness_compat/localisation/spanish/zzz_pd_wilderness_names_l_spanish.yml   459 claves
pd_wilderness_compat/localisation/english/zzz_pd_aw_wilderness_superprojects_l_english.yml  27 claves
pd_wilderness_compat/localisation/spanish/zzz_pd_aw_wilderness_superprojects_l_spanish.yml  27 claves
```

## Nombres de tipos de mundo de superproyecto (Wilderness)

Solo cambia el nombre de la clase planetaria resultante y el de su modificador; los jobs,
job swaps y distritos quedan intactos (se heredan de Wilderness).

| Clase PD | Clase Wilderness | EN | ES |
|---|---|---|---|
| `pc_pd_core_tap` | `pc_pd_core_tap_wilderness` | Coreheart | Corazón del Núcleo |
| `pc_pd_agriworld` | `pc_pd_agriworld_wilderness` | Harvestheart | Corazón de la Cosecha |
| `pc_pd_stripmine` | `pc_pd_stripmine_wilderness` | Oremarrow | Médula de Mineral |

Mecánica:

- Las clases son copias exactas de las de PD (entity, iconos, `district_set`, tamaño y
  modificadores); solo cambia el ID y la localización (nombre, descripción y adjetivo).
- Los modificadores también se copian (`pd_aw_*_wilderness`) con los mismos efectos; su
  tooltip nombra el distrito rural Wilderness correcto (photosynthesis fields / orchard
  forests / hollow mountains) en vez del distrito vanilla.
- Las tres decisiones ramifican con `owner = { is_wilderness_empire = yes }` para elegir
  `change_pc` y `add_modifier` `_wilderness`; el resto del efecto es idéntico.
- `pd_aw_is_superproject_class` se sobrescribe para reconocer ambos sets, de modo que las
  comprobaciones de PD (decisiones de terraformado, restricciones de edificios) siguen
  funcionando en mundos Wilderness.
- No hay migración automática: los mundos ya construidos conservan `pc_pd_*` y el
  modificador de PD, y por tanto el nombre de PD. Solo los proyectos nuevos usan el nombre
  Wilderness.
- El nombre sigue al planeta, no al dueño: si otro imperio conquista un superproyecto
  Wilderness, mantiene la clase `_wilderness` (y viceversa) hasta terraformar o rehacer el
  proyecto.
- Los títulos/descripciones de las decisiones siguen siendo los de PD; no se duplicaron.

## Corrección Agriworld (tech)

Síntoma: Wilderness solo veía Core Tap y Stripmine; Agriworld nunca aparecía.

Causa: `tech_pd_planetary_agriworld` (PD Ascension Worlds) exige
`tech_nano_vitality_crops`, un tech vanilla con `potential = { is_wilderness_empire = no }`.
Wilderness no puede investigarlo nunca, así que la decisión (que comprueba
`has_technology = tech_pd_planetary_agriworld`) queda oculta.

Solución en `common/technology/zzz_pd_aw_wilderness_technology.txt`:

- `prerequisites = { "tech_food_processing_2" "tech_ecological_adaptation" }` (ambos
  investigables por Wilderness; food processing 2 tiene swap Wilderness en vanilla).
- `potential = { OR = { is_wilderness_empire = yes has_technology = tech_nano_vitality_crops } }`:
  los imperios normales siguen necesitando nano vitality antes de que el tech aparezca.
- El modificador de peso `country_uses_food = no` se limita a `is_wilderness_empire = no`
  (Wilderness gasta biomasa, no comida; si no, el peso quedaría a 0).
- Coste, tier, categoría, `is_rare`, tooltip y `ai_weight` se copian de PD.

No hizo falta tocar el archivo de decisiones: ya comprobaba ese mismo ID.

Generador canónico: `tools/generate_wilderness_split.py`.
Datos editables de nombres: `tools/pd_wilderness_names.json` (51 entradas EN/ES).
Validador independiente: `tools/validate_wilderness_split.py`.
`tools/generate_rare_zones.ps1` queda deprecado y aborta salvo `-Force`.

## Comprobaciones ejecutadas

```
python tools\generate_wilderness_split.py   # genera y valida; idempotente (0 cambios en 2ª pasada)
python tools\validate_wilderness_split.py   # validation passed
```

Resultados:

- 114 definiciones de zona (63 originales + 51 copias); 51 originales gateadas.
- 51 jobs, 51 conceptos, 51 swaps Wilderness.
- 459 claves por idioma, mismo conjunto EN/ES, sin claves de PD sobrescritas.
- Todas las variables `$...$` resuelven (mod + PD + vanilla).
- Los bloques originales, tras normalizar gates/checks, son idénticos al snapshot
  `tools/_pre_split_snapshot` (sin cambios accidentales).
- `.yml` con BOM UTF-8 y LF; `.txt` sin BOM y LF.
- El override del tech tiene llaves balanceadas, sin BOM y con LF.
- 3 copias de clase y 3 de modificador comparadas línea a línea (código, sin comentarios)
  contra los bloques de PD: idénticas salvo el ID y el `custom_tooltip`.
- El trigger reconoce las 6 clases; las decisiones usan el `change_pc` y el
  `add_modifier` `_wilderness`.
- 27 claves de superproyecto por idioma, mismo conjunto EN/ES, con variables resueltas
  (`$district_*_plural$`, `$trait_pc_arctic_preference_desc$`).

## Pruebas en juego pendientes

1. Imperio Wilderness en un mundo raro: la zona aparece con nombre Wilderness
   (Ventheart, Rootspine, ...) y el job con su nombre propio (Ventsymbiont, ...).
2. Imperio no-Wilderness en el mismo tipo de mundo: nombres originales de PD.
3. Construir una zona y comprobar el tooltip del job y el `triggered_desc` del swap.
4. Conquistar el planeta con el otro tipo de imperio: la zona debe convertirse a la
   vanilla (`convert_to`), sin quedar bloqueada.
5. Probar “una de tres”: construir una, ver que las otras dos quedan bloqueadas, y que
   sigue bloqueado mientras hay una en cola (flag `pd_rare_zone_committed`).
6. Comprobar que guild/resort siguen sin aparecer para Wilderness.
7. Guardar/cargar y repetir 1–3.
8. Agriworld: investigar `tech_food_processing_2` + `tech_ecological_adaptation` (o
   `research_technology tech_pd_planetary_agriworld`), ver que la decisión aparece, y
   comprobar que Core Tap/Stripmine no cambiaron para Wilderness ni para otros imperios.
9. Mundos de superproyecto: con Wilderness, ejecutar los tres proyectos y comprobar que la
   clase y el modificador muestran Coreheart / Harvestheart / Oremarrow (EN) o Corazón del
   Núcleo / Corazón de la Cosecha / Médula de Mineral (ES), y que el tooltip del modificador
   nombra el distrito Wilderness correspondiente. Repetir con un imperio no-Wilderness y
   confirmar que conserva los nombres de PD.
10. Guardado antiguo con un superproyecto ya construido: debe conservar el nombre de PD
    (no hay migración automática).

## Limitaciones conocidas

- Los tooltips de modificador de las zonas raras (`pd_*_buildings_tt`) y los de clase
  planetaria son localización estática global: listan los conceptos originales. Wilderness
  ve nombres originales en esas listas, aunque el menú de construcción y los tooltips de
  zona/job muestran los nombres nuevos. Los superproyectos se dividieron aparte (clase,
  modificador y tooltip propios), pero las listas de zonas de los tooltips raros siguen
  siendo globales.
- El databank muestra ambos conceptos (original y `_wilderness`); el nuevo solo lleva la
  línea de flavor, sin el desglose de bonus.
- Guardados antiguos: una zona PD ya construida por Wilderness pasa a vanilla al cargar
  (pierde slots/modificadores de esa zona). Hacer copia de seguridad.
- Superproyectos ya construidos antes de este cambio: conservan `pc_pd_*` y el modificador
  de PD, así que mantienen los nombres de PD. No hay migración automática; solo los
  proyectos nuevos usan los nombres Wilderness.
- El nombre del tipo de mundo sigue al planeta, no al dueño: si otro imperio conquista un
  superproyecto Wilderness conserva la clase `_wilderness` (y viceversa) hasta terraformar
  o rehacer el proyecto.
- Los títulos y descripciones de las decisiones siguen siendo los de PD; solo se renombró
  el tipo de mundo resultante y su modificador.
- Multiplayer: todos los jugadores necesitan exactamente los mismos archivos y la misma
  versión de PD; el split es determinista y no usa aleatoriedad.

## Orden de carga

PD core → Ascension Worlds → (Exóticos si se usa) → este mod al final. Los archivos de
zona/job/concepto/clase/mundo redefinen o amplían IDs de PD y deben cargarse después que
cualquier otro mod que toque zonas raras, jobs `_drone` o los superproyectos.

## Regeneración

```
python tools\generate_wilderness_split.py
```

Si PD cambia nombres o claves, el generador aborta indicando la clave que falta. Editar
solo `tools/pd_wilderness_names.json` para cambiar los nombres Wilderness.

El generador no toca las decisiones, el tech de Agriworld, las clases planetarias, los
modificadores ni el trigger de superproyectos: todo eso se mantiene a mano. Tras actualizar
Ascension Worlds, compararlos con sus archivos originales (`pd_aw_decisions.txt`,
`pd_aw_technology.txt`, `pd_aw_superproject_planet_classes.txt`,
`pd_aw_static_modifiers.txt`, `pd_aw_scripted_triggers.txt`). El validador compara clases y
modificadores línea a línea y comprueba trigger, decisiones y localización.

Los nombres de los tres tipos de mundo de superproyecto se editan en
`localisation/{english,spanish}/zzz_pd_aw_wilderness_superprojects_l_*.yml` (nombre,
descripción y adjetivo), no en `tools/pd_wilderness_names.json`.
