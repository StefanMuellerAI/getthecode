import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.API_URL || 'http://localhost:8000';

interface ChallengeRequestBody {
  prompt: string;
  conversation_id?: string | null;
}

export async function POST(request: NextRequest) {
  try {
    const body: ChallengeRequestBody = await request.json();

    // SECURITY: Only forward prompt and conversation_id
    // Conversation history is stored server-side to prevent manipulation
    const requestBody: Record<string, string> = {
      prompt: body.prompt,
    };
    
    // Only include conversation_id if it exists
    if (body.conversation_id) {
      requestBody.conversation_id = body.conversation_id;
    }

    const response = await fetch(`${API_URL}/challenge`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const error = await response.text();
      return NextResponse.json(
        { error: 'Challenge request failed', details: error },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Challenge API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
