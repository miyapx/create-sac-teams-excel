# Bulk Create SAC Teams from Excel

## Summary

Creating SAC teams one by one in the UI is manageable for a few requests, but it gets repetitive fast when the list grows.

This repository turns that admin flow into a simpler upload pattern:

1. prepare one Excel workbook
2. upload it into a local Streamlit tool
3. validate the workbook
4. run create team, assign role, and assign user actions from one screen

Important: this tool is **our own implementation**, not SAP sample code.
It is better described as a free source-available toolkit than a classic open-source project, because the current license restricts commercial use.

## Why This Version Is Easier To Use

The app is built for local use:

- always light theme
- no `config.ini` required to start
- connection values entered from the UI
- sample workbook available as a download, not auto-loaded
- uploaded workbook summary kept compact

## Workbook Contract

The tool is driven by:

`data/sac_team_data.xlsx`

Expected sheets:

- `Create_Teams`
- `Assign_Roles`
- `Users`

Expected columns:

- `Create_Teams`: `Team ID`, `Team Description`
- `Assign_Roles`: `TeamID`, `RoleID`
- `Users`: `UserName`, `TeamID`

## App Flow

### Step 1: Download the Excel template if needed

The sample file is there only as a template.
It does not run by default.

### Step 2: Upload your workbook

Once the file is uploaded, the app validates the workbook structure.

### Step 3: Open Connection Settings

Fill in:

- `tenant_url`
- `token_url`
- `client_id`
- `client_secret`

You can also save the config locally for future runs.

### Step 4: Click `Validate & Preview`

This does not call SAC.
It only checks the workbook and shows the planned actions.

### Step 5: Run the action you want

Choose a task from the dropdown, then click `Run`.

Available tasks:

- `Validate & Preview`
- `Create Teams`
- `Assign Roles`
- `Assign Users`
- `Run All`

## Compact Workbook Summary

After upload, the UI only shows a small summary:

- how many team rows
- how many role rows
- how many user rows

This keeps the screen readable even when the workbook contains large datasets.

## Publish Note

This repository snapshot was prepared for the workflow current on **9 May 2026**.

## License Note

This repository is shared free of charge for personal, learning, and internal non-commercial use only, with no warranty and no liability. See `LICENSE.md`.
