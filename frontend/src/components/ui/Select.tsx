import type { SelectHTMLAttributes } from "react";

import styles from "./Select.module.css";

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  id: string;
  label: string;
  options: readonly SelectOption[];
  hint?: string;
  error?: string;
}

export default function Select({
  id,
  label,
  options,
  hint,
  error,
  className,
  "aria-describedby": ariaDescribedBy,
  ...props
}: SelectProps) {
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;

  const describedBy =
    [ariaDescribedBy, hintId, errorId].filter(Boolean).join(" ") ||
    undefined;

  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={id}>
        {label}
      </label>

      <select
        {...props}
        id={id}
        className={[
          styles.select,
          error ? styles.invalid : "",
          className ?? "",
        ]
          .filter(Boolean)
          .join(" ")}
        aria-invalid={error ? true : props["aria-invalid"]}
        aria-describedby={describedBy}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

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