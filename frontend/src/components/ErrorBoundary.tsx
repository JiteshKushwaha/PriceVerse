import { Component, type ErrorInfo, type ReactNode } from "react";

export class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state: { error: Error | null } = { error: null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("UI crashed", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="grid min-h-screen place-items-center bg-miles p-6 text-paper">
          <div className="panel max-w-md p-6 text-center">
            <p className="headline text-3xl">KA-BOOM!</p>
            <p className="mt-2">The UI hit a villain: {this.state.error.message}</p>
            <button className="mt-4 rounded border-[3px] border-black bg-comic px-4 py-2 font-display text-miles" onClick={() => window.location.reload()}>
              RELOAD
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}