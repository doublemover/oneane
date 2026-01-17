#!/usr/bin/env node
/*
Extract the Barnard auth key from decoded APK smali sources.

This script looks for InstrumentRepository.getAuthHeader() and pulls the
64-byte base64 key used for Ed25519 signing. Output defaults to
src/python/.auth_key (gitignored). If no input is provided, it searches
for an APK/XAPK/ZIP in the repo root and prompts for a path if needed.
*/

const fs = require("node:fs");
const path = require("node:path");
const childProcess = require("node:child_process");
const readline = require("node:readline");
const os = require("node:os");

const BASE64_RE = /^[A-Za-z0-9+/]+={0,2}$/;
const METHOD_RE = /\.method[^\n]*getAuthHeader[^\n]*\n([\s\S]*?)\n\.end method/;
const STRING_RE = /const-string(?:\/jumbo)?\s+v\d+,\s+"([^"]+)"/g;

/**
 * @returns {string}
 */
function repoRoot() {
  return path.resolve(__dirname, "..");
}

function normalizeForCompare(value) {
  return process.platform === "win32" ? value.toLowerCase() : value;
}

function isWithinRoot(root, candidate) {
  const normalizedRoot = normalizeForCompare(root);
  const normalizedCandidate = normalizeForCompare(candidate);
  if (normalizedCandidate === normalizedRoot) {
    return true;
  }
  return normalizedCandidate.startsWith(`${normalizedRoot}${path.sep}`);
}

function normalizeSafePath(candidate, { mustExist = false } = {}) {
  if (!candidate) {
    throw new Error("Path is required.");
  }
  const resolved = path.resolve(candidate);
  const safeRoots = [
    process.cwd(),
    repoRoot(),
    os.homedir(),
    os.tmpdir(),
  ].map((root) => path.resolve(root));
  const allowed = safeRoots.some((root) => isWithinRoot(root, resolved));
  if (!allowed) {
    throw new Error(`Path outside allowed roots: ${resolved}`);
  }
  if (mustExist && !fs.existsSync(resolved)) {
    throw new Error(`Path not found: ${resolved}`);
  }
  return resolved;
}

/**
 * @returns {string}
 */
function defaultOutput() {
  return path.join(repoRoot(), "src", "python", ".auth_key");
}

/**
 * @returns {Promise<string>}
 */
function promptForPath() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise((resolve, reject) => {
    rl.question(
      "Enter path to Barnard APK/XAPK/ZIP or decoded folder: ",
      (answer) => {
        rl.close();
        const trimmed = answer.trim();
        if (!trimmed) {
          reject(new Error("No input provided."));
          return;
        }
        resolve(normalizeSafePath(trimmed, { mustExist: true }));
      }
    );
  });
}

/**
 * @param {string} root
 * @returns {string[]}
 */
function pickCandidates(root) {
  const preferred = path.join(root, "com.vaonis.barnard.zip");
  const candidates = [];
  if (fs.existsSync(preferred)) {
    candidates.push(preferred);
  }
  for (const ext of [".apk", ".xapk", ".zip"]) {
    for (const entry of fs.readdirSync(root)) {
      if (entry.endsWith(ext)) {
        const candidate = path.join(root, entry);
        if (!candidates.includes(candidate)) {
          candidates.push(candidate);
        }
      }
    }
  }
  return candidates;
}

/**
 * @param {string} name
 * @returns {string}
 */
function ensureTempDir(name) {
  const dir = path.join(repoRoot(), "temp", name);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

/**
 * @param {string} command
 * @param {string[]} args
 * @returns {void}
 */
function runCommand(command, args) {
  const result = childProcess.spawnSync(command, args, {
    stdio: "inherit",
  });
  if (result.status !== 0) {
    throw new Error(`${command} exited with code ${result.status}`);
  }
}

/**
 * @param {string} zipPath
 * @returns {string}
 */
function expandZip(zipPath) {
  const stamp = new Date().toISOString().replace(/[:.]/g, "");
  const outDir = ensureTempDir(`zip_extract_${stamp}`);
  if (process.platform === "win32") {
    const command = [
      "-NoProfile",
      "-Command",
      `Expand-Archive -Force -LiteralPath "${zipPath}" -DestinationPath "${outDir}"`,
    ];
    runCommand("powershell", command);
  } else {
    runCommand("unzip", ["-q", zipPath, "-d", outDir]);
  }
  return outDir;
}

/**
 * @param {string} apkPath
 * @param {string} apktoolJar
 * @returns {string}
 */
function decodeApk(apkPath, apktoolJar) {
  const stamp = new Date().toISOString().replace(/[:.]/g, "");
  const baseName = path.basename(apkPath).replace(/\W+/g, "_");
  const outDir = ensureTempDir(`apktool_${stamp}_${baseName}`);
  runCommand("java", [
    "-jar",
    apktoolJar,
    "d",
    "-f",
    "-o",
    outDir,
    apkPath,
  ]);
  return outDir;
}

/**
 * @param {string} root
 * @param {string} fileName
 * @returns {string[]}
 */
function findFilesByName(root, fileName) {
  const results = [];
  const safeRoot = normalizeSafePath(root, { mustExist: true });
  const entries = fs.readdirSync(safeRoot, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(safeRoot, entry.name);
    if (entry.isDirectory()) {
      results.push(...findFilesByName(fullPath, fileName));
    } else if (entry.isFile() && entry.name === fileName) {
      results.push(fullPath);
    }
  }
  return results;
}

/**
 * @param {string} root
 * @param {string} ext
 * @returns {string[]}
 */
function findFilesByExt(root, ext) {
  const results = [];
  const safeRoot = normalizeSafePath(root, { mustExist: true });
  const entries = fs.readdirSync(safeRoot, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(safeRoot, entry.name);
    if (entry.isDirectory()) {
      results.push(...findFilesByExt(fullPath, ext));
    } else if (entry.isFile() && entry.name.toLowerCase().endsWith(ext)) {
      results.push(fullPath);
    }
  }
  return results;
}

/**
 * @param {string} apkPath
 * @returns {number}
 */
function scoreApk(apkPath) {
  const name = path.basename(apkPath).toLowerCase();
  if (name.includes("base")) {
    return 0;
  }
  if (name.includes("com.vaonis") || name.includes("barnard")) {
    return 1;
  }
  return 2;
}

/**
 * @param {string} text
 * @returns {string[]}
 */
function extractCandidates(text) {
  const match = text.match(METHOD_RE);
  const segment = match ? match[1] : text;
  const candidates = [];
  for (const stringMatch of segment.matchAll(STRING_RE)) {
    const raw = stringMatch[1].trim();
    if (raw.length < 20 || !BASE64_RE.test(raw)) {
      continue;
    }
    const decoded = Buffer.from(raw, "base64");
    if (decoded.length === 64) {
      candidates.push(raw);
    }
  }
  return candidates;
}

/**
 * @param {Record<string, string[]>} keys
 * @returns {string}
 */
function selectKey(keys) {
  const entries = Object.entries(keys);
  if (entries.length === 0) {
    throw new Error("No 64-byte base64 key found.");
  }
  if (entries.length > 1) {
    const details = entries
      .map(([key, paths]) => `${key}: ${paths.join(", ")}`)
      .join("\n");
    throw new Error(`Multiple keys found:\n${details}`);
  }
  return entries[0][0];
}

/**
 * @param {string|null} provided
 * @param {string} outputPath
 * @returns {Promise<string>}
 */
async function resolveInputPath(provided) {
  if (provided) {
    return normalizeSafePath(provided, { mustExist: true });
  }
  const candidates = pickCandidates(repoRoot());
  if (candidates.length > 0) {
    return normalizeSafePath(candidates[0], { mustExist: true });
  }
  return await promptForPath();
}

/**
 * @typedef {Object} ScriptArgs
 * @property {string|null} input
 * @property {string|null} smali
 * @property {string|null} searchRoot
 * @property {string} apktoolJar
 * @property {string} out
 * @property {boolean} json
 */

/**
 * @param {string[]} argv
 * @returns {ScriptArgs}
 */
function parseArgs(argv) {
  const args = {
    input: null,
    smali: null,
    searchRoot: null,
    apktoolJar: path.join(repoRoot(), "tools", "apktool_2.9.3.jar"),
    out: defaultOutput(),
    json: false,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const value = argv[i];
    if (value === "--input") {
      args.input = argv[i + 1];
      i += 1;
    } else if (value === "--smali") {
      args.smali = argv[i + 1];
      i += 1;
    } else if (value === "--search-root") {
      args.searchRoot = argv[i + 1];
      i += 1;
    } else if (value === "--apktool-jar") {
      args.apktoolJar = argv[i + 1];
      i += 1;
    } else if (value === "--out") {
      args.out = argv[i + 1];
      i += 1;
    } else if (value === "--json") {
      args.json = true;
    }
  }
  return args;
}

/**
 * @returns {Promise<void>}
 */
async function main(args) {
  const outputPath = normalizeSafePath(args.out);
  if (fs.existsSync(outputPath)) {
    const content = fs.readFileSync(outputPath, "utf8").trim();
    if (content) {
      return {
        outputPath,
        inputPath: null,
        alreadyPresent: true,
      };
    }
  }
  const inputPath =
    !args.smali && !args.searchRoot
      ? await resolveInputPath(args.input)
      : args.input
        ? normalizeSafePath(args.input, { mustExist: true })
        : null;

  let searchRoot = args.searchRoot
    ? normalizeSafePath(args.searchRoot, { mustExist: true })
    : null;
  let smaliPath = args.smali
    ? normalizeSafePath(args.smali, { mustExist: true })
    : null;

  if (!smaliPath && !searchRoot && inputPath) {
    const resolved = normalizeSafePath(inputPath, { mustExist: true });
    if (!fs.existsSync(resolved)) {
      throw new Error(`Input not found: ${resolved}`);
    }
    const stat = fs.statSync(resolved);
    if (stat.isDirectory()) {
      searchRoot = resolved;
    } else if (resolved.endsWith(".zip") || resolved.endsWith(".xapk")) {
      searchRoot = expandZip(resolved);
    } else if (resolved.endsWith(".apk")) {
      const apktoolJar = normalizeSafePath(args.apktoolJar, { mustExist: true });
      searchRoot = decodeApk(resolved, apktoolJar);
    } else {
      throw new Error(`Unsupported input: ${resolved}`);
    }
  }

  if (!smaliPath && !searchRoot) {
    throw new Error("Provide --smali, --search-root, or --input.");
  }

  const smaliFiles = new Set();
  if (smaliPath) {
    const stat = fs.statSync(smaliPath);
    if (stat.isDirectory()) {
      for (const file of findFilesByName(smaliPath, "InstrumentRepository.smali")) {
        smaliFiles.add(file);
      }
    } else {
      smaliFiles.add(smaliPath);
    }
  }
  if (
    searchRoot &&
    fs.existsSync(searchRoot) &&
    fs.statSync(searchRoot).isDirectory()
  ) {
    for (const file of findFilesByName(searchRoot, "InstrumentRepository.smali")) {
      smaliFiles.add(file);
    }
  }

  let smaliList = Array.from(smaliFiles);
  if (
    smaliList.length === 0 &&
    searchRoot &&
    fs.existsSync(searchRoot) &&
    fs.statSync(searchRoot).isDirectory()
  ) {
    const apks = findFilesByExt(searchRoot, ".apk").sort(
      (a, b) => scoreApk(a) - scoreApk(b)
    );
    for (const apkPath of apks) {
      const apktoolJar = normalizeSafePath(args.apktoolJar, { mustExist: true });
      const decoded = decodeApk(apkPath, apktoolJar);
      smaliList = findFilesByName(decoded, "InstrumentRepository.smali");
      if (smaliList.length > 0) {
        break;
      }
    }
  }

  if (smaliList.length === 0) {
    throw new Error("No InstrumentRepository.smali files found.");
  }

  const keys = {};
  for (const filePath of smaliList) {
    const safePath = normalizeSafePath(filePath, { mustExist: true });
    const text = fs.readFileSync(safePath, "utf8");
    for (const key of extractCandidates(text)) {
      keys[key] = keys[key] || [];
      keys[key].push(safePath);
    }
  }

  const key = selectKey(keys);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${key}\n`, "utf8");
  return {
    outputPath,
    inputPath: args.input ? path.resolve(args.input) : null,
  };
}

async function run() {
  const args = parseArgs(process.argv.slice(2));
  try {
    const result = await main(args);
    if (args.json) {
      console.log(
        JSON.stringify(
          {
            ok: true,
            outputPath: result.outputPath,
            inputPath: result.inputPath,
            alreadyPresent: Boolean(result.alreadyPresent),
          },
          null,
          0
        )
      );
    } else {
      if (result.alreadyPresent) {
        console.log(`Auth key already present at ${result.outputPath}`);
      } else {
        console.log(`Wrote auth key to ${result.outputPath}`);
      }
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    if (args.json) {
      console.log(JSON.stringify({ ok: false, error: message }, null, 0));
    } else {
      console.error(`error: ${message}`);
    }
    process.exit(1);
  }
}

run();
