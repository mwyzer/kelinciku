import type { Metadata } from "next";
import "./globals.css";
import ThemeRegistry from "../theme/ThemeRegistry";

export const metadata: Metadata = {
  title: "Portal Operasional Terpadu — PT Dua Kelinci (Materio Admin)",
  description: "Next.js Materio MUI Executive Dashboard, AI Agent, WMS FEFO & e-Signature",
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
        <ThemeRegistry>
          {children}
        </ThemeRegistry>
      </body>
    </html>
  );
}
