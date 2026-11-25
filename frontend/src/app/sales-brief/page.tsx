"use client";

import React, { useState } from "react";
import Link from "next/link";
import { API_BASE } from "../../lib/api";

export default function SalesBriefPage() {
  const [copied, setCopied] = useState(false);
  const [botToken, setBotToken] = useState("");
  const [chatId, setChatId] = useState("@mwyzer");
  const [statusMsg, setStatusMsg] = useState<{ success: boolean; text: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const telegramText = `Kepada Yth. @mwyzer (Head of Sales PT Dua Kelinci),

📊 Ringkasan Eksekutif Kinerja Penjualan (Sep–Okt 2026): Total realisasi penjualan bersih tercatat mencapai Rp 1,73 Miliar (8.745 karton) dari 42 outlet aktif nasional. Wilayah Jabodetabek memimpin sebagai kontributor tertinggi senilai Rp 495,8 Juta (28,7%) disusul Sumatera dan Jawa Barat, didorong dominasi brand Kacang Dua Kelinci sebesar Rp 739,8 Juta (42,9%) diikuti Tos Tos dan Sukro. Namun demikian, perhatian mendesak dan arahan Bapak @mwyzer diperlukan untuk mengintervensi 5 outlet dengan penjualan terlemah—khususnya Warung Maju Lancar (Malang, Jatim: Rp 1,1 Jt), Warung Sumber Makmur (Banjarmasin: Rp 7,0 Jt), Toko Mekar (Banjarmasin: Rp 7,6 Jt), Warung Murah Meriah (Cirebon: Rp 8,1 Jt), dan Minimarket Berkah (Bandung: Rp 9,0 Jt)—agar tim sales lapangan segera melakukan audit rute kunjungan, penambahan stok display SKU favorit, serta evaluasi batas kredit toko.`;

  const copyText = () => {
    navigator.clipboard.writeText(telegramText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const shareTelegram = () => {
    window.open(`https://t.me/share/url?url=${encodeURIComponent('https://duakelinci.id')}&text=${encodeURIComponent(telegramText)}`, '_blank');
  };

  const sendBot = async () => {
    if (!botToken || !chatId) {
      alert("Masukkan Bot Token dan Chat ID.");
      return;
    }
    setLoading(true);
    setStatusMsg(null);
    try {
      const res = await fetch(`${API_BASE}/telegram/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bot_token: botToken, chat_id: chatId, text: telegramText })
      });
      const data = await res.json();
      if (data.success) {
        setStatusMsg({ success: true, text: `Pesan sukses terkirim ke Telegram ID: ${chatId}` });
      } else {
        setStatusMsg({ success: false, text: data.error || "Gagal mengirim pesan bot." });
      }
    } catch (e: any) {
      setStatusMsg({ success: false, text: "Koneksi Error: " + e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <header className="bg-white border-b border-slate-200 px-4 h-16 flex items-center justify-between shadow-sm">
        <div className="flex items-center space-x-3">
          <Link href="/" className="w-10 h-10 rounded-xl bg-red-600 flex items-center justify-center text-white font-black text-xl shadow-md">
            2K
          </Link>
          <div>
            <h1 className="text-base sm:text-lg font-bold text-slate-900 leading-tight">
              Sales Analytics &amp; Telegram Executive Brief (Next.js)
            </h1>
            <p className="text-xs text-slate-500">PT Dua Kelinci &bull; Sep–Okt 2026</p>
          </div>
        </div>
        <Link href="/" className="text-xs font-semibold text-slate-600 hover:text-red-600">
          &larr; Kembali ke Dashboard
        </Link>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        {/* Telegram Card */}
        <div className="bg-gradient-to-r from-sky-900 to-slate-900 text-white rounded-2xl p-6 shadow-md border border-sky-800 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold flex items-center">
                <i className="fa-brands fa-telegram mr-2 text-sky-400 text-xl"></i>
                Ringkasan Eksekutif Telegram (Target: <span className="text-sky-300 ml-1 font-mono">@mwyzer</span>)
              </h2>
              <p className="text-xs text-sky-200">Format pesan ringkas satu paragraf siap pakai</p>
            </div>
            <div className="flex items-center space-x-2">
              <a href="https://t.me/mwyzer" target="_blank" className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3 py-2 rounded-lg">
                Buka Chat @mwyzer
              </a>
              <button onClick={shareTelegram} className="bg-sky-500 hover:bg-sky-400 text-white text-xs font-bold px-3 py-2 rounded-lg">
                Kirim via Telegram
              </button>
              <button onClick={copyText} className="bg-slate-700 hover:bg-slate-600 text-white text-xs font-bold px-3 py-2 rounded-lg">
                {copied ? "Tersalin!" : "Salin Teks"}
              </button>
            </div>
          </div>

          <div className="bg-slate-950/70 p-4 rounded-xl border border-sky-700/50 text-xs sm:text-sm leading-relaxed text-sky-50 whitespace-pre-line">
            {telegramText}
          </div>

          {/* BotFather Form */}
          <div className="bg-slate-900/90 p-4 rounded-xl border border-sky-800 text-xs space-y-3">
            <span className="font-bold text-sky-300 flex items-center">
              <i className="fa-solid fa-robot mr-1.5 text-sky-400"></i>Kirim Otomatis Menggunakan BotFather API
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-400 text-[11px] mb-1">Bot Token:</label>
                <input
                  type="password"
                  value={botToken}
                  onChange={(e) => setBotToken(e.target.value)}
                  placeholder="Token dari @BotFather"
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-100 font-mono text-xs focus:outline-none focus:border-sky-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 text-[11px] mb-1">Chat ID / Username:</label>
                <input
                  type="text"
                  value={chatId}
                  onChange={(e) => setChatId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-100 font-mono text-xs focus:outline-none focus:border-sky-500"
                />
              </div>
            </div>
            <div className="flex justify-end pt-1">
              <button
                onClick={sendBot}
                disabled={loading}
                className="bg-sky-600 hover:bg-sky-500 text-white font-bold px-4 py-1.5 rounded-lg text-xs"
              >
                {loading ? "Mengirim..." : "Kirim via Bot Sekarang"}
              </button>
            </div>
            {statusMsg && (
              <div className={`p-2.5 rounded-lg text-xs ${statusMsg.success ? "bg-emerald-950 text-emerald-200 border border-emerald-600" : "bg-red-950 text-red-200 border border-red-600"}`}>
                {statusMsg.text}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
