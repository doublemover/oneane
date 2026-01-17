import { schemas as schemaBundle } from './schemas.js';

/**
 * Full extracted schema bundle.
 *
 * @type {object}
 */
export const schemas = schemaBundle;

/**
 * Socket.IO events exposed by the instrument.
 */
export const events = schemaBundle.events;

/**
 * All extracted model definitions (bodies, responses, status DTOs, a few supporting libs).
 */
export const definitions = schemaBundle.definitions;

/**
 * Get the schema for a socket event name.
 *
 * @param {string} eventName
 * @returns {object | null}
 */
export function getEventSchema(eventName) {
  return schemaBundle.events?.[eventName] ?? null;
}

/**
 * Get a model definition by its fully-qualified dot name.
 *
 * Example: "com.vaonis.instruments.sdk.models.status.StellinaStatus"
 *
 * @param {string} dotName
 * @returns {object | null}
 */
export function getDefinition(dotName) {
  return schemaBundle.definitions?.[dotName] ?? null;
}

export default {
  schemas: schemaBundle,
  events,
  definitions,
  getEventSchema,
  getDefinition,
};
