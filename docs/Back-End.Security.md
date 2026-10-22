# Backend security and operations

## Upload and inference contract

- Public `POST /predict` accepts exactly one `image` multipart field. Public
  `POST /training` also requires exactly one allow-listed `label`: `match_ready`
  or `not_match_ready`. The frontend deliberately submits public camera JPEGs;
  no admin secret or sign-in has been added to browser code.
- Image bytes: at most 5 MiB; label bytes: at most 15; entire parsed multipart
  envelope: at most 5 MiB + 64 KiB. Duplicate/unknown fields are rejected.
- Only single-frame JPEG and PNG content is accepted, regardless of filename
  or MIME declaration. Both dimensions must be 1–4096 inclusive and their product
  at most 12,000,000 pixels. Limits are checked before pixel decoding. BMP, GIF,
  TIFF, WebP, animation, corrupt/truncated and oversized images are rejected.
- Two requests may upload/process at once across all HTTP workers. Uploads
  have a 15-second deadline, image validation 10 seconds, inference 60 seconds.
  Only one inference subprocess runs at a time; overload fails fast with 503.
  Timed-out children are killed and reaped before releasing capacity. A client
  disconnect cannot release capacity while its child continues running.
- Private random temporary directories include subprocess caches and are removed
  on completion/error/timeout. Predictions use the original validated pixels;
  preprocessing and the three-model ensemble remain unchanged. Models still load
  once per bounded subprocess: isolation is preferred over a persistent worker in
  this change. CPU threads are limited, but cold-start latency remains.
- Client errors contain no Python stderr, internal paths or exceptions. Bounded
  diagnostics go to stderr via the service logger, not an unbounded local file.

## Contribution review, quotas and retention (operator action required)

Accepted contributions return HTTP 200 as before, with `status: success` and
`review_status: pending`. They are **not trusted training data**. Images are
re-encoded as clean RGB JPEGs without metadata or trailing data, then saved under
`TRAINING_PENDING_DIR/{match_ready,not_match_ready}` (default
`backend/training_data/pending`, relative to the backend working directory).
Client labels are suggestions, not ground truth. No code auto-promotes them.

The entire pending collection is limited to 500 files and 256 MiB. At capacity,
new submissions get 503; existing unreviewed contributions are not evicted to
make room for an attacker. Files at least seven days old are removed on startup,
before each submission, and hourly while the service runs. Deletion can lag by
one cleanup interval and is not secure erasure from backups. No append-only
submission log is retained. Run **one API instance per pending directory**;
in-process serialization is not a distributed quota lock.

Review pending images within seven days. Check content, label correctness,
duplicates, provenance/consent and dataset balance before copying selected images
to a separately managed training dataset. Reject/delete unwanted files; never
bulk-import pending labels into `nn-classifier/dataset`. Keep approved data and
models outside the pending tree; their retention/backup policy is operator-owned.
Existing `training_data/{label}` and legacy logs are not automatically migrated
or deleted: back them up privately, review or delete them separately. They remain
untrusted. Export existing container-local data **before** recreating a live
container; otherwise it may be lost. No live migration is performed by this PR.

## Deployment isolation and persistence

`backend/compose.yaml` and `backend/Dockerfile` are a new opt-in deployment recipe,
not a change to the live deployment. From `backend`, prepare TLS certificate/key
files in `certs/` readable by UID/GID 10001 (key permissions 0400, owner 10001),
then, only when deployment is approved, build/start with `docker compose up -d --build`.
Keep private keys out of Git. The service uses:

- Non-root UID/GID 10001, read-only root filesystem, no Linux capabilities,
  no-new-privileges, an init process for child reaping.
- 2 GiB memory/no extra swap, 64 PIDs, two CPUs, and a 128 MiB noexec tmpfs.
- A named `contributions` volume at `/data`, initialized with UID/GID 10001
  ownership. Pending images survive container recreation. Do not use
  `docker compose down -v` unless deliberately destroying retained contributions.
  Back up privately; backups require their own retention policy and disk quota.
- TLS on port 49161, published only to the host loopback interface for a tunnel
  or reverse proxy; rotated Docker logs (3 × 10 MiB).

Check limits and healthy real predictions on the target hardware before adopting
the recipe. ARM64/Pi installation and load testing must be verified separately.
The systemd installer now builds sources (Rust + OpenSSL development headers are
required), uses Python >=3.11 and adds filesystem, privilege, memory, task and CPU
restrictions. The stale ARM64 prebuilt binary has been removed; do not reuse it.
The installer starts a service, so running it is a deployment action.

The backend directly owns Actix configuration rather than changing/publishing
the shared `rusty-api` package. TLS is enabled by default using
`cricket-ready.crt` and `cricket-ready.key` in the backend working directory.
`PYTHON_EXECUTABLE` defaults to `nn-classifier/venv/bin/python3`; the container sets
it to `python3`. `HTTP_LOOPBACK=1` is an explicit HTTP-only loopback mode for local
tests or a co-located TLS-terminating proxy; do not use it with Docker port
publishing (loopback inside a container is not its external interface).

Only HTTP/1.1 is enabled upstream; unused HTTP/2/compression/cookie features are
disabled to remove the vulnerable `h2` 0.3 dependency (RUSTSEC-2026-0258).
Browsers and the public edge may still use HTTP/2 to the edge, with HTTP/1.1 from
the proxy to this backend. Verify the tunnel/proxy's origin protocol before rollout.

## Website compatibility and residual abuse risk

Default CORS origins are `https://alexheffernan.dev` (the actual Pages site origin)
and `https://alexanderheffernan.github.io`; `ALLOWED_ORIGINS` can replace the
comma-separated list for another deployment. POST and the frontend's
`ngrok-skip-browser-warning` preflight header are allowed. CORS is not authentication.
Peer-IP rate limiting retains burst 20, replenishing one request per 3 seconds;
expired limiter entries are pruned each minute. Forwarded headers are not trusted.
Behind a tunnel, users may share the proxy peer's bucket. Configure per-client
rate limiting at the trusted edge; do not enable arbitrary forwarded-IP trust.

An anonymous attacker can still occupy capacity or fill quarantine until review
or expiry. Byte/pixel/time/concurrency/storage limits bound impact and quarantine
prevents automatic poisoning, but do not guarantee availability or trustworthy
labels. Monitor 429/503/504 and disk usage. Models, scripts, certificates and
operator-selected Python executable are trusted, read-only deployment inputs.

## Dependencies and verification

Pillow 13.0.0 is the fixed release for the reachable BMP RLE amplification advisory
[GHSA-24rc-8hj2-v98c](https://osv.dev/vulnerability/GHSA-24rc-8hj2-v98c).
[PyPI](https://pypi.org/project/pillow/13.0.0/) requires Python >=3.11. Decoder
restriction independently excludes BMP. The refreshed, tested inference pair is
torch 2.14.1 / torchvision 0.29.1 with numpy 2.4.2; model loading explicitly uses
`weights_only=True`. This path does not save TIFF or call `torch.jit.load`; those
unrelated advisories are not claimed reachable. Runtime requirements are split
from training-only scikit-learn dependencies.

Run from `backend` after installing `nn-classifier/requirements-inference.txt`:

```sh
cargo fmt --check
cargo clippy --all-targets --locked -- -D warnings
cargo build --locked
python tests/security.py
cargo audit
pip-audit
pip-audit --no-deps --disable-pip -r nn-classifier/requirements-inference.txt
docker compose config --quiet
```

The HTTP suite uses temporary data, loopback only, a 2 GiB address-space limit,
real validation/model inference, and controlled failure/sleep subprocesses. It
covers accepted/rejected uploads, exact byte/dimension/pixel boundaries, both
labels, unsupported formats, animation, storage quotas/expiry, restart persistence,
safe failures, deadlines, child cleanup, overload, CORS and rate limiting. Do not
send adversarial test inputs to production.

Audit both the installed dependency environment and the pinned release requirements:
PyPI-based auditors may skip the `+cpu` wheel versions. The release audit checks
their upstream version numbers explicitly. The production 2.10.0 release had
pt2-loader and `torch.jit.script` advisories outside this image-inference path;
they are not presented as remote image-upload vulnerabilities. The refreshed pair
also removes those version findings, and was tested with the existing model files.

Frontend lockfile refresh and reviewed overrides reduce the prior npm audit from
4 critical/85 high/18 moderate/6 low to 0 critical/52 high/6 moderate/3 low
(2026-10-22). `npm audit --omit=dev` has zero findings. Remaining Vue CLI/Jest/
webpack development-tool chains include braces, node-forge, dev-server and older
transitive tooling; no blind major upgrades or `audit fix --force` were used.
Keep development servers private and build only trusted source. Full elimination
needs a separate, tested build-tool migration. PostCSS, selector-parser,
serialize-javascript and cross-spawn overrides were verified by production build
and lint. Vue Router stays on its previous 4.5 line for TypeScript 4.5 compatibility.
CI uses Node 24, rather than the previous end-of-life Node 21.
