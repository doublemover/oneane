import io from "socket.io-client";

/**
 * @typedef {Object} SocketClientOptions
 * @property {string} [url]
 * @property {string} [path]
 * @property {string} [deviceId]
 * @property {string} [name]
 * @property {string} [countryCode]
 * @property {boolean} [autoConnect]
 * @property {Record<string, any>} [socketOptions]
 */

/**
 * @typedef {Object} SystemTimeOptions
 * @property {boolean} [useObject]
 */

export class VaonisSocketClient {
  /**
   * @param {SocketClientOptions} [options]
   */
  constructor({
    url = "http://10.0.0.1:8083",
    path = "/socket.io",
    deviceId = "",
    name = "",
    countryCode = "",
    autoConnect = false,
    socketOptions = {},
  } = {}) {
    this.url = url;
    this.path = path.startsWith("/") ? path : `/${path}`;
    this.deviceId = deviceId;
    this.name = name;
    this.countryCode = countryCode;
    this.socket = io(this.url, {
      path: this.path,
      query: {
        id: this.deviceId,
        name: this.name,
        countryCode: this.countryCode,
      },
      autoConnect,
      ...socketOptions,
    });
  }

  /**
   * @param {(payload: any) => void} handler
   */
  onStatusUpdated(handler) {
    this.socket.on("STATUS_UPDATED", handler);
  }

  /**
   * @param {(payload: any) => void} handler
   */
  onControlError(handler) {
    this.socket.on("CONTROL_ERROR", handler);
  }

  /**
   * @param {(...args: any[]) => void} handler
   */
  onConnect(handler) {
    this.socket.on("connect", handler);
  }

  /**
   * @param {(...args: any[]) => void} handler
   */
  onDisconnect(handler) {
    this.socket.on("disconnect", handler);
  }

  /**
   * @param {(...args: any[]) => void} handler
   */
  onReconnect(handler) {
    this.socket.on("reconnect", handler);
  }

  /**
   * @param {(...args: any[]) => void} handler
   */
  onError(handler) {
    this.socket.on("error", handler);
  }

  /**
   * @param {(...args: any[]) => void} handler
   */
  onConnectError(handler) {
    this.socket.on("connect_error", handler);
  }

  /**
   * @param {string} event
   * @param {(...args: any[]) => void} handler
   */
  onEvent(event, handler) {
    this.socket.on(event, handler);
  }

  /**
   * @returns {void}
   */
  connect() {
    this.socket.connect();
  }

  /**
   * @returns {void}
   */
  disconnect() {
    this.socket.disconnect();
  }

  /**
   * @param {string} command
   * @param {any} [payload]
   * @param {(...args: any[]) => void} [callback]
   * @returns {void}
   */
  sendCommand(command, payload = undefined, callback = undefined) {
    const data = payload === undefined ? [command] : [command, payload];
    if (callback) {
      this.socket.emit("message", data, callback);
    } else {
      this.socket.emit("message", data);
    }
  }

  /**
   * @param {string|null} [userId]
   * @returns {void}
   */
  takeControl(userId = null) {
    const payload = userId ? { userId } : undefined;
    this.sendCommand("takeControl", payload);
  }

  /**
   * @param {string|null} [userId]
   * @returns {void}
   */
  releaseControl(userId = null) {
    const payload = userId ? { userId } : undefined;
    this.sendCommand("releaseControl", payload);
  }

  /**
   * @param {number} epochMs
   * @param {SystemTimeOptions} [options]
   * @returns {void}
   */
  setSystemTime(epochMs, { useObject = false } = {}) {
    const payload = useObject ? { timestamp: Number(epochMs) } : Number(epochMs);
    this.sendCommand("setSystemTime", payload);
  }

  /**
   * @param {string|null} [userName]
   * @returns {void}
   */
  setUserName(userName = null) {
    const payload = {
      device: this.deviceId,
      user: userName ?? "null",
    };
    this.sendCommand("setUserName", payload);
  }

  /**
   * @param {(...args: any[]) => void} [callback]
   * @returns {void}
   */
  getStatus(callback = undefined) {
    this.sendCommand("getStatus", undefined, callback);
  }

  /**
   * @param {(...args: any[]) => void} [callback]
   * @returns {void}
   */
  restartApp(callback = undefined) {
    this.sendCommand("restartApp", undefined, callback);
  }

  /**
   * @param {(...args: any[]) => void} [callback]
   * @returns {void}
   */
  shutdown(callback = undefined) {
    this.sendCommand("shutdown", undefined, callback);
  }
}

export const StellinaSocketV2Client = VaonisSocketClient;
