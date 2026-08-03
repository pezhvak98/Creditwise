import { useMemo } from "react";

interface FormattedTextProps {
  text: string;
  className?: string;
}

type ParsedBlock =
  | { type: "paragraph"; content: string }
  | { type: "bullet"; items: string[] }
  | { type: "ordered"; items: string[] };

export function FormattedText({ text, className = "" }: FormattedTextProps) {
  const blocks = useMemo(() => parseText(text), [text]);

  return (
    <div className={`space-y-2 ${className}`}>
      {blocks.map((block, index) => {
        switch (block.type) {
          case "paragraph":
            return (
              <p key={index} className="leading-relaxed">
                {block.content}
              </p>
            );
          case "bullet":
            return (
              <ul key={index} className="list-disc list-inside space-y-1 mr-4">
                {block.items.map((item, i) => (
                  <li key={i} className="leading-relaxed">
                    {item}
                  </li>
                ))}
              </ul>
            );
          case "ordered":
            return (
              <ol key={index} className="list-decimal list-inside space-y-1 mr-4">
                {block.items.map((item, i) => (
                  <li key={i} className="leading-relaxed">
                    {item}
                  </li>
                ))}
              </ol>
            );
        }
      })}
    </div>
  );
}

function parseText(text: string): ParsedBlock[] {
  const lines = text.split("\n").map((line) => line.trim());
  const blocks: ParsedBlock[] = [];
  let currentParagraph: string[] = [];
  let currentBullet: string[] = [];
  let currentOrdered: string[] = [];

  const flushParagraph = () => {
    if (currentParagraph.length > 0) {
      blocks.push({ type: "paragraph", content: currentParagraph.join(" ") });
      currentParagraph = [];
    }
  };

  const flushBullet = () => {
    if (currentBullet.length > 0) {
      blocks.push({ type: "bullet", items: currentBullet });
      currentBullet = [];
    }
  };

  const flushOrdered = () => {
    if (currentOrdered.length > 0) {
      blocks.push({ type: "ordered", items: currentOrdered });
      currentOrdered = [];
    }
  };

  const flushAll = () => {
    flushParagraph();
    flushBullet();
    flushOrdered();
  };

  for (const line of lines) {
    // Check for bullet points: "- item", "• item", "* item"
    const bulletMatch = line.match(/^[-•*]\s+(.+)/);
    if (bulletMatch) {
      flushParagraph();
      flushOrdered();
      currentBullet.push(bulletMatch[1]);
      continue;
    }

    // Check for ordered list: "1. item", "2) item"
    const orderedMatch = line.match(/^\d+[.)]\s+(.+)/);
    if (orderedMatch) {
      flushParagraph();
      flushBullet();
      currentOrdered.push(orderedMatch[1]);
      continue;
    }

    // Empty line: flush current blocks
    if (line === "") {
      flushAll();
      continue;
    }

    // Regular paragraph text
    flushBullet();
    flushOrdered();
    currentParagraph.push(line);
  }

  flushAll();
  return blocks;
}