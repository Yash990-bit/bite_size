"""
Main Command Line Interface for BiteSize Agent
"""
import sys
import argparse
import webbrowser
from bitesize.agent import BiteSizeAgent
from bitesize.tui import run_interactive_tui


def main():
    parser = argparse.ArgumentParser(
        description="BiteSize: The Open-Source ADHD Task De-Overwhelmer Agent"
    )
    parser.add_argument("--model", type=str, default="llama3.2:latest", help="Ollama open-weight model name")
    parser.add_argument("--user", type=str, default="Aarav", help="User name (default: Aarav)")
    parser.add_argument("--sample", action="store_true", help="Auto-load Aarav's messy Sunday backlog")
    parser.add_argument("--web", action="store_true", help="Launch FastAPI web dashboard and API server")
    parser.add_argument("--port", type=int, default=8000, help="Port for web server (default 8000)")
    parser.add_argument("--export-devrelay", action="store_true", help="Export recent agent session for DevRelay")

    args = parser.parse_args()

    if args.export_devrelay:
        from devrelay_export import export_devrelay_session
        export_devrelay_session()
        return

    if args.web:
        import uvicorn
        print(f"Starting BiteSize Agent Server at http://localhost:{args.port}...")
        webbrowser.open(f"http://localhost:{args.port}")
        uvicorn.run("api:app", host="127.0.0.1", port=args.port, reload=False)
        return

    agent = BiteSizeAgent(model_name=args.model, user_name=args.user)
    run_interactive_tui(agent, sample_mode=args.sample)


if __name__ == "__main__":
    main()
