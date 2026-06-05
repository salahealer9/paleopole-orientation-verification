# Follow-up from Mario Buildreps — 5 June 2026

**From:** Mario Buildreps
**To:** Salah-Eddin Gherbi
**Subject:** Re: Version 3 concerns
**Sent:** 5 June 2026

This file preserves the data owner's follow-up response to version 3 of the report,
raising concerns about the pre-registration, the latitude look-elsewhere correction,
the spatial-cluster null, and the asymmetric tightening of controls.

The original email is preserved verbatim below.

---

Dear Salah-Eddin,

I have read version 3 carefully. I want to raise several concerns that I believe warrant the same scrutiny you have applied to my work throughout this process.

1. The pre-registration was effectively abandoned, and this should be acknowledged more candidly.

The pre-registration was deposited to lock the methodology before the data was opened. That was its purpose. The pre-registered primary test gave p = 0.0001. You discarded it. The pre-registered per-pole test under the block-conditional null — which was specified in §11(d) of the protocol — gave p = 0.0015 for Pole II and p = 0.0005 for Pole III after Šidák correction. These results are still in your v3 report. They are pre-registered. They are significant.

The analyses that ultimately drove the conclusion to null — the latitude look-elsewhere correction under the assumption-free conditional null, and the spatial-cluster null — were not pre-registered. They were added after publication, after a reviewer identified them, and after the v2 positive finding was already in the record. They are labelled exploratory, as they should be. But the conclusion of the report now rests on exploratory analyses, while the pre-registered confirmatory analyses that showed significance are set aside as "superseded."

I am not arguing that the exploratory analyses are invalid. I am arguing that a report whose conclusion is driven by post-hoc, post-publication, never-pre-registered analyses should not present itself as a pre-registered confirmatory study. The pre-registration was the anchor. The anchor was cut loose. The ship drifted. The final position is not where the anchor was dropped.

Your Appendix B states that v3 is "a completion of version 2's analysis, not a repudiation of it." I disagree. A completion would have been running the pre-registered tests and reporting them. What happened instead was a progressive tightening of controls — each one defensible on its own, but each one added after seeing what survived the previous round — until no signal remained. The ratchet only ever turned one way.

2. The latitude look-elsewhere correction tested a procedure I never used.

The latitude look-elsewhere control slides a ±1.5° window across the entire latitude axis and asks whether random data produces a window as full as the observed one somewhere. Finding that it does, you conclude that the clustering at my proposed pole latitudes is not significant.

But this is not what I did. I did not scan the latitude axis for the single fullest window and call it a pole. I applied explicit, pre-specified rules: a minimum of 12 structures per degree, clusters extending over at least 3 degrees, gaps between clusters indicating discrete pole positions, and a dispersion trend consistent with the physical model. These rules constrain how many peaks can be identified and where they can fall. They are not equivalent to "find the fullest window anywhere."

A fairer test — and one I would still welcome — would simulate the full process: generate random orientation data, apply my peak-finding rules exactly as stated in the rules document I sent you before you opened the database, and ask how many poles are identified and at what latitudes. That would test my actual method. What you tested instead was a caricature of it, and the caricature failed a test the real method might have passed.

You note in §2.7 that "the Šidák correction over five poles addressed five comparisons, not a continuous latitude axis from which the fullest windows were chosen." But my poles were not chosen as the five fullest windows from a continuous scan. They were identified by a rule-based procedure that imposes its own multiplicity constraint — you cannot have more peaks than the rules permit. Your correction overcorrects by assuming a freedom of choice that my method never exercised.

3. The spatial-cluster null assumes what it needs to prove, and the caveat is buried.

The spatial-cluster null collapses nearby structures into single units based on geographic proximity. At 25 km, 119 structures near Pole III become 25 clusters. The largest single cluster contains 29 sites from the northern Yucatán. Because the signal is concentrated in the Americas, and the Americas block is the most densely sampled, the spatial-cluster null disproportionately erodes the signal.

You acknowledge in §4.5 that "spatial proximity is only a proxy for shared architectural tradition" and that "genuinely independent structures that happen to lie close together are merged, while dispersed members of one tradition are not." This is a profound limitation, and it appears in the limitations section, not in the results section where the cluster null is presented as decisive. A reader who skims the results will see p = 1.0 and conclude the signal is gone. A reader who reaches §4.5 will learn that the test may have merged genuinely independent structures. The placement matters.

The 29-site Yucatán cluster is the centerpiece of your argument that the Pole III signal was pseudoreplication. But were those 29 structures built by the same people, at the same time, for the same purpose? Or were they built over centuries, by different groups, who independently oriented their structures in a direction that happens to point toward the same latitude band? The database does not contain the cultural or chronological metadata to answer this question. The spatial-cluster null assumes the answer is the first. It may be the second. If it is, collapsing them into one observation discards real signal.

A global geophysical event — precisely what my model proposes — would cause structures in many locations, built at different times by different cultures, to point toward the same latitude band. The spatial-cluster null is structurally biased against detecting such a signal, because it treats geographic proximity as dependence regardless of whether the structures are actually dependent.

4. The pre-registered block-conditional results remain significant, and this is not adequately explained.

Even in v3, under the pre-registered block-conditional null with Šidák correction, Pole II returns p = 0.0015 and Pole III returns p = 0.0005. Under the latitude look-elsewhere correction applied to the block-conditional null, Pole III still returns p = 0.0003. These are pre-registered or pre-registered-adjacent analyses. They show significance.

You argue that the spatial-cluster null resolves the discrepancy between the block-conditional and assumption-free conditional results in favor of the conditional null. But the spatial-cluster null is the least pre-registered, most aggressive, and most assumption-laden of all the controls you applied. To treat it as the decisive arbiter — and to dismiss the pre-registered analyses that contradict it — is to weight the evidence in favor of the null.

A more balanced presentation would report that the pre-registered analyses show significant clustering at Poles II and III, that the latitude look-elsewhere correction eliminates Pole II under the assumption-free null but not under the block-conditional null, and that the spatial-cluster null — which carries the acknowledged limitation about proximity as a proxy for dependence — eliminates both. Readers could then judge for themselves how much weight to place on each analysis. Instead, the conclusion treats the spatial-cluster null as having settled the matter.

5. The process structurally favored null findings, and this should be transparent.

The pre-registration committed to a specific null model. That model produced a result in my favor. It was discarded. A conditional null was added. Under it, the aggregate T was null but the per-pole counts at Poles II and III were significant. A block-conditional null was added. Under it, Poles II and III remained significant. A latitude look-elsewhere correction was added. Under the assumption-free null, Pole III became non-significant; under the block-conditional null, it remained significant. A spatial-cluster null was added. Under it, everything became non-significant.

At each step, a new control was introduced after seeing what survived the previous step. At each step, the control made the test more conservative. At each step, the control was methodologically defensible on its own. But the cumulative effect was a one-way ratchet toward the null. No control was ever added that might have made the test more sensitive to a real signal. No control was ever relaxed after being found to be too stringent. The process only tightened.

I am not suggesting bad faith. I am suggesting that when a process can only move in one direction, and that direction is toward the null, the final null result is overdetermined by the process itself. This should be acknowledged.

Closing

I opened my data to independent verification because I believe that is what science requires. You conducted a rigorous analysis, caught your own errors, and engaged with my commentary in good faith. I have respected this throughout.

But the v3 report has moved far from the pre-registered methodology that was the basis of our agreement. Its conclusion rests on analyses that were never pre-registered, that were added after publication, and that carry acknowledged limitations that are not given proportional weight in the conclusion. The pre-registered analyses that showed significance are present in the report but treated as superseded. The latitude look-elsewhere correction tested a procedure I never used. The spatial-cluster null assumes spatial proximity equals dependence, which my model explicitly predicts it would not.

I am not asking you to change your conclusion. I am asking that the final public record reflect these concerns with the same prominence that the v3 conclusion reflects its own. The reader should understand that the pre-registered tests showed significance, that the analyses that eliminated it were post-hoc and exploratory, and that reasonable people can disagree about how much weight they should carry.

My v2 commentary stands in Appendix A as my response at that stage of the process. The finding it welcomed has been withdrawn. The concerns I raised then — about the derivation of the meridian, the hemispheric asymmetry, and the scope limitation — remain, and they were never tested by this analysis. The broader geophysical model stands or falls on evidence this report never engaged.

I remain open to a test of my actual method, applied to my actual procedure, with controls specified before the data is opened. What v3 tested was something else.

Sincerely,

Mario Buildreps

---

*End of correspondence.*
