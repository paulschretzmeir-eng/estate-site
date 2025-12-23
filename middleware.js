import { NextResponse } from 'next/server';

/**
 * Middleware for Vercel Edge: Basic Authentication
 * 
 * Protects private EstateGPT frontend with username/password
 * Configuration via environment variables:
 * - BASIC_AUTH_USER (default: 'admin')
 * - BASIC_AUTH_PASSWORD (default: 'password123')
 * 
 * Usage: Add to vercel.json or configure in Vercel dashboard
 */

export function middleware(request) {
  // Only apply auth to API routes and specific paths
  // Adjust the pathname pattern as needed
  const { pathname } = request.nextUrl;
  
  // Skip authentication for public assets
  if (pathname.startsWith('/_next') || pathname.startsWith('/public')) {
    return NextResponse.next();
  }

  // Get credentials from environment variables
  const basicAuthUser = process.env.BASIC_AUTH_USER || 'admin';
  const basicAuthPassword = process.env.BASIC_AUTH_PASSWORD || 'password123';

  // Check for Authorization header
  const authHeader = request.headers.get('authorization');

  if (!authHeader || !authHeader.startsWith('Basic ')) {
    // Return 401 Unauthorized with WWW-Authenticate challenge
    return new NextResponse('Unauthorized', {
      status: 401,
      headers: {
        'WWW-Authenticate': 'Basic realm="EstateGPT - Private Deployment"',
      },
    });
  }

  // Decode the Base64 credentials
  const credentials = atob(authHeader.slice(6));
  const [username, password] = credentials.split(':');

  // Validate credentials
  if (username === basicAuthUser && password === basicAuthPassword) {
    // Credentials are valid, proceed to next middleware or route
    return NextResponse.next();
  }

  // Invalid credentials
  return new NextResponse('Unauthorized', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="EstateGPT - Private Deployment"',
    },
  });
}

// Configure which routes this middleware applies to
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public).*)',
  ],
};
