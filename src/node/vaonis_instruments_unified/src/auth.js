import { createHash } from "crypto";
import { existsSync, readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { homedir, tmpdir } from "node:os";
import nacl from "tweetnacl";

const __dirname = dirname(fileURLToPath(import.meta.url));

/**
 * @typedef {Object} AuthContext
 * @property {string} challenge
 * @property {string} telescopeId
 * @property {string|number} bootCount
 */

/**
 * @typedef {Object} AuthOptions
 * @property {string|Buffer|Uint8Array} [keyMaterial]
 * @property {string} [keyFile]
 */

/**
 * @param {string} path
 * @returns {Buffer}
 */
function readKeyFile(path) {
  const safePath = normalizeKeyPath(path);
  const raw = readFileSync(safePath, "utf-8").trim();
  return Buffer.from(raw, "base64");
}

const SAFE_KEY_ROOTS = [
  process.cwd(),
  homedir(),
  tmpdir(),
  resolve(__dirname, ".."),
  resolve(__dirname, "../../.."),
];

function normalizeForCompare(value) {
  const normalized = resolve(value).replace(/[\\\/]+$/, "");
  return process.platform === "win32" ? normalized.toLowerCase() : normalized;
}

function isWithinRoot(root, target) {
  const normalizedRoot = normalizeForCompare(root);
  const normalizedTarget = normalizeForCompare(target);
  if (normalizedRoot === normalizedTarget) {
    return true;
  }
  const withSep = normalizedRoot.endsWith("\\") || normalizedRoot.endsWith("/")
    ? normalizedRoot
    : `${normalizedRoot}${normalizedRoot.includes("\\") ? "\\" : "/"}`;
  return normalizedTarget.startsWith(withSep);
}

/**
 * @param {string} value
 * @returns {string}
 */
function normalizeKeyPath(value) {
  const resolved = resolve(String(value));
  for (const root of SAFE_KEY_ROOTS) {
    if (root && isWithinRoot(root, resolved)) {
      return resolved;
    }
  }
  throw new Error(`Key file path is outside allowed roots: ${resolved}`);
}

/**
 * @param {string|null|undefined} explicitPath
 * @returns {string|null}
 */
function findKeyPath(explicitPath) {
  const candidates = [];
  if (explicitPath) {
    candidates.push(explicitPath);
  }
  if (process.env.VAONIS_AUTH_KEY_FILE) {
    candidates.push(process.env.VAONIS_AUTH_KEY_FILE);
  }
  candidates.push(resolve(process.cwd(), ".auth_key"));
  candidates.push(resolve(__dirname, "../.auth_key"));
  candidates.push(resolve(__dirname, "../../..", "python", ".auth_key"));

  for (const candidate of candidates) {
    if (candidate && existsSync(candidate)) {
      try {
        return normalizeKeyPath(candidate);
      } catch (err) {
        continue;
      }
    }
  }
  return null;
}

/**
 * @param {AuthOptions} [options]
 * @returns {Buffer}
 */
function resolveKeyMaterial({ keyMaterial, keyFile } = {}) {
  if (keyMaterial !== undefined && keyMaterial !== null) {
    if (typeof keyMaterial === "string") {
      return Buffer.from(keyMaterial, "base64");
    }
    return Buffer.from(keyMaterial);
  }

  const path = findKeyPath(keyFile);
  if (!path) {
    throw new Error(
      "Authorization key file not found. Set VAONIS_AUTH_KEY_FILE or pass keyMaterial."
    );
  }
  return readKeyFile(path);
}

/**
 * @param {AuthContext} ctx
 * @returns {Buffer}
 */
function buildPayload({ challenge, telescopeId, bootCount }) {
  if (!challenge || challenge.length < 2) {
    throw new Error("challenge must include a prefix + base64 payload");
  }
  const challengeBytes = Buffer.from(challenge.slice(1), "base64");
  const tail = `|${telescopeId}|${bootCount}`;
  return Buffer.concat([challengeBytes, Buffer.from(tail, "utf-8")]);
}

/**
 * @param {Buffer} digest
 * @param {Buffer} keyBytes
 * @returns {Uint8Array}
 */
function signDigest(digest, keyBytes) {
  if (keyBytes.length === 64) {
    return nacl.sign(digest, keyBytes);
  }
  if (keyBytes.length === 32) {
    const keyPair = nacl.sign.keyPair.fromSeed(keyBytes);
    return nacl.sign(digest, keyPair.secretKey);
  }
  throw new Error(`Unexpected Ed25519 key length: ${keyBytes.length} bytes`);
}

/**
 * @param {AuthContext} ctx
 * @param {AuthOptions} [options]
 * @returns {string}
 */
export function buildAuthorizationHeader(ctx, options = {}) {
  const keyBytes = resolveKeyMaterial(options);
  const payload = buildPayload(ctx);
  const digest = createHash("sha512").update(payload).digest();
  const signedMessage = signDigest(digest, keyBytes);
  const signatureB64 = Buffer.from(signedMessage).toString("base64");
  const prefix = ctx.challenge[0];
  return `Basic android|${prefix}|${signatureB64}`;
}

export { resolveKeyMaterial };
