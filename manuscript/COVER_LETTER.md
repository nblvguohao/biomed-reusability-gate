# Cover letter

Dear Editors,

Please consider our manuscript, “A leakage-safe reusability audit of Squidiff for single-cell temporal prediction,” as a Reusability Report in *Nature Machine Intelligence*.

Squidiff is a diffusion-model framework for predicting cellular development and perturbation responses from single-cell transcriptomes. Its scientific value depends not only on whether released files execute, but also on whether a new research team can identify the necessary preprocessing, exercise the advertised interfaces and obtain defensible predictions when future biological samples are kept outside every fitting and selection step. We therefore audited the pinned public release before evaluating reuse on an independent longitudinal CAR-NK dataset.

The manuscript makes three contributions suited to the journal’s Reusability Report format. First, it separates functional verification of the released checkpoint from predictive assessment. Second, it identifies actionable interface and workflow boundaries and supplies regression-tested corrections. Third, it evaluates temporal prediction at three predeclared cutoffs with five independently trained seeds, four training-only baselines, same-distribution references and structure-aware population metrics. This design shows where conclusions are stable and where they depend on temporal information, baseline choice or the estimand. The released VO analysis is retained only as a target-informed mechanism sanity check; because its checkpoint and direction use target-day information, it does not support out-of-sample generalization.

The work is an independent audit of publicly available software and data, not a challenge to the validity of a single claim in the linked article. Its primary purpose is to establish what another laboratory can reuse, which information boundaries are needed for future prediction, and which executable checks should accompany releases of generative models. We therefore believe the Reusability Report format is more appropriate than a correspondence or Matters Arising format.

The manuscript is original, is not under consideration elsewhere and has been approved by all authors. No new animal, human-participant or wet-laboratory experiments were performed. Publicly deposited single-cell data were reanalysed; derived source data and the code needed to reproduce the audit are described in the availability statements. The manuscript reports no formal null-hypothesis test across computational seeds and does not treat cells or seeds as independent biological replicates.

Generative artificial intelligence was used for language editing, code assistance and preparation of submission materials. The authors inspected the generated text and code, reran the analyses and accept responsibility for the accuracy, originality and integrity of the submitted work.

Thank you for considering this manuscript.

Sincerely,

Ailian Zhou and Lichuan Gu, on behalf of all authors

Corresponding authors: zhouailian@caas.cn; glc@ahau.edu.cn

