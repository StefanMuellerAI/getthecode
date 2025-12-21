import { NextResponse } from 'next/server';

const API_URL = process.env.API_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/jackpot`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Cache for 1 minute
      next: { revalidate: 60 },
    });

    if (!response.ok) {
      const error = await response.text();
      return NextResponse.json(
        { error: 'Jackpot request failed', details: error },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Jackpot API error:', error);
    
    // Return fallback data if backend is unavailable
    const startDate = new Date('2025-01-01');
    const now = new Date();
    const months = Math.max(1, 
      (now.getFullYear() - startDate.getFullYear()) * 12 + 
      (now.getMonth() - startDate.getMonth()) + 1
    );
    
    return NextResponse.json({
      amount: months * 100,
      months_active: months,
      start_date: '2025-01-01',
      currency: 'EUR'
    });
  }
}

