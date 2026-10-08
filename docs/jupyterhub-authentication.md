# Partner JupyterHub authentication

The API accepts `Authorization: JupyterHub <partner-id> <hub-token>`.
Existing Token, OAuth and session authentication remain available. This
integration is disabled until trusted partners are configured.

Set `JUPYTERHUB_PARTNERS_JSON` in the backend container environment to JSON:

```json
{
  "linea-dev": {
    "enabled": true,
    "user_url": "https://jupyter-dev.linea.org.br/hub/api/user"
  }
}
```

The username returned by the trusted Hub must exactly match the `username` of
an existing active PzServer account, including case. No ID mapping, email
fallback, normalization or automatic account creation is performed. Partner
approval means trusting that partner's username namespace to identify the same
people as the local namespace. Never put Hub tokens in this configuration.
Ensure your deployment passes the variable to the backend, then restart it.
No database migration is needed.

The backend must reach the configured HTTPS endpoint. It forwards the token
only to this fixed endpoint, disables redirects, uses connection/read timeouts,
and validates the returned user identity on every request. It rejects service
identities, unknown usernames and inactive local accounts. Hub admin flags and
groups do not change local permissions. Upstream failures return 503.

Smoke test from the partner notebook after deployment:

```python
import os
import requests

response = requests.get(
    "https://pzserver-dev.linea.org.br/api/",
    headers={
        "Authorization": "JupyterHub linea-dev " + os.environ["JUPYTERHUB_API_TOKEN"]
    },
    timeout=(5, 20),
    allow_redirects=False,
)
print(response.status_code)
```

Use only the intended, trusted PzServer deployment over HTTPS. The Hub token
also grants Hub permissions: redact Authorization headers in application,
proxy and monitoring logs. Do not print or persist the token in notebooks.
With the corresponding Python package update, use
`PzServer(host="pz-dev")` in the partner notebook. It discovers the Hub from
`JUPYTERHUB_PUBLIC_HUB_URL` or `JUPYTERHUB_HOST` when a recognized public Hub
URL is available and no explicit or saved PzServer token takes precedence.

To disable a partner set `enabled` to false and reload the backend. Deactivating
a local account blocks its access, including partner authentication. No
production configuration or user account is changed by this code change.
