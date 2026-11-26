"use client";

import React, { useEffect, useState } from "react";
import { API_BASE } from "../lib/api";

type StaffTab = "sales" | "wms" | "iot";

export default function StaffPortalPage() {
  const [activeTab, setActiveTab] = useState<StaffTab>("sales");
  const [staffEmail, setStaffEmail] = useState("budi.santoso@duakelinci.id");
  const [toast, setToast] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // Sales Route State
  const [salesRouteData, setSalesRouteData] = useState<any>(null);
  const [activeVisitId, setActiveVisitId] = useState<number | null>(null);
  const [selectedStop, setSelectedStop] = useState<any>(null);
  const [checkOutForm, setCheckOutForm] = useState({
    order_amount_idr: 3500000,
    order_carton_qty: 35,
    notes: "Repeat order berjalan lancar, stok rak terisi.",
    duration_minutes: 25,
  });

  // WMS State
  const [barcodeQuery, setBarcodeQuery] = useState("8992741001234");
  const [barcodeResult, setBarcodeResult] = useState<any>(null);
  const [fefoResult, setFefoResult] = useState<any>(null);
  const [wmsTransactions, setWmsTransactions] = useState<any[]>([]);
  const [inboundForm, setInboundForm] = useState({
    warehouse_id: "WH-HO-PATI",
    sku_id: "SKU-KCG-001",
    sku_name: "Kacang Garing 200g",
    brand: "Dua Kelinci",
    batch_no: "BATCH-DK-202611-02",
    expiry_date: "2027-11-30",
    qty_carton: 120,
    reference_doc_no: "PO-STAF-2026",
  });

  // IoT Technician State
  const [iotStatus, setIotStatus] = useState<any>(null);

  const showToast = (type: "success" | "error", message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 4000);
  };

  const loadSalesRoute = async () => {
    try {
      const res = await fetch(
        `${API_BASE}/sales-route/daily-plan?salesman_email=${encodeURIComponent(staffEmail)}&plan_date=2026-10-31`
      );
      const data = await res.json();
      setSalesRouteData(data);
    } catch {
      showToast("error", "Gagal memuat rute kunjungan sales.");
    }
  };

  const loadWms = async () => {
    try {
      const res = await fetch(`${API_BASE}/wms/transactions`);
      const data = await res.json();
      setWmsTransactions(Array.isArray(data) ? data : []);
    } catch {
      showToast("error", "Gagal memuat transaksi gudang.");
    }
  };

  const loadIot = async () => {
    try {
      const res = await fetch(`${API_BASE}/iot/live-status`);
      const data = await res.json();
      setIotStatus(data);
    } catch {
      showToast("error", "Gagal memuat status mesin IoT.");
    }
  };

  useEffect(() => {
    if (activeTab === "sales") loadSalesRoute();
    if (activeTab === "wms") loadWms();
    if (activeTab === "iot") loadIot();
  }, [activeTab, staffEmail]);

  // Sales Actions
  const handleCheckIn = async (stop: any) => {
    try {
      const res = await fetch(`${API_BASE}/sales-route/check-in`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          call_plan_id: stop.id,
          salesman_email: staffEmail,
          salesman_name: staffEmail.split("@")[0].replace(".", " ").toUpperCase(),
          outlet_id: stop.outlet_id,
          outlet_name: stop.outlet_name,
          latitude: (stop.target_lat || -6.2) + (Math.random() * 0.0002 - 0.0001),
          longitude: (stop.target_lng || 106.8) + (Math.random() * 0.0002 - 0.0001),
          visit_purpose: "ORDER_TAKING",
        }),
      });
      const data = await res.json();
      if (data.success) {
        setActiveVisitId(data.visit_id);
        setSelectedStop(stop);
        showToast("success", `Check-in GPS berhasil (${data.distance_meters}m).`);
        loadSalesRoute();
      } else {
        showToast("error", data.detail || "Gagal check-in.");
      }
    } catch {
      showToast("error", "Koneksi ke server gagal saat check-in.");
    }
  };

  const handleCheckOut = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeVisitId) return;
    try {
      const res = await fetch(`${API_BASE}/sales-route/check-out`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          visit_id: activeVisitId,
          ...checkOutForm,
        }),
      });
      const data = await res.json();
      if (data.success) {
        showToast("success", `Check-out selesai! Order Rp ${checkOutForm.order_amount_idr.toLocaleString("id-ID")} tercatat.`);
        setActiveVisitId(null);
        setSelectedStop(null);
        loadSalesRoute();
      } else {
        showToast("error", data.detail || "Gagal check-out.");
      }
    } catch {
      showToast("error", "Koneksi ke server gagal saat check-out.");
    }
  };

  // WMS Actions
  const handleBarcodeLookup = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/wms/barcode-lookup?barcode=${encodeURIComponent(barcodeQuery)}`);
      const data = await res.json();
      setBarcodeResult(data);
    } catch {
      showToast("error", "Gagal mencari barcode.");
    }
  };

  const handleInboundSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/wms/inbound`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...inboundForm, operator_email: staffEmail }),
      });
      const data = await res.json();
      if (data.success) {
        showToast("success", `Inbound dicatat (${data.transaction_no}). Antrean QAD: PENDING.`);
        loadWms();
      } else {
        showToast("error", data.detail || "Gagal mencatat inbound.");
      }
    } catch {
      showToast("error", "Gagal menghubungi server WMS.");
    }
  };

  const handleCheckFefo = async () => {
    try {
      const res = await fetch(`${API_BASE}/wms/fefo-recommendation?warehouse_id=WH-BDG&sku=Sukro%20Pedas%20100g&qty=50`);
      const data = await res.json();
      setFefoResult(data);
    } catch {
      showToast("error", "Gagal memuat rekomendasi FEFO.");
    }
  };

  const handleQadSync = async () => {
    try {
      const res = await fetch(`${API_BASE}/wms/qad/trigger-sync`, { method: "POST" });
      const data = await res.json();
      showToast("success", `Sinkronisasi QAD selesai (${data.synced_records ?? 0} transaksi).`);
      loadWms();
    } catch {
      showToast("error", "Gagal sinkronisasi QAD.");
    }
  };

  // IoT Actions
  const handleAckAlert = async (alertId: string | number) => {
    try {
      const res = await fetch(`${API_BASE}/iot/alerts/${alertId}/acknowledge`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ acknowledged_by: staffEmail }),
      });
      const data = await res.json();
      if (data.success) {
        showToast("success", `Alert #${alertId} dikonfirmasi (Acknowledged).`);
        loadIot();
      }
    } catch {
      showToast("error", "Gagal acknowledge alert.");
    }
  };

  const handleResolveAlert = async (alertId: string | number) => {
    try {
      const res = await fetch(`${API_BASE}/iot/alerts/${alertId}/resolve`, { method: "POST" });
      const data = await res.json();
      if (data.success) {
        showToast("success", `Alert #${alertId} ditandai selesai (Resolved).`);
        loadIot();
      }
    } catch {
      showToast("error", "Gagal resolve alert.");
    }
  };

  const stops = salesRouteData?.stops || salesRouteData?.call_plans || [];
  const alerts = iotStatus?.active_alerts || [];
  const machines = iotStatus?.machines || [];

  return (
    <div className="min-h-screen bg-[#F4F5FA] text-[#3A3541] pb-24">
      {/* Top App Bar */}
      <header className="sticky top-0 z-20 bg-white border-b border-[rgba(58,53,65,0.08)] px-4 py-3 shadow-sm">
        <div className="max-w-3xl mx-auto flex items-center justify-between gap-2">
          <div className="flex items-center space-x-2.5">
            <div
              className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#56CA00] to-[#3F9700] flex items-center justify-center text-white font-black text-sm shadow"
            >
              2K
            </div>
            <div>
              <h1 className="text-sm font-extrabold leading-tight">Portal Staf</h1>
              <p className="text-[11px] text-slate-400">Operasional Lapangan &amp; Pabrik</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <select
              value={staffEmail}
              onChange={(e) => setStaffEmail(e.target.value)}
              className="text-xs bg-[#F9FAFC] border border-slate-200 rounded-lg px-2 py-1.5 font-semibold max-w-[165px] truncate outline-none focus:ring-1 focus:ring-[#56CA00]"
            >
              <option value="budi.santoso@duakelinci.id">Budi (Sales Jakarta)</option>
              <option value="eko.prasetyo@duakelinci.id">Eko (Sales Surabaya)</option>
              <option value="surya.picker@duakelinci.id">Surya (Operator Gudang)</option>
              <option value="agus.wh.bdg@duakelinci.id">Agus (WH Bandung)</option>
              <option value="teknisi.pati@duakelinci.id">Teknisi Pabrik Pati</option>
            </select>
          </div>
        </div>
      </header>

      {/* Toast Notification */}
      {toast && (
        <div className="max-w-3xl mx-auto px-4 pt-3">
          <div
            className={`px-4 py-2.5 rounded-xl text-xs font-bold flex items-center justify-between shadow-sm ${
              toast.type === "success"
                ? "bg-[#56CA00]/15 text-[#2E7000] border border-[#56CA00]/30"
                : "bg-[#FF4C51]/15 text-[#B42318] border border-[#FF4C51]/30"
            }`}
          >
            <span>{toast.message}</span>
            <button onClick={() => setToast(null)} className="ml-3 opacity-70 hover:opacity-100">
              <i className="fa-solid fa-xmark"></i>
            </button>
          </div>
        </div>
      )}

      {/* Desktop / Tablet Tab Pills */}
      <div className="max-w-3xl mx-auto px-4 pt-4">
        <div className="grid grid-cols-3 gap-2 bg-white p-1.5 rounded-2xl border border-slate-200/80 shadow-sm">
          <button
            onClick={() => setActiveTab("sales")}
            className={`py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition ${
              activeTab === "sales" ? "bg-[#16B1FF] text-white shadow" : "text-slate-600 hover:bg-slate-50"
            }`}
          >
            <i className="fa-solid fa-route"></i>
            <span>Sales</span>
          </button>
          <button
            onClick={() => setActiveTab("wms")}
            className={`py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition ${
              activeTab === "wms" ? "bg-[#56CA00] text-white shadow" : "text-slate-600 hover:bg-slate-50"
            }`}
          >
            <i className="fa-solid fa-boxes-stacked"></i>
            <span>Gudang</span>
          </button>
          <button
            onClick={() => setActiveTab("iot")}
            className={`py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center space-x-1.5 transition ${
              activeTab === "iot" ? "bg-[#FF4C51] text-white shadow" : "text-slate-600 hover:bg-slate-50"
            }`}
          >
            <i className="fa-solid fa-industry"></i>
            <span>Teknisi IoT</span>
            {alerts.length > 0 && (
              <span className="ml-1 px-1.5 py-0.5 text-[10px] rounded-full bg-white text-[#FF4C51] font-black">
                {alerts.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 py-4 space-y-4">
        {/* ================= TAB 1: SALES LAPANGAN ================= */}
        {activeTab === "sales" && (
          <div className="space-y-4">
            {/* Summary Banner */}
            <div className="bg-gradient-to-r from-[#16B1FF] to-[#0095E8] text-white rounded-2xl p-4 shadow-md flex items-center justify-between">
              <div>
                <p className="text-[11px] uppercase tracking-wider font-bold opacity-85">Rute Kunjungan Hari Ini</p>
                <h2 className="text-lg font-black mt-0.5">{stops.length} Outlet Dijadwalkan</h2>
                <p className="text-xs opacity-90 mt-0.5">{staffEmail}</p>
              </div>
              <button
                onClick={loadSalesRoute}
                className="px-3 py-2 rounded-xl bg-white/20 hover:bg-white/30 text-xs font-bold transition"
              >
                <i className="fa-solid fa-rotate mr-1"></i> Refresh
              </button>
            </div>

            {/* Active Visit Check-out Form */}
            {activeVisitId && selectedStop && (
              <form
                onSubmit={handleCheckOut}
                className="bg-white rounded-2xl p-4 border-2 border-[#16B1FF] shadow-md space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-extrabold text-[#16B1FF] uppercase">
                    <i className="fa-solid fa-location-dot mr-1"></i> Sedang Berkunjung: {selectedStop.outlet_name}
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#16B1FF]/10 text-[#16B1FF]">
                    Visit #{activeVisitId}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-bold text-slate-500 mb-1">Nilai Order (Rp)</label>
                    <input
                      type="number"
                      value={checkOutForm.order_amount_idr}
                      onChange={(e) => setCheckOutForm({ ...checkOutForm, order_amount_idr: Number(e.target.value) })}
                      className="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs font-semibold"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-bold text-slate-500 mb-1">Qty Karton</label>
                    <input
                      type="number"
                      value={checkOutForm.order_carton_qty}
                      onChange={(e) => setCheckOutForm({ ...checkOutForm, order_carton_qty: Number(e.target.value) })}
                      className="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs font-semibold"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-500 mb-1">Catatan Kunjungan</label>
                  <textarea
                    rows={2}
                    value={checkOutForm.notes}
                    onChange={(e) => setCheckOutForm({ ...checkOutForm, notes: e.target.value })}
                    className="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full py-2.5 rounded-xl bg-[#56CA00] hover:bg-[#49AD00] text-white text-xs font-extrabold shadow transition"
                >
                  <i className="fa-solid fa-circle-check mr-1.5"></i> Selesaikan Kunjungan &amp; Simpan Order
                </button>
              </form>
            )}

            {/* Outlet List */}
            <div className="space-y-3">
              {stops.length === 0 ? (
                <div className="bg-white rounded-2xl p-6 text-center text-xs text-slate-400 border border-slate-100">
                  Belum ada jadwal kunjungan untuk akun ini.
                </div>
              ) : (
                stops.map((stop: any, idx: number) => (
                  <div
                    key={stop.id || idx}
                    className="bg-white rounded-2xl p-4 border border-slate-100 shadow-sm flex items-center justify-between gap-3"
                  >
                    <div className="min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className="w-6 h-6 rounded-full bg-slate-100 text-slate-700 text-[11px] font-black flex items-center justify-center flex-shrink-0">
                          {idx + 1}
                        </span>
                        <h3 className="text-sm font-bold truncate">{stop.outlet_name || stop.outlet_id}</h3>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1 ml-8">
                        ID: {stop.outlet_id} &bull; Status:{" "}
                        <span className="font-bold text-slate-600">{stop.status || "PLANNED"}</span>
                      </p>
                    </div>
                    <button
                      onClick={() => handleCheckIn(stop)}
                      disabled={stop.status === "COMPLETED"}
                      className={`px-3.5 py-2 rounded-xl text-xs font-bold flex-shrink-0 transition ${
                        stop.status === "COMPLETED"
                          ? "bg-slate-100 text-slate-400 cursor-not-allowed"
                          : "bg-[#16B1FF] hover:bg-[#0095E8] text-white shadow-sm"
                      }`}
                    >
                      <i className="fa-solid fa-location-crosshairs mr-1"></i>
                      {stop.status === "COMPLETED" ? "Selesai" : "Check-In"}
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* ================= TAB 2: OPERATOR GUDANG (WMS) ================= */}
        {activeTab === "wms" && (
          <div className="space-y-4">
            {/* Barcode Scanner Card */}
            <form onSubmit={handleBarcodeLookup} className="bg-white rounded-2xl p-4 border border-slate-100 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-extrabold flex items-center space-x-2">
                  <i className="fa-solid fa-barcode text-[#56CA00]"></i>
                  <span>Scan / Cek Barcode Cepat</span>
                </h2>
                <button
                  type="button"
                  onClick={handleQadSync}
                  className="text-[11px] font-bold px-2.5 py-1 rounded-lg bg-[#8C57FF]/10 text-[#8C57FF] hover:bg-[#8C57FF]/20"
                >
                  <i className="fa-solid fa-arrows-rotate mr-1"></i> Sync QAD
                </button>
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={barcodeQuery}
                  onChange={(e) => setBarcodeQuery(e.target.value)}
                  placeholder="Masukkan atau scan barcode..."
                  className="flex-1 border border-slate-200 rounded-xl px-3 py-2 text-xs font-mono"
                />
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-[#56CA00] hover:bg-[#49AD00] text-white text-xs font-bold shadow-sm"
                >
                  Cek
                </button>
              </div>
              {barcodeResult && (
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1">
                  <div className="font-bold text-[#3A3541]">
                    {barcodeResult.sku_name || barcodeResult.message || "Hasil Lookup"}
                  </div>
                  <div className="text-[11px] text-slate-500">
                    SKU: {barcodeResult.sku_id || "-"} &bull; Brand: {barcodeResult.brand || "-"} &bull; Stok:{" "}
                    <strong>{barcodeResult.total_stock ?? barcodeResult.qty_available ?? "-"}</strong>
                  </div>
                </div>
              )}
            </form>

            {/* Quick Inbound Form */}
            <form onSubmit={handleInboundSubmit} className="bg-white rounded-2xl p-4 border border-slate-100 shadow-sm space-y-3">
              <h2 className="text-sm font-extrabold flex items-center space-x-2">
                <i className="fa-solid fa-truck-ramp-box text-[#56CA00]"></i>
                <span>Catat Penerimaan Barang (Inbound)</span>
              </h2>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-slate-500 mb-1">Gudang</label>
                  <input
                    type="text"
                    value={inboundForm.warehouse_id}
                    onChange={(e) => setInboundForm({ ...inboundForm, warehouse_id: e.target.value })}
                    className="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-500 mb-1">Qty (Karton)</label>
                  <input
                    type="number"
                    value={inboundForm.qty_carton}
                    onChange={(e) => setInboundForm({ ...inboundForm, qty_carton: Number(e.target.value) })}
                    className="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-500 mb-1">SKU</label>
                  <input
                    type="text"
                    value={inboundForm.sku_name}
                    onChange={(e) => setInboundForm({ ...inboundForm, sku_name: e.target.value })}
                    className="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-500 mb-1">No. Batch</label>
                  <input
                    type="text"
                    value={inboundForm.batch_no}
                    onChange={(e) => setInboundForm({ ...inboundForm, batch_no: e.target.value })}
                    className="w-full border border-slate-200 rounded-xl px-3 py-2 text-xs font-mono"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 py-2.5 rounded-xl bg-[#56CA00] hover:bg-[#49AD00] text-white text-xs font-extrabold shadow-sm"
                >
                  Simpan Inbound
                </button>
                <button
                  type="button"
                  onClick={handleCheckFefo}
                  className="px-4 py-2.5 rounded-xl bg-amber-50 text-amber-700 border border-amber-200 text-xs font-bold"
                >
                  Cek FEFO
                </button>
              </div>
              {fefoResult && (
                <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200 text-xs text-amber-900">
                  <strong>Rekomendasi FEFO:</strong> {fefoResult.recommended_batch || JSON.stringify(fefoResult).slice(0, 120)}
                </div>
              )}
            </form>

            {/* Recent Transactions */}
            <div className="bg-white rounded-2xl p-4 border border-slate-100 shadow-sm space-y-2.5">
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-400">Transaksi Gudang Terakhir</h3>
              {wmsTransactions.slice(0, 5).map((tx: any, i: number) => (
                <div key={tx.id || i} className="flex items-center justify-between py-2 border-b last:border-b-0 border-slate-100 text-xs">
                  <div>
                    <div className="font-bold">{tx.sku_name || tx.sku_id}</div>
                    <div className="text-[11px] text-slate-400">
                      {tx.transaction_type || "INBOUND"} &bull; {tx.warehouse_id} &bull; {tx.qty_carton} Ktn
                    </div>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      tx.qad_sync_status === "SYNCED"
                        ? "bg-[#56CA00]/10 text-[#3F9700]"
                        : "bg-amber-100 text-amber-700"
                    }`}
                  >
                    QAD: {tx.qad_sync_status || "PENDING"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ================= TAB 3: TEKNISI PABRIK (IOT) ================= */}
        {activeTab === "iot" && (
          <div className="space-y-4">
            {/* Active Alerts */}
            <div className="bg-white rounded-2xl p-4 border border-slate-100 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-extrabold flex items-center space-x-2 text-[#FF4C51]">
                  <i className="fa-solid fa-triangle-exclamation"></i>
                  <span>Alert Mesin Aktif ({alerts.length})</span>
                </h2>
                <button
                  onClick={loadIot}
                  className="text-xs font-bold text-slate-500 hover:text-slate-800"
                >
                  <i className="fa-solid fa-rotate mr-1"></i> Refresh
                </button>
              </div>

              {alerts.length === 0 ? (
                <div className="p-4 rounded-xl bg-[#56CA00]/10 text-[#2E7000] text-xs font-bold text-center">
                  <i className="fa-solid fa-circle-check mr-1.5"></i> Semua mesin dalam kondisi normal. Tidak ada alert aktif.
                </div>
              ) : (
                alerts.map((al: any, idx: number) => (
                  <div
                    key={al.id || al.alert_id || idx}
                    className="p-3.5 rounded-xl bg-red-50/70 border border-red-200 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-extrabold text-red-700">
                        {al.machine_id} — {al.alert_type}
                      </span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-600 text-white">
                        {al.severity || "HIGH"}
                      </span>
                    </div>
                    <p className="text-xs text-slate-700">{al.alert_message || al.message}</p>
                    <div className="flex gap-2 pt-1">
                      <button
                        onClick={() => handleAckAlert(al.alert_id || al.id)}
                        className="flex-1 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold"
                      >
                        Acknowledge
                      </button>
                      <button
                        onClick={() => handleResolveAlert(al.alert_id || al.id)}
                        className="flex-1 py-1.5 rounded-lg bg-[#56CA00] hover:bg-[#49AD00] text-white text-xs font-bold"
                      >
                        Resolve
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Machine Status List */}
            <div className="bg-white rounded-2xl p-4 border border-slate-100 shadow-sm space-y-3">
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-400">Status Mesin Realtime</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {machines.map((m: any, idx: number) => (
                  <div key={m.machine_id || idx} className="p-3 rounded-xl border border-slate-100 bg-[#F9FAFC] space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-extrabold">{m.machine_name || m.machine_id}</span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          m.status === "RUNNING" || m.machine_status === "RUNNING"
                            ? "bg-[#56CA00]/15 text-[#2E7000]"
                            : "bg-red-100 text-red-700"
                        }`}
                      >
                        {m.status || m.machine_status || "UNKNOWN"}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-1 text-[11px] text-slate-500 pt-1">
                      <div>
                        Suhu: <strong className="text-slate-800">{m.temperature ?? "-"}°C</strong>
                      </div>
                      <div>
                        Getar: <strong className="text-slate-800">{m.vibration ?? "-"}</strong>
                      </div>
                      <div>
                        Out: <strong className="text-slate-800">{m.output_counter ?? "-"}</strong>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Mobile Bottom Navigation */}
      <nav className="fixed bottom-0 inset-x-0 bg-white border-t border-slate-200 px-4 py-2 flex justify-around items-center sm:hidden z-30 shadow-[0_-4px_12px_rgba(0,0,0,0.04)]">
        <button
          onClick={() => setActiveTab("sales")}
          className={`flex flex-col items-center text-[11px] font-bold ${
            activeTab === "sales" ? "text-[#16B1FF]" : "text-slate-400"
          }`}
        >
          <i className="fa-solid fa-route text-base mb-0.5"></i>
          <span>Sales</span>
        </button>
        <button
          onClick={() => setActiveTab("wms")}
          className={`flex flex-col items-center text-[11px] font-bold ${
            activeTab === "wms" ? "text-[#56CA00]" : "text-slate-400"
          }`}
        >
          <i className="fa-solid fa-boxes-stacked text-base mb-0.5"></i>
          <span>Gudang</span>
        </button>
        <button
          onClick={() => setActiveTab("iot")}
          className={`flex flex-col items-center text-[11px] font-bold ${
            activeTab === "iot" ? "text-[#FF4C51]" : "text-slate-400"
          }`}
        >
          <i className="fa-solid fa-industry text-base mb-0.5"></i>
          <span>IoT</span>
        </button>
      </nav>
    </div>
  );
}
