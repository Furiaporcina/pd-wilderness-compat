#!/usr/bin/env python3
"""
Standalone validator for the Wilderness zone/job split.

`tools/generate_wilderness_split.py` validates its own output, but only against the
data it just wrote. This script re-reads the mod from disk and checks the invariants
that matter for a release:

  * zone definitions: 114 total, 51 `_wilderness` copies, 51 gated originals,
    guild/resort zones never gated;
  * every `num_zones` sibling check counts the `_wilderness` twin when it exists;
  * 51 job stubs, each with `possible = { always = no }`;
  * 51 wilderness swap entries, with the originals gated to non-Wilderness;
  * 51 concepts;
  * localisation: 459 keys per language, identical key sets, no PD key overridden,
    every `$variable$` resolves (mod, PD, and vanilla localisation when available);
  * ascension worlds: the agriworld technology override keeps the Wilderness exemption
    and the decisions only reference technology IDs that exist in PD/vanilla;
  * file encoding: `.yml` UTF-8 with BOM, `.txt` UTF-8 without BOM, LF only.

Usage:
    python tools\\validate_wilderness_split.py
    python tools\\validate_wilderness_split.py --vanilla-root "E:\\Steam\\steamapps\\common\\Stellaris"

If --vanilla-root is omitted, the script tries $STELLARIS_ROOT and the default Steam
path. Without vanilla localisation the variable check only covers mod + PD keys, which
still catches every key the split itself introduces.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "pd_wilderness_compat"
PD = ROOT / "PlanetaryDiveristy-main/planetary_diversity"
ASCENSION = ROOT / "PlanetaryDiveristy-main/planetary_diversity_ascension_worlds"
NAMES = ROOT / "tools/pd_wilderness_names.json"

sys.path.insert(0, str(ROOT / "tools"))
import generate_wilderness_split as gen  # noqa: E402

ZONE_FILES = [
    MOD / "common/zones/zzz_pd_wilderness_rare_zones.txt",
    MOD / "common/zones/zzz_pd_wilderness_uncommon_zones.txt",
]
JOBS_FILE = MOD / "common/pop_jobs/zzz_pd_wilderness_jobs.txt"
CONCEPTS_FILE = MOD / "common/game_concepts/zzz_pd_wilderness_concepts.txt"
DECISIONS_FILE = MOD / "common/decisions/zzz_pd_aw_wilderness_decisions.txt"
TECH_FILE = MOD / "common/technology/zzz_pd_aw_wilderness_technology.txt"
PLANET_CLASSES_FILE = MOD / "common/planet_classes/zzz_pd_aw_wilderness_planet_classes.txt"
STATIC_MODIFIERS_FILE = MOD / "common/static_modifiers/zzz_pd_aw_wilderness_static_modifiers.txt"
TRIGGERS_FILE = MOD / "common/scripted_triggers/zzz_pd_aw_wilderness_scripted_triggers.txt"
SUPERPROJECT_LOC = {
    "en": MOD / "localisation/english/zzz_pd_aw_wilderness_superprojects_l_english.yml",
    "es": MOD / "localisation/spanish/zzz_pd_aw_wilderness_superprojects_l_spanish.yml",
}
LOC_FILES = {
    "en": MOD / "localisation/english/zzz_pd_wilderness_names_l_english.yml",
    "es": MOD / "localisation/spanish/zzz_pd_wilderness_names_l_spanish.yml",
}
PD_LOC = {
    "en": PD / "localisation/english/planetarydiversity_l_english.yml",
    "es": PD / "localisation/spanish/planetarydiversity_l_spanish.yml",
}

LOC_KEY_RE = re.compile(r'^[ \t]*([A-Za-z0-9_\-.]+):[0-9]*[ \t]*"')
VAR_RE = re.compile(r"\$([A-Za-z0-9_]+)\$")


def read_yml(path: Path) -> dict[str, str]:
    return gen.parse_loc(path)


def vanilla_loc_keys(root: Path | None) -> set[str]:
    if root is None:
        return set()
    folder = root / "localisation/english"
    if not folder.is_dir():
        return set()
    keys: set[str] = set()
    for path in folder.glob("*.yml"):
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            m = LOC_KEY_RE.match(line)
            if m:
                keys.add(m.group(1))
    return keys


def collect_tech_ids(folders: list[Path]) -> set[str]:
    ids: set[str] = set()
    for folder in folders:
        if not folder.is_dir():
            continue
        for path in folder.rglob("*.txt"):
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            ids.update(re.findall(r"^[ \t]*(tech_[a-z0-9_]+)[ \t]*=[ \t]*\{", text, re.M))
    return ids


def find_vanilla_root(explicit: str | None) -> Path | None:
    candidates = [explicit, os.environ.get("STELLARIS_ROOT"),
                  r"E:\Steam\steamapps\common\Stellaris"]
    for candidate in candidates:
        if candidate and (Path(candidate) / "common/zones").is_dir():
            return Path(candidate)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vanilla-root", default=None)
    args = parser.parse_args()

    errors: list[str] = []
    names = json.loads(NAMES.read_text(encoding="utf-8"))
    wild_zones = {entry["zone"] + "_wilderness" for entry in names}
    wild_jobs = {entry["job"] + "_wilderness" for entry in names}

    # --- zones -----------------------------------------------------------------
    zone_blocks: dict[str, list[str]] = {}
    for path in ZONE_FILES:
        for key, _s, _e, block in gen.split_top_level_blocks(
            gen.read_lines(path), r"^(zone_pd_[a-z0-9_]+)\s*=\s*\{"
        ):
            if key in zone_blocks:
                errors.append(f"duplicate zone definition {key}")
            zone_blocks[key] = block

    guild_resort = {k for k in zone_blocks if k.endswith("_guild") or k.endswith("_resort")}
    if len(zone_blocks) != 114:
        errors.append(f"expected 114 zone definitions, found {len(zone_blocks)}")
    if {k for k in zone_blocks if k.endswith('_wilderness')} != wild_zones:
        errors.append("wilderness zone id set does not match pd_wilderness_names.json")

    for key, block in zone_blocks.items():
        text = "\n".join(block)
        if key in guild_resort:
            if "is_wilderness_empire" in text:
                errors.append(f"{key}: guild/resort zone must not carry a wilderness gate")
            continue
        expected = "is_wilderness_empire = yes" if key in wild_zones else "is_wilderness_empire = no"
        if expected not in text:
            errors.append(f"{key}: missing gate '{expected}'")
        if key in wild_zones:
            if "zones/pd_rare_zone_common_nonwilderness" in text:
                errors.append(f"{key}: uses the non-Wilderness inline script")
            if "zones/pd_rare_zone_common_wilderness" not in text and "unlock = {" not in text:
                errors.append(f"{key}: no Wilderness unlock")
            if not re.search(r"text = pd_[a-z0-9_]+_wilderness_swap_tt", text):
                errors.append(f"{key}: drone swap tooltip was not renamed")
            if "convert_to" not in text:
                errors.append(f"{key}: missing convert_to fallback")

    for key, block in zone_blocks.items():
        text = "\n".join(block)
        for match in re.finditer(r"num_zones = \{ type = (zone_pd_[a-z0-9_]+) value = 0 \}", text):
            base = match.group(1)
            if base + "_wilderness" in wild_zones and base + "_wilderness" not in text:
                errors.append(f"{key}: sibling check for {base} does not count the wilderness twin")

    # --- jobs ------------------------------------------------------------------
    job_blocks = gen.split_top_level_blocks(gen.read_lines(JOBS_FILE), r"^(pd_[a-z0-9_]+)\s*=\s*\{")
    if {key for key, *_ in job_blocks} != wild_jobs:
        errors.append("job stub id set does not match pd_wilderness_names.json")
    for key, _s, _e, block in job_blocks:
        if not any("possible = { always = no }" in line for line in block):
            errors.append(f"{key}: missing 'possible = {{ always = no }}'")

    # --- concepts --------------------------------------------------------------
    concept_blocks = gen.split_top_level_blocks(
        gen.read_lines(CONCEPTS_FILE), r"^(concept_zone_pd_[a-z0-9_]+)\s*=\s*\{"
    )
    expected_concepts = {"concept_" + entry["zone"] + "_wilderness" for entry in names}
    if {key for key, *_ in concept_blocks} != expected_concepts:
        errors.append("concept id set does not match pd_wilderness_names.json")

    # --- swaps -----------------------------------------------------------------
    swap_copies = 0
    for filename in gen.SWAP_FILES:
        text = (MOD / "common/pop_jobs" / filename).read_text(encoding="utf-8")
        swap_copies += len(re.findall(r"^\s*name = pd_[a-z0-9_]+_drone_wilderness\s*$", text, re.M))
        if "owner = { is_wilderness_empire = no }" not in text:
            errors.append(f"{filename}: original PD swaps are not gated to non-Wilderness")
        for match in re.finditer(r"^\s*name = (pd_[a-z0-9_]+_drone_wilderness)\s*$", text, re.M):
            if match.group(1) not in wild_jobs:
                errors.append(f"{filename}: unknown wilderness job {match.group(1)}")
        for match in re.finditer(r"num_zones = \{ type = (zone_pd_[a-z0-9_]+) value > 0 \}", text):
            base = match.group(1)
            if base + "_wilderness" in wild_zones and base + "_wilderness" not in text:
                errors.append(f"{filename}: swap check for {base} does not count the wilderness twin")
    if swap_copies != 51:
        errors.append(f"expected 51 wilderness swap entries, found {swap_copies}")

    # --- ascension worlds ------------------------------------------------------
    vanilla_root = find_vanilla_root(args.vanilla_root)

    tech_blocks = gen.split_top_level_blocks(
        gen.read_lines(TECH_FILE), r"^(tech_[a-z0-9_]+)\s*=\s*\{"
    )
    if {key for key, *_ in tech_blocks} != {"tech_pd_planetary_agriworld"}:
        errors.append("technology override must define exactly tech_pd_planetary_agriworld")
    tech_body = "\n".join(tech_blocks[0][3]) if tech_blocks else ""
    prereq = re.search(r"prerequisites\s*=\s*\{([^}]*)\}", tech_body)
    prereq_text = prereq.group(1) if prereq else ""
    if "tech_nano_vitality_crops" in prereq_text:
        errors.append("agriworld technology: tech_nano_vitality_crops is still a prerequisite")
    for tech in ("tech_food_processing_2", "tech_ecological_adaptation"):
        if tech not in prereq_text:
            errors.append(f"agriworld technology: missing prerequisite {tech}")
    if "is_wilderness_empire = yes" not in tech_body or "tech_nano_vitality_crops" not in tech_body:
        errors.append(
            "agriworld technology: lost the Wilderness exemption or the nano vitality potential gate"
        )

    known_techs = collect_tech_ids([ASCENSION / "common/technology", PD / "common/technology"])
    if vanilla_root is not None:
        known_techs |= collect_tech_ids([vanilla_root / "common/technology"])
    decision_techs = set(
        re.findall(r"\b(tech_[a-z0-9_]+)", DECISIONS_FILE.read_text(encoding="utf-8"))
    )
    for tech in sorted(decision_techs - known_techs):
        errors.append(f"decisions reference unknown technology {tech}")

    # --- superproject world types ---------------------------------------------
    wilderness_classes = {
        "pc_pd_core_tap_wilderness",
        "pc_pd_agriworld_wilderness",
        "pc_pd_stripmine_wilderness",
    }
    class_blocks = {
        key: block
        for key, _s, _e, block in gen.split_top_level_blocks(
            gen.read_lines(PLANET_CLASSES_FILE), r"^(pc_pd_[a-z0-9_]+)\s*=\s*\{"
        )
    }
    if set(class_blocks) != wilderness_classes:
        errors.append("planet class copies do not match the expected three _wilderness classes")

    pd_class_blocks = {
        key: block
        for key, _s, _e, block in gen.split_top_level_blocks(
            gen.read_lines(ASCENSION / "common/planet_classes/pd_aw_superproject_planet_classes.txt"),
            r"^(pc_pd_[a-z0-9_]+)\s*=\s*\{",
        )
    }

    def code_lines(block: list[str]) -> list[str]:
        return [
            line.rstrip()
            for line in block[1:]
            if line.strip() and not line.lstrip().startswith("#")
        ]

    for key in sorted(wilderness_classes):
        base = key.removesuffix("_wilderness")
        if base not in pd_class_blocks:
            errors.append(f"{key}: no matching PD planet class {base}")
        elif code_lines(class_blocks[key]) != code_lines(pd_class_blocks[base]):
            errors.append(f"{key}: planet class body differs from {base}")

    modifier_blocks = {
        key: block
        for key, _s, _e, block in gen.split_top_level_blocks(
            gen.read_lines(STATIC_MODIFIERS_FILE), r"^(pd_aw_[a-z0-9_]+)\s*=\s*\{"
        )
    }
    expected_modifiers = {key.replace("pc_pd_", "pd_aw_") for key in wilderness_classes}
    if set(modifier_blocks) != expected_modifiers:
        errors.append("static modifier copies do not match the expected three _wilderness modifiers")

    pd_modifier_blocks = {
        key: block
        for key, _s, _e, block in gen.split_top_level_blocks(
            gen.read_lines(ASCENSION / "common/static_modifiers/pd_aw_static_modifiers.txt"),
            r"^(pd_aw_[a-z0-9_]+)\s*=\s*\{",
        )
    }
    for key in sorted(expected_modifiers):
        base = key.removesuffix("_wilderness")
        if base not in pd_modifier_blocks:
            errors.append(f"{key}: no matching PD static modifier {base}")
            continue
        expected_body = [
            line.replace(f"custom_tooltip = {base}_tooltip", f"custom_tooltip = {key}_tooltip")
            for line in code_lines(pd_modifier_blocks[base])
        ]
        if code_lines(modifier_blocks[key]) != expected_body:
            errors.append(f"{key}: effects differ from {base}")

    trigger_text = TRIGGERS_FILE.read_text(encoding="utf-8")
    if "pd_aw_is_superproject_class = {" not in trigger_text:
        errors.append("superproject trigger override is missing")
    superproject_base_classes = {key.removesuffix("_wilderness") for key in wilderness_classes}
    for pc in sorted(wilderness_classes | superproject_base_classes):
        if f"is_planet_class = {pc}" not in trigger_text:
            errors.append(f"superproject trigger does not recognise {pc}")

    decisions_text = DECISIONS_FILE.read_text(encoding="utf-8")
    for pc in sorted(wilderness_classes):
        modifier = pc.replace("pc_pd_", "pd_aw_")
        if f"change_pc = {pc}" not in decisions_text:
            errors.append(f"decisions do not change to {pc}")
        if f"modifier = {modifier}" not in decisions_text:
            errors.append(f"decisions do not add {modifier}")

    # --- localisation ----------------------------------------------------------
    pd_values = {lang: read_yml(path) for lang, path in PD_LOC.items()}
    vanilla = vanilla_loc_keys(vanilla_root)
    values = {lang: read_yml(path) for lang, path in LOC_FILES.items()}

    if set(values["en"]) != set(values["es"]):
        errors.append("EN and ES key sets differ")
    if len(values["en"]) != 459:
        errors.append(f"expected 459 localisation keys per language, found {len(values['en'])}")
    for lang, table in values.items():
        for key, value in table.items():
            if key in pd_values[lang]:
                errors.append(f"{lang}: overrides the original PD key {key}")
            for var in VAR_RE.findall(value):
                if var not in table and var not in pd_values[lang] and var not in vanilla:
                    errors.append(f"{lang}: {key} references undefined ${var}$")
    if not vanilla:
        print("note: vanilla localisation not found; variable check limited to mod + PD keys")

    superproject_values = {lang: read_yml(path) for lang, path in SUPERPROJECT_LOC.items()}
    if set(superproject_values["en"]) != set(superproject_values["es"]):
        errors.append("superproject EN and ES key sets differ")
    if len(superproject_values["en"]) != 27:
        errors.append(
            "expected 27 superproject localisation keys per language, "
            f"found {len(superproject_values['en'])}"
        )
    for lang, table in superproject_values.items():
        for key, value in table.items():
            if key in pd_values[lang]:
                errors.append(f"{lang}: superproject key overrides PD key {key}")
            for var in VAR_RE.findall(value):
                if var not in table and var not in pd_values[lang] and var not in vanilla:
                    errors.append(f"{lang}: {key} references undefined ${var}$")

    # --- encoding --------------------------------------------------------------
    for path in list(LOC_FILES.values()) + list(SUPERPROJECT_LOC.values()):
        raw = path.read_bytes()
        if raw[:3] != b"\xef\xbb\xbf":
            errors.append(f"{path.name}: missing UTF-8 BOM")
        if b"\r\n" in raw:
            errors.append(f"{path.name}: contains CRLF")
    txt_files = ZONE_FILES + [
        JOBS_FILE,
        CONCEPTS_FILE,
        DECISIONS_FILE,
        TECH_FILE,
        PLANET_CLASSES_FILE,
        STATIC_MODIFIERS_FILE,
        TRIGGERS_FILE,
        MOD / "common/inline_scripts/zones/pd_rare_zone_common.txt",
        MOD / "common/inline_scripts/zones/pd_rare_zone_common_nonwilderness.txt",
        MOD / "common/inline_scripts/zones/pd_rare_zone_common_wilderness.txt",
    ] + [MOD / "common/pop_jobs" / name for name in gen.SWAP_FILES]
    for path in txt_files:
        raw = path.read_bytes()
        if raw[:3] == b"\xef\xbb\xbf":
            errors.append(f"{path.name}: unexpected UTF-8 BOM")
        if b"\r\n" in raw:
            errors.append(f"{path.name}: contains CRLF")

    # --- report ----------------------------------------------------------------
    print(f"zones:    {len(zone_blocks)} definitions, {len(wild_zones)} wilderness copies")
    print(f"jobs:     {len(job_blocks)} stubs")
    print(f"concepts: {len(concept_blocks)}")
    print(f"swaps:    {swap_copies} wilderness entries")
    print(f"tech:     agriworld override ok, {len(decision_techs)} decision technologies resolved")
    print(f"worlds:   {len(class_blocks)} class copies, {len(modifier_blocks)} modifier copies")
    print(f"loc:      {len(values['en'])} keys / {len(values['es'])} keys")
    print(f"vanilla:  {len(vanilla)} localisation keys indexed")

    if errors:
        print("\nVALIDATION FAILED")
        for error in errors:
            print(" -", error)
        return 1

    print("\nvalidation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
