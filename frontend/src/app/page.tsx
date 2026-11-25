"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { API_BASE } from "../lib/api";

export default function HomePage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [persona, setPersona] = useState("muhammad.wyzer@gmail.com");
  const [overview, setOverview] = useState<any>(null);
  const [esignDocs, setEsignDocs] = useState<any[]>([]);

  // 1. Date Range Filter State
  const [startDate, setStartDate] = useState("2026-09-01");
  const [endDate, setEndDate] = useState("2026-10-31");
  const [presetDate, setPresetDate] = useState("sep-oct");

  // 2. Charts Data State
  const [dailyTrends, setDailyTrends] = useState<any[]>([]);
  const [brandBreakdown, setBrandBreakdown] = useState<any[]>([]);

  // 3. FITUR 2: WMS GUDANG RINGAN (Inbound, Outbound, Opname, Barcode, QAD)
  const [wmsSubTab, setWmsSubTab] = useState<"transactions" | "opname" | "fefo" | "barcode">("transactions");
  const [wmsTransactions, setWmsTransactions] = useState<any[]>([]);
  const [opnameSessions, setOpnameSessions] = useState<any[]>([]);
  const [fefoResult, setFefoResult] = useState<any>(null);
  const [barcodeQuery, setBarcodeQuery] = useState("8992741001234");
  const [barcodeResult, setBarcodeResult] = useState<any>(null);
  const [inboundModal, setInboundModal] = useState(false);
  const [inboundForm, setInboundForm] = useState({
    warehouse_id: "WH-HO-PATI",
    sku_id: "SKU-KCG-001",
    sku_name: "Kacang Garing 200g",
    brand: "Dua Kelinci",
    batch_no: "BATCH-DK-202611-01",
    expiry_date: "2027-11-30",
    qty_carton: 250,
    reference_doc_no: "PO-PABRIK-1099"
  });

  // 4. FITUR 4: RUTE SALES LAPANGAN (Call Plan, Peta, GPS Geofencing, Take Order)
  const [salesRouteData, setSalesRouteData] = useState<any>(null);
  const [selectedCallStop, setSelectedCallStop] = useState<any>(null);
  const [salesCheckInModal, setSalesCheckInModal] = useState(false);
  const [salesCheckOutModal, setSalesCheckOutModal] = useState(false);
  const [activeVisitId, setActiveVisitId] = useState<number | null>(null);
  const [checkOutForm, setCheckOutForm] = useState({
    order_amount_idr: 4500000,
    order_carton_qty: 45,
    notes: "Toko repeat order 45 karton Kacang Sukro & Deka.",
    duration_minutes: 30
  });

  // 5. FITUR 5: IOT PABRIK SHOP FLOOR (Sensor, Status Mesin, Alert, OEE)
  const [iotStatus, setIotStatus] = useState<any>(null);
  const [iotSubTab, setIotSubTab] = useState<"overview" | "machines" | "devices" | "oee_report">("overview");
  const [deviceHealthList, setDeviceHealthList] = useState<any[]>([]);

  // Master Data State
  const [masterSubTab, setMasterSubTab] = useState<"outlets" | "products" | "warehouses" | "employees">("employees");
  const [isMasterMenuOpen, setIsMasterMenuOpen] = useState(true);
  const [products, setProducts] = useState<any[]>([]);
  const [outlets, setOutlets] = useState<any[]>([]);
  const [warehouses, setWarehouses] = useState<any[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);

  // Search & Filter State for Master Data
  const [empSearch, setEmpSearch] = useState<string>("");
  const [empDeptFilter, setEmpDeptFilter] = useState<string>("ALL");
  const [empRoleFilter, setEmpRoleFilter] = useState<string>("ALL");

  const [outletSearch, setOutletSearch] = useState<string>("");
  const [outletTypeFilter, setOutletTypeFilter] = useState<string>("ALL");
  const [outletRegionFilter, setOutletRegionFilter] = useState<string>("ALL");

  const [productSearch, setProductSearch] = useState<string>("");
  const [productBrandFilter, setProductBrandFilter] = useState<string>("ALL");

  const [whSearch, setWhSearch] = useState<string>("");
  const [whRegionFilter, setWhRegionFilter] = useState<string>("ALL");

  const [editingItem, setEditingItem] = useState<{ mode: "edit" | "add"; type: "outlets" | "products" | "warehouses" | "employees"; data: any } | null>(null);

  // --- DATA LOADERS ---
  const loadDashboardAnalytics = async () => {
    try {
      const [resOverview, resTrends, resBrands] = await Promise.all([
        fetch(`${API_BASE}/dashboard/overview?start_date=${startDate}&end_date=${endDate}`, {
          headers: { "X-User-Email": persona }
        }).then(r => r.json()),
        fetch(`${API_BASE}/dashboard/charts/daily-trend?start_date=${startDate}&end_date=${endDate}`, {
          headers: { "X-User-Email": persona }
        }).then(r => r.json()),
        fetch(`${API_BASE}/dashboard/breakdown/brand?start_date=${startDate}&end_date=${endDate}`, {
          headers: { "X-User-Email": persona }
        }).then(r => r.json())
      ]);
      setOverview(resOverview);
      setDailyTrends(resTrends || []);
      setBrandBreakdown(resBrands || []);
    } catch (err) {
      console.error("Dashboard Analytics load error:", err);
    }
  };

  const loadWmsData = async () => {
    try {
      const [resTx, resOpn] = await Promise.all([
        fetch(`${API_BASE}/wms/transactions`).then(r => r.json()),
        fetch(`${API_BASE}/wms/opname/sessions`).then(r => r.json())
      ]);
      setWmsTransactions(resTx || []);
      setOpnameSessions(resOpn || []);
    } catch (err) {
      console.error("WMS load error:", err);
    }
  };

  const loadSalesRoute = async () => {
    try {
      const res = await fetch(`${API_BASE}/sales-route/daily-plan?salesman_email=${encodeURIComponent(persona)}&plan_date=2026-10-31`);
      const data = await res.json();
      setSalesRouteData(data);
    } catch (err) {
      console.error("Sales route load error:", err);
    }
  };

  const loadIotStatus = async () => {
    try {
      const [resStatus, resDevices] = await Promise.all([
        fetch(`${API_BASE}/iot/live-status`).then(r => r.json()),
        fetch(`${API_BASE}/iot/devices/health`).then(r => r.json())
      ]);
      setIotStatus(resStatus);
      setDeviceHealthList(resDevices || []);
    } catch (err) {
      console.error("IoT load error:", err);
    }
  };

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      const res = await fetch(`${API_BASE}/iot/alerts/${alertId}/acknowledge`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ acknowledged_by: persona })
      });
      const data = await res.json();
      if (data.success) {
        alert("Alert telah dikonfirmasi (Acknowledged) oleh supervisor shift!");
        loadIotStatus();
      }
    } catch (e) {
      alert("Gagal acknowledge alert: " + e);
    }
  };

  const loadMasterData = async () => {
    try {
      const [resOutlets, resProducts, resWh, resEmp] = await Promise.all([
        fetch(`${API_BASE}/master/outlets`).then(r => r.json()),
        fetch(`${API_BASE}/master/products`).then(r => r.json()),
        fetch(`${API_BASE}/master/warehouses`).then(r => r.json()),
        fetch(`${API_BASE}/master/employees`).then(r => r.json())
      ]);
      setOutlets(resOutlets || []);
      setProducts(resProducts || []);
      setWarehouses(resWh || []);
      setEmployees(resEmp || []);
    } catch (e) {
      console.error("Master data load error:", e);
    }
  };

  const loadEsignDocs = async () => {
    try {
      const res = await fetch(`${API_BASE}/esign/documents`);
      const data = await res.json();
      setEsignDocs(data || []);
    } catch (err) {
      console.error("eSign load error:", err);
    }
  };

  useEffect(() => {
    loadDashboardAnalytics();
  }, [persona, startDate, endDate]);

  useEffect(() => {
    loadMasterData();
    loadEsignDocs();
    loadWmsData();
    loadSalesRoute();
    loadIotStatus();
  }, [persona]);

  useEffect(() => {
    if (activeTab === "wms") loadWmsData();
    if (activeTab === "sales_route") loadSalesRoute();
    if (activeTab === "iot") loadIotStatus();
    if (activeTab === "master") loadMasterData();
    if (activeTab === "esign") loadEsignDocs();
  }, [activeTab]);

  // --- ACTIONS: WMS ---
  const handleTriggerQadSync = async () => {
    try {
      const res = await fetch(`${API_BASE}/wms/qad/trigger-sync`, { method: "POST" });
      const data = await res.json();
      alert(`Sinkronisasi ERP QAD Berhasil! ${data.synced_records} transaksi telah diposting.`);
      loadWmsData();
    } catch (e) {
      alert("Gagal sinkron QAD: " + e);
    }
  };

  const handleInboundSubmit = async () => {
    try {
      const res = await fetch(`${API_BASE}/wms/inbound`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...inboundForm, operator_email: persona })
      });
      const data = await res.json();
      if (data.success) {
        alert(`Penerimaan barang berhasil dicatat (${data.transaction_no})! Status antrean QAD: PENDING.`);
        setInboundModal(false);
        loadWmsData();
      }
    } catch (e) {
      alert("Gagal simpan inbound: " + e);
    }
  };

  const handleBarcodeLookup = async () => {
    try {
      const res = await fetch(`${API_BASE}/wms/barcode-lookup?barcode=${encodeURIComponent(barcodeQuery)}`);
      const data = await res.json();
      setBarcodeResult(data);
    } catch (e) {
      alert("Gagal lookup barcode: " + e);
    }
  };

  const handleCheckFEFO = async () => {
    try {
      const res = await fetch(`${API_BASE}/wms/fefo-recommendation?warehouse_id=WH-BDG&sku=Sukro%20Pedas%20100g&qty=50`);
      const data = await res.json();
      setFefoResult(data);
    } catch (e) {
      alert("Gagal FEFO: " + e);
    }
  };

  // --- ACTIONS: MASTER DATA & CSV ---
  const handleExportCsv = (type: string) => {
    let dataToExport: any[] = [];
    let filename = `master_${type}_${new Date().toISOString().slice(0, 10)}.csv`;

    if (type === "employees") dataToExport = employees;
    else if (type === "outlets") dataToExport = outlets;
    else if (type === "products") dataToExport = products;
    else if (type === "warehouses") dataToExport = warehouses;

    if (!dataToExport || dataToExport.length === 0) {
      alert("Tidak ada data untuk diekspor.");
      return;
    }

    const headers = Object.keys(dataToExport[0]).join(",");
    const rows = dataToExport.map(item =>
      Object.values(item).map(val => `"${String(val ?? '').replace(/"/g, '""')}"`).join(",")
    ).join("\n");

    const blob = new Blob([`${headers}\n${rows}`], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleImportCsv = async (entityType: string, event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      const csvContent = e.target?.result as string;
      if (!csvContent) return;

      try {
        const res = await fetch(`${API_BASE}/master/import-csv`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ entity_type: entityType, csv_content: csvContent })
        });
        const data = await res.json();
        if (data.success) {
          alert(`Sukses! ${data.message}`);
          loadMasterData();
        } else {
          alert(`Gagal impor: ${data.detail || "Terjadi kesalahan"}`);
        }
      } catch (err) {
        alert(`Gagal mengunggah file CSV: ${err}`);
      }
    };
    reader.readAsText(file);
    // Reset file input
    event.target.value = "";
  };

  const handleImportSalesCsv = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      const csvContent = e.target?.result as string;
      if (!csvContent) return;

      try {
        const res = await fetch(`${API_BASE}/dashboard/import-sales-csv`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ csv_content: csvContent })
        });
        const data = await res.json();
        if (data.success) {
          alert(`Sukses! ${data.message}`);
          loadDashboardAnalytics();
        } else {
          alert(`Gagal impor: ${data.detail || "Terjadi kesalahan"}`);
        }
      } catch (err) {
        alert(`Gagal mengunggah sales CSV: ${err}`);
      }
    };
    reader.readAsText(file);
    event.target.value = "";
  };

  const handleDeleteMasterItem = async (type: string, id: string) => {
    if (!confirm(`Apakah Anda yakin ingin menghapus data ${type} ID: ${id}?`)) return;
    try {
      const endpoint = type === "employees" ? `employees/${id}` :
                       type === "outlets" ? `outlets/${id}` :
                       type === "products" ? `products/${id}` : `warehouses/${id}`;
      const res = await fetch(`${API_BASE}/master/${endpoint}`, { method: "DELETE" });
      const data = await res.json();
      if (data.success) {
        alert(`Data ${id} berhasil dihapus.`);
        loadMasterData();
      }
    } catch (e) {
      alert("Gagal menghapus data: " + e);
    }
  };

  const handleSaveMasterItem = async () => {
    if (!editingItem) return;
    try {
      const { mode, type, data } = editingItem;
      const isAdd = mode === "add";
      let url = `${API_BASE}/master/${type}`;
      let method = isAdd ? "POST" : "PUT";

      if (!isAdd) {
        const id = type === "employees" ? data.employee_id :
                   type === "outlets" ? data.outlet_id :
                   type === "products" ? data.sku_id : data.warehouse_id;
        url = `${API_BASE}/master/${type}/${id}`;
      }

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      const result = await res.json();
      if (result.success) {
        alert(`Data master ${type} berhasil disimpan!`);
        setEditingItem(null);
        loadMasterData();
      } else {
        alert(`Gagal: ${result.detail || "Terjadi kesalahan"}`);
      }
    } catch (e) {
      alert("Gagal menyimpan data master: " + e);
    }
  };

  // --- ACTIONS: SALES ROUTE ---
  const handleSalesCheckIn = async (stop: any) => {
    try {
      const res = await fetch(`${API_BASE}/sales-route/check-in`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          call_plan_id: stop.id,
          salesman_email: persona,
          salesman_name: persona.split("@")[0].replace(".", " ").toUpperCase(),
          outlet_id: stop.outlet_id,
          outlet_name: stop.outlet_name,
          latitude: stop.target_lat + (Math.random() * 0.0002 - 0.0001),
          longitude: stop.target_lng + (Math.random() * 0.0002 - 0.0001),
          visit_purpose: "ORDER_TAKING"
        })
      });
      const data = await res.json();
      if (data.success) {
        alert(`Check-in GPS Berhasil! Radius: ${data.distance_meters}m (Geofence Valid). Status: CHECKED_IN.`);
        setActiveVisitId(data.visit_id);
        loadSalesRoute();
      }
    } catch (e) {
      alert("Gagal check-in: " + e);
    }
  };

  const handleSalesCheckOutSubmit = async () => {
    if (!activeVisitId) return;
    try {
      const res = await fetch(`${API_BASE}/sales-route/check-out`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          visit_id: activeVisitId,
          ...checkOutForm
        })
      });
      const data = await res.json();
      if (data.success) {
        alert(`Check-out Kunjungan Selesai! Take Order Rp ${checkOutForm.order_amount_idr.toLocaleString('id-ID')} dicatat.`);
        setSalesCheckOutModal(false);
        setActiveVisitId(null);
        loadSalesRoute();
      }
    } catch (e) {
      alert("Gagal check-out: " + e);
    }
  };

  // --- ACTIONS: IOT PABRIK ---
  const handleResolveAlert = async (alertId: number) => {
    try {
      const res = await fetch(`${API_BASE}/iot/alerts/${alertId}/resolve`, { method: "POST" });
      const data = await res.json();
      if (data.success) {
        alert("Alert mesin berhasil ditandai telah diselesaikan oleh teknisi!");
        loadIotStatus();
      }
    } catch (e) {
      alert("Gagal resolve alert: " + e);
    }
  };

  const isWarehousePersona = persona.includes("warehouse") || persona.includes(".wh.") || persona.includes("picker") || persona.includes("checker");

  // Chart calculation metrics
  const maxTrendSales = Math.max(...dailyTrends.map(t => t.net_sales_idr || 0), 1);
  const totalBrandSales = brandBreakdown.reduce((acc, curr) => acc + (curr.net_sales_idr || 0), 0) || 1;

  return (
    <div className="flex min-h-screen bg-[#F4F5FA] font-sans text-[#3A3541]">
      
      {/* 1. VERTICAL SIDEBAR MENU (Materio MUI Free Theme Style) */}
      <aside className="w-64 bg-white border-r border-[rgba(58,53,65,0.12)] flex flex-col justify-between shadow-[0_4px_14px_0_rgba(58,53,65,0.06)] flex-shrink-0 z-20">
        <div>
          {/* Brand Header */}
          <div className="p-5 border-b border-[rgba(58,53,65,0.08)] flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#8C57FF] to-[#A379FF] flex items-center justify-center text-white font-black text-xl shadow-[0_4px_12px_rgba(140,87,255,0.4)]">
              2K
            </div>
            <div>
              <h1 className="font-extrabold text-sm tracking-wide text-[#3A3541] uppercase">Dua Kelinci</h1>
              <p className="text-[11px] text-[#8C57FF] font-semibold">Materio Enterprise Ops</p>
            </div>
          </div>

          {/* Active Persona Badge */}
          <div className="px-4 py-2.5 bg-[#F9FAFC] border-b border-[rgba(58,53,65,0.06)] flex items-center space-x-2">
            <span className={`w-2.5 h-2.5 rounded-full ${isWarehousePersona ? 'bg-[#8C57FF]' : 'bg-[#FF4C51]'} animate-pulse`}></span>
            <div className="overflow-hidden">
              <span className="block text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                Persona: {isWarehousePersona ? 'Warehouse / Logistik' : 'Sales & Distribution'}
              </span>
              <span className="block text-xs font-bold text-[#3A3541] truncate">
                {persona}
              </span>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="p-3 space-y-1">
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition ${
                activeTab === "dashboard"
                  ? "bg-gradient-to-r from-[#8C57FF] to-[#9E6FFF] text-white shadow-[0_4px_10px_rgba(140,87,255,0.35)] font-bold"
                  : "text-slate-600 hover:bg-[rgba(58,53,65,0.04)] hover:text-[#8C57FF]"
              }`}
            >
              <i className="fa-solid fa-chart-line text-sm w-4"></i>
              <span>Dashboard &amp; Charts</span>
            </button>

            {/* FITUR 2: GUDANG (WMS RINGAN) */}
            <button
              onClick={() => setActiveTab("wms")}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-semibold transition ${
                activeTab === "wms"
                  ? "bg-[#56CA00] text-white shadow-[0_4px_10px_rgba(86,202,0,0.35)] font-bold"
                  : "text-slate-600 hover:bg-[rgba(58,53,65,0.04)] hover:text-[#56CA00]"
              }`}
            >
              <div className="flex items-center space-x-3">
                <i className="fa-solid fa-boxes-stacked text-sm w-4"></i>
                <span>Gudang (WMS Ringan)</span>
              </div>
              <span className="text-[10px] bg-white/20 px-1.5 py-0.5 rounded font-mono">QAD</span>
            </button>

            {/* FITUR 4: RUTE SALES LAPANGAN */}
            <button
              onClick={() => setActiveTab("sales_route")}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-semibold transition ${
                activeTab === "sales_route"
                  ? "bg-[#16B1FF] text-white shadow-[0_4px_10px_rgba(22,177,255,0.35)] font-bold"
                  : "text-slate-600 hover:bg-[rgba(58,53,65,0.04)] hover:text-[#16B1FF]"
              }`}
            >
              <div className="flex items-center space-x-3">
                <i className="fa-solid fa-route text-sm w-4"></i>
                <span>Rute Sales Lapangan</span>
              </div>
              <span className="text-[10px] bg-white/20 px-1.5 py-0.5 rounded font-mono">GPS</span>
            </button>

            {/* FITUR 5: IOT PABRIK SHOP FLOOR */}
            <button
              onClick={() => setActiveTab("iot")}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-semibold transition ${
                activeTab === "iot"
                  ? "bg-[#FF4C51] text-white shadow-[0_4px_10px_rgba(255,76,81,0.35)] font-bold"
                  : "text-slate-600 hover:bg-[rgba(58,53,65,0.04)] hover:text-[#FF4C51]"
              }`}
            >
              <div className="flex items-center space-x-3">
                <i className="fa-solid fa-industry text-sm w-4"></i>
                <span>IoT Pabrik &amp; OEE</span>
              </div>
              {iotStatus && iotStatus.active_alerts_count > 0 && (
                <span className="text-[10px] bg-white text-red-600 font-black px-1.5 py-0.5 rounded-full animate-bounce">
                  {iotStatus.active_alerts_count}
                </span>
              )}
            </button>

            {/* MASTER DATA */}
            <div className="space-y-0.5">
              <button
                onClick={() => {
                  setActiveTab("master");
                  setIsMasterMenuOpen(!isMasterMenuOpen);
                }}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-semibold transition ${
                  activeTab === "master"
                    ? "bg-[#8C57FF] text-white shadow-[0_4px_10px_rgba(140,87,255,0.35)] font-bold"
                    : "text-slate-600 hover:bg-[rgba(58,53,65,0.04)] hover:text-[#8C57FF]"
                }`}
              >
                <div className="flex items-center space-x-3">
                  <i className="fa-solid fa-database text-sm w-4"></i>
                  <span>Master Data MDM</span>
                </div>
                <i className={`fa-solid fa-chevron-down text-[10px] transition-transform duration-200 ${isMasterMenuOpen ? "transform rotate-180" : ""}`}></i>
              </button>

              {isMasterMenuOpen && (
                <div className="ml-4 pl-3 border-l-2 border-[#8C57FF]/30 space-y-1 py-1">
                  <button
                    onClick={() => { setActiveTab("master"); setMasterSubTab("employees"); }}
                    className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-[11px] font-medium transition ${
                      activeTab === "master" && masterSubTab === "employees" ? "bg-[#8C57FF]/10 text-[#8C57FF] font-bold" : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    <span>Master Karyawan</span>
                    <span className="text-[10px] bg-slate-200/80 px-1.5 py-0.5 rounded text-slate-700 font-bold">{employees.length}</span>
                  </button>
                  <button
                    onClick={() => { setActiveTab("master"); setMasterSubTab("outlets"); }}
                    className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-[11px] font-medium transition ${
                      activeTab === "master" && masterSubTab === "outlets" ? "bg-[#56CA00]/10 text-[#56CA00] font-bold" : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    <span>Master Outlet</span>
                    <span className="text-[10px] bg-slate-200/80 px-1.5 py-0.5 rounded text-slate-700 font-bold">{outlets.length}</span>
                  </button>
                  <button
                    onClick={() => { setActiveTab("master"); setMasterSubTab("products"); }}
                    className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-[11px] font-medium transition ${
                      activeTab === "master" && masterSubTab === "products" ? "bg-[#FFB400]/10 text-[#FFB400] font-bold" : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    <span>Master SKU</span>
                    <span className="text-[10px] bg-slate-200/80 px-1.5 py-0.5 rounded text-slate-700 font-bold">{products.length}</span>
                  </button>
                  <button
                    onClick={() => { setActiveTab("master"); setMasterSubTab("warehouses"); }}
                    className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-[11px] font-medium transition ${
                      activeTab === "master" && masterSubTab === "warehouses" ? "bg-[#16B1FF]/10 text-[#16B1FF] font-bold" : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    <span>Master Gudang</span>
                    <span className="text-[10px] bg-slate-200/80 px-1.5 py-0.5 rounded text-slate-700 font-bold">{warehouses.length}</span>
                  </button>
                </div>
              )}
            </div>

            {/* E-SIGNATURE */}
            <button
              onClick={() => setActiveTab("esign")}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-semibold transition ${
                activeTab === "esign"
                  ? "bg-[#FFB400] text-white shadow-[0_4px_10px_rgba(255,180,0,0.35)] font-bold"
                  : "text-slate-600 hover:bg-[rgba(58,53,65,0.04)] hover:text-[#FFB400]"
              }`}
            >
              <div className="flex items-center space-x-3">
                <i className="fa-solid fa-file-signature text-sm w-4"></i>
                <span>e-Signature HOD</span>
              </div>
              <span className="text-[10px] bg-white/20 px-1.5 py-0.5 rounded font-mono">{esignDocs.length}</span>
            </button>

            <div className="pt-3 pb-1">
              <span className="px-3.5 text-[10px] uppercase font-bold tracking-wider text-slate-400">Shortcut Cepat</span>
            </div>

            <a
              href={process.env.NEXT_PUBLIC_STAFF_URL || "http://localhost:3001"}
              className="flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-bold bg-[#56CA00]/10 text-[#3F9700] hover:bg-[#56CA00]/20 transition"
            >
              <i className="fa-solid fa-mobile-screen-button text-sm w-4"></i>
              <span>Portal Staf (Port 3001)</span>
            </a>

            <Link
              href="/sales-brief"
              className="flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold text-[#16B1FF] hover:bg-sky-50 transition"
            >
              <i className="fa-brands fa-telegram text-sm w-4"></i>
              <span>Telegram Sales Brief</span>
            </Link>
          </nav>
        </div>

        {/* User Scope / Role Switcher */}
        <div className="p-4 border-t border-[rgba(58,53,65,0.08)] bg-[#F9FAFC]">
          <label className="block text-[10px] uppercase font-bold text-slate-500 mb-1.5 flex items-center justify-between">
            <span>Pilih Persona:</span>
            <span className="text-[#8C57FF] font-semibold">{isWarehousePersona ? '📦 Gudang' : '📈 Sales'}</span>
          </label>
          <select
            value={persona}
            onChange={(e) => setPersona(e.target.value)}
            className="w-full text-xs bg-white border border-[rgba(58,53,65,0.18)] text-[#3A3541] rounded-lg p-2 focus:ring-1 focus:ring-[#8C57FF] outline-none shadow-sm"
          >
            <optgroup label="--- PERSONA SALES (Manajerial & Lapangan) ---">
              <option value="muhammad.wyzer@gmail.com">Muhammad Wyzer (Head of Sales - Nasional)</option>
              <option value="budi.santoso@duakelinci.id">Budi Santoso (Field Salesman Jakarta)</option>
              <option value="eko.prasetyo@duakelinci.id">Eko Prasetyo (Field Salesman Surabaya)</option>
              <option value="hr.jabar@duakelinci.id">Dedi Kurniawan (Regional Sales Manager Jabar)</option>
            </optgroup>
            <optgroup label="--- PERSONA WAREHOUSE (Gudang & FEFO) ---">
              <option value="bambang.warehouse@duakelinci.id">Bambang Soeprapto (Head of Warehouse)</option>
              <option value="agus.wh.bdg@duakelinci.id">Agus Setiawan (Warehouse Manager Bandung)</option>
              <option value="surya.picker@duakelinci.id">Surya Saputra (FEFO Picking Lead Operator)</option>
            </optgroup>
          </select>
        </div>
      </aside>

      {/* 2. MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        
        {/* Top Header */}
        <header className="bg-white border-b border-[rgba(58,53,65,0.08)] px-6 py-3.5 flex items-center justify-between shadow-[0_2px_8px_rgba(58,53,65,0.04)] sticky top-0 z-10">
          <div>
            <h2 className="text-sm font-bold text-[#3A3541]">
              {activeTab === "dashboard" && "Dashboard Eksekutif & Visual Analytics"}
              {activeTab === "wms" && "Gudang (WMS Ringan) & Sinkronisasi ERP QAD"}
              {activeTab === "sales_route" && "Rute Sales Lapangan (Call Plan & GPS Geofencing)"}
              {activeTab === "iot" && "IoT Pabrik Pati - Live Shop Floor Monitoring & OEE"}
              {activeTab === "master" && "Master Data Management (MDM)"}
              {activeTab === "esign" && "Otorisasi Dokumen e-Signature HOD"}
            </h2>
            <p className="text-xs text-slate-400">PT Dua Kelinci &bull; Divisi {isWarehousePersona ? 'Logistik & Pergudangan' : 'Penjualan & Distribusi Nasional'}</p>
          </div>

          <div className="flex items-center space-x-3">
            <a
              href={process.env.NEXT_PUBLIC_STAFF_URL || "http://localhost:3001"}
              className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-bold bg-[#3A3541] text-white hover:bg-[#524B5C] transition shadow-sm"
            >
              <i className="fa-solid fa-users-gear mr-1.5"></i>
              Portal Staf
            </a>
            <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${isWarehousePersona ? 'bg-[#8C57FF]/10 text-[#8C57FF]' : 'bg-[#16B1FF]/10 text-[#16B1FF]'}`}>
              <i className={`fa-solid ${isWarehousePersona ? 'fa-box' : 'fa-briefcase'} mr-1.5`}></i>
              {isWarehousePersona ? 'Role: Pergudangan' : 'Role: Penjualan'}
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-[#56CA00]/10 text-[#56CA00]">
              <span className="w-2 h-2 mr-1.5 bg-[#56CA00] rounded-full animate-pulse"></span>
              Live Sync
            </span>
          </div>
        </header>

        {/* Tab Body */}
        <main className="p-6 space-y-6">

          {/* TAB 1: DASHBOARD */}
          {activeTab === "dashboard" && overview && (
            <div className="space-y-6">
              {/* Date Filter */}
              <div className="bg-white p-4 rounded-2xl border border-[rgba(58,53,65,0.08)] shadow-[0_4px_18px_rgba(58,53,65,0.06)] flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center space-x-3">
                  <div className="w-9 h-9 rounded-xl bg-[#8C57FF]/10 text-[#8C57FF] flex items-center justify-center text-sm font-bold">
                    <i className="fa-solid fa-calendar-days"></i>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block">Rentang Tanggal Analisis</span>
                    <span className="text-xs font-extrabold text-[#3A3541]">Periode: {startDate} s/d {endDate}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button onClick={() => { setStartDate("2026-09-01"); setEndDate("2026-10-31"); setPresetDate("all"); }} className={`px-3 py-1.5 rounded-md text-xs font-bold ${presetDate === "all" ? "bg-[#8C57FF] text-white" : "bg-slate-100 text-slate-700"}`}>Semua</button>
                  <button onClick={() => { setStartDate("2026-10-01"); setEndDate("2026-10-31"); setPresetDate("oct"); }} className={`px-3 py-1.5 rounded-md text-xs font-bold ${presetDate === "oct" ? "bg-[#8C57FF] text-white" : "bg-slate-100 text-slate-700"}`}>Okt 2026</button>
                  <label className="cursor-pointer bg-[#56CA00] hover:bg-[#4CB200] text-white text-xs font-bold px-3 py-1.5 rounded-md flex items-center space-x-1.5 shadow transition">
                    <i className="fa-solid fa-file-arrow-up"></i>
                    <span>Impor CSV Sales</span>
                    <input type="file" accept=".csv" onChange={handleImportSalesCsv} className="hidden" />
                  </label>
                </div>
              </div>

              {/* KPI Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                <div className="bg-white p-5 rounded-2xl border border-[rgba(58,53,65,0.08)] shadow-[0_4px_18px_rgba(58,53,65,0.08)]">
                  <span className="text-xs font-medium text-slate-500">Net Sales</span>
                  <div className="text-2xl font-black text-[#3A3541] mt-2">Rp {(overview.net_sales_idr / 1e9).toFixed(2)} M</div>
                  <div className="text-xs text-[#56CA00] mt-1 font-semibold">Target Achieved: {overview.achievement_pct}%</div>
                </div>
                <div className="bg-white p-5 rounded-2xl border border-[rgba(58,53,65,0.08)] shadow-[0_4px_18px_rgba(58,53,65,0.08)]">
                  <span className="text-xs font-medium text-slate-500">Volume Terjual</span>
                  <div className="text-2xl font-black text-[#3A3541] mt-2">{Number(overview.qty_carton).toLocaleString('id-ID')} Karton</div>
                  <div className="text-xs text-slate-400 mt-1">Faktur: {overview.total_invoices} Transaksi</div>
                </div>
                <div className="bg-white p-5 rounded-2xl border border-[rgba(58,53,65,0.08)] shadow-[0_4px_18px_rgba(58,53,65,0.08)]">
                  <span className="text-xs font-medium text-slate-500">Diskon Promosi</span>
                  <div className="text-2xl font-black text-[#FFB400] mt-2">Rp {(overview.discount_idr / 1e6).toFixed(1)} Jt</div>
                  <div className="text-xs text-slate-400 mt-1">Rasio Diskon: {overview.discount_pct}%</div>
                </div>
                <div className="bg-white p-5 rounded-2xl border border-[rgba(58,53,65,0.08)] shadow-[0_4px_18px_rgba(58,53,65,0.08)]">
                  <span className="text-xs font-medium text-slate-500">Stok Kritis Gudang (FEFO)</span>
                  <div className="text-2xl font-black text-[#FF4C51] mt-2">{overview.critical_stock_count} Batch</div>
                  <div className="text-xs text-[#FF4C51] mt-1 font-semibold">Perlu Alokasi Segera</div>
                </div>
              </div>

              {/* Visual Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-white p-5 rounded-2xl border border-[rgba(58,53,65,0.08)] shadow-[0_4px_18px_rgba(58,53,65,0.08)]">
                  <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center space-x-2">
                    <i className="fa-solid fa-chart-simple text-[#8C57FF]"></i>
                    <span>Trend Penjualan Harian</span>
                  </h3>
                  <div className="h-52 flex items-end gap-1.5 px-2 pb-2 border-b border-slate-200 overflow-x-auto">
                    {dailyTrends.slice(-25).map((t, idx) => {
                      const heightPct = Math.max(12, Math.round((t.net_sales_idr / maxTrendSales) * 100));
                      return (
                        <div key={idx} className="flex-1 min-w-[14px] flex flex-col items-center group relative cursor-pointer">
                          <div style={{ height: `${heightPct}%` }} className="w-full bg-gradient-to-t from-[#8C57FF] to-[#A379FF] rounded-t group-hover:from-[#7335FF] group-hover:to-[#8C57FF] transition-all"></div>
                          <span className="text-[9px] text-slate-400 mt-1 font-mono">{t.date ? t.date.slice(8, 10) : ''}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="bg-white p-5 rounded-2xl border border-[rgba(58,53,65,0.08)] shadow-[0_4px_18px_rgba(58,53,65,0.08)]">
                  <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center space-x-2">
                    <i className="fa-solid fa-chart-pie text-[#56CA00]"></i>
                    <span>Brand Market Share</span>
                  </h3>
                  <div className="space-y-3">
                    {brandBreakdown.slice(0, 5).map((b, idx) => {
                      const pct = Math.round((b.net_sales_idr / totalBrandSales) * 100);
                      const colors = ["#8C57FF", "#56CA00", "#FFB400", "#16B1FF", "#FF4C51"];
                      return (
                        <div key={idx} className="space-y-1 text-xs">
                          <div className="flex justify-between font-bold">
                            <span>{b.name}</span>
                            <span>{pct}%</span>
                          </div>
                          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                            <div style={{ width: `${pct}%`, backgroundColor: colors[idx % colors.length] }} className="h-full rounded-full"></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: FITUR 2 - GUDANG (WMS RINGAN) */}
          {activeTab === "wms" && (
            <div className="bg-white p-6 rounded-2xl border border-[rgba(58,53,65,0.08)] shadow-[0_4px_18px_rgba(58,53,65,0.08)] space-y-4">
              <div className="flex flex-wrap items-center justify-between pb-3 border-b border-slate-200 gap-3">
                <div>
                  <h2 className="text-base font-bold text-slate-900 flex items-center">
                    <i className="fa-solid fa-boxes-stacked text-[#56CA00] mr-2"></i>
                    Gudang (WMS Ringan) &amp; Sinkronisasi ERP QAD
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Pengelolaan Inbound, Outbound FEFO, Stock Opname, Scan Barcode, dan rekonsiliasi data ke ERP QAD.
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setInboundModal(true)}
                    className="bg-[#56CA00] hover:bg-[#4CB200] text-white text-xs font-bold px-3.5 py-2 rounded-lg flex items-center space-x-1.5 shadow"
                  >
                    <i className="fa-solid fa-dolly"></i>
                    <span>Penerimaan (Inbound)</span>
                  </button>
                  <button
                    onClick={handleTriggerQadSync}
                    className="bg-[#8C57FF] hover:bg-[#7E4EE6] text-white text-xs font-bold px-3.5 py-2 rounded-lg flex items-center space-x-1.5 shadow"
                  >
                    <i className="fa-solid fa-arrows-rotate"></i>
                    <span>Sinkron ke ERP QAD</span>
                  </button>
                </div>
              </div>

              {/* Sub Navigation Bar */}
              <div className="flex border-b border-slate-200 text-xs font-bold space-x-4">
                <button
                  onClick={() => setWmsSubTab("transactions")}
                  className={`pb-2 border-b-2 transition ${wmsSubTab === "transactions" ? "border-[#56CA00] text-[#56CA00]" : "border-transparent text-slate-500 hover:text-slate-800"}`}
                >
                  Transaksi Inventory ({wmsTransactions.length})
                </button>
                <button
                  onClick={() => setWmsSubTab("opname")}
                  className={`pb-2 border-b-2 transition ${wmsSubTab === "opname" ? "border-[#56CA00] text-[#56CA00]" : "border-transparent text-slate-500 hover:text-slate-800"}`}
                >
                  Stock Opname Fisik ({opnameSessions.length})
                </button>
                <button
                  onClick={() => setWmsSubTab("barcode")}
                  className={`pb-2 border-b-2 transition ${wmsSubTab === "barcode" ? "border-[#56CA00] text-[#56CA00]" : "border-transparent text-slate-500 hover:text-slate-800"}`}
                >
                  Scan Barcode EAN-13
                </button>
                <button
                  onClick={() => setWmsSubTab("fefo")}
                  className={`pb-2 border-b-2 transition ${wmsSubTab === "fefo" ? "border-[#56CA00] text-[#56CA00]" : "border-transparent text-slate-500 hover:text-slate-800"}`}
                >
                  Uji Alokasi FEFO Picking
                </button>
              </div>

              {/* View 1: Transactions Table */}
              {wmsSubTab === "transactions" && (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
                    <thead className="bg-slate-50 text-slate-600 font-bold uppercase">
                      <tr>
                        <th className="py-2.5 px-3">No. Transaksi</th>
                        <th className="py-2.5 px-3">Tipe</th>
                        <th className="py-2.5 px-3">Gudang</th>
                        <th className="py-2.5 px-3">SKU &amp; Batch</th>
                        <th className="py-2.5 px-3 text-right">Kuantitas</th>
                        <th className="py-2.5 px-3">Dokumen Ref</th>
                        <th className="py-2.5 px-3 text-center">Status QAD</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {wmsTransactions.map((tx) => (
                        <tr key={tx.id} className="hover:bg-slate-50 transition">
                          <td className="py-2.5 px-3 font-mono font-bold text-slate-900">{tx.transaction_no}</td>
                          <td className="py-2.5 px-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              tx.transaction_type === 'INBOUND' ? 'bg-emerald-100 text-emerald-800' :
                              tx.transaction_type === 'OUTBOUND' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
                            }`}>
                              {tx.transaction_type}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 font-bold">{tx.warehouse_id}</td>
                          <td className="py-2.5 px-3">
                            <span className="font-bold text-slate-900 block">{tx.sku_name}</span>
                            <span className="text-[10px] text-slate-400 font-mono">Batch: {tx.batch_no} &bull; Exp: {tx.expiry_date}</span>
                          </td>
                          <td className="py-2.5 px-3 text-right font-black text-slate-900">{tx.qty_carton} ctn</td>
                          <td className="py-2.5 px-3 font-mono text-slate-500">{tx.reference_doc_no || "-"}</td>
                          <td className="py-2.5 px-3 text-center">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              tx.qad_sync_status === 'SYNCED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800 animate-pulse'
                            }`}>
                              {tx.qad_sync_status}
                            </span>
                            {tx.qad_voucher_no && (
                              <span className="block text-[9px] text-slate-400 font-mono mt-0.5">{tx.qad_voucher_no}</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* View 2: Stock Opname */}
              {wmsSubTab === "opname" && (
                <div className="space-y-4">
                  {opnameSessions.map((s) => (
                    <div key={s.id} className="border border-slate-200 rounded-xl p-4 bg-slate-50/50 space-y-3">
                      <div className="flex justify-between items-center pb-2 border-b border-slate-200">
                        <div>
                          <span className="font-mono font-bold text-slate-900 text-sm mr-2">{s.session_no}</span>
                          <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded font-bold">{s.warehouse_id}</span>
                          <p className="text-xs text-slate-500 mt-0.5">{s.notes} &bull; Dibuat: {s.created_by}</p>
                        </div>
                        <span className="bg-amber-100 text-amber-800 text-xs font-bold px-2.5 py-1 rounded-md">{s.status}</span>
                      </div>
                      <table className="min-w-full text-xs text-left">
                        <thead className="text-slate-400 uppercase font-semibold">
                          <tr>
                            <th>SKU &amp; Batch</th>
                            <th className="text-right">Stok Sistem</th>
                            <th className="text-right">Hitung Fisik</th>
                            <th className="text-right">Selisih (Variance)</th>
                            <th className="text-center">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200">
                          {(s.items || []).map((it: any) => (
                            <tr key={it.id}>
                              <td className="py-2 font-bold text-slate-800">{it.sku_name} ({it.batch_no})</td>
                              <td className="py-2 text-right font-mono">{it.system_qty_carton} ctn</td>
                              <td className="py-2 text-right font-mono font-bold text-slate-900">{it.physical_qty_carton} ctn</td>
                              <td className={`py-2 text-right font-mono font-bold ${it.variance_carton < 0 ? "text-red-600" : it.variance_carton > 0 ? "text-emerald-600" : "text-slate-400"}`}>
                                {it.variance_carton > 0 ? `+${it.variance_carton}` : it.variance_carton} ctn
                              </td>
                              <td className="py-2 text-center">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${it.variance_carton === 0 ? "bg-emerald-100 text-emerald-800" : "bg-red-100 text-red-800"}`}>
                                  {it.variance_carton === 0 ? "Match" : "Variance"}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ))}
                </div>
              )}

              {/* View 3: Scan Barcode */}
              {wmsSubTab === "barcode" && (
                <div className="max-w-xl mx-auto p-4 border border-slate-200 rounded-xl space-y-3 bg-slate-50">
                  <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center">
                    <i className="fa-solid fa-barcode mr-2 text-[#56CA00]"></i>Simulator Barcode Reader EAN-13 / GS1-128
                  </h3>
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={barcodeQuery}
                      onChange={(e) => setBarcodeQuery(e.target.value)}
                      placeholder="Masukkan atau scan barcode EAN-13..."
                      className="flex-1 p-2 bg-white border border-slate-300 rounded-lg text-xs font-mono font-bold"
                    />
                    <button
                      onClick={handleBarcodeLookup}
                      className="bg-[#56CA00] hover:bg-[#4CB200] text-white px-4 py-2 rounded-lg text-xs font-bold"
                    >
                      Pindai (Scan)
                    </button>
                  </div>
                  {barcodeResult && barcodeResult.product && (
                    <div className="p-3 bg-white border border-emerald-200 rounded-lg text-xs space-y-1 mt-2">
                      <div className="font-bold text-slate-900 text-sm">{barcodeResult.product.sku_name}</div>
                      <div className="text-slate-500">Brand: <strong>{barcodeResult.product.brand}</strong> &bull; Kategori: {barcodeResult.product.category}</div>
                      <div className="text-slate-500">Isi Karton: {barcodeResult.product.pack_size} &bull; Masa Simpan: {barcodeResult.product.shelf_life_days} Hari</div>
                    </div>
                  )}
                </div>
              )}

              {/* View 4: FEFO Alokasi */}
              {wmsSubTab === "fefo" && (
                <div className="space-y-3">
                  <button onClick={handleCheckFEFO} className="bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold px-4 py-2 rounded-lg">
                    Jalankan Algoritma FEFO Picking (Sukro Pedas - WH-BDG)
                  </button>
                  {fefoResult && (
                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                      <div className="text-xs font-bold text-slate-800">Hasil Rekomendasi Batch Terdekat:</div>
                      {(fefoResult.fefo_allocations || []).map((a: any, i: number) => (
                        <div key={i} className="flex justify-between items-center text-xs p-2.5 bg-white rounded-lg border border-slate-200">
                          <span>Batch: <strong>{a.batch_no}</strong> &bull; Exp: <strong className="text-red-600">{a.expiry_date}</strong></span>
                          <span className="font-bold text-purple-700">Ambil: {a.allocated_qty} Karton</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: FITUR 4 - RUTE SALES LAPANGAN */}
          {activeTab === "sales_route" && salesRouteData && (
            <div className="bg-white p-6 rounded-2xl border border-[rgba(58,53,65,0.08)] shadow-[0_4px_18px_rgba(58,53,65,0.08)] space-y-6">
              <div className="flex flex-wrap items-center justify-between pb-3 border-b border-slate-200 gap-3">
                <div>
                  <h2 className="text-base font-bold text-slate-900 flex items-center">
                    <i className="fa-solid fa-route text-[#16B1FF] mr-2"></i>
                    Rencana Kunjungan Sales &amp; GPS Geofencing (Call Plan)
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Panduan rute terstruktur harian, validasi radius kehadiran fisik (&lt; 50m), dan Take Order (TO).
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs bg-slate-100 text-slate-700 px-3 py-1.5 rounded-lg font-semibold">
                    Salesman: <strong>{salesRouteData.salesman_email}</strong>
                  </span>
                </div>
              </div>

              {/* Route Performance Metrics Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                  <span className="text-xs text-slate-500 font-semibold">Target Toko Hari Ini</span>
                  <div className="text-2xl font-black text-slate-800 mt-1">{salesRouteData.total_targets} Toko</div>
                  <span className="text-[11px] text-slate-400">Telah dikunjungi: {salesRouteData.visited_count}</span>
                </div>
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                  <span className="text-xs text-slate-500 font-semibold">Effective Call (EC)</span>
                  <div className="text-2xl font-black text-emerald-600 mt-1">{salesRouteData.effective_calls} Transaksi</div>
                  <span className="text-[11px] text-emerald-600 font-bold">Kunjungan Berhasil Pesan</span>
                </div>
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                  <span className="text-xs text-slate-500 font-semibold">Strike Rate (%)</span>
                  <div className="text-2xl font-black text-[#16B1FF] mt-1">{salesRouteData.strike_rate_pct}%</div>
                  <span className="text-[11px] text-slate-400">Rasio Sukses Order</span>
                </div>
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                  <span className="text-xs text-slate-500 font-semibold">Total Nilai Pesanan (TO)</span>
                  <div className="text-2xl font-black text-slate-900 mt-1">Rp {(salesRouteData.total_to_amount_idr / 1e6).toFixed(1)} Jt</div>
                  <span className="text-[11px] text-slate-400">{salesRouteData.total_to_cartons} Karton</span>
                </div>
              </div>

              {/* Interactive Route Stop Sequence */}
              <div className="space-y-3">
                <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-400">Urutan Rute Outlet Harian</h3>
                <div className="space-y-2">
                  {(salesRouteData.route_stops || []).map((stop: any) => (
                    <div
                      key={stop.id}
                      className={`p-4 rounded-xl border flex flex-wrap items-center justify-between gap-3 transition ${
                        stop.status === 'CHECKED_IN' ? 'bg-amber-50/70 border-amber-300 shadow-sm' :
                        stop.status === 'VISITED' ? 'bg-emerald-50/50 border-emerald-200' : 'bg-white border-slate-200'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${
                          stop.status === 'VISITED' ? 'bg-emerald-600 text-white' :
                          stop.status === 'CHECKED_IN' ? 'bg-amber-500 text-white animate-pulse' : 'bg-slate-200 text-slate-700'
                        }`}>
                          {stop.sequence_order}
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-slate-900 text-sm">{stop.outlet_name}</span>
                            <span className="font-mono text-[10px] text-slate-400">{stop.outlet_id}</span>
                            {stop.is_mandatory && <span className="bg-red-100 text-red-700 text-[10px] px-1.5 py-0.2 rounded font-bold">Wajib</span>}
                          </div>
                          <p className="text-xs text-slate-500">{stop.outlet_address}</p>
                          <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                            Koordinat Target: {stop.target_lat}, {stop.target_lng}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        {stop.status === 'PLANNED' && (
                          <button
                            onClick={() => handleSalesCheckIn(stop)}
                            className="bg-[#16B1FF] hover:bg-[#139CE0] text-white text-xs font-bold px-3.5 py-2 rounded-lg flex items-center space-x-1.5 shadow"
                          >
                            <i className="fa-solid fa-location-crosshairs"></i>
                            <span>GPS Check-In</span>
                          </button>
                        )}
                        {stop.status === 'CHECKED_IN' && (
                          <button
                            onClick={() => {
                              setSelectedCallStop(stop);
                              setSalesCheckOutModal(true);
                            }}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold px-3.5 py-2 rounded-lg flex items-center space-x-1.5 shadow animate-bounce"
                          >
                            <i className="fa-solid fa-cart-shopping"></i>
                            <span>Input Take Order &amp; Check-Out</span>
                          </button>
                        )}
                        {stop.status === 'VISITED' && (
                          <span className="inline-flex items-center text-xs font-bold text-emerald-700 bg-emerald-100 px-3 py-1.5 rounded-lg">
                            <i className="fa-solid fa-check-circle mr-1.5"></i>Kunjungan Selesai
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: FITUR 5 - IOT PABRIK SHOP FLOOR (SESUAI PRD ADDENDUM 5.5) */}
          {activeTab === "iot" && iotStatus && (
            <div className="bg-white p-6 rounded-2xl border border-[rgba(58,53,65,0.08)] shadow-[0_4px_18px_rgba(58,53,65,0.08)] space-y-6">
              
              {/* Header */}
              <div className="flex flex-wrap items-center justify-between pb-3 border-b border-slate-200 gap-3">
                <div>
                  <h2 className="text-base font-bold text-slate-900 flex items-center">
                    <i className="fa-solid fa-industry text-[#FF4C51] mr-2"></i>
                    Industrial IoT &amp; Digital Factory Monitoring (Plant Pati)
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {iotStatus.plant_location} &bull; Sampling Telemetri Realtime &bull; Terakhir: {iotStatus.timestamp_wib}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs bg-slate-100 text-slate-700 px-3 py-1.5 rounded-lg font-bold">
                    Rata-Rata OEE: <span className="text-[#8C57FF]">{iotStatus.average_oee_pct}%</span>
                  </span>
                  <span className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-3 py-1.5 rounded-lg font-bold">
                    Perangkat Online: {iotStatus.online_devices_count} / {iotStatus.total_devices_count}
                  </span>
                  <button onClick={loadIotStatus} className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-3 py-1.5 rounded-lg font-bold">
                    <i className="fa-solid fa-rotate"></i>
                  </button>
                </div>
              </div>

              {/* IoT Sub Navigation Bar (PRD 5.5.H) */}
              <div className="flex border-b border-slate-200 text-xs font-bold space-x-4">
                <button
                  onClick={() => setIotSubTab("overview")}
                  className={`pb-2 border-b-2 transition ${iotSubTab === "overview" ? "border-[#FF4C51] text-[#FF4C51]" : "border-transparent text-slate-500 hover:text-slate-800"}`}
                >
                  Factory Overview
                </button>
                <button
                  onClick={() => setIotSubTab("machines")}
                  className={`pb-2 border-b-2 transition ${iotSubTab === "machines" ? "border-[#FF4C51] text-[#FF4C51]" : "border-transparent text-slate-500 hover:text-slate-800"}`}
                >
                  Machine Performance ({iotStatus.machines ? iotStatus.machines.length : 0})
                </button>
                <button
                  onClick={() => setIotSubTab("devices")}
                  className={`pb-2 border-b-2 transition ${iotSubTab === "devices" ? "border-[#FF4C51] text-[#FF4C51]" : "border-transparent text-slate-500 hover:text-slate-800"}`}
                >
                  Hardware &amp; Sensor Health ({deviceHealthList.length})
                </button>
                <button
                  onClick={() => setIotSubTab("oee_report")}
                  className={`pb-2 border-b-2 transition ${iotSubTab === "oee_report" ? "border-[#FF4C51] text-[#FF4C51]" : "border-transparent text-slate-500 hover:text-slate-800"}`}
                >
                  OEE &amp; Downtime Report
                </button>
              </div>

              {/* Active Threshold Alerts (PRD 5.5.F) */}
              {iotStatus.active_alerts && iotStatus.active_alerts.length > 0 && (
                <div className="space-y-2">
                  {iotStatus.active_alerts.map((al: any) => (
                    <div key={al.id} className="p-4 rounded-xl bg-red-50 border border-red-200 flex flex-wrap items-center justify-between text-xs text-red-900 shadow-sm gap-2">
                      <div className="flex items-center space-x-3">
                        <i className="fa-solid fa-triangle-exclamation text-xl text-red-600 animate-bounce"></i>
                        <div>
                          <div className="font-extrabold text-sm">{al.alert_type} ({al.severity}): {al.alert_message}</div>
                          <span className="text-[10px] text-red-700 font-mono">
                            Mesin: {al.machine_id} &bull; Sensor: {al.device_id || 'Chamber'} &bull; Nilai: {al.metric_value} (Ambang: {al.threshold_value}) &bull; Waktu: {al.triggered_at}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {!al.acknowledged_at ? (
                          <button
                            onClick={() => handleAcknowledgeAlert(al.alert_id || al.id)}
                            className="bg-amber-600 hover:bg-amber-700 text-white font-bold px-3 py-1.5 rounded-lg text-xs"
                          >
                            Konfirmasi (Acknowledge)
                          </button>
                        ) : (
                          <span className="text-[10px] bg-amber-100 text-amber-800 px-2 py-1 rounded font-bold">
                            Ack by: {al.acknowledged_by || 'Supervisor'}
                          </span>
                        )}
                        <button
                          onClick={() => handleResolveAlert(al.id)}
                          className="bg-red-600 hover:bg-red-700 text-white font-bold px-3 py-1.5 rounded-lg text-xs"
                        >
                          Tandai Selesai (Resolve)
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* VIEW 1: FACTORY OVERVIEW */}
              {iotSubTab === "overview" && (
                <div className="space-y-6">
                  {/* Summary Metric Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                      <span className="text-xs text-slate-500 font-semibold">Total Output Baik (Good Units)</span>
                      <div className="text-2xl font-black text-emerald-600 mt-1">{iotStatus.total_output_units.toLocaleString('id-ID')} Pcs</div>
                      <span className="text-[11px] text-slate-400">Shift Berjalan</span>
                    </div>
                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                      <span className="text-xs text-slate-500 font-semibold">Total Reject (QC Defect)</span>
                      <div className="text-2xl font-black text-red-600 mt-1">{iotStatus.total_reject_units.toLocaleString('id-ID')} Pcs</div>
                      <span className="text-[11px] text-red-500 font-bold">Reject Rate: {((iotStatus.total_reject_units / Math.max(iotStatus.total_output_units + iotStatus.total_reject_units, 1)) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                      <span className="text-xs text-slate-500 font-semibold">Kondisi Lini Produksi</span>
                      <div className="text-2xl font-black text-slate-800 mt-1">4 Lini Aktif</div>
                      <span className="text-[11px] text-slate-400">Pati Peanut &amp; Wafer Lines</span>
                    </div>
                    <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                      <span className="text-xs text-slate-500 font-semibold">Rata-Rata OEE Pabrik</span>
                      <div className="text-2xl font-black text-purple-700 mt-1">{iotStatus.average_oee_pct}%</div>
                      <span className="text-[11px] text-slate-400">Target Benchmark: 85.0%</span>
                    </div>
                  </div>

                  {/* Machine Live Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                    {(iotStatus.machines || []).map((m: any) => (
                      <div key={m.machine_id} className="p-5 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-xs font-bold text-slate-400">{m.machine_id}</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-black ${
                            m.machine_status === 'RUNNING' ? 'bg-emerald-100 text-emerald-800' :
                            m.machine_status === 'IDLE' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {m.machine_status || m.status}
                          </span>
                        </div>
                        <div>
                          <h4 className="font-bold text-slate-900 text-sm">{m.machine_name}</h4>
                          <p className="text-[11px] text-slate-400">{m.production_line}</p>
                        </div>
                        <div className="space-y-2 pt-2 border-t border-slate-100 text-xs">
                          <div className="flex justify-between items-center">
                            <span className="text-slate-500">Suhu Roasting / Fryer:</span>
                            <span className={`font-mono font-bold ${m.current_temp_celsius > (m.temperature_max || 185) ? "text-red-600" : "text-slate-900"}`}>
                              {m.current_temp_celsius}°C
                            </span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-slate-500">Kelembapan Ruang:</span>
                            <span className="font-mono font-bold text-slate-900">{m.current_humidity_rh}% RH</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-slate-500">Getaran (Vibration):</span>
                            <span className={`font-mono font-bold ${m.current_vibration_mms > (m.vibration_threshold || 4.5) ? "text-red-600" : "text-slate-900"}`}>
                              {m.current_vibration_mms || 2.1} mm/s
                            </span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-slate-500">Output Speed:</span>
                            <span className="font-mono font-bold text-emerald-600">{m.current_speed_ppm} / {m.ideal_speed_ppm} ppm</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* VIEW 2: MACHINE PERFORMANCE & SENSOR MAPPING (PRD 5.5.D) */}
              {iotSubTab === "machines" && (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
                    <thead className="bg-slate-50 text-slate-600 font-bold uppercase">
                      <tr>
                        <th className="py-2.5 px-3">ID Mesin</th>
                        <th className="py-2.5 px-3">Nama Mesin &amp; Lini</th>
                        <th className="py-2.5 px-3">Produk</th>
                        <th className="py-2.5 px-3 text-right">Ideal Speed</th>
                        <th className="py-2.5 px-3 text-right">Ambang Suhu</th>
                        <th className="py-2.5 px-3 text-right">Ambang RH</th>
                        <th className="py-2.5 px-3 text-right">Ambang Getaran</th>
                        <th className="py-2.5 px-3 text-center">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {(iotStatus.machines || []).map((m: any) => (
                        <tr key={m.machine_id} className="hover:bg-slate-50">
                          <td className="py-2.5 px-3 font-mono font-bold text-slate-500">{m.machine_id}</td>
                          <td className="py-2.5 px-3">
                            <span className="font-bold text-slate-900 block">{m.machine_name}</span>
                            <span className="text-[10px] text-slate-400">{m.production_line}</span>
                          </td>
                          <td className="py-2.5 px-3 font-semibold">{m.product_type}</td>
                          <td className="py-2.5 px-3 text-right font-mono font-bold">{m.ideal_speed_ppm} ppm</td>
                          <td className="py-2.5 px-3 text-right font-mono">{m.temperature_min}°C - {m.temperature_max}°C</td>
                          <td className="py-2.5 px-3 text-right font-mono">&le; {m.humidity_max}% RH</td>
                          <td className="py-2.5 px-3 text-right font-mono">&le; {m.vibration_threshold} mm/s</td>
                          <td className="py-2.5 px-3 text-center">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-black ${
                              m.machine_status === 'RUNNING' ? 'bg-emerald-100 text-emerald-800' :
                              m.machine_status === 'IDLE' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {m.machine_status || m.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* VIEW 3: HARDWARE & SENSOR HEALTH (PRD 5.5.B & 11.3.B) */}
              {iotSubTab === "devices" && (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
                    <thead className="bg-slate-50 text-slate-600 font-bold uppercase">
                      <tr>
                        <th className="py-2.5 px-3">Device ID</th>
                        <th className="py-2.5 px-3">Mesin Terpasang</th>
                        <th className="py-2.5 px-3">Tipe Device &amp; Sensor</th>
                        <th className="py-2.5 px-3">Protokol Komunikasi</th>
                        <th className="py-2.5 px-3">Titik Lokasi Instalasi</th>
                        <th className="py-2.5 px-3">Satuan</th>
                        <th className="py-2.5 px-3 text-center">Konektivitas</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {deviceHealthList.map((d: any) => (
                        <tr key={d.device_id} className="hover:bg-slate-50">
                          <td className="py-2.5 px-3 font-mono font-bold text-slate-900">{d.device_id}</td>
                          <td className="py-2.5 px-3">
                            <span className="font-bold text-slate-900 block">{d.machine_name}</span>
                            <span className="text-[10px] text-slate-400 font-mono">{d.machine_id}</span>
                          </td>
                          <td className="py-2.5 px-3">
                            <span className="font-bold text-slate-800 block">{d.sensor_type}</span>
                            <span className="text-[10px] text-slate-400">{d.device_type}</span>
                          </td>
                          <td className="py-2.5 px-3 font-mono font-semibold text-purple-700">{d.protocol}</td>
                          <td className="py-2.5 px-3">{d.installation_location}</td>
                          <td className="py-2.5 px-3 font-mono font-bold">{d.unit}</td>
                          <td className="py-2.5 px-3 text-center">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              d.connection_status === 'ONLINE' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800 animate-pulse'
                            }`}>
                              {d.connection_status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* VIEW 4: OEE & DOWNTIME REPORT (PRD 5.5.G & 5.5.H) */}
              {iotSubTab === "oee_report" && (
                <div className="space-y-4">
                  <div className="p-3 bg-purple-50 border border-purple-200 rounded-xl text-xs text-purple-900 flex justify-between items-center">
                    <div>
                      <strong>Formula OEE Standar Industri:</strong> Availability x Performance x Quality
                    </div>
                    <span className="font-mono text-purple-700 font-bold">Shift 1 &bull; 2026-10-31</span>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-slate-200 text-xs text-left">
                      <thead className="bg-slate-50 text-slate-600 font-bold uppercase">
                        <tr>
                          <th className="py-2.5 px-3">Lini Mesin Produksi</th>
                          <th className="py-2.5 px-3 text-right">Downtime (Menit)</th>
                          <th className="py-2.5 px-3 text-right">Availability (A)</th>
                          <th className="py-2.5 px-3 text-right">Performance (P)</th>
                          <th className="py-2.5 px-3 text-right">Quality (Q)</th>
                          <th className="py-2.5 px-3 text-right">Skor OEE</th>
                          <th className="py-2.5 px-3 text-right">Output Baik</th>
                          <th className="py-2.5 px-3 text-right">Reject</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 text-slate-700">
                        {(iotStatus.oee_records || []).map((o: any) => (
                          <tr key={o.id} className="hover:bg-slate-50">
                            <td className="py-2.5 px-3 font-bold text-slate-900">
                              {o.production_line}
                              <span className="block text-[10px] text-slate-400 font-normal">{o.machine_id}</span>
                            </td>
                            <td className="py-2.5 px-3 text-right font-mono text-red-600 font-bold">{o.downtime_minutes} min</td>
                            <td className="py-2.5 px-3 text-right font-mono">{o.availability_percentage || o.availability_pct}%</td>
                            <td className="py-2.5 px-3 text-right font-mono">{o.performance_percentage || o.performance_pct}%</td>
                            <td className="py-2.5 px-3 text-right font-mono">{o.quality_percentage || o.quality_pct}%</td>
                            <td className="py-2.5 px-3 text-right font-mono font-black text-purple-700 text-sm">
                              {o.oee_percentage || o.oee_pct}%
                            </td>
                            <td className="py-2.5 px-3 text-right font-mono font-bold text-emerald-700">
                              {(o.good_count || o.total_output_carton).toLocaleString('id-ID')}
                            </td>
                            <td className="py-2.5 px-3 text-right font-mono text-red-600">
                              {(o.reject_count || 50).toLocaleString('id-ID')}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

            </div>
          )}

          {/* TAB 5: MASTER DATA */}
          {activeTab === "master" && (
            <div className="bg-white p-6 rounded-2xl border border-[rgba(58,53,65,0.08)] shadow-[0_4px_18px_rgba(58,53,65,0.08)] space-y-5">
              
              {/* Header Action Toolbar */}
              <div className="flex flex-wrap items-center justify-between pb-4 border-b border-slate-200 gap-3">
                <div>
                  <h2 className="text-base font-bold text-slate-900 flex items-center">
                    <i className="fa-solid fa-database text-[#8C57FF] mr-2"></i>
                    Master Data: {
                      masterSubTab === "employees" ? "Karyawan & Personil" :
                      masterSubTab === "outlets" ? "Outlet & Toko Mitra" :
                      masterSubTab === "products" ? "SKU Produk & Harga" : "Gudang & Depo Cabang"
                    }
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Data Master terintegrasi dengan WMS, Rute Sales, dan Fact Tables. Total: {
                      masterSubTab === "employees" ? employees.length :
                      masterSubTab === "outlets" ? outlets.length :
                      masterSubTab === "products" ? products.length : warehouses.length
                    } entri terdaftar.
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  {/* TOMBOL IMPOR CSV */}
                  <label className="cursor-pointer bg-[#56CA00] hover:bg-[#4CB200] text-white text-xs font-bold px-3.5 py-2 rounded-lg flex items-center space-x-1.5 shadow transition">
                    <i className="fa-solid fa-file-csv"></i>
                    <span>Impor CSV {masterSubTab.toUpperCase()}</span>
                    <input
                      type="file"
                      accept=".csv"
                      onChange={(e) => handleImportCsv(masterSubTab, e)}
                      className="hidden"
                    />
                  </label>

                  {/* TOMBOL EKSPOR CSV */}
                  <button
                    onClick={() => handleExportCsv(masterSubTab)}
                    className="bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 text-xs font-bold px-3 py-2 rounded-lg flex items-center space-x-1.5 shadow-sm transition"
                  >
                    <i className="fa-solid fa-download text-slate-500"></i>
                    <span>Ekspor CSV</span>
                  </button>

                  {/* TOMBOL TAMBAH DATA */}
                  <button
                    onClick={() => {
                      const defaultData: any =
                        masterSubTab === "employees" ? { employee_id: `EMP-NEW-${Date.now().toString().slice(-4)}`, full_name: "", email: "", phone: "", department: "SALES", job_title: "", role_type: "STAFF", region: "Jawa Barat", branch: "Bandung", warehouse_id: "WH-BDG", status: "ACTIVE" } :
                        masterSubTab === "outlets" ? { outlet_id: `OUT-NEW-${Date.now().toString().slice(-4)}`, outlet_name: "", outlet_type: "Toko Kelontong", region: "Jawa Barat", branch: "Bandung", credit_limit_idr: 50000000, payment_term_days: 14, status: "ACTIVE" } :
                        masterSubTab === "products" ? { sku_id: `SKU-NEW-${Date.now().toString().slice(-4)}`, sku_name: "", brand: "Kacang Dua Kelinci", category: "Snack", carton_pack_qty: 24, price_het_idr: 120000, price_wholesale_idr: 105000, shelf_life_days: 365, status: "ACTIVE" } :
                        { warehouse_id: `WH-NEW-${Date.now().toString().slice(-4)}`, warehouse_name: "", region: "Jawa Barat", branch: "Bandung", capacity_carton: 15000, status: "ACTIVE" };
                      setEditingItem({ mode: "add", type: masterSubTab, data: defaultData });
                    }}
                    className="bg-[#8C57FF] hover:bg-[#7E4EE6] text-white text-xs font-bold px-3.5 py-2 rounded-lg flex items-center space-x-1.5 shadow transition"
                  >
                    <i className="fa-solid fa-plus"></i>
                    <span>Tambah Data</span>
                  </button>
                </div>
              </div>

              {/* TABEL MASTER: EMPLOYEES */}
              {masterSubTab === "employees" && (
                <div className="space-y-3">
                  {/* Filter Toolbar */}
                  <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <div className="flex items-center space-x-2 flex-1 max-w-sm">
                      <i className="fa-solid fa-magnifying-glass text-slate-400 text-xs"></i>
                      <input
                        type="text"
                        placeholder="Cari NIP, nama, email..."
                        value={empSearch}
                        onChange={(e) => setEmpSearch(e.target.value)}
                        className="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs outline-none focus:border-[#8C57FF]"
                      />
                    </div>
                    <div className="flex items-center space-x-2 text-xs">
                      <span className="text-slate-500 font-semibold">Departemen:</span>
                      <select
                        value={empDeptFilter}
                        onChange={(e) => setEmpDeptFilter(e.target.value)}
                        className="bg-white border border-slate-300 rounded-lg px-2 py-1.5 text-xs outline-none"
                      >
                        <option value="ALL">Semua Departemen</option>
                        <option value="SALES">SALES</option>
                        <option value="WAREHOUSE">WAREHOUSE</option>
                      </select>
                      <select
                        value={empRoleFilter}
                        onChange={(e) => setEmpRoleFilter(e.target.value)}
                        className="bg-white border border-slate-300 rounded-lg px-2 py-1.5 text-xs outline-none"
                      >
                        <option value="ALL">Semua Level</option>
                        <option value="MANAGER">MANAGER</option>
                        <option value="SUPERVISOR">SUPERVISOR</option>
                        <option value="STAFF">STAFF</option>
                      </select>
                    </div>
                  </div>

                  {/* Table */}
                  <div className="overflow-x-auto border border-slate-200 rounded-xl">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                        <tr>
                          <th className="py-2.5 px-3">NIP</th>
                          <th className="py-2.5 px-3">Nama Lengkap</th>
                          <th className="py-2.5 px-3">Kontak / Email</th>
                          <th className="py-2.5 px-3">Dept / Level</th>
                          <th className="py-2.5 px-3">Wilayah / Cabang</th>
                          <th className="py-2.5 px-3">Depo Gudang</th>
                          <th className="py-2.5 px-3 text-center">Aksi</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 font-medium">
                        {employees
                          .filter(e => {
                            const matchSearch = (e.full_name || "").toLowerCase().includes(empSearch.toLowerCase()) ||
                                                (e.employee_id || "").toLowerCase().includes(empSearch.toLowerCase()) ||
                                                (e.email || "").toLowerCase().includes(empSearch.toLowerCase());
                            const matchDept = empDeptFilter === "ALL" || e.department === empDeptFilter;
                            const matchRole = empRoleFilter === "ALL" || e.role_type === empRoleFilter;
                            return matchSearch && matchDept && matchRole;
                          })
                          .map((emp) => (
                            <tr key={emp.employee_id} className="hover:bg-slate-50/80 transition">
                              <td className="py-2.5 px-3 font-mono font-bold text-slate-800">{emp.employee_id}</td>
                              <td className="py-2.5 px-3 font-bold text-slate-900">{emp.full_name}</td>
                              <td className="py-2.5 px-3 text-slate-600">
                                <div>{emp.email}</div>
                                <div className="text-[10px] text-slate-400">{emp.phone}</div>
                              </td>
                              <td className="py-2.5 px-3">
                                <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${emp.department === 'SALES' ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'}`}>
                                  {emp.department}
                                </span>
                                <span className="ml-1 text-slate-500 font-semibold">{emp.job_title}</span>
                              </td>
                              <td className="py-2.5 px-3 text-slate-600">{emp.region} ({emp.branch})</td>
                              <td className="py-2.5 px-3 font-mono text-slate-700">{emp.warehouse_id || "-"}</td>
                              <td className="py-2.5 px-3 text-center space-x-1">
                                <button
                                  onClick={() => setEditingItem({ mode: "edit", type: "employees", data: { ...emp } })}
                                  className="p-1.5 text-blue-600 hover:bg-blue-50 rounded"
                                  title="Edit"
                                >
                                  <i className="fa-solid fa-pen-to-square"></i>
                                </button>
                                <button
                                  onClick={() => handleDeleteMasterItem("employees", emp.employee_id)}
                                  className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                                  title="Hapus"
                                >
                                  <i className="fa-solid fa-trash-can"></i>
                                </button>
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* TABEL MASTER: OUTLETS */}
              {masterSubTab === "outlets" && (
                <div className="space-y-3">
                  {/* Filter Toolbar */}
                  <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <div className="flex items-center space-x-2 flex-1 max-w-sm">
                      <i className="fa-solid fa-magnifying-glass text-slate-400 text-xs"></i>
                      <input
                        type="text"
                        placeholder="Cari ID, nama outlet, cabang..."
                        value={outletSearch}
                        onChange={(e) => setOutletSearch(e.target.value)}
                        className="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs outline-none focus:border-[#8C57FF]"
                      />
                    </div>
                    <div className="flex items-center space-x-2 text-xs">
                      <select
                        value={outletRegionFilter}
                        onChange={(e) => setOutletRegionFilter(e.target.value)}
                        className="bg-white border border-slate-300 rounded-lg px-2 py-1.5 text-xs outline-none"
                      >
                        <option value="ALL">Semua Wilayah</option>
                        <option value="Jawa Barat">Jawa Barat</option>
                        <option value="Jawa Tengah">Jawa Tengah</option>
                        <option value="Jawa Timur">Jawa Timur</option>
                        <option value="DKI Jakarta">DKI Jakarta</option>
                      </select>
                      <select
                        value={outletTypeFilter}
                        onChange={(e) => setOutletTypeFilter(e.target.value)}
                        className="bg-white border border-slate-300 rounded-lg px-2 py-1.5 text-xs outline-none"
                      >
                        <option value="ALL">Semua Tipe Outlet</option>
                        <option value="Grosir Besar">Grosir Besar</option>
                        <option value="Supermarket">Supermarket</option>
                        <option value="Toko Kelontong">Toko Kelontong</option>
                      </select>
                    </div>
                  </div>

                  {/* Table */}
                  <div className="overflow-x-auto border border-slate-200 rounded-xl">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                        <tr>
                          <th className="py-2.5 px-3">Kode Outlet</th>
                          <th className="py-2.5 px-3">Nama Toko / Outlet</th>
                          <th className="py-2.5 px-3">Tipe Saluran</th>
                          <th className="py-2.5 px-3">Wilayah / Cabang</th>
                          <th className="py-2.5 px-3 text-right">Plafon Kredit (IDR)</th>
                          <th className="py-2.5 px-3 text-center">TOP (Hari)</th>
                          <th className="py-2.5 px-3 text-center">Aksi</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 font-medium">
                        {outlets
                          .filter(o => {
                            const matchSearch = (o.outlet_name || "").toLowerCase().includes(outletSearch.toLowerCase()) ||
                                                (o.outlet_id || "").toLowerCase().includes(outletSearch.toLowerCase());
                            const matchRegion = outletRegionFilter === "ALL" || o.region === outletRegionFilter;
                            const matchType = outletTypeFilter === "ALL" || o.outlet_type === outletTypeFilter;
                            return matchSearch && matchRegion && matchType;
                          })
                          .map((o) => (
                            <tr key={o.outlet_id} className="hover:bg-slate-50/80 transition">
                              <td className="py-2.5 px-3 font-mono font-bold text-slate-800">{o.outlet_id}</td>
                              <td className="py-2.5 px-3 font-bold text-slate-900">{o.outlet_name}</td>
                              <td className="py-2.5 px-3">
                                <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-semibold text-[10px]">
                                  {o.outlet_type}
                                </span>
                              </td>
                              <td className="py-2.5 px-3 text-slate-600">{o.region} - {o.branch}</td>
                              <td className="py-2.5 px-3 text-right font-mono font-bold text-[#56CA00]">
                                Rp {Number(o.credit_limit_idr || 0).toLocaleString('id-ID')}
                              </td>
                              <td className="py-2.5 px-3 text-center font-mono">{o.payment_term_days} Hari</td>
                              <td className="py-2.5 px-3 text-center space-x-1">
                                <button
                                  onClick={() => setEditingItem({ mode: "edit", type: "outlets", data: { ...o } })}
                                  className="p-1.5 text-blue-600 hover:bg-blue-50 rounded"
                                  title="Edit"
                                >
                                  <i className="fa-solid fa-pen-to-square"></i>
                                </button>
                                <button
                                  onClick={() => handleDeleteMasterItem("outlets", o.outlet_id)}
                                  className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                                  title="Hapus"
                                >
                                  <i className="fa-solid fa-trash-can"></i>
                                </button>
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* TABEL MASTER: PRODUCTS */}
              {masterSubTab === "products" && (
                <div className="space-y-3">
                  {/* Filter Toolbar */}
                  <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <div className="flex items-center space-x-2 flex-1 max-w-sm">
                      <i className="fa-solid fa-magnifying-glass text-slate-400 text-xs"></i>
                      <input
                        type="text"
                        placeholder="Cari SKU, nama produk, brand..."
                        value={productSearch}
                        onChange={(e) => setProductSearch(e.target.value)}
                        className="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs outline-none focus:border-[#8C57FF]"
                      />
                    </div>
                    <div className="flex items-center space-x-2 text-xs">
                      <select
                        value={productBrandFilter}
                        onChange={(e) => setProductBrandFilter(e.target.value)}
                        className="bg-white border border-slate-300 rounded-lg px-2 py-1.5 text-xs outline-none"
                      >
                        <option value="ALL">Semua Brand</option>
                        <option value="Kacang Dua Kelinci">Kacang Dua Kelinci</option>
                        <option value="Sukro">Sukro</option>
                        <option value="Deka Wafer">Deka Wafer</option>
                        <option value="TicTac">TicTac</option>
                        <option value="Fuzo">Fuzo</option>
                      </select>
                    </div>
                  </div>

                  {/* Table */}
                  <div className="overflow-x-auto border border-slate-200 rounded-xl">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                        <tr>
                          <th className="py-2.5 px-3">Kode SKU</th>
                          <th className="py-2.5 px-3">Nama Produk</th>
                          <th className="py-2.5 px-3">Brand</th>
                          <th className="py-2.5 px-3 text-center">Isi / Karton</th>
                          <th className="py-2.5 px-3 text-right">Harga HET (IDR)</th>
                          <th className="py-2.5 px-3 text-right">Harga Grosir (IDR)</th>
                          <th className="py-2.5 px-3 text-center">Shelf Life</th>
                          <th className="py-2.5 px-3 text-center">Aksi</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 font-medium">
                        {products
                          .filter(p => {
                            const matchSearch = (p.sku_name || "").toLowerCase().includes(productSearch.toLowerCase()) ||
                                                (p.sku_id || "").toLowerCase().includes(productSearch.toLowerCase());
                            const matchBrand = productBrandFilter === "ALL" || p.brand === productBrandFilter;
                            return matchSearch && matchBrand;
                          })
                          .map((p) => (
                            <tr key={p.sku_id} className="hover:bg-slate-50/80 transition">
                              <td className="py-2.5 px-3 font-mono font-bold text-slate-800">{p.sku_id}</td>
                              <td className="py-2.5 px-3 font-bold text-slate-900">{p.sku_name}</td>
                              <td className="py-2.5 px-3">
                                <span className="bg-purple-50 text-[#8C57FF] px-2 py-0.5 rounded font-bold text-[10px]">
                                  {p.brand}
                                </span>
                              </td>
                              <td className="py-2.5 px-3 text-center font-mono">{p.carton_pack_qty} Pcs</td>
                              <td className="py-2.5 px-3 text-right font-mono">
                                Rp {Number(p.price_het_idr || 0).toLocaleString('id-ID')}
                              </td>
                              <td className="py-2.5 px-3 text-right font-mono font-bold text-emerald-600">
                                Rp {Number(p.price_wholesale_idr || 0).toLocaleString('id-ID')}
                              </td>
                              <td className="py-2.5 px-3 text-center font-mono">{p.shelf_life_days || 365} Hari</td>
                              <td className="py-2.5 px-3 text-center space-x-1">
                                <button
                                  onClick={() => setEditingItem({ mode: "edit", type: "products", data: { ...p } })}
                                  className="p-1.5 text-blue-600 hover:bg-blue-50 rounded"
                                  title="Edit"
                                >
                                  <i className="fa-solid fa-pen-to-square"></i>
                                </button>
                                <button
                                  onClick={() => handleDeleteMasterItem("products", p.sku_id)}
                                  className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                                  title="Hapus"
                                >
                                  <i className="fa-solid fa-trash-can"></i>
                                </button>
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* TABEL MASTER: WAREHOUSES */}
              {masterSubTab === "warehouses" && (
                <div className="space-y-3">
                  {/* Filter Toolbar */}
                  <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <div className="flex items-center space-x-2 flex-1 max-w-sm">
                      <i className="fa-solid fa-magnifying-glass text-slate-400 text-xs"></i>
                      <input
                        type="text"
                        placeholder="Cari kode gudang, nama depo..."
                        value={whSearch}
                        onChange={(e) => setWhSearch(e.target.value)}
                        className="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs outline-none focus:border-[#8C57FF]"
                      />
                    </div>
                    <div className="flex items-center space-x-2 text-xs">
                      <select
                        value={whRegionFilter}
                        onChange={(e) => setWhRegionFilter(e.target.value)}
                        className="bg-white border border-slate-300 rounded-lg px-2 py-1.5 text-xs outline-none"
                      >
                        <option value="ALL">Semua Wilayah</option>
                        <option value="Jawa Barat">Jawa Barat</option>
                        <option value="Jawa Tengah">Jawa Tengah</option>
                        <option value="Jawa Timur">Jawa Timur</option>
                      </select>
                    </div>
                  </div>

                  {/* Table */}
                  <div className="overflow-x-auto border border-slate-200 rounded-xl">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                        <tr>
                          <th className="py-2.5 px-3">Kode Gudang</th>
                          <th className="py-2.5 px-3">Nama Depo / Gudang</th>
                          <th className="py-2.5 px-3">Wilayah</th>
                          <th className="py-2.5 px-3">Cabang</th>
                          <th className="py-2.5 px-3 text-right">Kapasitas (Karton)</th>
                          <th className="py-2.5 px-3 text-center">Status</th>
                          <th className="py-2.5 px-3 text-center">Aksi</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 font-medium">
                        {warehouses
                          .filter(w => {
                            const matchSearch = (w.warehouse_name || "").toLowerCase().includes(whSearch.toLowerCase()) ||
                                                (w.warehouse_id || "").toLowerCase().includes(whSearch.toLowerCase());
                            const matchRegion = whRegionFilter === "ALL" || w.region === whRegionFilter;
                            return matchSearch && matchRegion;
                          })
                          .map((w) => (
                            <tr key={w.warehouse_id} className="hover:bg-slate-50/80 transition">
                              <td className="py-2.5 px-3 font-mono font-bold text-slate-800">{w.warehouse_id}</td>
                              <td className="py-2.5 px-3 font-bold text-slate-900">{w.warehouse_name}</td>
                              <td className="py-2.5 px-3 text-slate-600">{w.region}</td>
                              <td className="py-2.5 px-3 text-slate-600">{w.branch}</td>
                              <td className="py-2.5 px-3 text-right font-mono font-bold text-blue-600">
                                {Number(w.capacity_carton || 10000).toLocaleString('id-ID')} Karton
                              </td>
                              <td className="py-2.5 px-3 text-center">
                                <span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold text-[10px]">
                                  {w.status || "ACTIVE"}
                                </span>
                              </td>
                              <td className="py-2.5 px-3 text-center space-x-1">
                                <button
                                  onClick={() => setEditingItem({ mode: "edit", type: "warehouses", data: { ...w } })}
                                  className="p-1.5 text-blue-600 hover:bg-blue-50 rounded"
                                  title="Edit"
                                >
                                  <i className="fa-solid fa-pen-to-square"></i>
                                </button>
                                <button
                                  onClick={() => handleDeleteMasterItem("warehouses", w.warehouse_id)}
                                  className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                                  title="Hapus"
                                >
                                  <i className="fa-solid fa-trash-can"></i>
                                </button>
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

            </div>
          )}

          {/* TAB 6: E-SIGNATURE */}
          {activeTab === "esign" && (
            <div className="bg-white p-6 rounded-2xl border border-[rgba(58,53,65,0.08)] shadow-[0_4px_18px_rgba(58,53,65,0.08)] space-y-4">
              <h2 className="text-base font-bold text-slate-900">Otorisasi Dokumen e-Signature HOD ({esignDocs.length})</h2>
              <div className="space-y-3">
                {esignDocs.map((doc: any) => (
                  <div key={doc.id} className="p-4 border rounded-xl bg-slate-50/50 flex justify-between items-center text-xs">
                    <div>
                      <div className="font-bold text-slate-900">{doc.title}</div>
                      <div className="text-slate-400 font-mono">SHA-256: {doc.sha256_hash ? doc.sha256_hash.substring(0, 24) : "-"}...</div>
                    </div>
                    <span className="bg-blue-100 text-blue-800 font-bold px-2 py-0.5 rounded">{doc.status}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

        </main>
      </div>

      {/* MODAL INBOUND (WMS) */}
      {inboundModal && (
        <div className="fixed inset-0 bg-slate-950/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="font-bold text-slate-900 text-sm">Penerimaan Barang Gudang (Goods Receipt)</h3>
            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Gudang Penerima</label>
                <select
                  value={inboundForm.warehouse_id}
                  onChange={(e) => setInboundForm({ ...inboundForm, warehouse_id: e.target.value })}
                  className="w-full p-2 border rounded-lg font-bold"
                >
                  {warehouses.map(w => <option key={w.warehouse_id} value={w.warehouse_id}>{w.warehouse_id} - {w.warehouse_name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-slate-700 font-semibold mb-1">SKU Produk</label>
                <select
                  value={inboundForm.sku_name}
                  onChange={(e) => setInboundForm({ ...inboundForm, sku_name: e.target.value })}
                  className="w-full p-2 border rounded-lg font-bold"
                >
                  {products.map(p => <option key={p.sku_id} value={p.sku_name}>{p.sku_name}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Kuantitas (Karton)</label>
                  <input
                    type="number"
                    value={inboundForm.qty_carton}
                    onChange={(e) => setInboundForm({ ...inboundForm, qty_carton: parseInt(e.target.value) || 0 })}
                    className="w-full p-2 border rounded-lg font-bold"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Tanggal Expired</label>
                  <input
                    type="date"
                    value={inboundForm.expiry_date}
                    onChange={(e) => setInboundForm({ ...inboundForm, expiry_date: e.target.value })}
                    className="w-full p-2 border rounded-lg"
                  />
                </div>
              </div>
            </div>
            <div className="pt-3 border-t flex justify-end space-x-2">
              <button onClick={() => setInboundModal(false)} className="px-4 py-2 bg-slate-100 rounded-lg text-xs font-semibold">Batal</button>
              <button onClick={handleInboundSubmit} className="px-4 py-2 bg-[#56CA00] text-white rounded-lg text-xs font-bold">Simpan Penerimaan</button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL SALES CHECK-OUT & TAKE ORDER */}
      {salesCheckOutModal && (
        <div className="fixed inset-0 bg-slate-950/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="font-bold text-slate-900 text-sm">Formulir Selesai Kunjungan &amp; Take Order (TO)</h3>
            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Nilai Pesanan Penjualan (IDR)</label>
                <input
                  type="number"
                  value={checkOutForm.order_amount_idr}
                  onChange={(e) => setCheckOutForm({ ...checkOutForm, order_amount_idr: parseFloat(e.target.value) || 0 })}
                  className="w-full p-2 border rounded-lg font-bold text-slate-900"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Volume (Karton)</label>
                  <input
                    type="number"
                    value={checkOutForm.order_carton_qty}
                    onChange={(e) => setCheckOutForm({ ...checkOutForm, order_carton_qty: parseInt(e.target.value) || 0 })}
                    className="w-full p-2 border rounded-lg font-bold"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">Durasi Kunjungan (Menit)</label>
                  <input
                    type="number"
                    value={checkOutForm.duration_minutes}
                    onChange={(e) => setCheckOutForm({ ...checkOutForm, duration_minutes: parseInt(e.target.value) || 0 })}
                    className="w-full p-2 border rounded-lg"
                  />
                </div>
              </div>
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Catatan Hasil Kunjungan</label>
                <textarea
                  rows={2}
                  value={checkOutForm.notes}
                  onChange={(e) => setCheckOutForm({ ...checkOutForm, notes: e.target.value })}
                  className="w-full p-2 border rounded-lg text-slate-700"
                ></textarea>
              </div>
            </div>
            <div className="pt-3 border-t flex justify-end space-x-2">
              <button onClick={() => setSalesCheckOutModal(false)} className="px-4 py-2 bg-slate-100 rounded-lg text-xs font-semibold">Batal</button>
              <button onClick={handleSalesCheckOutSubmit} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-xs font-bold">Simpan Take Order</button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL EDIT / TAMBAH MASTER DATA */}
      {editingItem && (
        <div className="fixed inset-0 bg-slate-950/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 space-y-4">
            <h3 className="font-bold text-slate-900 text-sm flex items-center">
              <i className="fa-solid fa-pen-to-square text-[#8C57FF] mr-2"></i>
              <span>{editingItem.mode === "add" ? "Tambah Data Master" : "Edit Data Master"}: {editingItem.type.toUpperCase()}</span>
            </h3>

            <div className="space-y-3 text-xs max-h-[70vh] overflow-y-auto pr-1">
              {/* Form fields for Employees */}
              {editingItem.type === "employees" && (
                <>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">NIP / Employee ID</label>
                    <input
                      type="text"
                      disabled={editingItem.mode === "edit"}
                      value={editingItem.data.employee_id || ""}
                      onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, employee_id: e.target.value } })}
                      className="w-full p-2 border rounded-lg bg-slate-50 font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">Nama Lengkap</label>
                    <input
                      type="text"
                      value={editingItem.data.full_name || ""}
                      onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, full_name: e.target.value } })}
                      className="w-full p-2 border rounded-lg font-bold"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Email</label>
                      <input
                        type="email"
                        value={editingItem.data.email || ""}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, email: e.target.value } })}
                        className="w-full p-2 border rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">No Telepon</label>
                      <input
                        type="text"
                        value={editingItem.data.phone || ""}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, phone: e.target.value } })}
                        className="w-full p-2 border rounded-lg"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Departemen</label>
                      <select
                        value={editingItem.data.department || "SALES"}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, department: e.target.value } })}
                        className="w-full p-2 border rounded-lg"
                      >
                        <option value="SALES">SALES</option>
                        <option value="WAREHOUSE">WAREHOUSE</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Level / Role</label>
                      <select
                        value={editingItem.data.role_type || "STAFF"}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, role_type: e.target.value } })}
                        className="w-full p-2 border rounded-lg"
                      >
                        <option value="MANAGER">MANAGER</option>
                        <option value="SUPERVISOR">SUPERVISOR</option>
                        <option value="STAFF">STAFF</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">Jabatan (Job Title)</label>
                    <input
                      type="text"
                      value={editingItem.data.job_title || ""}
                      onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, job_title: e.target.value } })}
                      className="w-full p-2 border rounded-lg"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Wilayah</label>
                      <input
                        type="text"
                        value={editingItem.data.region || "Jawa Barat"}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, region: e.target.value } })}
                        className="w-full p-2 border rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Cabang</label>
                      <input
                        type="text"
                        value={editingItem.data.branch || "Bandung"}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, branch: e.target.value } })}
                        className="w-full p-2 border rounded-lg"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">Depo Gudang (Opsional)</label>
                    <input
                      type="text"
                      value={editingItem.data.warehouse_id || ""}
                      onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, warehouse_id: e.target.value } })}
                      className="w-full p-2 border rounded-lg font-mono"
                      placeholder="Contoh: WH-BDG"
                    />
                  </div>
                </>
              )}

              {/* Form fields for Outlets */}
              {editingItem.type === "outlets" && (
                <>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">Kode Outlet</label>
                    <input
                      type="text"
                      disabled={editingItem.mode === "edit"}
                      value={editingItem.data.outlet_id || ""}
                      onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, outlet_id: e.target.value } })}
                      className="w-full p-2 border rounded-lg bg-slate-50 font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">Nama Toko / Outlet</label>
                    <input
                      type="text"
                      value={editingItem.data.outlet_name || ""}
                      onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, outlet_name: e.target.value } })}
                      className="w-full p-2 border rounded-lg font-bold"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Tipe Saluran</label>
                      <select
                        value={editingItem.data.outlet_type || "Toko Kelontong"}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, outlet_type: e.target.value } })}
                        className="w-full p-2 border rounded-lg"
                      >
                        <option value="Grosir Besar">Grosir Besar</option>
                        <option value="Supermarket">Supermarket</option>
                        <option value="Toko Kelontong">Toko Kelontong</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">TOP (Hari)</label>
                      <input
                        type="number"
                        value={editingItem.data.payment_term_days || 14}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, payment_term_days: parseInt(e.target.value) || 0 } })}
                        className="w-full p-2 border rounded-lg font-mono"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">Plafon Kredit (IDR)</label>
                    <input
                      type="number"
                      value={editingItem.data.credit_limit_idr || 0}
                      onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, credit_limit_idr: parseFloat(e.target.value) || 0 } })}
                      className="w-full p-2 border rounded-lg font-bold text-emerald-600"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Wilayah</label>
                      <input
                        type="text"
                        value={editingItem.data.region || "Jawa Barat"}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, region: e.target.value } })}
                        className="w-full p-2 border rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Cabang</label>
                      <input
                        type="text"
                        value={editingItem.data.branch || "Bandung"}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, branch: e.target.value } })}
                        className="w-full p-2 border rounded-lg"
                      />
                    </div>
                  </div>
                </>
              )}

              {/* Form fields for Products */}
              {editingItem.type === "products" && (
                <>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">Kode SKU</label>
                    <input
                      type="text"
                      disabled={editingItem.mode === "edit"}
                      value={editingItem.data.sku_id || ""}
                      onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, sku_id: e.target.value } })}
                      className="w-full p-2 border rounded-lg bg-slate-50 font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">Nama Produk SKU</label>
                    <input
                      type="text"
                      value={editingItem.data.sku_name || ""}
                      onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, sku_name: e.target.value } })}
                      className="w-full p-2 border rounded-lg font-bold"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Brand</label>
                      <input
                        type="text"
                        value={editingItem.data.brand || "Kacang Dua Kelinci"}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, brand: e.target.value } })}
                        className="w-full p-2 border rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Isi per Karton</label>
                      <input
                        type="number"
                        value={editingItem.data.carton_pack_qty || 24}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, carton_pack_qty: parseInt(e.target.value) || 0 } })}
                        className="w-full p-2 border rounded-lg font-mono"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Harga HET (IDR)</label>
                      <input
                        type="number"
                        value={editingItem.data.price_het_idr || 0}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, price_het_idr: parseFloat(e.target.value) || 0 } })}
                        className="w-full p-2 border rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Harga Grosir (IDR)</label>
                      <input
                        type="number"
                        value={editingItem.data.price_wholesale_idr || 0}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, price_wholesale_idr: parseFloat(e.target.value) || 0 } })}
                        className="w-full p-2 border rounded-lg font-bold text-emerald-600"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">Shelf Life (Hari)</label>
                    <input
                      type="number"
                      value={editingItem.data.shelf_life_days || 365}
                      onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, shelf_life_days: parseInt(e.target.value) || 0 } })}
                      className="w-full p-2 border rounded-lg font-mono"
                    />
                  </div>
                </>
              )}

              {/* Form fields for Warehouses */}
              {editingItem.type === "warehouses" && (
                <>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">Kode Gudang</label>
                    <input
                      type="text"
                      disabled={editingItem.mode === "edit"}
                      value={editingItem.data.warehouse_id || ""}
                      onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, warehouse_id: e.target.value } })}
                      className="w-full p-2 border rounded-lg bg-slate-50 font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">Nama Depo / Gudang</label>
                    <input
                      type="text"
                      value={editingItem.data.warehouse_name || ""}
                      onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, warehouse_name: e.target.value } })}
                      className="w-full p-2 border rounded-lg font-bold"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Wilayah</label>
                      <input
                        type="text"
                        value={editingItem.data.region || "Jawa Barat"}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, region: e.target.value } })}
                        className="w-full p-2 border rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-semibold mb-1">Cabang</label>
                      <input
                        type="text"
                        value={editingItem.data.branch || "Bandung"}
                        onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, branch: e.target.value } })}
                        className="w-full p-2 border rounded-lg"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-slate-700 font-semibold mb-1">Kapasitas Maksimal (Karton)</label>
                    <input
                      type="number"
                      value={editingItem.data.capacity_carton || 15000}
                      onChange={(e) => setEditingItem({ ...editingItem, data: { ...editingItem.data, capacity_carton: parseInt(e.target.value) || 0 } })}
                      className="w-full p-2 border rounded-lg font-mono font-bold text-blue-600"
                    />
                  </div>
                </>
              )}
            </div>

            <div className="pt-3 border-t flex justify-end space-x-2">
              <button
                onClick={() => setEditingItem(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold"
              >
                Batal
              </button>
              <button
                onClick={handleSaveMasterItem}
                className="px-4 py-2 bg-[#8C57FF] hover:bg-[#7E4EE6] text-white rounded-lg text-xs font-bold shadow"
              >
                Simpan Perubahan
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
