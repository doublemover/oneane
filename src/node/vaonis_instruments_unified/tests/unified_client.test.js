import assert from "node:assert/strict";
import test from "node:test";

import { UnifiedHttpClient } from "../src/unified_client.js";

function makeJsonResponse(payload, { status = 200 } = {}) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "content-type": "application/json" },
  });
}

function makeTextResponse(text, { status = 200 } = {}) {
  return new Response(text, {
    status,
    headers: { "content-type": "text/plain" },
  });
}

test("detectBaseUrl tries prefixes", async () => {
  const seen = [];
  const fetchImpl = async (url) => {
    seen.push(url);
    if (url.includes("/stellina/http/v1/app/status")) {
      return makeTextResponse("ok", { status: 200 });
    }
    return makeTextResponse("no", { status: 404 });
  };

  const client = new UnifiedHttpClient({
    host: "example",
    port: 8082,
    prefixes: ["", "/stellina/http"],
    fetchImpl,
    logResponses: false,
  });

  const base = await client.detectBaseUrl();

  assert.equal(base, "http://example:8082/stellina/http/v1");
  assert.ok(seen.length >= 2);
});

test("request builds query and headers", async () => {
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, options });
    return makeJsonResponse({ ok: true });
  };

  const client = new UnifiedHttpClient({ fetchImpl, logResponses: false });
  client.baseUrl = "http://example:8082/v1";

  const result = await client.request("POST", "/app/status", {
    auth: "token",
    params: { a: 1, b: ["x", "y"] },
    jsonBody: { hello: "world" },
  });

  assert.deepEqual(result, { ok: true });
  assert.ok(calls[0].url.includes("a=1"));
  assert.ok(calls[0].url.includes("b=x"));
  assert.ok(calls[0].url.includes("b=y"));
  assert.equal(calls[0].options.headers.Authorization, "token");
  assert.equal(calls[0].options.headers["Content-Type"], "application/json");
});

test("request throws on non-ok response", async () => {
  const fetchImpl = async () => makeTextResponse("bad", { status: 400 });
  const client = new UnifiedHttpClient({ fetchImpl, logResponses: false });
  client.baseUrl = "http://example:8082/v1";

  await assert.rejects(
    () => client.request("GET", "/app/status"),
    /HTTP 400/
  );
});

test("downloadImage returns bytes for image-like content", async () => {
  const png = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, options });
    return new Response(png, {
      status: 500,
      headers: { "content-type": "application/octet-stream" },
    });
  };

  const client = new UnifiedHttpClient({ fetchImpl, logResponses: false });
  client.baseUrl = "http://example:8082/v1";

  const buffer = await client.downloadImage("/image", { auth: "token" });

  assert.equal(buffer.slice(0, 8).toString("hex"), png.toString("hex"));
  assert.equal(calls[0].options.headers.Authorization, "token");
});

test("downloadImage throws for non-image content", async () => {
  const fetchImpl = async () =>
    new Response("no", {
      status: 500,
      headers: { "content-type": "text/plain" },
    });

  const client = new UnifiedHttpClient({ fetchImpl, logResponses: false });
  client.baseUrl = "http://example:8082/v1";

  await assert.rejects(() => client.downloadImage("/image"), /HTTP 500/);
});

test("constructor throws without fetch implementation", () => {
  assert.throws(() => new UnifiedHttpClient({ fetchImpl: null }), /fetch is required/);
});

test("detectBaseUrl throws when none succeed", async () => {
  const fetchImpl = async () => makeTextResponse("no", { status: 404 });
  const client = new UnifiedHttpClient({
    host: "example",
    port: 8082,
    prefixes: ["", "/stellina/http"],
    fetchImpl,
    logResponses: false,
  });

  await assert.rejects(() => client.detectBaseUrl(), /Unable to detect/);
});

test("request logs colorized payload when enabled", async () => {
  const logs = [];
  const fetchImpl = async () => makeJsonResponse({ ok: true });
  const client = new UnifiedHttpClient({
    fetchImpl,
    logResponses: true,
    colorizeResponses: true,
    logger: { log: (line) => logs.push(line) },
  });
  client.baseUrl = "http://example:8082/v1";

  await client.request("GET", "/app/status");

  assert.ok(logs.some((line) => line.includes("\u001b[")));
});

test("request handles text responses", async () => {
  const fetchImpl = async () => makeTextResponse("hello");
  const client = new UnifiedHttpClient({ fetchImpl, logResponses: false });
  client.baseUrl = "http://example:8082/v1";

  const payload = await client.request("GET", "/app/status");

  assert.equal(payload, "hello");
});

test("callOperation rejects unknown id", async () => {
  const fetchImpl = async () => makeJsonResponse({ ok: true });
  const client = new UnifiedHttpClient({ fetchImpl, logResponses: false });
  client.baseUrl = "http://example:8082/v1";

  await assert.rejects(() => client.callOperation("nope"), /Unknown operationId/);
});

test("fetchWithTimeout forwards abort signal", async () => {
  const seen = [];
  const fetchImpl = async (url, options) => {
    seen.push({ url, signal: options.signal });
    return makeJsonResponse({ ok: true });
  };
  const client = new UnifiedHttpClient({ fetchImpl, logResponses: false });

  await client._fetchWithTimeout("http://example", { method: "GET" });

  assert.equal(seen.length, 1);
  assert.equal(typeof seen[0].signal?.aborted, "boolean");
});

test("downloadImage logs buffer payload", async () => {
  const logs = [];
  const png = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  const fetchImpl = async () =>
    new Response(png, {
      status: 200,
      headers: { "content-type": "image/png" },
    });
  const client = new UnifiedHttpClient({
    fetchImpl,
    logResponses: true,
    logger: { log: (line) => logs.push(line) },
  });
  client.baseUrl = "http://example:8082/v1";

  await client.downloadImage("/image");

  assert.ok(logs.some((line) => line.includes("image bytes=")));
});
