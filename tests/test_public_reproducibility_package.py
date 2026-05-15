import collections
import csv
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "studies/sparc_residual_disturbance_inference_v01"
PACKET = STUDY / "packet_v01_seed"
PAPER1_INPUTS = (
    ROOT
    / "studies/sparc_residual_coherence_test_v01/paper_packet_v06_distance_balanced"
)


def test_publication_repo_checklist_files_exist():
    required = [
        ROOT / "README.md",
        ROOT / "LICENSE",
        ROOT / "CITATION.cff",
        ROOT / "DATA_NOTICE.md",
        ROOT / "requirements.txt",
        ROOT / "figures/README.md",
        ROOT / "tests",
        STUDY / "README.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_minimal_derived_inputs_exist():
    required = [
        PAPER1_INPUTS / "taucore_specificity_point_map.csv",
        PAPER1_INPUTS / "baseline_score_by_galaxy.csv",
        PAPER1_INPUTS / "scale_matched_pairs.csv",
        PAPER1_INPUTS / "scale_matched_stress.csv",
        PAPER1_INPUTS / "external_evidence_table.csv",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_paper2_packet_referenced_paths_exist():
    required = [
        PACKET / "README.md",
        PACKET / "packet_manifest.json",
        PACKET / "paper2_manuscript_skeleton.md",
        PACKET / "paper2_manuscript_draft.md",
        PACKET / "paper2_final_metric_table.csv",
        PACKET / "paper2_readiness_table.csv",
        PACKET / "paper2_figure_plan.csv",
        PACKET / "paper2_claim_boundary.csv",
        PACKET / "paper2_related_work.md",
        PACKET / "paper2_validation_controls.md",
        PACKET / "paper2_calibration_policy.md",
        PACKET / "s_tau_eff_pilot.md",
        PACKET / "s_tau_eff_point_pilot.csv",
        PACKET / "s_tau_eff_galaxy_summary.csv",
        PACKET / "predictive_s_tau_rule_v01.md",
        PACKET / "predictive_s_tau_rule_v01.csv",
        PACKET / "predictive_s_tau_by_galaxy_v01.csv",
        PACKET / "predictive_s_tau_readout_v01.csv",
        PACKET / "predictive_s_tau_velocity_readout.md",
        PACKET / "predictive_s_tau_velocity_point_readout.csv",
        PACKET / "predictive_s_tau_velocity_galaxy_summary.csv",
        PACKET / "predictive_s_tau_velocity_metric_summary.csv",
        PACKET / "radial_s_tau_rule_v01.md",
        PACKET / "radial_s_tau_rule_v01.csv",
        PACKET / "radial_s_tau_velocity_point_readout.csv",
        PACKET / "radial_s_tau_velocity_galaxy_summary.csv",
        PACKET / "radial_s_tau_velocity_metric_summary.csv",
        PACKET / "path_b_source_only_stau_readout.md",
        PACKET / "path_b_source_only_stau_readout_joined_points.csv",
        PACKET / "things_source_s_tau_velocity_readout.md",
        PACKET / "things_source_s_tau_velocity_point_readout.csv",
        PACKET / "things_source_s_tau_velocity_galaxy_summary.csv",
        PACKET / "things_source_s_tau_velocity_metric_summary.csv",
        PACKET / "things_source_s_tau_failure_audit.md",
        PACKET / "things_source_s_tau_failure_point_audit.csv",
        PACKET / "things_source_s_tau_failure_galaxy_audit.csv",
        PACKET / "things_source_s_tau_failure_metric_summary.csv",
        PACKET / "contextual_s_tau_rule_v01.md",
        PACKET / "contextual_s_tau_rule_v01.csv",
        PACKET / "contextual_s_tau_velocity_point_readout.csv",
        PACKET / "contextual_s_tau_velocity_galaxy_summary.csv",
        PACKET / "contextual_s_tau_velocity_metric_summary.csv",
        PACKET / "integrated_tau_drift_v01.md",
        PACKET / "integrated_tau_drift_point_trace_v01.csv",
        PACKET / "integrated_tau_drift_galaxy_summary_v01.csv",
        PACKET / "integrated_tau_drift_metric_summary_v01.csv",
        PACKET / "history_s_tau_rule_v01.md",
        PACKET / "history_s_tau_rule_v01.csv",
        PACKET / "history_s_tau_velocity_point_readout.csv",
        PACKET / "history_s_tau_velocity_galaxy_summary.csv",
        PACKET / "history_s_tau_velocity_metric_summary.csv",
        PACKET / "tau_core_signal_candidate_v01.md",
        PACKET / "tau_core_signal_candidate_galaxy_summary_v01.csv",
        PACKET / "tau_core_signal_candidate_relation_summary_v01.csv",
        PACKET / "w_tau_eff_field_seed_v01.md",
        PACKET / "w_tau_eff_field_seed_v01.csv",
        PACKET / "w_tau_eff_field_seed_summary_v01.csv",
        PACKET / "w_tau_eff_branch_closure_audit_v01.md",
        PACKET / "w_tau_eff_branch_claim_boundary_v01.csv",
        PACKET / "w_tau_eff_branch_failure_modes_v01.csv",
        PACKET / "w_tau_eff_branch_next_gate_v01.csv",
        PACKET / "tau_core_weight_model_gate_v01.md",
        PACKET / "tau_core_weight_model_gate_v01.csv",
        PACKET / "tau_core_weight_model_evidence_matrix_v01.csv",
        PACKET / "tau_core_weight_model_next_tests_v01.csv",
        PACKET / "source_side_history_proxy_inventory_v01.md",
        PACKET / "source_side_history_proxy_inventory_v01.csv",
        PACKET / "source_side_history_proxy_readiness_v01.csv",
        PACKET / "w_env_obs_proxy_design_v01.md",
        PACKET / "w_env_obs_proxy_design_v01.csv",
        PACKET / "w_env_obs_proxy_rule_freeze_v01.csv",
        PACKET / "w_env_obs_proxy_endpoint_plan_v01.csv",
        PACKET / "proxy_direction_w_tau_eff_readout_v01.md",
        PACKET / "proxy_direction_w_tau_eff_join_v01.csv",
        PACKET / "proxy_direction_w_tau_eff_metric_summary_v01.csv",
        PACKET / "whisp_vaneymeren2011_overlap.csv",
        PACKET / "p07_whisp_w_tau_eff_holdout_v01.md",
        PACKET / "p07_whisp_w_tau_eff_holdout_join_v01.csv",
        PACKET / "p07_whisp_w_tau_eff_holdout_metric_summary_v01.csv",
        PACKET / "w_env_obs_systematics_competition_v01.md",
        PACKET / "w_env_obs_systematics_competition_matrix_v01.csv",
        PACKET / "w_env_obs_systematics_competition_coverage_v01.csv",
        PACKET / "w_env_obs_systematics_competition_readiness_v01.csv",
        PACKET / "systematics_control_things_harmonic_summary_v01.csv",
        PACKET / "systematics_control_littlethings_pressure_summary_v01.csv",
        PACKET / "systematics_control_halogas_linewidth_summary_v01.csv",
        PACKET / "systematics_control_inclination_summary_v01.csv",
        PACKET / "p05_things_non_circular_w_tau_eff_control_v01.md",
        PACKET / "p05_things_non_circular_w_tau_eff_control_join_v01.csv",
        PACKET / "p05_things_non_circular_w_tau_eff_control_metrics_v01.csv",
        PACKET / "p05_things_non_circular_w_tau_eff_control_decision_v01.csv",
        PACKET / "p09_observability_decomposition_v01.md",
        PACKET / "p09_observability_decomposition_join_v01.csv",
        PACKET / "p09_observability_decomposition_metrics_v01.csv",
        PACKET / "p09_observability_decomposition_decision_v01.csv",
        PACKET / "distance_resolution_environment_join_v01.md",
        PACKET / "distance_resolution_environment_join_v01.csv",
        PACKET / "distance_resolution_environment_metrics_v01.csv",
        PACKET / "distance_resolution_environment_decision_v01.csv",
        PACKET / "multivariable_no_velocity_stress_v01.md",
        PACKET / "multivariable_no_velocity_stress_join_v01.csv",
        PACKET / "multivariable_no_velocity_stress_metrics_v01.csv",
        PACKET / "multivariable_no_velocity_stress_decision_v01.csv",
        PACKET / "observer_distance_hypothesis_gate_v01.md",
        PACKET / "observer_distance_hypothesis_claim_boundary_v01.csv",
        PACKET / "observer_distance_hypothesis_validation_plan_v01.csv",
        PACKET / "observer_distance_hypothesis_readiness_v01.csv",
        PACKET / "observer_distance_whisp_external_validation_v01.md",
        PACKET / "observer_distance_whisp_external_validation_join_v01.csv",
        PACKET / "observer_distance_whisp_external_validation_metrics_v01.csv",
        PACKET / "observer_distance_whisp_external_validation_decision_v01.csv",
        PACKET / "external_validation_status_board_v01.md",
        PACKET / "external_validation_status_board_v01.csv",
        PACKET / "external_validation_status_decision_v01.csv",
        PACKET / "expanded_external_validation_targets_v01.md",
        PACKET / "expanded_external_validation_targets_v01.csv",
        PACKET / "expanded_external_validation_pass_fail_v01.csv",
        PACKET / "external_source_acquisition_plan_v01.md",
        PACKET / "external_source_acquisition_plan_v01.csv",
        PACKET / "external_source_required_fields_v01.csv",
        PACKET / "external_source_download_manifest_v01.md",
        PACKET / "external_source_download_manifest_v01.csv",
        PACKET / "halogas_zenodo_file_index_v01.csv",
        PACKET / "halogas_candidate_moment_downloads_v01.md",
        PACKET / "halogas_candidate_moment_downloads_v01.csv",
        PACKET / "source_alias_crossmatch_v01.md",
        PACKET / "source_alias_crossmatch_v01.csv",
        PACKET / "halogas_moment_features_v01.md",
        PACKET / "halogas_moment_feature_summary_v01.csv",
        PACKET / "halogas_moment_w_tau_eff_join_v01.csv",
        PACKET / "halogas_moment_proxy_readout_v01.md",
        PACKET / "halogas_moment_proxy_metrics_v01.csv",
        PACKET / "halogas_moment_proxy_decision_v01.csv",
        PACKET / "things_table3_expanded_overlap_v01.md",
        PACKET / "things_trachternach2008_table3_v01.csv",
        PACKET / "things_table3_w_tau_eff_overlap_v01.csv",
        PACKET / "things_table3_w_tau_eff_metrics_v01.csv",
        PACKET / "things_table3_expansion_decision_v01.csv",
        PACKET / "reynolds2020_asymmetry_crossmatch_v01.md",
        PACKET / "reynolds2020_vizier_download_manifest_v01.csv",
        PACKET / "reynolds2020_asymmetry_catalog_v01.csv",
        PACKET / "reynolds2020_asymmetry_w_tau_eff_crossmatch_v01.csv",
        PACKET / "reynolds2020_asymmetry_crossmatch_metrics_v01.csv",
        PACKET / "reynolds2020_asymmetry_crossmatch_decision_v01.csv",
        PACKET / "reynolds2020_lvh_alias_resolved_crossmatch_v01.md",
        PACKET / "lvhis_database_download_manifest_v01.csv",
        PACKET / "lvhis_alias_resolution_v01.csv",
        PACKET / "reynolds2020_lvh_alias_resolved_w_tau_eff_crossmatch_v01.csv",
        PACKET / "reynolds2020_lvh_alias_resolved_metrics_v01.csv",
        PACKET / "reynolds2020_lvh_alias_resolved_decision_v01.csv",
        PACKET / "reynolds2020_coverage_ceiling_audit_v01.md",
        PACKET / "reynolds2020_coverage_ceiling_audit_v01.csv",
        PACKET / "reynolds2020_coverage_ceiling_next_actions_v01.csv",
        PACKET / "reynolds2020_seed_expansion_freeze_v01.md",
        PACKET / "reynolds2020_seed_expansion_policy_v01.csv",
        PACKET / "reynolds2020_seed_expansion_candidate_queue_v01.csv",
        PACKET / "reynolds2020_seed_expansion_gate_v01.csv",
        PACKET / "reynolds2020_sparc_rotmod_availability_audit_v01.md",
        PACKET / "reynolds2020_sparc_rotmod_availability_v01.csv",
        PACKET / "reynolds2020_sparc_rotmod_availability_summary_v01.csv",
        PACKET / "reynolds2020_sparc_rotmod_availability_decision_v01.csv",
        PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_v01.md",
        PACKET / "yu2022_alfalfa_download_manifest_v01.csv",
        PACKET / "yu2022_alfalfa_profile_asymmetry_catalog_v01.csv",
        PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_v01.csv",
        PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_summary_v01.csv",
        PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_decision_v01.csv",
        PACKET / "yu2022_alfalfa_seed_expansion_freeze_v01.md",
        PACKET / "yu2022_alfalfa_seed_expansion_policy_v01.csv",
        PACKET / "yu2022_alfalfa_seed_expansion_queue_v01.csv",
        PACKET / "yu2022_alfalfa_seed_expansion_gate_v01.csv",
        PACKET / "yu2022_alfalfa_expanded_w_tau_eff_scoring_v01.md",
        PACKET / "yu2022_alfalfa_expanded_w_tau_eff_point_trace_v01.csv",
        PACKET / "yu2022_alfalfa_expanded_w_tau_eff_scores_v01.csv",
        PACKET / "yu2022_alfalfa_expanded_w_tau_eff_summary_v01.csv",
        PACKET / "yu2022_alfalfa_expanded_w_tau_eff_decision_v01.csv",
        PACKET / "yu2022_alfalfa_af_ac_directional_readout_v01.md",
        PACKET / "yu2022_alfalfa_af_ac_w_tau_eff_join_v01.csv",
        PACKET / "yu2022_alfalfa_af_ac_w_tau_eff_metrics_v01.csv",
        PACKET / "yu2022_alfalfa_af_ac_w_tau_eff_decision_v01.csv",
        PACKET / "spatial_kinematic_proxy_next_gate_v01.md",
        PACKET / "spatial_kinematic_proxy_next_gate_matrix_v01.csv",
        PACKET / "spatial_kinematic_proxy_next_gate_decision_v01.csv",
        PACKET / "whisp_expanded_w_tau_eff_readout_v01.md",
        PACKET / "whisp_expanded_w_tau_eff_readout_join_v01.csv",
        PACKET / "whisp_expanded_w_tau_eff_readout_metrics_v01.csv",
        PACKET / "whisp_expanded_w_tau_eff_readout_decision_v01.csv",
        PACKET / "whisp_holwerda2011_morphology_readout_v01.md",
        PACKET / "whisp_holwerda2011_download_manifest_v01.csv",
        PACKET / "whisp_holwerda2011_morphology_catalog_v01.csv",
        PACKET / "whisp_holwerda2011_w_tau_eff_join_v01.csv",
        PACKET / "whisp_holwerda2011_w_tau_eff_metrics_v01.csv",
        PACKET / "whisp_holwerda2011_w_tau_eff_decision_v01.csv",
        PACKET / "things_control_gate_v01.md",
        PACKET / "things_expanded_score_resolver_audit_v01.csv",
        PACKET / "things_vs_whisp_control_matrix_v01.csv",
        PACKET / "things_control_gate_decision_v01.csv",
        PACKET / "things_table3_expanded_w_tau_eff_v01.md",
        PACKET / "things_table3_expanded_w_tau_eff_point_trace_v01.csv",
        PACKET / "things_table3_expanded_w_tau_eff_scores_v01.csv",
        PACKET / "things_table3_expanded_w_tau_eff_summary_v01.csv",
        PACKET / "things_table3_expanded_w_tau_eff_decision_v01.csv",
        PACKET / "things_table3_expanded_control_readout_v01.md",
        PACKET / "things_table3_expanded_control_readout_join_v01.csv",
        PACKET / "things_table3_expanded_control_readout_metrics_v01.csv",
        PACKET / "things_table3_expanded_control_readout_decision_v01.csv",
        PACKET / "things_missing_rotmod_acquisition_audit_v01.md",
        PACKET / "things_missing_rotmod_acquisition_audit_v01.csv",
        PACKET / "things_missing_rotmod_acquisition_plan_v01.csv",
        PACKET / "things_missing_mass_model_source_probe_v01.md",
        PACKET / "things_missing_mass_model_source_probe_v01.csv",
        PACKET / "things_missing_mass_model_source_probe_decision_v01.csv",
        PACKET / "things_mass_model_recovery_gate_v01.md",
        PACKET / "things_mass_model_recovery_gate_v01.csv",
        PACKET / "things_mass_model_route2_reconstruction_plan_v01.csv",
        PACKET / "things_mass_model_recovery_gate_decision_v01.csv",
        PACKET / "things_route2_mass_model_reconstruction_protocol_v01.md",
        PACKET / "things_route2_required_inputs_v01.csv",
        PACKET / "things_route2_frozen_rules_v01.csv",
        PACKET / "things_route2_scoring_gate_v01.csv",
        PACKET / "things_route2_input_inventory_v01.md",
        PACKET / "things_route2_input_inventory_v01.csv",
        PACKET / "things_route2_input_download_manifest_v01.csv",
        PACKET / "things_route2_input_inventory_gate_v01.csv",
        PACKET / "things_route2_primary_input_staging_v01.md",
        PACKET / "things_route2_primary_input_staging_manifest_v01.csv",
        PACKET / "things_route2_primary_input_staging_gate_v01.csv",
        PACKET / "things_route2_fits_readiness_v01.md",
        PACKET / "things_route2_fits_header_readiness_v01.csv",
        PACKET / "things_route2_component_derivation_readiness_gate_v01.csv",
        PACKET / "things_route2_geometry_solver_protocol_v01.md",
        PACKET / "things_route2_geometry_policy_v01.csv",
        PACKET / "things_route2_surface_density_conversion_policy_v01.csv",
        PACKET / "things_route2_velocity_solver_policy_v01.csv",
        PACKET / "things_route2_geometry_solver_gate_v01.csv",
        PACKET / "things_route2_solver_validation_gate_v01.md",
        PACKET / "things_route2_solver_validation_targets_v01.csv",
        PACKET / "things_route2_solver_validation_requirements_v01.csv",
        PACKET / "things_route2_solver_validation_gate_v01.csv",
        PACKET / "things_route2_solver_validation_input_staging_v01.md",
        PACKET / "things_route2_solver_validation_input_staging_manifest_v01.csv",
        PACKET / "things_route2_solver_validation_input_staging_gate_v01.csv",
        PACKET / "things_route2_solver_validation_fits_v01.md",
        PACKET / "things_route2_solver_validation_fits_header_v01.csv",
        PACKET / "things_route2_solver_validation_fits_gate_v01.csv",
        PACKET / "things_route2_validation_surface_profiles_v01.md",
        PACKET / "things_route2_validation_surface_profiles_v01.csv",
        PACKET / "things_route2_validation_surface_profile_summary_v01.csv",
        PACKET / "things_route2_validation_surface_profile_gate_v01.csv",
        PACKET / "things_route2_validation_surface_density_v01.md",
        PACKET / "things_route2_validation_surface_density_profiles_v01.csv",
        PACKET / "things_route2_validation_beam_conversion_audit_v01.csv",
        PACKET / "things_route2_validation_surface_density_summary_v01.csv",
        PACKET / "things_route2_validation_surface_density_gate_v01.csv",
        PACKET / "things_route2_velocity_solver_validation_gate_v01.md",
        PACKET / "things_route2_validation_sparc_surface_profile_join_v01.csv",
        PACKET / "things_route2_validation_sparc_surface_profile_metrics_v01.csv",
        PACKET / "things_route2_velocity_solver_validation_gate_v01.csv",
        PACKET / "residual_feature_table.csv",
        PACKET / "residual_disturbance_score_v01.csv",
        PACKET / "residual_inference_loogo_metric_summary.csv",
        PACKET / "residual_inference_projection_rms_error_audit.csv",
        PACKET / "residual_inference_projection_rms_error_summary.csv",
        ROOT / "figures/paper2_projection_rms_distribution.svg",
        ROOT / "figures/paper2_baseline_auc_comparison.svg",
        ROOT / "figures/paper2_error_audit.svg",
        ROOT / "figures/paper2_distance_stress.svg",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_final_metrics_and_claim_boundaries_are_guardrailed():
    with (PACKET / "paper2_final_metric_table.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["Projection_RMS_LOOGO"]["Value"] == "0.771008403"
    assert metrics["Projection_RMS_shuffle_null_p"]["Value"] == "0.002000000"
    assert metrics["Newtonian_Baryonic_RMS_LOOGO_AUC"]["Value"] == "0.506302521"
    assert "diagnostic_class_recovery_not_tau_core_validation" in {
        row["Guardrail"] for row in metrics.values()
    }

    manuscript = (PACKET / "paper2_manuscript_skeleton.md").read_text(encoding="utf-8")
    assert "not a Tau Core validation claim" in manuscript
    assert "Forbidden: Tau Core validation" in manuscript
    assert "replacement of external labels by residual-only labels" in manuscript

    draft = (PACKET / "paper2_manuscript_draft.md").read_text(encoding="utf-8")
    assert "## 12. Phase II" in draft
    assert "not as a Tau Core validation result" in draft
    assert "does not establish projection-formula uniqueness" in draft


def test_regeneration_scripts_exist_in_expected_order():
    required = [
        STUDY / "make_packet_v01_seed.py",
        STUDY / "make_loogo_validation_v01.py",
        STUDY / "make_classifier_gate_v01.py",
        STUDY / "make_error_audit_v01.py",
        STUDY / "make_paper2_seed_packet.py",
        STUDY / "make_paper2_validation_controls.py",
        STUDY / "make_paper2_calibration_policy.py",
        STUDY / "make_paper2_manuscript_packet.py",
        STUDY / "make_paper2_figures_and_draft.py",
        STUDY / "make_s_tau_eff_pilot.py",
        STUDY / "make_predictive_s_tau_rule.py",
        STUDY / "evaluate_predictive_s_tau_velocity.py",
        STUDY / "evaluate_radial_s_tau_rule.py",
        STUDY / "evaluate_things_source_s_tau_velocity.py",
        STUDY / "audit_things_source_s_tau_failure.py",
        STUDY / "evaluate_contextual_s_tau_rule.py",
        STUDY / "make_integrated_tau_drift_v01.py",
        STUDY / "evaluate_history_s_tau_rule.py",
        STUDY / "make_tau_core_signal_candidate_v01.py",
        STUDY / "make_w_tau_eff_field_seed_v01.py",
        STUDY / "make_w_tau_eff_branch_closure_audit_v01.py",
        STUDY / "make_tau_core_weight_model_gate_v01.py",
        STUDY / "make_source_side_history_proxy_inventory_v01.py",
        STUDY / "freeze_w_env_obs_proxy_design_v01.py",
        STUDY / "evaluate_proxy_direction_vs_w_tau_eff_v01.py",
        STUDY / "evaluate_p07_whisp_holdout_v01.py",
        STUDY / "make_w_env_obs_systematics_competition_v01.py",
        STUDY / "evaluate_p05_things_non_circular_control_v01.py",
        STUDY / "evaluate_p09_observability_decomposition_v01.py",
        STUDY / "evaluate_distance_resolution_environment_join_v01.py",
        STUDY / "evaluate_multivariable_no_velocity_stress_v01.py",
        STUDY / "make_observer_distance_hypothesis_gate_v01.py",
        STUDY / "evaluate_observer_distance_whisp_external_validation_v01.py",
        STUDY / "make_external_validation_status_board_v01.py",
        STUDY / "make_expanded_external_validation_targets_v01.py",
        STUDY / "make_external_source_acquisition_plan_v01.py",
        STUDY / "download_external_validation_sources_v01.py",
        STUDY / "download_halogas_candidate_moments_v01.py",
        STUDY / "make_source_alias_crossmatch_v01.py",
        STUDY / "derive_halogas_moment_features_v01.py",
        STUDY / "evaluate_halogas_moment_proxy_v01.py",
        STUDY / "make_things_table3_expanded_overlap_v01.py",
        STUDY / "make_reynolds2020_asymmetry_crossmatch_v01.py",
        STUDY / "make_lvh_alias_resolved_reynolds2020_crossmatch_v01.py",
        STUDY / "make_reynolds2020_coverage_ceiling_audit_v01.py",
        STUDY / "make_reynolds2020_seed_expansion_freeze_v01.py",
        STUDY / "audit_reynolds2020_sparc_rotmod_availability_v01.py",
        STUDY / "audit_yu2022_alfalfa_profile_asymmetry_coverage_v01.py",
        STUDY / "make_yu2022_alfalfa_seed_expansion_freeze_v01.py",
        STUDY / "score_yu2022_alfalfa_expanded_w_tau_eff_v01.py",
        STUDY / "evaluate_yu2022_alfalfa_af_ac_directional_readout_v01.py",
        STUDY / "make_spatial_kinematic_proxy_next_gate_v01.py",
        STUDY / "evaluate_whisp_expanded_w_tau_eff_readout_v01.py",
        STUDY / "evaluate_whisp_holwerda2011_morphology_readout_v01.py",
        STUDY / "make_things_expanded_resolver_control_gate_v01.py",
        STUDY / "score_things_table3_expanded_w_tau_eff_v01.py",
        STUDY / "evaluate_things_table3_expanded_control_readout_v01.py",
        STUDY / "make_things_missing_rotmod_acquisition_audit_v01.py",
        STUDY / "make_things_missing_source_probe_v01.py",
        STUDY / "make_things_mass_model_recovery_gate_v01.py",
        STUDY / "freeze_things_route2_mass_model_protocol_v01.py",
        STUDY / "make_things_route2_input_inventory_v01.py",
        STUDY / "stage_things_route2_primary_inputs_v01.py",
        STUDY / "audit_things_route2_fits_readiness_v01.py",
        STUDY / "freeze_things_route2_geometry_solver_v01.py",
        STUDY / "make_things_route2_solver_validation_gate_v01.py",
        STUDY / "stage_things_route2_solver_validation_inputs_v01.py",
        STUDY / "audit_things_route2_solver_validation_fits_v01.py",
        STUDY / "derive_things_route2_validation_surface_profiles_v01.py",
        STUDY / "convert_things_route2_validation_surface_density_v01.py",
        STUDY / "validate_things_route2_surface_profiles_against_sparc_v01.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert missing == []


def test_raw_sparc_inputs_are_not_tracked():
    if not (ROOT / ".git").exists():
        return
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    tracked_paths = set(result.stdout.splitlines())
    forbidden = [
        "data/external/SPARC_Table1.txt",
        "data/raw/sparc_zenodo_16284118/Rotmod_LTG.zip",
    ]
    assert not any(path in tracked_paths for path in forbidden)
    assert not any(path.startswith("data/sparc/Rotmod_LTG/") for path in tracked_paths)


def test_effective_s_tau_pilot_is_diagnostic_and_not_predictive():
    with (PACKET / "s_tau_eff_galaxy_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    a_values = [
        float(row["Median_S_tau_eff_clipped"])
        for row in rows
        if row["Class"] == "A"
    ]
    c_values = [
        float(row["Median_S_tau_eff_clipped"])
        for row in rows
        if row["Class"] == "C"
    ]
    assert round(sorted(a_values)[len(a_values) // 2], 9) == 1.093121010
    assert round((sorted(c_values)[13] + sorted(c_values)[14]) / 2, 9) == 0.888249933
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "derived_from_vobs_not_heldout_prediction"
    }

    text = (PACKET / "s_tau_eff_pilot.md").read_text(encoding="utf-8")
    assert "`S_tau=1` is the old TPG/projection baseline" in text
    assert "not a predictive model yet" in text
    assert "without using the target residual" in text


def test_predictive_s_tau_rule_is_frozen_without_target_leakage():
    with (PACKET / "predictive_s_tau_rule_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rules = list(csv.DictReader(handle))
    assert len(rules) == 9
    assert {row["AllowedInputs"] for row in rules} == {"EvidenceType;Confidence"}
    assert {row["ForbiddenInputs"] for row in rules} == {
        "Vobs;Vbar;Projection_RMS;residuals;S_tau_eff;Class"
    }
    assert {row["InterpretationGuardrail"] for row in rules} == {
        "frozen_source_side_rule_not_fit_to_s_tau_eff"
    }

    with (PACKET / "predictive_s_tau_readout_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    assert {row["ReadoutUse"] for row in rows} == {
        "post_freeze_diagnostic_only_not_rule_training"
    }

    predicted = [float(row["Predicted_S_tau_source_v01"]) for row in rows]
    readout = [float(row["Median_S_tau_eff_clipped_ReadoutOnly"]) for row in rows]
    mae_rule = sum(abs(a - b) for a, b in zip(predicted, readout)) / len(rows)
    mae_baseline = sum(abs(1.0 - value) for value in readout) / len(rows)
    assert round(mae_rule, 9) == 0.337389701
    assert round(mae_baseline, 9) == 0.358271634

    text = (PACKET / "predictive_s_tau_rule_v01.md").read_text(encoding="utf-8")
    assert "Forbidden inputs: `Vobs`, `Vbar`, residuals" in text
    assert "Pearson(predicted source S_tau, empirical S_tau_eff): 0.171323258" in text
    assert "not a fitted improvement over TPG" in text


def test_predictive_s_tau_velocity_readout_is_no_refit_and_mixed():
    with (PACKET / "predictive_s_tau_velocity_metric_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Subset"]: row for row in csv.DictReader(handle)}
    assert set(rows) == {"all", "A", "C"}
    assert rows["all"]["MedianDeltaRMS_SourceMinusS1"] == "-0.003098856"
    assert rows["all"]["FractionGalaxiesImproved"] == "0.511111111"
    assert rows["A"]["MedianDeltaRMS_SourceMinusS1"] == "-0.003098856"
    assert rows["C"]["MedianDeltaRMS_SourceMinusS1"] == "0.007165785"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "velocity_residual_readout_not_refit"
    }

    with (PACKET / "predictive_s_tau_velocity_galaxy_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        galaxies = list(csv.DictReader(handle))
    assert len(galaxies) == 45
    assert {row["InterpretationGuardrail"] for row in galaxies} == {
        "source_rule_vs_s_tau1_no_refit"
    }

    text = (PACKET / "predictive_s_tau_velocity_readout.md").read_text(
        encoding="utf-8"
    )
    assert "No coefficients are refit" in text
    assert "weak or mixed result" in text
    assert "radial or kinematic source information" in text


def test_radial_s_tau_rule_is_frozen_and_still_caveated_for_c_systems():
    with (PACKET / "radial_s_tau_rule_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rules = list(csv.DictReader(handle))
    assert len(rules) == 5
    assert {row["AllowedInputs"] for row in rules} == {
        "EvidenceType;Confidence;RadiusFraction;aN_over_a0"
    }
    assert {row["ForbiddenInputs"] for row in rules} == {
        "Vobs;Vbar;Projection_RMS;residuals;S_tau_eff;Class"
    }

    with (PACKET / "radial_s_tau_velocity_metric_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Subset"]: row for row in csv.DictReader(handle)}
    assert rows["all"]["MedianDeltaRMS_RadialMinusS1"] == "-0.010837261"
    assert rows["all"]["FractionGalaxiesImproved"] == "0.555555556"
    assert rows["A"]["MedianDeltaRMS_RadialMinusS1"] == "-0.010837261"
    assert rows["C"]["MedianDeltaRMS_RadialMinusS1"] == "0.006546441"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "radial_velocity_residual_readout_not_refit"
    }

    text = (PACKET / "radial_s_tau_rule_v01.md").read_text(encoding="utf-8")
    assert "does not use `Vobs`, residuals, or `S_tau_eff`" in text
    assert "leakage-controlled radial heuristic" in text


def test_things_source_s_tau_velocity_gate_is_small_overlap_and_no_refit():
    with (PACKET / "path_b_source_only_stau_readout_joined_points.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        source_rows = list(csv.DictReader(handle))
    assert len(source_rows) == 245
    assert {row["ReadoutStatus"] for row in source_rows} == {
        "source_only_bounded_stau_sensitivity_not_model_selection"
    }
    assert {
        row["GalaxyName"] for row in source_rows
    } == {"DDO154", "NGC2366", "NGC2403", "NGC2976", "NGC3198", "NGC5055", "NGC7331"}

    with (PACKET / "things_source_s_tau_velocity_point_readout.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        point_rows = list(csv.DictReader(handle))
    assert len(point_rows) == 245
    assert {row["InterpretationGuardrail"] for row in point_rows} == {
        "things_source_s_tau_velocity_readout_no_refit_not_validation"
    }
    assert max(float(row["JoinRadiusDeltaKpc"]) for row in point_rows) == 0.0

    with (PACKET / "things_source_s_tau_velocity_metric_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Subset"]: row for row in csv.DictReader(handle)}
    assert set(rows) == {"all", "A", "C"}
    assert rows["all"]["NGalaxies"] == "7"
    assert rows["all"]["MedianDeltaRMS_SourcePercentileMinusS1"] == "0.136344406"
    assert rows["all"]["FractionGalaxiesImprovedPercentile"] == "0.285714286"
    assert rows["all"]["MedianDeltaRMS_SourceLogMinusS1"] == "0.207599642"
    assert rows["all"]["FractionGalaxiesImprovedLog"] == "0.000000000"
    assert rows["C"]["MedianDeltaRMS_SourcePercentileMinusS1"] == "0.014173140"
    assert rows["C"]["MedianDeltaRMS_SourceLogMinusS1"] == "0.022111705"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "things_source_s_tau_velocity_readout_no_refit_not_validation"
    }

    text = (PACKET / "things_source_s_tau_velocity_readout.md").read_text(
        encoding="utf-8"
    )
    assert "does not select one by outcome" in text
    assert "not external validation and not a Tau Core proof" in text


def test_things_source_s_tau_failure_audit_explains_direction_without_rule_selection():
    with (PACKET / "things_source_s_tau_failure_point_audit.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        points = list(csv.DictReader(handle))
    assert len(points) == 245
    assert {row["InterpretationGuardrail"] for row in points} == {
        "post_outcome_failure_diagnostic_not_rule_selection"
    }

    with (PACKET / "things_source_s_tau_failure_metric_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Group"]: row for row in csv.DictReader(handle)}
    assert rows["all"]["MedianDeltaAbsError_SourcePercentileMinusS1"] == "0.255945686"
    assert rows["all"]["MedianDeltaAbsError_SourceLogMinusS1"] == "0.528276275"
    assert rows["all"]["FractionPercentileTooLow"] == "0.751020408"
    assert rows["all"]["FractionLogTooLow"] == "0.889795918"
    assert rows["all"]["PearsonStress_EmpiricalS_tau_eff"] == "-0.325117821"
    assert rows["C"]["MedianDeltaAbsError_SourcePercentileMinusS1"] == "-0.127651156"
    assert rows["radius_outer"]["FractionLogTooLow"] == "1.000000000"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "post_outcome_failure_diagnostic_not_rule_selection"
    }

    text = (PACKET / "things_source_s_tau_failure_audit.md").read_text(
        encoding="utf-8"
    )
    assert "must not be used to choose a new rule" in text
    assert "stress magnitude alone is therefore an incomplete proxy" in text


def test_contextual_s_tau_rule_is_conservative_and_hypothesis_generating():
    with (PACKET / "contextual_s_tau_rule_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rules = list(csv.DictReader(handle))
    assert len(rules) == 9
    assert {row["AllowedInputs"] for row in rules} == {
        "RadiusFraction;aN_over_a0;StressDispersionOverRotationScale"
    }
    assert {row["ForbiddenInputs"] for row in rules} == {
        "Vobs;Vbar;residuals;S_tau_eff;Class;outcome_selected_mapping"
    }
    assert {row["InterpretationGuardrail"] for row in rules} == {
        "contextual_s_tau_rule_post_audit_candidate_not_validation"
    }

    with (PACKET / "contextual_s_tau_velocity_point_readout.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        points = list(csv.DictReader(handle))
    assert len(points) == 245
    s_values = [float(row["Predicted_S_tau_contextual_v01"]) for row in points]
    assert min(s_values) >= 0.88
    assert max(s_values) <= 1.12

    with (PACKET / "contextual_s_tau_velocity_metric_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Subset"]: row for row in csv.DictReader(handle)}
    assert rows["all"]["NGalaxies"] == "7"
    assert rows["all"]["MedianDeltaRMS_ContextualMinusS1"] == "0.002491356"
    assert rows["all"]["FractionGalaxiesImproved"] == "0.428571429"
    assert rows["A"]["MedianDeltaRMS_ContextualMinusS1"] == "-0.004336262"
    assert rows["C"]["MedianDeltaRMS_ContextualMinusS1"] == "0.009241461"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "contextual_s_tau_rule_post_audit_candidate_not_validation"
    }

    text = (PACKET / "contextual_s_tau_rule_v01.md").read_text(encoding="utf-8")
    assert "post-audit candidate, not validation" in text
    assert "held-out source-family gate" in text


def test_integrated_tau_drift_supports_history_dependent_diagnostic_gate():
    with (PACKET / "integrated_tau_drift_point_trace_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        points = list(csv.DictReader(handle))
    assert len(points) == 926
    assert {row["InterpretationGuardrail"] for row in points} == {
        "signed_residual_drift_diagnostic_not_predictive_s_tau_rule"
    }

    with (PACKET / "integrated_tau_drift_galaxy_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        galaxies = list(csv.DictReader(handle))
    assert len(galaxies) == 45
    assert {row["InterpretationGuardrail"] for row in galaxies} == {
        "signed_residual_drift_diagnostic_not_predictive_s_tau_rule"
    }

    with (PACKET / "integrated_tau_drift_metric_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {(row["Group"], row["Metric"]): row for row in csv.DictReader(handle)}
    assert rows[("all", "AbsFinalMeanSignedResidual")]["AUC_C_higher"] == "0.783613445"
    assert rows[("all", "MaxAbsCumulativeMeanResidual")]["AUC_C_higher"] == "0.670168067"
    assert rows[("all", "SignImbalance")]["AUC_C_higher"] == "0.685924370"
    assert rows[("all", "MaxSameSignRunFraction")]["AUC_C_higher"] == "0.710084034"
    assert rows[("A", "AbsFinalMeanSignedResidual")]["Median"] == "0.070366381"
    assert rows[("C", "AbsFinalMeanSignedResidual")]["Median"] == "0.173436672"
    assert rows[("A", "MaxSameSignRunFraction")]["Median"] == "0.750000000"
    assert rows[("C", "MaxSameSignRunFraction")]["Median"] == "0.970588235"

    text = (PACKET / "integrated_tau_drift_v01.md").read_text(encoding="utf-8")
    assert "cumulative radial drift rather than pointwise random scatter" in text
    assert "integrated or history-dependent quantity" in text


def test_history_s_tau_rule_uses_inner_residual_history_and_improves_readout():
    with (PACKET / "history_s_tau_rule_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rules = list(csv.DictReader(handle))
    assert len(rules) == 4
    assert {row["AllowedInputs"] for row in rules} == {
        "inner_radius_signed_TPG_residual_history"
    }
    assert {row["ForbiddenInputs"] for row in rules} == {
        "current_point_residual;future_points;S_tau_eff;Class;external_label"
    }
    assert {row["InterpretationGuardrail"] for row in rules} == {
        "causal_inner_residual_history_readout_not_external_prediction"
    }

    with (PACKET / "history_s_tau_velocity_point_readout.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        points = list(csv.DictReader(handle))
    assert len(points) == 926
    s_values = [float(row["Predicted_S_tau_history_v01"]) for row in points]
    assert min(s_values) >= 0.5
    assert max(s_values) <= 1.5
    first_points = [row for row in points if row["PointIndex"] == "1"]
    assert {row["HistoryStatePriorMeanSignedResidual"] for row in first_points} == {
        "0.000000000"
    }

    with (PACKET / "history_s_tau_velocity_metric_summary.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Subset"]: row for row in csv.DictReader(handle)}
    assert rows["all"]["MedianDeltaRMS_HistoryMinusS1"] == "-0.016862038"
    assert rows["all"]["FractionGalaxiesImproved"] == "0.933333333"
    assert rows["A"]["MedianDeltaRMS_HistoryMinusS1"] == "-0.008566997"
    assert rows["A"]["FractionGalaxiesImproved"] == "0.823529412"
    assert rows["C"]["MedianDeltaRMS_HistoryMinusS1"] == "-0.042417618"
    assert rows["C"]["FractionGalaxiesImproved"] == "1.000000000"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "causal_inner_residual_history_readout_not_external_prediction"
    }

    text = (PACKET / "history_s_tau_rule_v01.md").read_text(encoding="utf-8")
    assert "current point residual, future points" in text
    assert "source-side proxy for the history state" in text


def test_tau_core_signal_candidate_is_framed_without_attribution_claim():
    with (PACKET / "tau_core_signal_candidate_galaxy_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        galaxies = list(csv.DictReader(handle))
    assert len(galaxies) == 45
    assert {row["InterpretationGuardrail"] for row in galaxies} == {
        "tau_core_signal_candidate_not_attribution_or_proof"
    }

    with (PACKET / "tau_core_signal_candidate_relation_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Relation"]: row for row in csv.DictReader(handle)}
    assert rows["Projection_RMS__vs__TauCoreSignalCandidateScore_v01"]["Pearson"] == "0.731059386"
    assert rows["Projection_RMS__vs__TauCoreSignalCandidateScore_v01"]["RightAUC_C_higher"] == "0.774159664"
    assert rows["AbsFinalMeanSignedResidual__vs__HistoryImprovement_PositiveIsBetter"]["Pearson"] == "0.954744346"
    assert rows["HistoryImprovement_PositiveIsBetter__vs__TauCoreSignalCandidateScore_v01"]["LeftAUC_C_higher"] == "0.762605042"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "tau_core_signal_candidate_not_attribution_or_proof"
    }

    a_scores = [
        float(row["TauCoreSignalCandidateScore_v01"])
        for row in galaxies
        if row["Class"] == "A"
    ]
    c_scores = [
        float(row["TauCoreSignalCandidateScore_v01"])
        for row in galaxies
        if row["Class"] == "C"
    ]
    assert round(sorted(a_scores)[len(a_scores) // 2], 9) == 0.304545455
    assert round((sorted(c_scores)[13] + sorted(c_scores)[14]) / 2, 9) == 0.579545455

    text = (PACKET / "tau_core_signal_candidate_v01.md").read_text(encoding="utf-8")
    assert "TPG prescription already carries the local Tau Core weights" in text
    assert "It does not identify the residual itself with Tau Core" in text
    assert "environment/observer weights" in text
    assert "Attribution requires external source-side predictors or controls" in text


def test_w_tau_eff_field_seed_closes_branch_without_map_claim():
    with (PACKET / "w_tau_eff_field_seed_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    assert {row["MapReadiness"] for row in rows} == {
        "needs_ra_dec_distance_environment_join"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "w_tau_eff_residual_inferred_seed_not_tau_core_field_map"
    }
    assert {row["CandidateConfidenceTier"] for row in rows} == {
        "high_candidate",
        "medium_candidate",
        "low_or_control_candidate",
    }

    with (PACKET / "w_tau_eff_field_seed_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        summary = {row["Group"]: row for row in csv.DictReader(handle)}
    assert summary["all"]["NGalaxies"] == "45"
    assert summary["all"]["Median_W_tau_eff_candidate_score_v01"] == "0.500000000"
    assert summary["A"]["Median_W_tau_eff_candidate_score_v01"] == "0.304545455"
    assert summary["C"]["Median_W_tau_eff_candidate_score_v01"] == "0.579545455"
    assert summary["all"]["NHighCandidate"] == "12"
    assert summary["A"]["NHighCandidate"] == "2"
    assert summary["C"]["NHighCandidate"] == "10"
    assert {row["InterpretationGuardrail"] for row in summary.values()} == {
        "w_tau_eff_residual_inferred_seed_not_tau_core_field_map"
    }

    text = (PACKET / "w_tau_eff_field_seed_v01.md").read_text(encoding="utf-8")
    assert "TPG`: effective baseline carrying local Tau Core weights" in text
    assert "not claim a Tau Core field map" in text
    assert "RA, Dec, distance, distance uncertainty" in text


def test_w_tau_eff_branch_closure_audit_blocks_premature_mapping_claims():
    with (PACKET / "w_tau_eff_branch_claim_boundary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        claims = {row["ClaimID"]: row for row in csv.DictReader(handle)}
    assert claims["C01"]["Status"] == "supported"
    assert claims["C02"]["Status"] == "supported"
    assert claims["C03"]["Status"] == "supported"
    assert claims["C04"]["Status"] == "not_established"
    assert claims["C05"]["Status"] == "not_established"
    assert "W_tau_eff is the Tau Core field" in claims["C04"]["Claim"]
    assert {row["Guardrail"] for row in claims.values()} == {
        "w_tau_eff_branch_closed_not_map_not_tau_core_proof"
    }

    with (PACKET / "w_tau_eff_branch_failure_modes_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        failures = list(csv.DictReader(handle))
    assert len(failures) == 5
    alternatives = {row["AlternativeExplanation"] for row in failures}
    assert "Non-circular or non-equilibrium gas motions" in alternatives
    assert "Observability and resolution bias" in alternatives
    assert "Inclination and deprojection uncertainty" in alternatives
    assert "Baryonic mass-model mismatch" in alternatives
    assert "Environmental galaxy dynamics rather than observer-weight field" in alternatives

    with (PACKET / "w_tau_eff_branch_next_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert set(gates) == {"G01", "G02", "G03", "G04"}
    assert gates["G01"]["Gate"] == "coordinate_distance_join"
    assert gates["G02"]["Gate"] == "systematics_join"
    assert gates["G03"]["Gate"] == "environment_join"
    assert gates["G04"]["Gate"] == "map_null_tests"
    assert "visual sky maps are treated as evidence without null tests" in gates["G04"]["DoNotProceedIf"]

    text = (PACKET / "w_tau_eff_branch_closure_audit_v01.md").read_text(
        encoding="utf-8"
    )
    assert "Closed for definition and seed generation" in text
    assert "Not closed for Tau Core attribution or field mapping" in text
    assert "not with interpretive sky maps" in text


def test_tau_core_weight_model_gate_freezes_next_model_target():
    with (PACKET / "tau_core_weight_model_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        components = {row["ComponentID"]: row for row in csv.DictReader(handle)}
    assert set(components) == {"M01", "M02", "M03", "M04"}
    assert components["M01"]["Symbol"] == "W_local_TPG(R)"
    assert "local Tau Core weights" in components["M01"]["Definition"]
    assert components["M02"]["Symbol"] == "W_env_obs(R)"
    assert "environment_tuning" in components["M01"]["ForbiddenInputs"]
    assert "current_point_residual" in components["M02"]["ForbiddenInputs"]
    assert {row["Guardrail"] for row in components.values()} == {
        "model_gate_not_fit_not_tau_core_proof"
    }

    with (PACKET / "tau_core_weight_model_evidence_matrix_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        evidence = {row["EvidenceID"]: row for row in csv.DictReader(handle)}
    assert evidence["E01"]["Metric"] == "TauCoreSignalCandidateScore_v01 AUC(C higher)=0.774159664"
    assert "all-galaxy improvement fraction=0.933333333" in evidence["E03"]["Metric"]
    assert evidence["E04"]["Metric"] == "Pearson=0.954744346"

    with (PACKET / "tau_core_weight_model_next_tests_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        tests = {row["TestID"]: row for row in csv.DictReader(handle)}
    assert tests["T01"]["NextTest"] == "source_side_history_proxy"
    assert tests["T02"]["NextTest"] == "systematics_competition"
    assert tests["T03"]["NextTest"] == "map_readiness_join"
    assert tests["T04"]["NextTest"] == "heldout_formula_freeze"
    assert "Predeclared proxy" in tests["T01"]["PassCondition"]

    text = (PACKET / "tau_core_weight_model_gate_v01.md").read_text(
        encoding="utf-8"
    )
    assert "TPG carries local Tau Core weights" in text
    assert "S_tau_full(R)=1+g(W_env_obs(R))" in text
    assert "does not prove Tau Core" in text


def test_source_side_history_proxy_inventory_has_no_endpoint_readout():
    with (PACKET / "source_side_history_proxy_inventory_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["ProxyID"]: row for row in csv.DictReader(handle)}
    assert set(rows) == {"P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09"}
    assert rows["P01"]["ReadinessTier"] == "ready_as_broad_prior"
    assert rows["P07"]["ReadinessTier"] == "ready_for_source_family_holdout"
    assert rows["P03"]["ReadinessTier"] == "ready_for_small_heldout_sanity_check"
    assert rows["P09"]["ReadinessTier"] == "control_required"
    assert rows["P01"]["CoverageGalaxies"] == "73"
    assert rows["P07"]["CoverageGalaxies"] == "14"
    assert "TPG_residual" in rows["P01"]["ForbiddenInputs"]
    assert {row["Guardrail"] for row in rows.values()} == {
        "proxy_inventory_only_no_velocity_endpoint_no_rule_selection"
    }

    with (PACKET / "source_side_history_proxy_readiness_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        readiness = {row["ReadinessTier"]: row for row in csv.DictReader(handle)}
    assert readiness["ready_as_broad_prior"]["ProxyIDs"] == "P01"
    assert readiness["ready_for_source_family_holdout"]["ProxyIDs"] == "P07"
    assert readiness["ready_for_small_heldout_sanity_check"]["ProxyIDs"] == "P03;P04"
    assert readiness["control_required"]["ProxyIDs"] == "P09"

    text = (PACKET / "source_side_history_proxy_inventory_v01.md").read_text(
        encoding="utf-8"
    )
    assert "No velocity endpoint is evaluated here" in text
    assert "Ready broad/holdout proxy IDs: P01, P07" in text
    assert "Do not tune a velocity formula from this inventory" in text


def test_w_env_obs_proxy_design_freezes_roles_and_blocks_velocity_endpoint():
    with (PACKET / "w_env_obs_proxy_design_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        design = {row["DesignID"]: row for row in csv.DictReader(handle)}
    assert design["D01"]["ProxyID"] == "P01"
    assert design["D01"]["Role"] == "primary_broad_prior"
    assert design["D02"]["ProxyID"] == "P07"
    assert design["D02"]["Role"] == "source_family_holdout"
    assert design["D03"]["ProxyID"] == "P03"
    assert design["D04"]["ProxyID"] == "P04"
    assert design["D05"]["ProxyID"] == "P09"
    assert "TPG_residual" in design["D01"]["ForbiddenInputs"]
    assert {row["Guardrail"] for row in design.values()} == {
        "proxy_design_frozen_no_endpoint_readout_no_rule_fitting"
    }

    with (PACKET / "w_env_obs_proxy_rule_freeze_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rules = {row["RuleStep"]: row for row in csv.DictReader(handle)}
    assert rules["R01"]["FrozenChoice"] == "P01_primary"
    assert rules["R02"]["FrozenChoice"] == "direction_only_no_coefficients"
    assert rules["R03"]["FrozenChoice"] == "P07_holdout"
    assert rules["R05"]["FrozenChoice"] == "endpoint_blocked"

    with (PACKET / "w_env_obs_proxy_endpoint_plan_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        endpoints = {row["EndpointGate"]: row for row in csv.DictReader(handle)}
    assert endpoints["E01"]["AllowedAfterThisDesign"] == "yes_next"
    assert endpoints["E02"]["AllowedAfterThisDesign"] == "yes_after_E01"
    assert endpoints["E03"]["AllowedAfterThisDesign"] == "no"
    assert endpoints["E03"]["Endpoint"] == "velocity_readout_with_S_tau_full"

    text = (PACKET / "w_env_obs_proxy_design_v01.md").read_text(encoding="utf-8")
    assert "Primary broad prior: `P01`" in text
    assert "No `S_tau_full` coefficient selection" in text
    assert "No velocity endpoint readout" in text


def test_proxy_direction_vs_w_tau_eff_is_positive_without_velocity_endpoint():
    with (PACKET / "proxy_direction_w_tau_eff_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    assert {row["ReadoutUse"] for row in rows} == {
        "frozen_P01_direction_vs_existing_W_tau_eff_no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "proxy_direction_readout_no_velocity_endpoint_no_coefficient_fit"
    }
    assert {row["P01BurdenTier"] for row in rows} == {"low", "high"}

    with (PACKET / "proxy_direction_w_tau_eff_metric_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "45"
    assert metrics["coverage_scored_low_medium_high"]["SecondaryValue"] == "low=17;medium=0;high=28"
    assert metrics["median_score_low"]["Value"] == "0.304545455"
    assert metrics["median_score_high"]["Value"] == "0.579545455"
    assert metrics["auc_high_vs_low_score"]["Value"] == "0.774159664"
    assert metrics["pearson_ordinal_vs_score"]["Value"] == "0.457880425"
    assert {row["InterpretationGuardrail"] for row in metrics.values()} == {
        "proxy_direction_readout_no_velocity_endpoint_no_coefficient_fit"
    }

    text = (PACKET / "proxy_direction_w_tau_eff_readout_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not evaluate velocity residuals" in text
    assert "AUC high-vs-low score: 0.774159664" in text
    assert "must not be promoted to a velocity formula" in text


def test_p07_whisp_holdout_is_positive_but_small_overlap():
    with (PACKET / "p07_whisp_w_tau_eff_holdout_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 10
    assert {row["ReadoutUse"] for row in rows} == {
        "P07_WHISP_source_family_holdout_no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "p07_source_family_holdout_no_velocity_endpoint_no_coefficient_fit"
    }
    assert {row["WHISP_BurdenSplit"] for row in rows} == {"low", "high"}

    with (PACKET / "p07_whisp_w_tau_eff_holdout_metric_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "10"
    assert metrics["pearson_whisp_burden_vs_w_tau_score"]["Value"] == "0.441950994"
    assert metrics["pearson_whisp_burden_vs_abs_w_tau"]["Value"] == "0.530958640"
    assert metrics["median_score_low_whisp_burden"]["Value"] == "0.231818182"
    assert metrics["median_score_high_whisp_burden"]["Value"] == "0.531818182"
    assert metrics["auc_high_vs_low_whisp_burden"]["Value"] == "0.760000000"

    text = (PACKET / "p07_whisp_w_tau_eff_holdout_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not evaluate velocity residuals" in text
    assert "AUC high-vs-low WHISP burden: 0.760000000" in text
    assert "source-family sanity check rather than a final validation" in text


def test_w_env_obs_systematics_competition_blocks_attribution_until_controls():
    with (PACKET / "w_env_obs_systematics_competition_matrix_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        matrix = {row["ControlID"]: row for row in csv.DictReader(handle)}
    assert set(matrix) == {"S01", "S02", "S03", "S04", "S05", "S06"}
    assert matrix["S01"]["ProxyID"] == "P05"
    assert matrix["S01"]["CurrentReadout"] == (
        "Pearson=0.217454567;AUC=0.333333333;Status=does_not_absorb_direction_in_small_overlap"
    )
    assert matrix["S01"]["Decision"] == "does_not_absorb_direction_in_small_overlap"
    assert matrix["S04"]["ProxyID"] == "P09"
    assert matrix["S04"]["CanCompeteNow"] == "summary_only"
    assert matrix["S04"]["CurrentReadout"] == (
        "ReconstructionRiskAUC=0.750000000;ObserverGeometryAUC=0.389328063;"
        "Status=ordinary_observability_risk_competes_with_signal"
    )
    assert matrix["S04"]["Decision"] == "ordinary_observability_risk_competes_with_signal"
    assert matrix["S05"]["CurrentReadout"] == "AUC=0.774159664"
    assert matrix["S06"]["CurrentReadout"] == "AUC=0.760000000;Pearson=0.441950994"
    assert {row["InterpretationGuardrail"] for row in matrix.values()} == {
        "systematics_competition_no_attribution_no_velocity_endpoint"
    }

    with (PACKET / "w_env_obs_systematics_competition_coverage_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        coverage = {row["Family"]: row for row in csv.DictReader(handle)}
    assert coverage["P01_paper1_external_evidence"]["JoinedWithWTauEff"] == "45"
    assert coverage["P07_WHISP_lopsidedness"]["JoinedWithWTauEff"] == "10"
    assert coverage["P05_THINGS_harmonic_non_circular"]["JoinedWithWTauEff"] == "7"
    assert coverage["P06_LITTLE_THINGS_pressure"]["JoinedWithWTauEff"] == "2"
    assert coverage["P08_HALOGAS_linewidth"]["JoinedWithWTauEff"] == "5"
    assert coverage["P09_inclination_systematics"]["JoinedWithWTauEff"] == "binned_summary"

    with (PACKET / "systematics_control_things_harmonic_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        things = list(csv.DictReader(handle))
    assert len(things) == 7
    assert "MeanAbsResidualProjection" not in things[0]
    assert "MeanAbsResidualMONDSimple" not in things[0]
    assert {row["ControlUse"] for row in things} == {
        "published_harmonic_non_circular_control_only"
    }

    with (PACKET / "systematics_control_halogas_linewidth_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        halogas = list(csv.DictReader(handle))
    assert len(halogas) == 5
    assert "MeanAbsResidualProjection" not in halogas[0]
    assert {row["ControlUse"] for row in halogas} == {
        "external_linewidth_stress_control_only"
    }

    with (PACKET / "w_env_obs_systematics_competition_readiness_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        readiness = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert readiness["D01"]["Status"] == "supported_but_not_attributed"
    assert readiness["D02"]["Status"] == "ordinary_observability_risk_now_primary_blocker"
    assert readiness["D03"]["Status"] == "blocked"
    assert readiness["D04"]["NextAction"] == "distance_resolution_environment_join_before_formula"

    text = (PACKET / "w_env_obs_systematics_competition_v01.md").read_text(
        encoding="utf-8"
    )
    assert "The velocity endpoint remains closed" in text
    assert "not a new positive endpoint" in text


def test_p05_things_non_circular_control_is_small_overlap_and_does_not_absorb_signal():
    with (PACKET / "p05_things_non_circular_w_tau_eff_control_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 7
    assert {row["GalaxyName"] for row in rows} == {
        "DDO154",
        "NGC2366",
        "NGC2403",
        "NGC2976",
        "NGC3198",
        "NGC5055",
        "NGC7331",
    }
    assert {row["ReadoutUse"] for row in rows} == {
        "P05_THINGS_non_circular_control_no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "p05_non_circular_control_no_velocity_endpoint_no_attribution"
    }

    with (PACKET / "p05_things_non_circular_w_tau_eff_control_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "7"
    assert metrics["pearson_p05_burden_vs_w_tau_score"]["Value"] == "0.217454567"
    assert metrics["spearman_p05_burden_vs_w_tau_score"]["Value"] == "0.107142857"
    assert metrics["auc_high_vs_low_p05_burden"]["Value"] == "0.333333333"
    assert metrics["pearson_NonCircularAmplitudeOverVmaxPercent_vs_w_tau_score"]["Value"] == "0.518486407"

    with (PACKET / "p05_things_non_circular_w_tau_eff_control_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["P05D01"]["Status"] == "does_not_absorb_direction_in_small_overlap"
    assert decisions["P05D01"]["NextAction"] == "retain_P05_control_but_proceed_to_P09_observability_join"
    assert decisions["P05D02"]["Status"] == "velocity_endpoint_still_closed"

    text = (PACKET / "p05_things_non_circular_w_tau_eff_control_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not use velocity residuals as predictors" in text
    assert "cannot by itself fit or reject a Tau Core formula" in text


def test_p09_observability_decomposition_keeps_observer_channel_but_flags_reconstruction_risk():
    with (PACKET / "p09_observability_decomposition_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    assert {row["ReadoutUse"] for row in rows} == {
        "P09_observability_decomposition_no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "p09_observability_decomposition_not_bias_erasure_not_attribution"
    }
    assert {row["ResidualBlindCheck"] for row in rows} == {"true"}
    assert {row["Class"] for row in rows} == {"A", "C"}

    with (PACKET / "p09_observability_decomposition_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "45"
    assert metrics["pearson_observer_geometry_vs_w_tau_score"]["Value"] == "-0.225721262"
    assert metrics["auc_high_vs_low_observer_geometry"]["Value"] == "0.389328063"
    assert metrics["pearson_reconstruction_risk_vs_w_tau_score"]["Value"] == "0.289724767"
    assert metrics["spearman_reconstruction_risk_vs_w_tau_score"]["Value"] == "0.333959220"
    assert metrics["auc_high_vs_low_reconstruction_risk"]["Value"] == "0.750000000"
    assert metrics["median_score_by_ReconstructionRiskSplit_high"]["Value"] == "0.659090910"
    assert metrics["median_score_by_ReconstructionRiskSplit_low"]["Value"] == "0.327272727"

    with (PACKET / "p09_observability_decomposition_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["P09D01"]["Status"] == "ordinary_observability_risk_competes_with_signal"
    assert decisions["P09D01"]["NextAction"] == "do_not_open_velocity_endpoint_before_distance_resolution_regression"
    assert decisions["P09D02"]["Status"] == "decompose_observability_do_not_delete_it"

    text = (PACKET / "p09_observability_decomposition_v01.md").read_text(
        encoding="utf-8"
    )
    assert "not as something to erase automatically" in text
    assert "observer geometry should not be dismissed as mere nuisance" in text


def test_distance_resolution_environment_join_keeps_formula_endpoint_closed():
    with (PACKET / "distance_resolution_environment_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    assert {row["ReadoutUse"] for row in rows} == {
        "distance_resolution_environment_join_no_formula_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "distance_resolution_environment_control_no_formula_endpoint"
    }
    assert sum(1 for row in rows if row["EnvironmentCuePresent"] == "true") == 15
    assert {row["Class"] for row in rows} == {"A", "C"}

    with (PACKET / "distance_resolution_environment_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "45"
    assert metrics["environment_cue_coverage"]["Value"] == "15"
    assert metrics["pearson_DistanceMpc_vs_w_tau_score"]["Value"] == "-0.329848302"
    assert metrics["spearman_DistanceMpc_vs_w_tau_score"]["Value"] == "-0.447379969"
    assert metrics["auc_high_vs_low_DistanceSplit"]["Value"] == "0.269762846"
    assert metrics["auc_high_vs_low_AngularRadiusProxySplit"]["Value"] == "0.432806324"
    assert metrics["auc_high_vs_low_ReconstructionRiskSplit"]["Value"] == "0.750000000"
    assert metrics["auc_high_vs_low_EnvMaxThetaSplit"]["Value"] == "0.602040816"

    with (PACKET / "distance_resolution_environment_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["DRE01"]["Status"] == "reconstruction_risk_remains_primary_observability_blocker"
    assert decisions["DRE01"]["NextAction"] == "freeze_multivariable_no_velocity_endpoint_stress_test"
    assert decisions["DRE02"]["Status"] == "velocity_endpoint_still_closed"

    text = (PACKET / "distance_resolution_environment_join_v01.md").read_text(
        encoding="utf-8"
    )
    assert "before any velocity formula is opened" in text
    assert "does not select or validate a Tau Core velocity formula" in text


def test_multivariable_no_velocity_stress_supports_observer_distance_hypothesis_only():
    with (PACKET / "multivariable_no_velocity_stress_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 45
    assert {row["ReadoutUse"] for row in rows} == {
        "observer_distance_tau_candidate_stress_no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "multivariable_stress_no_velocity_endpoint_no_formula_selection"
    }
    assert {row["Class"] for row in rows} == {"A", "C"}

    with (PACKET / "multivariable_no_velocity_stress_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "45"
    assert metrics["pearson_tau_distance_raw_vs_w_tau_score"]["Value"] == "0.404324367"
    assert metrics["auc_nearer_vs_farther_tau_distance_raw"]["Value"] == "0.771739130"
    assert metrics[
        "partial_pearson_tau_distance_after_nuisance_vs_score_after_nuisance"
    ]["Value"] == "0.434416486"
    assert metrics["partial_auc_tau_distance_residual_high_vs_low_score_residual"]["Value"] == "0.662000000"
    assert metrics["nuisance_model_r2_for_w_tau_score"]["Value"] == "0.207747757"

    with (PACKET / "multivariable_no_velocity_stress_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["MV01"]["Status"] == "observer_distance_candidate_survives_nuisance_stress"
    assert decisions["MV01"]["NextAction"] == (
        "freeze_as_hypothesis_not_formula_then_seek_external_environment_distance_validation"
    )
    assert decisions["MV02"]["Status"] == "velocity_endpoint_still_closed"

    text = (PACKET / "multivariable_no_velocity_stress_v01.md").read_text(
        encoding="utf-8"
    )
    assert "without opening a velocity endpoint" in text
    assert "does not establish a Tau Core field" in text


def test_observer_distance_hypothesis_gate_freezes_claim_boundary_and_validation_plan():
    with (PACKET / "observer_distance_hypothesis_claim_boundary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        claims = {row["ClaimID"]: row for row in csv.DictReader(handle)}
    assert set(claims) == {"ODC01", "ODC02", "ODC03", "ODC04"}
    assert claims["ODC01"]["Status"] == "supported_as_in_sample_hypothesis"
    assert claims["ODC01"]["Evidence"] == "raw Pearson=0.404324367; raw AUC=0.771739130"
    assert claims["ODC02"]["Status"] == "supported_as_stress_survival"
    assert claims["ODC02"]["Evidence"] == (
        "partial Pearson=0.434416486; partial AUC=0.662000000; "
        "nuisance-only R2=0.207747757"
    )
    assert claims["ODC03"]["Status"] == "not_established"
    assert claims["ODC04"]["Status"] == "blocked"
    assert "velocity formula" in claims["ODC01"]["ForbiddenWording"]
    assert "formula validation" in claims["ODC04"]["ForbiddenWording"]
    assert {row["InterpretationGuardrail"] for row in claims.values()} == {
        "observer_distance_hypothesis_only_no_formula_no_tau_core_proof"
    }

    with (PACKET / "observer_distance_hypothesis_validation_plan_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        validation = {row["ValidationID"]: row for row in csv.DictReader(handle)}
    assert set(validation) == {"ODV01", "ODV02", "ODV03", "ODV04"}
    assert validation["ODV01"]["Target"] == "WHISP overlap"
    assert validation["ODV02"]["EndpointPermission"] == "no_velocity_endpoint"
    assert validation["ODV04"]["EndpointPermission"] == "blocked_until_external_validation"

    with (PACKET / "observer_distance_hypothesis_readiness_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        readiness = {row["ReadinessID"]: row for row in csv.DictReader(handle)}
    assert readiness["ODR01"]["Status"] == "yes_with_guardrails"
    assert readiness["ODR02"]["Status"] == "no"
    assert readiness["ODR03"]["NextAction"] == "observer_distance_external_validation_readout"

    text = (PACKET / "observer_distance_hypothesis_gate_v01.md").read_text(
        encoding="utf-8"
    )
    assert "hypothesis-level result only" in text
    assert "does not claim a Tau Core field detection" in text
    assert "At least one external source-family validation" in text


def test_observer_distance_whisp_external_validation_is_guardrailed():
    with (PACKET / "observer_distance_whisp_external_validation_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 10
    assert {row["Class"] for row in rows} == {"C"}
    assert {row["ReadoutUse"] for row in rows} == {
        "WHISP_observer_distance_external_validation_no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "whisp_external_validation_no_velocity_endpoint_no_formula_selection"
    }

    with (PACKET / "observer_distance_whisp_external_validation_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "10"
    assert metrics["class_coverage"]["Value"] == "C"
    assert metrics["pearson_tau_distance_raw_vs_w_tau_score"]["Value"] == "0.167726020"
    assert metrics["auc_nearer_vs_farther_tau_distance_raw"]["Value"] == "0.560000000"
    assert (
        metrics["partial_pearson_tau_distance_after_whisp_controls"]["Value"]
        == "-0.224079320"
    )
    assert metrics["partial_auc_tau_distance_after_whisp_controls"]["Value"] == "0.360000000"

    with (PACKET / "observer_distance_whisp_external_validation_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["ODW01"]["Status"] == (
        "direction_not_reproduced_in_small_whisp_overlap"
    )
    assert decisions["ODW01"]["NextAction"] == (
        "do_not_promote_observer_distance_hypothesis_before_other_external_checks"
    )
    assert decisions["ODW02"]["Status"] == "velocity_endpoint_still_closed"

    text = (PACKET / "observer_distance_whisp_external_validation_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not open a velocity endpoint" in text
    assert "not class-balanced" in text
    assert "cannot validate a Tau Core field or velocity formula" in text


def test_external_validation_status_board_closes_observer_distance_endpoint():
    with (PACKET / "external_validation_status_board_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["FamilyID"]: row for row in csv.DictReader(handle)}
    assert set(rows) == {"P07", "ODW", "P05", "P06", "P08", "R20", "LVH"}
    assert rows["P07"]["Status"] == "positive_small_source_family_sanity_check"
    assert rows["P07"]["PrimaryMetric"] == "AUC=0.760000000;Pearson=0.441950994"
    assert rows["ODW"]["Status"] == "direction_not_reproduced_in_small_whisp_overlap"
    assert rows["ODW"]["PrimaryMetric"] == (
        "rawPearson=0.167726020;partialPearson=-0.224079320;partialAUC=0.360000000"
    )
    assert rows["P05"]["Status"] == "does_not_absorb_direction_in_small_overlap"
    assert rows["P06"]["Status"] == "too_small_for_directional_validation"
    assert rows["P08"]["Status"] == "weak_small_overlap_control_only"
    assert rows["R20"]["Status"] == "catalog_ingested_exact_overlap_below_minimum_n"
    assert rows["LVH"]["Status"] == "alias_resolution_improves_overlap_but_below_minimum_n"
    assert rows["LVH"]["PrimaryMetric"] == (
        "AmapPearson=-0.233039744;AvelPearson=0.375346400;AvelAUC=0.777777778"
    )
    assert {row["EndpointPermission"] for row in rows.values()} == {
        "no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "external_validation_status_no_velocity_endpoint_no_tau_core_claim"
    }

    with (PACKET / "external_validation_status_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["EVS01"]["Status"] == (
        "mixed_external_validation_supporting_w_tau_direction_not_observer_distance"
    )
    assert decisions["EVS01"]["NextAction"] == (
        "prioritize_non_whisp_THINGS_LITTLE_THINGS_HALOGAS_expansion_before_formula"
    )
    assert decisions["EVS02"]["Status"] == "closed"

    text = (PACKET / "external_validation_status_board_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not open a velocity endpoint" in text
    assert "does not claim a Tau Core field detection" in text
    assert "not for the observer-distance interpretation" in text


def test_expanded_external_validation_targets_freeze_next_data_gate():
    with (PACKET / "expanded_external_validation_targets_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        targets = {row["TargetID"]: row for row in csv.DictReader(handle)}
    assert set(targets) == {"EVT01", "EVT02", "EVT03", "EVT04", "EVT05"}
    assert targets["EVT01"]["SourceFamily"] == "THINGS harmonic velocity-field controls"
    assert targets["EVT01"]["MinimumDirectionalN"] == "12"
    assert targets["EVT01"]["MinimumBalancedClasses"] == "at_least_4_A_and_4_C"
    assert targets["EVT01"]["Priority"] == "high"
    assert targets["EVT04"]["SourceFamily"] == "Non-WHISP resolved HI asymmetry catalogues"
    assert targets["EVT04"]["MinimumDirectionalN"] == "15"
    assert targets["EVT04"]["RoleIfPasses"] == (
        "strongest_near_term_external_validation_candidate"
    )
    assert targets["EVT05"]["Endpoint"] == "observer_distance_hypothesis_stress_only"
    assert targets["EVT05"]["RoleIfFails"] == "park_observer_distance_interpretation"
    assert {row["InterpretationGuardrail"] for row in targets.values()} == {
        "expanded_external_validation_targets_no_velocity_endpoint_no_formula_fit"
    }

    with (PACKET / "expanded_external_validation_pass_fail_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert set(gates) == {"EVG01", "EVG02", "EVG03", "EVG04"}
    assert gates["EVG01"]["CurrentStatus"] == "not_yet_met"
    assert gates["EVG02"]["Blocks"] == "observer_distance_claim"
    assert gates["EVG03"]["CurrentStatus"] == "open"
    assert gates["EVG04"]["CurrentStatus"] == "closed"
    assert gates["EVG04"]["NextAction"] == "keep_velocity_endpoint_closed"

    text = (PACKET / "expanded_external_validation_targets_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not add a velocity endpoint" in text
    assert "does not promote the observer-distance interpretation" in text
    assert "targeted external-data expansion" in text


def test_external_source_acquisition_plan_freezes_sources_and_no_raw_data_policy():
    with (PACKET / "external_source_acquisition_plan_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        sources = {row["SourceID"]: row for row in csv.DictReader(handle)}
    assert set(sources) == {"SRC01", "SRC02", "SRC03", "SRC04", "SRC05"}
    assert sources["SRC01"]["TargetID"] == "EVT01"
    assert sources["SRC01"]["AccessURL"] == "https://arxiv.org/abs/0810.2116"
    assert sources["SRC02"]["AccessURL"] == (
        "https://science.nrao.edu/science/surveys/littlethings/data"
    )
    assert sources["SRC03"]["AccessURL"] == "https://zenodo.org/records/2552349"
    assert sources["SRC03"]["RedistributionPolicy"] == (
        "do not commit raw cubes; commit checksums and derived small summary"
    )
    assert sources["SRC04"]["Priority"] == "high"
    assert {row["InterpretationGuardrail"] for row in sources.values()} == {
        "source_acquisition_plan_no_raw_data_redistribution_no_velocity_endpoint"
    }

    with (PACKET / "external_source_required_fields_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        fields = {row["FieldID"]: row for row in csv.DictReader(handle)}
    assert set(fields) == {
        "FLD01",
        "FLD02",
        "FLD03",
        "FLD04",
        "FLD05",
        "FLD06",
        "FLD07",
        "FLD08",
    }
    assert fields["FLD05"]["FieldName"] == "LinewidthStressOrCubeDerivedProxy"
    assert fields["FLD08"]["AllowedUse"] == "forbidden"
    assert fields["FLD08"]["FieldName"] == "VobsResidualOrFormulaSelectedQuantity"

    text = (PACKET / "external_source_acquisition_plan_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not redistribute raw survey products" in text
    assert "does not open a velocity endpoint" in text
    assert "Raw FITS cubes or large survey products should remain outside" in text


def test_external_source_download_manifest_is_structured_and_local_raw_only():
    with (PACKET / "external_source_download_manifest_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 7
    assert sum(row["Status"] == "downloaded" for row in rows) == 5
    assert sum(row["Status"] == "failed" for row in rows) == 2
    assert {row["PublicPacketUse"] for row in rows} == {"derived_index_only"}
    assert all(row["LocalRawPath"].startswith("data/raw/") for row in rows)
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "raw_downloads_local_only_public_packet_derived_index_only"
    }

    with (PACKET / "halogas_zenodo_file_index_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        halogas = list(csv.DictReader(handle))
    assert len(halogas) == 192
    candidate_rows = [row for row in halogas if row["CandidateSPARCOverlap"]]
    assert len(candidate_rows) == 40
    assert {
        row["CandidateSPARCOverlap"]
        for row in candidate_rows
        if row["CandidateSPARCOverlap"]
    } == {"NGC2403", "NGC3198", "NGC4559", "NGC5055", "NGC5585"}
    assert all(row["Checksum"].startswith("md5:") for row in halogas)

    text = (PACKET / "external_source_download_manifest_v01.md").read_text(
        encoding="utf-8"
    )
    assert "Raw downloaded files are stored under `data/raw/`" in text
    assert "HALOGAS indexed files: 192" in text


def test_halogas_candidate_moment_downloads_are_md5_verified_and_no_cubes():
    with (PACKET / "halogas_candidate_moment_downloads_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 30
    assert {row["GalaxyName"] for row in rows} == {
        "NGC2403",
        "NGC3198",
        "NGC4559",
        "NGC5055",
        "NGC5585",
    }
    assert {row["Status"] for row in rows} == {"downloaded_verified"}
    assert all("cube" not in row["FileName"].lower() for row in rows)
    assert all(row["ExpectedChecksum"] == "md5:" + row["ActualMD5"] for row in rows)
    assert all(row["ExpectedBytes"] == row["ActualBytes"] for row in rows)
    assert {row["PublicPacketUse"] for row in rows} == {"derived_manifest_only"}
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "halogas_raw_fits_local_only_commit_derived_manifest_only"
    }

    text = (PACKET / "halogas_candidate_moment_downloads_v01.md").read_text(
        encoding="utf-8"
    )
    assert "Large cubes are intentionally excluded" in text
    assert "Verified files: 30" in text
    assert "Verified bytes: 117547200" in text


def test_source_alias_crossmatch_exact_matches_current_external_sources():
    with (PACKET / "source_alias_crossmatch_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 15
    assert sum(row["InWTauEff"] == "yes" for row in rows) == 14
    assert sum(row["InWTauEff"] == "no" for row in rows) == 1
    assert {
        row["ExternalName"] for row in rows if row["InWTauEff"] == "no"
    } == {"DDO168"}
    assert {row["SourceFamily"] for row in rows} == {
        "HALOGAS",
        "LITTLE_THINGS",
        "THINGS",
    }
    assert {row["AllowedUse"] for row in rows} == {"join_key_only"}
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "alias_crossmatch_join_only_no_velocity_endpoint"
    }

    text = (PACKET / "source_alias_crossmatch_v01.md").read_text(encoding="utf-8")
    assert "join audit only" in text
    assert "Matched to `W_tau_eff`: 14" in text


def test_halogas_moment_features_are_derived_external_proxies_only():
    with (PACKET / "halogas_moment_feature_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        features = list(csv.DictReader(handle))
    assert len(features) == 30
    assert {row["Product"] for row in features} == {"coldens", "mom0", "mom1"}
    assert {row["Resolution"] for row in features} == {"HR", "LR"}
    assert {row["AllowedUse"] for row in features} == {
        "external_halogas_moment_proxy_only"
    }

    with (PACKET / "halogas_moment_w_tau_eff_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        joined = {row["GalaxyName"]: row for row in csv.DictReader(handle)}
    assert set(joined) == {"NGC2403", "NGC3198", "NGC4559", "NGC5055", "NGC5585"}
    assert joined["NGC2403"]["HALOGAS_moment_stress_proxy_v01"] == "138.580994941"
    assert joined["NGC5055"]["Class"] == "C"
    assert {row["ReadoutUse"] for row in joined.values()} == {
        "HALOGAS_moment_proxy_no_velocity_endpoint"
    }
    assert {row["InterpretationGuardrail"] for row in joined.values()} == {
        "halogas_moment_features_external_proxy_only_no_velocity_endpoint"
    }

    text = (PACKET / "halogas_moment_features_v01.md").read_text(encoding="utf-8")
    assert "does not use SPARC velocity residuals as predictors" in text
    assert "does not open a velocity endpoint" in text


def test_halogas_moment_proxy_readout_remains_weak_control():
    with (PACKET / "halogas_moment_proxy_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "5"
    assert metrics["coverage_joined"]["SecondaryValue"] == "A;C"
    assert (
        metrics["pearson_halogas_moment_stress_vs_w_tau_score"]["Value"]
        == "0.216413317"
    )
    assert metrics["auc_high_vs_low_halogas_moment_stress"]["Value"] == "0.500000000"

    with (PACKET / "halogas_moment_proxy_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["HMP01"]["Status"] == "weak_or_null_halogas_moment_proxy_control"
    assert decisions["HMP01"]["NextAction"] == (
        "retain_HALOGAS_as_weak_control_prioritize_THINGS_or_non_WHISP_asymmetry"
    )
    assert decisions["HMP02"]["Status"] == "velocity_endpoint_still_closed"

    text = (PACKET / "halogas_moment_proxy_readout_v01.md").read_text(
        encoding="utf-8"
    )
    assert "small-overlap external control" in text
    assert "does not open a velocity endpoint" in text


def test_things_table3_expanded_overlap_is_below_gate_and_not_positive():
    with (PACKET / "things_trachternach2008_table3_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        table = list(csv.DictReader(handle))
    assert len(table) == 18
    assert {row["AllowedUse"] for row in table} == {
        "published_non_circular_motion_control_only"
    }
    assert {row["InterpretationGuardrail"] for row in table} == {
        "things_table3_published_control_no_velocity_endpoint"
    }

    with (PACKET / "things_table3_w_tau_eff_overlap_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        overlap = {row["GalaxyName"]: row for row in csv.DictReader(handle)}
    assert set(overlap) == {
        "DDO154",
        "IC2574",
        "NGC2366",
        "NGC2403",
        "NGC2976",
        "NGC3198",
        "NGC5055",
        "NGC7331",
    }
    assert overlap["IC2574"]["Class"] == "C"
    assert overlap["IC2574"]["MedianNonCircularAmplitudeKms"] == "3.750000000"
    assert {row["ReadoutUse"] for row in overlap.values()} == {
        "THINGS_Table3_expanded_overlap_no_velocity_endpoint"
    }

    with (PACKET / "things_table3_w_tau_eff_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["things_table3_total_rows"]["Value"] == "18"
    assert metrics["things_table3_w_tau_overlap"]["Value"] == "8"
    assert metrics["pearson_table3_ar_vs_w_tau_score"]["Value"] == "-0.087767676"
    assert metrics["auc_high_vs_low_table3_ar"]["Value"] == "0.187500000"
    assert metrics["minimum_directional_n_gate"]["Value"] == "not_met"

    with (PACKET / "things_table3_expansion_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["T3D01"]["Status"] == (
        "expanded_overlap_available_but_below_minimum_n"
    )
    assert decisions["T3D02"]["Status"] == "closed"

    text = (PACKET / "things_table3_expanded_overlap_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not open a velocity endpoint" in text
    assert "Minimum N gate: not_met" in text


def test_reynolds2020_asymmetry_crossmatch_ingests_vizier_but_below_gate():
    with (PACKET / "reynolds2020_vizier_download_manifest_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        downloads = {row["FileName"]: row for row in csv.DictReader(handle)}
    assert set(downloads) == {"ReadMe.txt", "tablea1.dat", "tablea2.dat", "tablea3.dat"}
    assert {row["Status"] for row in downloads.values()} == {"downloaded"}
    assert {row["PublicPacketUse"] for row in downloads.values()} == {
        "derived_catalog_and_crossmatch_only"
    }

    with (PACKET / "reynolds2020_asymmetry_catalog_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        catalog = list(csv.DictReader(handle))
    assert len(catalog) == 142
    assert {row["Survey"] for row in catalog} == {"LVHIS", "VIVA", "HALOGAS"}
    assert {row["AllowedUse"] for row in catalog} == {
        "published_resolved_HI_asymmetry_proxy_only"
    }

    with (PACKET / "reynolds2020_asymmetry_w_tau_eff_crossmatch_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        cross = {row["ExternalName"]: row for row in csv.DictReader(handle)}
    assert set(cross) == {"NGC3198", "NGC4559", "NGC5055", "NGC5585"}
    assert {row["Survey"] for row in cross.values()} == {"HALOGAS"}
    assert cross["NGC5055"]["Class"] == "C"
    assert cross["NGC5055"]["Amap"] == "0.270000000"
    assert {row["ReadoutUse"] for row in cross.values()} == {
        "non_WHISP_resolved_HI_asymmetry_crossmatch_no_velocity_endpoint"
    }

    with (PACKET / "reynolds2020_asymmetry_crossmatch_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["reynolds2020_catalog_rows"]["Value"] == "142"
    assert metrics["exact_w_tau_eff_crossmatch_rows"]["Value"] == "4"
    assert metrics["exact_w_tau_eff_crossmatch_rows"]["SecondaryValue"] == "HALOGAS"
    assert metrics["pearson_amap_vs_w_tau_score"]["Value"] == "0.514475616"
    assert metrics["pearson_avel_vs_w_tau_score"]["Value"] == "0.063521995"
    assert metrics["minimum_non_whisp_asymmetry_gate"]["Value"] == "not_met"

    with (PACKET / "reynolds2020_asymmetry_crossmatch_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["R20D01"]["Status"] == (
        "catalog_ingested_but_exact_overlap_below_minimum_n"
    )
    assert decisions["R20D01"]["NextAction"] == (
        "resolve_LVHIS_aliases_or_expand_W_tau_eff_seed_before_directional_claim"
    )
    assert decisions["R20D02"]["Status"] == "closed"

    text = (PACKET / "reynolds2020_asymmetry_crossmatch_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not open a velocity endpoint" in text
    assert "LVHIS alias resolution is the next step" in text


def test_lvh_alias_resolved_reynolds2020_crossmatch_improves_but_below_gate():
    with (PACKET / "lvhis_database_download_manifest_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        downloads = {row["FileName"]: row for row in csv.DictReader(handle)}
    assert set(downloads) == {"LVHIS-database.html"}
    assert downloads["LVHIS-database.html"]["Status"] == "downloaded"
    assert downloads["LVHIS-database.html"]["PublicPacketUse"] == (
        "derived_alias_table_only"
    )

    with (PACKET / "lvhis_alias_resolution_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        aliases = {row["ExternalName"]: row for row in csv.DictReader(handle)}
    assert len(aliases) == 82
    assert aliases["LVHIS004"]["CanonicalSPARCNameCandidate"] == "NGC0055"
    assert aliases["LVHIS018"]["CanonicalSPARCNameCandidate"] == "NGC1705"
    assert {row["AllowedUse"] for row in aliases.values()} == {"alias_resolution_only"}

    with (
        PACKET / "reynolds2020_lvh_alias_resolved_w_tau_eff_crossmatch_v01.csv"
    ).open(newline="", encoding="utf-8") as handle:
        cross = {row["CanonicalSPARCName"]: row for row in csv.DictReader(handle)}
    assert set(cross) == {"NGC0055", "NGC1705", "NGC3198", "NGC4559", "NGC5055", "NGC5585"}
    assert cross["NGC0055"]["CrossmatchMode"] == "lvhis_database_optical_id_alias"
    assert cross["NGC1705"]["CrossmatchMode"] == "lvhis_database_optical_id_alias"
    assert {row["ReadoutUse"] for row in cross.values()} == {
        "non_WHISP_resolved_HI_asymmetry_alias_resolved_no_velocity_endpoint"
    }

    with (PACKET / "reynolds2020_lvh_alias_resolved_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["lvhis_alias_rows"]["Value"] == "82"
    assert metrics["alias_resolved_w_tau_eff_crossmatch_rows"]["Value"] == "6"
    assert metrics["lvhis_new_alias_matches"]["SecondaryValue"] == "NGC0055;NGC1705"
    assert metrics["pearson_amap_vs_w_tau_score_alias_resolved"]["Value"] == "-0.233039744"
    assert metrics["pearson_avel_vs_w_tau_score_alias_resolved"]["Value"] == "0.375346400"
    assert metrics["auc_c_higher_amap_alias_resolved"]["Value"] == "0.388888889"
    assert metrics["auc_c_higher_avel_alias_resolved"]["Value"] == "0.777777778"
    assert metrics["minimum_non_whisp_asymmetry_gate_alias_resolved"]["Value"] == "not_met"

    with (PACKET / "reynolds2020_lvh_alias_resolved_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["LVHD01"]["Status"] == (
        "alias_resolution_improves_overlap_but_below_minimum_n"
    )
    assert decisions["LVHD02"]["Status"] == "closed"

    text = (PACKET / "reynolds2020_lvh_alias_resolved_crossmatch_v01.md").read_text(
        encoding="utf-8"
    )
    assert "small-sample hint only" in text
    assert "does not open a velocity endpoint" in text


def test_reynolds2020_coverage_ceiling_closes_simple_alias_route():
    with (PACKET / "reynolds2020_coverage_ceiling_audit_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["Survey"]: row for row in csv.DictReader(handle)}
    assert set(rows) == {"LVHIS", "VIVA", "HALOGAS", "TOTAL"}
    assert rows["LVHIS"]["TotalWTauEffMatches"] == "2"
    assert rows["VIVA"]["TotalWTauEffMatches"] == "0"
    assert rows["HALOGAS"]["TotalWTauEffMatches"] == "4"
    assert rows["TOTAL"]["TotalWTauEffMatches"] == "6"
    assert rows["TOTAL"]["MatchedCanonicalNames"] == (
        "NGC0055;NGC1705;NGC3198;NGC4559;NGC5055;NGC5585"
    )
    assert rows["TOTAL"]["CeilingStatus"] == "below_minimum_directional_gate"
    assert {row["InterpretationGuardrail"] for row in rows.values()} == {
        "reynolds2020_coverage_ceiling_no_velocity_endpoint"
    }

    with (PACKET / "reynolds2020_coverage_ceiling_next_actions_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        actions = {row["ActionID"]: row for row in csv.DictReader(handle)}
    assert actions["R20C01"]["Status"] == "hard_ceiling_below_gate"
    assert actions["R20C01"]["RequiredBeforeClaim"] == (
        "add_at_least_9_eligible_independent_matches_or_change_source_family"
    )
    assert actions["R20C03"]["Status"] == "closed"

    text = (PACKET / "reynolds2020_coverage_ceiling_audit_v01.md").read_text(
        encoding="utf-8"
    )
    assert "This closes the simple-alias route" in text
    assert "does not use Vobs residuals" not in text
    assert "velocity-field asymmetry behaves differently from map asymmetry" in text


def test_reynolds2020_seed_expansion_freezes_queue_before_readout():
    with (PACKET / "reynolds2020_seed_expansion_candidate_queue_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 142
    status_counts = collections.Counter(row["ExpansionStatus"] for row in rows)
    assert status_counts["already_in_frozen_seed"] == 6
    assert status_counts["predeclared_candidate_pending_sparc_rotmod_audit"] == 123
    assert status_counts["excluded_before_scoring"] == 13
    candidate_rows = [
        row
        for row in rows
        if row["ExpansionStatus"]
        == "predeclared_candidate_pending_sparc_rotmod_audit"
    ]
    assert collections.Counter(row["Survey"] for row in candidate_rows) == {
        "LVHIS": 64,
        "VIVA": 45,
        "HALOGAS": 14,
    }
    assert sum(row["PreScorePriority"] == "high" for row in candidate_rows) == 91
    assert {row["InterpretationGuardrail"] for row in rows} == {
        "reynolds2020_seed_expansion_freeze_no_directional_readout"
    }

    with (PACKET / "reynolds2020_seed_expansion_policy_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        policies = {row["RuleID"]: row for row in csv.DictReader(handle)}
    assert policies["R20F01"]["NRows"] == "123"
    assert policies["R20F02"]["NRows"] == "pending"
    assert policies["R20F03"]["NRows"] == "91"
    assert policies["R20F05"]["AllowedUse"] == "locks_the_next_endpoint"

    with (PACKET / "reynolds2020_seed_expansion_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert gates["R20G01"]["Status"] == "met"
    assert gates["R20G01"]["N"] == "123"
    assert gates["R20G02"]["N"] == "91"
    assert gates["R20G03"]["Status"] == "closed"

    text = (PACKET / "reynolds2020_seed_expansion_freeze_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not calculate any new residual score" in text
    assert "A Reynolds Amap/Avel directional readout is still forbidden" in text


def test_reynolds2020_sparc_rotmod_availability_remains_below_gate():
    with (PACKET / "reynolds2020_sparc_rotmod_availability_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = {row["CanonicalSPARCNameCandidate"]: row for row in csv.DictReader(handle)}
    available = [row for row in rows.values() if row["RotmodAvailable"] == "yes"]
    passed = [
        row
        for row in rows.values()
        if row["PassesMinimumRadialPointGate"] == "yes"
    ]
    assert {row["CanonicalSPARCNameCandidate"] for row in available} == {
        "NGC0300",
        "NGC0247",
        "NGC2915",
        "ESO444-G084",
        "UGCA442",
        "NGC7793",
    }
    assert {row["CanonicalSPARCNameCandidate"] for row in passed} == {
        "NGC0300",
        "NGC0247",
        "NGC2915",
        "UGCA442",
        "NGC7793",
    }
    assert rows["ESO444-G084"]["NRotmodPoints"] == "7"
    assert {row["AllowedPublicUse"] for row in rows.values()} == {
        "derived_availability_manifest_only"
    }

    with (PACKET / "reynolds2020_sparc_rotmod_availability_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        summary = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert summary["predeclared_expansion_candidates"]["Value"] == "123"
    assert summary["rotmod_available_candidates"]["Value"] == "6"
    assert summary["minimum_radial_point_gate_passed"]["Value"] == "5"
    assert summary["high_priority_avel_passed"]["Value"] == "5"
    assert summary["expanded_validation_minimum_n_gate"]["Value"] == "not_met"
    assert summary["lvhis_candidate_passed_rotmod_gate"]["Value"] == "5"
    assert summary["viva_candidate_passed_rotmod_gate"]["Value"] == "0"
    assert summary["halogas_candidate_passed_rotmod_gate"]["Value"] == "0"

    with (PACKET / "reynolds2020_sparc_rotmod_availability_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["R20A01"]["Status"] == (
        "current_local_sparc_rotmod_overlap_below_minimum_n"
    )
    assert decisions["R20A02"]["Status"] == "raw_sparc_rotmods_not_redistributed"
    assert decisions["R20A03"]["Status"] == "closed"

    text = (PACKET / "reynolds2020_sparc_rotmod_availability_audit_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not redistribute raw SPARC rotmod files" in text
    assert "too small for a paper-grade Reynolds directional validation" in text


def test_yu2022_alfalfa_profile_asymmetry_coverage_is_promising_but_closed():
    with (PACKET / "yu2022_alfalfa_download_manifest_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        downloads = {row["FileName"]: row for row in csv.DictReader(handle)}
    assert set(downloads) == {"ReadMe.txt", "table2.dat.gz", "table2.dat"}
    assert {row["Status"] for row in downloads.values()} == {"downloaded"}
    assert {row["PublicPacketUse"] for row in downloads.values()} == {
        "derived_catalog_and_coverage_only"
    }

    with (PACKET / "yu2022_alfalfa_profile_asymmetry_catalog_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        catalog = list(csv.DictReader(handle))
    assert len(catalog) == 29958
    assert catalog[0]["AllowedUse"] == "global_HI_profile_asymmetry_proxy_only"

    with (PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        summary = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert summary["current_w_tau_eff_seed_overlap"]["Value"] == "7"
    assert summary["local_sparc_rotmod_overlap"]["Value"] == "26"
    assert summary["new_seed_expansion_candidates"]["Value"] == "19"
    assert summary["minimum_n_gate_after_potential_expansion"]["Value"] == "met"

    with (PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        coverage = list(csv.DictReader(handle))
    assert len(coverage) == 26
    assert {row["ReadoutPermission"] for row in coverage} == {
        "coverage_only_no_directional_readout"
    }
    assert {
        row["CanonicalSPARCNameCandidate"]
        for row in coverage
        if row["InWTauEffSeed"] == "yes"
    } == {
        "UGC00128",
        "UGC00191",
        "UGC02455",
        "UGC05716",
        "UGC05764",
        "UGC05829",
        "UGC07603",
    }

    with (PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["YU22D01"]["Status"] == (
        "promising_for_predeclared_seed_expansion"
    )
    assert decisions["YU22D02"]["Status"] == "closed"

    text = (PACKET / "yu2022_alfalfa_profile_asymmetry_coverage_v01.md").read_text(
        encoding="utf-8"
    )
    assert "coverage audit only" in text
    assert "does not compute an Af/Ac directional readout" not in text
    assert "freeze the expansion rule before computing" in text


def test_yu2022_alfalfa_seed_expansion_freezes_queue_before_scoring():
    with (PACKET / "yu2022_alfalfa_seed_expansion_queue_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 26
    assert collections.Counter(row["FreezeRole"] for row in rows) == {
        "anchor_existing_seed": 7,
        "predeclared_expansion_candidate": 19,
    }
    assert collections.Counter(row["ScoringPermission"] for row in rows) == {
        "anchor_only_no_refit": 7,
        "allowed_after_expanded_scoring_script_committed": 19,
    }
    assert {row["ProfileQualityFlag"] for row in rows} == {"primary_quality"}
    assert {row["DirectionalReadoutPermission"] for row in rows} == {
        "closed_until_expanded_scores_committed"
    }

    with (PACKET / "yu2022_alfalfa_seed_expansion_policy_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        policies = {row["RuleID"]: row for row in csv.DictReader(handle)}
    assert policies["YU22F01"]["NRows"] == "19"
    assert policies["YU22F02"]["NRows"] == "19"
    assert policies["YU22F03"]["NRows"] == "7"
    assert policies["YU22F04"]["AllowedUse"] == "locks_the_next_endpoint"

    with (PACKET / "yu2022_alfalfa_seed_expansion_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert gates["YU22G01"]["Status"] == "met"
    assert gates["YU22G01"]["N"] == "19"
    assert gates["YU22G02"]["N"] == "19"
    assert gates["YU22G03"]["Status"] == "met"
    assert gates["YU22G03"]["N"] == "26"
    assert gates["YU22G04"]["Status"] == "closed"

    text = (PACKET / "yu2022_alfalfa_seed_expansion_freeze_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not calculate expanded residual scores" in text
    assert "Af/Ac directional readout remains forbidden" in text


def test_yu2022_alfalfa_expanded_w_tau_eff_scoring_is_frozen_before_directional_readout():
    with (PACKET / "yu2022_alfalfa_expanded_w_tau_eff_scores_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        scores = list(csv.DictReader(handle))
    assert len(scores) == 26
    assert collections.Counter(row["FreezeRole"] for row in scores) == {
        "anchor_existing_seed": 7,
        "predeclared_expansion_candidate": 19,
    }
    assert collections.Counter(row["ScoringStatus"] for row in scores) == {
        "anchor_not_refit": 7,
        "scored": 15,
        "excluded": 4,
    }
    assert {
        row["GalaxyName"]
        for row in scores
        if row["ScoringStatus"] == "excluded"
    } == {"UGC00634", "UGC00891", "UGC05999", "UGC07261"}
    assert all(
        row["AnchorPolicy"] == "retained_without_refit"
        for row in scores
        if row["FreezeRole"] == "anchor_existing_seed"
    )
    assert all(
        row["W_tau_eff_readout_score_v01"] == ""
        for row in scores
        if row["ScoringStatus"] == "excluded"
    )
    assert "Af" not in scores[0]
    assert "Ac" not in scores[0]

    with (PACKET / "yu2022_alfalfa_expanded_w_tau_eff_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        summary = {row["Subset"]: row for row in csv.DictReader(handle)}
    assert summary["anchors"]["NGalaxies"] == "7"
    assert summary["scored_expansion_candidates"]["NGalaxies"] == "15"
    assert summary["excluded_expansion_candidates"]["NGalaxies"] == "4"
    assert summary["directional_readout_ready_rows"]["NGalaxies"] == "22"
    assert (
        summary["directional_readout_ready_rows"][
            "Median_W_tau_eff_readout_score_v01"
        ]
        == "0.413636363"
    )

    with (PACKET / "yu2022_alfalfa_expanded_w_tau_eff_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["YU22S01"]["Status"] == "met"
    assert decisions["YU22S01"]["N"] == "15"
    assert decisions["YU22S02"]["Status"] == "ready_after_commit"
    assert decisions["YU22S02"]["N"] == "22"
    assert decisions["YU22S03"]["Status"] == "satisfied"
    assert decisions["YU22S03"]["N"] == "7"

    text = (PACKET / "yu2022_alfalfa_expanded_w_tau_eff_scoring_v01.md").read_text(
        encoding="utf-8"
    )
    assert "It does not compute the Af/Ac directional readout." in text
    assert "Existing `W_tau_eff` seed overlaps are retained as anchors without refit." in text


def test_yu2022_alfalfa_af_ac_directional_readout_is_not_supported():
    with (PACKET / "yu2022_alfalfa_af_ac_w_tau_eff_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 22
    assert collections.Counter(row["ProfileAsymmetryTier"] for row in rows) == {
        "low_profile_asymmetry": 12,
        "medium_profile_asymmetry": 4,
        "high_profile_asymmetry": 6,
    }
    assert {row["ReadoutUse"] for row in rows} == {
        "frozen_yu2022_af_ac_direction_vs_committed_w_tau_eff_score"
    }

    with (PACKET / "yu2022_alfalfa_af_ac_w_tau_eff_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_directional_readout_rows"]["Value"] == "22"
    assert (
        metrics["coverage_directional_readout_rows"]["SecondaryValue"]
        == "low=12;medium=4;high=6"
    )
    assert metrics["spearman_LogMaxAfAc_vs_w_tau_score"]["Value"] == "0.013023835"
    assert metrics["pearson_LogMaxAfAc_vs_w_tau_score"]["Value"] == "0.010298371"
    assert metrics["auc_high_vs_low_profile_asymmetry_score"]["Value"] == "0.472222222"
    assert metrics["median_score_low_profile_asymmetry"]["Value"] == "0.397727273"
    assert metrics["median_score_high_profile_asymmetry"]["Value"] == "0.388636363"

    with (PACKET / "yu2022_alfalfa_af_ac_w_tau_eff_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["YU22R01"]["Status"] == "not_supported"
    assert decisions["YU22R02"]["Status"] == "no_model_validation_claim"

    text = (PACKET / "yu2022_alfalfa_af_ac_directional_readout_v01.md").read_text(
        encoding="utf-8"
    )
    assert "It does not fit coefficients and does not validate a Tau Core field model." in text
    assert "This is a source-side external hint, not a validation." in text


def test_spatial_kinematic_proxy_next_gate_selects_whisp_with_things_control():
    with (PACKET / "spatial_kinematic_proxy_next_gate_matrix_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        matrix = {row["CandidateGate"]: row for row in csv.DictReader(handle)}
    assert matrix["WHISP_P07_radial_lopsidedness_family"]["UseNext"] == (
        "primary_source_family_extension"
    )
    assert matrix["WHISP_P07_radial_lopsidedness_family"]["CoverageN"] == "10"
    assert matrix["WHISP_P07_radial_lopsidedness_family"]["PrimaryValue"] == "0.760000000"
    assert matrix["THINGS_P03_P05_kinematic_control"]["UseNext"] == (
        "mandatory_systematics_competition_control"
    )
    assert matrix["Yu2022_ALFALFA_global_profile_asymmetry"]["ResultDirection"] == (
        "not_supported"
    )
    assert matrix["HALOGAS_LR_cube_moment_stress"]["UseNext"] == (
        "control_only_until_overlap_expands"
    )

    with (PACKET / "spatial_kinematic_proxy_next_gate_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["SKG01"]["Status"] == (
        "select_WHISP_radial_lopsidedness_extension"
    )
    assert decisions["SKG02"]["Status"] == (
        "retain_THINGS_non_circular_competition_control"
    )
    assert decisions["SKG03"]["Status"] == "do_not_promote_Yu_global_Af_Ac"

    text = (PACKET / "spatial_kinematic_proxy_next_gate_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not fit a new endpoint" in text
    assert "WHISP is prioritized" in text
    assert "THINGS remains mandatory" in text


def test_whisp_expanded_readout_is_positive_but_below_validation_gate():
    with (PACKET / "whisp_expanded_w_tau_eff_readout_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 14
    assert collections.Counter(row["ScoreSource"] for row in rows) == {
        "frozen_original_w_tau_eff_seed": 10,
        "expanded_yu2022_rotmod_scoring_frozen_w_tau_eff_calibration": 4,
    }
    assert collections.Counter(row["WHISP_BurdenSplit"] for row in rows) == {
        "low": 7,
        "high": 7,
    }
    assert {row["ReadoutUse"] for row in rows} == {
        "WHISP_full_overlap_original_plus_expanded_W_tau_eff_no_refit"
    }

    with (PACKET / "whisp_expanded_w_tau_eff_readout_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "14"
    assert metrics["coverage_joined"]["SecondaryValue"] == "original_seed=10;expanded=4"
    assert metrics["pearson_whisp_burden_vs_w_tau_score"]["Value"] == "0.391218683"
    assert metrics["spearman_whisp_burden_vs_w_tau_score"]["Value"] == "0.362637363"
    assert metrics["auc_high_vs_low_whisp_burden"]["Value"] == "0.714285714"
    assert metrics["pearson_radial_contrast_vs_w_tau_score"]["Value"] == "0.374287364"
    assert metrics["pearson_epsilon_kin_vs_w_tau_score"]["Value"] == "0.273373152"

    with (PACKET / "whisp_expanded_w_tau_eff_readout_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["WXR01"]["Status"] == "positive_but_not_paper_grade"
    assert decisions["WXR01"]["N"] == "14"
    assert decisions["WXR02"]["Status"] == "diagnostic_only"

    text = (PACKET / "whisp_expanded_w_tau_eff_readout_v01.md").read_text(
        encoding="utf-8"
    )
    assert "Original seed scores are retained without refit" in text
    assert "below the frozen N>=15 external-validation gate" in text


def test_whisp_holwerda2011_morphology_clears_n15_but_stays_whisp_family_only():
    with (PACKET / "whisp_holwerda2011_download_manifest_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        manifest = {row["FileName"]: row for row in csv.DictReader(handle)}
    assert set(manifest) == {"ReadMe.txt", "tablea1.dat", "tablea2.dat"}
    assert manifest["tablea1.dat"]["Bytes"] == "46343"
    assert manifest["tablea2.dat"]["Bytes"] == "42855"
    assert {row["PublicPacketUse"] for row in manifest.values()} == {
        "derived_catalog_and_crossmatch_only"
    }

    with (PACKET / "whisp_holwerda2011_morphology_catalog_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        catalog = list(csv.DictReader(handle))
    assert len(catalog) == 141
    assert collections.Counter(row["SurveyTable"] for row in catalog) == {
        "Swaters2002_WHISP": 73,
        "Noordermeer2005_WHISP": 68,
    }

    with (PACKET / "whisp_holwerda2011_w_tau_eff_join_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 25
    assert collections.Counter(row["ScoreSource"] for row in rows) == {
        "frozen_original_w_tau_eff_seed": 17,
        "expanded_yu2022_rotmod_scoring_frozen_w_tau_eff_calibration": 8,
    }
    assert collections.Counter(row["AsymmetryASplit"] for row in rows) == {
        "low": 13,
        "high": 12,
    }

    with (PACKET / "whisp_holwerda2011_w_tau_eff_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "25"
    assert metrics["coverage_joined"]["SecondaryValue"] == "original_seed=17;expanded=8"
    assert metrics["spearman_AsymmetryA_vs_w_tau_score"]["Value"] == "0.235045205"
    assert metrics["pearson_AsymmetryA_vs_w_tau_score"]["Value"] == "0.161199465"
    assert metrics["auc_high_vs_low_AsymmetryA"]["Value"] == "0.644230769"
    assert metrics["median_score_low_AsymmetryA"]["Value"] == "0.554545455"
    assert metrics["median_score_high_AsymmetryA"]["Value"] == "0.690909091"

    with (PACKET / "whisp_holwerda2011_w_tau_eff_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["WHM01"]["Status"] == "met"
    assert decisions["WHM01"]["N"] == "25"
    assert decisions["WHM02"]["Status"] == "positive_source_family_replication"
    assert decisions["WHM03"]["Status"] == (
        "WHISP_source_family_only_not_independent_family"
    )

    text = (PACKET / "whisp_holwerda2011_morphology_readout_v01.md").read_text(
        encoding="utf-8"
    )
    assert "clears the N>=15 source-family gate" in text
    assert "not a fully independent external-family validation" in text


def test_things_control_gate_does_not_absorb_whisp_direction():
    with (PACKET / "things_expanded_score_resolver_audit_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        audit = list(csv.DictReader(handle))
    assert len(audit) == 18
    assert sum(row["InExpandedWTauEffResolver"] == "yes" for row in audit) == 8
    assert sum(
        row["InOriginalWTauEffSeed"] == "no"
        and row["InExpandedWTauEffResolver"] == "yes"
        for row in audit
    ) == 0

    with (PACKET / "things_vs_whisp_control_matrix_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        matrix = {row["Readout"]: row for row in csv.DictReader(handle)}
    assert matrix["WHISP_Holwerda2011_morphology"]["PrimaryValue"] == "0.644230769"
    assert matrix["WHISP_vanEymeren2011_lopsidedness"]["PrimaryValue"] == "0.714285714"
    assert matrix["THINGS_Trachternach2008_Table3"]["PrimaryValue"] == "0.187500000"
    assert matrix["THINGS_Trachternach2008_Table3"]["SecondaryValue"] == "-0.087767676"
    assert matrix["THINGS_P05_harmonic_control"]["PrimaryValue"] == "0.333333333"

    with (PACKET / "things_control_gate_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["TCG01"]["Status"] == (
        "no_new_THINGS_overlap_from_expanded_resolver"
    )
    assert decisions["TCG02"]["Status"] == (
        "THINGS_controls_do_not_absorb_WHISP_direction"
    )
    assert decisions["TCG03"]["Status"] == "control_only_below_THINGS_validation_n"

    text = (PACKET / "things_control_gate_v01.md").read_text(encoding="utf-8")
    assert "does not fit coefficients" in text
    assert "THINGS non-circular controls do not reproduce the WHISP-positive direction" in text
    assert "non-WHISP resolved-HI replication" in text


def test_things_table3_expanded_scoring_and_control_readout_remain_below_n15():
    with (PACKET / "things_table3_expanded_w_tau_eff_scores_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        scores = list(csv.DictReader(handle))
    assert len(scores) == 18
    assert collections.Counter(row["ScoringStatus"] for row in scores) == {
        "existing_score_retained": 8,
        "newly_scored_from_rotmod": 5,
        "excluded_no_rotmod": 5,
    }
    assert {
        row["GalaxyName"]
        for row in scores
        if row["ScoringStatus"] == "newly_scored_from_rotmod"
    } == {"NGC2841", "NGC2903", "NGC3521", "NGC6946", "NGC7793"}

    with (PACKET / "things_table3_expanded_w_tau_eff_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        summary = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert summary["things_table3_total_rows"]["Value"] == "18"
    assert summary["things_table3_resolved_w_tau_eff_rows"]["Value"] == "13"
    assert summary["newly_scored_from_rotmod"]["Value"] == "5"
    assert summary["excluded_no_rotmod"]["Value"] == "5"

    with (PACKET / "things_table3_expanded_w_tau_eff_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["T3X01"]["Status"] == "expanded_but_still_below_N15"
    assert decisions["T3X01"]["N"] == "13"
    assert decisions["T3X02"]["Status"] == "no_refit_no_velocity_formula"

    with (PACKET / "things_table3_expanded_control_readout_metrics_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        metrics = {row["Metric"]: row for row in csv.DictReader(handle)}
    assert metrics["coverage_joined"]["Value"] == "13"
    assert metrics["pearson_Ar_vs_w_tau_score"]["Value"] == "-0.310471908"
    assert metrics["spearman_Ar_vs_w_tau_score"]["Value"] == "-0.310866869"
    assert metrics["auc_high_vs_low_Ar"]["Value"] == "0.345238095"
    assert metrics["pearson_ArOverVmaxPercent_vs_w_tau_score"]["Value"] == "0.321831406"
    assert metrics["auc_high_vs_low_ArOverVmaxPercent"]["Value"] == "0.702380952"

    with (PACKET / "things_table3_expanded_control_readout_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        readout_decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert readout_decisions["T3R01"]["Status"] == "does_not_absorb_WHISP_direction"
    assert readout_decisions["T3R01"]["N"] == "13"
    assert readout_decisions["T3R02"]["Status"] == "control_only_below_N15"

    text = (PACKET / "things_table3_expanded_control_readout_v01.md").read_text(
        encoding="utf-8"
    )
    assert "does not reproduce the WHISP-positive direction" in text
    assert "below the N>=15 validation threshold" in text


def test_things_missing_rotmod_acquisition_audit_freezes_no_synthetic_expansion():
    with (PACKET / "things_missing_rotmod_acquisition_audit_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        audit = list(csv.DictReader(handle))
    missing = {
        row["GalaxyName"]: row
        for row in audit
        if row["CurrentStatus"] == "missing_local_sparc_rotmod"
    }
    assert set(missing) == {"NGC925", "NGC3031", "NGC3621", "NGC3627", "NGC4736"}
    assert all(row["HasLocalSparcRotmod"] == "no" for row in missing.values())
    assert all(row["CurrentScoreStatus"] == "excluded_no_rotmod" for row in missing.values())
    assert all(
        row["AllowedNextUse"]
        == "score_only_if_public_mass_model_columns_are_recovered_and_conversion_rule_is_frozen"
        for row in missing.values()
    )
    assert missing["NGC925"]["PrimarySource"] == "de_Blok_etal_2008_THINGS_mass_models"
    assert missing["NGC3031"]["PrimarySource"] == "de_Blok_etal_2008_THINGS_mass_models"
    assert missing["NGC3627"]["PrimarySource"] == "de_Blok_etal_2008_THINGS_mass_models"
    assert (
        missing["NGC3621"]["AcquisitionClass"]
        == "possible_but_not_clean_THINGS_Table3_completion"
    )
    assert missing["NGC4736"]["AcquisitionClass"] == "possible_but_high_systematics_risk"

    with (PACKET / "things_missing_rotmod_acquisition_plan_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        plan = {row["StepID"]: row for row in csv.DictReader(handle)}
    assert plan["TMA01"]["MinimumSuccess"] == (
        "at_least_two_missing_galaxies_with_Vobs_Vgas_Vdisk_Vbul"
    )
    assert plan["TMA01"]["ForbiddenAction"] == (
        "synthetic_baryonic_components_or_fit_to_W_tau_eff"
    )
    assert plan["TMA03"]["ForbiddenAction"] == "claim_THINGS_N15_validation"

    text = (PACKET / "things_missing_rotmod_acquisition_audit_v01.md").read_text(
        encoding="utf-8"
    )
    assert "Missing local SPARC-like rotmod inputs: 5" in text
    assert "Published rotation curves alone are insufficient" in text
    assert "at least two of the missing galaxies" in text


def test_things_missing_mass_model_source_probe_keeps_things_gate_closed():
    with (PACKET / "things_missing_mass_model_source_probe_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        probes = {row["SourceID"]: row for row in csv.DictReader(handle)}
    assert probes["SPARC_ROTMod_LTG"]["ProbeResult"] == "no_missing_five_found"
    assert probes["SPARC_ROTMod_LTG"]["UsableForWtauEff"] == "no"
    assert probes["SPARC_TABLE2_MRT"]["ProbeResult"] == "no_missing_five_found"
    assert probes["SPARC_TABLE2_MRT"]["UsableForWtauEff"] == "no"
    assert probes["THINGS_DATA_PRODUCTS"]["ProbeResult"] == (
        "hi_fits_products_exist_for_missing_five"
    )
    assert probes["THINGS_DATA_PRODUCTS"]["UsableForWtauEff"] == "not_directly"
    assert probes["DEBLOK2008_ARXIV_SOURCE"]["UsableForWtauEff"] == "not_directly"
    assert all(
        row["Guardrail"]
        == "source_probe_no_raw_data_redistribution_no_synthetic_mass_models"
        for row in probes.values()
    )

    with (PACKET / "things_missing_mass_model_source_probe_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["TMSP01"]["Status"] == (
        "SPARC_public_rotmod_does_not_resolve_missing_five"
    )
    assert decisions["TMSP01"]["ForbiddenAction"] == (
        "claim_THINGS_N15_or_score_from_rotation_curve_only"
    )
    assert decisions["TMSP02"]["Status"] == (
        "THINGS_HI_products_are_available_but_not_score_ready"
    )

    text = (PACKET / "things_missing_mass_model_source_probe_v01.md").read_text(
        encoding="utf-8"
    )
    assert "SPARC LTG rotmod archive" in text
    assert "do not resolve the missing five" in text
    assert "at least two missing galaxies" in text


def test_things_mass_model_recovery_gate_closes_route1_before_route2():
    with (PACKET / "things_mass_model_recovery_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        recovery = list(csv.DictReader(handle))
    assert {row["GalaxyName"] for row in recovery} == {
        "NGC925",
        "NGC3031",
        "NGC3621",
        "NGC3627",
        "NGC4736",
    }
    assert all(
        row["ScoreReadyColumnsFound"] == "no"
        and row["Route1Conclusion"] == "not_score_ready_from_direct_public_tables"
        for row in recovery
    )
    assert all(
        row["DeblokArxivSourceStatus"]
        == "method_and_global_fit_tables_present_per_radius_columns_not_exposed"
        for row in recovery
    )
    assert all(
        row["Guardrail"] == "route1_then_route2_no_score_from_plots_no_target_refit"
        for row in recovery
    )

    with (PACKET / "things_mass_model_route2_reconstruction_plan_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        route2 = {row["StepID"]: row for row in csv.DictReader(handle)}
    assert route2["R2-01"]["Forbidden"] == "choose_rule_after_viewing_score_direction"
    assert route2["R2-02"]["Forbidden"] == "tune_gas_component_to_reduce_residuals"
    assert route2["R2-03"]["Forbidden"] == "fit_ML_to_W_tau_eff_or_Vobs_endpoint"
    assert route2["R2-04"]["Forbidden"] == "claim_THINGS_N15_before_two_score_ready_rows"

    with (PACKET / "things_mass_model_recovery_gate_decision_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        decisions = {row["DecisionID"]: row for row in csv.DictReader(handle)}
    assert decisions["TMRG01"]["Status"] == "route1_direct_table_recovery_not_score_ready"
    assert decisions["TMRG01"]["NextGate"] == "route2_frozen_reconstruction_protocol"
    assert decisions["TMRG02"]["Status"] == "route2_allowed_but_not_yet_scored"

    text = (PACKET / "things_mass_model_recovery_gate_v01.md").read_text(
        encoding="utf-8"
    )
    assert "first attempt direct recovery" in text
    assert "This closes route 1 for immediate scoring" in text
    assert "Route 2 is allowed only as a pre-registered reconstruction protocol" in text


def test_things_route2_protocol_is_frozen_before_any_new_score():
    with (PACKET / "things_route2_required_inputs_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        inputs = {row["InputID"]: row for row in csv.DictReader(handle)}
    assert inputs["R2I01"]["RequiredField"] == "R_kpc;Vobs_kms;eVobs_kms"
    assert inputs["R2I02"]["RequiredField"] == "Vgas_kms"
    assert inputs["R2I03"]["RequiredField"] == "Vdisk_kms"
    assert inputs["R2I04"]["RequiredField"] == (
        "Vbul_kms_or_zero_with_documented_no_bulge_policy"
    )
    assert inputs["R2I05"]["RequiredField"] == (
        "source_url;download_date;file_size_or_checksum;processing_script"
    )
    assert inputs["R2I02"]["Forbidden"] == "tune_gas_curve_to_match_Vobs_or_W_tau_eff"
    assert inputs["R2I03"]["Forbidden"] == "fit_disk_ML_to_velocity_residuals"
    assert inputs["R2I04"]["Forbidden"] == (
        "toggle_bulge_component_after_viewing_score_direction"
    )

    with (PACKET / "things_route2_frozen_rules_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rules = {row["RuleID"]: row for row in csv.DictReader(handle)}
    assert rules["R2F01"]["FrozenChoice"] == "complete_inputs_and_protocol_first_then_score"
    assert rules["R2F03"]["FrozenChoice"] == (
        "thin_disk_HI_component_with_1p4_helium_metals_factor_if_deriving_from_HI_surface_density"
    )
    assert rules["R2F06"]["FrozenChoice"] == (
        "score_only_galaxies_with_at_least_eight_valid_radial_points_and_all_required_components"
    )
    assert rules["R2F07"]["FrozenChoice"] == (
        "route2_outputs_are_THINGS_control_inputs_not_tau_validation"
    )

    with (PACKET / "things_route2_scoring_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert gates["R2G01"]["CurrentStatus"] == "passed_protocol_only_no_scores"
    assert gates["R2G02"]["CurrentStatus"] == "not_started"
    assert gates["R2G04"]["CurrentStatus"] == "blocked_until_inputs_complete"

    text = (PACKET / "things_route2_mass_model_reconstruction_protocol_v01.md").read_text(
        encoding="utf-8"
    )
    assert "no new `W_tau_eff` score is computed here" in text
    assert "Fix the 3.6 micron stellar mass-to-light policy before scoring" in text
    assert "Do not claim THINGS N>=15" in text
    assert "it remains a THINGS control expansion" in text


def test_things_route2_input_inventory_finds_two_candidates_without_scoring():
    with (PACKET / "things_route2_input_inventory_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        inventory = {row["GalaxyName"]: row for row in csv.DictReader(handle)}
    primary = {
        name for name, row in inventory.items() if row["CandidatePriority"] == "primary_candidate"
    }
    assert primary == {"NGC925", "NGC3031"}
    assert inventory["NGC925"]["MLPolicySeed"] == "disk_ML_3p6_equals_0p65"
    assert inventory["NGC925"]["BulgePolicySeed"] == (
        "zero_bulge_candidate_from_deBlok_text_before_scoring"
    )
    assert inventory["NGC3031"]["MLPolicySeed"] == (
        "disk_ML_3p6_equals_0p8_central_component_ML_3p6_equals_1p0"
    )
    assert inventory["NGC3031"]["BulgePolicySeed"] == (
        "central_component_required_from_deBlok_text_before_scoring"
    )
    assert all(row["CanScoreNow"] == "no" for row in inventory.values())
    assert all(
        row["CurrentCompleteness"] == "source_inputs_identified_not_component_arrays"
        for row in inventory.values()
    )

    with (PACKET / "things_route2_input_download_manifest_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        manifest = list(csv.DictReader(handle))
    roles = {(row["GalaxyName"], row["SourceRole"]): row for row in manifest}
    assert roles[("NGC925", "THINGS_HI_MOM0_NA")]["SizeBytes"] == "4253760"
    assert roles[("NGC925", "SINGS_IRAC1_3p6um")]["SizeBytes"] == "13046400"
    assert roles[("NGC3031", "THINGS_HI_MOM0_NA")]["SizeBytes"] == "19465920"
    assert roles[("NGC3031", "SINGS_IRAC1_3p6um")]["SizeBytes"] == "42042240"
    assert all(
        row["RedistributionPolicy"] == "source_url_only_no_raw_redistribution"
        for row in manifest
    )

    with (PACKET / "things_route2_input_inventory_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert gates["R2INV01"]["Status"] == "at_least_two_primary_candidates_identified"
    assert gates["R2INV02"]["Status"] == "component_arrays_not_yet_derived"
    assert gates["R2INV03"]["Status"] == "N15_gate_still_blocked"
    assert all(row["CanScoreNow"] == "no" for row in gates.values())

    text = (PACKET / "things_route2_input_inventory_v01.md").read_text(
        encoding="utf-8"
    )
    assert "`NGC925`" in text
    assert "`NGC3031`" in text
    assert "not yet score-ready" in text


def test_things_route2_primary_inputs_are_staged_but_not_score_ready():
    with (PACKET / "things_route2_primary_input_staging_manifest_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 10
    assert {row["GalaxyName"] for row in rows} == {"NGC925", "NGC3031"}
    assert collections.Counter(row["SourceRole"] for row in rows) == {
        "THINGS_HI_MOM0_NA": 2,
        "THINGS_HI_MOM1_NA": 2,
        "THINGS_HI_MOM0_RO": 2,
        "THINGS_HI_MOM1_RO": 2,
        "SINGS_IRAC1_3P6UM": 2,
    }
    assert sum(int(row["SizeBytes"]) for row in rows) == 149967360
    assert all(row["Exists"] == "yes" for row in rows)
    assert all(row["GitTracked"] == "no" for row in rows)
    assert all(len(row["SHA256"]) == 64 for row in rows)
    assert all(
        row["RedistributionPolicy"] == "raw_file_ignored_source_url_and_checksum_only"
        for row in rows
    )

    with (PACKET / "things_route2_primary_input_staging_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert gates["R2STAGE01"]["Status"] == "primary_raw_inputs_staged_for_two_galaxies"
    assert gates["R2STAGE01"]["Galaxies"] == "NGC3031;NGC925"
    assert gates["R2STAGE01"]["CanScoreNow"] == "no"
    assert gates["R2STAGE02"]["Status"] == "raw_inputs_not_git_tracked"

    text = (PACKET / "things_route2_primary_input_staging_v01.md").read_text(
        encoding="utf-8"
    )
    assert "Staged files: 10" in text
    assert "Raw files are under `data/raw/`, which is ignored by git" in text
    assert "No `W_tau_eff` score is computed here" in text


def test_things_route2_fits_readiness_blocks_scoring_until_solver_freeze():
    with (PACKET / "things_route2_fits_header_readiness_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 10
    assert {row["GalaxyName"] for row in rows} == {"NGC925", "NGC3031"}
    assert collections.Counter(row["SourceRole"] for row in rows) == {
        "THINGS_HI_MOM0": 4,
        "THINGS_HI_MOM1": 4,
        "SINGS_IRAC1_3P6UM": 2,
    }
    assert all(row["HeaderReadable"] == "yes" for row in rows)
    assert all(row["GitTrackedRaw"] == "no" for row in rows)
    bunit_by_role = collections.defaultdict(set)
    for row in rows:
        bunit_by_role[row["SourceRole"]].add(row["BUNIT"])
    assert bunit_by_role["SINGS_IRAC1_3P6UM"] == {"MJy/sr"}
    assert bunit_by_role["THINGS_HI_MOM0"] == {"JY/B*M/S"}
    assert bunit_by_role["THINGS_HI_MOM1"] == {"METR/SEC"}

    with (PACKET / "things_route2_component_derivation_readiness_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert gates["R2FITS01"]["Status"] == (
        "fits_headers_readable_for_two_primary_galaxies"
    )
    assert gates["R2FITS01"]["CanDeriveComponentArraysNow"] == (
        "not_without_geometry_and_mass_model_solver"
    )
    assert gates["R2FITS02"]["Status"] == "source_units_identified"
    assert gates["R2FITS03"]["Status"] == "component_arrays_not_yet_derived"
    assert all(row["CanScoreNow"] == "no" for row in gates.values())

    text = (PACKET / "things_route2_fits_readiness_v01.md").read_text(
        encoding="utf-8"
    )
    assert "THINGS MOM0/MOM1 products are readable" in text
    assert "Component arrays are still not derived" in text
    assert "Apply a frozen disk-potential or external solver rule" in text


def test_things_route2_geometry_solver_policy_is_frozen_before_scoring():
    with (PACKET / "things_route2_geometry_policy_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        geometry = {row["GalaxyName"]: row for row in csv.DictReader(handle)}
    assert set(geometry) == {"NGC925", "NGC3031"}
    assert geometry["NGC925"]["DistanceMpc"] == "9.2"
    assert geometry["NGC925"]["InclinationDeg"] == "66.0"
    assert geometry["NGC925"]["PositionAngleDeg"] == "286.6"
    assert geometry["NGC925"]["VsysKms"] == "546.3"
    assert geometry["NGC3031"]["DistanceMpc"] == "3.6"
    assert geometry["NGC3031"]["InclinationDeg"] == "59.0"
    assert geometry["NGC3031"]["PositionAngleDeg"] == "330.2"
    assert geometry["NGC3031"]["VsysKms"] == "-39.8"
    assert geometry["NGC3031"]["AliasResolution"] == (
        "NGC3031_M81_header_alias_M81NORTH"
    )
    assert all(row["CanTuneAfterScore"] == "no" for row in geometry.values())
    assert all(
        row["ScoreUse"] == "frozen_geometry_seed_only_no_score_here"
        for row in geometry.values()
    )

    with (PACKET / "things_route2_surface_density_conversion_policy_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        conversions = {row["Component"]: row for row in csv.DictReader(handle)}
    assert conversions["HI_gas"]["InputBUNIT"] == "JY/B*M/S"
    assert conversions["HI_gas"]["MassFactor"] == "1.4"
    assert conversions["stellar_disk_NGC925"]["InputBUNIT"] == "MJy/sr"
    assert conversions["stellar_disk_NGC925"]["MLPolicy"] == (
        "disk_ML_3p6_equals_0p65_zero_bulge_candidate"
    )
    assert conversions["stellar_disk_and_central_component_NGC3031"]["MLPolicy"] == (
        "disk_ML_3p6_equals_0p8_central_component_ML_3p6_equals_1p0_mu0_12p2_h_0p25kpc"
    )
    assert all(row["CanTuneAfterScore"] == "no" for row in conversions.values())
    assert all(row["CanScoreNow"] == "no" for row in conversions.values())
    assert all("W_tau_eff" in row["ForbiddenInputs"] for row in conversions.values())

    with (PACKET / "things_route2_velocity_solver_policy_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        solvers = {row["SolverID"]: row for row in csv.DictReader(handle)}
    assert solvers["R2SOLVER01"]["ValidationRequirement"] == (
        "validate_against_existing_THINGS_SPARC_overlap_before_scoring_missing_galaxies"
    )
    assert solvers["R2SOLVER02"]["ValidationRequirement"] == (
        "must_reproduce_existing_SPARC_component_curves_with_predeclared_tolerance_before_use"
    )
    assert all(row["CanTuneAfterScore"] == "no" for row in solvers.values())
    assert all(row["CanScoreNow"] == "no" for row in solvers.values())
    assert all("W_tau_eff" in row["ForbiddenInputs"] for row in solvers.values())

    with (PACKET / "things_route2_geometry_solver_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert gates["R2SOLV01"]["Status"] == (
        "geometry_policy_frozen_for_NGC925_NGC3031"
    )
    assert gates["R2SOLV02"]["Status"] == "conversion_policy_frozen_not_implemented"
    assert gates["R2SOLV03"]["Status"] == (
        "velocity_solver_policy_frozen_requires_validation"
    )
    assert gates["R2SOLV04"]["Status"] == "component_arrays_still_absent"
    assert all(row["CanScoreNow"] == "no" for row in gates.values())

    text = (PACKET / "things_route2_geometry_solver_protocol_v01.md").read_text(
        encoding="utf-8"
    )
    assert "No component arrays are derived here" in text
    assert "No `W_tau_eff` score is computed here" in text
    assert "Validate the component-derivation solver on existing THINGS/SPARC overlap" in text


def test_things_route2_solver_validation_gate_blocks_missing_scores():
    with (PACKET / "things_route2_solver_validation_targets_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        targets = {row["GalaxyName"]: row for row in csv.DictReader(handle)}
    assert set(targets) == {
        "DDO154",
        "NGC2366",
        "NGC2403",
        "NGC2976",
        "NGC3198",
        "NGC5055",
        "NGC7331",
    }
    assert all(row["ExistingSparcReference"] == "yes" for row in targets.values())
    assert all(row["ExistingWtauEffSeed"] == "yes" for row in targets.values())
    assert all(
        row["ValidationUse"] == "solver_reconstruction_accuracy_only_not_tau_endpoint"
        for row in targets.values()
    )
    assert all(
        row["ForbiddenUse"] == "choose_solver_or_tolerance_by_W_tau_eff_direction"
        for row in targets.values()
    )
    assert all(row["CanScoreMissingGalaxiesNow"] == "no" for row in targets.values())

    with (PACKET / "things_route2_solver_validation_requirements_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        requirements = {row["RequirementID"]: row for row in csv.DictReader(handle)}
    assert requirements["R2VAL01"]["Requirement"] == "stage_validation_raw_inputs"
    assert requirements["R2VAL03"]["PassCondition"] == (
        "median_absolute_fractional_component_error_le_0p15_for_at_least_three_validation_galaxies"
    )
    assert all(
        row["FailureAction"] in {
            "do_not_apply_solver_to_NGC925_NGC3031",
            "revise_solver_only_before_any_missing_score_and_restart_validation",
            "keep_route2_as_not_score_ready",
        }
        for row in requirements.values()
    )
    assert all(
        row["CanScoreMissingGalaxiesNow"] == "no" for row in requirements.values()
    )

    with (PACKET / "things_route2_solver_validation_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert gates["R2VALG01"]["Status"] == (
        "validation_targets_defined_from_existing_THINGS_SPARC_overlap"
    )
    assert gates["R2VALG02"]["Status"] == "validation_raw_inputs_not_yet_staged"
    assert gates["R2VALG03"]["Status"] == "solver_not_yet_accuracy_validated"
    assert all(
        row["CanApplySolverToMissingGalaxies"] == "no" for row in gates.values()
    )
    assert all(row["CanScoreMissingGalaxiesNow"] == "no" for row in gates.values())

    text = (PACKET / "things_route2_solver_validation_gate_v01.md").read_text(
        encoding="utf-8"
    )
    assert "No missing-galaxy score may be computed from route 2" in text
    assert "No solver or tolerance may be selected using `W_tau_eff` direction" in text


def test_things_route2_solver_validation_inputs_are_staged_without_scores():
    with (
        PACKET / "things_route2_solver_validation_input_staging_manifest_v01.csv"
    ).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 6
    assert {row["GalaxyName"] for row in rows} == {"NGC2403", "NGC3198", "NGC5055"}
    assert collections.Counter(row["SourceRole"] for row in rows) == {
        "THINGS_HI_MOM0_NA": 3,
        "SINGS_IRAC1_3P6UM": 3,
    }
    assert all(row["Exists"] == "yes" for row in rows)
    assert all(row["GitTracked"] == "no" for row in rows)
    assert all(len(row["SHA256"]) == 64 for row in rows)
    assert all(
        row["RedistributionPolicy"] == "raw_file_ignored_source_url_and_checksum_only"
        for row in rows
    )
    assert all(
        row["ValidationUse"] == "solver_reconstruction_accuracy_only_not_tau_endpoint"
        for row in rows
    )
    assert all(row["CanScoreMissingGalaxiesNow"] == "no" for row in rows)

    with (
        PACKET / "things_route2_solver_validation_input_staging_gate_v01.csv"
    ).open(newline="", encoding="utf-8") as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert gates["R2VALSTAGE01"]["Status"] == (
        "validation_raw_inputs_staged_for_three_overlap_galaxies"
    )
    assert gates["R2VALSTAGE01"]["NCompleteGalaxies"] == "3"
    assert gates["R2VALSTAGE01"]["CanValidateSolverNow"] == "yes"
    assert gates["R2VALSTAGE01"]["CanScoreMissingGalaxiesNow"] == "no"
    assert gates["R2VALSTAGE02"]["Status"] == "validation_raw_inputs_not_git_tracked"

    text = (
        PACKET / "things_route2_solver_validation_input_staging_v01.md"
    ).read_text(encoding="utf-8")
    assert "Validation galaxies: `NGC2403`, `NGC3198`, `NGC5055`" in text
    assert "No missing-galaxy score is computed here" in text
    assert "No `W_tau_eff` endpoint is opened here" in text


def test_things_route2_solver_validation_fits_audit_blocks_missing_scores():
    with (PACKET / "things_route2_solver_validation_fits_header_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 6
    assert {row["GalaxyName"] for row in rows} == {"NGC2403", "NGC3198", "NGC5055"}
    assert collections.Counter(row["SourceRole"] for row in rows) == {
        "THINGS_HI_MOM0": 3,
        "SINGS_IRAC1_3P6UM": 3,
    }
    assert all(row["HeaderReadable"] == "yes" for row in rows)
    assert all(row["GitTrackedRaw"] == "no" for row in rows)
    assert all(row["CanScoreMissingGalaxiesNow"] == "no" for row in rows)
    bunit_by_role = collections.defaultdict(set)
    for row in rows:
        bunit_by_role[row["SourceRole"]].add(row["BUNIT"])
    assert bunit_by_role["THINGS_HI_MOM0"] == {"JY/B*M/S"}
    assert bunit_by_role["SINGS_IRAC1_3P6UM"] == {"MJy/sr"}

    with (PACKET / "things_route2_solver_validation_fits_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert gates["R2VALFITS01"]["Status"] == (
        "validation_fits_headers_readable_for_three_overlap_galaxies"
    )
    assert gates["R2VALFITS02"]["Status"] == "source_units_identified"
    assert gates["R2VALFITS03"]["Status"] == "component_arrays_not_yet_derived"
    assert all(row["CanScoreMissingGalaxiesNow"] == "no" for row in gates.values())

    text = (PACKET / "things_route2_solver_validation_fits_v01.md").read_text(
        encoding="utf-8"
    )
    assert "No component arrays are derived here" in text
    assert "No missing-galaxy score is computed here" in text


def test_things_route2_validation_surface_profiles_are_native_unit_only():
    with (PACKET / "things_route2_validation_surface_profiles_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) >= 60
    assert {row["GalaxyName"] for row in rows} == {"NGC2403", "NGC3198", "NGC5055"}
    assert {row["SourceRole"] for row in rows} == {
        "THINGS_HI_MOM0",
        "SINGS_IRAC1_3P6UM",
    }
    assert all(row["GitTrackedRaw"] == "no" for row in rows)
    assert all(row["CanScoreMissingGalaxiesNow"] == "no" for row in rows)
    assert all(
        row["ValidationUse"] == "surface_profile_extraction_only_not_velocity_solver"
        for row in rows
    )
    units = {(row["SourceRole"], row["InputBUNIT"]) for row in rows}
    assert ("THINGS_HI_MOM0", "JY/B*M/S") in units
    assert ("SINGS_IRAC1_3P6UM", "MJy/sr") in units

    with (PACKET / "things_route2_validation_surface_profile_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        summary = list(csv.DictReader(handle))
    assert len(summary) == 6
    assert all(row["ProfileStatus"] == "derived_native_unit_profile" for row in summary)
    assert all(int(row["NProfileBins"]) >= 5 for row in summary)
    assert all(row["CanScoreMissingGalaxiesNow"] == "no" for row in summary)

    with (PACKET / "things_route2_validation_surface_profile_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert gates["R2VALPROF01"]["Status"] == (
        "native_unit_surface_profiles_derived_for_three_validation_galaxies"
    )
    assert gates["R2VALPROF01"]["CanValidateSolverNow"] == (
        "not_until_native_profiles_are_converted_to_surface_density"
    )
    assert gates["R2VALPROF02"]["Status"] == "velocity_solver_not_run"
    assert all(row["CanScoreMissingGalaxiesNow"] == "no" for row in gates.values())

    text = (PACKET / "things_route2_validation_surface_profiles_v01.md").read_text(
        encoding="utf-8"
    )
    assert "No velocity component arrays are derived here" in text
    assert "No `W_tau_eff` endpoint is opened here" in text


def test_things_route2_validation_surface_density_conversion_is_not_solver():
    with (PACKET / "things_route2_validation_beam_conversion_audit_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        beams = {row["GalaxyName"]: row for row in csv.DictReader(handle)}
    assert set(beams) == {"NGC2403", "NGC3198", "NGC5055"}
    assert all(row["BeamParsed"] == "yes" for row in beams.values())
    assert all(row["BeamSource"] == "AIPS_CLEAN_HISTORY" for row in beams.values())
    assert all(float(row["BmajArcsec"]) > 0 for row in beams.values())
    assert all(float(row["BminArcsec"]) > 0 for row in beams.values())

    with (PACKET / "things_route2_validation_surface_density_profiles_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) >= 60
    assert {row["GalaxyName"] for row in rows} == {"NGC2403", "NGC3198", "NGC5055"}
    assert {row["SourceRole"] for row in rows} == {
        "THINGS_HI_MOM0",
        "SINGS_IRAC1_3P6UM",
    }
    assert all(
        row["ValidationUse"] == "surface_density_profile_only_not_velocity_solver"
        for row in rows
    )
    assert all(row["CanScoreMissingGalaxiesNow"] == "no" for row in rows)
    quantities = {row["ConvertedQuantity"] for row in rows}
    assert "SigmaGasWithHelium_MsunPc2" in quantities
    assert "I3p6_LsunPc2_AB_Msun6p02" in quantities

    with (PACKET / "things_route2_validation_surface_density_summary_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        summary = list(csv.DictReader(handle))
    assert len(summary) == 6
    assert all(
        row["ConversionStatus"] == "converted_surface_density_proxy"
        for row in summary
    )
    assert all(int(row["NConvertedBins"]) >= 5 for row in summary)

    with (PACKET / "things_route2_validation_surface_density_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert gates["R2VALDENS01"]["Status"] == (
        "surface_density_proxy_profiles_converted_for_three_validation_galaxies"
    )
    assert gates["R2VALDENS01"]["CanValidateSolverNow"] == (
        "not_until_velocity_solver_maps_surface_density_to_components"
    )
    assert gates["R2VALDENS02"]["Status"] == "velocity_solver_not_run"
    assert all(row["CanScoreMissingGalaxiesNow"] == "no" for row in gates.values())

    text = (PACKET / "things_route2_validation_surface_density_v01.md").read_text(
        encoding="utf-8"
    )
    assert "No velocity component arrays are derived here" in text
    assert "No `W_tau_eff` endpoint is opened here" in text


def test_things_route2_velocity_solver_validation_is_blocked_by_profile_check():
    with (
        PACKET / "things_route2_validation_sparc_surface_profile_metrics_v01.csv"
    ).open(newline="", encoding="utf-8") as handle:
        metrics = {row["GalaxyName"]: row for row in csv.DictReader(handle)}
    assert set(metrics) == {"NGC2403", "NGC3198", "NGC5055"}
    assert metrics["NGC2403"]["ValidationStatus"] == "fail_surface_profile_mismatch"
    assert metrics["NGC3198"]["ValidationStatus"] == "fail_surface_profile_mismatch"
    assert metrics["NGC5055"]["ValidationStatus"] == "fail_surface_profile_mismatch"
    assert all(row["CanRunVelocitySolverNow"] == "no" for row in metrics.values())
    assert all(row["CanScoreMissingGalaxiesNow"] == "no" for row in metrics.values())

    with (PACKET / "things_route2_velocity_solver_validation_gate_v01.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        gates = {row["GateID"]: row for row in csv.DictReader(handle)}
    assert gates["R2VELVAL01"]["Status"] == "surface_profile_reference_check_failed"
    assert gates["R2VELVAL01"]["CanRunVelocitySolverNow"] == "no"
    assert gates["R2VELVAL02"]["Status"] == "missing_galaxy_route2_scores_blocked"
    assert all(row["CanScoreMissingGalaxiesNow"] == "no" for row in gates.values())

    text = (PACKET / "things_route2_velocity_solver_validation_gate_v01.md").read_text(
        encoding="utf-8"
    )
    assert "not yet a validated route to SPARC-compatible stellar component curves" in text
    assert "No velocity component arrays are derived here" in text
    assert "No `W_tau_eff` endpoint is opened here" in text


def test_public_package_is_english_only():
    public_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [
            ROOT / "README.md",
            ROOT / "DATA_NOTICE.md",
            PACKET / "paper2_manuscript_skeleton.md",
            PACKET / "paper2_manuscript_draft.md",
            PACKET / "packet_manifest.json",
        ]
    )
    assert "_hu." not in public_text
    assert "laikusan" not in public_text.lower()
