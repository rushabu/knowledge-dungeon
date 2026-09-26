import type { ReactNode } from "react";

/** A little desktop window: striped title bar, square buttons, hard drop shadow. */
export default function RetroWindow({ title, extra, onClose, className = "", bodyClassName = "", children }: {
  title: ReactNode;
  extra?: ReactNode;
  onClose?: () => void;
  className?: string;
  bodyClassName?: string;
  children: ReactNode;
}) {
  return (
    <section className={`win ${className}`}>
      <header className="win-bar">
        {onClose ? (
          <button className="win-box close" onClick={onClose} aria-label="Close" />
        ) : (
          <span className="win-box" aria-hidden />
        )}
        <span className="win-stripes" aria-hidden />
        <span className="win-title">{title}</span>
        <span className="win-stripes" aria-hidden />
        {extra}
        <span className="win-box min" aria-hidden />
      </header>
      <div className={`win-body ${bodyClassName}`}>{children}</div>
    </section>
  );
}
