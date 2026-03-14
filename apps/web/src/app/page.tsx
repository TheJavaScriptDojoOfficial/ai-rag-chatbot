export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <main className="mx-auto max-w-2xl px-6 py-16">
        <h1 className="text-3xl font-semibold tracking-tight">
          Company RAG Chatbot
        </h1>
        <p className="mt-2 text-slate-600">
          Foundation setup complete
        </p>

        <section className="mt-12 space-y-6">
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-sm font-medium uppercase tracking-wide text-slate-500">
              Frontend
            </h2>
            <p className="mt-1 font-medium">Next.js</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-sm font-medium uppercase tracking-wide text-slate-500">
              Backend
            </h2>
            <p className="mt-1 font-medium">FastAPI</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <h2 className="text-sm font-medium uppercase tracking-wide text-slate-500">
              Status
            </h2>
            <p className="mt-1 font-medium">Ready for next phase</p>
          </div>
        </section>
      </main>
    </div>
  );
}
