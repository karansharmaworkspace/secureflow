const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const TARGET_URL = process.env.TARGET_URL || "https://bank.example.com";
const OUTPUT_DIR = process.env.OUTPUT_DIR || "/opt/discovery/output";

const discoveredEndpoints = new Set();
const discoveredPatterns = [];

async function interceptRequests(page) {
  await page.route("**/*", (route) => {
    const request = route.request();
    const url = new URL(request.url());

    if (
      url.pathname.startsWith("/api/") ||
      url.pathname.startsWith("/v1/") ||
      url.pathname.startsWith("/v2/") ||
      url.pathname.startsWith("/v3/")
    ) {
      const endpoint = `${request.method()} ${url.pathname}`;
      if (!discoveredEndpoints.has(endpoint)) {
        discoveredEndpoints.add(endpoint);
        discoveredPatterns.push({
          method: request.method(),
          path: url.pathname,
          host: url.hostname,
          headers: request.headers(),
          resourceType: request.resourceType(),
          timestamp: new Date().toISOString(),
        });
      }
    }

    route.continue();
  });
}

async function extractJsApis(page) {
  const apiPatterns = await page.evaluate(() => {
    const patterns = [];
    const scriptContents = document.querySelectorAll("script:not([src])");
    scriptContents.forEach((script) => {
      const content = script.textContent || "";
      const matches = content.match(
        /["'](\/api\/[a-zA-Z0-9_\-/{}]+)["']/g
      );
      if (matches) {
        matches.forEach((m) => patterns.push(m.replace(/["']/g, "")));
      }
    });
    return patterns;
  });

  apiPatterns.forEach((pattern) => {
    const endpoint = `GET ${pattern}`;
    if (!discoveredEndpoints.has(endpoint)) {
      discoveredEndpoints.add(endpoint);
      discoveredPatterns.push({
        method: "GET",
        path: pattern,
        source: "static-analysis",
        timestamp: new Date().toISOString(),
      });
    }
  });
}

async function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ZombieDiscovery/1.0",
  });
  const page = await context.newPage();

  await interceptRequests(page);

  await page.goto(TARGET_URL, { waitUntil: "networkidle", timeout: 30000 });

  const links = await page.$$eval("a[href]", (as) =>
    as.map((a) => a.href).filter((h) => h.startsWith(window.location.origin))
  );

  for (const link of links.slice(0, 20)) {
    try {
      await page.goto(link, { waitUntil: "networkidle", timeout: 15000 });
      await extractJsApis(page);
    } catch (e) {
      // skip failed navigations
    }
  }

  const catalog = {
    apiVersion: "backstage.io/v1alpha1",
    kind: "Location",
    metadata: {
      name: "discovered-apis",
      annotations: {
        "zombie-platform/discovery-method": "frontend-static-analysis",
        "zombie-platform/discovery-date": new Date().toISOString(),
      },
    },
    spec: {
      targets: discoveredPatterns.map((p, i) => `./api-${i}.yaml`),
    },
  };

  discoveredPatterns.forEach((p, i) => {
    const apiEntity = {
      apiVersion: "backstage.io/v1alpha1",
      kind: "API",
      metadata: {
        name: `discovered-${i}`,
        annotations: {
          "zombie-platform/path": p.path,
          "zombie-platform/method": p.method,
          "zombie-platform/host": p.host || TARGET_URL,
          "zombie-platform/source": p.source || "xhr-intercept",
        },
      },
      spec: {
        type: "discovered-api",
        lifecycle: "unknown",
        owner: "platform-engineering",
        definition: `${p.method} ${p.path}`,
      },
    };
    fs.writeFileSync(
      path.join(OUTPUT_DIR, `api-${i}.yaml`),
      JSON.stringify(apiEntity, null, 2)
    );
  });

  fs.writeFileSync(
    path.join(OUTPUT_DIR, "catalog-info.yaml"),
    JSON.stringify(catalog, null, 2)
  );

  console.log(
    `Discovered ${discoveredPatterns.length} API endpoints from ${TARGET_URL}`
  );
  console.log(JSON.stringify(discoveredPatterns, null, 2));

  await browser.close();
}

main().catch(console.error);
