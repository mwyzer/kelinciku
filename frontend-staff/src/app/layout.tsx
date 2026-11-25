import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Portal Staf Operasional — PT Dua Kelinci",
  description: "Mobile-first portal untuk Sales Lapangan, Operator Gudang (WMS), dan Teknisi IoT Pabrik",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id">
      <head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
        />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
        />
      </head>
      <body className="min-h-screen bg-[#F4F5FA] text-[#3A3541] antialiased">
        {children}
      </body>
    </html>
  );
}
