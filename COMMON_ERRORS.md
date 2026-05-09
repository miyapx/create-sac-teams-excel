# Common Errors

Quick reference for the most common issues when using this toolkit locally.

## 1. SSL certificate verify failed

Example:

```text
SSL verification failed while connecting to token_url
```

What it usually means:

- Python on your machine does not trust the local CA bundle yet
- a company proxy or SSL inspection layer is intercepting HTTPS

What to check:

- install dependencies from `toolkit/requirements.txt`
- install or refresh local Python certificates
- compare `curl` vs Python access to the same `token_url`

Useful commands:

```bash
curl -I "YOUR_TOKEN_URL"
python3 -c "import urllib.request; print(urllib.request.urlopen('YOUR_TOKEN_URL').status)"
```

## 2. Missing required config fields

Example:

```text
Missing required config fields: tenant_url, token_url, client_id, client_secret
```

What it means:

- the app is missing one or more SAC connection values

What to check:

- open `Connection Settings`
- fill `Tenant URL`, `Token URL`, `Client ID`, and `Client Secret`
- save locally if you want the values remembered

## 3. Authentication failed during POST token_url (401 or 403)

Example:

```text
Authentication failed during POST token_url (401)
```

What it usually means:

- `client_id` or `client_secret` is incorrect
- the OAuth client is not configured the way SAC expects

What to check:

- copy the values again from the SAC OAuth client
- confirm you are using the intended `Token URL`
- check the OAuth client setup in SAC, especially `API Access`, `User Provisioning`, and `Client Credentials`

## 4. token_url returned 404

Example:

```text
POST token_url returned 404
```

What it usually means:

- the token endpoint was copied with the wrong path or host

What to check:

- copy the `Token URL` again from SAC
- remove accidental spaces
- test the URL with `curl -I`

## 5. Authorization failed during SCIM write (403)

Example:

```text
Authorization failed during POST SAC SCIM API (403)
```

What it usually means:

- the token was created, but SAC does not allow the write operation
- the tenant accepts the route, but the OAuth client or SAC-side authorization still blocks it

What to check:

- verify the OAuth client permissions in SAC
- review `Execution Log` for:
  - configured SCIM candidates
  - active SCIM base URL
  - request trace before failure

## 6. HTTP 404 route does not exist

Example:

```text
HTTP 404 while calling SAC SCIM API. Response: 404 Not Found: Requested route does not exist.
```

What it usually means:

- that tenant does not accept the SCIM route the tool tried first

What to check:

- the toolkit already tries both `.../scim2` and `.../api/v1/scim`
- check `Execution Log` to see which base URL became active

## 7. Invalid role

Example:

```text
User/group operation not completed: Invalid role R_Planner.
```

What it usually means:

- the role value in `Assign_Roles` does not match the role ID SAC expects

What to check:

- confirm the role ID from your tenant
- standard roles often use `PROFILE:sap.epm:...`
- if your custom roles are stored without `PROFILE:` in Excel, the app auto-prefixes them before sending the update
- check `Execution Log` for `Normalized role IDs for team ...`

## 8. Team does not exist

Example:

```text
Team 'TEAM_X' does not exist.
```

What it usually means:

- `Assign Roles` or `Assign Users` is pointing to a team that is not available in SAC yet

What to check:

- run `Create Teams` first
- or confirm the team already exists in SAC

## 9. User does not exist in SAC

Example:

```text
User 'alice' does not exist in SAC.
```

What it means:

- the current workbook format assigns existing users only

What to check:

- confirm the user already exists in SAC
- confirm the `UserName` in Excel matches the SAC user exactly

## 10. Nothing happens after clicking Run

What to check:

- upload the workbook first
- make sure the workbook validates without errors
- for non-preview actions, make sure the connection fields are filled
- look at `Execution Log` for the step trace

## Best Place to Debug

If something fails, start with:

1. the error message under the action area
2. the `Execution Log` tab
3. the active SCIM base URL and normalized role IDs shown in the log
