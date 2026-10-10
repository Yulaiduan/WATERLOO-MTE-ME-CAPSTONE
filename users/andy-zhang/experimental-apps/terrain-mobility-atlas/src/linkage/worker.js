import { runSimulation, localStability, workspace, prescribedMotion } from './model.js';

self.onmessage = event => {
  const { id, type, config, mode, count } = event.data;
  try {
    let result;
    if (type === 'simulate') result = runSimulation(mode ? { ...config, simulation: { ...config.simulation, mode } } : config);
    else if (type === 'stability') result = localStability(config, mode);
    else if (type === 'workspace') result = workspace(config, count);
    else if (type === 'prescribed') result = prescribedMotion(config);
    else throw new Error(`Unknown worker request: ${type}`);
    self.postMessage({ id, type, result });
  } catch (error) {
    self.postMessage({ id, type, error: error instanceof Error ? error.message : String(error) });
  }
};
