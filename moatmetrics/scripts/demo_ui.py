"""
MoatMetrics Demo UI - A Streamlit-based interface for non-technical users
Enhanced with better error handling and debugging - Updated to fix deprecation warnings
"""
import streamlit as st
import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional, Any
import traceback

# Configuration
API_BASE_URL = "http://localhost:8000"
st.set_page_config(page_title="MoatMetrics Demo", layout="wide")

# Session state initialization
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'viewer'  # Default role
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False
if 'ai_status_checked' not in st.session_state:
    st.session_state.ai_status_checked = False
if 'ai_system_status' not in st.session_state:
    st.session_state.ai_system_status = None
if 'ai_models_status' not in st.session_state:
    st.session_state.ai_models_status = None

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #2c3e50; margin-bottom: 1rem;}
    .section-header {font-size: 1.8rem; color: #3498db; margin: 1.5rem 0 1rem 0;}
    .metric-card {border-radius: 10px; padding: 15px; margin: 10px 0; background: #f8f9fa;}
    .success {color: #27ae60;}
    .warning {color: #f39c12;}
    .danger {color: #e74c3c;}
    .debug-info {background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;}
</style>
""", unsafe_allow_html=True)

def debug_log(message: str, data: Any = None):
    """Debug logging function"""
    if st.session_state.get('debug_mode', False):
        st.sidebar.write(f"🛠 **Debug:** {message}")
        if data is not None:
            st.sidebar.json(data)

def ensure_approved_model_loaded():
    """Ensure approved model (tinyllama) is loaded before showing AI features"""
    try:
        # Check if AI system is available
        ai_health = make_api_call("/api/ai/health", "GET")
        if not ai_health or ai_health.get('status') != 'healthy':
            return False, "AI system not available"
        
        # Try to load approved model
        approved_model = 'tinyllama'
        load_result = make_api_call(f"/api/ai/models/{approved_model}/load", "POST")
        
        if load_result and load_result.get('success'):
            return True, f"Approved model '{approved_model}' loaded successfully"
        else:
            return False, f"Failed to load approved model '{approved_model}'"
            
    except Exception as e:
        debug_log("Error ensuring approved model is loaded", {"error": str(e)})
        return False, f"Error loading approved model: {str(e)}"

def check_ai_system_status():
    """Check AI system status and cache results"""
    if st.session_state.ai_status_checked:
        return st.session_state.ai_system_status, st.session_state.ai_models_status
    
    # Check AI system health
    ai_health = make_api_call("/api/ai/health", "GET")
    ai_system_status = None
    
    if ai_health:
        ai_system_status = {
            'status': ai_health.get('status', 'unknown'),
            'message': ai_health.get('message', 'No message'),
            'services': ai_health.get('services', {}),
            'timestamp': ai_health.get('timestamp', 'unknown')
        }
    
    # Check AI models if system is operational
    ai_models_status = None
    if ai_system_status and ai_system_status['status'] in ['healthy', 'degraded']:
        models_info = make_api_call("/api/ai/models", "GET")
        if models_info and models_info.get('success'):
            ai_models_status = {
                'total_models': models_info.get('total_models', 0),
                'hardware_tier': models_info.get('hardware_tier', 'unknown'),
                'models': models_info.get('models', [])
            }
    
    # Cache the results
    st.session_state.ai_status_checked = True
    st.session_state.ai_system_status = ai_system_status
    st.session_state.ai_models_status = ai_models_status
    
    return ai_system_status, ai_models_status

def display_ai_status_sidebar():
    """Display AI system status in sidebar"""
    ai_system_status, ai_models_status = check_ai_system_status()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 AI System Status")
    
    if ai_system_status:
        status = ai_system_status['status']
        if status == 'healthy':
            st.sidebar.success("✅ AI System: Operational")
        elif status == 'degraded':
            st.sidebar.warning("⚠️ AI System: Degraded")
        elif status == 'not_initialized':
            st.sidebar.info("🔄 AI System: Not Initialized")
        else:
            st.sidebar.error("❌ AI System: Error")
        
        # Show service status
        services = ai_system_status.get('services', {})
        if services:
            ollama_status = services.get('ollama', False)
            if ollama_status:
                st.sidebar.success("🦙 Ollama: Connected")
            else:
                st.sidebar.error("🦙 Ollama: Disconnected")
                st.sidebar.info("💡 Install Ollama for full AI features")
        
        # Show models status if available
        if ai_models_status:
            total_models = ai_models_status.get('total_models', 0)
            hardware_tier = ai_models_status.get('hardware_tier', 'unknown')
            st.sidebar.info(f"🧠 Models: {total_models} available")
            st.sidebar.info(f"💻 Hardware: {hardware_tier} tier")
            
            # Show model details
            models = ai_models_status.get('models', [])
            if models:
                available_models = [m['name'] for m in models if m['status'] == 'available']
                if available_models:
                    st.sidebar.success(f"📦 Available: {', '.join(available_models)}")
                else:
                    st.sidebar.warning("📦 No models available")
        
        # Refresh button
        if st.sidebar.button("🔄 Refresh AI Status"):
            st.session_state.ai_status_checked = False
            st.rerun()
    else:
        st.sidebar.error("❌ Cannot connect to AI system")
        st.sidebar.info("🚀 Make sure MoatMetrics API is running")
        
        if st.sidebar.button("🔄 Retry Connection"):
            st.session_state.ai_status_checked = False
            st.rerun()

def make_api_call(endpoint: str, method: str = "GET", data: Optional[Dict] = None, files: Optional[Dict] = None) -> Any:
    """Helper function to make authenticated API calls with enhanced error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    # Add auth token if available
    if st.session_state.get('auth_token'):
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    
    debug_log(f"Making {method} request to: {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data, timeout=30)  # Increased from 10 to 30 seconds
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, data=data, headers=headers, timeout=60)  # Increased from 30 to 60 seconds
            else:
                response = requests.post(url, json=data, headers=headers, timeout=60)  # Increased from 30 to 60 seconds
        
        debug_log(f"Response status: {response.status_code}")
        
        response.raise_for_status()
        result = response.json()
        debug_log("API Response received", result if isinstance(result, dict) and len(str(result)) < 1000 else "Large response data")
        return result
        
    except requests.exceptions.ConnectionError:
        st.error(f"🔌 Cannot connect to API server at {API_BASE_URL}. Is the server running?")
        st.info("💡 Make sure your FastAPI server is running on port 8000")
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The server might be slow to respond.")
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error occurred: {http_err}"
        try:
            if http_err.response.headers.get('content-type') == 'application/json':
                error_detail = http_err.response.json().get('detail', str(http_err))
                error_msg = f"API Error: {error_detail}"
        except:
            pass
        st.error(error_msg)
        debug_log("HTTP Error details", {"status": http_err.response.status_code, "text": http_err.response.text})
    except json.JSONDecodeError:
        st.error("📄 Server returned invalid JSON response")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        debug_log("Exception details", {"error": str(e), "traceback": traceback.format_exc()})
    
    return None

def show_dashboard():
    """Main dashboard view with enhanced error handling"""
    st.markdown("<h1 class='main-header'>MoatMetrics Dashboard</h1>", unsafe_allow_html=True)
    
    # Check if user is authenticated
    if not st.session_state.get('auth_token'):
        st.warning("Please log in to view the dashboard")
        return
    
    # Test API connection first
    with st.expander("🔧 API Connection Test", expanded=False):
        if st.button("Test API Connection"):
            with st.spinner("Testing API connection..."):
                health_check = make_api_call("/health", "GET")
                if health_check:
                    st.success("✅ API connection successful!")
                    st.json(health_check)
                else:
                    st.error("❌ API connection failed")
    
    try:
        # Fetch client data from API
        with st.spinner("Loading client data..."):
            debug_log("Fetching clients data...")
            clients_data = make_api_call("/api/clients", "GET")
            
        if clients_data is not None:
            debug_log("Processing clients data", {"type": type(clients_data), "length": len(clients_data) if isinstance(clients_data, list) else "Not a list"})
            
            # Handle different response formats
            if isinstance(clients_data, dict):
                # If response is wrapped in an object
                if 'clients' in clients_data:
                    clients_list = clients_data['clients']
                elif 'data' in clients_data:
                    clients_list = clients_data['data']
                else:
                    # If it's a single client object
                    clients_list = [clients_data]
            elif isinstance(clients_data, list):
                clients_list = clients_data
            else:
                st.error("Unexpected response format from API")
                st.json(clients_data)
                return
            
            if not clients_list:
                st.info("🔭 No client data available")
                return
            
            # Process clients data with flexible field mapping
            processed_clients = []
            for i, client in enumerate(clients_list):
                if not isinstance(client, dict):
                    debug_log(f"Client {i} is not a dict", client)
                    continue
                
                # Flexible field mapping
                client_data = {
                    'ID': client.get('id') or client.get('client_id') or client.get('_id') or f"client_{i}",
                    'Name': client.get('name') or client.get('client_name') or client.get('company_name') or 'Unknown',
                    'Status': client.get('status') or client.get('is_active', True) and 'Active' or 'Inactive',
                    'Last Updated': client.get('updated_at') or client.get('last_updated') or client.get('modified_date') or 'N/A'
                }
                processed_clients.append(client_data)
            
            # Convert to DataFrame for display
            clients_df = pd.DataFrame(processed_clients)
            
            # Display metrics
            st.markdown("<h2 class='section-header'>📊 Client Overview</h2>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Clients", len(clients_df))
            with col2:
                active_clients = len(clients_df[clients_df['Status'] == 'Active'])
                st.metric("Active Clients", active_clients)
            with col3:
                completion_rate = f"{(active_clients / len(clients_df) * 100):.1f}%" if len(clients_df) > 0 else "0%"
                st.metric("Active Rate", completion_rate)
            
            # Display clients table
            st.markdown("### 📋 Client Details")
            st.dataframe(
                clients_df,
                width='stretch',  # Fixed deprecation warning
                column_config={
                    "ID": st.column_config.TextColumn("ID", width="small"),
                    "Name": st.column_config.TextColumn("Client Name", width="medium"),
                    "Status": st.column_config.SelectboxColumn("Status", options=["Active", "Inactive", "Prospect"]),
                    "Last Updated": st.column_config.TextColumn("Last Updated", width="medium")
                },
                hide_index=True
            )
        else:
            st.warning("⚠️ Could not load client data. Please check your API connection.")
        
        # Fetch and display analytics
        with st.expander("📈 View Analytics", expanded=False):
            st.markdown("<h3>Analytics Overview</h3>", unsafe_allow_html=True)
            
            # Get analytics results
            analytics_data = make_api_call("/api/analytics/results", "GET", {"limit": 5})
            
            if analytics_data:
                if isinstance(analytics_data, list) and analytics_data:
                    analytics_df = pd.DataFrame(analytics_data)
                    st.dataframe(analytics_df, width='stretch')  # Fixed deprecation warning
                else:
                    st.info("📊 Analytics data structure:")
                    st.json(analytics_data)
            else:
                st.info("📈 No analytics data available. Run analytics first.")
                
                if st.button("🚀 Run Analytics"):
                    with st.spinner("Running analytics..."):
                        result = make_api_call(
                            "/api/analytics/run", 
                            "POST",
                            {"client_id": None, "metrics": ["profitability", "utilization"]}
                        )
                        if result:
                            st.success("✅ Analytics completed successfully!")
                            st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error loading dashboard data: {str(e)}")
        debug_log("Dashboard error details", {"error": str(e), "traceback": traceback.format_exc()})
        
        # Show raw API response for debugging
        if st.session_state.get('debug_mode'):
            st.markdown("### 🛠 Debug Information")
            with st.expander("Raw API Response"):
                try:
                    raw_response = make_api_call("/api/clients", "GET")
                    st.json(raw_response)
                except:
                    st.write("Could not fetch raw response")

def show_data_upload():
    """Data upload view with enhanced error handling"""
    st.markdown("<h1 class='main-header'>📤 Data Upload</h1>", unsafe_allow_html=True)
    
    if not st.session_state.get('auth_token'):
        st.warning("Please log in to upload data")
        return
    
    st.markdown("""
    Upload your client, invoice, or time tracking data in CSV format.
    The system will automatically process and analyze the data.
    """)
    
    # Data type mapping to API endpoints
    data_type_mapping = {
        "Clients": "clients",
        "Invoices": "invoices", 
        "Time Logs": "time_logs",
        "Licenses": "licenses"
    }
    
    col1, col2 = st.columns([2, 1])
    with col1:
        file_type = st.selectbox("Select Data Type", list(data_type_mapping.keys()))
    with col2:
        st.info(f"📁 Endpoint: `/api/upload/{data_type_mapping[file_type]}`")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file", 
        type=["csv", "xlsx", "xls"],
        help="Maximum file size: 200MB"
    )
    
    if uploaded_file is not None:
        # Show file info
        st.success(f"✅ File selected: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Show file preview
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, nrows=100)  # Limit preview rows
            else:  # Excel
                df = pd.read_excel(uploaded_file, nrows=100)
            
            st.write("📋 File Preview (first 100 rows):")
            st.dataframe(df.head(), width='stretch')  # Fixed deprecation warning
            
            # Show file statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")
            
            # Upload options
            with st.expander("⚙️ Upload Options"):
                validate_schema = st.checkbox("Validate Schema", value=True, help="Check if data matches expected format")
                create_snapshot = st.checkbox("Create Snapshot", value=True, help="Save a backup before processing")
                dry_run = st.checkbox("Dry Run (Validate Only)", value=False, help="Test upload without saving data")
            
            # Upload button
            col1, col2 = st.columns([1, 3])
            with col1:
                upload_btn = st.button("📤 Upload & Process", type="primary", width='stretch')  # Fixed deprecation warning
            with col2:
                if dry_run:
                    st.info("🧪 Dry run mode: Data will be validated but not saved")
            
            if upload_btn:
                with st.spinner("Uploading and processing your data..."):
                    try:
                        # Reset file pointer
                        uploaded_file.seek(0)
                        
                        # Prepare the file for upload
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {
                            "validate_schema": str(validate_schema).lower(),
                            "create_snapshot": str(create_snapshot).lower(),
                            "dry_run": str(dry_run).lower()
                        }
                        
                        debug_log(f"Uploading to: /api/upload/{data_type_mapping[file_type]}", data)
                        
                        # Make the API call
                        response = make_api_call(
                            f"/api/upload/{data_type_mapping[file_type]}",
                            "POST",
                            data=data,
                            files=files
                        )
                        
                        if response:
                            if dry_run:
                                st.success("🧪 Validation completed successfully!")
                            else:
                                st.success("✅ Data uploaded and processed successfully!")
                            
                            # Show response details
                            with st.expander("📋 Upload Results"):
                                st.json(response)
                            
                            if not dry_run:
                                st.balloons()
                    
                    except Exception as e:
                        st.error(f"❌ Error during upload: {str(e)}")
                        debug_log("Upload error", {"error": str(e), "traceback": traceback.format_exc()})
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.info("💡 Make sure the file is a valid CSV or Excel file")

def show_reports():
    """Reports view with enhanced error handling"""
    st.markdown("<h1 class='main-header'>📄 Reports</h1>", unsafe_allow_html=True)
    
    if not st.session_state.get('auth_token'):
        st.warning("Please log in to generate reports")
        return
    
    # Available report types from the API
    report_types = [
        "Client Profitability",
        "Resource Utilization", 
        "License Optimization",
        "Financial Summary",
        "Compliance Report"
    ]
    
    # Report parameters
    col1, col2 = st.columns([3, 1])
    with col1:
        report_type = st.selectbox("Select Report Type", report_types)
    with col2:
        date_range = st.selectbox(
            "Time Period",
            ["Last 30 Days", "Last Quarter", "Last 6 Months", "This Year", "Custom Range"]
        )
    
    # Additional filters based on report type
    selected_client = None
    if report_type == "Client Profitability":
        clients = make_api_call("/api/clients", "GET") or []
        if isinstance(clients, list) and clients:
            client_options = ["All Clients"] + [
                client.get('name', f"Client {i}") for i, client in enumerate(clients)
            ]
            selected_client = st.selectbox("Select Client", client_options)
    
    # Custom date range
    if date_range == "Custom Range":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=90))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
    
    # Generate report button
    if st.button("📊 Generate Report", type="primary", width='stretch'):  # Fixed deprecation warning
        with st.spinner(f"Generating {report_type} report..."):
            try:
                # Prepare report request
                report_request = {
                    "report_type": report_type.lower().replace(' ', '_'),
                    "time_period": date_range.lower().replace(' ', '_'),
                    "format": "pdf"
                }
                
                # Add custom date range
                if date_range == "Custom Range":
                    report_request["start_date"] = start_date.isoformat()
                    report_request["end_date"] = end_date.isoformat()
                
                # Add client filter if applicable
                if report_type == "Client Profitability" and selected_client != "All Clients":
                    clients = make_api_call("/api/clients", "GET") or []
                    if isinstance(clients, list):
                        client_id = next(
                            (c.get('id') for c in clients if c.get('name') == selected_client), 
                            None
                        )
                        if client_id:
                            report_request["client_id"] = client_id
                
                debug_log("Report request", report_request)
                
                # Call the API to generate the report
                response = make_api_call(
                    "/api/reports/generate",
                    "POST",
                    data=report_request
                )
                
                if response and 'report_id' in response:
                    st.success("✅ Report generated successfully!")
                    
                    # Show response details
                    with st.expander("📋 Report Details"):
                        st.json(response)
                    
                    # Create download button
                    try:
                        report_url = f"/api/reports/{response['report_id']}"
                        report_content = requests.get(f"{API_BASE_URL}{report_url}").content
                        
                        st.download_button(
                            label="💾 Download Report",
                            data=report_content,
                            file_name=f"{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            width='stretch'  # Fixed deprecation warning
                        )
                    except Exception as download_error:
                        st.error(f"❌ Error downloading report: {str(download_error)}")
                        st.info(f"💡 Try accessing the report directly: {API_BASE_URL}/api/reports/{response.get('report_id')}")
                
                else:
                    st.error("❌ Failed to generate report. Please try again.")
                    if response:
                        st.json(response)
            
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")
                debug_log("Report error", {"error": str(e), "traceback": traceback.format_exc()})

def login():
    """Enhanced login form"""
    with st.sidebar.form("login_form"):
        st.markdown("### 🔐 Login")
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        # Demo credentials helper
        with st.expander("💡 Demo Credentials"):
            st.code("Username: admin\nPassword: any")
            st.code("Username: user\nPassword: any")
        
        submit = st.form_submit_button("🚀 Login", width='stretch')  # Fixed deprecation warning
        
        if submit:
            if username and password:
                # Simple demo authentication
                st.session_state.auth_token = f"demo_token_{username}"
                st.session_state.user_role = "admin" if username == "admin" else "user"
                st.success(f"✅ Logged in as {username}")
                st.rerun()
            else:
                st.error("❌ Please enter both username and password")

def logout():
    """Logout and clear session"""
    st.session_state.auth_token = None
    st.session_state.user_role = None
    st.success("👋 Logged out successfully")
    st.rerun()

def show_ai_analytics():
    """AI Analytics interface with natural language queries"""
    st.markdown("<h1 class='main-header'>🤖 AI Analytics</h1>", unsafe_allow_html=True)
    
    if not st.session_state.get('auth_token'):
        st.warning("Please log in to use AI Analytics")
        return
    
    # Ensure approved model is loaded before showing AI features
    if not st.session_state.get('approved_model_checked', False):
        with st.spinner("Initializing AI system with approved model..."):
            model_ready, message = ensure_approved_model_loaded()
            st.session_state.approved_model_checked = True
            st.session_state.approved_model_ready = model_ready
            st.session_state.approved_model_message = message
    
    # Show model status
    if st.session_state.get('approved_model_ready', False):
        st.success(f"✅ {st.session_state.get('approved_model_message', 'Approved model ready')}")
    else:
        st.error(f"❌ {st.session_state.get('approved_model_message', 'Approved model not available')}")
        st.info("💡 **To use AI features:** Ensure the MoatMetrics API is running and Ollama service has tinyllama model available.")
        if st.button("🔄 Retry Model Loading"):
            st.session_state.approved_model_checked = False
            st.rerun()
        return
    
    # Display current AI system status at the top
    ai_system_status, ai_models_status = check_ai_system_status()
    
    # AI Status Banner
    if ai_system_status:
        status = ai_system_status['status']
        services = ai_system_status.get('services', {})
        ollama_connected = services.get('ollama', False)
        
        if status == 'healthy' and ollama_connected:
            st.success("🚀 AI System is fully operational! All features available.")
        elif status == 'healthy' and not ollama_connected:
            st.warning("⚠️ AI System is ready but Ollama is not connected. Limited functionality available.")
            st.info("💡 **To enable full AI features:** Install Ollama (https://ollama.ai) and run `ollama pull tinyllama`")
        elif status == 'degraded':
            st.warning("⚠️ AI System is partially operational. Some features may be limited.")
        elif status == 'not_initialized':
            st.info("🔄 AI System is starting up. Please wait or try initializing manually.")
            if st.button("🚀 Initialize AI System"):
                with st.spinner("Initializing AI system..."):
                    init_result = make_api_call("/api/ai/initialize", "POST")
                    if init_result and init_result.get('success'):
                        st.success("✅ AI system initialization started!")
                        st.session_state.ai_status_checked = False
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Failed to initialize AI system")
        else:
            st.error("❌ AI System error. Please check the system status or contact support.")
        
        # Model information
        if ai_models_status:
            models = ai_models_status.get('models', [])
            available_models = [m for m in models if m['status'] == 'available']
            
            if available_models:
                st.info(f"🧠 **AI Models Available:** {len(available_models)} models ready for {ai_models_status.get('hardware_tier', 'unknown')} tier hardware")
                
                # Show approved model (only tinyllama is approved)
                approved_model = 'tinyllama'  # Only approved model
                st.info(f"🎯 **Approved AI Model:** {approved_model} (Lightweight, secure, and optimized)")
            else:
                st.warning("📦 No AI models are currently available.")
    else:
        st.error("❌ Cannot connect to AI system. Please ensure the MoatMetrics API is running on http://localhost:8000")
        return
    
    # AI System Status
    with st.expander("🔍 AI System Status", expanded=False):
        if st.button("Check AI Status"):
            with st.spinner("Checking AI system status..."):
                ai_status = make_api_call("/api/ai/status", "GET")
                if ai_status:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Status", ai_status.get('status', 'Unknown'))
                    with col2:
                        st.metric("Primary Model", ai_status.get('primary_model', 'N/A'))
                    with col3:
                        st.metric("Hardware Tier", ai_status.get('hardware_tier', 'Unknown'))
                    
                    # System details
                    st.json({
                        "Available Models": ai_status.get('available_models', []),
                        "Memory Usage": ai_status.get('current_memory_usage', 'N/A'),
                        "Available Memory": ai_status.get('available_memory', 'N/A'),
                        "CPU Cores": ai_status.get('cpu_cores', 'N/A'),
                        "GPU Available": ai_status.get('gpu_available', False),
                        "Ollama Status": ai_status.get('ollama_status', 'Unknown'),
                        "Enhanced Features": ai_status.get('enhanced_features_available', False)
                    })
    
    # Natural Language Query Interface
    st.markdown("<h2 class='section-header'>💬 Ask Questions About Your Data</h2>", unsafe_allow_html=True)
    
    # Sample questions
    st.markdown("""
    **💡 Try asking questions like:**
    - "Which clients are most profitable this month?"
    - "How is our team utilization looking?"
    - "Are we wasting money on unused licenses?"
    - "What trends do you see in our revenue?"
    - "Which projects need more attention?"
    """)
    
    # Query input
    user_query = st.text_area(
        "Enter your question:",
        height=100,
        placeholder="Type your question about business metrics, clients, profitability, or any analytics...",
        help="Use natural language to ask about your business data"
    )
    
    # Query options
    col1, col2, col3 = st.columns(3)
    with col1:
        enhanced_ai = st.checkbox(
            "🚀 Enhanced AI", 
            value=False, 
            help="Use advanced ML optimization and security features (slower but more accurate)"
        )
    with col2:
        privacy_level = st.selectbox(
            "Privacy Level",
            ["standard", "high", "low"],
            help="Control how your data is processed"
        )
    with col3:
        urgency = st.selectbox(
            "Urgency",
            ["normal", "low", "high"],
            help="Processing priority level"
        )
    
    # Process query - but first check AI status
    if user_query and st.button("🧠 Ask AI", type="primary"):
        # Re-check AI status before processing
        current_ai_status, current_models_status = check_ai_system_status()
        
        if not current_ai_status or current_ai_status['status'] == 'error':
            st.error("❌ AI System is not available. Please check the system status.")
            return
        
        services = current_ai_status.get('services', {})
        ollama_connected = services.get('ollama', False)
        
        if not ollama_connected:
            st.warning("⚠️ Ollama is not connected. AI queries require Ollama to be running.")
            st.info("💡 Please install Ollama and pull a model (e.g., `ollama pull tinyllama`) to enable AI queries.")
            return
        
        with st.spinner("AI is analyzing your data and generating insights..."):
            # Ensure approved model (tinyllama) is loaded
            approved_model = 'tinyllama'  # Only approved model
            
            # Check if approved model is loaded
            load_result = make_api_call(f"/api/ai/models/{approved_model}/load", "POST")
            if load_result and load_result.get('success'):
                st.info(f"🧠 Using approved AI model: {approved_model}")
            else:
                st.error(f"❌ Could not load approved model '{approved_model}'. Please check system status.")
                return
            
            query_request = {
                "query": user_query,
                "enhanced": enhanced_ai,
                "privacy_level": privacy_level,
                "urgency": urgency,
                "enable_ensemble": False  # Can be made configurable later
            }
            
            debug_log("AI Query Request", query_request)
            
            result = make_api_call("/api/ai/query", "POST", data=query_request)
            
            if result and result.get('success'):
                # Display results
                st.success(f"✅ Analysis completed in {result.get('processing_time', 0):.2f} seconds")
                
                # Main Answer
                st.markdown("### 💡 AI Answer")
                st.markdown(f"**{result['answer']}**")
                
                # Confidence and Model Info
                col1, col2, col3 = st.columns(3)
                with col1:
                    confidence_pct = result.get('confidence', 0) * 100
                    st.metric("Confidence", f"{confidence_pct:.1f}%")
                with col2:
                    st.metric("Model Used", result.get('model_used', 'Unknown'))
                with col3:
                    st.metric("Processing Time", f"{result.get('processing_time', 0):.2f}s")
                
                # Enhanced metrics (if available)
                if enhanced_ai and result.get('quality_score'):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        quality_pct = result.get('quality_score', 0) * 100
                        st.metric("Quality Score", f"{quality_pct:.1f}%")
                    with col2:
                        security_pct = result.get('security_score', 0) * 100 if result.get('security_score') else 0
                        st.metric("Security Score", f"{security_pct:.1f}%")
                    with col3:
                        cache_status = "Cache Hit" if result.get('cache_hit') else "Fresh Analysis"
                        st.metric("Cache Status", cache_status)
                
                # Insights
                if result.get('insights'):
                    st.markdown("### 📊 Key Insights")
                    for i, insight in enumerate(result['insights'], 1):
                        st.markdown(f"**{i}.** {insight}")
                
                # Recommendations
                if result.get('recommendations'):
                    st.markdown("### 🎯 Recommendations")
                    for i, rec in enumerate(result['recommendations'], 1):
                        st.markdown(f"**{i}.** {rec}")
                
                # Data Sources
                if result.get('data_sources'):
                    with st.expander("📋 Data Sources Used"):
                        st.write("**Sources:** " + ", ".join(result['data_sources']))
                        if result.get('uncertainty_bounds'):
                            bounds = result['uncertainty_bounds']
                            st.write(f"**Confidence Range:** {bounds[0]*100:.1f}% - {bounds[1]*100:.1f}%")
                
            else:
                st.error("❌ Failed to process your question. Please try again or check the AI system status.")
    
    # Batch Query Section
    st.markdown("---")
    st.markdown("<h2 class='section-header'>📊 Batch Analytics</h2>", unsafe_allow_html=True)
    
    # Predefined query sets
    query_sets = {
        "Business Health Check": [
            "What is our overall financial health?",
            "Which clients are most profitable?", 
            "How efficient is our team utilization?"
        ],
        "License Optimization": [
            "Which licenses are underutilized?",
            "How much money could we save on licenses?",
            "What licenses do we need more of?"
        ],
        "Client Analysis": [
            "Which clients need more attention?",
            "What are the trends in client satisfaction?",
            "Which clients are at risk of churning?"
        ]
    }
    
    selected_set = st.selectbox("Choose a query set:", list(query_sets.keys()))
    
    if st.button(f"🚀 Run {selected_set} Analysis"):
        with st.spinner(f"Running {selected_set} analysis..."):
            batch_request = {
                "queries": query_sets[selected_set],
                "enhanced": enhanced_ai,
                "privacy_level": privacy_level,
                "enable_ensemble": False
            }
            
            batch_result = make_api_call("/api/ai/batch-query", "POST", data=batch_request)
            
            if batch_result and batch_result.get('success'):
                st.success(f"✅ Batch analysis completed! Processed {batch_result.get('total_queries', 0)} queries in {batch_result.get('total_processing_time', 0):.2f} seconds")
                
                # Display results
                results = batch_result.get('results', [])
                for i, (query, result) in enumerate(zip(query_sets[selected_set], results)):
                    with st.expander(f"📊 {i+1}. {query}", expanded=i == 0):
                        st.markdown(f"**Answer:** {result.get('answer', 'No answer')}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            confidence_pct = result.get('confidence', 0) * 100
                            st.metric("Confidence", f"{confidence_pct:.1f}%")
                        with col2:
                            st.metric("Time", f"{result.get('processing_time', 0):.2f}s")
                        
                        if result.get('insights'):
                            st.markdown("**Key Insights:**")
                            for insight in result['insights'][:3]:  # Show top 3
                                st.markdown(f"• {insight}")
                        
                        if result.get('recommendations'):
                            st.markdown("**Recommendations:**")
                            for rec in result['recommendations'][:2]:  # Show top 2
                                st.markdown(f"• {rec}")
            else:
                st.error("❌ Failed to process batch queries. Please try again.")

def show_admin():
    """Admin panel"""
    st.markdown("<h1 class='main-header'>⚙️ Admin Panel</h1>", unsafe_allow_html=True)
    
    if st.session_state.user_role != 'admin':
        st.error("🚫 Access denied. Admin privileges required.")
        return
    
    # Debug mode toggle
    st.session_state.debug_mode = st.checkbox(
        "🛠 Debug Mode", 
        value=st.session_state.get('debug_mode', False),
        help="Show detailed API calls and responses"
    )
    
    # API Health Check
    st.markdown("### 🏥 System Health")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Check API Health"):
            with st.spinner("Checking API health..."):
                health = make_api_call("/health", "GET")
                if health:
                    st.success("✅ API is healthy")
                    # Enhanced health display
                    if health.get('ai_analytics') == 'operational':
                        st.success("🤖 AI Analytics: Operational")
                    elif health.get('ai_analytics') == 'not_initialized':
                        st.warning("🤖 AI Analytics: Not Initialized")
                    else:
                        st.error(f"🤖 AI Analytics: {health.get('ai_analytics', 'Unknown')}")
                    
                    # Features status
                    features = health.get('features', {})
                    st.markdown("**Available Features:**")
                    for feature, status in features.items():
                        status_icon = "✅" if status else "❌"
                        st.markdown(f"- {status_icon} {feature.replace('_', ' ').title()}")
                    
                    with st.expander("Full Health Report"):
                        st.json(health)
                else:
                    st.error("❌ API health check failed")
    
    with col2:
        if st.button("📊 System Status"):
            with st.spinner("Getting system status..."):
                status = make_api_call("/api/status", "GET")
                if status:
                    st.success("✅ System status retrieved")
                    st.json(status)
                else:
                    st.info("ℹ️ System status endpoint not available")
    
    # AI Management Console
    st.markdown("---")
    st.markdown("### 🤖 AI Management Console")
    
    # AI System Status
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Check AI System Status"):
            with st.spinner("Checking AI system status..."):
                ai_health = make_api_call("/api/ai/health", "GET")
                if ai_health:
                    status = ai_health.get('status', 'Unknown')
                    if status == 'healthy':
                        st.success(f"✅ AI System: {status.title()}")
                    elif status == 'degraded':
                        st.warning(f"⚠️ AI System: {status.title()}")
                    else:
                        st.error(f"❌ AI System: {status.title()}")
                    
                    # Service details
                    services = ai_health.get('services', {})
                    st.markdown("**AI Services:**")
                    for service, status in services.items():
                        status_icon = "✅" if status else "❌"
                        st.markdown(f"- {status_icon} {service.replace('_', ' ').title()}")
                    
                    st.json(ai_health)
                else:
                    st.error("❌ AI health check failed")
    
    with col2:
        if st.button("🚀 Initialize AI System"):
            with st.spinner("Initializing AI system..."):
                init_result = make_api_call("/api/ai/initialize", "POST")
                if init_result and init_result.get('success'):
                    st.success("✅ AI system initialization started")
                    st.info(init_result.get('message', 'Initialization in progress'))
                else:
                    st.error("❌ Failed to initialize AI system")
    
    # AI Models Management
    st.markdown("### 🧠 AI Models Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 List Available Models"):
            with st.spinner("Getting available AI models..."):
                models_info = make_api_call("/api/ai/models", "GET")
                if models_info and models_info.get('success'):
                    st.success(f"✅ Found {models_info.get('total_models', 0)} models")
                    
                    models = models_info.get('models', [])
                    if models:
                        # Create a DataFrame for better display
                        import pandas as pd
                        models_df = pd.DataFrame(models)
                        
                        st.dataframe(
                            models_df,
                            column_config={
                                "name": st.column_config.TextColumn("Model Name", width="medium"),
                                "memory_required_gb": st.column_config.NumberColumn("Memory (GB)", format="%.1f GB"),
                                "parameters": st.column_config.TextColumn("Parameters"),
                                "status": st.column_config.SelectboxColumn("Status", options=["available", "unavailable"]),
                                "description": st.column_config.TextColumn("Description", width="large")
                            },
                            hide_index=True,
                            width='stretch'
                        )
                        
                        # Hardware info
                        hardware_tier = models_info.get('hardware_tier', 'Unknown')
                        st.info(f"💻 Hardware Tier: {hardware_tier}")
                    else:
                        st.warning("No models found")
                else:
                    st.error("❌ Failed to get models information")
    
    with col2:
        # Model loading interface
        st.markdown("**Quick Model Loading:**")
        
        # Show approved model (only tinyllama is approved)
        if models_info and models_info.get('success'):
            approved_model = 'tinyllama'  # Only approved model
            
            st.info(f"🎯 **Approved AI Model:** {approved_model} (Lightweight, secure, optimized for all hardware)")
            
            # Quick load button for approved model
            if st.button(f"⚡ Load {approved_model} (Approved)"):
                with st.spinner(f"Loading approved model {approved_model}..."):
                    load_result = make_api_call(f"/api/ai/models/{approved_model}/load", "POST")
                    if load_result and load_result.get('success'):
                        st.success(f"✅ {approved_model} loaded successfully!")
                        st.info(load_result.get('message', 'Approved model is ready for AI queries'))
                        # Refresh the models list
                        st.session_state.ai_status_checked = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to load approved model {approved_model}")
                        st.info("💡 Make sure Ollama is running and tinyllama model is available")
        
        st.markdown("---")
        st.markdown("**Manual Model Loading:**")
        model_to_load = st.text_input("Model Name to Load:", placeholder="e.g., tinyllama")
        if st.button("⬇️ Load Model") and model_to_load:
            with st.spinner(f"Loading model {model_to_load}..."):
                load_result = make_api_call(f"/api/ai/models/{model_to_load}/load", "POST")
                if load_result and load_result.get('success'):
                    st.success(f"✅ Model {model_to_load} loaded successfully")
                    st.info(load_result.get('message', 'Model is now available'))
                    # Refresh status
                    st.session_state.ai_status_checked = False
                else:
                    st.error(f"❌ Failed to load model {model_to_load}")
    
    # AI Performance Report
    st.markdown("### 📊 AI Performance Report")
    if st.button("📈 Generate Performance Report"):
        with st.spinner("Generating comprehensive AI performance report..."):
            perf_report = make_api_call("/api/ai/performance-report", "GET")
            if perf_report and perf_report.get('success'):
                st.success("✅ Performance report generated")
                
                report = perf_report.get('report', {})
                
                # System Configuration
                if 'system_configuration' in report:
                    with st.expander("🖥️ System Configuration", expanded=True):
                        config = report['system_configuration']
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Primary Model", config.get('primary_model', 'N/A'))
                        with col2:
                            st.metric("Hardware Tier", config.get('hardware_tier', 'N/A'))
                        with col3:
                            st.metric("CPU Cores", config.get('cpu_cores', 'N/A'))
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Memory Usage", config.get('current_memory_usage', 'N/A'))
                        with col2:
                            st.metric("Available Memory", config.get('available_memory', 'N/A'))
                        with col3:
                            gpu_status = "Yes" if config.get('gpu_available', False) else "No"
                            st.metric("GPU Available", gpu_status)
                
                # ML Optimization Report
                if 'ml_optimization' in report:
                    with st.expander("🔧 ML Optimization Metrics"):
                        st.json(report['ml_optimization'])
                
                # Security Framework Report  
                if 'security_framework' in report:
                    with st.expander("🔒 Security Framework Status"):
                        st.json(report['security_framework'])
                
                # Enhanced Features
                if 'enhanced_features' in report:
                    with st.expander("✨ Enhanced Features Status"):
                        features = report['enhanced_features']
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            ensemble_models = features.get('ensemble_models_available', 0)
                            st.metric("Ensemble Models", ensemble_models)
                        with col2:
                            quality_threshold = features.get('quality_threshold', 0)
                            st.metric("Quality Threshold", f"{quality_threshold:.1f}")
                        
                        # Feature flags
                        st.markdown("**Feature Flags:**")
                        uncertainty_est = "✅" if features.get('uncertainty_estimation', False) else "❌"
                        adaptive_conf = "✅" if features.get('adaptive_confidence', False) else "❌"
                        
                        st.markdown(f"- {uncertainty_est} Uncertainty Estimation")
                        st.markdown(f"- {adaptive_conf} Adaptive Confidence")
                
                # Integration Status
                integration_status = report.get('integration_status', 'Unknown')
                if integration_status == 'fully_operational':
                    st.success(f"🔗 Integration Status: {integration_status.replace('_', ' ').title()}")
                else:
                    st.warning(f"🔗 Integration Status: {integration_status.replace('_', ' ').title()}")
                
                # Full report in expander
                with st.expander("📋 Full Performance Report"):
                    st.json(report)
                    
            else:
                st.error("❌ Failed to generate performance report")
    
    # Configuration
    st.markdown("### ⚙️ Configuration")
    st.text_input("API Base URL", value=API_BASE_URL, disabled=True)
    
    # Session info
    st.markdown("### 👤 Session Information")
    session_info = {
        "User Role": st.session_state.get('user_role'),
        "Auth Token": st.session_state.get('auth_token', "None")[:20] + "..." if st.session_state.get('auth_token') else "None",
        "Debug Mode": st.session_state.get('debug_mode', False)
    }
    st.json(session_info)

def main():
    # Sidebar navigation
    st.sidebar.title("🏰 MoatMetrics")
    
    # Show version and links
    st.sidebar.markdown("---")
    st.sidebar.markdown("**v1.0.1** | [API Docs](http://localhost:8000/docs) | [GitHub](#)")
    
    # Display AI status in sidebar (always show)
    display_ai_status_sidebar()
    
    # Check authentication
    if not st.session_state.get('auth_token'):
        login()
        st.markdown("""
        # 🏰 Welcome to MoatMetrics
        
        **MoatMetrics** is a comprehensive business analytics platform designed to help you:
        
        - 📊 **Track Client Performance** - Monitor profitability and engagement metrics
        - 📈 **Analyze Resource Utilization** - Optimize team productivity and allocation  
        - 💰 **Manage License Costs** - Track and optimize software subscriptions
        - 📄 **Generate Reports** - Create detailed business intelligence reports
        - 🤖 **AI-Powered Analytics** - Ask questions in natural language
        
        ### 🤖 AI System Status
        """)
        
        # Show AI status on welcome page
        ai_system_status, ai_models_status = check_ai_system_status()
        
        if ai_system_status:
            status = ai_system_status['status']
            services = ai_system_status.get('services', {})
            ollama_connected = services.get('ollama', False)
            
            if status == 'healthy' and ollama_connected:
                st.success("🚀 AI System: Fully Operational - Natural language queries available!")
                if ai_models_status:
                    available_models = [m['name'] for m in ai_models_status.get('models', []) if m['status'] == 'available']
                    if available_models:
                        st.info(f"🧠 Available AI Models: {', '.join(available_models)}")
            elif status == 'healthy' and not ollama_connected:
                st.warning("⚠️ AI System: Ready but Ollama not connected")
                st.info("💡 Install Ollama for AI-powered natural language queries")
            elif status == 'not_initialized':
                st.info("🔄 AI System: Initializing...")
            else:
                st.error("❌ AI System: Not Available")
        else:
            st.error("❌ Cannot connect to AI system")
        
        st.markdown("""
        ### 🚀 Getting Started
        1. **Login** using the sidebar (use 'admin'/'user' with any password)
        2. **Upload Data** via CSV/Excel files
        3. **View Dashboard** for real-time metrics
        4. **Try AI Analytics** to ask questions in natural language
        5. **Generate Reports** for detailed analysis
        
        ---
        👈 **Please log in to continue**
        """)
        return
    
    # Show user info
    st.sidebar.markdown(f"""
    ---  
    👤 **{st.session_state.user_role.upper()}**  
    *Logged in successfully*
    """)
    
    # Navigation menu
    menu_items = ["📊 Dashboard", "📤 Data Upload", "📄 Reports", "🤖 AI Analytics"]
    
    # Role-based access control
    if st.session_state.user_role == 'admin':
        menu_items.append("⚙️ Admin")
    
    choice = st.sidebar.radio("🧭 Navigation", menu_items)
    
    # Logout button
    if st.sidebar.button("👋 Logout", width='stretch'):  # Fixed deprecation warning
        logout()
    
    # Display the selected page
    if choice == "📊 Dashboard":
        show_dashboard()
    elif choice == "📤 Data Upload":
        show_data_upload()
    elif choice == "📄 Reports":
        show_reports()
    elif choice == "🤖 AI Analytics":
        show_ai_analytics()
    elif choice == "⚙️ Admin" and st.session_state.user_role == 'admin':
        show_admin()

if __name__ == "__main__":
    main()