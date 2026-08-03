import { useTypewriter } from "../hooks/useTypewriter";
import { FormattedText } from "./FormattedText";

interface TypewriterFormattedTextProps {
  text: string;
  speed?: number;
  startDelay?: number;
  className?: string;
  showCursor?: boolean;
}

export function TypewriterFormattedText({
  text,
  speed = 18,
  startDelay = 300,
  className = "",
  showCursor = true,
}: TypewriterFormattedTextProps) {
  const { displayText, isComplete } = useTypewriter(text, {
    speed,
    startDelay,
  });

  return (
    <div className="relative">
      <FormattedText text={displayText} className={className} />
      {showCursor && !isComplete && (
        <span className="inline-block w-0.5 h-4 bg-slate-600 animate-pulse mr-1 align-middle" />
      )}
    </div>
  );
}