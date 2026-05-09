import configparser
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import requests


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
        self.assertEqual(config.scim_base_url, "https://example.analytics.cloud.sap/scim2")

    def test_save_and_reload_config_round_trips(self):
        from sac_role_core import AppConfig, load_config, save_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.ini"
            original = AppConfig(
                tenant_url="https://example.analytics.cloud.sap",
                token_url="https://example.authentication.hana.ondemand.com/oauth/token",
                client_id="client-id",
                client_secret="client-secret",
                custom_role_prefix="PROFILE:t.TEST:",
                verify_ssl=False,
                timeout_seconds=45,
                scim_base_url="https://example.analytics.cloud.sap/scim2",
            )

            save_config(original, config_path)
            loaded = load_config(config_path)

        self.assertEqual(loaded.tenant_url, original.tenant_url)
        self.assertEqual(loaded.client_secret, original.client_secret)
        self.assertEqual(loaded.custom_role_prefix, original.custom_role_prefix)
        self.assertTrue(loaded.verify_ssl)
        self.assertEqual(loaded.timeout_seconds, 30)

    def test_load_workbook_uses_actual_sheet_and_column_names(self):
        from sac_role_core import load_workbook_data

        workbook = load_workbook_data(ROOT / "sac_team_data.xlsx")

        self.assertEqual(len(workbook.teams), 10)
        self.assertEqual(workbook.teams[0].team_id, "T_Alpha_Finance_Planners")
        self.assertEqual(workbook.team_roles[0].role_id, "PROFILE:sap.epm:Planner_Reporter")
        self.assertEqual(workbook.users[0].username, "Miya")

    def test_load_workbook_data_from_uploaded_bytes(self):
        from sac_role_core import load_workbook_data_from_bytes

        workbook_path = ROOT / "sac_team_data.xlsx"
        workbook = load_workbook_data_from_bytes(workbook_path.read_bytes())

        self.assertEqual(len(workbook.teams), 10)
        self.assertEqual(workbook.users[-1].username, "Brandon")

    def test_validate_dataset_allows_existing_teams_outside_create_sheet(self):
        from sac_role_core import TeamRoleRow, TeamRow, UserRow, WorkbookData, validate_workbook_data

        data = WorkbookData(
            teams=[TeamRow(team_id="TEAM_A", description="A")],
            team_roles=[TeamRoleRow(team_id="TEAM_X", role_id="PROFILE:sap.epm:Viewer")],
            users=[UserRow(username="Alice", team_id="TEAM_A")],
        )

        errors = validate_workbook_data(data)

        self.assertEqual(errors, [])

    def test_validate_dataset_allows_custom_role_ids(self):
        from sac_role_core import TeamRoleRow, TeamRow, UserRow, WorkbookData, validate_workbook_data

        data = WorkbookData(
            teams=[TeamRow(team_id="TEAM_A", description="A")],
            team_roles=[TeamRoleRow(team_id="TEAM_A", role_id="R_Planner")],
            users=[UserRow(username="Alice", team_id="TEAM_A")],
        )

        errors = validate_workbook_data(data)

        self.assertEqual(errors, [])

    def test_normalize_role_id_adds_custom_prefix_for_non_profile_roles(self):
        from sac_role_core import AppConfig, SacScimClient

        client = SacScimClient(
            AppConfig(
                tenant_url="https://example.analytics.cloud.sap",
                token_url="https://example.authentication.hana.ondemand.com/oauth/token",
                client_id="client-id",
                client_secret="client-secret",
                custom_role_prefix="PROFILE:t.TEST:",
                scim_base_url="https://example.analytics.cloud.sap/scim2",
            )
        )

        self.assertEqual(client.normalize_role_id("R_Planner"), "PROFILE:t.TEST:R_Planner")
        self.assertEqual(
            client.normalize_role_id("PROFILE:sap.epm:Viewer"),
            "PROFILE:sap.epm:Viewer",
        )

    def test_plan_groups_role_assignments_and_user_assignments(self):
        from sac_role_core import build_execution_plan, load_workbook_data

        workbook = load_workbook_data(ROOT / "sac_team_data.xlsx")
        plan = build_execution_plan(workbook)

        self.assertEqual(len(plan.create_team_ops), 10)
        self.assertEqual(plan.assign_role_ops[0].role_ids, ["PROFILE:sap.epm:Planner_Reporter"])
        self.assertEqual(plan.assign_user_ops[0].username, "Miya")
        self.assertEqual(plan.assign_user_ops[0].team_ids, ["T_Alpha_Finance_Planners"])

    def test_dry_run_report_mentions_all_three_steps(self):
        from sac_role_core import build_execution_plan, dry_run_report, load_workbook_data

        workbook = load_workbook_data(ROOT / "sac_team_data.xlsx")
        plan = build_execution_plan(workbook)
        report = dry_run_report(plan)

        self.assertIn("CREATE TEAMS", report)
        self.assertIn("ASSIGN ROLES", report)
        self.assertIn("ASSIGN USERS", report)
        self.assertIn("T_Alpha_Finance_Planners", report)
        self.assertIn("Miya", report)

    def test_run_create_teams_reports_progress(self):
        from sac_role_core import CreateTeamOp, ExecutionPlan, run_create_teams

        class StubClient:
            def __init__(self):
                self.created = []

            def create_team(self, op):
                self.created.append(op.team_id)

        client = StubClient()
        plan = ExecutionPlan(
            create_team_ops=[
                CreateTeamOp(team_id="TEAM_A", description="A"),
                CreateTeamOp(team_id="TEAM_B", description="B"),
            ],
            assign_role_ops=[],
            assign_user_ops=[],
        )
        events = []

        lines = run_create_teams(
            client,
            plan,
            progress_callback=lambda label, current, total: events.append((label, current, total)),
        )

        self.assertEqual(client.created, ["TEAM_A", "TEAM_B"])
        self.assertEqual(lines, ["Team ready: TEAM_A", "Team ready: TEAM_B"])
        self.assertEqual(
            events,
            [
                ("Create Teams", 1, 2),
                ("Create Teams", 2, 2),
            ],
        )

    def test_run_assign_roles_reports_progress(self):
        from sac_role_core import AssignRoleOp, ExecutionPlan, run_assign_roles

        class StubClient:
            def __init__(self):
                self.assigned = []

            def assign_roles(self, op):
                self.assigned.append((op.team_id, list(op.role_ids)))

        client = StubClient()
        plan = ExecutionPlan(
            create_team_ops=[],
            assign_role_ops=[
                AssignRoleOp(team_id="TEAM_A", role_ids=["R_Planner"]),
                AssignRoleOp(team_id="TEAM_B", role_ids=["PROFILE:sap.epm:Viewer"]),
            ],
            assign_user_ops=[],
        )
        events = []

        lines = run_assign_roles(
            client,
            plan,
            progress_callback=lambda label, current, total: events.append((label, current, total)),
        )

        self.assertEqual(
            client.assigned,
            [
                ("TEAM_A", ["R_Planner"]),
                ("TEAM_B", ["PROFILE:sap.epm:Viewer"]),
            ],
        )
        self.assertEqual(
            lines,
            [
                "Roles assigned: TEAM_A -> R_Planner",
                "Roles assigned: TEAM_B -> PROFILE:sap.epm:Viewer",
            ],
        )
        self.assertEqual(
            events,
            [
                ("Assign Roles", 1, 2),
                ("Assign Roles", 2, 2),
            ],
        )

    def test_run_assign_users_reports_progress(self):
        from sac_role_core import AssignUserOp, ExecutionPlan, run_assign_users

        class StubClient:
            def __init__(self):
                self.assigned = []

            def assign_user_teams(self, op):
                self.assigned.append((op.username, list(op.team_ids)))

        client = StubClient()
        plan = ExecutionPlan(
            create_team_ops=[],
            assign_role_ops=[],
            assign_user_ops=[
                AssignUserOp(username="Miya", team_ids=["TEAM_A"]),
                AssignUserOp(username="Brandon", team_ids=["TEAM_B", "TEAM_C"]),
            ],
        )
        events = []

        lines = run_assign_users(
            client,
            plan,
            progress_callback=lambda label, current, total: events.append((label, current, total)),
        )

        self.assertEqual(
            client.assigned,
            [
                ("Miya", ["TEAM_A"]),
                ("Brandon", ["TEAM_B", "TEAM_C"]),
            ],
        )
        self.assertEqual(
            lines,
            [
                "User assigned: Miya -> TEAM_A",
                "User assigned: Brandon -> TEAM_B, TEAM_C",
            ],
        )
        self.assertEqual(
            events,
            [
                ("Assign Users", 1, 2),
                ("Assign Users", 2, 2),
            ],
        )

    def test_workbook_record_counts_returns_sheet_totals(self):
        from sac_role_core import load_workbook_data, workbook_record_counts

        workbook = load_workbook_data(ROOT / "sac_team_data.xlsx")

        counts = workbook_record_counts(workbook)

        self.assertEqual(
            counts,
            {
                "create_teams": 10,
                "assign_roles": 10,
                "users": 3,
            },
        )

    def test_http_error_message_identifies_token_auth_failure(self):
        from sac_role_core import AppConfig, SacScimClient

        client = SacScimClient(
            AppConfig(
                tenant_url="https://example.analytics.cloud.sap",
                token_url="https://example.authentication.hana.ondemand.com/oauth/token",
                client_id="client-id",
                client_secret="client-secret",
                scim_base_url="https://example.analytics.cloud.sap/scim2",
            )
        )

        message = client._format_http_error(
            "POST",
            "https://example.authentication.hana.ondemand.com/oauth/token?grant_type=client_credentials",
            401,
            "",
        )

        self.assertIn("Authentication failed during POST token_url", message)

    def test_http_error_message_identifies_bad_token_url(self):
        from sac_role_core import AppConfig, SacScimClient

        client = SacScimClient(
            AppConfig(
                tenant_url="https://example.analytics.cloud.sap",
                token_url="https://example.authentication.hana.ondemand.com/oauth/token",
                client_id="client-id",
                client_secret="client-secret",
                scim_base_url="https://example.analytics.cloud.sap/scim2",
            )
        )

        message = client._format_http_error(
            "POST",
            "https://example.authentication.hana.ondemand.com/oauth/token?grant_type=client_credentials",
            404,
            "",
        )

        self.assertIn("token_url returned 404", message)

    def test_url_error_message_identifies_ssl_failure(self):
        from sac_role_core import AppConfig, SacScimClient

        client = SacScimClient(
            AppConfig(
                tenant_url="https://example.analytics.cloud.sap",
                token_url="https://example.authentication.hana.ondemand.com/oauth/token",
                client_id="client-id",
                client_secret="client-secret",
                scim_base_url="https://example.analytics.cloud.sap/scim2",
            )
        )

        message = client._format_url_error(
            "https://example.authentication.hana.ondemand.com/oauth/token",
            requests.exceptions.SSLError("[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed"),
        )

        self.assertIn("SSL verification failed while connecting to token_url", message)

    def test_verify_value_uses_certifi_when_ssl_verification_is_enabled(self):
        from sac_role_core import AppConfig, SacScimClient

        client = SacScimClient(
            AppConfig(
                tenant_url="https://example.analytics.cloud.sap",
                token_url="https://example.authentication.hana.ondemand.com/oauth/token",
                client_id="client-id",
                client_secret="client-secret",
                scim_base_url="https://example.analytics.cloud.sap/scim2",
            )
        )

        with mock.patch("sac_role_core.certifi.where", return_value="/tmp/certifi.pem"):
            verify_value = client._verify_value()

        self.assertEqual(verify_value, "/tmp/certifi.pem")

    def test_verify_value_can_disable_ssl_verification(self):
        from sac_role_core import AppConfig, SacScimClient

        client = SacScimClient(
            AppConfig(
                tenant_url="https://example.analytics.cloud.sap",
                token_url="https://example.authentication.hana.ondemand.com/oauth/token",
                client_id="client-id",
                client_secret="client-secret",
                verify_ssl=False,
                scim_base_url="https://example.analytics.cloud.sap/scim2",
            )
        )

        self.assertFalse(client._verify_value())

    def test_scim_base_url_candidates_include_api_v1_fallback_for_scim2_default(self):
        from sac_role_core import AppConfig, SacScimClient

        client = SacScimClient(
            AppConfig(
                tenant_url="https://example.analytics.cloud.sap",
                token_url="https://example.authentication.hana.ondemand.com/oauth/token",
                client_id="client-id",
                client_secret="client-secret",
                scim_base_url="https://example.analytics.cloud.sap/scim2",
            )
        )

        self.assertEqual(
            client._scim_base_url_candidates(),
            [
                "https://example.analytics.cloud.sap/scim2",
                "https://example.analytics.cloud.sap/api/v1/scim",
            ],
        )

    def test_scim_base_url_candidates_include_scim2_fallback_for_api_v1_default(self):
        from sac_role_core import AppConfig, SacScimClient

        client = SacScimClient(
            AppConfig(
                tenant_url="https://example.analytics.cloud.sap",
                token_url="https://example.authentication.hana.ondemand.com/oauth/token",
                client_id="client-id",
                client_secret="client-secret",
                scim_base_url="https://example.analytics.cloud.sap/api/v1/scim",
            )
        )

        self.assertEqual(
            client._scim_base_url_candidates(),
            [
                "https://example.analytics.cloud.sap/api/v1/scim",
                "https://example.analytics.cloud.sap/scim2",
            ],
        )

    def test_http_error_message_identifies_possible_csrf_issue(self):
        from sac_role_core import AppConfig, SacScimClient

        client = SacScimClient(
            AppConfig(
                tenant_url="https://example.analytics.cloud.sap",
                token_url="https://example.authentication.hana.ondemand.com/oauth/token",
                client_id="client-id",
                client_secret="client-secret",
                scim_base_url="https://example.analytics.cloud.sap/api/v1/scim",
            )
        )

        message = client._format_http_error(
            "POST",
            "https://example.analytics.cloud.sap/api/v1/scim/Groups",
            403,
            '{"message":"CSRF token validation failed"}',
        )

        self.assertIn("Possible CSRF or session cookie issue", message)
        self.assertIn("POST SAC SCIM API", message)

    def test_debug_snapshot_exposes_scim_candidates_and_active_url(self):
        from sac_role_core import AppConfig, SacScimClient

        client = SacScimClient(
            AppConfig(
                tenant_url="https://example.analytics.cloud.sap",
                token_url="https://example.authentication.hana.ondemand.com/oauth/token",
                client_id="client-id",
                client_secret="client-secret",
                scim_base_url="https://example.analytics.cloud.sap/scim2",
            )
        )

        snapshot = client.get_debug_snapshot()

        self.assertEqual(snapshot["active_scim_base_url"], "")
        self.assertEqual(
            snapshot["scim_base_url_candidates"],
            [
                "https://example.analytics.cloud.sap/scim2",
                "https://example.analytics.cloud.sap/api/v1/scim",
            ],
        )

    def test_debug_trace_records_steps(self):
        from sac_role_core import AppConfig, SacScimClient

        client = SacScimClient(
            AppConfig(
                tenant_url="https://example.analytics.cloud.sap",
                token_url="https://example.authentication.hana.ondemand.com/oauth/token",
                client_id="client-id",
                client_secret="client-secret",
                scim_base_url="https://example.analytics.cloud.sap/scim2",
            )
        )

        client._trace("Testing debug trace")

        self.assertIn("Testing debug trace", client.get_debug_snapshot()["trace"])


if __name__ == "__main__":
    unittest.main()
