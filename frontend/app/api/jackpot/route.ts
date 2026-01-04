import { NextResponse } from 'next/server';

const API_URL = process.env.API_URL || 'http://localhost:8000';

// Force dynamic rendering - never cache this route
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/jackpot`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // No caching - always fetch fresh data
      cache: 'no-store',
    });

    if (!response.ok) {
      const error = await response.text();
      console.error('Jackpot backend error:', error);
      // Return safe fallback on error
      return NextResponse.json({
        amount: 0,
        months_active: 0,
        start_date: '2025-01-01',
        currency: 'EUR',
        code_count: 0,
        game_status: 'loading'
      }, {
        headers: {
          'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
        }
      });
    }

    const data = await response.json();
    return NextResponse.json(data, {
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
      }
    });
  } catch (error) {
    console.error('Jackpot API error:', error);
    
    // Return 0€ fallback when backend is unavailable - NOT calculated value
    return NextResponse.json({
      amount: 0,
      months_active: 0,
      start_date: '2025-01-01',
      currency: 'EUR',
      code_count: 0,
      game_status: 'loading'
    }, {
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
      }
    });
  }
}

