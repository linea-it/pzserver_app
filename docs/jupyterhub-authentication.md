# Partner JupyterHub authentication

The API accepts `Authorization: JupyterHub <public-hub-url> <hub-token>`.
Existing Token, OAuth and session authentication remain available. The database
is the only source of trusted partners; there is no environment configuration
fallback and no attempts against unrelated Hubs.

## Deployment and optional migration from JSON

1. Deploy this backend version and run `python manage.py migrate` before serving
   Hub-authenticated requests. Migration `0063_trustedjupyterhub` creates the table.
2. If partners were configured with `JUPYTERHUB_PARTNERS_JSON`, pass that variable
   to a one-off `python manage.py import_jupyterhubs` command. Keys must be public
   HTTPS URLs (old arbitrary IDs must be converted first). This is transactional:
   invalid data rolls back the import. Repeating it skips existing canonical URLs
   without overwriting administrative edits. No tokens are imported or stored.
3. Remove the legacy variable from the runtime environment after import. Changing
   it no longer affects authentication.

The migration does not enable or create any partner automatically. The import
preserves the old `enabled` flag for new records; records created in Admin start
with it unchecked.

## Registering a partner in Django Admin

Open **Core → Trusted JupyterHubs → Add** and fill in:

- Name: e.g. `LIneA Development`.
- Public URL: `https://jupyter-dev.linea.org.br`.
- Aliases: a JSON list, e.g. `["https://jupyter-dev.linea.org.br/hub"]`, or `[]`.
- User URL: `https://jupyter-dev.linea.org.br/hub/api/user`.
- Enabled: check only after confirming connectivity and username ownership.

Only grant the model's view/add/change permissions to trusted integration
administrators with staff access. Registering a partner grants trust in its
identity namespace. Admin changes use Django's normal audit log. Deletion is
not exposed in Admin; disable a partner to preserve its record instead.

Public URLs and aliases are normalized and validated at save. Conflicts with
other partners (even disabled ones) and duplicate aliases are rejected. Both
client and server lowercase the hostname, remove port 443 and trailing slashes,
and preserve case-sensitive path prefixes and nondefault ports. Userinfo,
queries, fragments, whitespace, percent-encoded paths and dot segments are
rejected. The validation endpoint must be HTTPS; its exact path is preserved.

The package reads `JUPYTERHUB_PUBLIC_HUB_URL`, or `JUPYTERHUB_HOST` when the first
is empty. Register aliases matching the actual environment values. Never use
one alias for two installations. No package-side partner mapping is necessary.

## Validation flow and deactivation

Use `PzServer(host="pz-dev")` in the notebook with an updated package and no
explicit/saved PzServer token taking precedence. The client sends the public
Hub URL and the environment token only to a trusted PzServer destination.

The API resolves the URL to a single database record on each request and checks
`enabled` before contacting its fixed endpoint. It does not follow redirects.
The returned identity must be a user whose username exactly matches an active
local account, including case. Accounts are never automatically created. Hub
admin flags and groups do not grant local privileges. Only local permissions
apply. Unknown/disabled partners or invalid credentials are rejected; upstream
failures return 503. Ambiguous records also fail closed without contacting Hubs.

Unchecking Enabled takes effect on subsequent authentication checks without a
restart or cache expiry. A request already being processed may finish. Local
Token/OAuth access remains available. Deactivating a local user blocks that
user's Hub authentication as well.

Partner tokens also grant Hub permissions. Never print them or record
Authorization headers in application, proxy or monitoring logs. The partner
must guarantee matching usernames identify the same people in both systems.
Rubin/Nublado requires a separately supported integration.


## Individual user authorization

Run `python manage.py migrate` to apply migration `0064_jupyterhubconsent`.
No existing user is automatically authorized. After a normal PzServer login,
open the user menu → **JupyterHub access** (`/hub_access`). Review the partner
name and URL, choose **Authorize access**, and confirm. Use **Revoke access**
to block subsequent Hub-authenticated requests. Personal PzServer tokens and
operations already in progress are not revoked by this action.

The API requires both an enabled partner and explicit consent for the local
user/Hub pair. Missing authorization returns `hub_consent_required` internally
and a message directing notebook users to `/hub_access`. Existing local product
permissions continue to apply. There is no automatic fallback or account creation.

`GET /api/hub-access/` lists partners and the current user's consent.
`PUT /api/hub-access/<id>/` accepts `{ "enabled": true, "signature": "..." }`
(the signature comes from the GET response); revoke with `{ "enabled": false }`.
Only the current authenticated user can be modified. Management accepts normal
PzServer OAuth or a Django session with CSRF protection. Hub credentials and
personal API tokens are rejected. The session-to-OAuth bridge now accepts Django
sessions only, preventing a Hub credential from minting an OAuth token through it.

Changes to a partner's public URL, aliases or validation endpoint revoke existing
consents on save, including when reverting a change later. Users must reload the
page and explicitly authorize again. A stale confirmation is rejected. Changing
only the display name does not revoke consent. Disabling a partner blocks access;
re-enabling it with the same identity preserves individual authorizations.


## Hub validation cache

Apply migration `0065_jupyterhub_validation_cache` before serving requests.
Successful Hub authentications are cached for 300 seconds (five minutes) in a
shared database cache, so all API workers can reuse the validated username.
The cache stores only that username under an HMAC-derived key scoped to the
Hub, its configuration and the token. It does not store the raw Hub token.
Cache hits do not renew the expiration; failed authentications are not cached.
Concurrent cache misses may each contact the Hub.

Every request still checks the enabled Hub, active local user and current
individual consent. Local permissions remain enforced as usual. Revoking
consent or disabling the Hub/user blocks subsequent requests even with a warm
cache. Changing Hub URLs or the validation endpoint causes a cache miss.
Revocation or identity changes at the partner Hub may take up to five minutes
to be observed. Once an entry expires, upstream failures are not bypassed by
using stale cached identities. No Python client changes are required.
