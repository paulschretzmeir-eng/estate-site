export const config = {
  matcher: ['/', '/index.html'],
};

export default function middleware(request) {
  const header = request.headers.get('authorization') || '';

  // Minimal debug logging to trace auth flow
  console.log('[edge] middleware invoked');
  if (header) console.log('[edge] auth header present');

  const parts = header.split(' ');
  const scheme = parts[0] || '';
  const encoded = parts[1] || '';

  if (scheme.toLowerCase() === 'basic' && encoded) {
    try {
      const decoded = atob(encoded);
      const sepIndex = decoded.indexOf(':');
      const user = sepIndex >= 0 ? decoded.slice(0, sepIndex) : decoded;
      const pwd = sepIndex >= 0 ? decoded.slice(sepIndex + 1) : '';

      // Hardcoded credentials for Edge Runtime (temporary)
      const validUser = 'schretzmeirp';
      const validPassword = 'Pauls007.';

      const userMatch = user === validUser;
      const pwdMatch = pwd === validPassword;
      console.log(`[edge] user match: ${userMatch}, pwd match: ${pwdMatch}`);

      if (userMatch && pwdMatch) {
        console.log('[edge] auth success, allowing request');
        // Return nothing to allow the request to continue
        return;
      }
      console.warn('[edge] auth failed: credentials mismatch');
    } catch (e) {
      console.error('[edge] auth decode error:', e);
    }
  } else {
    if (header) console.warn('[edge] unsupported auth scheme');
    else console.log('[edge] no auth header');
  }

  // Challenge the client for Basic Auth
  return new Response('Auth required', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="Secure Area"',
    },
  });
}
