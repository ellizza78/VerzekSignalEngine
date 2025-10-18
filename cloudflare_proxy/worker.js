/**
 * Cloudflare Workers Proxy for Exchange API Routing
 * Provides static IP address for Binance/Bybit/Phemex/Coinexx IP whitelisting
 * 
 * Deploy this to Cloudflare Workers to get a consistent egress IP address
 */

// ============================================
// CONFIGURATION
// ============================================

const ALLOWED_EXCHANGES = [
  'fapi.binance.com',
  'testnet.binancefuture.com',
  'api.binance.com',
  'api.bybit.com',
  'api-testnet.bybit.com',
  'api.phemex.com',
  'testnet-api.phemex.com',
  'api.coinexx.com'
];

// Security: HMAC signature verification
const PROXY_SECRET_KEY = 'YOUR_PROXY_SECRET_KEY_HERE'; // Set in Cloudflare Workers environment

// ============================================
// CORS HEADERS
// ============================================

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, X-Proxy-Signature, X-Exchange-Host',
};

// ============================================
// HMAC SIGNATURE VERIFICATION
// ============================================

async function verifySignature(request, body) {
  const signature = request.headers.get('X-Proxy-Signature');
  if (!signature) {
    return false;
  }

  // Compute expected signature: HMAC-SHA256(secret, body)
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(PROXY_SECRET_KEY),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );

  const bodyText = body || '';
  const expectedSignature = await crypto.subtle.sign(
    'HMAC',
    key,
    encoder.encode(bodyText)
  );

  const expectedHex = Array.from(new Uint8Array(expectedSignature))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');

  return signature === expectedHex;
}

// ============================================
// EXCHANGE ROUTING
// ============================================

function isAllowedExchange(host) {
  return ALLOWED_EXCHANGES.includes(host);
}

async function proxyToExchange(request, exchangeHost, path, queryParams) {
  // Validate exchange
  if (!isAllowedExchange(exchangeHost)) {
    return new Response(
      JSON.stringify({ error: 'Unauthorized exchange host' }),
      { status: 403, headers: { 'Content-Type': 'application/json' } }
    );
  }

  // Build target URL
  const targetUrl = `https://${exchangeHost}${path}${queryParams ? '?' + queryParams : ''}`;

  // Forward request with original headers (except proxy-specific ones)
  const headers = new Headers(request.headers);
  headers.delete('X-Proxy-Signature');
  headers.delete('X-Exchange-Host');
  headers.set('Host', exchangeHost);

  const proxyRequest = new Request(targetUrl, {
    method: request.method,
    headers: headers,
    body: request.method !== 'GET' && request.method !== 'HEAD' ? await request.clone().arrayBuffer() : null,
  });

  try {
    const response = await fetch(proxyRequest);
    
    // Clone response and add CORS headers
    const responseHeaders = new Headers(response.headers);
    Object.keys(corsHeaders).forEach(key => {
      responseHeaders.set(key, corsHeaders[key]);
    });

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    return new Response(
      JSON.stringify({ error: 'Proxy request failed', details: error.message }),
      { 
        status: 502,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      }
    );
  }
}

// ============================================
// MAIN HANDLER
// ============================================

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);

  // Handle CORS preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  // Health check endpoint
  if (url.pathname === '/health') {
    return new Response(
      JSON.stringify({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'VerzekAutoTrader Exchange Proxy'
      }),
      { 
        status: 200,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      }
    );
  }

  // Get egress IP endpoint (for whitelisting reference)
  if (url.pathname === '/ip') {
    // Cloudflare provides CF-Connecting-IP header
    const ip = request.headers.get('CF-Connecting-IP') || 'Unknown';
    return new Response(
      JSON.stringify({
        egress_ip: 'Contact Cloudflare Support for static egress IP',
        note: 'Cloudflare Workers use shared egress IPs. For dedicated IP, upgrade to Enterprise plan.',
        connecting_ip: ip,
        timestamp: new Date().toISOString()
      }),
      { 
        status: 200,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      }
    );
  }

  // Proxy endpoint: /proxy
  if (url.pathname === '/proxy') {
    const exchangeHost = request.headers.get('X-Exchange-Host');
    const targetPath = url.searchParams.get('path') || '/';
    
    if (!exchangeHost) {
      return new Response(
        JSON.stringify({ error: 'Missing X-Exchange-Host header' }),
        { 
          status: 400,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        }
      );
    }

    // Get request body for signature verification
    const bodyText = request.method !== 'GET' && request.method !== 'HEAD' 
      ? await request.clone().text() 
      : '';

    // Verify HMAC signature
    const isValid = await verifySignature(request, bodyText);
    if (!isValid) {
      return new Response(
        JSON.stringify({ error: 'Invalid or missing X-Proxy-Signature header' }),
        { 
          status: 401,
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        }
      );
    }

    // Extract query params (excluding 'path')
    const queryParams = new URLSearchParams(url.search);
    queryParams.delete('path');
    const queryString = queryParams.toString();

    return proxyToExchange(request, exchangeHost, targetPath, queryString);
  }

  // Default: 404
  return new Response(
    JSON.stringify({ 
      error: 'Not found',
      endpoints: {
        '/health': 'Health check',
        '/ip': 'Get egress IP information',
        '/proxy?path=/endpoint': 'Proxy to exchange (requires X-Exchange-Host header)'
      }
    }),
    { 
      status: 404,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    }
  );
}
