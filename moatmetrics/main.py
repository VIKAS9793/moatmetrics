"""
Main entry point for MoatMetrics MVP.

Run this file to start the FastAPI server and access the complete
MoatMetrics platform via REST API.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from src.utils.logging_config import setup_logging
from src.utils.config_loader import get_config
from src.api.main import app


def main():
    """Main entry point for MoatMetrics."""
    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     ███╗   ███╗ ██████╗  █████╗ ████████╗                     ║
║     ████╗ ████║██╔═══██╗██╔══██╗╚══██╔══╝                     ║
║     ██╔████╔██║██║   ██║███████║   ██║                        ║
║     ██║╚██╔╝██║██║   ██║██╔══██║   ██║                        ║
║     ██║ ╚═╝ ██║╚██████╔╝██║  ██║   ██║                        ║
║     ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝                        ║
║                                                                  ║
║     ███╗   ███╗███████╗████████╗██████╗ ██╗ ██████╗███████╗   ║
║     ████╗ ████║██╔════╝╚══██╔══╝██╔══██╗██║██╔════╝██╔════╝   ║
║     ██╔████╔██║█████╗     ██║   ██████╔╝██║██║     ███████╗   ║
║     ██║╚██╔╝██║██╔══╝     ██║   ██╔══██╗██║██║     ╚════██║   ║
║     ██║ ╚═╝ ██║███████╗   ██║   ██║  ██║██║╚██████╗███████║   ║
║     ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝╚══════╝   ║
║                                                                  ║
║          Privacy-First Offline Analytics Platform               ║
║                    for MSPs - MVP v1.0.0                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Setup logging
    setup_logging()
    
    # Get configuration
    config = get_config()
    
    print(f"""
Starting MoatMetrics Server...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Configuration:
• Environment: {config.app.environment}
• Debug Mode: {config.app.debug}
• Database: SQLite (offline)
• API Host: {config.api.host}
• API Port: {config.api.port}

Features Enabled:
✓ Offline Analytics Engine
✓ SHAP Explainability
✓ Data Governance & Compliance
✓ Human-in-the-Loop for Low Confidence
✓ Audit Trail & Reporting
✓ Role-Based Access Control

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    print(f"📡 API Documentation: http://{config.api.host}:{config.api.port}/docs")
    print(f"📊 Interactive API: http://{config.api.host}:{config.api.port}/redoc")
    print(f"❤️  Health Check: http://{config.api.host}:{config.api.port}/health")
    print("\n" + "━"*70 + "\n")
    
    # Run the FastAPI server
    try:
        uvicorn.run(
            "src.api.main:app",
            host=config.api.host,
            port=config.api.port,
            reload=config.app.debug,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n✋ Shutting down MoatMetrics...")
        print("Thank you for using MoatMetrics MVP!\n")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
