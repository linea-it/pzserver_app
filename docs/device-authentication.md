# Device authorization

PzServer maintains guarded subclasses of Django OAuth Toolkit 3.4.1 in
`backend/core/views/device_oauth.py`. Toolkit files are not patched. The normal
backend requirements pin this version and oauthlib 4.0.1. Device authorization
is part of the regular backend routes; the public client still must be registered
explicitly and no user authorization is created automatically.

## Deployment configuration

Build the backend image from this source. For local testing, set in the backend environment:

```text
URI=http://localhost
```

Set `DJANGO_OAUTH_CLIENT_ID` in the backend to the same client ID used by the
frontend. `PZSERVER_WEB_CLIENT_ID` may explicitly override it. The session-to-OAuth
bridge fails closed if unset and rejects all other applications, including Device
clients. No client secret is needed for Device Flow.

Preserve the existing database, SATOSA metadata, SAML certificates, trusted
origins and host settings. No new JupyterHub registration is needed. Before
serving the updated backend, run inside its container:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py register_device_client
```

The idempotent registration command creates the public client
`pzserver-python-device`, with explicit user approval required. It refuses to
modify an existing incompatible client. There is no client secret to distribute.
The toolkit includes new database migrations; apply them before using the flow.
The older experimental client ID ending in `-poc` is not used.

## Real login smoke test

1. POST a form (`application/x-www-form-urlencoded`) to
   `/api/device-oauth/device-authorization/` with
   `client_id=pzserver-python-device` and `scope=read write`.
2. Keep `device_code` private. Display only `verification_uri` and `user_code`.
3. Open the verification URI. Without a session it should redirect through the
   existing `/saml2/login/` flow and return to the device page. Enter the code,
   review the application and scopes, then approve or deny.
4. Poll `/api/device-oauth/token/` with `client_id`, `device_code` and
   `grant_type=urn:ietf:params:oauth:grant-type:device_code`. Respect `interval`;
   increase it by five seconds on every `slow_down`. Stop on denial or expiry.
5. Use the returned access token as `Authorization: Bearer ...` to call a
   protected PzServer endpoint. Check access is limited by the user's existing
   permissions. No Hub token is involved.
6. Refresh through the same token endpoint (`grant_type=refresh_token`,
   `client_id`, `refresh_token`). Revoke credentials at
   `/api/device-oauth/revoke_token/`. Do not print/store token responses in logs.

Device clients use an access token of one hour and a rotating refresh token
valid for 30 days from its issuance. Each successful refresh issues a new refresh
token and restarts that 30-day window (an inactivity policy, not an absolute
30-day session limit). Existing web clients keep their current lifetimes.
Configure device lifetimes through `PZSERVER_DEVICE_ACCESS_TOKEN_SECONDS`
(default 3600) and `PZSERVER_DEVICE_REFRESH_TOKEN_SECONDS` (default 2592000).
The short authorization-code deadline is unchanged. Tokens already issued keep
their access-token expiry; the refresh policy is checked at redemption.
This change does not add new read/write scope restrictions to existing API views.
Successful redemption deletes the temporary grant, so its old browser status
URL can subsequently return 404. A dedicated final confirmation UX remains work
for the client-facing rollout. The Python package now provides `login_device(host="localhost")`, persistent
credentials and automatic renewal. Connected applications can be renamed and revoked from the user menu.

## Maintained protections and compatibility

- Row locks and a transaction serialize redemption on PostgreSQL; token issuance
  and deletion of the single-use code commit together. Failure rolls both back.
- Expired codes cannot be redeemed or approved; inactive users cannot redeem.
- Polling state is shared in the database. Early polling increases the interval.
- Codes are bound to the initiating public client. Browser approval requires a
  session and CSRF. User-code association is rechecked under a row lock.
- The old `/api/auth/token` endpoint (with or without a trailing slash) always
  rejects device grants. Device refreshes use the maintained lifetime validator
  and web clients retain their existing policy.
- The social conversion endpoint rejects Device clients; they must use approval.
- The dedicated token endpoint accepts only Device issuance and Device refresh.
  Existing SATOSA, manual token and JupyterHub authentication are retained.

Changes to the pinned toolkit must rerun these regressions before release. Do
not remove a local guard solely because the library advertises Device Flow.
The Django-session flow, Python package, token renewal and revocation were
validated on pzserver-dev. A deployment using the real SATOSA redirect must still
be validated before production rollout.

## Validation and CI

The full backend suite passed in an isolated backend container with DOT 3.4.1
and oauthlib 4.0.1: **258 passed and 5 skipped** on SQLite. The combined Device
Flow and session-bridge suites passed **32 tests with 5 PostgreSQL-only tests
skipped**. CI runs the focused Device Flow suite again on PostgreSQL to cover row
locks, simultaneous redemption, rate-limit serialization and
refresh/revocation races. Live SATOSA login remains pending.

CI runs the normal suite on SQLite and Device Flow tests again on PostgreSQL.
To run the latter locally against a disposable PostgreSQL instance:

```bash
PZSERVER_TEST_POSTGRES_HOST=127.0.0.1 \
PZSERVER_TEST_POSTGRES_PORT=5432 \
PZSERVER_TEST_POSTGRES_USER=postgres \
PZSERVER_TEST_POSTGRES_PASSWORD='<test database password>' \
pytest core/test/test_device_flow.py -q
```

Run from `backend/`. The database account must be able to create a test database;
these settings belong to `pzserver.test_settings`, not deployment settings.


## Authorization pages

The device-code form, consent screen and result use project-owned templates in
`core/templates/pzserver/device/`. They retain server-side validation and CSRF,
show the signed-in account and requested permissions, and support narrow screens,
keyboard focus and the frontend's saved dark-mode preference. The charcoal header
and footer, gray background, Material-style controls and Roboto/Oxanium fonts
follow the existing frontend. Fonts use the same Google Fonts provider as the
frontend, with local fallbacks; logos use the frontend's existing public assets.
Templates are only assigned to the Device Flow views.


## Web session compatibility with Toolkit 3.4.1

The session-to-OAuth bridge stores the explicit `.token` fields in cookies,
not the token models' display strings, and persists the refresh token before
returning it. The frontend discards malformed legacy cookies containing
whitespace and retries the bridge through the existing Django session. OAuth
cores for guarded views are cached per concrete view class so a core initialized
by the legacy parent cannot bypass the device-specific lifetime validator.
Regression tests cover cookies, logged-user lookup, refresh and cache isolation.


## Python package local validation

Install the sibling package checkout in the active notebook kernel and restart it:

```python
%pip install -e /home/singulani/projects/pzserver
```

Then, in a new cell:

```python
from pzserver import login_device, PzServer
login_device(host="localhost", open_browser=False)
pz = PzServer(host="localhost")
```

Open the displayed URL, log in through the local Django admin if no SAML
registration exists, then return to the device URL, enter the code and approve.
Later processes only need `PzServer(host="localhost")`. Use the same API origin
in the browser and the package. HTTP is permitted only for loopback development.
The package stores credentials privately by endpoint, refreshes before expiry,
and locks refresh across processes. `logout` removes local credentials without
server revocation. Legacy tokens and Hub authentication are unchanged.

Validation also exercised the real HTTP flow against a disposable local Django
server and separate database: admin session, CSRF consent, package login, two
instances, refresh rotation and revocation. No real SATOSA login was used in that
automated test. The Python package suite passed **141 tests** after rebasing the
implementation onto the current main branch.


## Connected applications

The user menu links to `/connected_applications`. The page uses the existing
Material UI theme, header/footer, cards, buttons and dialogs; no global CSS is
added. It lists only the signed-in user's Device authorizations, including date,
last renewal, status and an editable display name. Names are labels, not verified
environment identities. A confirmation dialog is required before revocation.

`GET /api/device-access/` returns metadata only. `PATCH` and `DELETE` on
`/api/device-access/<uuid>/` rename or revoke an individual authorization.
Management requires the configured web OAuth client or a Django session (with
CSRF for mutations). Device, manual and partner credentials cannot manage these
records. Other users' records return 404.

A durable `DeviceAccess` record tracks the toolkit token family, rather than a
single refresh token. Rotation locks that record inside the toolkit transaction;
revocation uses the same lock, marks it revoked, revokes the family's refresh
tokens and deletes its access tokens. Rotation cannot restore an access revoked
concurrently. Requests authenticated before revocation may finish. Other Device
connections, web login and manual/Hub tokens are unchanged.

Apply migrations 0066 and 0067 before serving the updated code. Existing Device
families are imported so they can also be managed; web credentials are excluded.
Local `pzserver.logout()` only forgets local credentials; server revocation is
performed from this page.


## Pending requests, code attempts and rate limits

Apply migration `0068_device_authorization_limits` before serving this version;
rebuild the backend image and update the Python package together. The local
containers were stopped during this change and were not started or migrated.

- Code lifetime: **900 seconds (15 minutes)**, configurable through
  `PZSERVER_DEVICE_CODE_SECONDS`. The database expiry and `expires_in` response
  agree; resuming locally never extends the original deadline.
- The verification URI contains an opaque request identifier. It does not contain
  the private `device_code` or prefill the user code. The complete link must be
  used; the old bare `/device/` form cannot bypass the per-request guard.
- The configurable `PZSERVER_DEVICE_MAX_CODE_ERRORS` policy defaults to **3**
  incorrect user-code submissions before blocking that request (DENIED). The
  authorization response advertises the same value to the Python package.
  Counters are in the database, not browser cookies, and share the same grant lock
  as issuance/cancellation/approval. Switching browsers does not reset attempts.
  A code from another pending request counts as incorrect. Failed CSRF checks and
  background polling do not consume these three attempts. Password failures are
  handled separately by the existing login provider.
- Python saves pending state in a private file and serializes local login calls.
  Interrupting and rerunning reuses the same code and persisted polling interval.
  `login_device(force=True)` calls `/api/device-oauth/cancel/` with the private
  device code before replacing an unredeemed request. Cancelling a request does
  not revoke previously issued access tokens or another environment's request.

The application-level limit is deliberately bound to the authenticated user,
not to an IP address. In this infrastructure Django may observe the reverse
proxy address instead of the original client address, which would incorrectly
put unrelated users in the same bucket.

| Action | Scope | Default | Setting |
|---|---|---|---|
| Code entry | Authenticated user | 30/minute | `PZSERVER_DEVICE_VERIFY_PER_MINUTE` |

Exceeding the user limit returns HTTP 429 with `Retry-After`. Valid polling uses
each grant's interval (5 seconds by default); an early request returns `slow_down`
and adds 5 seconds. Volume protection for anonymous code issuance, unknown-code
polling and cancellation belongs at the trusted reverse proxy or ingress, where
the original client address is available. No per-client global issuance lock is
used because the public client ID is shared by all Python users.

Schedule `python manage.py prune_device_authorizations` daily to remove expired
temporary grants and rate counters older than one day. It does not delete saved
DeviceAccess history or active OAuth credentials.

Counter retention defaults to 86400 seconds and is configurable through
`PZSERVER_DEVICE_RATE_LIMIT_RETENTION_SECONDS`. All Device duration and limit
environment variables must be strictly positive integers; invalid values stop
Django during startup instead of silently weakening or disabling a policy.
