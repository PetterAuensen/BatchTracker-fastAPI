"use client";

import { useState } from "react";
import NewBatchForm from "./components/NewBatchForm";
import LinkRFIDForm from "./components/LinkRFIDForm";

export default function Home() {
  const [view, setView] = useState<"batch" | "rfid">("batch");
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="flex justify-center gap-4 mb-6">
        <button
          onClick={() => setView("batch")}
          className={`px-4 py-2 rounded ${
            view === "batch" ? "bg-blue-600 text-white" : "bg-white border"
          }`}
        >
          Registrer batch
        </button>
        <button
          onClick={() => setView("rfid")}
          className={`px-4 py-2 rounded ${
            view === "rfid" ? "bg-blue-600 text-white" : "bg-white border"
          }`}
        >
          Koble RFID
        </button>
      </div>

      {toast && (
        <div className="fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded shadow">
          {toast}
        </div>
      )}

      {view === "batch" ? <NewBatchForm /> : <LinkRFIDForm onSuccess={showToast} />}
    </main>
  );
}
