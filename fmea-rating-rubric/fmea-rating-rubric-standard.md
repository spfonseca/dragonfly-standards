# FMEA Rating Rubric Standard

| Field | Value |
|---|---|
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-09-20 |

## Purpose

This standard fixes the rubric under which a failure modes and effects analysis (FMEA) rates
**severity**, **occurrence** and **detection**, so that a 7 in one analysis means what a 7 means in
every other. An FMEA's value is comparative — which failure modes deserve action first, across a
portfolio and over time — and ratings read against different anchors, or against none, cannot be
compared. The rubric is therefore one for the organization, published once, and rated against
rather than reinvented.

## Scope

Applies to every FMEA recorded as a `failure-modes-effects-analysis` resource of the Enterprise
Architecture Guidance service, to every experience that renders or authors one, and to the
`fmea-analysis/rubrics` resource that serves the rubric. Specific to FMEA: each kind of analysis
defines its own rubric, and this one is not shared with any other. Any requirement may be waived
only through an explicit, documented, approved waiver recorded in the analysis itself.

---

## 1. One Rubric

### 1.1 Rate every analysis against the published rubric.

[REQUIRED] Every FMEA shall rate severity, occurrence and detection against the organization's
published rubric, served whole as the singleton `GET /v1/fmea-analysis/rubrics` with one attribute
per scale — `severity`, `occurrence`, `detection`. An analysis shall not define, carry or
reference a rubric of its own. *Rationale:* Two competing tables make no two analyses comparable,
which is the only reason to have a rubric at all.

### 1.2 Rate on a ten-point integer scale, ten the worst.

[REQUIRED] Each of the three ratings shall be an integer from 1 to 10, where 10 is the worst
outcome on that scale: the gravest effect, the most frequent cause, the least detectable failure.
Detection therefore reads the other way round from a likelihood — 10 means no control would catch
it. *Rationale:* Ten points is what the anchor tables resolve; a coarser scale loses the
distinctions the tables draw, and a finer one invents distinctions they do not.

### 1.3 Rate against the level's criteria, not against other failure modes.

[REQUIRED] A rating shall be the level whose criteria the failure mode meets, read from the table.
It shall not be adjusted to rank one failure mode above another within the analysis. *Rationale:*
Relative rating makes the scale local to one analysis; the anchors exist so a rating stands alone.

### 1.4 Treat the served rubric as authoritative.

[RECOMMENDED] A consumer may bundle a copy of the rubric so ratings can be explained before
anything is fetched, but the copy should be the same content as the published version and the
served singleton should govern where they differ. *Rationale:* The rubric will be revised; a
consumer explaining a rating against a stale copy explains it wrongly.

---

## 2. Severity

### 2.1 Rate severity from the worst credible effect of the failure mode.

[REQUIRED] Severity shall be rated on the worst effect the failure mode can credibly produce, by
who is exposed and whether the failure gives warning, against the table below. *Rationale:* Effects
are listed several to a failure mode; the rating that matters for action is the one that would
hurt most.

| Ranking | Level | Severity of effect |
|---|---|---|
| 10 | Hazardous - Without Warning | May expose client to loss, harm or major disruption - failure will occur without warning |
| 9 | Hazardous - With Warning | May expose client to loss, harm or major disruption - failure will occur with warning |
| 8 | Very High | Major disruption of service involving client interaction, resulting in either associate re-work or inconvenience to client |
| 7 | High | Minor disruption of service involving client interaction and resulting in either associate re-work or inconvenience to clients |
| 6 | Moderate | Major disruption of service not involving client interaction and resulting in either associate re-work or inconvenience to clients |
| 5 | Low | Minor disruption of service not involving client interaction and resulting in either associate re-work or inconvenience to clients |
| 4 | Very Low | Minor disruption of service involving client interaction that does not result in either associate re-work or inconvenience to clients |
| 3 | Minor | Minor disruption of service not involving client interaction and does not result in either associate re-work or inconvenience to clients |
| 2 | Very Minor | No disruption of service noticed by the client in any capacity and does not result in either associate re-work or inconvenience to clients |
| 1 | None | No Effect |

### 2.2 Keep severity where it is unless the failure mode itself is changed.

[REQUIRED] Actions that reduce how often a cause occurs or how soon a failure is detected shall not
lower the post-mitigation severity. Severity moves only when the effect is changed — a graceful
degradation designed in, an exposure removed. *Rationale:* Severity is a property of the effect,
not of the odds; lowering it because the odds fell hides the worst case from the reader.

---

## 3. Occurrence

### 3.1 Rate occurrence of the cause against a time period or a per-item rate.

[REQUIRED] Occurrence shall be rated on how often the cause produces the failure mode, against the
table below, using whichever of the time-period or per-item anchor fits how the function runs.
Where a rate has been observed, it shall be used in place of judgment. *Rationale:* A probability
without an anchor is a feeling, and two analysts' feelings do not compare.

| Ranking | Level | Probability of failure | Time period | Per item |
|---|---|---|---|---|
| 10 | Very High | Failure is almost inevitable | More than once per day | >= 1 in 2 |
| 9 | Very High | Failure is almost inevitable | Once every 3-4 days | 1 in 3 |
| 8 | High | Generally associated with processes similar to previous processes that have often failed | Once every week | 1 in 8 |
| 7 | High | Generally associated with processes similar to previous processes that have often failed | Once every month | 1 in 20 |
| 6 | Moderate | Generally associated with processes similar to previous processes which have experienced occasional failures, but not in major proportions | Once every 3 months | 1 in 80 |
| 5 | Moderate | Generally associated with processes similar to previous processes which have experienced occasional failures, but not in major proportions | Once every 6 months | 1 in 400 |
| 4 | Moderate | Generally associated with processes similar to previous processes which have experienced occasional failures, but not in major proportions | Once a year | 1 in 800 |
| 3 | Low | Isolated failures associated with similar processes | Once every 1 - 3 years | 1 in 1,500 |
| 2 | Very Low | Only isolated failures associated with almost identical processes | Once every 3 - 6 years | 1 in 3,000 |
| 1 | Remote | Failure is unlikely. No failures associated with almost identical processes | Once every 7+ years | 1 in 6000 |

---

## 4. Detection

### 4.1 Rate detection from the controls in place, not the controls planned.

[REQUIRED] Detection shall be rated on the likelihood that the current prevention and detection
controls catch the failure before the next process step or before a client is exposed, against the
table below. A recommended action shall not lower detection until it is an action taken.
*Rationale:* A control that does not exist yet detects nothing; rating it as if it did records the
plan as the state.

| Ranking | Level | Likelihood the existence of a defect will be detected by process controls before next or subsequent process, or before exposure to a client |
|---|---|---|
| 10 | Almost Impossible | No known controls available to detect failure mode |
| 9 | Very Remote | Very remote likelihood current controls will detect failure mode |
| 8 | Remote | Remote likelihood current controls will detect failure mode |
| 7 | Very Low | Very low likelihood current controls will detect failure mode |
| 6 | Low | Low likelihood current controls will detect failure mode |
| 5 | Moderate | Moderate likelihood current controls will detect failure mode |
| 4 | Moderately High | Moderately high likelihood current controls will detect failure mode |
| 3 | High | High likelihood current controls will detect failure mode |
| 2 | Very High | Very high likelihood current controls will detect failure mode |
| 1 | Almost Certain | Current controls almost certain to detect the failure mode. Reliable detection controls are known with similar processes. |

---

## 5. Prioritisation

### 5.1 Do not compute or store a risk priority number.

[REQUIRED] The product of the three ratings (RPN) shall not be stored on the analysis and shall not
be shown in an experience that renders one. *Rationale:* The product hides which rating drove it — a
10 × 1 × 1 and a 2 × 5 × 1 are not the same kind of problem, and the first is the one that matters.
The AIAG-VDA handbook withdrew RPN for the same reason.

### 5.2 Prioritise with severity dominating.

[REQUIRED] Where failure modes are ordered or actions prioritised, severity shall order first,
occurrence second, detection third. *Rationale:* The gravest effect deserves attention whatever its
odds; the odds decide among effects of equal gravity.

### 5.3 Re-rate after actions taken, on the same rubric.

[REQUIRED] Post-mitigation severity, occurrence and detection shall be rated only once the actions
they credit have been taken, against the same tables, and recorded alongside the original ratings
rather than in their place. *Rationale:* The before and the after are the evidence that the action
worked; overwriting the before loses it.

---

## 6. Presentation

### 6.1 Say what a rating means wherever the number is shown.

[RECOMMENDED] An experience that shows a rating should show, on demand, the level and criteria it
denotes on its scale. *Rationale:* A bare 7 is read against whatever scale the reader has in their
head; the level text puts the published one there.

### 6.2 Keep the rubric reachable from any view of an analysis.

[RECOMMENDED] The three tables should be reachable from the analysis being read without leaving
it. *Rationale:* Ratings are checked in the reading; a rubric elsewhere is a rubric not consulted.
