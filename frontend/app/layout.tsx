import "./globals.css";

export const metadata = { title: "Calvin AI Resume Assistant", description: "基于真实职业资料的 AI 简历问答助手" };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="zh-CN"><body>{children}</body></html>; }
