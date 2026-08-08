import { sseResponse } from "../../../../lib/live/server";
export const runtime = "nodejs"; export const dynamic = "force-dynamic";
export async function GET(request: Request, context: { params: Promise<{ stream: string }> }) { return sseResponse(request, (await context.params).stream); }
