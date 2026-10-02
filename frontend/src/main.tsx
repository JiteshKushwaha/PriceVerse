import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import App from "./App";
import { ErrorBoundary } from "./components/ErrorBoundary";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false, gcTime: 30 * 60_000 } },
});

// StrictMode is intentionally omitted: it double-opens the SSE stream in dev and burns rate-limit quota.
ReactDOM.createRoot(document.getElementById("root")!).render(
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <App />
      <Toaster position="bottom-center" toastOptions={{ style: { border: "3px solid #000", fontWeight: 600 } }} />
    </QueryClientProvider>
  </ErrorBoundary>,
);