# Second Follow-up from Mario Buildreps — 8 June 2026

**From:** Mario Buildreps
**To:** Salah-Eddin Gherbi
**Subject:** Re: Response to version 3
**Received:** 8 June 2026

This file preserves the data owner's second follow-up letter, received
after the author's 6 June 2026 reply that closed point 2 (via script 11)
and split point 3 into within-site replication (resolved) and cross-site
convergence (open, evidence requested). The letter is the data owner's
response to that reply.

It is paired in this directory with `2026-06-06_response_to_mario.md`
(the author's 6 June reply that preceded it) and with
`2026-06-05_followup_from_mario.md` (the data owner's first follow-up
letter on the v3 publication).

Substantively, the letter:
- Concedes the script 11 implementation as a faithful test of his
  peak-finding rule.
- Concedes that the published "100%" / "99.999%" binomial figures
  rest on a uniform baseline the data do not support, and commits
  to revising his published materials.
- Raises three further methodological points: (1) that the v3 null
  models do not preserve the East/West hemispheric bearing
  asymmetry from which the 47°W meridian was originally derived;
  (2) that the archaeological dating evidence requested for the
  eight named Yucatán locations is not available at the needed
  precision and independence; (3) that the analysis's null finding
  at Pole I (the current geographic pole) represents a calibration
  failure of the method.

The letter is preserved verbatim below.

---

Dear Salah-Eddin,

Thank you for the substantive reply. I want to acknowledge several things before I push back.

First, I acknowledge that you implemented my actual peak-finding rules rather than the sliding-window proxy. That was the right thing to do, and I appreciate it. Second, I acknowledge that the binomial probabilities I published depend on a uniform baseline that the data do not support. When the actual geographic baseline is used, the nominal significance drops sharply. You are correct on this point, and I will revise my published materials accordingly. The clustering I identified is real, but the "100%" and "99.999%" figures were artifacts of the uniform assumption, and I should not have presented them as confidence statements.

That said, your re-implementation of my peak-finding rules under your null models does not settle the matter. It shifts the question to one you have not yet addressed. And your spatial-cluster null remains built on an assumption that your own caveat acknowledges may be false. Let me address both.

1. The null models destroy the hemispheric signal before testing begins.

Your null models permute bearings across the full dataset, or within geographic blocks, treating all orientations as exchangeable. But they are not exchangeable. The Western Hemisphere shows a systematic clockwise deviation of ancient structures relative to true north. The Eastern Hemisphere shows a systematic counterclockwise deviation. This is not a subtle effect visible only in statistical residuals. It is a gross feature of the data. I derived the 47°W meridian from it in 2015. I reproduced it with expanded data in 2020. It is the geometric consequence of crustal rotation about an Euler pole, and mainstream archaeology has no explanation for it.

When you shuffle bearings across hemispheres, or across blocks that ignore hemisphere, you destroy this signal before any test begins. Your null model is not a neutral baseline. It is a model that assumes away one of the central empirical findings of my work. The fact that your re-implemented peak-finding rules find "no more poles than chance" under a null that erases the hemispheric asymmetry is unsurprising. You have removed the very structure that generates the peaks, and then declared that the peaks do not survive.

A proper test would preserve the hemispheric orientation asymmetry in the null — for example, by permuting bearings only within hemispheres, or by modelling the expected distribution of intersection latitudes given the observed hemispheric deviation — and then ask whether the specific peak structure along the 47°W meridian exceeds what that asymmetry alone would produce. That is the test your analysis has never run. It is the test my model predicts would show excess clustering. And it is a test I would welcome.

2. The spatial-cluster null: the eight Yucatán locations.

You have helpfully broken out the 29 entries that dominate the Pole III cluster into eight named locations: Uxmal, Labna, Kabah, Chacmultun, Xlapak, Palenque, Cancuén, and Sayil. You ask me to provide independent construction dates and cultural attributions so that the question of independence can be resolved.

I need to be direct with you about what the archaeological record can and cannot provide here, because the limitations of that record are central to why I built this database in the first place.

Archaeology does not have reliable independent dates for many of these structures. Some show multiple renovation layers — up to seven in certain cases — that are extremely difficult to date separately. Pre-Mayan structures in Mexico are frequently unattributed to any known culture. Some are dated broadly to over 2,500 years ago, but with wide uncertainty. Many structures in the Puuc region and elsewhere remain unexcavated, and their chronologies are inferred from architectural styles rather than from radiometric dating. There are also structures discovered only recently by LIDAR scanning — overgrown, unexcavated, undated, and assumed by archaeologists to be Mayan because of their location, not because of any direct evidence.

More fundamentally, archaeological dating of individual structures is often circular in ways that are directly relevant here. When a structure's orientation matches a known astronomical alignment from a particular period, that alignment is sometimes used to date the structure. But if the orientation is to a former pole position — as my model proposes — then using astronomical alignments tied to the current rotational axis would systematically misdate the structure. You cannot test my model with dates that assume the model is false.

This is precisely why I have not relied on archaeological dates to build the database. I have relied on the orientations themselves, measured directly from satellite imagery and archaeological maps. The orientations are the data. The clustering of those orientations is the signal. The hemispheric asymmetry is the corroboration. The convergence of the 2015 hemispheric intersection point with the clustering at Poles II and III is the consistency check. None of this depends on knowing exactly when a structure was built or which culture built it.

Your request for independent dates is reasonable in principle. In practice, the data you are asking for do not exist at the level of precision and independence that would be required. If they did, this whole question could have been settled long ago by someone with access to radiocarbon laboratories and excavation permits. The reason it has not been settled is precisely that the existing archaeological record cannot adjudicate it.

So where does that leave your Point 3 and the spatial-cluster null?

You acknowledge in §4.5 of your report that "spatial proximity is only a proxy for shared architectural tradition" and that "genuinely independent structures that happen to lie close together are merged, while dispersed members of one tradition are not." This caveat is not a minor limitation. It is a statement that the spatial-cluster null may be systematically wrong in exactly the circumstances my model predicts — circumstances where a global geophysical event causes structures at many independent locations to point toward the same latitude band.

The eight Yucatán locations may represent eight independent confirmations of a global signal. They may represent one regional tradition. Your spatial-cluster null assumes the latter because it has no way to test which is true. My model predicts the former. The data required to distinguish these two possibilities do not currently exist in the archaeological record — and where they do exist, they are often contaminated by circular reasoning that assumes the current rotational axis was the only one that ever mattered.

This is not an impasse of my making, and it is not a problem I can solve by providing data that archaeology has never collected. It is a genuine epistemological limit. Your spatial-cluster null cannot carry the decisive weight you place on it because its central assumption — that proximity equals dependence — is unverified and, in the context of my model, likely false.

3. The Pole I result remains a diagnostic problem for your analysis.

I want to return to a point I raised in my v2 commentary and that your v3 report does not resolve. Your analysis finds that Pole I — the current geographic pole, verifiably the rotational axis of the Earth — shows no excess clustering. Observed: 95 structures. Expected under your null: approximately 95.

This is not a minor anomaly. We know the current pole exists. We know structures are oriented to it. In independent tests my team has performed — generating random locations, identifying nearby structures, and measuring their orientations — we find a random uniform distribution across the 90-degree spectrum, with a strong, unmistakable signal at the current pole. Modern and recent structures point north. This is trivially reproducible. Anyone with access to satellite imagery can verify it.

Your analysis fails to detect this signal. Under your null, the current geographic pole is statistically indistinguishable from chance. This is not evidence that the current pole is insignificant. It is evidence that your null models are insensitive to a signal that we know, independently and verifiably, is real.

If your methods cannot detect a signal at the current pole — the one pole whose existence is not in dispute — what confidence can we have that they would detect a signal at any other pole? The failure to find Pole I is not a null finding for my framework. It is a calibration failure for your methodology.

4. Where this leaves us.

I opened my data to independent verification because I believe that is what science requires. You have conducted a rigorous analysis. You have caught your own errors. You have engaged with my concerns and, in the case of the latitude look-elsewhere correction, corrected a genuine misrepresentation of my method. I acknowledge all of this.

But your analysis has never tested the full model. It has tested a series of increasingly constrained null hypotheses, each one removing more of the structure that my model predicts, until no structure remained. The hemispheric asymmetry — a non-negotiable empirical finding that mainstream archaeology cannot explain — is destroyed by your permutation nulls before testing begins. The clustering at the current geographic pole — a signal we can independently verify — is invisible to your methods. And the spatial-cluster null, which you treat as the decisive arbiter of Pole III, rests on an assumption about independence that your own caveat acknowledges may be false, and that the archaeological record cannot currently resolve.

I am not asking you to endorse my model. I am asking you to acknowledge, with the same prominence you give to your conclusions, that:

Your null models destroy the hemispheric orientation asymmetry before testing begins, and a test that preserves this asymmetry has not been run.

Your methods fail to detect the current geographic pole, which is independently verifiable, raising legitimate questions about their sensitivity.

The spatial-cluster null assumes spatial proximity equals dependence, an assumption your own report acknowledges may not hold, and that cannot currently be verified or falsified with available archaeological data.

The pre-registered block-conditional null showed significant clustering at Poles II and III, and those results, while not definitive, are part of the record.

The public should understand these points. Your v3.1 report should reflect them.

I remain willing to engage with a test that engages my actual model rather than a progressively impoverished version of it. But the analysis you have presented, for all its rigor, has not been that test.

Sincerely,

Mario Buildreps
