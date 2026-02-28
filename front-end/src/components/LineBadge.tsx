import { getLineColor, getLineDisplayName } from "../utils/lineColors";

interface Props {
  line: string;
  size?: "sm" | "md";
}

export default function LineBadge({ line, size = "sm" }: Props) {
  const sizeClasses = size === "sm" ? "text-[10px] px-1.5 py-0.5" : "text-xs px-2 py-1";
  return (
    <span
      className={`inline-block rounded-full font-semibold text-white ${sizeClasses}`}
      style={{ backgroundColor: getLineColor(line) }}
    >
      {getLineDisplayName(line)}
    </span>
  );
}
