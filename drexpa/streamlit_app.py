"""
DREXPA Streamlit Web App
A user-friendly interface for the DREXPA bioinformatics pipeline.
Users upload data → configure pipeline → execute → download results.
"""

import streamlit as st
import pandas as pd
import tempfile
import shutil
from pathlib import Path

from drexpa.app_utils.file_handlers import validate_and_preview_files, get_file_summary
from drexpa.app_utils.pipeline_runner import build_config, run_pipeline_with_progress
from drexpa.app_utils.visualizations import plot_targets_per_drug, plot_drug_target_heatmap, plot_network_diagram

# Page configuration
st.set_page_config(
    page_title="DREXPA Pipeline",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}
if "pipeline_results" not in st.session_state:
    st.session_state.pipeline_results = None
if "config" not in st.session_state:
    st.session_state.config = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Sidebar navigation
st.sidebar.title("🧬 DREXPA Pipeline")
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Upload Data", "Configuration", "Execute Pipeline", "Results"],
    key="nav_radio"
)
st.session_state.current_page = page

# ============================================================================
# PAGE: HOME
# ============================================================================
if page == "Home":
    st.title("🧬 DREXPA Web Application")
    st.markdown("""
    ### Convert Drug Screening Data into Drug Panels and Perturbation Files

    **DREXPA** (DRug EXperimental PAnel) is a bioinformatics pipeline that transforms
    experimental drug screening datasets into:
    - Drug panels in DrugLogics format
    - Perturbation files for in silico validation
    - Gene-target interactions
    - Drug profiles with unique identifiers

    #### How to Use
    1. **Upload Data** - Provide drug names, screening results, and gene mappings
    2. **Configure** - Choose pipeline steps and fine-tune parameters
    3. **Execute** - Run the pipeline and track progress
    4. **Download** - Get all output files and visualizations

    #### What You Need
    - `drug_names.txt` - One drug name per line
    - `synergy_data.csv` - Drug combination screening results
    - `node_dict.csv` - Gene symbol → Logical node mapping
    - Optional: `tissue_cline.csv` - Tissue/cell line info
    - Optional: `manual_chembl.csv` - Pre-mapped ChEMBL IDs

    #### Quick Start
    👉 Go to **Upload Data** to get started!
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📤 **Upload Data**\nAdd your input files")
    with col2:
        st.info("⚙️ **Configure**\nCustomize pipeline options")
    with col3:
        st.info("🚀 **Run**\nExecute and download results")

# ============================================================================
# PAGE: UPLOAD DATA
# ============================================================================
elif page == "Upload Data":
    st.title("📤 Upload Your Data")
    st.markdown("Choose how to provide files for the DREXPA pipeline:")

    # Tab selection: Upload or Directory
    input_method = st.radio(
        "Input Method",
        ["📁 Upload Files", "📂 Use Local Directory"],
        horizontal=True
    )

    files_dict = {
        "drug_names_file": None,
        "synergy_data_file": None,
        "node_dict_file": None,
        "tissue_cline_file": None,
        "manual_chembl_file": None,
    }

    if input_method == "📁 Upload Files":
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Required Files")
            drug_names_file = st.file_uploader(
                "Drug Names (drug_names.txt)",
                type=["txt"],
                help="One drug name per line"
            )

            synergy_data_file = st.file_uploader(
                "Synergy Data (synergy_data.csv)",
                type=["csv"],
                help="Drug combination screening results"
            )

            node_dict_file = st.file_uploader(
                "Node Dictionary (node_dict.csv)",
                type=["csv"],
                help="Gene symbol → Node mapping"
            )

        with col2:
            st.subheader("Optional Files")
            tissue_cline_file = st.file_uploader(
                "Tissue/Cell Line (tissue_cline.csv)",
                type=["csv"],
                help="Maps cell lines to tissues"
            )

            manual_chembl_file = st.file_uploader(
                "Manual ChEMBL (manual_chembl.csv)",
                type=["csv"],
                help="Pre-mapped ChEMBL IDs"
            )

        files_dict = {
            "drug_names_file": drug_names_file,
            "synergy_data_file": synergy_data_file,
            "node_dict_file": node_dict_file,
            "tissue_cline_file": tissue_cline_file,
            "manual_chembl_file": manual_chembl_file,
        }

    else:  # Use Local Directory
        st.subheader("Local Directory Path")
        data_dir = st.text_input(
            "Full path to directory containing data files",
            placeholder="/home/user/my_data or C:\\Users\\user\\my_data",
            help="Enter the absolute path to your data directory"
        )

        if data_dir:
            data_path = Path(data_dir)
            if not data_path.exists():
                st.error(f"❌ Directory does not exist: {data_dir}")
            else:
                st.success(f"✓ Directory found: {data_dir}")

                # Look for files in the directory
                st.subheader("Files Found in Directory")
                found_files = {
                    "drug_names_file": None,
                    "synergy_data_file": None,
                    "node_dict_file": None,
                    "tissue_cline_file": None,
                    "manual_chembl_file": None,
                }

                # Map common filenames
                filename_patterns = {
                    "drug_names_file": ["drug_names.txt", "drug_list.txt", "drugs.txt"],
                    "synergy_data_file": ["synergy_data.csv", "synergy.csv", "screening.csv"],
                    "node_dict_file": ["node_dict.csv", "nodes.csv", "gene_mapping.csv"],
                    "tissue_cline_file": ["tissue_cline.csv", "cell_lines.csv"],
                    "manual_chembl_file": ["manual_chembl.csv", "chembl_ids.csv"],
                }

                for file_type, patterns in filename_patterns.items():
                    for pattern in patterns:
                        filepath = data_path / pattern
                        if filepath.exists():
                            found_files[file_type] = str(filepath)
                            is_required = file_type != "tissue_cline_file" and file_type != "manual_chembl_file"
                            marker = "✓" if is_required else "○"
                            st.write(f"{marker} {pattern}")
                            break

                files_dict = found_files

    # Store files in session state
    st.session_state.uploaded_files = files_dict

    # Validation and preview
    st.subheader("File Preview & Validation")
    if files_dict["drug_names_file"] or files_dict["synergy_data_file"] or files_dict["node_dict_file"]:
        validation_ok, messages = validate_and_preview_files(files_dict)

        for msg in messages:
            if "✓" in msg:
                st.success(msg)
            elif "✗" in msg:
                st.error(msg)
            else:
                st.info(msg)

        if validation_ok:
            st.success("✅ All required files are ready! Proceed to Configuration.")
        else:
            st.warning("⚠️ Some required files are missing.")
    else:
        st.info("Upload files or select a directory to see preview and validation")

# ============================================================================
# PAGE: CONFIGURATION
# ============================================================================
elif page == "Configuration":
    st.title("⚙️ Pipeline Configuration")

    if not st.session_state.uploaded_files.get("drug_names_file"):
        st.error("❌ Please upload files first (Upload Data page)")
    else:
        config = {}

        # Global Options (Sidebar)
        st.sidebar.subheader("Global Options")
        output_dir = st.sidebar.text_input(
            "Output Directory",
            value="drexpa",
            help="Where to save pipeline results (relative to workspace)"
        )
        verbose = st.sidebar.checkbox("Verbose Logging", value=False)
        save_files = st.sidebar.checkbox("Save Output Files", value=True)

        config["global"] = {
            "output_dir": output_dir,
            "base_data_dir": ".",
            "verbose": verbose,
            "save": save_files,
        }

        # Pipeline Steps
        st.subheader("Pipeline Steps to Run")
        st.markdown("Select which steps to execute (dependencies auto-resolved):")

        steps = [
            "load_data",
            "chembl_ids",
            "doses",
            "targets",
            "node_targets",
            "profiles",
            "combinations",
            "panel",
            "perturbations",
            "synergies",
        ]

        cols = st.columns(2)
        selected_steps = []
        for idx, step in enumerate(steps):
            col = cols[idx % 2]
            if col.checkbox(step, value=(idx < 6)):  # Default: first 6 steps
                selected_steps.append(step)

        config["selected_steps"] = selected_steps

        # Pipeline Options (Expandable)
        with st.expander("📋 Pipeline Options"):
            col1, col2 = st.columns(2)

            with col1:
                synergy_threshold = st.slider(
                    "Synergy Threshold",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.0,
                    step=0.05,
                    help="Minimum synergy effect to include"
                )

            with col2:
                double_drug = st.checkbox(
                    "Double Drug Screen",
                    value=True,
                    help="Include 2-drug combinations"
                )

            target_merge = st.selectbox(
                "Target Merge Strategy",
                ["fill_missing", "keep_original"],
                help="How to handle missing targets"
            )

            config["options"] = {
                "synergy_threshold": synergy_threshold,
                "double_drug_screen": double_drug,
                "original_target_merge": target_merge,
            }

        # Column Names (Advanced)
        with st.expander("🔧 Advanced: Column Names"):
            st.markdown("Customize column names if your data differs from defaults:")

            col1, col2, col3 = st.columns(3)
            with col1:
                drug_name_col = st.text_input("Drug Name Column", value="drug_name")
                drug_a_col = st.text_input("Drug A Column", value="drug_name_A")
                drug_b_col = st.text_input("Drug B Column", value="drug_name_B")

            with col2:
                conc_a_col = st.text_input("Concentration A", value="conc_A")
                conc_b_col = st.text_input("Concentration B", value="conc_B")
                cell_line_col = st.text_input("Cell Line Column", value="cell_line")

            with col3:
                synergy_col = st.text_input("Synergy Column", value="synergy")
                tissue_col = st.text_input("Tissue Column", value="tissue")
                chembl_col = st.text_input("ChEMBL ID Column", value="chembl_id")

            config["columns"] = {
                "drug_name": drug_name_col,
                "drug_name_A": drug_a_col,
                "drug_name_B": drug_b_col,
                "conc_A": conc_a_col,
                "conc_B": conc_b_col,
                "cell_line": cell_line_col,
                "synergy": synergy_col,
                "tissue": tissue_col,
                "chembl_id": chembl_col,
            }

        # Preview config
        st.subheader("Configuration Summary")
        st.json(config)

        # Save config to session
        st.session_state.config = config
        st.success("✅ Configuration ready. Proceed to Execute Pipeline.")

# ============================================================================
# PAGE: EXECUTE PIPELINE
# ============================================================================
elif page == "Execute Pipeline":
    st.title("🚀 Execute Pipeline")

    if not st.session_state.config:
        st.error("❌ Please configure the pipeline first (Configuration page)")
    else:
        st.markdown("Click the button below to start the pipeline execution:")

        if st.button("▶️ Run Pipeline", key="run_button", use_container_width=True):
            with st.spinner("Setting up pipeline..."):
                # Create temp directory for files
                temp_dir = tempfile.mkdtemp()
                try:
                    # Write uploaded files to temp directory
                    files_info = {}

                    if st.session_state.uploaded_files["drug_names_file"]:
                        path = Path(temp_dir) / "drug_names.txt"
                        path.write_bytes(st.session_state.uploaded_files["drug_names_file"].read())
                        files_info["drug_names_file"] = str(path)

                    if st.session_state.uploaded_files["synergy_data_file"]:
                        path = Path(temp_dir) / "synergy_data.csv"
                        path.write_bytes(st.session_state.uploaded_files["synergy_data_file"].read())
                        files_info["synergy_data_file"] = str(path)

                    if st.session_state.uploaded_files["node_dict_file"]:
                        path = Path(temp_dir) / "node_dict.csv"
                        path.write_bytes(st.session_state.uploaded_files["node_dict_file"].read())
                        files_info["node_dict_file"] = str(path)

                    if st.session_state.uploaded_files["tissue_cline_file"]:
                        path = Path(temp_dir) / "tissue_cline.csv"
                        path.write_bytes(st.session_state.uploaded_files["tissue_cline_file"].read())
                        files_info["tissue_cline_file"] = str(path)

                    if st.session_state.uploaded_files["manual_chembl_file"]:
                        path = Path(temp_dir) / "manual_chembl.csv"
                        path.write_bytes(st.session_state.uploaded_files["manual_chembl_file"].read())
                        files_info["manual_chembl_file"] = str(path)

                    # Progress placeholder
                    progress_placeholder = st.empty()
                    log_placeholder = st.empty()

                    # Run pipeline
                    success, results, error_msg = run_pipeline_with_progress(
                        st.session_state.config,
                        files_info,
                        temp_dir,
                        progress_placeholder,
                        log_placeholder
                    )

                    if success:
                        st.session_state.pipeline_results = results
                        st.success("✅ Pipeline completed successfully!")
                        st.info("📊 Go to Results page to view output and download files")
                    else:
                        st.error(f"❌ Pipeline failed: {error_msg}")

                finally:
                    # Keep temp_dir for results page, will clean up later
                    pass

# ============================================================================
# PAGE: RESULTS
# ============================================================================
elif page == "Results":
    st.title("📊 Pipeline Results")

    if st.session_state.pipeline_results is None:
        st.info("⏳ Run the pipeline first to see results")
    else:
        results = st.session_state.pipeline_results

        # Summary Statistics
        st.subheader("📈 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Drugs Processed", results.get("n_drugs", 0))
        with col2:
            st.metric("Unique Profiles", results.get("n_profiles", 0))
        with col3:
            st.metric("Perturbation Files", results.get("n_perturbations", 0))
        with col4:
            st.metric("Execution Time", f"{results.get('execution_time', 0):.1f}s")

        # DataFrames Display
        st.subheader("📋 Results Tables")

        tabs = st.tabs([
            "Profiles",
            "Panel",
            "Targets",
            "Node Targets",
            "ChEMBL IDs",
        ])

        with tabs[0]:
            if "drug_profiles" in results:
                st.dataframe(results["drug_profiles"], use_container_width=True)
                csv = results["drug_profiles"].to_csv(index=False)
                st.download_button(
                    "⬇️ Download drug_profiles.csv",
                    csv,
                    "drug_profiles.csv",
                    "text/csv",
                )

        with tabs[1]:
            if "drug_panel" in results:
                st.dataframe(results["drug_panel"], use_container_width=True)
                csv = results["drug_panel"].to_csv(index=False)
                st.download_button(
                    "⬇️ Download drug_panel_df.csv",
                    csv,
                    "drug_panel_df.csv",
                    "text/csv",
                )

        with tabs[2]:
            if "drug_targets" in results:
                st.dataframe(results["drug_targets"], use_container_width=True)
                csv = results["drug_targets"].to_csv(index=False)
                st.download_button(
                    "⬇️ Download drug_ChEMBL_targets.csv",
                    csv,
                    "drug_ChEMBL_targets.csv",
                    "text/csv",
                )

        with tabs[3]:
            if "drug_node_targets" in results:
                st.dataframe(results["drug_node_targets"], use_container_width=True)
                csv = results["drug_node_targets"].to_csv(index=False)
                st.download_button(
                    "⬇️ Download drug_node_targets.csv",
                    csv,
                    "drug_node_targets.csv",
                    "text/csv",
                )

        with tabs[4]:
            if "drug_chembl_ids" in results:
                st.dataframe(results["drug_chembl_ids"], use_container_width=True)
                csv = results["drug_chembl_ids"].to_csv(index=False)
                st.download_button(
                    "⬇️ Download drug_ChEMBL_IDs.csv",
                    csv,
                    "drug_ChEMBL_IDs.csv",
                    "text/csv",
                )

        # Visualizations
        st.subheader("📊 Visualizations")

        viz_tabs = st.tabs(["Targets per Drug", "Drug-Target Heatmap", "Network"])

        with viz_tabs[0]:
            if "drug_targets" in results:
                fig = plot_targets_per_drug(results["drug_targets"])
                st.plotly_chart(fig, use_container_width=True)

        with viz_tabs[1]:
            if "drug_targets" in results:
                fig = plot_drug_target_heatmap(results["drug_targets"])
                st.plotly_chart(fig, use_container_width=True)

        with viz_tabs[2]:
            if "drug_targets" in results:
                fig = plot_network_diagram(results["drug_targets"])
                st.plotly_chart(fig, use_container_width=True)

        # Download All
        st.subheader("📥 Download All Results")
        if st.button("📦 Prepare ZIP Download", key="download_all"):
            # TODO: Implement zip download
            st.info("ZIP download functionality coming soon")

        # Reset
        if st.button("🔄 Start New Analysis", key="reset_button"):
            st.session_state.pipeline_results = None
            st.session_state.uploaded_files = {}
            st.session_state.config = None
            st.rerun()
