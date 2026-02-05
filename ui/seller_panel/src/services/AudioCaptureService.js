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
    this.apiKey = import.meta.env.VITE_API_KEY || '';
    
    // Audio capture
    this.mediaStream = null;
    this.mediaRecorder = null;
    this.audioContext = null;
    this.audioChunkSequence = 0;
    this.isCapturing = false;
    
    // Event callbacks
    this.onTranscriptChunk = null;
    this.onQueryResponse = null;
    this.onStatusUpdate = null;
    this.onSummaryReady = null;
    this.onError = null;
    this.onConnectionStateChange = null;
  }
  
  /**
   * Get the API base URL
   */
  getApiBaseUrl() {
    return import.meta.env.VITE_API_URL || 'http://localhost:8000';
  }
  
  /**
   * Get the WebSocket URL for a call
   */
  getWebSocketUrl(callId) {
    const baseUrl = this.getApiBaseUrl();
    const wsUrl = baseUrl.replace('http', 'ws');
    return `${wsUrl}/ws/call/${callId}`;
  }
  
  /**
   * Create a call via REST API
   */
  async createCall(dealId, accountName, contactName) {
    const baseUrl = this.getApiBaseUrl();
    const response = await fetch(`${baseUrl}/api/calls/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.apiKey,
      },
      body: JSON.stringify({
        deal_id: dealId,
        account_name: accountName,
        contact_name: contactName,
      }),
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to create call' }));
      throw new Error(error.detail || 'Failed to create call');
    }
    
    return response.json();
  }
  
  /**
   * Connect to WebSocket for a call
   * First creates the call via REST API, then connects to WebSocket
   */
  async connect(callIdOrOptions, options = {}) {
    if (this.ws && this.connectionState === ConnectionState.CONNECTED) {
      console.warn('Already connected to a call. Disconnect first.');
      return false;
    }
    
    this.setConnectionState(ConnectionState.CONNECTING);
    
    try {
      // If options has dealId, create call first via REST API
      const dealId = options.dealId;
      const accountName = options.accountName;
      const contactName = options.contactName;
      
      let callId;
      
      if (dealId && accountName) {
        // Create call via REST API first
        console.log('Creating call via REST API...');
        const callData = await this.createCall(dealId, accountName, contactName);
        callId = callData.call_id;
        console.log('Call created:', callId);
      } else {
        // Use provided callId directly (for reconnection)
        callId = callIdOrOptions;
      }
      
      this.callId = callId;
      
      return new Promise((resolve, reject) => {
        const url = this.getWebSocketUrl(callId);
        console.log('Connecting to WebSocket:', url);
        
        this.ws = new WebSocket(url);
        
        this.ws.onopen = async () => {
          console.log('WebSocket connected');
          this.setConnectionState(ConnectionState.CONNECTED);
          this.reconnectAttempts = 0;
          
          // Start audio capture after WebSocket is connected
          const captureStarted = await this.startAudioCapture();
          if (!captureStarted) {
            console.warn('Audio capture failed to start, continuing without microphone');
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
      });
      
    } catch (error) {
      console.error('Failed to connect:', error);
      this.setConnectionState(ConnectionState.ERROR);
      this.handleError('Connection failed', error.message);
      throw error;
    }
  }
  
  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    // Stop audio capture first
    this.stopAudioCapture();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.callId = null;
    this.setConnectionState(ConnectionState.DISCONNECTED);
  }
  
  /**
   * Start capturing audio from microphone
   */
  async startAudioCapture() {
    if (this.isCapturing) {
      console.warn('Audio capture already running');
      return true;
    }
    
    try {
      // Request microphone access
      console.log('Requesting microphone access...');
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      
      console.log('Microphone access granted');
      
      // Create MediaRecorder for capturing audio chunks
      const mimeType = this.getSupportedMimeType();
      console.log('Using audio format:', mimeType);
      
      this.mediaRecorder = new MediaRecorder(this.mediaStream, {
        mimeType: mimeType,
        audioBitsPerSecond: 16000,
      });
      
      this.audioChunkSequence = 0;
      
      // Handle audio data
      this.mediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0 && this.connectionState === ConnectionState.CONNECTED) {
          await this.processAudioChunk(event.data);
        }
      };
      
      this.mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event.error);
        this.handleError('Audio capture error', event.error?.message);
      };
      
      // Start recording with 1-second chunks (good for real-time streaming)
      this.mediaRecorder.start(1000);
      this.isCapturing = true;
      
      console.log('Audio capture started');
      return true;
      
    } catch (error) {
      console.error('Failed to start audio capture:', error);
      
      let errorMessage = 'Microphone access denied';
      if (error.name === 'NotFoundError') {
        errorMessage = 'No microphone found';
      } else if (error.name === 'NotAllowedError') {
        errorMessage = 'Microphone permission denied. Please allow access.';
      }
      
      this.handleError('Audio capture failed', errorMessage);
      return false;
    }
  }
  
  /**
   * Stop audio capture
   */
  stopAudioCapture() {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
      console.log('MediaRecorder stopped');
    }
    
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
      console.log('Media stream stopped');
    }
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    this.mediaRecorder = null;
    this.isCapturing = false;
    this.audioChunkSequence = 0;
  }
  
  /**
   * Get supported audio MIME type
   */
  getSupportedMimeType() {
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/mp4',
    ];
    
    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }
    
    return 'audio/webm'; // Fallback
  }
  
  /**
   * Process and send audio chunk
   */
  async processAudioChunk(blob) {
    try {
      // Convert blob to base64
      const arrayBuffer = await blob.arrayBuffer();
      const base64 = this.arrayBufferToBase64(arrayBuffer);
      
      // Send via WebSocket
      this.sendAudioChunk(base64, this.audioChunkSequence);
      this.audioChunkSequence++;
      
    } catch (error) {
      console.error('Error processing audio chunk:', error);
    }
  }
  
  /**
   * Convert ArrayBuffer to Base64
   */
  arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
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
    const sent = this.send({
      type: WSMessageType.AUDIO_CHUNK,
      audio_data: audioData,
      chunk_sequence: sequence,
    });
    
    if (sent && sequence % 5 === 0) {
      console.log(`Sent audio chunk #${sequence}`);
    }
    
    return sent;
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
  
  /**
   * Check if audio capture is active
   */
  isAudioCaptureActive() {
    return this.isCapturing;
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
