# Planetary Diversity: Wilderness Compatibility

Compatibility mod for **Planetary Diversity** and the vanilla **Wilderness** origin in
Stellaris 4.5.x (tested against 4.5.4 "Cygnus").

It makes the Rare/Uncommon Worlds specialization zones and the three Ascension Worlds
superprojects usable by Wilderness empires, and gives Wilderness its own visible zone and
job names, **without editing Planetary Diversity** and without renaming anything for
non-Wilderness empires.

## What it changes

### 1. Rare-world zones (54 zones, 18 worlds)

Planetary Diversity gates every rare-world specialization zone twice:

* `potential` in `common/zones/pd_rare_zones.txt` (54 lines)
* `unlock`, either inline (3 Geothermal zones) or through the shared
  `common/inline_scripts/zones/pd_rare_zone_common.txt` (1 line)

The gate is:

```
hidden_trigger = { exists = owner  owner = { is_wilderness_empire = no } }
```

Because localisation cannot be trigger-conditional, the mod cannot simply delete that
line: non-Wilderness empires would lose the PD names as soon as the names become
Wilderness-flavoured. Instead, every Wilderness-available zone is **duplicated**:

| Zone | Gate |
|---|---|
| `zone_pd_<name>` (original) | non-Wilderness only (`is_wilderness_empire = no`) |
| `zone_pd_<name>_wilderness` (copy) | Wilderness only (`is_wilderness_empire = yes`) |

Everything else is copied unchanged into both IDs: `num_zones` one-of-three checks,
`planet_limit`, `pd_rare_zone_committed`, costs, `convert_to`, `included_building_sets`,
job swaps and tooltips. Every `num_zones = { type = zone_pd_X value = 0 }` check also
counts `zone_pd_X_wilderness`, so the "one of three" rule still holds after a conquest, a
save upgrade or while a sibling is queued (the planet flag covers the queue window).

`convert_to` is the safety net: if a planet changes owner, the now-invalid zone (original
or `_wilderness`) converts back to the plain vanilla zone.

Available options after the patch (one buildable per planet, same as for other empires):

| Options | Worlds |
|---|---|
| 3 of 3 | Geothermal, Megaflora, Salt, Primal, Supercontinent, Storm, Iceberg, Lichen |
| 2 of 3 | Petrified, Reef, Archipelago, Biolumen, Aquifer, Sinkhole, Glaciovolcanic, Lanthanide |
| 1 of 3 | Coral, Cryoflora |

The `guild` and `resort` zones stay unavailable **on purpose**:

* `guild` requires `country_uses_consumer_goods = yes`; Wilderness (hive) does not use
  consumer goods, and its artisan drone would produce a resource the empire cannot use.
* `resort` requires `is_gestalt = no` and uses entertainer jobs; it is excluded for every
  gestalt empire, not only Wilderness.

They keep their original PD IDs, names and shared unlock script. Only their `num_zones`
sibling checks were extended to count the `_wilderness` twins, which is harmless for them.

### 1b. Uncommon Worlds zones (9 zones)

The same split is applied to the nine zones of `common/zones/pd_uncommon_zones.txt`
(Tidally Locked, Cave and Superhabitable worlds). Their shared `unlock` script is already
open, so only the class/modifier gates and the sibling checks needed the same treatment.
It lets Wilderness use these specializations on the base (standard district set) variants
of those classes. Hive/machine class variants use `hive_world` / `machine_world` district
sets where Wilderness has no districts anyway, so no extra handling is needed.

### 2. Wilderness-specific names for zones and jobs

The 51 zones that Wilderness can actually build, and the 51 drone jobs their swaps use,
are duplicated so that the names are per-empire rather than global:

* 51 new zone IDs `zone_pd_*_wilderness` with their own localisation keys.
* 51 new job stubs `pd_*_drone_wilderness` (byte-for-byte copies of PD's stubs, with
  `possible = { always = no }`, assigned only through the new swaps).
* 51 new job swap entries across the seven `zzz_pd_*_drone.txt` files. Each file keeps
  PD's original entry gated to non-Wilderness empires and appends a Wilderness copy with
  `weight = 300` that points at the `_wilderness` job.
* 51 new game concepts `concept_zone_pd_*_wilderness`, copying the original icon so the
  build menu and tooltips keep the district-specialization art.

The style is the "hybrid" one: PD keeps its ecological identity, but the words borrow
Wilderness' biological/anatomical grammar (`symbiont`, `evosymbiont`, `forgesymbiont`,
`-spine`, `-stem`, `-bloom`, `-core`, `-gut`, `-heart`). The 15 names flagged `[B]` are
kept verbatim: `Ventheart`, `Magmaforge`, `Thermocore`, `Rootspine`, `Xylembloom`,
`Fossilspine`, `Reefmind`, `Tidegut`, `Kelpweave`, `Brinegut`, `Boneforge`, `Riftheart`,
`Stormmind`, `Frostgut`, `Tephraspine`.

Example:

| Zone ID | Wilderness name | Job ID | Wilderness job |
|---|---|---|---|
| `zone_pd_geothermal_grid_wilderness` | Ventheart | `pd_geothermal_vent_tapper_drone_wilderness` | Ventsymbiont |
| `zone_pd_archipelago_foundry_wilderness` | Tidegut | `pd_archipelago_tidal_smelter_drone_wilderness` | Tidal Forgesymbiont |
| `zone_pd_petrified_mine_wilderness` | Fossilspine | `pd_petrified_fossil_quarrier_drone_wilderness` | Fossilsymbiont |
| `zone_pd_reef_lab_wilderness` | Reefmind | `pd_reef_ecologist_drone_wilderness` | Reef Evosymbiont |

Spanish names are shipped too (for example *Corazón de Fumarolas* / *Simbionte de
Fumarola* for Ventheart / Ventsymbiont).

Scope and caveats:

* **Only Wilderness sees the new names.** Non-Wilderness empires use the original PD zone
  IDs, job IDs, concepts and localisation, unchanged.
* **No original key is overridden.** The mod's name files only define `_wilderness` keys,
  so a PD update that changes a name or a tooltip is picked up automatically by the
  originals, and the generator fails loudly if a referenced key disappears.
* **Descriptions are forwarded, not retranslated.** The new zone/concept/job description
  keys alias the PD originals (`$zone_pd_*_desc$`, `$job_*_desc$`), so all flavour text
  and formatting stay in sync with PD.
* **Swap tooltips are split as well.** The new swap entries use a dedicated
  `pd_*_wilderness_swap_tt` that lists the wilderness job plural; the original tooltips are
  untouched.
* `guild` and `resort` zones are not duplicated and are not renamed.
* Exotic Worlds is not touched.

### 3. Ascension Worlds superprojects

The three decisions (`Core Tap`, `Agriworld`, `Stripmine`) require vanilla rural districts
that Wilderness can never build. This mod adds a Wilderness branch to their `allow` block:

| Decision | Wilderness requirement |
|---|---|
| Core Tap | 3+ `district_photosynthesis_fields`, no hollow mountains, no orchard forests |
| Agriworld | 3+ `district_orchard_forests`, no photosynthesis fields, no hollow mountains |
| Stripmine | 3+ `district_hollow_mountains`, no photosynthesis fields, no orchard forests |

The AI bypass, costs, effects, `change_pc`, `set_carrier_flag` and PD modifiers are
untouched. Wilderness rural districts share the vanilla capacity pools
(`district_photosynthesis_fields` → generator, `district_hollow_mountains` → mining,
`district_orchard_forests` → farming), so PD's `-1` max multipliers on the two unused
pools remove the other two wilderness district types when the project completes, while
the carrier flag (`uncapped_*_districts`) makes the matching wilderness district uncapped.
That is the intended "specialize the world" behaviour.

#### Agriworld technology prerequisite

PD's `tech_pd_planetary_agriworld` lists `tech_nano_vitality_crops` as one of its three
prerequisites. That is a vanilla technology with `potential = { is_wilderness_empire = no }`,
so a Wilderness empire can never research it. Because the decision checks
`has_technology = tech_pd_planetary_agriworld`, the Agriworld decision silently never
appeared for Wilderness, even though the decision's Wilderness branch was correct.

This mod overrides `tech_pd_planetary_agriworld` in
`common/technology/zzz_pd_aw_wilderness_technology.txt`:

* the shared `prerequisites` are `tech_food_processing_2` and `tech_ecological_adaptation`,
  both researchable by Wilderness (vanilla gives food processing 2 a Wilderness swap);
* `potential` keeps `tech_nano_vitality_crops` as a requirement for non-Wilderness empires
  (`OR = { is_wilderness_empire = yes has_technology = tech_nano_vitality_crops }`), so
  their availability is unchanged;
* the `country_uses_food = no` weight penalty is limited to non-Wilderness empires, because
  Wilderness spends biomass instead of food and would otherwise be pushed to weight 0.

Cost, tier, category, `is_rare`, tooltip and `ai_weight` are copied from PD. The decision
file did not need any change: it already checks the same technology ID.

#### Superproject world type names

The three resulting planet classes are also renamed **only for Wilderness**:

| Original class | Wilderness class | EN | ES |
|---|---|---|---|
| `pc_pd_core_tap` | `pc_pd_core_tap_wilderness` | Coreheart | Corazón del Núcleo |
| `pc_pd_agriworld` | `pc_pd_agriworld_wilderness` | Harvestheart | Corazón de la Cosecha |
| `pc_pd_stripmine` | `pc_pd_stripmine_wilderness` | Oremarrow | Médula de Mineral |

The classes are copies of PD's definitions (same entity, icons, district set, size and
modifiers); only the ID and the localisation change. The decisions branch on
`owner = { is_wilderness_empire = yes }` and pick the `_wilderness` class and modifier.
The planet modifiers are copied as well, so the modifier list shows the same Wilderness
name and its "uncapped" tooltip names the Wilderness rural district
(`photosynthesis fields`, `orchard forests`, `hollow mountains`) instead of the vanilla
one.

`pd_aw_is_superproject_class` is overridden to recognise both ID sets, so PD's other
checks (terraforming decisions, building restrictions) keep working on Wilderness
superproject worlds. Jobs, job swaps and districts are untouched: they keep the
Wilderness content and names inherited from the vanilla origin. Non-Wilderness empires
keep the original classes, modifiers and names.

### 4. Not included: Exotic Worlds

Exotic cryo worlds are **not** patched. Planetary Diversity deliberately forbids the
combination at empire creation:

`planetary_diversity_exotics/common/governments/civics/zzz_pd_exotic_cryophile_overrides.txt`

```
species_class = { NOT = { value = CRYO } }
```

Cryo worlds use `district_set = pdexotic_cryo`, and neither vanilla `district_craglands`
nor PD's `district_hive` accepts Wilderness on that set, so the colony would have no urban
district or capital. Supporting it would be new content, not a bug fix, and is out of
scope for this mod.

## Files

| File | Contents |
|---|---|
| `common/zones/zzz_pd_wilderness_rare_zones.txt` | 54 original zones (51 gated to non-Wilderness) + 51 `_wilderness` copies |
| `common/zones/zzz_pd_wilderness_uncommon_zones.txt` | 9 original zones (gated) + 9 `_wilderness` copies |
| `common/inline_scripts/zones/pd_rare_zone_common.txt` | PD's shared unlock script, unchanged; still used by guild/resort |
| `common/inline_scripts/zones/pd_rare_zone_common_nonwilderness.txt` | same script with a `is_wilderness_empire = no` gate |
| `common/inline_scripts/zones/pd_rare_zone_common_wilderness.txt` | same script with a `is_wilderness_empire = yes` gate |
| `common/pop_jobs/zzz_pd_wilderness_jobs.txt` | 51 `pd_*_drone_wilderness` job stubs |
| `common/pop_jobs/zzz_pd_{agri,calculator_*,fabricator,mining_drone,technician_drone}.txt` | 7 overridden swap files: gated originals + Wilderness copies |
| `common/game_concepts/zzz_pd_wilderness_concepts.txt` | 51 `concept_zone_pd_*_wilderness` definitions |
| `common/decisions/zzz_pd_aw_wilderness_decisions.txt` | the three Ascension Worlds decisions with a Wilderness branch |
| `common/technology/zzz_pd_aw_wilderness_technology.txt` | `tech_pd_planetary_agriworld` override: Wilderness-reachable prerequisites, non-Wilderness `potential` unchanged |
| `common/planet_classes/zzz_pd_aw_wilderness_planet_classes.txt` | 3 `_wilderness` copies of the superproject planet classes |
| `common/static_modifiers/zzz_pd_aw_wilderness_static_modifiers.txt` | 3 `_wilderness` copies of the superproject planet modifiers |
| `common/scripted_triggers/zzz_pd_aw_wilderness_scripted_triggers.txt` | `pd_aw_is_superproject_class` accepting both class ID sets |
| `localisation/english/zzz_pd_wilderness_names_l_english.yml` | 459 Wilderness-only keys (zones, concepts, jobs, swap tooltips) |
| `localisation/spanish/zzz_pd_wilderness_names_l_spanish.yml` | same 459 keys in Spanish |
| `localisation/english/zzz_pd_aw_wilderness_superprojects_l_english.yml` | 27 keys for the Wilderness superproject classes/modifiers |
| `localisation/spanish/zzz_pd_aw_wilderness_superprojects_l_spanish.yml` | same 27 keys in Spanish |

All `.txt` files are UTF-8 without BOM and LF; the `.yml` files are UTF-8 **with** BOM, as
Stellaris expects.

## Requirements

* Stellaris 4.5.x
* Planetary Diversity core (`planetary_diversity`)
* Planetary Diversity: Ascension Worlds (`planetary_diversity_ascension_worlds`)
* The base mod's Rare Worlds content (included in PD core)

Exotics is not required. Arcologies, Gaias, Uniques, City Sets, Planetview and Vanilla
Replacements are optional.

## Installation and load order

The launcher descriptor has already been created at:

```
C:\Users\furia\Documents\Paradox Interactive\Stellaris\mod\pd_wilderness_compat.mod
```

It points at:

```
C:\Users\furia\Downloads\PlanetaryDiveristy-main\pd_wilderness_compat
```

If you move the mod folder, update the `path=` line in the `.mod` file (forward slashes).

Then, in the Paradox launcher:

1. Enable **Planetary Diversity** and its modules.
2. Enable **Planetary Diversity: Wilderness Compatibility**.
3. Place it at the bottom of the load order (after PD core, Exotics and Ascension Worlds).
4. Launch the game.

Load order matters because the mod ships files that redefine PD zone IDs, job swap roots
and concept keys. If another mod redefines the same IDs after this one, the split can be
lost; keep this mod last among mods that touch PD rare zones or drone jobs.

## Regenerating after a Planetary Diversity update

Everything under `common/zones`, `common/game_concepts`, `common/pop_jobs` (the
`zzz_pd_*` files) and the two `zzz_pd_wilderness_names_*.yml` files is generated. Do not
hand-edit them. If PD updates its zones, jobs, concepts or localisation:

```
python tools\generate_wilderness_split.py
```

The generator:

* reads PD from `PlanetaryDiveristy-main/planetary_diversity`;
* reads the Wilderness names from `tools/pd_wilderness_names.json` (51 entries, EN + ES:
  zone name, job name, plural), which is the only file to edit when a zone or job name
  changes;
* rewrites the zone files, the two inline variants, the job stubs, the concepts, the seven
  swap files and both name localisations;
* is idempotent (it strips its own gates, twin checks and appended section before
  regenerating) and aborts on any unexpected zone, missing PD key, missing concept, job
  stub mismatch, duplicate key or unbalanced block.

`tools\generate_rare_zones.ps1` is deprecated: it regenerates the old gate-free files and
would delete the split. It refuses to run without `-Force`.

The three decision overrides, the agriworld technology override, the planet class/modifier
copies and the `pd_aw_is_superproject_class` override are maintained manually. The decisions
contain hand-written Wilderness branches, and the other files are partial copies of PD's
blocks, so re-check them after an Ascension Worlds update (compare them against
`common/decisions/pd_aw_decisions.txt`, `common/technology/pd_aw_technology.txt`,
`common/planet_classes/pd_aw_superproject_planet_classes.txt`,
`common/static_modifiers/pd_aw_static_modifiers.txt` and
`common/scripted_triggers/pd_aw_scripted_triggers.txt`). The validator compares the class
and modifier copies against PD's originals and checks the trigger, decisions and
localisation, so a PD update that changes them fails loudly.

The Wilderness names for the three superproject world types live in the two
`zzz_pd_aw_wilderness_superprojects_*.yml` files; edit the localisation values (name,
description and adjective) there, not in `pd_wilderness_names.json`.

### Version note: snapshot vs. installed Workshop build

This release was generated from the development snapshot
`PlanetaryDiveristy-main\PlanetaryDiveristy-main`. Compared with the installed Workshop
copy (`819148835`), that snapshot only differs in 15 lines of `pd_rare_zones.txt`, where
the workshop build still passes `AMOUNT` to the vanilla `jobs/zone_engineers_add` inline
script. Stellaris 4.5 reads `$LARGE_AMOUNT$` in that script, so the snapshot's
`LARGE_AMOUNT` is the value that actually adds the zone engineer jobs. Keeping the
snapshot version therefore also fixes the research specializations (the workshop build
grants no engineer jobs on them). No other zone, cost, job or tooltip line differs.

The Ascension Worlds decisions only differ from the installed build by one unrelated
`pd_is_flooded_planet = no` line in an earlier decision that this mod does not override,
so the three superproject overrides match the installed mod.

If you prefer to mirror the installed Workshop files byte-for-byte instead, regenerate
with the workshop path in `PD_ROOT` of the generator; you will get the older `AMOUNT`
behaviour back.

## Quick in-game test

1. Start a **Wilderness** empire (hive mind, Biogenesis DLC).
2. Use the console to find or create a Rare World, or colonize a known PD rare planet.
3. Open the planet's district/zone UI. One of the PD specializations should now appear on
   Geothermal, Megaflora, etc., with the Wilderness name (Ventheart, Rootspine, ...).
4. Build it and hover the job: the job should show the Wilderness name (Ventsymbiont,
   Rootbreakersymbiont, ...), and the zone tooltip should describe the swap with the
   Wilderness plural.
5. Start or load a **non-Wilderness** empire on a PD rare world and confirm the zones and
   jobs still show PD's original names.
6. For Ascension: research the superproject technologies first (`research_all_technologies`, or
   `research_technology tech_pd_planetary_agriworld` to test the Agriworld fix in isolation).
   Build 3 photosynthesis fields on a world and check that **Core Tap** is allowed; repeat
   with 3 orchard forests for Agriworld and 3 hollow mountains for Stripmine. Agriworld must
   now appear once `tech_pd_planetary_agriworld` is researched.
7. Enact each superproject as Wilderness: the planet class and the planet modifier must show
   the Wilderness name (Coreheart / Harvestheart / Oremarrow in English). The modifier
   tooltip must name photosynthesis fields / orchard forests / hollow mountains, not the
   vanilla districts. Repeat as a non-Wilderness empire and confirm the PD names are intact.

Where the zones appear:

* `urban` specializations (foundry, lab) use the two urban slots of the capital
  `district_craglands`. If both slots are already taken by Wilderness zones, remove one
  first.
* `energy`, `minerals` and `food` specializations need the matching Wilderness rural
  district built (`district_photosynthesis_fields`, `district_hollow_mountains`,
  `district_orchard_forests`) to provide the slot.

Useful console commands:

```
debugtooltip
research_all_technologies
planet_size 30
```

## Multiplayer

* Every player must use the same version of this mod and the same PD version.
* Do not add or remove the mod mid-save if rare zones or superprojects are already built.
* The host and all clients must have matching files; otherwise the checksum differs and
  the game will desync.
* The split adds deterministic IDs and no randomness, so it is MP-safe as long as the
  files match.
* Mods disable achievements.

## Save compatibility

* Adding the zone IDs is save-compatible for planets without PD specialization zones.
* If a Wilderness empire already has a PD specialization zone from an older build of this
  mod (or from a console command), that zone is now invalid for its owner. On load,
  `convert_to` replaces it with the plain vanilla zone; the zone's building slots and
  modifiers are lost with it. Make a backup before upgrading a long-running save.
* Localisation changes are save-safe: IDs in the save are unchanged for non-Wilderness
  empires.
* Superproject worlds built before this update keep `pc_pd_*` and the PD modifier, so they
  keep the PD names (Core Tap / Agriworld / Stripmine). New projects use the `_wilderness`
  class and modifier for Wilderness. There is no automatic migration by design; re-enacting
  the superproject is the only in-game way to switch an old world.

## Known limitations

* **Rare-zone modifier tooltips are still global.** PD's planet-modifier tooltips
  (`pd_*_buildings_tt`) and the planet-class tooltips are static localisation and list the
  original concept keys. A Wilderness player sees the original PD zone names in those
  lists, while the build menu and the zone/job tooltips show the Wilderness names. The
  three superproject worlds are split separately (see 3b), but the zone-name lists inside
  the rare-zone tooltips stay global; making them conditional would require splitting every
  modifier and planet class that references a zone.
* **The databank shows both concept entries**, original and `_wilderness`, because both
  concepts exist. The `_wilderness` entry only has the flavour line (the bonus list lives
  in the original concept description).
* `guild` and `resort` rare zones remain unavailable to Wilderness by design (see above).
* Uncommon Worlds zones are included, but the base/hive/machine class variants differ in
  district set. Wilderness only gets districts on the `standard` variants, so test the
  hive/machine variants separately.
* Exotic cryo worlds are not supported (see above).
* The superproject `-1` max multipliers remove the other two rural district types when the
  project completes (existing districts included). Wilderness keeps only its matching
  district type, now uncapped. This is intended; test it on a disposable save.
* **Planet names follow the planet, not the owner.** If another empire conquers a
  Wilderness superproject, it keeps the `_wilderness` class and name (and the reverse for
  a Wilderness empire conquering a normal superproject) until the planet is terraformed or
  the project is re-enacted.
* The decisions keep PD's titles and descriptions ("Planetary Superproject: Agriworld",
  etc.) for every empire. Only the resulting world type and its planet modifier are renamed
  for Wilderness; duplicating the decisions was out of scope.
