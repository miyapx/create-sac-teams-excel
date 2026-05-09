import configparser
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class SacRoleCoreTests(unittest.TestCase):
    def test_load_config_reads_required_settings(self):
        from sac_role_core import load_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.ini"
            parser = configparser.ConfigParser()
            parser["SAC"] = {
                "tenant_url": "https://example.analytics.cloud.sap",
                "token_url": "https://example.authentication.hana.ondemand.com/oauth/token",
                "client_id": "abc",
                "client_secret": "xyz",
            }
            with config_path.open("w", encoding="utf-8") as handle:
                parser.write(handle)

            config = load_config(config_path)

        self.assertEqual(config.tenant_url, "https://example.analytics.cloud.sap")
        self.assertTrue(config.verify_ssl)

    def test_save_and_reload_config_round_trips(self):
        from sac_role_core import AppConfig, load_config, save_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.ini"
            original = AppConfig(
                tenant_url="https://example.analytics.cloud.sap",
                token_url="https://example.authentication.hana.ondemand.com/oauth/token",
                client_id="client-id",
                client_secret="client-secret",
                verify_ssl=False,
                timeout_seconds=45,
                scim_base_url="https://example.analytics.cloud.sap/api/v1/scim",
            )

            save_config(original, config_path)
            loaded = load_config(config_path)

        self.assertEqual(loaded.tenant_url, original.tenant_url)
        self.assertEqual(loaded.client_secret, original.client_secret)
        self.assertTrue(loaded.verify_ssl)
        self.assertEqual(loaded.timeout_seconds, 30)

    def test_load_workbook_uses_actual_sheet_and_column_names(self):
        from sac_role_core import load_workbook_data

        workbook = load_workbook_data(ROOT / "data" / "sac_team_data.xlsx")

        self.assertEqual(len(workbook.teams), 10)
        self.assertEqual(workbook.teams[0].team_id, "T_Alpha_Finance_Planners")
        self.assertEqual(workbook.team_roles[0].role_id, "R_Planner")
        self.assertEqual(workbook.users[0].username, "Miya")

    def test_load_workbook_data_from_uploaded_bytes(self):
        from sac_role_core import load_workbook_data_from_bytes

        workbook_path = ROOT / "data" / "sac_team_data.xlsx"
        workbook = load_workbook_data_from_bytes(workbook_path.read_bytes())

        self.assertEqual(len(workbook.teams), 10)
        self.assertEqual(workbook.users[-1].username, "Brandon")

    def test_validate_dataset_allows_existing_teams_outside_create_sheet(self):
        from sac_role_core import TeamRoleRow, TeamRow, UserRow, WorkbookData, validate_workbook_data

        data = WorkbookData(
            teams=[TeamRow(team_id="TEAM_A", description="A")],
            team_roles=[TeamRoleRow(team_id="TEAM_X", role_id="R_Viewer")],
            users=[UserRow(username="Alice", team_id="TEAM_A")],
        )

        errors = validate_workbook_data(data)

        self.assertEqual(errors, [])

    def test_plan_groups_role_assignments_and_user_assignments(self):
        from sac_role_core import build_execution_plan, load_workbook_data

        workbook = load_workbook_data(ROOT / "data" / "sac_team_data.xlsx")
        plan = build_execution_plan(workbook)

        self.assertEqual(len(plan.create_team_ops), 10)
        self.assertEqual(plan.assign_role_ops[0].role_ids, ["R_Planner"])
        self.assertEqual(plan.assign_user_ops[0].username, "Miya")
        self.assertEqual(plan.assign_user_ops[0].team_ids, ["T_Alpha_Finance_Planners"])

    def test_dry_run_report_mentions_all_three_steps(self):
        from sac_role_core import build_execution_plan, dry_run_report, load_workbook_data

        workbook = load_workbook_data(ROOT / "data" / "sac_team_data.xlsx")
        plan = build_execution_plan(workbook)
        report = dry_run_report(plan)

        self.assertIn("CREATE TEAMS", report)
        self.assertIn("ASSIGN ROLES", report)
        self.assertIn("ASSIGN USERS", report)
        self.assertIn("T_Alpha_Finance_Planners", report)
        self.assertIn("Miya", report)

    def test_workbook_record_counts_returns_sheet_totals(self):
        from sac_role_core import load_workbook_data, workbook_record_counts

        workbook = load_workbook_data(ROOT / "data" / "sac_team_data.xlsx")

        counts = workbook_record_counts(workbook)

        self.assertEqual(
            counts,
            {
                "create_teams": 10,
                "assign_roles": 10,
                "users": 3,
            },
        )


if __name__ == "__main__":
    unittest.main()
