export const config = {
  matcher: ['/', '/index.html'],
};

export default function middleware(request) {
  const basicAuth = request.headers.get('authorization');

  if (basicAuth) {
    const authValue = basicAuth.split(' ')[1];
    const [user, pwd] = atob(authValue).split(':');

    // Check against environment variables
    if (user === 'schretzmeirp' && pwd === process.env.BASIC_AUTH_PASSWORD) {
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
