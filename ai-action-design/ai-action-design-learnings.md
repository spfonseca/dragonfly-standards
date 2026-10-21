# AI Action Design — learnings from the first build

| | |
|---|---|
| **Status** | Learnings. Not a standard, and not to be measured against. |
| **Covers** | What an application declares to a model, what the model may know, how a call is run and answered, and what a person sees. |
| **Drawn from** | The Action Catalog and the capability model editor, built and run in dev during October 2026. |

Every rule below cost something to learn. Each one states what to do, and then the failure that
produced it, because a rule without its failure is one a reader talks themselves out of.

---

## 1. What a model may know

**A model knows three things: what a read gave it, the context the product supplied, and the
actions it may call. A record's id is none of them.**

An id is the store's identity for a record and the service's. It reaches a model only when a
binding passes its arguments through without looking at them.

An action therefore takes a **name**, and the code behind it resolves the name to an id before it
calls anything. A read returns names and shape, never ids.

> A model added seven capabilities and reported them to the person as a table of eight-character
> handles — `36e6702b`, `1a9ab12c` — under the heading "Draft id". The person could do nothing
> with any of them. The model had not invented them: the action returned them, so it passed them
> on.

Resolving a name needs three decisions, and each has a right answer:

1. **Case and surrounding space are ignored.** A model repeating a name from an earlier reply is
   repeating what it read, and a difference of case is not a different record.
2. **Where versions share a name, the newest that is not retired is the one meant.** That is what
   a person means when they say it.
3. **A name that reaches nothing comes back as a sentence naming what was asked for and what
   there is.** The model corrects itself from that. "Not found" produces a model that gives up or
   repeats itself.

---

## 2. The declaration and the binding are two things

**What an action *is* and what an action *does* are separate, and joined only by the name a model
calls it.**

The **declaration** is published: the three names, what it does, what it accepts, its effect
class. The **binding** holds `run` and never leaves the browser, because execution is the
application's and nothing outside the deployed code should be able to invoke it.

The join is `nameForModel`, which means the two can disagree, which means the release must check
both directions:

- a declaration with no binding reaches a model as something it can call and nothing can run, and
  the model discovers it mid-conversation;
- a binding nothing publishes is code that never runs, and reads equally as something forgotten
  or something withdrawn.

> Both checks were described in a comment before either existed. The comment said the release
> "catches a mismatch before it ships"; nothing did, because there was no registry to check
> against.

---

## 3. A schema says what a field means, never how it behaves

**Describe the outcome. A description that explains a mechanic hands a model a sentence, and the
model says it to the person.**

| Instead of | Write |
|---|---|
| "Replaces the labels whole" | "Every label it should end with. One not listed is gone" |
| "Omit to clear the placement and let it flow" | "Where it should sit; without one it flows with its siblings" |
| "Can be used to replace all tags, or to add one by reading, adding and putting" | "Every tag it should end with" |

> Told that tags "replace the labels whole", a model answered a person with: *"the tags field
> always replaces the whole list — there's no append option, so to add `hi` while keeping
> `nutanix` I have to send both."* Accurate, and no use to anyone.

Three forms to avoid, each for its own reason:

1. **Mechanics**, because the model recites them.
2. **Permission language** — "can be used to… or to…" — because a model given options reports
   which one it chose.
3. **Procedures** — "read, then add, then put" — because a recipe is the most quotable form of a
   mechanic.

The outcome phrasing loses nothing: a model that wants to add one item to a replaced set works
out that it must send the others.

---

## 4. The product names what ran; the model does not

**Every declaration carries a name a person reads, and the application renders it. Nothing asks a
model to name what it did.**

Three names, none derivable from another:

| Name | Read by | Example |
|---|---|---|
| `nameForModel` | the model, and the binding | `put_draft_capabilities` |
| `displayName` | the person | Change a capability |
| `sayToUse` | the person, to learn how to ask | "rename this capability" |

The transcript resolves a call to its `displayName` through the catalog — the same catalog the
actions panel reads — so the two cannot drift. `displayName` is required, so there is nothing to
fall back to: a name that does not resolve is a defect and says so where a developer sees it,
rather than being dressed as a label.

> The transcript wrote the name onto the message when the result was posted. The next reconcile
> replaced the message with the record, which carries a call's id and nothing else, and every line
> read "Action · done". Deriving it from the catalog on every render survives the reconcile and a
> page reload both.

---

## 5. Offer only what can actually happen

**An action is offered when three things hold: the person's reach setting allows it, this build
has a binding for it, and that binding says it is usable right now.**

Usability is the question nothing published can answer — an editor is still loading, nothing is
selected, nothing has changed to save — so it is asked at the moment of offering.

A model offered something it cannot run calls it and gets an error, which costs a turn and
teaches it nothing.

**Nothing is hidden.** The panel shows every action with its standing and why: reach is the
person's own setting and they should see what it cost them; usability is the state of the screen
and is not theirs to reconsider.

---

## 6. An experience must be mounted, or its actions stand nowhere

**Reach is the relationship between an action and the experience a person is standing in. An
experience nothing mounts is never open, so every action it publishes stands nowhere.**

The failure is silent and total: the catalog holds the actions, the release ships them, and the
panel is empty on the very screen they were written for. It reads as a missing feature.

Two checks, and only together:

1. every mounted experience key resolves to a declaration;
2. **every declared experience is mounted somewhere.**

The first alone passes trivially when nothing is mounted at all, which is exactly the state that
shipped.

> And where an application carries more than one route table — one rendered by the build, one
> mirroring it — "mounted somewhere" is not enough. Mounting in the table nobody serves passes a
> check and changes nothing on screen.

---

## 7. Nothing in the run path throws

**Every outcome of a call is a string the model reads, because every outcome is something it can
act on.**

| Outcome | What the model is told |
|---|---|
| It ran | the state after it, in a sentence |
| Arguments did not parse | that they were not valid JSON |
| Arguments were refused | each issue, by path, so the call can be corrected |
| The action is not usable | that it is not available, and nothing more |
| The run failed | what failed |

A thrown error leaves the call unanswered, and a model with an unanswered call is one the service
will not resume. The person is then looking at a conversation that has stopped for no stated
reason.

The "not available" message stays short on purpose. The actions available are sent with every
turn, so the model already holds the current list, and the next turn carries that list without
the action that failed.

---

## 8. Approval is a turn of its own

**A reply that asks for actions is settled after the whole reply has arrived, not as each call
lands.**

The person sees every call at once rather than each interrupting the next, and the decisions are
theirs as a set — whether a subset still makes sense is their judgment to make.

1. The reply finishes. Every call it made is in hand.
2. What runs unattended runs.
3. What needs approval is stacked in the order the model asked, and decided one at a time.
4. Nothing is posted until the last is decided.
5. Every result is posted together.

Step 4 is not a preference. **A provider requires every result for one model turn in the single
message that follows it.** Posting one early leaves the rest outstanding and the model unresumed.

Three answers, not two: **allow**, **refuse** — one standard sentence, the same for every action
— and **say something instead**, which is an answer in the person's own words that the model
reads in place of a result. Writing instead is not a refusal to answer.

Record what the gate did, not what the person's setting was: approved, refused, asked about
automatically, or not asked because governance was off. The setting is a different thing and
belongs nowhere on the wire.

---

## 9. The transcript shows what ran, once

**The calls are the model asking. A person's line is what happened.**

Render the results, grouped: one line per turn, naming the first and counting the rest, with every
one of them in a tooltip. Do not render the calls at all.

> A model asked for ten actions. Each call rendered as its own collapsible row showing its
> arguments as JSON, so the person had ten rows of JSON above one correct line. The arguments are
> the model's business; a person opening one is reading JSON to find out what happened.

---

## 10. Publish a selection, not an export

**Which of an editor's operations become actions is a decision, made per experience, and written
down with its reason.**

The capability model editor has eleven operations and publishes five. The six that are not
published are not an oversight:

- **the lifecycle, the next version and delete** are decisions about a record every other screen
  in the organization draws from, rather than edits to a draft;
- **revert and the dismissals** undo or acknowledge, and a model has nothing to undo that it did
  not just do itself, and nothing to acknowledge.

List the set by hand. A directory scan makes the set depend on what happens to be on disk, and an
action reaching a model because a file was added is the opposite of a selection.

---

## 11. An editor over a set treats membership as a change

**Where an editor edits a collection on one screen, adding and removing are changes like any
other, and Save commits them with the field edits.**

Almost every editor edits one record: it is created once, by the act of opening it, and
everything after is field edits that wait for Save. An editor over a set is different in kind,
because creation and deletion happen repeatedly inside a session — and that is the only place
this question arises.

> A model added eleven capabilities in one turn. Each committed the moment the action was called,
> because a create needs the service's answer. The person pressed **Discard**, left, came back,
> and all eleven were there. The dialog had offered to discard the field edits, which was all it
> could reach.

Where a set editor holds additions until Save:

1. An addition takes an id the editor mints and holds until Save.
2. Save creates the additions **parents before children**, because a child names its parent by an
   id that does not exist yet.
3. Each real id, as it arrives, replaces the held one everywhere — another addition's parent, and
   any change that re-parented an existing record under a new one.
4. The field changes are sent after.
5. Discard drops all of it.

Call the control **Save All** where it commits a set. "Save" invites the reading that it saves
the record in front of you.

The cost is real and worth stating: a name collision is reported at Save rather than when it was
typed, and anything referring to a new member holds a temporary id until then. The gain is that
Save means one thing, Discard means discard, and a model's batch is reviewable before any of it
exists.

---

## 12. Whatever you give a model, it passes on

This is the one sentence behind section 1, section 3 and half of section 4. A model does not
distinguish what it was told in order to act from what is worth telling a person. It relays ids
it was handed, mechanics it was taught and options it was offered.

So the discipline is at the boundary, in what an action accepts, what a read returns and what a
result says — not in asking the model to use judgment about which of the things we gave it are
fit to repeat.
