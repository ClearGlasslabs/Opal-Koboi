import { getPublicSnapshot } from "./snapshot";

export const STREAMS = new Set(["public", "status", "performance", "content", "dashboard"]);
export async function snapshotResponse(stream: string) {
  if (!STREAMS.has(stream)) return Response.json({ error: "Unknown stream" }, { status: 404 });
  return Response.json(await getPublicSnapshot(stream), { headers: { "Cache-Control": "public, max-age=0, s-maxage=30, stale-while-revalidate=300" } });
}
export async function sseResponse(request: Request, stream: string) {
  if (!STREAMS.has(stream)) return Response.json({ error: "Unknown stream" }, { status: 404 });
  if (stream === "dashboard") return Response.json({ error: "Authentication required" }, { status: 401 });
  const origin = request.headers.get("origin");
  if (origin && origin !== new URL(request.url).origin) return Response.json({ error: "Origin denied" }, { status: 403 });
  const snapshot = await getPublicSnapshot(stream);
  if (!snapshot.enabled) return Response.json(snapshot, { status: 503, headers: { "Retry-After": "30" } });
  const encoder = new TextEncoder();
  const body = new ReadableStream({ start(controller) { controller.enqueue(encoder.encode(": connected\nretry: 5000\n\n")); controller.close(); } });
  return new Response(body, { headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-cache, no-transform", Connection: "keep-alive", "X-Accel-Buffering": "no" } });
}
