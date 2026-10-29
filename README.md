[![DOI](https://img.shields.io/badge/DOI-10.82901%2Fnemar.nm000319-blue)](https://doi.org/10.82901/nemar.nm000319)

Kueper2024
==========

Unilateral and bilateral movement-execution EEG dataset [1]_, [2]_, [3]_.

Dataset Overview
----------------
  Code: Kueper2024
  Paradigm: movement execution (MOABB paradigm tag: imagery)
  DOI: 10.1038/s41598-024-65910-8
  Subjects: 14
  Sessions per subject: 1
  Events: unilateral=1, bilateral=2, rest=3
  Trial interval: (-2.0, 1.0) s
  Runs per session: 6
  File format: BrainVision

Acquisition
-----------
  Sampling rate: 500.0 Hz
  Number of channels: 67
  Channel types: eeg=64, misc=3
  Channel names: Fp1, Fp2, F7, F3, Fz, F4, F8, FC5, FC1, FC2, FC6, T7, C3, Cz, C4, T8, TP9, CP5, CP1, CP2, CP6, TP10, P7, P3, Pz, P4, P8, PO9, O1, Oz, O2, PO10, AF7, AF3, AF4, AF8, F5, F1, F2, F6, FT9, FT7, FC3, FC4, FT8, FT10, C5, C1, C2, C6, TP7, CP3, CPz, CP4, TP8, P5, P1, P2, P6, PO7, PO3, POz, PO4, PO8
  Montage: extended 10-20
  Hardware: Brain Products LiveAmp64 (wireless, active electrodes)
  Reference: FCz
  Ground: AFz
  Sensor type: active
  Line frequency: 50.0 Hz
  Cap manufacturer: Brain Products GmbH
  Cap model: Acticap slim
  Electrode type: active

Participants
------------
  Number of subjects: 14
  Health status: healthy
  Age: mean=24.57, std=3.06, min=19, max=30
  Gender distribution: male=6, female=8
  Handedness: right

Experimental Protocol
---------------------
  Paradigm: movement execution (MOABB paradigm tag: imagery)
  Number of classes: 3
  Class labels: unilateral, bilateral, rest
  Trial duration: 3.0 s
  Study design: Executed (not imagined), self-initiated, self-paced reaching movements: unilateral (right thumb presses a button in front of the participant) and bilateral (both arms synchronously), each followed by a return of the hands to hand switches. Each movement follows a rest of at least 5 s with the hands on the switches; a shorter rest triggered an error message. 3 sets of 40 movements per condition. First study: 8 subjects, both conditions; second study: 6 subjects, unilateral only.
  Feedback type: none
  Synchronicity: self-paced
  Mode: offline

HED Event Annotations
---------------------
  Schema: HED 8.4.0 | Browse: https://www.hedtags.org/hed-schema-browser

  rest
    ├─ Sensory-event
    ├─ Experimental-stimulus
    ├─ Visual-presentation
    └─ Rest

  unilateral
    ├─ Sensory-event
    └─ Label/unilateral

  bilateral
    ├─ Sensory-event
    └─ Label/bilateral

Paradigm-Specific Parameters
----------------------------
  Detected paradigm: motor_imagery
  Imagery tasks: unilateral, bilateral, rest

Data Structure
--------------
  Trials: 240
  Trials per class: unilateral=120, bilateral=120
  Blocks per session: 6
  Trials context: 3 sets of 40 executed movements per condition by design; one run per set. Subjects 1-8: 6 runs (subject XP01: 7 recordings, its third unilateral set split in two), 240 movement trials. Subjects 9-14: 3 unilateral runs, 120 movement trials. Error and additional trials are dropped (only onsets followed by the end-of-correct-trial marker S128 are kept); one rest trial is added per correct movement whose preceding rest lasted at least 5 s. Loaded: 1,662 unilateral, 959 bilateral and 2,542 rest trials (subjects 9-14: 116-119 movements, as most of their recordings also mark the first hand placement with S128).

Preprocessing
-------------
  Data state: raw
  Preprocessing applied: False
  Highpass filter: 0.1 Hz
  Lowpass filter: 131.0 Hz
  Notes: Hardware-prefiltered by the amplifier to 0.1-131 Hz; no further preprocessing applied.

Tags
----
  Modality: Motor
  Type: Movement Execution

Documentation
-------------
  Description: EEG dataset of self-initiated, executed unilateral (right arm) and bilateral reaching movements from 14 healthy subjects (8 in both conditions, 6 in the unilateral condition only), for movement intention recognition in exoskeleton-supported rehabilitation.
  DOI: 10.1038/s41598-024-65910-8
  License: CC-BY-4.0
  Investigators: Niklas Kueper, Su Kyoung Kim, Kartik Chari, Elsa Andrea Kirchner
  Institution: German Research Centre for Artificial Intelligence (DFKI)
  Country: DE
  Repository: Zenodo
  Data URL: https://doi.org/10.5281/zenodo.17940098
  Publication year: 2024
  Keywords: EEG, movement intention, movement execution, ERP, BCI, stroke rehabilitation, LRP

References
----------
Kueper, N., Kim, S. K., & Kirchner, E. A. (2023). EEG Dataset of Unilateral and Bilateral Movement Executions [Data set]. Zenodo. DOI: https://doi.org/10.5281/zenodo.10229480

Kueper, N., Kim, S. K., & Kirchner, E. A. (2024). Avoidance of specific calibration sessions in motor intention recognition for exoskeleton-supported rehabilitation through transfer learning on EEG data. Scientific Reports, 14(1), 16690. DOI: https://doi.org/10.1038/s41598-024-65910-8

Kueper, N., Kim, S. K., Chari, K., & Kirchner, E. A. (2025). EEG dataset of unilateral and bilateral movement executions (version 2) [Data set]. Zenodo. DOI: https://doi.org/10.5281/zenodo.17940098

Notes

.. versionadded:: 1.8.0

.. versionchanged:: 1.8.0 Version 2 of the release (subjects 9-14), ``rest`` class, error and additional trials dropped (:gh:`1333`).
Appelhoff, S., Sanderson, M., Brooks, T., Vliet, M., Quentin, R., Holdgraf, C., Chaumon, M., Mikulan, E., Tavabi, K., Hochenberger, R., Welke, D., Brunner, C., Rockhill, A., Larson, E., Gramfort, A. and Jas, M. (2019). MNE-BIDS: Organizing electrophysiological data into the BIDS format and facilitating their analysis. Journal of Open Source Software 4: (1896). https://doi.org/10.21105/joss.01896

Pernet, C. R., Appelhoff, S., Gorgolewski, K. J., Flandin, G., Phillips, C., Delorme, A., Oostenveld, R. (2019). EEG-BIDS, an extension to the brain imaging data structure for electroencephalography. Scientific Data, 6, 103. https://doi.org/10.1038/s41597-019-0104-8

---
Generated by MOABB 1.8.0 (Mother of All BCI Benchmarks)
https://github.com/NeuroTechX/moabb

Version 1.1.0 (2026-10-29)
--------------------------
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
