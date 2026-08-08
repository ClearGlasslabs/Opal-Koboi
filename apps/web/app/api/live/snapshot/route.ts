import { snapshotResponse } from "../../../../lib/live/server";
export const dynamic = "force-dynamic";
export async function GET(request: Request) { return snapshotResponse(new URL(request.url).searchParams.get("stream") ?? "public"); }
