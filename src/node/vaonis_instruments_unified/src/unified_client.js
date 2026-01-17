import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROUTES_PATH = resolve(__dirname, "../data/http_routes_union.json");

export const DEFAULT_PREFIXES = ["", "/stellina/http", "/vespera/http"];

let routesCache = null;

const ANSI_RESET = "\x1b[0m";
const ANSI_BLUE = "\x1b[94m";
const ANSI_GREEN = "\x1b[92m";
const ANSI_CYAN = "\x1b[96m";
const ANSI_MAGENTA = "\x1b[95m";

/**
 * @typedef {Object} RouteDefinition
 * @property {string} operationId
 * @property {string} method
 * @property {string} path
 */

/**
 * @typedef {Object} RequestOptions
 * @property {string|null} [auth]
 * @property {Record<string, any>|null} [params]
 * @property {any} [jsonBody]
 * @property {any} [body]
 * @property {Record<string, string>} [headers]
 */

/**
 * @typedef {Object} DownloadImageOptions
 * @property {string|null} [auth]
 * @property {Record<string, string>} [headers]
 * @property {Record<string, any>|null} [params]
 */

/**
 * @typedef {Object} ClientOptions
 * @property {string} [host]
 * @property {number} [port]
 * @property {string} [apiBasePath]
 * @property {Iterable<string>} [prefixes]
 * @property {number} [timeoutMs]
 * @property {typeof fetch} [fetchImpl]
 * @property {{ log: (...args: any[]) => void }} [logger]
 * @property {boolean} [logResponses]
 * @property {boolean} [colorizeResponses]
 * @property {number} [logResponseLimit]
 */

/**
 * @returns {Map<string, RouteDefinition>}
 */
function loadRoutes() {
  if (routesCache) {
    return routesCache;
  }
  const data = JSON.parse(readFileSync(ROUTES_PATH, "utf-8"));
  routesCache = new Map(data.map((item) => [item.operationId, item]));
  return routesCache;
}

/**
 * @param {URL} url
 * @param {Record<string, any>|null|undefined} params
 * @returns {URL}
 */
function buildQuery(url, params) {
  if (!params) {
    return url;
  }
  for (const [key, value] of Object.entries(params)) {
    if (Array.isArray(value)) {
      for (const item of value) {
        url.searchParams.append(key, String(item));
      }
    } else if (value !== undefined && value !== null) {
      url.searchParams.set(key, String(value));
    }
  }
  return url;
}

/**
 * @param {Buffer} buffer
 * @param {string} contentType
 * @returns {boolean}
 */
function looksLikeImage(buffer, contentType) {
  if (contentType && contentType.toLowerCase().startsWith("image/")) {
    return true;
  }
  if (!buffer || buffer.length < 4) {
    return false;
  }
  if (buffer[0] === 0xff && buffer[1] === 0xd8 && buffer[2] === 0xff) {
    return true; // JPEG
  }
  if (buffer.slice(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))) {
    return true; // PNG
  }
  if (buffer.slice(0, 2).equals(Buffer.from("BM"))) {
    return true; // BMP
  }
  if (buffer.slice(0, 6).equals(Buffer.from("GIF87a")) || buffer.slice(0, 6).equals(Buffer.from("GIF89a"))) {
    return true; // GIF
  }
  if (buffer.slice(0, 4).equals(Buffer.from([0x49, 0x49, 0x2a, 0x00])) || buffer.slice(0, 4).equals(Buffer.from([0x4d, 0x4d, 0x00, 0x2a]))) {
    return true; // TIFF
  }
  if (buffer.length >= 12 && buffer.slice(0, 4).equals(Buffer.from("RIFF")) && buffer.slice(8, 12).equals(Buffer.from("WEBP"))) {
    return true; // WEBP
  }
  return false;
}

function colorizeJsonLine(line) {
  const match = line.match(/^(\s*)("[^"]+")(\s*:\s*)(.*)$/);
  if (!match) {
    return line;
  }
  const [, indent, key, sep, rest] = match;
  const keyColored = `${ANSI_BLUE}${key}${ANSI_RESET}`;
  let value = rest;
  const stringMatch = value.match(/^"[^"]*"/);
  if (stringMatch) {
    const token = stringMatch[0];
    value = `${ANSI_GREEN}${token}${ANSI_RESET}${value.slice(token.length)}`;
  } else {
    const numberMatch = value.match(/^-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?/);
    if (numberMatch) {
      const token = numberMatch[0];
      value = `${ANSI_CYAN}${token}${ANSI_RESET}${value.slice(token.length)}`;
    } else {
      const boolMatch = value.match(/^(true|false|null)\b/);
      if (boolMatch) {
        const token = boolMatch[0];
        value = `${ANSI_MAGENTA}${token}${ANSI_RESET}${value.slice(token.length)}`;
      }
    }
  }
  return `${indent}${keyColored}${sep}${value}`;
}

function colorizeJson(text) {
  return text.split("\n").map(colorizeJsonLine).join("\n");
}

function formatPayload(value, { color = false, maxLen = 4000 } = {}) {
  let rendered = "";
  if (Buffer.isBuffer(value)) {
    rendered = `<${value.length} bytes>`;
  } else if (value && typeof value === "object") {
    rendered = JSON.stringify(value, null, 2);
  } else if (typeof value === "string") {
    const trimmed = value.trim();
    if (trimmed) {
      try {
        const parsed = JSON.parse(trimmed);
        rendered = JSON.stringify(parsed, null, 2);
      } catch {
        rendered = value;
      }
    } else {
      rendered = value;
    }
  } else {
    rendered = String(value);
  }
  if (maxLen > 0 && rendered.length > maxLen) {
    rendered = `${rendered.slice(0, maxLen - 20)}... (truncated)`;
  }
  if (color) {
    return colorizeJson(rendered);
  }
  return rendered;
}

export class UnifiedHttpClient {
  /**
   * @param {ClientOptions} [options]
   */
  constructor({
    host = "10.0.0.1",
    port = 8082,
    apiBasePath = "/v1",
    prefixes = DEFAULT_PREFIXES,
    timeoutMs = 10000,
    fetchImpl = globalThis.fetch,
    logger = console,
    logResponses = true,
    colorizeResponses = true,
    logResponseLimit = 4000,
  } = {}) {
    if (!fetchImpl) {
      throw new Error("fetch is required (Node 18+ or provide fetchImpl)");
    }
    this.host = host;
    this.port = port;
    this.apiBasePath = apiBasePath;
    this.prefixes = Array.from(prefixes);
    this.timeoutMs = timeoutMs;
    this.fetch = fetchImpl;
    this.baseUrl = null;
    this.logger = logger;
    this.logResponses = logResponses;
    this.colorizeResponses = colorizeResponses;
    this.logResponseLimit = logResponseLimit;
  }

  /**
   * @returns {Promise<string>}
   */
  async detectBaseUrl() {
    for (const prefix of this.prefixes) {
      const candidate = this._makeBaseUrl(prefix);
      try {
        const response = await this._fetchWithTimeout(`${candidate}/app/status`, {
          method: "GET",
        });
        if (response.ok) {
          this.baseUrl = candidate;
          return candidate;
        }
      } catch {
        // Ignore and try next prefix.
      }
    }
    throw new Error("Unable to detect a working base URL");
  }

  /**
   * @param {string} method
   * @param {string} path
   * @param {RequestOptions} [options]
   * @returns {Promise<any>}
   */
  async request(
    method,
    path,
    { auth = null, params = null, jsonBody = undefined, body = undefined, headers = {} } = {}
  ) {
    const base = this.baseUrl || (await this.detectBaseUrl());
    const url = new URL(`${base.replace(/\/+$/, "")}/${path.replace(/^\//, "")}`);
    buildQuery(url, params);

    const resolvedHeaders = { ...headers };
    if (auth) {
      resolvedHeaders.Authorization = auth;
    }
    let resolvedBody = body;
    if (jsonBody !== undefined) {
      resolvedBody = JSON.stringify(jsonBody);
      if (!resolvedHeaders["Content-Type"]) {
        resolvedHeaders["Content-Type"] = "application/json";
      }
    }

    const response = await this._fetchWithTimeout(url.toString(), {
      method,
      headers: resolvedHeaders,
      body: resolvedBody,
    });

    const contentType = response.headers.get("content-type") || "";
    let payload;
    if (contentType.includes("application/json")) {
      payload = await response.json();
    } else {
      payload = await response.text();
    }

    if (this.logResponses) {
      const formatted = formatPayload(payload, {
        color: this.colorizeResponses,
        maxLen: this.logResponseLimit,
      });
      this.logger.log(`HTTP ${response.status} ${response.statusText}\n${formatted}`);
    }

    if (!response.ok) {
      const message = typeof payload === "string" ? payload : "";
      throw new Error(`HTTP ${response.status} ${response.statusText} ${message}`.trim());
    }
    return payload;
  }

  /**
   * @param {string} operationId
   * @param {RequestOptions} [options]
   * @returns {Promise<any>}
   */
  async callOperation(operationId, options = {}) {
    const route = loadRoutes().get(operationId);
    if (!route) {
      throw new Error(`Unknown operationId: ${operationId}`);
    }
    return this.request(route.method, route.path, options);
  }

  /**
   * @param {string} urlOrPath
   * @param {DownloadImageOptions} [options]
   * @returns {Promise<Buffer>}
   */
  async downloadImage(urlOrPath, { auth = null, headers = {}, params = null } = {}) {
    const base = this.baseUrl || (await this.detectBaseUrl());
    const fullUrl =
      urlOrPath.startsWith("http://") || urlOrPath.startsWith("https://")
        ? urlOrPath
        : `${base.replace(/\/+$/, "")}/${urlOrPath.replace(/^\//, "")}`;
    const url = new URL(fullUrl);
    buildQuery(url, params);

    const resolvedHeaders = { ...headers };
    if (auth) {
      resolvedHeaders.Authorization = auth;
    }
    const response = await this._fetchWithTimeout(url.toString(), {
      method: "GET",
      headers: resolvedHeaders,
    });
    const buffer = Buffer.from(await response.arrayBuffer());
    const contentType = response.headers.get("content-type") || "";
    if (this.logResponses) {
      const formatted = formatPayload(buffer, {
        color: false,
        maxLen: this.logResponseLimit,
      });
      this.logger.log(
        `HTTP ${response.status} ${response.statusText} image bytes=${formatted}`
      );
    }
    if (response.ok || looksLikeImage(buffer, contentType)) {
      return buffer;
    }
    throw new Error(`HTTP ${response.status} ${response.statusText}`.trim());
  }

  /**
   * @param {string} prefix
   * @returns {string}
   */
  _makeBaseUrl(prefix) {
    const raw = `http://${this.host}:${this.port}${prefix}${this.apiBasePath}`;
    return raw.replace(/\/+$/, "");
  }

  /**
   * @param {string} url
   * @param {RequestInit} options
   * @returns {Promise<Response>}
   */
  async _fetchWithTimeout(url, options) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.timeoutMs);
    try {
      return await this.fetch(url, { ...options, signal: controller.signal });
    } finally {
      clearTimeout(timeout);
    }
  }
}

export { loadRoutes };
