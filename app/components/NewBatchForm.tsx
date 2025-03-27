
"use client";
import { useState } from "react";

export default function Home() {
  const today = new Date().toISOString().split("T")[0];
  const [formData, setFormData] = useState({
    customer_id: "",
    store_id: "",
    batch_id: "",
    article_id: "",
    expiration_date: today,
    status: "",
    production_method: "",
    production_place: "",
    supplier: "",
    dynamic_fields: {
      farge: "",
      type: "",
    },
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (name === "farge" || name === "type") {
      setFormData((prev) => ({
        ...prev,
        dynamic_fields: {
          ...prev.dynamic_fields,
          [name]: value,
        },
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const requiredFields = ["customer_id", "store_id", "batch_id", "article_id", "expiration_date", "status"];
    for (const field of requiredFields) {
      if (!formData[field as keyof typeof formData]) {
        alert(`Feltet ${field} er påkrevd.`);
        return;
      }
    }

    if (!["1", "8", "9"].includes(formData.status)) {
      alert("Status må være 1, 8 eller 9.");
      return;
    }

    const response = await fetch("https://batchtracker-fastapi-production.up.railway.app/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    const data = await response.json();
    alert("Svar fra server: " + JSON.stringify(data));
  };

  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-6 rounded-2xl shadow-md w-full max-w-md space-y-4"
      >
        <h1 className="text-2xl font-bold mb-4">Registrer ny batch</h1>

        <div>
          <label htmlFor="customer_id" className="block mb-1">Customer ID*</label>
          <input
            id="customer_id"
            name="customer_id"
            value={formData.customer_id}
            onChange={handleChange}
            className="w-full border p-2"
          />
        </div>

        <div>
          <label htmlFor="store_id" className="block mb-1">Store ID*</label>
          <input
            id="store_id"
            name="store_id"
            value={formData.store_id}
            onChange={handleChange}
            className="w-full border p-2"
          />
        </div>

        <div>
          <label htmlFor="batch_id" className="block mb-1">Batch ID*</label>
          <input
            id="batch_id"
            name="batch_id"
            value={formData.batch_id}
            onChange={handleChange}
            className="w-full border p-2"
          />
        </div>

        <div>
          <label htmlFor="article_id" className="block mb-1">Article ID*</label>
          <input
            id="article_id"
            name="article_id"
            value={formData.article_id}
            onChange={handleChange}
            className="w-full border p-2"
          />
        </div>

        <div>
          <label htmlFor="expiration_date" className="block mb-1">Expiration Date*</label>
          <input
            id="expiration_date"
            name="expiration_date"
            value={formData.expiration_date}
            onChange={handleChange}
            className="w-full border p-2"
            type="date"
          />
        </div>

        <div>
          <label htmlFor="status" className="block mb-1">Status* (1, 8, 9)</label>
          <input
            id="status"
            name="status"
            value={formData.status}
            onChange={handleChange}
            className="w-full border p-2"
          />
        </div>

        <div>
          <label htmlFor="production_method" className="block mb-1">Production Method</label>
          <input
            id="production_method"
            name="production_method"
            value={formData.production_method}
            onChange={handleChange}
            className="w-full border p-2"
          />
        </div>

        <div>
          <label htmlFor="production_place" className="block mb-1">Production Place</label>
          <input
            id="production_place"
            name="production_place"
            value={formData.production_place}
            onChange={handleChange}
            className="w-full border p-2"
          />
        </div>

        <div>
          <label htmlFor="supplier" className="block mb-1">Supplier</label>
          <input
            id="supplier"
            name="supplier"
            value={formData.supplier}
            onChange={handleChange}
            className="w-full border p-2"
          />
        </div>

        <div>
          <label htmlFor="farge" className="block mb-1">Farge</label>
          <input
            id="farge"
            name="farge"
            value={formData.dynamic_fields.farge}
            onChange={handleChange}
            className="w-full border p-2"
          />
        </div>

        <div>
          <label htmlFor="type" className="block mb-1">Type</label>
          <input
            id="type"
            name="type"
            value={formData.dynamic_fields.type}
            onChange={handleChange}
            className="w-full border p-2"
          />
        </div>

        <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded-xl">
          Send inn
        </button>
      </form>
    </main>
  );
}
