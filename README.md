# Mass Upload Excel to Create SAC Teams and Assign Roles via Python SCIM API - For SAC Admin & Consultant 

Lightweight local toolkit for SAC admins and consultants to:

- create teams
- assign roles
- assign existing users to teams

using one Excel workbook and one Streamlit UI.

## Best For

- SAC consultants preparing or validating team provisioning
- SAC admins running controlled local or internal operations

## Quick Links
- License: [LICENSE.md](LICENSE.md)


```text
SAC_ROLE/
├── .streamlit/
├── toolkit/
├── README.md
├── run.command
└── run.bat
```


## Run

macOS:

```bash
./run.command
```

Windows:

```bat
run.bat
```

Or manually:

```bash
python3 -m pip install -r toolkit/requirements.txt
python3 -m streamlit run toolkit/app.py
```

## SSL Certificate Requirement

This toolkit calls SAC over HTTPS. On some machines, especially fresh local Python installs, Python may fail with:

```text
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

If `curl` can reach your `token_url` but Python cannot, the issue is usually the local Python certificate store.

### macOS

Install dependencies first:

```bash
python3 -m pip install -r toolkit/requirements.txt
python3 -m pip install --upgrade certifi
```

If you installed Python from `python.org`, also run:

```bash
open "/Applications/Python 3.14/Install Certificates.command"
```

If needed, launch the app with the `certifi` bundle explicitly:

```bash
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
python3 -m streamlit run toolkit/app.py
```

### Windows

Install dependencies first:

```bat
py -3 -m pip install -r toolkit\requirements.txt
py -3 -m pip install --upgrade certifi
```

If Python still fails on HTTPS, point Python to the `certifi` CA bundle for the current terminal session:

```bat
for /f "delims=" %i in ('py -3 -c "import certifi; print(certifi.where())"') do set SSL_CERT_FILE=%i
py -3 -m streamlit run toolkit\app.py
```

### Quick Check

These checks help identify whether the issue is SAC auth or local SSL:

```bash
curl -I "YOUR_TOKEN_URL"
python3 -c "import urllib.request; print(urllib.request.urlopen('YOUR_TOKEN_URL').status)"
```

- If `curl` works but Python fails, fix the local Python certificate setup.
- If both fail, check network, proxy, or endpoint access.

## Notes

- The Excel template is `toolkit/sac_team_data.xlsx`
- The sample config is `toolkit/config.ini.example`
- Local saved config is stored beside the app inside `toolkit/config.ini`
- In the `Assign_Roles` sheet, `RoleID` must match the exact role ID in your SAC tenant. Standard roles often use `PROFILE:...`; custom role IDs can differ by tenant.
- For role assignment, the app automatically keeps `PROFILE:...` values as-is and prefixes non-`PROFILE:` values with the configured tenant custom role prefix before sending the SCIM update.
- For common runtime issues, see `toolkit/COMMON_ERRORS.md`
- This is a free source-available toolkit, not an OSI-style open-source project


## More 

- Common errors: [toolkit/COMMON_ERRORS.md](toolkit/COMMON_ERRORS.md)
- License: [toolkit/LICENSE.md](toolkit/LICENSE.md)
