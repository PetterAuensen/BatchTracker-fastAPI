"use client";

import { useState } from "react";

type Props = {
  onSuccess?: (message: string) => void;
};

export default function LinkRFIDForm({ onSuccess }: Props) {
  const [form, setForm] = useState({
    customer_id: "",
    store_id: "",
    batch_id: "",
    rfid: "",
  });

  const [message, setMessage] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    for (const key of Object.keys(form)) {
      if (!(form as any)[key]) {
        alert(`Feltet ${key} er påkrevd.`);
        return;
      }
    }

    try {
      const res = await fetch("https://batchtracker-fastapi-production.up.railway.app/rfid/link", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const data = await res.json();
      const msg = `RFID er koblet til batch ${data.batch_id}`;
      setMessage(msg);
      if (onSuccess) onSuccess(msg);
    } catch (err) {
      setMessage("Det oppstod en feil ved innsending.");
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 p-6 border rounded-xl shadow">
      <h2 className="text-xl font-bold mb-4">Koble RFID til batch</h2>
      <form onSubmit={handleSubmit} className="grid gap-4">
        {[
          { name: "customer_id", label: "Customer ID*" },
          { name: "store_id", label: "Store ID*" },
          { name: "batch_id", label: "Batch ID*" },
          { name: "rfid", label: "RFID*" },
        ].map((field) => (
          <div key={field.name}>
            <label htmlFor={field.name} className="block mb-1">
              {field.label}
            </label>
            <input
              id={field.name}
              name={field.name}
              value={(form as any)[field.name]}
              onChange={handleChange}
              className="w-full border p-2"
            />
          </div>
        ))}
        <button
          type="submit"
          className="w-full bg-green-600 text-white p-2 rounded hover:bg-green-700"
        >
          Koble RFID
        </button>
      </form>
      {message && (
        <div className="mt-4 bg-gray-100 p-2 rounded text-sm text-center">
          {message}
        </div>
      )}
    </div>
  );
}