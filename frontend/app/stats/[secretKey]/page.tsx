'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

interface StatsOverview {
  total_conversations: number;
  total_messages: number;
  conversations_with_leaks: number;
  messages_code_detected: number;
  referee_stops: number;
  recent_conversations_24h: number;
}

interface ConversationSummary {
  id: string;
  created_at: string | null;
  last_message_at: string | null;
  message_count: number;
  has_code_leak: boolean;
}

interface Message {
  id: number;
  role: string;
  content: string;
  sanitized_content: string | null;
  referee2_decision: string | null;
  referee2_reasoning: string | null;
  referee3_decision: string | null;
  referee3_reasoning: string | null;
  code_detected: boolean;
  detection_method: string | null;
  created_at: string | null;
}

interface GiftCode {
  id: number;
  code: string;
  value: number;
  added_at: string | null;
  burned_at: string | null;
  winner_conversation_id: string | null;
  is_available: boolean;
}

interface Claim {
  id: number;
  conversation_id: string;
  claimed_code: string;
  linkedin_profile: string | null;
  claim_message: string | null;
  ip_address: string | null;
  created_at: string | null;
  status: string;
  reviewed_at: string | null;
  reviewed_by: string | null;
  review_notes: string | null;
}

interface GameStatus {
  status: string;
  jackpot_value: number;
  code_count: number;
  last_winner_conversation_id: string | null;
  last_win_at: string | null;
}

type TabType = 'conversations' | 'codes' | 'claims' | 'status';

export default function StatsPage() {
  const params = useParams();
  const secretKey = params.secretKey as string;

  const [overview, setOverview] = useState<StatsOverview | null>(null);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [onlyLeaks, setOnlyLeaks] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  
  // New state for Gift Codes and Claims
  const [activeTab, setActiveTab] = useState<TabType>('conversations');
  const [giftCodes, setGiftCodes] = useState<GiftCode[]>([]);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [gameStatus, setGameStatus] = useState<GameStatus | null>(null);
  const [newCode, setNewCode] = useState({ code: '', value: 100 });
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [redemptionModal, setRedemptionModal] = useState<{ url: string; message: string } | null>(null);

  const fetchOverview = useCallback(async () => {
    try {
      const res = await fetch(`/api/stats/${secretKey}/overview`);
      if (!res.ok) {
        if (res.status === 404) {
          setError('Zugang verweigert');
          return;
        }
        throw new Error('Failed to fetch overview');
      }
      const data = await res.json();
      setOverview(data);
    } catch (err) {
      console.error('Error fetching overview:', err);
      setError('Fehler beim Laden der Statistiken');
    }
  }, [secretKey]);

  const fetchConversations = useCallback(async () => {
    try {
      const res = await fetch(`/api/stats/${secretKey}/conversations?only_leaks=${onlyLeaks}`);
      if (!res.ok) throw new Error('Failed to fetch conversations');
      const data = await res.json();
      setConversations(data.conversations);
    } catch (err) {
      console.error('Error fetching conversations:', err);
    }
  }, [secretKey, onlyLeaks]);

  const fetchMessages = useCallback(async (conversationId: string) => {
    setLoadingMessages(true);
    try {
      const res = await fetch(`/api/stats/${secretKey}/conversation/${conversationId}`);
      if (!res.ok) throw new Error('Failed to fetch messages');
      const data = await res.json();
      setMessages(data.messages);
    } catch (err) {
      console.error('Error fetching messages:', err);
      setMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  }, [secretKey]);

  const fetchGiftCodes = useCallback(async () => {
    try {
      const res = await fetch(`/api/stats/${secretKey}/codes`);
      if (!res.ok) throw new Error('Failed to fetch gift codes');
      const data = await res.json();
      setGiftCodes(data.codes);
    } catch (err) {
      console.error('Error fetching gift codes:', err);
    }
  }, [secretKey]);

  const fetchClaims = useCallback(async () => {
    try {
      const res = await fetch(`/api/stats/${secretKey}/claims`);
      if (!res.ok) throw new Error('Failed to fetch claims');
      const data = await res.json();
      setClaims(data.claims);
    } catch (err) {
      console.error('Error fetching claims:', err);
    }
  }, [secretKey]);

  const fetchGameStatus = useCallback(async () => {
    try {
      const res = await fetch(`/api/stats/${secretKey}/game-status`);
      if (!res.ok) throw new Error('Failed to fetch game status');
      const data = await res.json();
      setGameStatus(data);
    } catch (err) {
      console.error('Error fetching game status:', err);
    }
  }, [secretKey]);

  const addGiftCode = async () => {
    if (!newCode.code.trim()) return;
    setActionLoading('add-code');
    try {
      const res = await fetch(`/api/stats/${secretKey}/codes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newCode),
      });
      if (res.ok) {
        setNewCode({ code: '', value: 100 });
        await fetchGiftCodes();
        await fetchGameStatus();
      }
    } catch (err) {
      console.error('Error adding gift code:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleClaimAction = async (claimId: number, action: 'approve' | 'reject') => {
    setActionLoading(`claim-${claimId}`);
    try {
      const res = await fetch(`/api/stats/${secretKey}/claims/${claimId}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ review_notes: '' }),
      });
      const data = await res.json();
      if (data.success && action === 'approve' && data.redemption_token) {
        // Construct the URL from the token (don't use message which includes text)
        const redemptionUrl = `${window.location.origin}/redeem/${data.redemption_token}`;
        setRedemptionModal({
          url: redemptionUrl,
          message: 'Claim approved! Der Gewinner kann diesen Link nutzen, um seinen Gewinn einzulösen:'
        });
      }
      await fetchClaims();
      await fetchGameStatus();
    } catch (err) {
      console.error(`Error ${action}ing claim:`, err);
    } finally {
      setActionLoading(null);
    }
  };

  const resetGameStatus = async (status: string) => {
    setActionLoading('reset-status');
    try {
      const res = await fetch(`/api/stats/${secretKey}/game-status/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_status: status }),
      });
      if (res.ok) {
        await fetchGameStatus();
      }
    } catch (err) {
      console.error('Error resetting game status:', err);
    } finally {
      setActionLoading(null);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchOverview(),
        fetchConversations(),
        fetchGiftCodes(),
        fetchClaims(),
        fetchGameStatus(),
      ]);
      setLoading(false);
    };
    loadData();
  }, [fetchOverview, fetchConversations, fetchGiftCodes, fetchClaims, fetchGameStatus]);

  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation);
    }
  }, [selectedConversation, fetchMessages]);

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('de-DE');
  };

  if (error) {
    return (
      <main className="min-h-screen p-8 flex flex-col items-center justify-center relative z-10">
        <div className="terminal-window p-8 text-center">
          <div className="text-red-500 text-2xl mb-4">ACCESS DENIED</div>
          <p className="text-terminal-green/70">{error}</p>
          <Link href="/" className="mt-6 inline-block text-terminal-cyan hover:glow-text-frost">
            Zur Challenge
          </Link>
        </div>
      </main>
    );
  }

  if (loading) {
    return (
      <main className="min-h-screen p-8 flex flex-col items-center justify-center relative z-10">
        <div className="terminal-window p-8 text-center">
          <div className="text-terminal-green text-xl loading-dots">Lade Statistiken</div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-4 md:p-8 flex flex-col items-center relative z-10">
      {/* Header */}
      <header className="w-full max-w-6xl mb-6">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl md:text-3xl font-bold font-['Orbitron']">
            <span className="text-terminal-cyan glow-text-frost">ADMIN</span>
            {' '}
            <span className="text-terminal-green glow-text">STATS</span>
          </h1>
          <Link
            href="/"
            className="text-terminal-green/70 hover:text-terminal-green transition-colors text-sm"
          >
            Zur Challenge
          </Link>
        </div>
      </header>

      {/* Overview Stats */}
      {overview && (
        <div className="w-full max-w-6xl grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
          <StatCard
            label="Conversations"
            value={overview.total_conversations}
            icon="💬"
          />
          <StatCard
            label="Messages"
            value={overview.total_messages}
            icon="📝"
          />
          <StatCard
            label="Code Leaks"
            value={overview.conversations_with_leaks}
            icon="🚨"
            highlight={overview.conversations_with_leaks > 0}
          />
          <StatCard
            label="Code Detected"
            value={overview.messages_code_detected}
            icon="🔍"
          />
          <StatCard
            label="Referee Stops"
            value={overview.referee_stops}
            icon="🛑"
          />
          <StatCard
            label="24h Activity"
            value={overview.recent_conversations_24h}
            icon="📊"
          />
        </div>
      )}

      {/* Tab Navigation */}
      <div className="w-full max-w-6xl flex gap-2 mb-4 overflow-x-auto">
        {[
          { key: 'conversations' as TabType, label: '💬 Conversations', count: conversations.length },
          { key: 'codes' as TabType, label: '🎁 Gift Codes', count: giftCodes.filter(c => c.is_available).length },
          { key: 'claims' as TabType, label: '🏆 Claims', count: claims.filter(c => c.status === 'pending').length },
          { key: 'status' as TabType, label: '⚙️ Game Status' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-t-lg font-bold text-sm transition-all whitespace-nowrap ${
              activeTab === tab.key
                ? 'bg-terminal-green text-black'
                : 'bg-[#21262d] text-gray-400 hover:bg-[#30363d]'
            }`}
          >
            {tab.label}
            {tab.count !== undefined && tab.count > 0 && (
              <span className={`ml-2 px-1.5 py-0.5 rounded text-xs ${
                activeTab === tab.key ? 'bg-black/20' : 'bg-terminal-green/20 text-terminal-green'
              }`}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Conversations Tab */}
      {activeTab === 'conversations' && (
        <>
      {/* Conversations List */}
      <div className="w-full max-w-6xl terminal-window">
        <div className="terminal-header flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="terminal-dot red" />
            <div className="terminal-dot yellow" />
            <div className="terminal-dot green" />
            <span className="ml-4 text-sm opacity-50">
              📋 Conversations
            </span>
          </div>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={onlyLeaks}
              onChange={(e) => {
                setOnlyLeaks(e.target.checked);
                setSelectedConversation(null);
              }}
              className="accent-terminal-green"
            />
            <span className="text-terminal-green/70">Nur mit Leaks</span>
          </label>
        </div>

        <div className="p-4">
          {conversations.length === 0 ? (
            <div className="text-center text-terminal-green/50 py-8">
              Keine Conversations gefunden
            </div>
          ) : (
            <div className="space-y-2">
              {conversations.map((conv) => (
                <ConversationRow
                  key={conv.id}
                  conversation={conv}
                  isSelected={selectedConversation === conv.id}
                  onClick={() => setSelectedConversation(
                    selectedConversation === conv.id ? null : conv.id
                  )}
                  formatDate={formatDate}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Selected Conversation Details */}
      {selectedConversation && (
        <div className="w-full max-w-6xl terminal-window mt-6">
          <div className="terminal-header">
            <div className="terminal-dot red" />
            <div className="terminal-dot yellow" />
            <div className="terminal-dot green" />
            <span className="ml-4 text-sm opacity-50">
              🔍 Chat Detail: {selectedConversation}
            </span>
          </div>

          <div className="p-4">
            {loadingMessages ? (
              <div className="text-center text-terminal-green/70 py-4 loading-dots">
                Lade Nachrichten
              </div>
            ) : messages.length === 0 ? (
              <div className="text-center text-terminal-green/50 py-4">
                Keine Nachrichten gefunden
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg, idx) => (
                  <MessageCard key={msg.id} message={msg} index={idx} formatDate={formatDate} />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
        </>
      )}

      {/* Gift Codes Tab */}
      {activeTab === 'codes' && (
        <div className="w-full max-w-6xl terminal-window">
          <div className="terminal-header">
            <div className="terminal-dot red" />
            <div className="terminal-dot yellow" />
            <div className="terminal-dot green" />
            <span className="ml-4 text-sm opacity-50">🎁 Gift Codes</span>
          </div>
          <div className="p-4">
            {/* Add New Code Form */}
            <div className="flex gap-2 mb-4 p-4 bg-[#161b22] rounded-lg border border-[#30363d]">
              <input
                type="text"
                value={newCode.code}
                onChange={(e) => setNewCode({ ...newCode, code: e.target.value })}
                placeholder="Amazon Gift Code"
                className="flex-1 bg-[#0d1117] border border-[#30363d] rounded px-3 py-2 text-white font-mono"
              />
              <input
                type="number"
                value={newCode.value}
                onChange={(e) => setNewCode({ ...newCode, value: parseInt(e.target.value) || 0 })}
                placeholder="Wert in €"
                className="w-24 bg-[#0d1117] border border-[#30363d] rounded px-3 py-2 text-white"
              />
              <button
                onClick={addGiftCode}
                disabled={actionLoading === 'add-code' || !newCode.code.trim()}
                className="px-4 py-2 bg-terminal-green text-black font-bold rounded hover:bg-terminal-green/80 disabled:opacity-50"
              >
                {actionLoading === 'add-code' ? '...' : '+ Hinzufügen'}
              </button>
            </div>

            {/* Codes List */}
            <div className="space-y-2">
              {giftCodes.length === 0 ? (
                <div className="text-center text-terminal-green/50 py-8">
                  Keine Gift Codes vorhanden
                </div>
              ) : (
                giftCodes.map((code) => (
                  <div
                    key={code.id}
                    className={`p-3 rounded border ${
                      code.is_available
                        ? 'border-green-500/30 bg-green-500/5'
                        : 'border-red-500/30 bg-red-500/5'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        <span className={code.is_available ? 'text-green-400' : 'text-red-400'}>
                          {code.is_available ? '✓' : '✗'}
                        </span>
                        <code className="font-mono text-terminal-cyan">{code.code}</code>
                        <span className="text-yellow-400 font-bold">{code.value}€</span>
                      </div>
                      <div className="text-xs text-terminal-green/50">
                        {code.is_available ? (
                          `Hinzugefügt: ${formatDate(code.added_at)}`
                        ) : (
                          <>
                            <span className="text-red-400">Eingelöst: {formatDate(code.burned_at)}</span>
                            {code.winner_conversation_id && (
                              <span className="ml-2">({code.winner_conversation_id})</span>
                            )}
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Claims Tab */}
      {activeTab === 'claims' && (
        <div className="w-full max-w-6xl terminal-window">
          <div className="terminal-header">
            <div className="terminal-dot red" />
            <div className="terminal-dot yellow" />
            <div className="terminal-dot green" />
            <span className="ml-4 text-sm opacity-50">🏆 Winner Claims</span>
          </div>
          <div className="p-4">
            {claims.length === 0 ? (
              <div className="text-center text-terminal-green/50 py-8">
                Keine Claims vorhanden
              </div>
            ) : (
              <div className="space-y-4">
                {claims.map((claim) => (
                  <div
                    key={claim.id}
                    className={`p-4 rounded border ${
                      claim.status === 'pending'
                        ? 'border-yellow-500/30 bg-yellow-500/5'
                        : claim.status === 'approved'
                          ? 'border-green-500/30 bg-green-500/5'
                          : 'border-red-500/30 bg-red-500/5'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                          claim.status === 'pending'
                            ? 'bg-yellow-500/20 text-yellow-400'
                            : claim.status === 'approved'
                              ? 'bg-green-500/20 text-green-400'
                              : 'bg-red-500/20 text-red-400'
                        }`}>
                          {claim.status.toUpperCase()}
                        </span>
                        <span className="ml-2 text-xs text-terminal-green/50">
                          {formatDate(claim.created_at)}
                        </span>
                      </div>
                      {claim.status === 'pending' && (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleClaimAction(claim.id, 'approve')}
                            disabled={actionLoading === `claim-${claim.id}`}
                            className="px-3 py-1 bg-green-500 text-white text-sm font-bold rounded hover:bg-green-400 disabled:opacity-50"
                          >
                            ✓ Approve
                          </button>
                          <button
                            onClick={() => handleClaimAction(claim.id, 'reject')}
                            disabled={actionLoading === `claim-${claim.id}`}
                            className="px-3 py-1 bg-red-500 text-white text-sm font-bold rounded hover:bg-red-400 disabled:opacity-50"
                          >
                            ✗ Reject
                          </button>
                        </div>
                      )}
                    </div>
                    <div className="space-y-1 text-sm">
                      <div>
                        <span className="text-terminal-green/50">Conversation:</span>
                        <button
                          onClick={() => {
                            setActiveTab('conversations');
                            setSelectedConversation(claim.conversation_id);
                          }}
                          className="ml-2 font-mono text-terminal-cyan hover:underline"
                        >
                          {claim.conversation_id}
                        </button>
                      </div>
                      <div>
                        <span className="text-terminal-green/50">Claimed Code:</span>
                        <code className="ml-2 text-yellow-400">{claim.claimed_code}</code>
                      </div>
                      {claim.linkedin_profile && (
                        <div>
                          <span className="text-terminal-green/50">LinkedIn:</span>
                          <a 
                            href={claim.linkedin_profile.startsWith('http') ? claim.linkedin_profile : `https://${claim.linkedin_profile}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="ml-2 text-blue-400 hover:underline"
                          >
                            {claim.linkedin_profile}
                          </a>
                        </div>
                      )}
                      {claim.claim_message && (
                        <div>
                          <span className="text-terminal-green/50">Message:</span>
                          <span className="ml-2">{claim.claim_message}</span>
                        </div>
                      )}
                      {claim.review_notes && (
                        <div className="text-xs text-terminal-green/40 mt-2">
                          Review: {claim.review_notes} (by {claim.reviewed_by}, {formatDate(claim.reviewed_at)})
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Game Status Tab */}
      {activeTab === 'status' && gameStatus && (
        <div className="w-full max-w-6xl terminal-window">
          <div className="terminal-header">
            <div className="terminal-dot red" />
            <div className="terminal-dot yellow" />
            <div className="terminal-dot green" />
            <span className="ml-4 text-sm opacity-50">⚙️ Game Status</span>
          </div>
          <div className="p-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="p-4 bg-[#161b22] rounded-lg border border-[#30363d] text-center">
                <div className="text-xs text-terminal-green/50 mb-1">Status</div>
                <div className={`text-xl font-bold ${
                  gameStatus.status === 'active' ? 'text-green-400' :
                  gameStatus.status === 'won' ? 'text-yellow-400' :
                  gameStatus.status === 'pending_claim' ? 'text-blue-400' :
                  'text-gray-400'
                }`}>
                  {gameStatus.status.toUpperCase()}
                </div>
              </div>
              <div className="p-4 bg-[#161b22] rounded-lg border border-[#30363d] text-center">
                <div className="text-xs text-terminal-green/50 mb-1">Jackpot</div>
                <div className="text-xl font-bold text-yellow-400">{gameStatus.jackpot_value}€</div>
              </div>
              <div className="p-4 bg-[#161b22] rounded-lg border border-[#30363d] text-center">
                <div className="text-xs text-terminal-green/50 mb-1">Available Codes</div>
                <div className="text-xl font-bold text-terminal-green">{gameStatus.code_count}</div>
              </div>
              <div className="p-4 bg-[#161b22] rounded-lg border border-[#30363d] text-center">
                <div className="text-xs text-terminal-green/50 mb-1">Last Winner</div>
                <div className="text-sm text-terminal-cyan">
                  {gameStatus.last_winner_conversation_id || '-'}
                </div>
              </div>
            </div>

            {/* Reset Actions */}
            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <h3 className="text-red-400 font-bold mb-3">⚠️ Admin Actions</h3>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => resetGameStatus('active')}
                  disabled={actionLoading === 'reset-status' || gameStatus.status === 'active'}
                  className="px-4 py-2 bg-green-500 text-white font-bold rounded hover:bg-green-400 disabled:opacity-50"
                >
                  Set Active
                </button>
                <button
                  onClick={() => resetGameStatus('redeemed')}
                  disabled={actionLoading === 'reset-status'}
                  className="px-4 py-2 bg-gray-500 text-white font-bold rounded hover:bg-gray-400 disabled:opacity-50"
                >
                  Set Redeemed
                </button>
              </div>
              <p className="text-xs text-red-400/70 mt-2">
                Vorsicht: Diese Aktionen können den Spielstatus beeinflussen!
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Redemption URL Modal */}
      {redemptionModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-[#0d1117] border border-terminal-green/50 rounded-xl max-w-2xl w-full p-6 shadow-2xl">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold text-terminal-green flex items-center gap-2">
                <span className="text-2xl">✅</span>
                Claim Approved
              </h3>
              <button
                onClick={() => setRedemptionModal(null)}
                className="text-gray-400 hover:text-white transition-colors text-xl"
              >
                ✕
              </button>
            </div>
            
            <p className="text-terminal-green/70 mb-4">{redemptionModal.message}</p>
            
            <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 mb-4">
              <code className="text-sm text-terminal-cyan break-all select-all">
                {redemptionModal.url}
              </code>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(redemptionModal.url);
                }}
                className="flex-1 px-4 py-2 bg-terminal-green/20 text-terminal-green border border-terminal-green/50 rounded-lg hover:bg-terminal-green/30 transition-colors"
              >
                📋 URL kopieren
              </button>
              <button
                onClick={() => setRedemptionModal(null)}
                className="px-4 py-2 bg-[#21262d] text-gray-300 rounded-lg hover:bg-[#30363d] transition-colors"
              >
                Schließen
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

function StatCard({
  label,
  value,
  icon,
  highlight = false,
}: {
  label: string;
  value: number;
  icon: string;
  highlight?: boolean;
}) {
  return (
    <div className={`terminal-window p-4 text-center ${highlight ? 'border-red-500/50' : ''}`}>
      <div className="text-2xl mb-1">{icon}</div>
      <div className={`text-2xl font-bold font-['Orbitron'] ${highlight ? 'text-red-500' : 'text-terminal-green'}`}>
        {value.toLocaleString()}
      </div>
      <div className="text-xs text-terminal-green/50 mt-1">{label}</div>
    </div>
  );
}

function ConversationRow({
  conversation,
  isSelected,
  onClick,
  formatDate,
}: {
  conversation: ConversationSummary;
  isSelected: boolean;
  onClick: () => void;
  formatDate: (date: string | null) => string;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-3 rounded border transition-all ${
        isSelected
          ? 'border-terminal-cyan bg-terminal-cyan/10'
          : 'border-terminal-green/20 hover:border-terminal-green/50 hover:bg-terminal-green/5'
      }`}
    >
      <div className="flex flex-wrap justify-between items-start gap-2">
        <div className="flex items-center gap-2">
          {conversation.has_code_leak && (
            <span className="text-red-500" title="Code Leak detected">🚨</span>
          )}
          <span className="font-mono text-sm text-terminal-cyan">{conversation.id}</span>
        </div>
        <div className="flex items-center gap-4 text-xs text-terminal-green/50">
          <span>{conversation.message_count} Nachrichten</span>
          <span>{formatDate(conversation.created_at)}</span>
        </div>
      </div>
    </button>
  );
}

function MessageCard({
  message,
  index,
  formatDate,
}: {
  message: Message;
  index: number;
  formatDate: (date: string | null) => string;
}) {
  const [showDetails, setShowDetails] = useState(false);
  const isUser = message.role === 'user';
  const hasRefereeData = message.referee2_decision || message.referee3_decision;

  return (
    <div className={`rounded border p-4 ${
      message.code_detected
        ? 'border-red-500/50 bg-red-500/5'
        : isUser
          ? 'border-terminal-cyan/30 bg-terminal-cyan/5'
          : 'border-terminal-green/30 bg-terminal-green/5'
    }`}>
      {/* Header */}
      <div className="flex justify-between items-start mb-2">
        <div className="flex items-center gap-2">
          <span className={`text-sm font-bold ${isUser ? 'text-terminal-cyan' : 'text-terminal-green'}`}>
            {isUser ? '👤 User' : '🤖 Assistant'}
          </span>
          <span className="text-xs text-terminal-green/40">#{index + 1}</span>
          {message.code_detected && (
            <span className="text-xs text-red-500 bg-red-500/20 px-2 py-0.5 rounded">
              {message.detection_method || 'CODE DETECTED'}
            </span>
          )}
        </div>
        <span className="text-xs text-terminal-green/40">{formatDate(message.created_at)}</span>
      </div>

      {/* Content */}
      <div className="text-sm text-terminal-green/90 whitespace-pre-wrap mb-3 max-h-40 overflow-y-auto">
        {message.content}
      </div>

      {/* Sanitized content for user messages */}
      {isUser && message.sanitized_content && message.sanitized_content !== message.content && (
        <div className="text-xs text-terminal-amber/70 mb-3 p-2 bg-terminal-amber/10 rounded">
          <span className="font-bold">Sanitized:</span> {message.sanitized_content}
        </div>
      )}

      {/* Referee Section */}
      {hasRefereeData && (
        <div className="border-t border-terminal-green/20 pt-3 mt-3">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-xs text-terminal-cyan hover:glow-text-frost transition-all flex items-center gap-2"
          >
            <span>{showDetails ? '▼' : '▶'}</span>
            <span>Referee Protokoll</span>
            <RefereeStatusBadge decision={message.referee2_decision} label="R2" />
            <RefereeStatusBadge decision={message.referee3_decision} label="R3" />
          </button>

          {showDetails && (
            <div className="mt-3 space-y-3 text-xs">
              {message.referee2_decision && (
                <RefereeDetail
                  label="Referee 2"
                  decision={message.referee2_decision}
                  reasoning={message.referee2_reasoning}
                />
              )}
              {message.referee3_decision && (
                <RefereeDetail
                  label="Referee 3"
                  decision={message.referee3_decision}
                  reasoning={message.referee3_reasoning}
                />
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function RefereeStatusBadge({ decision, label }: { decision: string | null; label: string }) {
  if (!decision) return null;
  
  const isPass = decision === 'PASS';
  return (
    <span className={`px-1.5 py-0.5 rounded text-[10px] ${
      isPass ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
    }`}>
      {label}: {decision}
    </span>
  );
}

function RefereeDetail({
  label,
  decision,
  reasoning,
}: {
  label: string;
  decision: string;
  reasoning: string | null;
}) {
  const isPass = decision === 'PASS';
  
  return (
    <div className={`p-2 rounded ${isPass ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
      <div className="flex items-center gap-2 mb-1">
        <span className="font-bold text-terminal-green/70">{label}:</span>
        <span className={`font-bold ${isPass ? 'text-green-400' : 'text-red-400'}`}>
          {decision}
        </span>
      </div>
      {reasoning && (
        <div className="text-terminal-green/60 whitespace-pre-wrap">
          {reasoning}
        </div>
      )}
    </div>
  );
}

