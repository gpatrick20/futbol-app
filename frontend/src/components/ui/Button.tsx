import type { ButtonHTMLAttributes } from "react";


import styles from "./Button.module.css";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
  fullWidth?: boolean;
  loading?: boolean;
  loadingText?: string;
}

export default function Button({
  children,
  variant = "primary",
  fullWidth = false,
  loading = false,
  loadingText = "Procesando...",
  disabled = false,
  type = "button",
  className,
  ...props
}: ButtonProps) {
  const classes = [
    styles.button,
    styles[variant],
    fullWidth ? styles.fullWidth : "",
    className ?? "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button
      {...props}
      type={type}
      className={classes}
      disabled={disabled || loading}
      aria-busy={loading}
    >
      {loading && (
        <span className={styles.spinner} aria-hidden="true" />
      )}

      <span>{loading ? loadingText : children}</span>
    </button>
  );
}