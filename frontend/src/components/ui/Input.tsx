import type { InputHTMLAttributes } from "react";

import styles from "./Input.module.css";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  id: string;
  label: string;
  hint?: string;
  error?: string;
}

export default function Input({
  id,
  label,
  hint,
  error,
  className,
  "aria-describedby": ariaDescribedBy,
  ...props
}: InputProps) {
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;

  const describedBy = [ariaDescribedBy, hintId, errorId]
    .filter(Boolean)
    .join(" ") || undefined;

  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={id}>
        {label}
      </label>

      <input
        {...props}
        id={id}
        className={[
          styles.input,
          error ? styles.invalid : "",
          className ?? "",
        ]
          .filter(Boolean)
          .join(" ")}
        aria-invalid={error ? true : props["aria-invalid"]}
        aria-describedby={describedBy}
      />

      {hint && (
        <p id={hintId} className={styles.hint}>
          {hint}
        </p>
      )}

      {error && (
        <p id={errorId} className={styles.error} role="alert">
          {error}
        </p>
      )}
    </div>
  );
}