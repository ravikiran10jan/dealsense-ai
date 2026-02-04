/**
 * useHotkeyManager - Custom hook for global hotkey management
 * 
 * Features:
 * - Detects Ctrl+Space (or configurable hotkey) for push-to-talk
 * - Manages push-to-talk state
 * - Prevents conflicts with browser defaults
 * - Disabled when input fields are focused
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// Default hotkey configuration
const DEFAULT_HOTKEY = {
  key: ' ', // Space
  ctrlKey: true,
  shiftKey: false,
  altKey: false,
  metaKey: false,
};

/**
 * Check if an element is an input element
 */
function isInputElement(element) {
  if (!element) return false;
  
  const tagName = element.tagName.toLowerCase();
  const isInput = tagName === 'input' || tagName === 'textarea' || tagName === 'select';
  const isContentEditable = element.isContentEditable;
  
  return isInput || isContentEditable;
}

/**
 * Check if a keyboard event matches the hotkey configuration
 */
function matchesHotkey(event, hotkey) {
  return (
    event.key === hotkey.key &&
    event.ctrlKey === hotkey.ctrlKey &&
    event.shiftKey === hotkey.shiftKey &&
    event.altKey === hotkey.altKey &&
    event.metaKey === hotkey.metaKey
  );
}

/**
 * useHotkeyManager - Hook for managing push-to-talk hotkey
 * 
 * @param {Object} options - Configuration options
 * @param {boolean} options.enabled - Whether hotkey detection is enabled
 * @param {Object} options.hotkey - Hotkey configuration (default: Ctrl+Space)
 * @param {Function} options.onActivate - Callback when hotkey is pressed
 * @param {Function} options.onDeactivate - Callback when hotkey is released
 * @param {boolean} options.holdMode - If true, active while holding; if false, toggle mode
 * 
 * @returns {Object} Hook state and controls
 */
export function useHotkeyManager({
  enabled = true,
  hotkey = DEFAULT_HOTKEY,
  onActivate = null,
  onDeactivate = null,
  holdMode = true,
} = {}) {
  const [isActive, setIsActive] = useState(false);
  const [lastActivation, setLastActivation] = useState(null);
  const isActiveRef = useRef(false);
  
  // Handle keydown event
  const handleKeyDown = useCallback((event) => {
    // Skip if disabled
    if (!enabled) return;
    
    // Skip if focus is on input element
    if (isInputElement(document.activeElement)) return;
    
    // Check if matches hotkey
    if (matchesHotkey(event, hotkey)) {
      // Prevent browser default (e.g., scroll on space)
      event.preventDefault();
      event.stopPropagation();
      
      // Skip if already active (key repeat)
      if (isActiveRef.current) return;
      
      // Activate
      isActiveRef.current = true;
      setIsActive(true);
      setLastActivation(new Date());
      
      if (onActivate) {
        onActivate();
      }
    }
  }, [enabled, hotkey, onActivate]);
  
  // Handle keyup event
  const handleKeyUp = useCallback((event) => {
    // Skip if disabled
    if (!enabled) return;
    
    // Check if matches hotkey (for release)
    if (event.key === hotkey.key) {
      // Only deactivate if was active and in hold mode
      if (isActiveRef.current && holdMode) {
        isActiveRef.current = false;
        setIsActive(false);
        
        if (onDeactivate) {
          onDeactivate();
        }
      }
    }
  }, [enabled, hotkey, holdMode, onDeactivate]);
  
  // Handle window blur (deactivate if window loses focus)
  const handleBlur = useCallback(() => {
    if (isActiveRef.current) {
      isActiveRef.current = false;
      setIsActive(false);
      
      if (onDeactivate) {
        onDeactivate();
      }
    }
  }, [onDeactivate]);
  
  // Toggle mode activation (for non-hold mode)
  const toggle = useCallback(() => {
    if (!holdMode) {
      const newState = !isActiveRef.current;
      isActiveRef.current = newState;
      setIsActive(newState);
      
      if (newState && onActivate) {
        onActivate();
      } else if (!newState && onDeactivate) {
        onDeactivate();
      }
    }
  }, [holdMode, onActivate, onDeactivate]);
  
  // Manual deactivate
  const deactivate = useCallback(() => {
    if (isActiveRef.current) {
      isActiveRef.current = false;
      setIsActive(false);
      
      if (onDeactivate) {
        onDeactivate();
      }
    }
  }, [onDeactivate]);
  
  // Setup event listeners
  useEffect(() => {
    if (enabled) {
      window.addEventListener('keydown', handleKeyDown, { capture: true });
      window.addEventListener('keyup', handleKeyUp, { capture: true });
      window.addEventListener('blur', handleBlur);
      
      return () => {
        window.removeEventListener('keydown', handleKeyDown, { capture: true });
        window.removeEventListener('keyup', handleKeyUp, { capture: true });
        window.removeEventListener('blur', handleBlur);
      };
    }
  }, [enabled, handleKeyDown, handleKeyUp, handleBlur]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isActiveRef.current && onDeactivate) {
        onDeactivate();
      }
    };
  }, [onDeactivate]);
  
  return {
    isActive,
    lastActivation,
    toggle,
    deactivate,
    hotkeyLabel: getHotkeyLabel(hotkey),
  };
}

/**
 * Get human-readable label for hotkey
 */
function getHotkeyLabel(hotkey) {
  const parts = [];
  
  if (hotkey.ctrlKey) parts.push('Ctrl');
  if (hotkey.shiftKey) parts.push('Shift');
  if (hotkey.altKey) parts.push('Alt');
  if (hotkey.metaKey) parts.push('Cmd');
  
  // Format key
  let key = hotkey.key;
  if (key === ' ') key = 'Space';
  if (key.length === 1) key = key.toUpperCase();
  parts.push(key);
  
  return parts.join('+');
}

/**
 * usePushToTalk - Simplified hook specifically for push-to-talk functionality
 * 
 * @param {Object} options
 * @param {boolean} options.enabled - Whether push-to-talk is enabled
 * @param {Function} options.onStart - Called when push-to-talk starts
 * @param {Function} options.onEnd - Called when push-to-talk ends
 * 
 * @returns {Object} Hook state
 */
export function usePushToTalk({
  enabled = true,
  onStart = null,
  onEnd = null,
} = {}) {
  const {
    isActive,
    lastActivation,
    hotkeyLabel,
    deactivate,
  } = useHotkeyManager({
    enabled,
    onActivate: onStart,
    onDeactivate: onEnd,
    holdMode: true,
  });
  
  return {
    isListening: isActive,
    lastActivation,
    hotkeyLabel,
    stopListening: deactivate,
  };
}

export default useHotkeyManager;
