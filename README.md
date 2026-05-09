# SAC Role Provisioning Toolkit

Bulk-manage SAP Analytics Cloud teams, team-role assignments, and user-to-team assignments from a single Excel workbook.

This repository is built around:

- `data/sac_team_data.xlsx`
- `Create_Teams` sheet
- `Assign_Roles` sheet
- `Users` sheet

## Important Positioning

This toolkit is **our own implementation**.

What comes from SAP documentation in this workspace:
- Teams are managed from `Security > Teams`
- Roles can be assigned to users and teams
- OAuth Clients can be created from `System > Administration > App Integration`
- `User Provisioning` is the API access scope for SCIM 2.0

What is our implementation:
- the Excel workbook layout used by this repo
- the Python request flow
- the Streamlit application flow
- the preview output

## Repository Structure

```text
SAC_ROLE/
├── .streamlit/
│   └── config.toml
├── data/
│   └── sac_team_data.xlsx
├── app.py
├── sac_role_core.py
├── run.command
├── run.bat
├── config.ini.example
├── requirements.txt
├── .gitignore
└── tests/
```

## Excel Contract

The workbook path is:

`data/sac_team_data.xlsx`

### Sheet 1: `Create_Teams`

Required columns:
- `Team ID`
- `Team Description`

Example:

| Team ID | Team Description |
| --- | --- |
| T_Alpha_Finance_Planners | Finance planning team for Company Alpha |
| T_Alpha_Finance_Viewers | Finance read-only access for Company Alpha |

### Sheet 2: `Assign_Roles`

Required columns:
- `TeamID`
- `RoleID`

Example:

| TeamID | RoleID |
| --- | --- |
| T_Alpha_Finance_Planners | R_Planner |
| T_Alpha_Finance_Viewers | R_Viewer |

If `RoleID` already starts with `PROFILE:`, the tool uses it as-is.  
If not, the tool sends the value exactly as written in Excel.

`Assign_Roles` can reference:
- teams created from `Create_Teams`
- teams that already exist in SAC

### Sheet 3: `Users`

Required columns:
- `UserName`
- `TeamID`

Example:

| UserName | TeamID |
| --- | --- |
| Miya | T_Alpha_Finance_Planners |
| Alice | T_Alpha_Operations_Planners |

This repo treats the `Users` sheet as an **existing-user assignment sheet**.
That means the tool assigns existing SAC users into teams based on `UserName`.
It does not create new users from this workbook, because the workbook does not contain the required profile fields.
`TeamID` in this sheet can also point to an existing SAC team, not only one created in the same run.

## Setup

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd SAC_ROLE
```

### 2. Install requirements

```bash
python3 -m pip install -r requirements.txt
```

### 3. Run the app

```bash
python3 -m streamlit run app.py
```

Or double-click:
- `run.command` on macOS
- `run.bat` on Windows

No `config.ini` is required to start the app.
The Streamlit onboarding email prompt is already disabled in `.streamlit/config.toml`.

## Usage

### In the app

1. Upload `sac_team_data.xlsx`, or use the bundled sample workbook.
2. Fill in the SAC connection values in the sidebar:
   - `tenant_url`
   - `token_url`
   - `client_id`
   - `client_secret`
3. Optional: click `Save config locally` if you want the values stored in local `config.ini`
4. Optional: click `Load saved config` to reload the local file into the sidebar
5. Click `Validate & Preview` to validate the workbook and see planned operations.
6. Click:
   - `Step 1 Create Teams`
   - `Step 2 Assign Roles`
   - `Step 3 Assign Users`
   - or `Run All`

## Local Verification

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Run syntax check:

```bash
python3 -m py_compile sac_role_core.py app.py
```

## Notes on Safety

- No secrets are stored in code anymore.
- `config.ini` is optional and excluded from Git.
- `Validate & Preview` is the safest first action to run.
- If a team does not exist, role assignment will fail fast.
- If a user in the workbook does not already exist in SAC, user-to-team assignment will fail fast.
