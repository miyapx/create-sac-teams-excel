from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from sac_role_core import (
    AppConfig,
    DEFAULT_CUSTOM_ROLE_PREFIX,
    SacScimClient,
    build_execution_plan,
    dry_run_report,
    load_config,
    load_workbook_data_from_bytes,
    run_assign_roles,
    run_assign_users,
    run_create_teams,
    save_config,
    validate_workbook_data,
    workbook_record_counts,
)


APP_BROWSER_TITLE = "SAC Team"
APP_TITLE = "Bulk Create SAC Teams from Excel"
APP_SUBTITLE = "Upload one workbook, validate it, and run team, role, and user assignment from one minimal screen."
APP_STATUS_DATE = "9 May 2026"
APP_DIR = Path(__file__).parent
APP_FAVICON_PATH = APP_DIR / "miya.png"
TASK_OPTIONS = [
    ("Validate & Preview", "preview", "Check the workbook and preview the planned actions without calling SAC."),
    ("Create Teams", "create-teams", "Create teams from the `Create_Teams` sheet."),
    ("Assign Roles", "assign-roles", "Assign role IDs from the `Assign_Roles` sheet."),
    ("Assign Users", "assign-users", "Assign existing SAC users to teams from the `Users` sheet."),
    ("Run All", "all", "Run team creation, role assignment, and user assignment in one flow."),
]


st.set_page_config(
    page_title=APP_BROWSER_TITLE,
    page_icon=str(APP_FAVICON_PATH),
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background: #f8f8f6;
    }
    .block-container {
        padding-top: 4.25rem;
        padding-bottom: 4.75rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 720px;
    }
    header[data-testid="stHeader"],
    [data-testid="stToolbar"] {
        display: none;
    }
    [data-testid="stHeaderActionElements"],
    [data-testid="stDeployButton"],
    [data-testid="stStatusWidget"],
    #MainMenu,
    [data-testid="stDecoration"] {
        display: none;
    }
    div[data-testid="stHorizontalBlock"] button {
        min-height: 2.65rem;
        font-weight: 600;
        border-radius: 999px;
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        background: #198754;
        border: 1px solid #198754;
        color: white;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: #157347;
        border-color: #157347;
        color: white;
    }
    .hero {
        text-align: center;
        margin-bottom: 1.75rem;
    }
    .hero h1 {
        margin-bottom: 0.65rem;
        font-size: 2.45rem;
        line-height: 1.08;
        color: #171717;
    }
    .hero p {
        margin: 0 auto;
        max-width: 33rem;
        color: #6b7280;
        font-size: 1rem;
        line-height: 1.6;
    }
    .meta-note {
        margin-top: 0.7rem;
        font-size: 0.88rem;
        color: #8b8b84;
    }
    .control-row {
        margin: 0 auto 0.55rem auto;
        max-width: 560px;
    }
    .summary-line {
        text-align: center;
        color: #4b5563;
        font-size: 0.96rem;
        margin-top: 0.65rem;
        margin-bottom: 0.15rem;
    }
    .helper-note {
        text-align: center;
        color: #6b7280;
        font-size: 0.92rem;
        margin-top: 0.55rem;
        margin-bottom: 0;
    }
    .task-note {
        text-align: center;
        color: #6b7280;
        font-size: 0.92rem;
        line-height: 1.5;
        margin-top: 0.35rem;
        margin-bottom: 0.25rem;
    }
    .spacer-sm {
        height: 0.45rem;
    }
    .spacer-md {
        height: 0.75rem;
    }
    .spacer-lg {
        height: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_session_defaults() -> None:
    if st.session_state.get("_defaults_loaded"):
        return

    defaults = {
        "tenant_url": "",
        "token_url": "",
        "client_id": "",
        "client_secret": "",
    }

    config_path = APP_DIR / "config.ini"
    if config_path.exists():
        try:
            config = load_config(config_path)
            defaults.update(
                {
                    "tenant_url": config.tenant_url,
                    "token_url": config.token_url,
                    "client_id": config.client_id,
                    "client_secret": config.client_secret,
                }
            )
        except Exception:
            pass

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    st.session_state["_defaults_loaded"] = True
    st.session_state.setdefault("status_message", "")
    st.session_state.setdefault("action_error", "")
    st.session_state.setdefault("completion_message", "")
    st.session_state.setdefault(
        "progress_state",
        {
            "visible": False,
            "value": 0.0,
            "message": "",
        },
    )


def apply_browser_branding() -> None:
    icon_data = base64.b64encode(APP_FAVICON_PATH.read_bytes()).decode("ascii")
    components.html(
        f"""
        <script>
        const doc = window.parent.document;
        doc.title = "{APP_BROWSER_TITLE}";
        const iconHref = "data:image/png;base64,{icon_data}";
        const iconLinks = Array.from(doc.querySelectorAll("link[rel*='icon']"));
        if (iconLinks.length === 0) {{
          const favicon = doc.createElement("link");
          favicon.rel = "icon";
          favicon.type = "image/png";
          favicon.href = iconHref;
          doc.head.appendChild(favicon);
        }} else {{
          iconLinks.forEach((favicon) => {{
            favicon.rel = "icon";
            favicon.type = "image/png";
            favicon.href = iconHref;
          }});
        }}
        let touchIcon = doc.querySelector("link[rel='apple-touch-icon']");
        if (!touchIcon) {{
          touchIcon = doc.createElement("link");
          touchIcon.rel = "apple-touch-icon";
          doc.head.appendChild(touchIcon);
        }}
        touchIcon.href = iconHref;
        </script>
        """,
        height=0,
    )


def build_config_from_form() -> AppConfig:
    tenant_url = st.session_state.get("tenant_url", "").strip().rstrip("/")
    token_url = st.session_state.get("token_url", "").strip()
    client_id = st.session_state.get("client_id", "").strip()
    client_secret = st.session_state.get("client_secret", "").strip()

    missing = [
        name
        for name, value in [
            ("tenant_url", tenant_url),
            ("token_url", token_url),
            ("client_id", client_id),
            ("client_secret", client_secret),
        ]
        if value == ""
    ]
    if missing:
        raise ValueError(f"Missing required config fields: {', '.join(missing)}")

    return AppConfig(
        tenant_url=tenant_url,
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        custom_role_prefix=DEFAULT_CUSTOM_ROLE_PREFIX,
        scim_base_url=f"{tenant_url}/scim2",
    )


def get_uploaded_workbook_bytes() -> bytes | None:
    uploaded = st.session_state.get("uploaded_workbook")
    if uploaded is None:
        return None
    return uploaded.getvalue()


def analyze_workbook():
    payload = get_uploaded_workbook_bytes()
    if payload is None:
        return None, []
    workbook = load_workbook_data_from_bytes(payload)
    errors = validate_workbook_data(workbook)
    return workbook, errors


def get_plan():
    workbook, errors = analyze_workbook()
    if workbook is None:
        raise ValueError("Upload an Excel workbook before running this action.")
    if errors:
        raise ValueError("\n".join(errors))
    return build_execution_plan(workbook)


def append_log(message: str) -> None:
    logs = st.session_state.setdefault("execution_logs", [])
    logs.append(message)


def append_client_debug_logs(client: SacScimClient) -> None:
    snapshot = client.get_debug_snapshot()
    append_log(f"DEBUG token_url: {snapshot['token_url']}")
    append_log(
        "DEBUG SCIM candidates: "
        + ", ".join(snapshot["scim_base_url_candidates"])
    )
    active_scim_base_url = snapshot["active_scim_base_url"]
    if active_scim_base_url:
        append_log(f"DEBUG active SCIM base URL: {active_scim_base_url}")
    trace = snapshot["trace"]
    if trace:
        append_log("DEBUG trace:")
        for line in trace:
            append_log(f"  - {line}")


def set_progress_state(value: float, message: str, visible: bool = True) -> None:
    st.session_state["progress_state"] = {
        "visible": visible,
        "value": max(0.0, min(1.0, value)),
        "message": message,
    }


def clear_progress_state() -> None:
    set_progress_state(0.0, "", visible=False)


def render_progress_feedback(progress_slot, progress_text_slot) -> None:
    progress_state = st.session_state.get("progress_state", {})
    if progress_state.get("visible"):
        progress_slot.progress(progress_state.get("value", 0.0))
        progress_text_slot.caption(progress_state.get("message", ""))
    else:
        progress_slot.empty()
        progress_text_slot.empty()


def render_status_feedback(success_slot, error_slot) -> None:
    completion_message = st.session_state.get("completion_message", "")
    action_error = st.session_state.get("action_error", "")
    if completion_message:
        success_slot.success(completion_message)
    else:
        success_slot.empty()
    if action_error:
        error_slot.error(action_error)
    else:
        error_slot.empty()


def _operation_total_for_action(action: str, plan) -> int:
    if action == "create-teams":
        return len(plan.create_team_ops)
    if action == "assign-roles":
        return len(plan.assign_role_ops)
    if action == "assign-users":
        return len(plan.assign_user_ops)
    if action == "all":
        return len(plan.create_team_ops) + len(plan.assign_role_ops) + len(plan.assign_user_ops)
    return 0


def _make_progress_callback(
    progress_slot,
    progress_text_slot,
    phase_label: str,
    phase_total: int,
    overall_done: int,
    overall_total: int,
):
    def callback(label: str, current: int, total: int) -> None:
        effective_total = total or phase_total or 1
        completed = overall_done + current
        message = f"Running {phase_label} · {current}/{effective_total}"
        set_progress_state(completed / max(overall_total, 1), message)
        render_progress_feedback(progress_slot, progress_text_slot)

    return callback


initialize_session_defaults()
apply_browser_branding()


def config_path() -> Path:
    return APP_DIR / "config.ini"


def save_config_from_form() -> None:
    config = build_config_from_form()
    save_config(config, config_path())
    st.session_state["status_message"] = "Saved config locally to config.ini"


def load_config_into_form() -> None:
    config = load_config(config_path())
    st.session_state["tenant_url"] = config.tenant_url
    st.session_state["token_url"] = config.token_url
    st.session_state["client_id"] = config.client_id
    st.session_state["client_secret"] = config.client_secret
    st.session_state["status_message"] = "Loaded config from local config.ini"


def run_action(action: str, progress_slot, progress_text_slot) -> None:
    st.session_state["preview_text"] = ""
    st.session_state["completion_message"] = ""
    plan = get_plan()

    if action == "preview":
        set_progress_state(0.2, "Preparing workbook preview...")
        render_progress_feedback(progress_slot, progress_text_slot)
        st.session_state["preview_text"] = dry_run_report(plan)
        set_progress_state(1.0, "Validate & Preview complete.")
        render_progress_feedback(progress_slot, progress_text_slot)
        st.session_state["completion_message"] = "Validate & Preview completed successfully."
        append_log("Validate & Preview completed successfully.")
        return

    config = build_config_from_form()
    client = SacScimClient(config)
    append_log(f"Starting action: {action}")
    append_log(f"Configured tenant URL: {config.tenant_url}")
    append_log(f"Configured token URL: {config.token_url}")
    append_log(f"Configured SCIM base URL: {config.scim_base_url}")
    overall_total = _operation_total_for_action(action, plan)
    if overall_total == 0:
        set_progress_state(1.0, "No rows to process for this task.")
        render_progress_feedback(progress_slot, progress_text_slot)
        st.session_state["completion_message"] = "Nothing to run. The selected sheet has no rows to process."
        append_log("Selected action had no rows to process.")
        return
    try:
        if action == "create-teams":
            append_log("Step: Create Teams")
            set_progress_state(0.0, "Starting Create Teams...")
            render_progress_feedback(progress_slot, progress_text_slot)
            lines = run_create_teams(
                client,
                plan,
                progress_callback=_make_progress_callback(
                    progress_slot,
                    progress_text_slot,
                    "Create Teams",
                    len(plan.create_team_ops),
                    0,
                    overall_total,
                ),
            )
        elif action == "assign-roles":
            append_log("Step: Assign Roles")
            set_progress_state(0.0, "Starting Assign Roles...")
            render_progress_feedback(progress_slot, progress_text_slot)
            lines = run_assign_roles(
                client,
                plan,
                progress_callback=_make_progress_callback(
                    progress_slot,
                    progress_text_slot,
                    "Assign Roles",
                    len(plan.assign_role_ops),
                    0,
                    overall_total,
                ),
            )
        elif action == "assign-users":
            append_log("Step: Assign Users")
            set_progress_state(0.0, "Starting Assign Users...")
            render_progress_feedback(progress_slot, progress_text_slot)
            lines = run_assign_users(
                client,
                plan,
                progress_callback=_make_progress_callback(
                    progress_slot,
                    progress_text_slot,
                    "Assign Users",
                    len(plan.assign_user_ops),
                    0,
                    overall_total,
                ),
            )
        elif action == "all":
            append_log("Step: Run All")
            lines = []
            completed = 0
            append_log("Running team creation")
            if plan.create_team_ops:
                set_progress_state(completed / overall_total, "Starting Create Teams...")
                render_progress_feedback(progress_slot, progress_text_slot)
                lines.extend(
                    run_create_teams(
                        client,
                        plan,
                        progress_callback=_make_progress_callback(
                            progress_slot,
                            progress_text_slot,
                            "Create Teams",
                            len(plan.create_team_ops),
                            completed,
                            overall_total,
                        ),
                    )
                )
                completed += len(plan.create_team_ops)
            append_log("Running role assignment")
            if plan.assign_role_ops:
                set_progress_state(completed / overall_total, "Starting Assign Roles...")
                render_progress_feedback(progress_slot, progress_text_slot)
                lines.extend(
                    run_assign_roles(
                        client,
                        plan,
                        progress_callback=_make_progress_callback(
                            progress_slot,
                            progress_text_slot,
                            "Assign Roles",
                            len(plan.assign_role_ops),
                            completed,
                            overall_total,
                        ),
                    )
                )
                completed += len(plan.assign_role_ops)
            append_log("Running user assignment")
            if plan.assign_user_ops:
                set_progress_state(completed / overall_total, "Starting Assign Users...")
                render_progress_feedback(progress_slot, progress_text_slot)
                lines.extend(
                    run_assign_users(
                        client,
                        plan,
                        progress_callback=_make_progress_callback(
                            progress_slot,
                            progress_text_slot,
                            "Assign Users",
                            len(plan.assign_user_ops),
                            completed,
                            overall_total,
                        ),
                    )
                )
        else:
            raise ValueError(f"Unknown action: {action}")

        for line in lines:
            append_log(line)
        append_client_debug_logs(client)
    except Exception:
        append_client_debug_logs(client)
        raise

    completed_label = next(label for label, value, _ in TASK_OPTIONS if value == action)
    set_progress_state(1.0, f"{completed_label} complete.")
    render_progress_feedback(progress_slot, progress_text_slot)
    st.session_state["completion_message"] = f"{completed_label} completed successfully."


st.markdown(
    f"""
    <div class="hero">
        <h1>{APP_TITLE}</h1>
        <p>{APP_SUBTITLE}</p>
        <div class="meta-note">Prepared for local use and repository release status as of {APP_STATUS_DATE}.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="control-row">', unsafe_allow_html=True)
left_pad, controls_col, right_pad = st.columns([0.6, 4.6, 0.6])
with controls_col:
    action_left, action_right = st.columns(2, gap="small")
    with action_left:
        st.download_button(
            "Download Excel template",
            data=(APP_DIR / "sac_team_data.xlsx").read_bytes(),
            file_name="sac_team_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with action_right:
        with st.popover("Connection Settings", use_container_width=True):
            st.text_input("Tenant URL", key="tenant_url", placeholder="https://your-tenant.ap11.analytics.cloud.sap")
            st.text_input("Token URL", key="token_url", placeholder="https://your-tenant.authentication.ap11.hana.ondemand.com/oauth/token")
            st.text_input("Client ID", key="client_id")
            st.text_input("Client Secret", key="client_secret", type="password")
            config_cols = st.columns(2)
            with config_cols[0]:
                if st.button("Save locally", use_container_width=True):
                    try:
                        save_config_from_form()
                        st.toast("Config saved")
                    except Exception as exc:
                        st.session_state["status_message"] = f"Save failed: {exc}"
                        st.error(str(exc))
            with config_cols[1]:
                if st.button("Load saved", use_container_width=True):
                    try:
                        load_config_into_form()
                        st.toast("Config loaded")
                    except Exception as exc:
                        st.session_state["status_message"] = f"Load failed: {exc}"
                        st.error(str(exc))
st.markdown("</div>", unsafe_allow_html=True)
if st.session_state.get("status_message"):
    st.caption(st.session_state["status_message"])

st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
st.file_uploader("Upload Excel workbook", type=["xlsx"], key="uploaded_workbook")

try:
    workbook, workbook_errors = analyze_workbook()
except Exception as exc:
    workbook = None
    workbook_errors = [str(exc)]

if st.session_state.get("uploaded_workbook") is None:
    st.markdown(
        '<p class="helper-note">Upload your workbook to continue, or download the sample file above.</p>',
        unsafe_allow_html=True,
    )
elif workbook_errors:
    for issue in workbook_errors:
        st.error(issue)
else:
    counts = workbook_record_counts(workbook)
    st.markdown(
        (
            '<div class="summary-line">'
            f'Workbook ready · {counts["create_teams"]} teams · '
            f'{counts["assign_roles"]} role rows · {counts["users"]} user rows'
            "</div>"
        ),
        unsafe_allow_html=True,
    )

st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
st.caption("`Validate & Preview` checks the workbook and shows the planned actions without sending anything to SAC.")

actions_disabled = workbook is None or bool(workbook_errors)
task_lookup = {label: {"action": action, "description": description} for label, action, description in TASK_OPTIONS}
task_left, task_right = st.columns([3.4, 1], gap="small")
with task_left:
    selected_task = st.selectbox(
        "Choose task",
        options=[label for label, _, _ in TASK_OPTIONS],
        label_visibility="collapsed",
        disabled=actions_disabled,
    )
st.markdown(
    f'<p class="task-note">{task_lookup[selected_task]["description"]}</p>',
    unsafe_allow_html=True,
)
run_clicked = False
with task_right:
    run_clicked = st.button("Run", type="primary", use_container_width=True, disabled=actions_disabled)

feedback_block = st.container()
with feedback_block:
    progress_slot = st.empty()
    progress_text_slot = st.empty()
    success_slot = st.empty()
    error_slot = st.empty()

render_progress_feedback(progress_slot, progress_text_slot)
render_status_feedback(success_slot, error_slot)

if run_clicked:
    try:
        st.session_state["action_error"] = ""
        st.session_state["completion_message"] = ""
        clear_progress_state()
        render_progress_feedback(progress_slot, progress_text_slot)
        render_status_feedback(success_slot, error_slot)
        run_action(task_lookup[selected_task]["action"], progress_slot, progress_text_slot)
        render_status_feedback(success_slot, error_slot)
        st.toast(f"{selected_task} completed")
    except Exception as exc:
        append_log(f"ERROR during {selected_task}: {exc}")
        st.session_state["action_error"] = str(exc)
        render_status_feedback(success_slot, error_slot)


preview_text = st.session_state.get("preview_text", "")
logs = st.session_state.get("execution_logs", [])
if preview_text or logs:
    preview_tab, log_tab = st.tabs(["Planned Actions", "Execution Log"])

    with preview_tab:
        if preview_text:
            st.code(preview_text, language="text")
        else:
            st.markdown(
                '<p class="helper-note">No preview has been generated yet.</p>',
                unsafe_allow_html=True,
            )

    with log_tab:
        if logs:
            st.code("\n".join(logs), language="text")
        else:
            st.markdown(
                '<p class="helper-note">No actions have run yet.</p>',
                unsafe_allow_html=True,
            )


st.markdown("---")
st.caption(
    "Current workbook format: `Users` only includes `UserName` and `TeamID`, so this app assigns existing SAC users to teams. "
    "It does not create new users from the workbook in its current format."
)
st.caption(
    "Toolkit note: designed for SAC consultants and admins running locally or in a controlled internal environment. "
    "If you adapt this into a customer-facing deployed UI, keep OAuth credentials server-side, avoid exposing `client_secret` in browser-accessible code, "
    "and do not leak secrets through repos, screenshots, logs, or shared config files."
)
st.caption("Free for personal, learning, and internal non-commercial use only. No warranty. See `LICENSE.md`.")
