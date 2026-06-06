# Response to Mario Buildreps — 6 June 2026

**From:** Salah-Eddin Gherbi
**To:** Mario Buildreps
**Subject:** Re: version 3 — your 5 June follow-up (points 1–5)
**Sent:** 6 June 2026

This file preserves the response sent to the data owner after his 5 June 2026
follow-up letter. It is paired with `2026-06-05_followup_from_mario.md` in this
directory.

The response:
- Closes point 2 (script 11: rule faithful, baseline is the issue)
- Splits point 3 into within-site replication (resolved by his data) and
  cross-site convergence (requires his evidence)
- Flags Palenque/Cancuén coordinate discrepancies for confirmation
- States decision rule for cross-site evidence

---

Dear Mr. Buildreps,

Thank you for reading version 3 so carefully and for setting out your concerns at length. They warrant a substantive reply, and they have already prompted additional analysis and revisions, summarised below. Your letter is preserved verbatim in the report (Appendix D) so that it stands at the same prominence as my conclusions.

Let me take your five points in three groups: one I concede, three I have addressed in the revision, and one that remains genuinely open and now sits with you.

1. Point 2 — your method, not a caricature. You were right. The latitude look-elsewhere correction in the earlier version modelled a worst-case continuous search, not the rule-based procedure you actually use. I have now implemented your stated rules directly — minimum 12 structures per degree, clusters spanning at least 3 degrees, totals at least 36, the near-pole adjustment — exactly as you set them out in your 17 May email, with unit tests confirming the implementation matches your thresholds (script 11, §3.8.4 of the report).

The result has two parts. First, your rule, faithfully implemented, recovers your poles II–V on the observed data — so this tests your actual method. Second, when the same rule is run on data generated under realistic null models, it identifies no more poles than chance does (it covers the 72° band in essentially every random replicate, because the great-circle geometry concentrates intersections there regardless of permutation). And your per-degree binomial, which produces the 100% / 99.999% figures, was computed correctly — but those figures depend entirely on a uniform baseline of ~11 structures per degree. When I re-run your identical binomial using the per-degree expectation the site geography actually produces, the same counts that gave p = 1.6 × 10⁻⁹ at Pole III give p ≈ 0.03; Pole I moves from 10⁻⁵¹ to 0.67. The disagreement was never your rule. It is the baseline the rule's output is scored against: a uniform sky the data do not have.

2. Points 1, 4 and 5 — pre-registered vs exploratory, and the "ratchet." Version 3.1 now presents the pre-registered and exploratory results side by side (§3.7), with the methodological status and known caveat of each, so a reader can weigh them directly. I have not hidden that the conclusion rests on exploratory controls; I have set out why a pre-registered test with a since-identified flaw (treating spatially autocorrelated structures as independent) does not override the analysis that identified the flaw. On the "one-way ratchet": each successive control corrected an assumption that biased significance upward, so correcting them could only move the result one way — and one control (the finer-block gate) was specified so that it could have exonerated Pole III had its significance risen, and it did not. I record both points in the revision; readers who weight pre-registration status more heavily than I do can see every number and decide for themselves.

3. Point 3 — the spatial-cluster null and independence. This is the one I cannot close from the statistics alone, and I want to engage it precisely rather than wave it away.

When I pulled the membership of the 29-entry cluster that dominates the Pole III count, it resolved not to 29 sites but to 8 distinct named locations:

  Uxmal — 8 entries
  Labna — 6
  Kabah — 6
  Chacmultun — 4
  Xlapak — 2
  Palenque — 1
  Cancuén — 1
  Sayil — 1

The database has no unique structure identifiers, and the only explanatory note in the Remarks column for any of these is "2 structures similar oriented" (Sayil) — which points toward shared orientation, not independence. So part of your point 3 is answered by your own data: eight bearings recorded under the name "Uxmal" are not eight independent observations of a former pole, whatever Uxmal's construction history, and the cluster null collapsing them is the correct treatment of that multiplicity, not an over-aggressive one.

The part of your point 3 that does remain open is different and real: whether these distinct locations — Uxmal, Kabah, Sayil, and so on — represent cultures that independently converged on the same orientation, or one regional tradition that transmitted it. A global event would predict the former; a shared Maya convention would produce the latter. The database cannot distinguish these from its own contents, and I am a statistician, not an archaeologist; I am not in a position to adjudicate Maya chronology.

So I would ask you, as the author of the model that predicts independence, to supply what would let the question be tested without circularity. Specifically, for the structures in these eight locations:

  (a) unique structure identifiers, so multiple bearings at one site can be told apart;
  (b) construction dates that are model-independent — radiocarbon, ceramic seriation, or epigraphic — rather than inferred from orientation, since orientation-derived dates would assume the very conclusion under test;
  (c) the polity or cultural sphere each is attributed to.

The decision rule, stated in advance so neither of us fits it after the fact: if those data show the locations span multiple periods and multiple independent polities with a shared orientation not explained by a single documented Mesoamerican orientation family, then the cluster null over-merged genuinely independent observations, point 3 carries real weight, and I will run a new, pre-registered analysis (version 4) that incorporates the chronological constraints. If the available dating is orientation-derived, or absent, then the independence of these structures cannot be established from the evidence, and the conclusion stands under its stated and clearly-disclosed assumption.

One small data point I should flag, in that spirit: two of the entries carry names — Palenque and Cancuén — whose conventionally known locations (Chiapas and the Petén, respectively) do not match the coordinates recorded for them here, which sit in the Puuc region beside Kabah and Sayil. I mention it not to score a point but because it bears directly on (a): without structure-level provenance, I cannot tell whether these are mislabelled entries or different structures sharing a name, and that is exactly the kind of thing the identifiers would resolve.

To be clear about where this leaves us: the statistical question I pre-registered — do these orientations point at the proposed latitudes more than chance — has been answered across four null models, and the answer is no. Your broader geophysical model is not something this analysis tested or could test, and nothing here speaks to it except to remove the orientation-clustering result that had been offered as evidence for it. Point 3 is the one place where new evidence could change the statistical finding, and the evidence that would do so is evidence you are far better placed to provide than I am.

I remain glad you opened your data to this. It is rare, and it is the right instinct. I will hold the version 3.1 deposit until I hear from you, so that whatever you send can be reflected in the record.

With respect,
Salah-Eddin Gherbi
