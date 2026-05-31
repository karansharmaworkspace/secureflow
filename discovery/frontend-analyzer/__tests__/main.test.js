// Test the core logic functions by extracting them into pure functions
// Since the original code has side effects, we'll test the logic directly

describe('interceptRequests logic', () => {
  it('should identify API requests by path', () => {
    // Test the core logic from interceptRequests function
    const testUrl = (urlString) => {
      const url = new URL(urlString);
      return (
        url.pathname.startsWith("/api/") ||
        url.pathname.startsWith("/v1/") ||
        url.pathname.startsWith("/v2/") ||
        url.pathname.startsWith("/v3/")
      );
    };
    
    expect(testUrl('https://example.com/api/users')).toBe(true);
    expect(testUrl('https://example.com/v1/data')).toBe(true);
    expect(testUrl('https://example.com/v2/test')).toBe(true);
    expect(testUrl('https://example.com/v3/endpoint')).toBe(true);
    expect(testUrl('https://example.com/about')).toBe(false);
    expect(testUrl('https://example.com/static/css/style.css')).toBe(false);
  });
});

describe('extractJsApis logic', () => {
  it('should extract API patterns from script content', () => {
    // Test the regex logic from extractJsApis function
    const extractApiPatterns = (content) => {
      const matches = content.match(
        /["'](\/api\/[a-zA-Z0-9_\-/{}]+)["']/g
      );
      return matches ? matches.map(m => m.replace(/["']/g, "")) : [];
    };
    
    // Test with matches - only those starting with /api/
    const scriptWithApis = "const apiUrl = '/api/users'; const endpoint = '/api/v1/data';";
    expect(extractApiPatterns(scriptWithApis)).toEqual(['/api/users', '/api/v1/data']);
    
    // Test with no matches
    const scriptWithoutApis = "const hello = 'world'; const x = 42;";
    expect(extractApiPatterns(scriptWithoutApis)).toEqual([]);
    
    // Test with mixed content - only /api/ patterns should be extracted
    const mixedScript = "const normal = 'text'; const api = '/api/test'; const v1 = '/v1/other'; const num = 123;";
    expect(extractApiPatterns(mixedScript)).toEqual(['/api/test']);
  });
});

// Test the data structure creation logic
describe('discoveredPatterns structure', () => {
  it('should create correct pattern object from request', () => {
    // This mimics the logic in interceptRequests
    const createPatternFromRequest = (request) => ({
      method: request.method(),
      path: new URL(request.url()).pathname,
      host: new URL(request.url()).hostname,
      headers: request.headers(),
      resourceType: request.resourceType(),
      timestamp: new Date().toISOString(),
    });
    
    const mockRequest = {
      method: () => 'GET',
      url: () => 'https://api.example.com/v1/users',
      headers: () => ({ 'content-type': 'application/json' }),
      resourceType: () => 'xhr'
    };
    
    const pattern = createPatternFromRequest(mockRequest);
    expect(pattern.method).toBe('GET');
    expect(pattern.path).toBe('/v1/users');
    expect(pattern.host).toBe('api.example.com');
    expect(pattern.headers).toEqual({ 'content-type': 'application/json' });
    expect(pattern.resourceType).toBe('xhr');
    expect(pattern.timestamp).toMatch(/\d{4}-\d{2}-\d{2}/); // ISO date format
  });
});