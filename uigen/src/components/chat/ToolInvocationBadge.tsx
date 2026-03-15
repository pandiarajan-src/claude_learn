"use client";

import { Loader2 } from "lucide-react";
import path from "path";

interface ToolInvocationBadgeProps {
  toolInvocation: {
    toolName: string;
    state: string;
    result?: unknown;
    args?: Record<string, unknown>;
  };
}

export function getToolLabel(toolName: string, args?: Record<string, unknown>): string {
  const command = args?.command as string | undefined;
  const filename = args?.path ? path.basename(args.path as string) : undefined;

  if (toolName === "str_replace_editor") {
    switch (command) {
      case "create":
        return filename ? `Creating ${filename}` : "Creating file";
      case "str_replace":
      case "insert":
        return filename ? `Editing ${filename}` : "Editing file";
      case "view":
        return filename ? `Reading ${filename}` : "Reading file";
      case "undo_edit":
        return filename ? `Undoing edit in ${filename}` : "Undoing edit";
    }
  }

  if (toolName === "file_manager") {
    switch (command) {
      case "rename": {
        const from = args?.path ? path.basename(args.path as string) : "file";
        const to = args?.new_path ? path.basename(args.new_path as string) : "file";
        return `Renaming ${from} → ${to}`;
      }
      case "delete":
        return filename ? `Deleting ${filename}` : "Deleting file";
    }
  }

  return toolName;
}

export function ToolInvocationBadge({ toolInvocation }: ToolInvocationBadgeProps) {
  const label = getToolLabel(toolInvocation.toolName, toolInvocation.args);
  const isDone = toolInvocation.state === "result" && toolInvocation.result;

  return (
    <div className="inline-flex items-center gap-2 mt-2 px-3 py-1.5 bg-neutral-50 rounded-lg text-xs border border-neutral-200">
      {isDone ? (
        <div className="w-2 h-2 rounded-full bg-emerald-500" />
      ) : (
        <Loader2 className="w-3 h-3 animate-spin text-blue-600" />
      )}
      <span className="text-neutral-700">{label}</span>
    </div>
  );
}
