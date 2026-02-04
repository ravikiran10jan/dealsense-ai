/**
 * AudioCaptureService - WebSocket client for Live Call Assistant
 * 
 * Manages WebSocket connection to backend for:
 * - Real-time transcript streaming
 * - Push-to-talk queries
 * - Call lifecycle (start, end)
 * - Status updates
 */

// Message types (matching backend)
export const WSMessageType = {
  // Client -> Server
  START_CALL: 'start_call',
  AUDIO_CHUNK: 'audio_chunk',
  PUSH_TO_TALK_QUERY: 'push_to_talk_query',
  END_CALL: 'end_call',
  
  // Server -> Client
  TRANSCRIPT_CHUNK: 'transcript_chunk',
  QUERY_RESPONSE: 'query_response',
  STATUS_UPDATE: 'status_update',
  SUMMARY_READY: 'summary_ready',
  ERROR: 'error',
};

// Connection states
export const ConnectionState = {
  DISCONNECTED: 'disconnected',
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  ERROR: 'error',
};

class AudioCaptureService {
  constructor() {
    this.ws = null;
    this.callId = null;
    this.connectionState = ConnectionState.DISCONNECTED;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 3;
    this.reconnectDelay = 2000;
    
    // Event callbacks
    this.onTranscriptChunk = null;
    this.onQueryResponse = null;
    this.onStatusUpdate = null;
    this.onSummaryReady = null;
    this.onError = null;
    this.onConnectionStateChange = null;
  }
  
  /**
   * Get the WebSocket URL for a call
   */
  getWebSocketUrl(callId) {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const wsUrl = baseUrl.replace('http', 'ws');
    return `${wsUrl}/ws/call/${callId}`;
  }
  
  /**
   * Connect to WebSocket for a call
   */
  async connect(callId, options = {}) {
    if (this.ws && this.connectionState === ConnectionState.CONNECTED) {
      console.warn('Already connected to a call. Disconnect first.');
      return false;
    }
    
    this.callId = callId;
    this.setConnectionState(ConnectionState.CONNECTING);
    
    return new Promise((resolve, reject) => {
      try {
        const url = this.getWebSocketUrl(callId);
        console.log('Connecting to WebSocket:', url);
        
        this.ws = new WebSocket(url);
        
        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.setConnectionState(ConnectionState.CONNECTED);
          this.reconnectAttempts = 0;
          
          // Send start_call message if options provided
          if (options.dealId && options.accountName) {
            this.sendStartCall(options.dealId, options.accountName, options.contactName);
          }
          
          resolve(true);
        };
        
        this.ws.onmessage = (event) => {
          this.handleMessage(event.data);
        };
        
        this.ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          this.setConnectionState(ConnectionState.DISCONNECTED);
          
          // Attempt reconnect if not intentional close
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect();
          }
        };
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.setConnectionState(ConnectionState.ERROR);
          this.handleError('Connection error', error.message);
          reject(error);
        };
        
      } catch (error) {
        console.error('Failed to connect:', error);
        this.setConnectionState(ConnectionState.ERROR);
        reject(error);
      }
    });
  }
  
  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.callId = null;
    this.setConnectionState(ConnectionState.DISCONNECTED);
  }
  
  /**
   * Attempt to reconnect after disconnect
   */
  attemptReconnect() {
    this.reconnectAttempts++;
    console.log(`Reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
    
    setTimeout(() => {
      if (this.callId) {
        this.connect(this.callId).catch(() => {
          console.error('Reconnect failed');
        });
      }
    }, this.reconnectDelay * this.reconnectAttempts);
  }
  
  /**
   * Set connection state and notify listeners
   */
  setConnectionState(state) {
    this.connectionState = state;
    if (this.onConnectionStateChange) {
      this.onConnectionStateChange(state);
    }
  }
  
  /**
   * Send a message through WebSocket
   */
  send(message) {
    if (!this.ws || this.connectionState !== ConnectionState.CONNECTED) {
      console.error('WebSocket not connected');
      return false;
    }
    
    const messageWithTimestamp = {
      ...message,
      call_id: this.callId,
      timestamp: new Date().toISOString(),
    };
    
    this.ws.send(JSON.stringify(messageWithTimestamp));
    return true;
  }
  
  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(data) {
    try {
      const message = JSON.parse(data);
      
      switch (message.type) {
        case WSMessageType.TRANSCRIPT_CHUNK:
          if (this.onTranscriptChunk) {
            this.onTranscriptChunk({
              speaker: message.speaker,
              text: message.text,
              startTime: message.start_time,
              endTime: message.end_time,
              isFinal: message.is_final,
            });
          }
          break;
          
        case WSMessageType.QUERY_RESPONSE:
          if (this.onQueryResponse) {
            this.onQueryResponse({
              answer: message.answer,
              sources: message.sources || [],
              confidence: message.confidence || 1.0,
            });
          }
          break;
          
        case WSMessageType.STATUS_UPDATE:
          if (this.onStatusUpdate) {
            this.onStatusUpdate({
              status: message.status,
              message: message.message,
            });
          }
          break;
          
        case WSMessageType.SUMMARY_READY:
          if (this.onSummaryReady) {
            this.onSummaryReady({
              summaryId: message.summary_id,
            });
          }
          break;
          
        case WSMessageType.ERROR:
          this.handleError(message.error, message.details);
          break;
          
        default:
          console.warn('Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('Failed to parse message:', error);
    }
  }
  
  /**
   * Handle errors
   */
  handleError(error, details) {
    console.error('Call error:', error, details);
    if (this.onError) {
      this.onError({ error, details });
    }
  }
  
  // ==================== Message Senders ====================
  
  /**
   * Send start_call message
   */
  sendStartCall(dealId, accountName, contactName = null) {
    return this.send({
      type: WSMessageType.START_CALL,
      deal_id: dealId,
      account_name: accountName,
      contact_name: contactName,
    });
  }
  
  /**
   * Send push-to-talk query
   */
  sendQuery(query, dealId = null) {
    return this.send({
      type: WSMessageType.PUSH_TO_TALK_QUERY,
      query: query,
      deal_id: dealId,
    });
  }
  
  /**
   * Send end_call message
   */
  sendEndCall() {
    return this.send({
      type: WSMessageType.END_CALL,
    });
  }
  
  /**
   * Send audio chunk (for future use with real audio capture)
   */
  sendAudioChunk(audioData, sequence) {
    return this.send({
      type: WSMessageType.AUDIO_CHUNK,
      audio_data: audioData,
      chunk_sequence: sequence,
    });
  }
  
  // ==================== Event Handlers ====================
  
  /**
   * Set callback for transcript chunks
   */
  setOnTranscriptChunk(callback) {
    this.onTranscriptChunk = callback;
  }
  
  /**
   * Set callback for query responses
   */
  setOnQueryResponse(callback) {
    this.onQueryResponse = callback;
  }
  
  /**
   * Set callback for status updates
   */
  setOnStatusUpdate(callback) {
    this.onStatusUpdate = callback;
  }
  
  /**
   * Set callback for summary ready
   */
  setOnSummaryReady(callback) {
    this.onSummaryReady = callback;
  }
  
  /**
   * Set callback for errors
   */
  setOnError(callback) {
    this.onError = callback;
  }
  
  /**
   * Set callback for connection state changes
   */
  setOnConnectionStateChange(callback) {
    this.onConnectionStateChange = callback;
  }
  
  // ==================== Getters ====================
  
  /**
   * Check if connected
   */
  isConnected() {
    return this.connectionState === ConnectionState.CONNECTED;
  }
  
  /**
   * Get current call ID
   */
  getCallId() {
    return this.callId;
  }
  
  /**
   * Get connection state
   */
  getConnectionState() {
    return this.connectionState;
  }
}

// Singleton instance
let audioCaptureService = null;

export function getAudioCaptureService() {
  if (!audioCaptureService) {
    audioCaptureService = new AudioCaptureService();
  }
  return audioCaptureService;
}

export default AudioCaptureService;
