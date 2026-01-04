import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.API_URL || 'http://backend:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await fetch(`${API_URL}/api/verify-email-code`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Forwarded-For': request.headers.get('x-forwarded-for') || request.ip || 'unknown',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Verify email code error:', error);
    return NextResponse.json(
      { success: false, verified: false, message: 'Verbindungsfehler. Bitte versuche es später erneut.' },
      { status: 500 }
    );
  }
}

