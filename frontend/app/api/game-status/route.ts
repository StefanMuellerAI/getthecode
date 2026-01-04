import { NextResponse } from 'next/server';

const API_URL = process.env.API_URL || 'http://backend:8000';

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/api/game-status`, {
      cache: 'no-store',
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch game status' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Game status fetch error:', error);
    return NextResponse.json(
      { 
        status: 'unknown',
        jackpot_value: 0,
        code_count: 0,
        is_active: false,
        last_winner_at: null
      },
      { status: 200 }
    );
  }
}

