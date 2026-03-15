import { describe, it, expect, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";

afterEach(cleanup);
import { getToolLabel, ToolInvocationBadge } from "../ToolInvocationBadge";

describe("getToolLabel", () => {
  it("str_replace_editor + create", () => {
    expect(getToolLabel("str_replace_editor", { command: "create", path: "/components/Card.jsx" })).toBe("Creating Card.jsx");
  });

  it("str_replace_editor + str_replace", () => {
    expect(getToolLabel("str_replace_editor", { command: "str_replace", path: "/App.tsx" })).toBe("Editing App.tsx");
  });

  it("str_replace_editor + insert", () => {
    expect(getToolLabel("str_replace_editor", { command: "insert", path: "/App.tsx" })).toBe("Editing App.tsx");
  });

  it("str_replace_editor + view", () => {
    expect(getToolLabel("str_replace_editor", { command: "view", path: "/App.tsx" })).toBe("Reading App.tsx");
  });

  it("str_replace_editor + undo_edit", () => {
    expect(getToolLabel("str_replace_editor", { command: "undo_edit", path: "/App.tsx" })).toBe("Undoing edit in App.tsx");
  });

  it("file_manager + rename", () => {
    expect(getToolLabel("file_manager", { command: "rename", path: "/Card.jsx", new_path: "/NewCard.jsx" })).toBe("Renaming Card.jsx → NewCard.jsx");
  });

  it("file_manager + delete", () => {
    expect(getToolLabel("file_manager", { command: "delete", path: "/Card.jsx" })).toBe("Deleting Card.jsx");
  });

  it("fallback returns raw toolName", () => {
    expect(getToolLabel("unknown_tool", {})).toBe("unknown_tool");
  });
});

describe("ToolInvocationBadge", () => {
  it("pending state renders spinner, no green dot", () => {
    const { container } = render(
      <ToolInvocationBadge
        toolInvocation={{ toolName: "str_replace_editor", state: "call", args: { command: "create", path: "/Card.jsx" } }}
      />
    );
    expect(screen.getByText("Creating Card.jsx")).toBeTruthy();
    // spinner has animate-spin class
    expect(container.querySelector(".animate-spin")).toBeTruthy();
    // no green dot
    expect(container.querySelector(".bg-emerald-500")).toBeNull();
  });

  it("result state renders green dot, no spinner", () => {
    const { container } = render(
      <ToolInvocationBadge
        toolInvocation={{ toolName: "str_replace_editor", state: "result", result: "ok", args: { command: "create", path: "/Card.jsx" } }}
      />
    );
    expect(screen.getByText("Creating Card.jsx")).toBeTruthy();
    expect(container.querySelector(".bg-emerald-500")).toBeTruthy();
    expect(container.querySelector(".animate-spin")).toBeNull();
  });
});
