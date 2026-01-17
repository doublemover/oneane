const assert = require("node:assert/strict");
const childProcess = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

function makeTempDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "barnard-auth-"));
}

test("extract_auth_key.js emits JSON output", () => {
  const repoRoot = path.resolve(__dirname, "..", "..");
  const scriptPath = path.join(repoRoot, "tools", "extract_auth_key.js");
  const tempDir = makeTempDir();

  const key = Buffer.alloc(64, "A");
  const keyB64 = key.toString("base64");
  const smaliPath = path.join(tempDir, "InstrumentRepository.smali");
  const outPath = path.join(tempDir, "auth.key");

  const smali = [
    ".method public getAuthHeader()Ljava/lang/String;",
    "    .locals 1",
    `    const-string v0, \"${keyB64}\"`,
    "    return-object v0",
    ".end method",
    "",
  ].join("\n");
  fs.writeFileSync(smaliPath, smali, "utf8");

  const result = childProcess.spawnSync(
    process.execPath,
    [scriptPath, "--smali", smaliPath, "--out", outPath, "--json"],
    { encoding: "utf8" }
  );

  assert.equal(result.status, 0, result.stderr);
  const payload = JSON.parse(result.stdout.trim());
  assert.equal(payload.ok, true);
  assert.equal(fs.readFileSync(outPath, "utf8").trim(), keyB64);
});
