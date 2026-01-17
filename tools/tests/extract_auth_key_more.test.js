const assert = require("node:assert/strict");
const childProcess = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

function makeTempDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "barnard-auth-"));
}

function makeSmali(keyB64) {
  return [
    ".method public getAuthHeader()Ljava/lang/String;",
    "    .locals 1",
    `    const-string v0, \"${keyB64}\"`,
    "    return-object v0",
    ".end method",
    "",
  ].join("\n");
}

function runScript(args) {
  const repoRoot = path.resolve(__dirname, "..", "..");
  const scriptPath = path.join(repoRoot, "tools", "extract_auth_key.js");
  return childProcess.spawnSync(process.execPath, [scriptPath, ...args], {
    encoding: "utf8",
  });
}

test("extract_auth_key.js uses search-root with nested smali", () => {
  const tempDir = makeTempDir();
  const nested = path.join(tempDir, "smali");
  fs.mkdirSync(nested, { recursive: true });

  const key = Buffer.alloc(64, "A");
  const keyB64 = key.toString("base64");
  const smaliPath = path.join(nested, "InstrumentRepository.smali");
  const outPath = path.join(tempDir, "auth.key");
  fs.writeFileSync(smaliPath, makeSmali(keyB64), "utf8");

  const result = runScript(["--search-root", tempDir, "--out", outPath, "--json"]);

  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout.trim());
  assert.equal(payload.ok, true);
  assert.equal(fs.readFileSync(outPath, "utf8").trim(), keyB64);
});

test("extract_auth_key.js returns alreadyPresent when output exists", () => {
  const tempDir = makeTempDir();
  const key = Buffer.alloc(64, "B");
  const keyB64 = key.toString("base64");
  const smaliPath = path.join(tempDir, "InstrumentRepository.smali");
  const outPath = path.join(tempDir, "auth.key");
  fs.writeFileSync(smaliPath, makeSmali(keyB64), "utf8");
  fs.writeFileSync(outPath, `${keyB64}\n`, "utf8");

  const result = runScript(["--smali", smaliPath, "--out", outPath, "--json"]);

  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout.trim());
  assert.equal(payload.ok, true);
  assert.equal(payload.alreadyPresent, true);
});

test("extract_auth_key.js fails on multiple keys", () => {
  const tempDir = makeTempDir();
  const key1 = Buffer.alloc(64, "A").toString("base64");
  const key2 = Buffer.alloc(64, "B").toString("base64");
  const dirOne = path.join(tempDir, "one");
  const dirTwo = path.join(tempDir, "two");
  fs.mkdirSync(dirOne, { recursive: true });
  fs.mkdirSync(dirTwo, { recursive: true });
  const smaliOne = path.join(dirOne, "InstrumentRepository.smali");
  const smaliTwo = path.join(dirTwo, "InstrumentRepository.smali");
  const outPath = path.join(tempDir, "auth.key");
  fs.writeFileSync(smaliOne, makeSmali(key1), "utf8");
  fs.writeFileSync(smaliTwo, makeSmali(key2), "utf8");

  const result = runScript(["--search-root", tempDir, "--out", outPath, "--json"]);

  assert.equal(result.status, 1, result.stdout);
  const payload = JSON.parse(result.stdout.trim());
  assert.equal(payload.ok, false);
  assert.match(payload.error, /Multiple keys/);
});

test("extract_auth_key.js errors on missing input", () => {
  const tempDir = makeTempDir();
  const outPath = path.join(tempDir, "auth.key");
  const missing = path.join(tempDir, "missing.zip");

  const result = runScript(["--input", missing, "--out", outPath, "--json"]);

  assert.equal(result.status, 1, result.stdout);
  const payload = JSON.parse(result.stdout.trim());
  assert.equal(payload.ok, false);
  assert.match(payload.error, /Path not found/);
});
