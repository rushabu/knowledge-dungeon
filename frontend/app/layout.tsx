import type { Metadata } from "next";
import { IBM_Plex_Mono, Silkscreen } from "next/font/google";
import "./globals.css";

const body = IBM_Plex_Mono({ variable: "--font-body", weight: ["400", "500", "600"], subsets: ["latin"] });
const pixel = Silkscreen({ variable: "--font-pixel", weight: ["400", "700"], subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Knowledge Dungeon",
  description: "Turn your notes into a dungeon. Beat the bosses, remember everything.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${body.variable} ${pixel.variable}`}>
      <body>{children}</body>
    </html>
  );
}
