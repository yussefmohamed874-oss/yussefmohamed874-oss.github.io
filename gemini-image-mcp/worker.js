// Gemini Image MCP server — Cloudflare Worker (single file, no dependencies)
//
// Speaks MCP over "Streamable HTTP" (JSON responses) and exposes one tool:
//   generate_image(prompt, aspect_ratio?, reference_image_urls?) -> image
//
// Settings (Cloudflare dashboard > Worker > Settings > Variables and Secrets):
//   GEMINI_API_KEY  (Secret, required)  your key from Google AI Studio
//   ACCESS_TOKEN    (Secret, required)  any long random word; it becomes part of the URL
//   GEMINI_MODEL    (Text, optional)    defaults to gemini-2.5-flash-image
//
// Connector URL to put in claude.ai:
//   https://<your-worker>.workers.dev/mcp/<ACCESS_TOKEN>

const DEFAULT_MODEL = "gemini-2.5-flash-image";
const PROTOCOL_VERSIONS = ["2025-06-18", "2025-03-26", "2024-11-05"];
const ASPECT_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"];

const TOOLS = [
  {
    name: "generate_image",
    title: "Generate image with Gemini",
    description:
      "Generate one image from a text prompt using Google's Gemini image model. " +
      "Write the prompt in English for best results. Default aspect ratio is 9:16 (vertical, for reels/series scenes).",
    inputSchema: {
      type: "object",
      properties: {
        prompt: { type: "string", description: "Detailed description of the image to create." },
        aspect_ratio: {
          type: "string",
          enum: ASPECT_RATIOS,
          default: "9:16",
          description: "Image shape. 9:16 = vertical phone video.",
        },
        reference_image_urls: {
          type: "array",
          items: { type: "string" },
          maxItems: 4,
          description:
            "Optional: up to 4 public https links to character reference images (JPEG/PNG/WebP, ideally under 500 KB each). " +
            "Gemini keeps the characters looking like these images. Say in the prompt who is in which image.",
        },
      },
      required: ["prompt"],
    },
  },
];

function json(body, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", ...extraHeaders },
  });
}

function rpcResult(id, result) {
  return { jsonrpc: "2.0", id, result };
}

function rpcError(id, code, message) {
  return { jsonrpc: "2.0", id: id ?? null, error: { code, message } };
}

function toBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
  }
  return btoa(binary);
}

async function fetchReference(url) {
  let parsed;
  try {
    parsed = new URL(url);
  } catch {
    throw new Error(`Bad reference link: ${url}`);
  }
  if (parsed.protocol !== "https:") throw new Error(`Reference link must start with https: ${url}`);
  const res = await fetch(parsed.toString());
  if (!res.ok) throw new Error(`Could not download reference image (HTTP ${res.status}): ${url}`);
  const mimeType = (res.headers.get("content-type") || "").split(";")[0].trim();
  if (!["image/jpeg", "image/png", "image/webp"].includes(mimeType)) {
    throw new Error(`Reference is not a JPEG/PNG/WebP image (${mimeType || "unknown type"}): ${url}`);
  }
  const buf = await res.arrayBuffer();
  if (buf.byteLength > 7 * 1024 * 1024) throw new Error(`Reference image is larger than 7 MB: ${url}`);
  return { inlineData: { mimeType, data: toBase64(buf) } };
}

async function generateImage(env, prompt, aspectRatio, referenceUrls = []) {
  const model = env.GEMINI_MODEL || DEFAULT_MODEL;
  const refParts = await Promise.all(referenceUrls.map(fetchReference));
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json", "x-goog-api-key": env.GEMINI_API_KEY },
    body: JSON.stringify({
      contents: [{ role: "user", parts: [...refParts, { text: prompt }] }],
      generationConfig: {
        responseModalities: ["IMAGE", "TEXT"],
        imageConfig: { aspectRatio },
      },
    }),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data?.error?.message || `HTTP ${res.status}`;
    throw new Error(`Gemini API error: ${msg}`);
  }

  const parts = data?.candidates?.[0]?.content?.parts || [];
  const images = parts.filter((p) => p.inlineData?.data);
  const texts = parts.filter((p) => p.text).map((p) => p.text);

  if (images.length === 0) {
    const reason =
      data?.promptFeedback?.blockReason ||
      data?.candidates?.[0]?.finishReason ||
      "no image returned";
    throw new Error(`Gemini did not return an image (${reason}). ${texts.join(" ")}`.trim());
  }

  return { images, texts, model };
}

async function handleRpc(msg, env) {
  const { id, method, params } = msg || {};
  const isNotification = id === undefined || id === null;

  switch (method) {
    case "initialize": {
      const requested = params?.protocolVersion;
      const protocolVersion = PROTOCOL_VERSIONS.includes(requested) ? requested : PROTOCOL_VERSIONS[0];
      return rpcResult(id, {
        protocolVersion,
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: "gemini-image-mcp", version: "1.1.0" },
        instructions:
          "Use generate_image to create images with Gemini. Use 9:16 for vertical series scenes.",
      });
    }
    case "ping":
      return rpcResult(id, {});
    case "tools/list":
      return rpcResult(id, { tools: TOOLS });
    case "tools/call": {
      if (params?.name !== "generate_image") {
        return rpcError(id, -32602, `Unknown tool: ${params?.name}`);
      }
      const args = params.arguments || {};
      const prompt = typeof args.prompt === "string" ? args.prompt.trim() : "";
      const aspect = ASPECT_RATIOS.includes(args.aspect_ratio) ? args.aspect_ratio : "9:16";
      const refs = Array.isArray(args.reference_image_urls)
        ? args.reference_image_urls.filter((u) => typeof u === "string" && u.trim()).map((u) => u.trim())
        : [];
      if (refs.length > 4) {
        return rpcResult(id, { isError: true, content: [{ type: "text", text: "Use at most 4 reference images." }] });
      }
      if (!prompt) {
        return rpcResult(id, { isError: true, content: [{ type: "text", text: "prompt is required." }] });
      }
      if (!env.GEMINI_API_KEY) {
        return rpcResult(id, {
          isError: true,
          content: [{ type: "text", text: "Server is missing GEMINI_API_KEY. Add it in Cloudflare settings." }],
        });
      }
      try {
        const { images, texts, model } = await generateImage(env, prompt, aspect, refs);
        const content = images.map((p) => ({
          type: "image",
          data: p.inlineData.data,
          mimeType: p.inlineData.mimeType || "image/png",
        }));
        content.push({
          type: "text",
          text: `Generated ${images.length} image(s) with ${model}, aspect ratio ${aspect}, ${refs.length} reference image(s).` +
            (texts.length ? ` Model note: ${texts.join(" ")}` : ""),
        });
        return rpcResult(id, { content });
      } catch (err) {
        return rpcResult(id, { isError: true, content: [{ type: "text", text: String(err.message || err) }] });
      }
    }
    default:
      if (isNotification) return null; // e.g. notifications/initialized
      return rpcError(id, -32601, `Method not found: ${method}`);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Health check page so you can open the root URL in a browser.
    if (url.pathname === "/" && request.method === "GET") {
      return new Response("Gemini Image MCP server is running.", { headers: { "content-type": "text/plain" } });
    }

    // Only /mcp/<ACCESS_TOKEN> is served. Everything else is 404.
    const match = url.pathname.match(/^\/mcp\/([^/]+)\/?$/);
    if (!match || !env.ACCESS_TOKEN || match[1] !== env.ACCESS_TOKEN) {
      return new Response("Not found", { status: 404 });
    }

    if (request.method === "GET") {
      // No server-initiated stream; spec allows 405 here.
      return new Response("Method Not Allowed", { status: 405, headers: { allow: "POST, DELETE" } });
    }
    if (request.method === "DELETE") {
      return new Response(null, { status: 204 });
    }
    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json(rpcError(null, -32700, "Parse error"), 400);
    }

    const headers = {};
    if (Array.isArray(body)) {
      const out = (await Promise.all(body.map((m) => handleRpc(m, env)))).filter(Boolean);
      if (out.length === 0) return new Response(null, { status: 202 });
      return json(out, 200, headers);
    }

    const out = await handleRpc(body, env);
    if (!out) return new Response(null, { status: 202 });
    return json(out, 200, headers);
  },
};
