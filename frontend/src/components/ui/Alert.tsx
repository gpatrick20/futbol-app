import type { ReactNode } from "react";

import styles from "./Alert.module.css";

interface AlertProps {
  children: ReactNode;
  variant?: "error" | "success";
}

export default function Alert({
  children,
  variant = "error",
}: AlertProps) {
  return (
    <p
      className={[styles.alert, styles[variant]].join(" ")}
      role={variant === "error" ? "alert" : "status"}
    >
      {children}
    </p>
  );
}