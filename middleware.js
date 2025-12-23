export const config = {
  matcher: ['/', '/index.html'],
};

export default function middleware(request) {
  const basicAuth = request.headers.get('authorization');

  if (basicAuth) {
    const authValue = basicAuth.split(' ')[1];
    const [user, pwd] = atob(authValue).split(':');

    // Hardcoded credentials for Edge Runtime
    // (process.env is unreliable in Vercel Edge Middleware)
    // TODO: Move to Vercel environment variables in dashboard once stable
    const validUser = 'schretzmeirp';
    const validPassword = 'Pauls007.';

    if (user === validUser && pwd === validPassword) {
      // If auth is correct, return nothing (allows the request to continue)
      return;
    }
  }

  // If not authorized, return 401
  return new Response('Auth required', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="Secure Area"',
    },
  });
}
