# Bulk-create-team-in-SAC-via-excel-python-SCIM-API---for-SAC-Admins-
Automate SAC Team Creation via Excel + Python SCIM API — A Step-by-Step Guide for SAP Admins
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
- the CLI and step scripts
- the dry-run output
- the role prefix handling

## Repository Structure

```text
SAC_ROLE/
├── data/
│   └── sac_team_data.xlsx
├── sac_role_core.py
├── sac_role_cli.py
├── dry_run.py
├── run_all.py
├── script_1_create_teams.py
├── script_2_assign_roles.py
├── script_3_assign_users.py
├── check_role_id.py
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
If not, the tool prepends `custom_role_prefix` from `config.ini`.

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

### 1. Install requirements

```bash
python3 -m pip install -r requirements.txt
```

### 2. Create your local config

Copy:

```bash
cp config.ini.example config.ini
```

Then fill in:
- `tenant_url`
- `token_url`
- `client_id`
- `client_secret`
- `custom_role_prefix`

`config.ini` is ignored by Git on purpose.

## Usage

### Dry run

```bash
python3 dry_run.py
```

This validates the workbook and prints the exact operations the tool would perform.

### Step 1: Create teams

```bash
python3 script_1_create_teams.py
```

### Step 2: Assign roles to teams

```bash
python3 script_2_assign_roles.py
```

### Step 3: Assign users to teams

```bash
python3 script_3_assign_users.py
```

### Run everything

```bash
python3 run_all.py
```

### Advanced CLI

```bash
python3 sac_role_cli.py dry-run
python3 sac_role_cli.py create-teams
python3 sac_role_cli.py assign-roles
python3 sac_role_cli.py assign-users
python3 sac_role_cli.py all
```

## Local Verification

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

Run syntax check:

```bash
python3 -m py_compile sac_role_core.py sac_role_cli.py
```

## Notes on Safety

- No secrets are stored in code anymore.
- `config.ini` is excluded from Git.
- `dry_run.py` is the safest first command to run.
- If a team does not exist, role assignment will fail fast.
- If a user in the workbook does not already exist in SAC, user-to-team assignment will fail fast.
