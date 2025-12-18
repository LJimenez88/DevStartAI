import { useEffect, useState } from "react";

// Read from .env (VITE_API_BASE_URL=http://localhost:8000)
// and fall back to localhost if it's missing
//This information needs to be in the env file this was added as a fallback & or testing purposes
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";


const ALL_DB_OPTIONS = [
  { value: "none",     label: "No database (just in-memory)" },
  { value: "postgres", label: "Postgres (via DATABASE_URL)" },
  //SQLite will be reactivated once I figure out how to make it work
  //{ value: "sqlite",   label: "SQLite (local file)" },
  { value: "mongo",    label: "MongoDB" },
  {value: "mysql",     label: "MySQL"}
];

function getDbOptionsForStack(stackId) {
  // No stack yet? show everything
  if (!stackId) return ALL_DB_OPTIONS;

  // Any Express backend: hide SQLite
  //May use this once SQLite is up and running 
  /*if (stackId.startsWith("express")) {
    return ALL_DB_OPTIONS.filter((opt) => opt.value !== "sqlite");
  }*/

  // FastAPI or anything else: allow all
  return ALL_DB_OPTIONS;
}

function App() {
  // Form state
  const [projectName, setProjectName] = useState("");
  const [stackId, setStackId] = useState("");
  const [includeDocker, setIncludeDocker] = useState(false);
  const [includeAuth, setIncludeAuth] = useState(false);
  const [includeCI, setIncludeCI] = useState(false);
  const [dbEngine, setDbEngine] = useState("none");


  // Data from backend
  const [stacks, setStacks] = useState([]);

  // UI state
  const [loadingStacks, setLoadingStacks] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");

  // Load stacks on page load
  useEffect(() => {
    const fetchStacks = async () => {
      try {
        setLoadingStacks(true);
        setError("");

        const res = await fetch(`${API_BASE_URL}/stacks`);
        if (!res.ok) {
          throw new Error("Failed to retrieve stacks");
        }

        const data = await res.json();
        setStacks(data);

        // Preselect first stack by default
        if (data.length > 0) {
          setStackId(data[0].id);
        }
      } catch (err) {
        console.error(err);
        setError("Could not load stacks. Is the backend running?");
      } finally {
        setLoadingStacks(false);
      }
    };

    fetchStacks();
  }, []);

    // Keep dbEngine valid when stack changes
  useEffect(() => {
    const options = getDbOptionsForStack(stackId);
    const validValues = options.map((o) => o.value);

    // If current dbEngine isn't allowed anymore (e.g. sqlite on Express),
    // reset to the first valid option.
    if (!validValues.includes(dbEngine)) {
      setDbEngine(validValues[0] ?? "none");
    }
  }, [stackId, dbEngine]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!projectName.trim()) {
      setError("Enter a project name.");
      return;
    }

    if (!stackId) {
      setError("Please select a stack.");
      return;
    }

    try {
      setSubmitting(true);
      setError("");//clears old error log
      setDownloadUrl("");//clears old downloadURL

      // IMPORTANT: property names must match backend model
      const payload = {
        projectName,
        stackId,
        includeDocker,
        includeAuth: AUTH_ENABLED ? includeAuth : false,
        includeCI: CI_ENABLED ? includeCI : false,
        dbEngine, 
      };

      const res = await fetch(`${API_BASE_URL}/scaffold`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        const msg = errBody.detail || "Failed to scaffold project.";
        throw new Error(msg);
      }

      const data = await res.json();
      setDownloadUrl(data.downloadUrl || "");
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
      setProjectName("");
      setStackId("");

      setIncludeDocker(false);
      setIncludeAuth(false);
      setIncludeCI(false);
      setDbEngine("none");

      setError("");
      setDownloadUrl("");
    };

    //This ones is to disable until feat is ready
    const AUTH_ENABLED = false;
    const CI_ENABLED = false;


  // Simple UI
  return (
    <div className="min-h-screen bg-slate-900 text-gray-100 flex items-center justify-center p-6">
      <div className="w-full max-w-xl bg-slate-950 border border-slate-700 rounded-xl shadow-2xl p-7">
        <header className="mb-6">
          <p className="text-xs uppercase tracking-[0.2em] text-sky-400 mb-1">
            DevStart AI · v1
          </p>
          <h1 className="text-2xl font-semibold mb-1">
            Template-based project generator
          </h1>
          <p className="text-sm text-slate-400">
            Choose a stack, tweak options, and download a ready-to-use starter.
          </p>
        </header>

        <form onSubmit={handleSubmit} className="grid gap-4">
          {/* Project name */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Project name
            </label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="my-cool-app"
              className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
            />
          </div>

          {/* Stack select */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Stack
            </label>
            {loadingStacks ? (
              <div className="text-xs text-slate-400">Loading stacks…</div>
            ) : (
              <select
                value={stackId}
                onChange={(e) => setStackId(e.target.value)}
                className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
              >
                <option value="" disabled>
                  Select a stack…
                </option>
                {stacks.map((stack) => (
                  <option key={stack.id} value={stack.id}>
                    {stack.label}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Options */}
           <div>
            <p className="text-sm font-medium mb-1">Database (optional)</p>
            <select
              value={dbEngine}
              onChange={(e) => setDbEngine(e.target.value)}
              className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
            >
              {getDbOptionsForStack(stackId).map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          {/*This section was replaced so that once functional we can run this one instead
            -There is a hardcoded variables in order to prevent users from clicking true to the checkmarks
          */}
          {/*<div>
            <p className="text-sm font-medium mb-1">Options</p>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <label className="inline-flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={includeDocker}
                  onChange={(e) => setIncludeDocker(e.target.checked)}
                  className="h-3 w-3 rounded border-slate-500 bg-slate-900"
                />
                <span>Docker</span>
              </label>
              <label className="inline-flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={includeAuth}
                  onChange={(e) => setIncludeAuth(e.target.checked)}
                  className="h-3 w-3 rounded border-slate-500 bg-slate-900"
                />
                <span>Auth stub</span>
              </label>
              <label className="inline-flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={includeCI}
                  onChange={(e) => setIncludeCI(e.target.checked)}
                  className="h-3 w-3 rounded border-slate-500 bg-slate-900"
                />
                <span>CI config</span>
              </label>
            </div>
          </div>*/}
          <div>
            <p className="text-sm font-medium mb-1">Options</p>

            <div className="flex justify-between w-full gap-2 text-xs">
              {/* Docker (enabled) */}
              <label className="inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={includeDocker}
                  onChange={(e) => setIncludeDocker(e.target.checked)}
                  className="h-3 w-3 rounded border-slate-500 bg-slate-900"
                />
                <span>Docker</span>
              </label>

              {/* Auth (disabled) */}
              <label
                className={`inline-flex items-center gap-2 ${
                  AUTH_ENABLED ? "" : "opacity-50 cursor-not-allowed"
                }`}
                title={AUTH_ENABLED ? "" : "Coming soon"}
              >
                <input
                  type="checkbox"
                  checked={includeAuth}
                  onChange={(e) => setIncludeAuth(e.target.checked)}
                  disabled={!AUTH_ENABLED}
                  className="h-3 w-3 rounded border-slate-500 bg-slate-900"
                />
                <span className="flex items-center gap-2">
                  Auth stub
                  {!AUTH_ENABLED && (
                    <span className="rounded bg-slate-800 px-2 py-[2px] text-[10px] text-slate-300 border border-slate-700">
                      Coming soon
                    </span>
                  )}
                </span>
              </label>

              {/* CI (disabled) */}
              <label
                className={`inline-flex items-center gap-2 ${
                  CI_ENABLED ? "" : "opacity-50 cursor-not-allowed"
                }`}
                title={CI_ENABLED ? "" : "Coming soon"}
              >
                <input
                  type="checkbox"
                  checked={includeCI}
                  onChange={(e) => setIncludeCI(e.target.checked)}
                  disabled={!CI_ENABLED}
                  className="h-3 w-3 rounded border-slate-500 bg-slate-900"
                />
                <span className="flex items-center gap-2">
                  CI config
                  {!CI_ENABLED && (
                    <span className="rounded bg-slate-800 px-2 py-[2px] text-[10px] text-slate-300 border border-slate-700">
                      Coming soon
                    </span>
                  )}
                </span>
              </label>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="rounded-md bg-red-900/70 border border-red-500/70 px-3 py-2 text-xs text-red-100">
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={submitting}
            className={`mt-1 inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-semibold
              ${
                submitting
                  ? "bg-slate-600 cursor-not-allowed"
                  : "bg-emerald-500 hover:bg-emerald-400"
              } text-slate-950 transition-colors`}
          >
            {submitting ? "Generating…" : "Generate project"}
          </button>
        </form>

        {/* Download section */}
        {downloadUrl && (
          <div className="mt-6 border-t border-slate-800 pt-4 text-sm">
            <p className="mb-2 text-slate-200">
              Project generated! Download your scaffold:
            </p>
            <a
              href={downloadUrl}
              target="_blank"
              rel="noopener noreferrer"
              onClick={() => {
                setTimeout(resetForm, 0);
              }}
              className="inline-flex items-center gap-2 rounded-md bg-sky-500 px-4 py-2 text-xs font-medium text-slate-950 hover:bg-sky-400 transition-colors"
            >
              Download ZIP
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;