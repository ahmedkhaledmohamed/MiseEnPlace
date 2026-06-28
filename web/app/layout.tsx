import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";

const geist = Geist({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MiseEnPlace — Cook Smarter with the Meal Graph",
  description:
    "A visual-first cooking app powered by an intelligent graph that connects meals through shared ingredients, techniques, and cuisines.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geist.className} h-full`}>
      <body className="h-full">{children}</body>
    </html>
  );
}
