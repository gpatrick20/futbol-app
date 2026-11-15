import type { HTMLAttributes } from "react";

import styles from "./Card.module.css";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export default function Card({
  children,
  className,
  ...props
}: CardProps) {
  return (
    <div
      {...props}
      className={[styles.card, className ?? ""].filter(Boolean).join(" ")}
    >
      {children}
    </div>
  );
}