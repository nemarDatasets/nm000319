"""Rebuild NEMAR nm000319 (Kueper2024) as version 1.1.0: release v2 (14 subjects) and the dataset authors' points.

Usage: python build_319.py <repo> <bids_root> <v2_dir> <out_dir>

<repo>       nm000319 clone (git-annex initialised), checked out on the fix branch, HEAD = main.
<bids_root>  fresh MOABB ``Kueper2024().convert_to_bids()`` output (all 14 subjects) from MOABB PR #1334
             (branch fix/kueper2024-execution-v2): executed-movement protocol, correct trials only, ``rest`` class.
<v2_dir>     the extracted ``EEG_dataset/`` of Zenodo record 17940098 (version 2 of the release).
<out_dir>    receipts (build.json).

Issue NeuroTechX/moabb#1333 (dataset author Niklas Kueper):
  1. the movements are executed, not imagined; each trial = rest >= 5 s, movement onset at 0 s, self-paced execution;
  2. the task label "imagery" is wrong;
  3. version 2 of the release adds 6 subjects (unilateral only).
What this changes in the deposit:
  - BIDS tree regenerated for sub-1..sub-14; task label ``imagery`` -> ``reaching`` (files and TaskName);
    eeg.json TaskDescription/Instructions describe the executed protocol; the imagery CogAtlasID is removed;
    events.json HED tags the movements as agent actions; events keep correct trials only (S128) plus ``rest``.
  - participants.tsv: each participant's own age/sex/handedness from the release's Metadata/<code>.txt
    (version 1.0.x wrote the cohort mean age for everyone and no sex), plus study and release pseudo-code.
  - sourcedata/: the 54 BrainVision files of the 6 new participants, byte-checked (SHA-256) against v2;
    the 147 existing files are verified identical to their v2 members; provenance updated.
  - dataset_description.json (Name and Version untouched), README.md, CHANGES, code/.
No acquisition date is added (the release's Metadata texts carry exact dates; only age/sex/hand are taken).
"""

import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO, BIDS, V2, OUT = (Path(a) for a in sys.argv[1:5])
OUT.mkdir(parents=True, exist_ok=True)
DATE = "2026-10-29"
NEW_VERSION = "1.1.0"
CODES = ["AV82", "JD68", "JV43", "QS70", "RA12", "UP28", "XP01", "ZS27",
         "AF64D", "AU12D", "AW98D", "BR39D", "BS34D", "BZ29D"]
NEW_CODES = CODES[8:]
V2_URL = "https://zenodo.org/api/records/17940098/files/EEG_dataset.zip/content"
EXPECTED = {"unilateral": 1662, "bilateral": 959, "rest": 2542}
TASK_DESC = (
    "Executed (not imagined), self-initiated, self-paced reaching movements. Each trial is a rest of at least 5 s "
    "with the hands on hand switches (a shorter rest triggered an error message), the movement onset (time 0), then "
    "the self-paced execution until the hands are back on the switches. Unilateral: the right thumb presses a button "
    "placed in front of the participant; bilateral: both arms reach synchronously. 3 sets of 40 movements per "
    "condition (acq-unilateral, acq-bilateral); participants 9-14 (second study) recorded the unilateral condition only."
)
INSTRUCTIONS = (
    "Rest with both hands on the hand switches for at least 5 s, then, whenever you decide, reach and press the "
    "button (right thumb, or both arms in the bilateral condition) and return the hands to the switches."
)
HED = {
    "unilateral": "Agent-action, (Move, (Right, Hand)), Label/unilateral",
    "bilateral": "Agent-action, (Move, (Left, Hand)), (Move, (Right, Hand)), Label/bilateral",
    "rest": "Agent-action, Rest, Label/rest",
}


def die(msg):
    print("FATAL:", msg, flush=True)
    sys.exit(3)


def git(*args):
    r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
    if r.returncode != 0:
        die(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(p, d):
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


rec = {"date": DATE}

# ---- 0. sanity of inputs
subs = sorted(p.name for p in BIDS.glob("sub-*") if p.is_dir())
if subs != sorted(f"sub-{i}" for i in range(1, 15)):
    die(f"conversion has {subs}")
prov_p = REPO / "sourcedata" / "sourcedata_provenance.json"
prov = json.loads(prov_p.read_text())
if len(prov["files"]) != 147:
    die(f"provenance has {len(prov['files'])} files, expected 147")

# ---- 1. existing sourcedata == v2 members (provenance SHA-256 and git-annex key SHA-256)
for e in prov["files"]:
    member = V2 / "EEG" / e["file"]
    if not member.exists():
        die(f"v2 lacks {e['file']}")
    s = sha256(member)
    if s != e["sha256"]:
        die(f"{e['file']}: v2 sha256 differs from provenance")
    # blob = symlink target or unlocked pointer; both name the git-annex key
    blob = git("show", f"HEAD:sourcedata/{e['file']}")
    m = re.search(r"SHA256E-s(\d+)--([0-9a-f]{64})", blob)
    if not m or m.group(2) != s or int(m.group(1)) != e["bytes"]:
        die(f"{e['file']}: annex key in {blob[:120]!r} does not match v2 sha256/size")
rec["existing_sourcedata_identical_to_v2"] = len(prov["files"])

# ---- 2. new participants' sourcedata
added = []
for i, code in enumerate(NEW_CODES, start=9):
    src = V2 / "EEG" / "unilateral" / code
    files = sorted(src.iterdir())
    if len(files) != 9:
        die(f"{code}: {len(files)} files, expected 9 (3 sets x vhdr/vmrk/eeg)")
    if (V2 / "EEG" / "bilateral" / code).exists():
        die(f"{code}: unexpected bilateral folder")
    dst = REPO / "sourcedata" / "unilateral" / code
    dst.mkdir(parents=True, exist_ok=False)
    for f in files:
        shutil.copy2(f, dst / f.name)
        rel = f"unilateral/{code}/{f.name}"
        added.append({"file": rel, "bytes": f.stat().st_size, "sha256": sha256(dst / f.name), "subject": str(i),
                      "url": f"{V2_URL}#EEG_dataset/EEG/{rel}"})
prov["files"].extend(added)
prov["n_files"] = len(prov["files"])
prov["total_bytes"] = sum(e["bytes"] for e in prov["files"])
prov.setdefault("revisions", []).append({
    "date": DATE, "version": NEW_VERSION,
    "added_files": len(added), "added_bytes": sum(e["bytes"] for e in added),
    "note": ("Version 2 of the release (Zenodo record 17940098, 10.5281/zenodo.17940098, 2025-12-15) adds participants "
             "AF64D, AU12D, AW98D, BR39D, BS34D, BZ29D (MOABB subjects 9-14; second study, unilateral only). Added their "
             "54 BrainVision files from members EEG_dataset/EEG/unilateral/<code>/ of the v2 archive. The 147 files "
             "already here are byte-identical (SHA-256) to their v2 members, so subjects 1-8 are unchanged. The v2 "
             "Metadata texts are not included (they give exact recording dates); age, sex and handedness are in "
             "participants.tsv."),
})
write_json(prov_p, prov)
rec["sourcedata_added"] = len(added)

# ---- 3. replace the BIDS tree, task imagery -> reaching
old = [p for p in git("ls-files", "--", "sub-*").splitlines() if p]
git("rm", "-r", "-q", "--", *sorted({p.split("/")[0] for p in old}))
rec["bids_files_removed"] = len(old)
written = []
for p in sorted(BIDS.glob("sub-*/**/*")):
    if not p.is_file() or p.name.endswith("_lockfile.json") or p.name.endswith("_scans.tsv") or p.name.endswith("_scans.json"):
        continue
    rel = p.relative_to(BIDS).as_posix().replace("_task-imagery_", "_task-reaching_")
    dst = REPO / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if p.name.endswith("_eeg.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        d["TaskName"] = "reaching"
        d["TaskDescription"] = TASK_DESC
        d["Instructions"] = INSTRUCTIONS
        d.pop("CogAtlasID", None)
        write_json(dst, d)
    elif p.name.endswith("_events.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        levels = d.get("trial_type", {}).get("Levels") or {}
        d.setdefault("trial_type", {})["HED"] = dict(HED)
        d["trial_type"]["Levels"] = {
            "unilateral": "Movement onset of a correct unilateral trial (right thumb presses the button).",
            "bilateral": "Movement onset of a correct bilateral trial (both arms).",
            "rest": "3 s before a correct movement onset whose preceding rest (hands on the switches) lasted >= 5 s.",
            **{k: v for k, v in levels.items() if k not in HED},
        }
        d["Description"] = ("Events of the reaching task: movement onsets of correct trials (motion tracking for "
                            "participants 1-8, right hand-switch release for 9-14) and rest events.")
        write_json(dst, d)
    else:
        shutil.copy2(p, dst)
    written.append(rel)
if any("task-imagery" in w for w in written):
    die("task-imagery left in file names")
rec["bids_files_written"] = len(written)

# ---- 4. events check
counts, per_sub = Counter(), {}
for ev in sorted(REPO.glob("sub-*/ses-*/eeg/*_events.tsv")):
    with open(ev, newline="", encoding="utf-8-sig") as f:
        c = Counter(r["trial_type"] for r in csv.DictReader(f, delimiter="\t"))
    counts.update(c)
    s = ev.name.split("_")[0]
    per_sub.setdefault(s, Counter()).update(c)
if dict(counts) != EXPECTED:
    die(f"event totals {dict(counts)} != {EXPECTED}")
rec["events"] = dict(counts)
rec["events_per_subject"] = {k: dict(v) for k, v in sorted(per_sub.items(), key=lambda kv: int(kv[0][4:]))}

# ---- 5. participants from the release's Metadata texts (age, sex, handedness only)
rows = []
for i, code in enumerate(CODES, start=1):
    t = (V2 / "Metadata" / f"{code}.txt").read_text(encoding="latin1")
    age = re.search(r"^Age:\s*(\d+)", t, re.M)
    sex = re.search(r"^Gender:\s*(\w+)", t, re.M)
    hand = re.search(r"^Left/Right handed:\s*(\w+)", t, re.M)
    if not (age and sex and hand):
        die(f"{code}: metadata fields not found")
    rows.append({
        "participant_id": f"sub-{i}", "age": age.group(1), "sex": {"male": "M", "female": "F"}[sex.group(1).lower()],
        "hand": {"right": "R", "left": "L"}[hand.group(1).lower()], "group": "healthy", "species": "homo sapiens",
        "study": "1" if i <= 8 else "2", "source_id": code,
    })
with open(REPO / "participants.tsv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
write_json(REPO / "participants.json", {
    "participant_id": {"Description": "Participant identifier (MOABB subject number)."},
    "age": {"Description": "Age at recording, from the release's Metadata/<source_id>.txt.", "Units": "years"},
    "sex": {"Description": "Sex as given in the release (Gender field).", "Levels": {"M": "male", "F": "female"}},
    "hand": {"Description": "Handedness as given in the release.", "Levels": {"R": "right", "L": "left"}},
    "group": {"Description": "Participant group.", "Levels": {"healthy": "healthy volunteer"}},
    "species": {"Description": "Species."},
    "study": {"Description": "Study of the release.", "Levels": {
        "1": "first study: unilateral and bilateral conditions, shielded cabin (release v1)",
        "2": "second study: unilateral condition only, standard laboratory (added in release v2)"}},
    "source_id": {"Description": "Pseudo-code of the participant in the release (folder and file names)."},
})
rec["participants"] = {"n": len(rows), "sex": dict(Counter(r["sex"] for r in rows)),
                       "ages": [int(r["age"]) for r in rows]}

# ---- 6. dataset_description (Name, Version, DatasetDOI untouched)
dd_p = REPO / "dataset_description.json"
dd = json.loads(dd_p.read_text())
keep = {k: dd.get(k) for k in ("Name", "Version", "DatasetDOI")}
new = json.loads((BIDS / "dataset_description.json").read_text())
dd["Authors"] = ["Niklas Kueper", "Su Kyoung Kim", "Kartik Chari", "Elsa Andrea Kirchner"]
dd["ReferencesAndLinks"] = ["https://doi.org/10.5281/zenodo.17940098", "https://doi.org/10.5281/zenodo.10229480",
                            "https://doi.org/10.1038/s41598-024-65910-8"]
dd["SourceDatasets"] = [{"DOI": "10.5281/zenodo.17940098", "URL": "https://doi.org/10.5281/zenodo.17940098",
                         "Version": "2 (2025-12-15)"},
                        {"DOI": "10.5281/zenodo.10229480", "URL": "https://doi.org/10.5281/zenodo.10229480",
                         "Version": "1 (2023-11-30)"}]
dd["Keywords"] = new.get("Keywords", dd.get("Keywords"))
if new.get("GeneratedBy"):
    dd["GeneratedBy"] = new["GeneratedBy"]
dd.update({k: v for k, v in keep.items() if v is not None})
write_json(dd_p, dd)

# ---- 7. README.md, CHANGES, code/
readme_old = (REPO / "README.md").read_text(encoding="utf-8")
badge = readme_old.splitlines()[0] if readme_old.startswith("[![DOI]") else ""
body = (BIDS / "README").read_text(encoding="utf-8")
body = body.replace("  Paradigm: imagery", "  Paradigm: movement execution (MOABB paradigm tag: imagery)")
note = f"""
Version {NEW_VERSION} ({DATE})
{'-' * len(f'Version {NEW_VERSION} ({DATE})')}
Rebuilt after the dataset authors' review (https://github.com/NeuroTechX/moabb/issues/1333) and release version 2:
  - 14 participants: the 6 of the second study (sub-9 to sub-14, unilateral condition only) were added from
    Zenodo 10.5281/zenodo.17940098; sub-1 to sub-8 come from the same, unchanged recordings.
  - Movements are executed, not imagined: task label "reaching" (was "imagery"), executed-movement description.
  - Each trial is a rest of at least 5 s, the movement onset (0 s), then self-paced execution. Events keep correct
    trials only (versions 1.0.x also listed error trials, rest < 5 s, and additional trials) and add a "rest"
    event 3 s before a correct onset whose preceding rest lasted at least 5 s.
  - The second study has no motion-tracking marker: its movement onset is the release of the right hand switch,
    which follows the motion-tracking onset by a median of 54 ms in the first study.
  - participants.tsv gives each participant's age, sex and handedness (versions 1.0.x listed the cohort mean age).
"""
(REPO / "README.md").write_text((badge + "\n\n" if badge else "") + body.rstrip() + "\n" + note, encoding="utf-8")
changes_old = (REPO / "CHANGES").read_text(encoding="utf-8")
(REPO / "CHANGES").write_text(
    f"{NEW_VERSION} {DATE}\n"
    "  - Release version 2 (10.5281/zenodo.17940098): added the 6 participants of the second study (sub-9 to sub-14,\n"
    "    unilateral condition only) and their 54 BrainVision source files; sub-1 to sub-8 unchanged (source files\n"
    "    byte-identical in both versions).\n"
    "  - Dataset authors' review (NeuroTechX/moabb#1333): task label reaching (was imagery), executed-movement\n"
    "    description and HED, correct trials only (error and additional trials removed), rest events, per-participant\n"
    "    age/sex/handedness. Rebuilt with MOABB PR #1334 (Kueper2024 loader).\n\n" + changes_old, encoding="utf-8")
for p in (BIDS / "code").glob("*.yaml"):
    shutil.copy2(p, REPO / "code" / p.name)
shutil.copy2(__file__, REPO / "code" / "nm000319_v2_rebuild_20261029.py")

write_json(OUT / "build.json", rec)
print(json.dumps({k: rec[k] for k in ("existing_sourcedata_identical_to_v2", "sourcedata_added", "bids_files_removed",
                                      "bids_files_written", "events", "participants")}, indent=1))
