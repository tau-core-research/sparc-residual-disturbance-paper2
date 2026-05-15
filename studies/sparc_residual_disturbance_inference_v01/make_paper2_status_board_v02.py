#!/usr/bin/env python3
"""Build the post-route2 Paper 2 status and claim board."""

from __future__ import annotations

import json

from make_packet_v01_seed import PACKET, write_csv


STATUS_MD = PACKET / "paper2_external_validation_status_board_v02.md"
STATUS_CSV = PACKET / "paper2_external_validation_status_board_v02.csv"
CLAIMS_CSV = PACKET / "paper2_claim_boundary_v02.csv"
READINESS_CSV = PACKET / "paper2_readiness_table_v02.csv"
DECISION_CSV = PACKET / "paper2_next_step_decision_v02.csv"

GUARDRAIL = "paper2_v02_route2_closed_no_tau_validation_no_velocity_endpoint"


def status_rows() -> list[dict[str, str]]:
    return [
        {
            "FamilyID": "CORE",
            "Family": "SPARC residual-inferred W_tau_eff seed",
            "JoinedN": "45",
            "PrimaryMetric": "Projection_RMS_LOOGO_AUC=0.771008403;shuffle_null_p=0.002000000",
            "PaperRole": "primary_internal_diagnostic",
            "Status": "paper_candidate_with_caveats",
            "Limitation": "derived from SPARC residual structure; not external validation and not Tau Core proof",
            "AllowedClaim": "residual-shape features carry reproducible external-label information inside SPARC",
            "ForbiddenClaim": "Tau Core validation or physical field detection",
            "NextAction": "write_as_diagnostic_methodology_result",
            "Guardrail": GUARDRAIL,
        },
        {
            "FamilyID": "WHISP_RESOLVED",
            "Family": "WHISP resolved HI asymmetry",
            "JoinedN": "14",
            "PrimaryMetric": "Pearson=0.391218683;AUC=0.714285714",
            "PaperRole": "supporting_external_readout",
            "Status": "directional_support_but_small_overlap",
            "Limitation": "small overlap; no velocity endpoint; not independent mass-model validation",
            "AllowedClaim": "WHISP resolved-HI burden is directionally aligned with W_tau_eff in a small overlap",
            "ForbiddenClaim": "paper-grade external validation by itself",
            "NextAction": "retain_as_supporting_section_or_appendix",
            "Guardrail": GUARDRAIL,
        },
        {
            "FamilyID": "WHISP_MORPH",
            "Family": "WHISP Holwerda morphology",
            "JoinedN": "25",
            "PrimaryMetric": "AsymmetryA_AUC=0.644230769;MorphologyBurden_AUC=0.506410256",
            "PaperRole": "supporting_morphology_readout",
            "Status": "mixed_directional_support",
            "Limitation": "some morphology metrics align, composite burden is weak",
            "AllowedClaim": "some WHISP morphology coordinates weakly align with W_tau_eff",
            "ForbiddenClaim": "morphology validates Tau Core or replaces residual-blind labels",
            "NextAction": "report_as_mixed_external_context",
            "Guardrail": GUARDRAIL,
        },
        {
            "FamilyID": "REYNOLDS_LVH",
            "Family": "Reynolds 2020/LVHIS resolved HI asymmetry",
            "JoinedN": "6",
            "PrimaryMetric": "AvelPearson=0.375346400;AvelAUC=0.777777778",
            "PaperRole": "non_WHISP_candidate_support",
            "Status": "promising_below_minimum_n",
            "Limitation": "N=6 below frozen N>=15 directional gate; map asymmetry direction mixed",
            "AllowedClaim": "alias-resolved LVHIS velocity-field asymmetry is promising but underpowered",
            "ForbiddenClaim": "non-WHISP external validation achieved",
            "NextAction": "expand alias/source coverage before paper-grade claim",
            "Guardrail": GUARDRAIL,
        },
        {
            "FamilyID": "ALFALFA",
            "Family": "Yu 2022 ALFALFA profile asymmetry",
            "JoinedN": "22",
            "PrimaryMetric": "Pearson_Af=0.145935541;AUC_high_low=0.472222222",
            "PaperRole": "broad_profile_asymmetry_control",
            "Status": "weak_or_non_directional",
            "Limitation": "profile asymmetry does not show a clean directional W_tau_eff relation",
            "AllowedClaim": "ALFALFA profile asymmetry is a useful weak/control readout",
            "ForbiddenClaim": "profile asymmetry confirms W_tau_eff direction",
            "NextAction": "retain_as_negative_or_mixed_control",
            "Guardrail": GUARDRAIL,
        },
        {
            "FamilyID": "HALOGAS",
            "Family": "HALOGAS moment/linewidth proxy",
            "JoinedN": "5",
            "PrimaryMetric": "Pearson=0.216413317;AUC=0.500000000",
            "PaperRole": "small_overlap_control",
            "Status": "weak_control_only",
            "Limitation": "N=5 and median-split AUC is null",
            "AllowedClaim": "HALOGAS does not currently provide strong directional support",
            "ForbiddenClaim": "HALOGAS validates W_tau_eff",
            "NextAction": "do_not_center_paper_on_HALOGAS",
            "Guardrail": GUARDRAIL,
        },
        {
            "FamilyID": "THINGS_ROUTE2",
            "Family": "THINGS route2 missing-galaxy expansion",
            "JoinedN": "0_score_ready",
            "PrimaryMetric": "closed_not_score_ready;THINGS_N15_not_reached",
            "PaperRole": "negative_audit_appendix",
            "Status": "closed_not_score_ready",
            "Limitation": "published machine columns not recovered; photometry and solver validation failed before scoring",
            "AllowedClaim": "route2 is a reproducible negative audit and remains not score-ready",
            "ForbiddenClaim": "THINGS N>=15 or route2 paper-grade external validation",
            "NextAction": "exclude_from_positive_evidence; cite as limitation/audit discipline if needed",
            "Guardrail": GUARDRAIL,
        },
    ]


def claim_rows() -> list[dict[str, str]]:
    return [
        {
            "ClaimID": "P2V02_C01",
            "AllowedClaim": "Paper 2 is a diagnostic residual-inference and external-proxy audit, not a Tau Core validation paper.",
            "Evidence": "CORE AUC=0.771008403; multiple external proxy readouts; route2 closed not score-ready",
            "PaperPlacement": "abstract;introduction;discussion",
            "ForbiddenClaim": "Tau Core field detection; TOE evidence; gravity proof",
            "Status": "required",
            "Guardrail": GUARDRAIL,
        },
        {
            "ClaimID": "P2V02_C02",
            "AllowedClaim": "The strongest positive external context is WHISP resolved-HI, with small-overlap caveats.",
            "Evidence": "WHISP resolved N=14 Pearson=0.391218683 AUC=0.714285714",
            "PaperPlacement": "external validation section",
            "ForbiddenClaim": "WHISP alone is paper-grade independent validation",
            "Status": "allowed_with_caveat",
            "Guardrail": GUARDRAIL,
        },
        {
            "ClaimID": "P2V02_C03",
            "AllowedClaim": "Non-WHISP sources are mixed or underpowered and motivate future validation.",
            "Evidence": "LVHIS N=6 promising; ALFALFA N=22 weak; HALOGAS N=5 weak",
            "PaperPlacement": "limitations;roadmap",
            "ForbiddenClaim": "external validation broadly confirmed across catalogs",
            "Status": "required",
            "Guardrail": GUARDRAIL,
        },
        {
            "ClaimID": "P2V02_C04",
            "AllowedClaim": "THINGS route2 is closed as a negative audit, not used as positive evidence.",
            "Evidence": "route2 closure packet; score_ready_recovered=0; photometry policy failed",
            "PaperPlacement": "appendix or limitations",
            "ForbiddenClaim": "THINGS N>=15; route2 score-ready missing galaxies",
            "Status": "required",
            "Guardrail": GUARDRAIL,
        },
    ]


def readiness_rows() -> list[dict[str, str]]:
    return [
        {
            "Area": "Primary SPARC diagnostic",
            "Status": "ready_with_caveats",
            "Evidence": "frozen residual features and null tests exist",
            "BlockingIssue": "",
            "NextAction": "write concise diagnostic framing",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "External validation",
            "Status": "not_paper_grade_as_validation",
            "Evidence": "WHISP positive but small; non-WHISP mixed/underpowered",
            "BlockingIssue": "no independent N>=15 directional family with strong result",
            "NextAction": "frame as external-proxy audit, not validation",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "THINGS route2",
            "Status": "closed_not_score_ready",
            "Evidence": "closure packet",
            "BlockingIssue": "no machine mass-model columns and failed photometry validation",
            "NextAction": "do not use as positive evidence",
            "Guardrail": GUARDRAIL,
        },
        {
            "Area": "Paper 2 manuscript",
            "Status": "outline_ready_needs_rewrite",
            "Evidence": "claim boundary v02 and status board v02",
            "BlockingIssue": "old text may overstate validation",
            "NextAction": "regenerate/rewrite manuscript around v02 claims",
            "Guardrail": GUARDRAIL,
        },
    ]


def decision_rows() -> list[dict[str, str]]:
    return [
        {
            "DecisionID": "P2V02D01",
            "Decision": "paper2_identity",
            "Status": "diagnostic_external_proxy_audit",
            "Rationale": "primary internal signal exists; external catalog support is mixed and route2 is closed",
            "NextAction": "rewrite_paper2_as_cautious_audit_short_paper",
            "Guardrail": GUARDRAIL,
        },
        {
            "DecisionID": "P2V02D02",
            "Decision": "next_work_gate",
            "Status": "manuscript_rewrite_before_more_data_chasing",
            "Rationale": "route2 showed data chasing can be expensive and non-score-ready; current evidence needs clean framing",
            "NextAction": "generate_paper2_v02_manuscript_skeleton_and_update_abstract",
            "Guardrail": GUARDRAIL,
        },
    ]


def write_report(status: list[dict[str, str]], claims: list[dict[str, str]], decisions: list[dict[str, str]]) -> None:
    lines = [
        "# Paper 2 External Validation Status Board v0.2",
        "",
        "This board supersedes the route2-era working status. Route2 is closed as not score-ready; the paper-facing identity is now a cautious diagnostic and external-proxy audit, not a Tau Core validation claim.",
        "",
        "## Family Status",
        "",
    ]
    for row in status:
        lines.append(
            f"- `{row['FamilyID']}`: {row['Status']} ({row['PaperRole']}); metric={row['PrimaryMetric']}."
        )
    lines.extend(["", "## Claim Boundary", ""])
    for row in claims:
        lines.append(f"- `{row['ClaimID']}`: {row['Status']} - {row['AllowedClaim']}")
    lines.extend(["", "## Decisions", ""])
    for row in decisions:
        lines.append(f"- `{row['DecisionID']}`: {row['Status']} -> {row['NextAction']}.")
    lines.extend(
        [
            "",
            "## Bottom Line",
            "",
            "Paper 2 remains meaningful as a reproducible residual-inference audit with cautious external-proxy readouts. It is not yet an independent external-validation paper and must not claim Tau Core validation.",
            "",
            f"Guardrail: `{GUARDRAIL}`",
            "",
        ]
    )
    STATUS_MD.write_text("\n".join(lines), encoding="utf-8")


def update_manifest() -> None:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = set(manifest["files"])
    for path in [STATUS_MD, STATUS_CSV, CLAIMS_CSV, READINESS_CSV, DECISION_CSV]:
        files.add(path.name)
    manifest["files"] = sorted(files)
    manifest["paper2_external_validation_status_v02"] = (
        "route2_closed_paper_identity_diagnostic_external_proxy_audit"
    )
    manifest["paper2_next_gate"] = "generate_paper2_v02_manuscript_skeleton_and_update_abstract"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    status = status_rows()
    claims = claim_rows()
    readiness = readiness_rows()
    decisions = decision_rows()
    write_csv(
        STATUS_CSV,
        status,
        [
            "FamilyID",
            "Family",
            "JoinedN",
            "PrimaryMetric",
            "PaperRole",
            "Status",
            "Limitation",
            "AllowedClaim",
            "ForbiddenClaim",
            "NextAction",
            "Guardrail",
        ],
    )
    write_csv(
        CLAIMS_CSV,
        claims,
        ["ClaimID", "AllowedClaim", "Evidence", "PaperPlacement", "ForbiddenClaim", "Status", "Guardrail"],
    )
    write_csv(
        READINESS_CSV,
        readiness,
        ["Area", "Status", "Evidence", "BlockingIssue", "NextAction", "Guardrail"],
    )
    write_csv(
        DECISION_CSV,
        decisions,
        ["DecisionID", "Decision", "Status", "Rationale", "NextAction", "Guardrail"],
    )
    write_report(status, claims, decisions)
    update_manifest()
    print(STATUS_MD)


if __name__ == "__main__":
    main()
