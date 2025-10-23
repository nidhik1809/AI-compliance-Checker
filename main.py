import streamlit as st
import agreement_comparison
import data_extraction
import json
import notification
import os

# Mapping of agreement type to respective JSON file
AGREEMENT_JSON_MAP = {
    "Data Processing Agreement": "dpa.json",
    "Joint Controller Agreement": "jca.json",
    "Controller-to-Controller Agreement": "c2c.json",
    "Processor-to-Subprocessor Agreement": "subprocessor.json",
    "Standard Contractual Clauses": "scc.json"
}

st.title("📄 Contract Compliance Checker")

try:
    # File upload
    uploaded_file = st.file_uploader("Upload an agreement (PDF only)", type=["pdf"])

    if uploaded_file is not None:
        # Save uploaded file temporarily
        with open("temp_uploaded.pdf", "wb") as f:
            f.write(uploaded_file.read())
        st.info("Processing your file...")

        # Step 1: Identify the type of agreement
        agreement_type = agreement_comparison.document_type("temp_uploaded.pdf")
        st.write("**Detected Document Type:**", agreement_type)

        if agreement_type in AGREEMENT_JSON_MAP:
            # Step 2: Extract clauses
            unseen_data = data_extraction.clause_extraction("temp_uploaded.pdf")
            st.write("**Clause Extraction Completed:**")

            # Step 3: Load the respective template JSON
            template_file = AGREEMENT_JSON_MAP[agreement_type]
            with open(f"templates/{template_file}", "r", encoding="utf-8") as f:
                template_data = json.load(f)

            # Step 4: Compare agreements
            result = agreement_comparison.compare_agreements(unseen_data, template_data)

            # Show results
            st.subheader("📊 Comparison Result")
            st.write(result)
            
            # Send notifications
            body = f"Agreement type is {agreement_type}\nComparison Result: {result}"
            notification.send_notification("Comparison Result", body)
            
            # Slack notification with error handling
            webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
            if webhook_url:
                notification.send_slack_notification(body, webhook_url)
            else:
                st.warning("Slack webhook URL not configured")

        else:
            msg = f"No template found for detected type: {agreement_type}"
            st.error(msg)
            notification.send_notification("Compliance Checker Error", msg)

except Exception as e:
    error_msg = f"Error Occurred in document comparison: {e}"
    st.error(error_msg)
    notification.send_notification("Compliance Checker Error", error_msg)
    
    # Slack notification for errors with error handling
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if webhook_url:
        notification.send_slack_notification(error_msg, webhook_url)