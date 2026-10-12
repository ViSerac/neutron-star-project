var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// worker.js
var JSON_URL = "https://raw.githubusercontent.com/ViSerac/neutron-star-project/main/docs/data/NS_catalog_full.json";
var cachedCatalog = null;
var cacheTime = 0;
var CACHE_TTL = 3600 * 1e3;
async function getData(url, cached) {
  const now = Date.now();
  if (cached && now - cacheTime < CACHE_TTL)
    return cached;
  const res = await fetch(url);
  const json2 = await res.json();
  cacheTime = now;
  return Array.isArray(json2) ? json2 : json2.records || json2;
}
__name(getData, "getData");
function cors(response) {
  const headers = new Headers(response.headers);
  headers.set("Access-Control-Allow-Origin", "*");
  headers.set("Access-Control-Allow-Methods", "GET, OPTIONS");
  headers.set("Access-Control-Allow-Headers", "Content-Type");
  headers.set("Content-Type", "application/json");
  return new Response(response.body, { status: response.status, headers });
}
__name(cors, "cors");
function json(data, status = 200) {
  return cors(new Response(JSON.stringify(data), { status }));
}
__name(json, "json");
function separation(ra1, dec1, ra2, dec2) {
  const toRad = /* @__PURE__ */ __name((d) => d * Math.PI / 180, "toRad");
  const dDec = toRad(dec2 - dec1);
  const dRa = toRad(ra2 - ra1);
  const a = Math.sin(dDec / 2) ** 2 + Math.cos(toRad(dec1)) * Math.cos(toRad(dec2)) * Math.sin(dRa / 2) ** 2;
  return 2 * Math.asin(Math.sqrt(a)) * 180 / Math.PI;
}
__name(separation, "separation");
function raToDeg(ra) {
  if (ra == null)
    return null;
  const s = String(ra).trim();
  const parts = s.split(/\s+/);
  if (parts.length === 3) {
    const [h, m, sec] = parts.map(Number);
    return (h + m / 60 + sec / 3600) * 15;
  }
  return parseFloat(s);
}
__name(raToDeg, "raToDeg");
function decToDeg(dec) {
  if (dec == null)
    return null;
  const s = String(dec).trim();
  const parts = s.split(/\s+/);
  if (parts.length === 3) {
    const sign = s.startsWith("-") ? -1 : 1;
    const [d, m, sec] = parts.map((v) => Math.abs(parseFloat(v)));
    return sign * (d + m / 60 + sec / 3600);
  }
  return parseFloat(s);
}
__name(decToDeg, "decToDeg");
var worker_default = {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    if (request.method === "OPTIONS") {
      return cors(new Response(null, { status: 204 }));
    }
    if (path === "/" || path === "") {
      return json({
        name: "Neutron Star Project API",
        version: "1.0",
        endpoints: {
          "/search": "?name=<regex> \u2014 search by name",
          "/cone": "?ra=<deg>&dec=<deg>&radius=<deg> \u2014 cone search",
          "/object": "?name=<exact> \u2014 get single object",
          "/catalog": "?type=<type>&catalog=<ATNF|McGill|SIMBAD Magnificent Seven|SIMBAD CCOs>&galaxy=<milky_way|lmc|smc>&limit=<n>&offset=<n> \u2014 filtered catalog",
          "/types": "list all object types",
          "/stats": "catalog statistics"
        },
        source: "https://github.com/ViSerac/neutron-star-project",
        updated_weekly: true
      });
    }
    if (path === "/stats") {
      const data = await getData(JSON_URL, cachedCatalog);
      cachedCatalog = data;
      const types = {};
      const cats = {};
      for (const r of data) {
        types[r.type || "unknown"] = (types[r.type || "unknown"] || 0) + 1;
        cats[r.source_catalog || "unknown"] = (cats[r.source_catalog || "unknown"] || 0) + 1;
      }
      return json({ total: data.length, by_type: types, by_catalog: cats });
    }
    if (path === "/types") {
      const data = await getData(JSON_URL, cachedCatalog);
      cachedCatalog = data;
      const types = [...new Set(data.map((r) => r.type).filter(Boolean))].sort();
      return json({ types });
    }
    if (path === "/search") {
      const name = url.searchParams.get("name");
      if (!name)
        return json({ error: "name parameter required" }, 400);
      const data = await getData(JSON_URL, cachedCatalog);
      cachedCatalog = data;
      let pattern;
      try {
        pattern = new RegExp(name, "i");
      } catch {
        return json({ error: "invalid regex" }, 400);
      }
      const results = data.filter((r) => r.NS_NAME && pattern.test(r.NS_NAME));
      return json({ count: results.length, results });
    }
    if (path === "/object") {
      const name = url.searchParams.get("name");
      if (!name)
        return json({ error: "name parameter required" }, 400);
      const data = await getData(JSON_URL, cachedCatalog);
      cachedCatalog = data;
      const obj = data.find((r) => r.NS_NAME === name);
      if (!obj)
        return json({ error: "object not found" }, 404);
      return json(obj);
    }
    if (path === "/cone") {
      const ra = parseFloat(url.searchParams.get("ra"));
      const dec = parseFloat(url.searchParams.get("dec"));
      const radius = parseFloat(url.searchParams.get("radius") || "1.0");
      if (isNaN(ra) || isNaN(dec))
        return json({ error: "ra and dec required (degrees)" }, 400);
      const data = await getData(JSON_URL, cachedCatalog);
      cachedCatalog = data;
      const results = [];
      for (const r of data) {
        const raDeg = raToDeg(r.RAJ);
        const decDeg = decToDeg(r.DECJ);
        if (raDeg == null || decDeg == null)
          continue;
        const sep = separation(ra, dec, raDeg, decDeg);
        if (sep <= radius)
          results.push({ ...r, separation_deg: parseFloat(sep.toFixed(6)) });
      }
      results.sort((a, b) => a.separation_deg - b.separation_deg);
      return json({ count: results.length, ra, dec, radius_deg: radius, results });
    }
    if (path === "/catalog") {
      const type = url.searchParams.get("type");
      const catalog = url.searchParams.get("catalog");
      const limit = parseInt(url.searchParams.get("limit") || "100");
      const offset = parseInt(url.searchParams.get("offset") || "0");
      const galaxy = url.searchParams.get("galaxy");
      const data = await getData(JSON_URL, cachedCatalog);
      cachedCatalog = data;
      let results = data;
      if (type)
        results = results.filter((r) => r.type === type);
      if (catalog)
        results = results.filter((r) => r.source_catalog === catalog);
      if (galaxy)
        results = results.filter((r) => r.galaxy === galaxy);
      const total = results.length;
      results = results.slice(offset, offset + limit);
      return json({ total, offset, limit, count: results.length, results });
    }
    return json({ error: "endpoint not found" }, 404);
  }
};
export {
  worker_default as default
};
