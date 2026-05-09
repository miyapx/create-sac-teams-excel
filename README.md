# Bulk Create SAC Teams from Excel

Bulk-upload SAC team setup from one Excel workbook, then run:

- team creation
- role assignment
- user-to-team assignment

from one local Streamlit tool.

This repository is **our own implementation**. It is shared as a **free source-available toolkit**, not an OSI-style open-source project, because the current license restricts commercial use.

## Best For

- SAC consultants preparing or validating team provisioning
- SAC admins running controlled local or internal operations

## Quick Links

- Thai README: [docs/readme-th.md](docs/readme-th.md)
- English guide: [docs/guide-en.md](docs/guide-en.md)
- Thai guide: [docs/guide-th.md](docs/guide-th.md)
- License: [LICENSE.md](LICENSE.md)

## Clean Repository Layout

```text
SAC_ROLE/
├── .streamlit/
├── assets/
├── data/
├── docs/
├── examples/
├── scripts/
├── tests/
├── app.py
├── sac_role_core.py
├── requirements.txt
├── README.md
└── LICENSE.md
```

## Workbook Contract

The app expects one `.xlsx` file with these sheets and columns:

- `Create_Teams`: `Team ID`, `Team Description`
- `Assign_Roles`: `TeamID`, `RoleID`
- `Users`: `UserName`, `TeamID`

Notes:

- `RoleID` is sent exactly as written in Excel.
- `Assign_Roles` can target teams created in this run or teams that already exist in SAC.
- `Users` is treated as existing-user assignment only.

The template workbook is stored at:

- `data/sac_team_data.xlsx`

## Clone -> Install -> Run

```bash
git clone <your-repo-url>
cd <repo-folder-name>
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Or use:

- `scripts/run.command` on macOS
- `scripts/run.bat` on Windows

## App Flow

1. Click `Download Excel template` if you want the workbook format.
2. Upload your own `.xlsx` file.
3. Open `Connection Settings`.
4. Fill in:
   - `tenant_url`
   - `token_url`
   - `client_id`
   - `client_secret`
5. Optional: save the values locally into `config.ini`
6. Choose a task from the dropdown
7. Click `Run`

Available tasks:

- `Validate & Preview`
- `Create Teams`
- `Assign Roles`
- `Assign Users`
- `Run All`

## Repository Notes

- `assets/` contains the favicon and branding assets.
- `docs/` contains the Thai README and guide-style writeups.
- `examples/` contains `config.ini.example`.
- `scripts/` contains helper launchers.

## Operational Cautions

- `Validate & Preview` can run without SAC credentials, but the other tasks require valid connection settings.
- `Assign Roles` expects the target team to already exist in SAC or be created earlier in the same workbook flow.
- `Assign Users` works with existing SAC users only. It does not create user profiles from this workbook format.
- Review logs before re-running large batches, especially after partial failures.
- Validate the flow in a non-production tenant first.

## Deployment Guidance

If you adapt this into a deployed UI for customers:

- do not hardcode `client_secret`
- do not expose OAuth credentials in browser-accessible code
- do not commit customer config files into Git
- do not leak secrets through logs, screenshots, demo videos, or shared packages
- prefer server-side secret storage or a secure secret manager
- use a dedicated OAuth client with only the scope you really need

## Local Verification

```bash
python3 -m py_compile app.py sac_role_core.py
python3 -m unittest discover -s tests -v
```

## License

This repository is shared free of charge for personal, learning, and internal non-commercial use only.

- No warranty is provided.
- Use it at your own risk.
- The author is not liable for any loss, damage, or production impact.
- Commercial use is not allowed without separate permission.
