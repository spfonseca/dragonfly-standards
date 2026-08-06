# Web Asset Delivery Standard

| Field | Value |
|---|---|
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-08-06 |

## Purpose

This standard governs how a product's **static web assets** — the SPA shell, its bundles, and its
public content — are cached and routed at the edge. The RESTful API Design Standard §17 covers
caching of **API responses**; nothing covered it for static delivery, and the two failure modes
below both reached a deployed environment as a result.

## Scope

Applies to every product serving a browser application through a CDN in front of object storage
(GCP Cloud CDN over a backend bucket, in practice), and to the deploy tooling that writes those
objects. Any requirement may be waived only through an explicit, documented, approved waiver
recorded in the product's implementation guidance.

---

## 1. Cache Lifetimes

### 1.1 Cache each content class on its own policy, never one blanket TTL.

[REQUIRED] The bootstrap HTML, content-hashed bundles, and public content shall each carry their
own cache policy. A single CDN-wide TTL applied across content classes shall not be used.
*Rationale:* The shell and the bundles it references have opposite requirements — one must be
re-read to discover the other. One TTL cannot satisfy both, and the class that loses is always the
shell.

### 1.2 Serve bootstrap HTML as revalidate-always.

[REQUIRED] HTML that references content-hashed assets shall be served `Cache-Control: no-cache`
(or `no-store` where no revalidation benefit is wanted). It shall not carry a positive `max-age`
in either the shared or the browser cache. *Rationale:* A browser holding a stale shell requests
bundle filenames that no longer exist, producing a white screen no cache invalidation can reach —
the copy is on the user's machine.

### 1.3 Serve content-hashed assets as immutable.

[REQUIRED] Assets whose filenames contain a content hash shall be served
`Cache-Control: public, max-age=31536000, immutable`. *Rationale:* The hash *is* the cache key; a
new build produces a new filename, so the old one can never need revalidating.

### 1.4 Let the object's own headers govern CDN behavior.

[REQUIRED] The CDN shall be configured to honor origin cache headers rather than apply its own
heuristics or a default TTL to unlabeled objects. *Rationale:* Cacheability belongs to the
artifact, set once by the tooling that produced it, not to edge configuration in a separate repo
that drifts from it.

### 1.5 Stamp cache metadata before switching the CDN to origin-header mode.

[REQUIRED] Deploy tooling shall write `Cache-Control` on every object **before** the CDN is
switched to honor origin headers. *Rationale:* An origin-header-driven CDN will not cache an
object that carries no cache header at all; flipping the mode first silently stops all caching and
sends every request to the bucket.

---

## 2. Deep-Link Routing

### 2.1 Route client-side paths with a rewrite or a real object, never an error-code override.

[REQUIRED] Serving the SPA shell for a client-side route shall be implemented as a routing rewrite
or as a real stored object at that path. It shall **not** be implemented by matching the origin's
4xx and overriding the response code. *Rationale:* An error-override mechanism relabels whatever
the origin returned, including responses whose body is legitimately empty — see §2.3. A rewrite
serves the shell as an ordinary response with ordinary caching and validation semantics.

### 2.2 Give known routes real objects.

[RECOMMENDED] Where the route list is known at build time, deploy tooling should write a shell (or
prerendered) object for every known route, leaving any fallback to serve genuinely unknown paths
only. *Rationale:* Normal navigation then never depends on fallback behavior at all, and an
unknown path gets the 404 it deserves rather than a 200 carrying the shell.

### 2.3 Never convert a 304 into a 200.

[REQUIRED] No edge rule shall apply a response-code override to a `304 Not Modified`. A fallback
that re-fetches a shell object shall not forward the client's `If-None-Match` /
`If-Modified-Since` to that fetch unless it also forwards the resulting 304 unchanged.
*Rationale:* Found in `dev` 2026-08-06 and reproducible in one request. A returning visitor's
conditional deep link caused the origin to answer `304` with an empty body for the shell; the
error-override rule relabeled it `200`; the CDN cached a `200` with `Content-Length: 0` and served
a blank page to everyone until invalidated — and re-poisoned itself on every subsequent
revalidation, because the stored ETag kept matching:

```
curl -H 'If-None-Match: "<shell etag>"' https://app.<domain>/<any-client-side-route>
  → HTTP 200, Content-Length: 0        # unconditional request → 200, full shell
```

Negative-caching policy does not mitigate this: the cached entry is a `200`, not an error.

---

## 3. Verification

### 3.1 Assert a non-empty document, not a 200.

[REQUIRED] Post-deploy verification shall assert that representative routes return a document of
plausible size. A status-code check shall not be accepted as evidence of a served page.
*Rationale:* Both defects in §2.3 and §1.2 present as `HTTP 200`. A green status check is exactly
what let them ship.

### 3.2 Include a conditional request in that verification.

[REQUIRED] Verification shall include at least one request carrying `If-None-Match` for the shell,
against a client-side route. *Rationale:* This is the single cheapest reproduction of §2.3, and an
unconditional check passes while the defect is live.

### 3.3 Verify cache policy by reading it back from the live edge.

[REQUIRED] After changing CDN cache configuration, the effective policy shall be read back from
the deployed resource rather than inferred from a successful apply. *Rationale:* Cache
configuration fields have been observed to apply successfully and not persist; and a policy that
was applied correctly may still target the wrong layer, which reads identically in a plan.
