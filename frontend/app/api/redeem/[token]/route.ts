import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.API_URL || 'http://backend:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ token: string }> }
) {
  const { token } = await params;
  
  try {
    // Forward the request headers for IP and user agent
    const forwardedFor = request.headers.get('x-forwarded-for') || request.ip || 'unknown';
    const userAgent = request.headers.get('user-agent') || 'unknown';

    const response = await fetch(`${API_URL}/api/redeem/${token}`, {
      method: 'GET',
      headers: {
        'X-Forwarded-For': forwardedFor,
        'User-Agent': userAgent,
      },
      cache: 'no-store',
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Redemption error:', error);
    return NextResponse.json(
      { detail: 'Verbindungsfehler. Bitte versuche es später erneut.' },
      { status: 500 }
    );
  }
}

