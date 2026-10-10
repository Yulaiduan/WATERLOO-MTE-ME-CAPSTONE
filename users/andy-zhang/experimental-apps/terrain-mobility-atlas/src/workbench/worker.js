import { simulateScenario } from './engine.js';
self.onmessage = ({ data }) => {
  try { self.postMessage({ id: data.id, result: simulateScenario(data.terrain, data.scenario, data.mechanism, data.actuator) }); }
  catch (error) { self.postMessage({ id: data.id, error: error instanceof Error ? error.message : String(error) }); }
};
