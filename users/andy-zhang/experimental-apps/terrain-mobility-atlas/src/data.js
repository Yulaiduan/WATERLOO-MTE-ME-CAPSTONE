// All terrain values and scenario boundaries below are illustrative assumptions.
// They are NOT derived from the geographic outline or remotely sensed elevation.
export const REGIONS = [
  { id: 'shield', name: 'Canadian Shield', location: 'Ontario & Québec, Canada', biome: 'Boreal forest', color: '#78a785', center: [-83, 51], polygon: [[-96,49],[-87,48],[-80,46],[-73,48],[-67,53],[-73,57],[-86,58],[-96,54]], terrain: { grade: 18, cross: 10, roughness: 85, obstacle: 170, spacing: 1.8, corridor: 1.5, surface: 'mixed' }, description: 'Rolling bedrock, forest corridors, and frequent small steps. A useful scenario for testing obstacle and roughness tradeoffs.' },
  { id: 'rockies', name: 'Rocky Mountains', location: 'Western North America', biome: 'Alpine', color: '#a6a197', center: [-114, 46], polygon: [[-124,54],[-119,57],[-113,52],[-108,45],[-105,38],[-110,36],[-115,43]], terrain: { grade: 32, cross: 19, roughness: 145, obstacle: 280, spacing: 0.9, corridor: 1.8, surface: 'mixed' }, description: 'A demanding alpine scenario. Steep approaches and closely spaced obstacles can combine to limit mobility.' },
  { id: 'plains', name: 'Great Plains', location: 'Central North America', biome: 'Grassland', color: '#b3b978', center: [-100, 41], polygon: [[-106,48],[-98,49],[-93,44],[-96,35],[-104,34]], terrain: { grade: 8, cross: 5, roughness: 35, obstacle: 65, spacing: 3.5, corridor: 4, surface: 'mixed' }, description: 'Open, gently rolling grassland. This scenario has generous clearance and few large obstacles.' },
  { id: 'appalachia', name: 'Appalachian Forest', location: 'Eastern United States', biome: 'Temperate forest', color: '#89a97b', center: [-80, 39], polygon: [[-85,35],[-82,34],[-77,38],[-72,44],[-77,44],[-82,40]], terrain: { grade: 16, cross: 9, roughness: 65, obstacle: 120, spacing: 1.5, corridor: 1.0, surface: 'mixed' }, description: 'A narrow forest-corridor scenario for exploring vehicle width and clearance tradeoffs.' },
  { id: 'amazon', name: 'Amazon Basin', location: 'Northern South America', biome: 'Tropical forest', color: '#527f69', center: [-62, -5], polygon: [[-74,1],[-65,3],[-51,-2],[-49,-9],[-61,-14],[-73,-10]], terrain: { grade: 12, cross: 8, roughness: 110, obstacle: 240, spacing: 0.7, corridor: 0.85, surface: 'soft' }, description: 'An illustrative wet-forest scenario with confined corridors and soft ground. Land cover alone cannot establish these conditions.' },
  { id: 'andes', name: 'Andean Highlands', location: 'Western South America', biome: 'Alpine', color: '#a6a197', center: [-70, -24], polygon: [[-78,-7],[-74,-9],[-66,-22],[-68,-36],[-73,-38],[-75,-24]], terrain: { grade: 38, cross: 24, roughness: 170, obstacle: 340, spacing: 0.6, corridor: 1.3, surface: 'mixed' }, description: 'High-gradient mountain terrain with narrow passages and frequent steps.' },
  { id: 'patagonia', name: 'Patagonian Steppe', location: 'Southern Argentina', biome: 'Grassland', color: '#b3b978', center: [-67,-44], polygon: [[-70,-38],[-64,-39],[-65,-47],[-69,-51],[-72,-47]], terrain: { grade: 14, cross: 8, roughness: 55, obstacle: 95, spacing: 2.5, corridor: 3.5, surface: 'mixed' }, description: 'An open steppe scenario with moderate roughness and ample lateral clearance.' },
  { id: 'sahara', name: 'Sahara', location: 'Northern Africa', biome: 'Desert', color: '#cfb67b', center: [12,25], polygon: [[-14,26],[-8,31],[12,32],[31,27],[30,19],[13,17],[-5,20]], terrain: { grade: 20, cross: 12, roughness: 45, obstacle: 70, spacing: 3, corridor: 5, surface: 'loose' }, description: 'Loose-sand scenario. Surface capability is an assumption; it does not calculate traction or sinkage.' },
  { id: 'congo', name: 'Congo Basin', location: 'Central Africa', biome: 'Tropical forest', color: '#527f69', center: [23,-2], polygon: [[13,3],[24,5],[30,1],[28,-8],[17,-9],[12,-3]], terrain: { grade: 14, cross: 8, roughness: 100, obstacle: 230, spacing: 0.8, corridor: 0.95, surface: 'soft' }, description: 'Dense, wet forest scenario. Closely spaced obstacles and clearance dominate the assumed envelope.' },
  { id: 'savanna', name: 'East African Savanna', location: 'Kenya & Tanzania', biome: 'Savanna', color: '#b3b978', center: [36,-4], polygon: [[32,3],[39,1],[40,-6],[35,-12],[30,-8]], terrain: { grade: 12, cross: 7, roughness: 60, obstacle: 100, spacing: 2.3, corridor: 3, surface: 'mixed' }, description: 'Open savanna with moderate undulations. All values are synthetic screening inputs.' },
  { id: 'europe', name: 'Central European Lowlands', location: 'Central Europe', biome: 'Temperate forest', color: '#89a97b', center: [15,51], polygon: [[3,49],[10,55],[24,55],[30,49],[21,47],[10,47]], terrain: { grade: 10, cross: 6, roughness: 40, obstacle: 80, spacing: 2.5, corridor: 2.2, surface: 'hard' }, description: 'A simplified maintained-corridor scenario. It does not represent access permissions or every surface in this region.' },
  { id: 'scandinavia', name: 'Scandinavian Boreal', location: 'Northern Europe', biome: 'Boreal forest', color: '#78a785', center: [23,65], polygon: [[12,59],[19,70],[29,70],[32,64],[24,59]], terrain: { grade: 20, cross: 12, roughness: 95, obstacle: 195, spacing: 1.2, corridor: 1.5, surface: 'mixed' }, description: 'An assumed boreal rock-and-root scenario. Snow and seasonal soil changes are outside this screening model.' },
  { id: 'siberia', name: 'Siberian Taiga', location: 'Northern Asia', biome: 'Boreal forest', color: '#78a785', center: [95,59], polygon: [[46,57],[67,65],[109,64],[137,59],[128,52],[91,53],[61,51]], terrain: { grade: 15, cross: 8, roughness: null, obstacle: null, spacing: null, corridor: null, surface: 'mixed' }, description: 'An intentionally incomplete scenario demonstrating how missing critical terrain evidence is handled.' },
  { id: 'himalaya', name: 'Himalayan Range', location: 'South & Central Asia', biome: 'Alpine', color: '#a6a197', center: [85,30], polygon: [[72,34],[80,36],[94,31],[99,27],[89,26],[79,29]], terrain: { grade: 42, cross: 28, roughness: 190, obstacle: 380, spacing: 0.45, corridor: 1.1, surface: 'mixed' }, description: 'A highly demanding mountain scenario; it is not a measurement of Himalayan trails.' },
  { id: 'australia', name: 'Australian Interior', location: 'Central Australia', biome: 'Desert', color: '#cfb67b', center: [134,-25], polygon: [[119,-21],[129,-18],[140,-21],[143,-29],[133,-33],[122,-29]], terrain: { grade: 10, cross: 5, roughness: 45, obstacle: 80, spacing: 3.2, corridor: 5, surface: 'loose' }, description: 'Open, loose-ground scenario. Softness and traction remain assumed rather than calculated.' },
  { id: 'tundra', name: 'Alaskan Tundra', location: 'Alaska, United States', biome: 'Tundra', color: '#8ca6ac', center: [-151,66], polygon: [[-165,65],[-156,70],[-142,69],[-143,63],[-156,62]], terrain: { grade: 10, cross: 7, roughness: 80, obstacle: 130, spacing: 2, corridor: 3, surface: 'soft' }, description: 'A soft-ground tundra scenario. Seasonal freezing and snow are not modeled.' },
];

function contains(point, polygon) {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [x, y] = polygon[i], [px, py] = polygon[j];
    if ((y > point[1]) !== (py > point[1]) && point[0] < (px - x) * (point[1] - y) / (py - y) + x) inside = !inside;
  }
  return inside;
}
export function polygonArea(ring) {
  let sum = 0;
  for (let i = 0; i < ring.length - 1; i++) {
    sum += (ring[i + 1][0] - ring[i][0]) * Math.PI / 180 * (2 + Math.sin(ring[i][1] * Math.PI / 180) + Math.sin(ring[i + 1][1] * Math.PI / 180));
  }
  return Math.abs(sum) * 6371.0088 ** 2 / 2;
}
export const CELLS = [];
for (const region of REGIONS) {
  const xs = region.polygon.map(p => p[0]), ys = region.polygon.map(p => p[1]);
  let row = 0;
  for (let y = Math.min(...ys); y <= Math.max(...ys); y += 1.72, row++) {
    for (let x = Math.min(...xs) + (row % 2 ? 1 : 0); x <= Math.max(...xs); x += 2) {
      if (!contains([x, y], region.polygon)) continue;
      const ring = Array.from({ length: 6 }, (_, i) => {
        const angle = (30 + i * 60) * Math.PI / 180;
        return [x + 1.12 * Math.cos(angle), y + 1.12 * Math.sin(angle)];
      });
      ring.push(ring[0]);
      const seed = Math.sin(x * 17.4 + y * 31.8) * 43758.5453;
      const variation = 0.72 + (seed - Math.floor(seed)) * 0.52;
      const terrain = Object.fromEntries(Object.entries(region.terrain).map(([key, val]) => [key, typeof val === 'number' ? ['spacing', 'corridor'].includes(key) ? Math.round(val / variation * 100) / 100 : Math.round(val * variation) : val]));
      CELLS.push({ id: CELLS.length, region: region.id, center: [x, y], geometry: { type: 'Polygon', coordinates: [ring] }, area: polygonArea(ring), terrain });
    }
  }
}
export const REGION_FEATURES = { type: 'FeatureCollection', features: REGIONS.map(r => ({ type: 'Feature', properties: { id: r.id }, geometry: { type: 'Polygon', coordinates: [[...r.polygon, r.polygon[0]]] } })) };
export function defaultCell(regionId) {
  const region = REGIONS.find(r => r.id === regionId);
  return CELLS.filter(c => c.region === regionId).sort((a, b) => Math.hypot(a.center[0] - region.center[0], a.center[1] - region.center[1]) - Math.hypot(b.center[0] - region.center[0], b.center[1] - region.center[1]))[0];
}
