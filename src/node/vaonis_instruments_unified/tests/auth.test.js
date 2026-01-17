import assert from "node:assert/strict";
import test from "node:test";

import { buildAuthorizationHeader, resolveKeyMaterial } from "../src/auth.js";

function makeChallenge(prefix, payload) {
  return `${prefix}${Buffer.from(payload).toString("base64")}`;
}

test("buildAuthorizationHeader uses prefix and signs", () => {
  const key = Buffer.alloc(64, 1);
  const header = buildAuthorizationHeader(
    {
      challenge: makeChallenge("A", "abc"),
      telescopeId: "scope",
      bootCount: 2,
    },
    { keyMaterial: key }
  );

  assert.ok(header.startsWith("Basic android|A|"));
  const signature = Buffer.from(header.split("|")[2], "base64");
  assert.equal(signature.length, 128);
});

test("resolveKeyMaterial supports base64 strings", () => {
  const key = Buffer.alloc(64, 2);
  const keyB64 = key.toString("base64");
  const resolved = resolveKeyMaterial({ keyMaterial: keyB64 });
  assert.equal(resolved.length, 64);
  assert.equal(resolved[0], 2);
});

test("buildAuthorizationHeader supports 32-byte keys", () => {
  const key = Buffer.alloc(32, 3);
  const header = buildAuthorizationHeader(
    {
      challenge: makeChallenge("B", "payload"),
      telescopeId: "scope",
      bootCount: 1,
    },
    { keyMaterial: key }
  );

  assert.ok(header.startsWith("Basic android|B|"));
});

test("buildAuthorizationHeader rejects invalid challenge", () => {
  const key = Buffer.alloc(64, 1);
  assert.throws(
    () =>
      buildAuthorizationHeader(
        { challenge: "A", telescopeId: "scope", bootCount: 1 },
        { keyMaterial: key }
      ),
    /challenge must include/
  );
});

test("buildAuthorizationHeader rejects unexpected key length", () => {
  const key = Buffer.alloc(5, 1);
  assert.throws(
    () =>
      buildAuthorizationHeader(
        { challenge: makeChallenge("C", "payload"), telescopeId: "scope", bootCount: 1 },
        { keyMaterial: key }
      ),
    /Unexpected Ed25519 key length/
  );
});
