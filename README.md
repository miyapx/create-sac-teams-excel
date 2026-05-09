# Bulk Create SAC Teams from Excel

Bulk-upload SAC team setup from one Excel workbook, then run:

- team creation
- role assignment
- user-to-team assignment

from a single local Streamlit app.

## Status

Prepared for the current repository workflow as of **9 May 2026**.

## Important Positioning

This repository is **our own implementation**.
It is shared as a **free source-available toolkit**, not an OSI-style open-source project, because the current license restricts commercial use.

SAP concepts referenced in this workspace support the SAC-side setup, such as:

- Teams managed from `Security > Teams`
- Roles assigned to users and teams
- OAuth Clients created from `System > Administration > App Integration`
- `User Provisioning` used for SCIM-related access

What this repository adds on top:

- the Excel workbook structure
- the Python processing flow
- the Streamlit upload tool
- the local config experience

## Repository Files

```text
SAC_ROLE/
├── .streamlit/
│   └── config.toml
├── data/
│   └── sac_team_data.xlsx
├── app.py
├── sac_role_core.py
├── README.md
├── README_TH.md
├── LICENSE.md
├── config.ini.example
├── requirements.txt
├── run.command
├── run.bat
└── tests/
```

## Excel Workbook Contract

The app expects one `.xlsx` file with these sheets and columns.

### `Create_Teams`

Required columns:

- `Team ID`
- `Team Description`

### `Assign_Roles`

Required columns:

- `TeamID`
- `RoleID`

### `Users`

Required columns:

- `UserName`
- `TeamID`

Notes:

- `RoleID` is sent exactly as written in Excel.
- `Assign_Roles` can target teams created in this run or teams that already exist in SAC.
- `Users` is treated as existing-user assignment only.

## Clone -> Install -> Run

```bash
git clone <your-repo-url>
cd <repo-folder-name>
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Or double-click:

- `run.command` on macOS
- `run.bat` on Windows

## How To Use

1. Click `Download Excel template` if you want the template.
2. Upload your own `.xlsx` file.
3. Open `Connection Settings`.
4. Fill in:
   - `tenant_url`
   - `token_url`
   - `client_id`
   - `client_secret`
5. Optional: click `Save locally` to create a local `config.ini`
6. Optional: click `Load saved` to reload the local file
7. Select a task from the task dropdown
8. Click `Run`

Available tasks:

- `Validate & Preview`
- `Create Teams`
- `Assign Roles`
- `Assign Users`
- `Run All`

## Workbook Summary In The App

After upload, the app shows a compact workbook summary only:

- number of team records
- number of role assignment records
- number of user assignment records

It does not expand the full sheet content by default.

## Deployment Guidance

This toolkit is best suited for:

- SAC consultants preparing or validating team provisioning
- SAC admins running controlled local or internal operations

If you adapt it into a deployed UI for customers, be careful with credential handling:

- do not hardcode `client_secret`
- do not expose OAuth credentials in browser-accessible code
- do not commit customer config files into Git
- do not leak secrets through logs, screenshots, demo videos, or shared packages
- prefer server-side secret storage or a secure secret manager
- use a dedicated OAuth client with only the scope you really need
- validate the flow in a non-production SAC tenant first

## Operational Cautions

- `Validate & Preview` can run without SAC credentials, but the other tasks require valid connection settings.
- `Assign Roles` expects the target team to already exist in SAC or be created earlier in the same workbook flow.
- `Assign Users` works with existing SAC users only. It does not create user profiles from this workbook format.
- Test role and user assignment in a non-production tenant first, especially if your tenant has strict security governance or naming conventions.
- Review logs before re-running large batches, especially after partial failures.

## Local Verification

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Run syntax check:

```bash
python3 -m py_compile sac_role_core.py app.py
```

## License

This repository is shared free of charge for personal, learning, and internal non-commercial use only.

- No warranty is provided.
- Use it at your own risk.
- The author is not liable for any loss, damage, or production impact.
- Commercial use is not allowed without separate permission.

See [LICENSE.md](LICENSE.md).
