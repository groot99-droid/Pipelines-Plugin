/**
 * HistoryManager.js - Undo/Redo System
 *
 * Implements command pattern with 50-step stack.
 */

export class HistoryManager {
  constructor(maxSteps = 50) {
    this.maxSteps = maxSteps;
    this.undoStack = [];
    this.redoStack = [];
    this.isProcessing = false;
  }

  /**
   * Push a new state to the history
   */
  push(state, action = '') {
    if (this.isProcessing) return;

    // Clear redo stack when new action is performed
    this.redoStack = [];

    // Add to undo stack
    this.undoStack.push({
      state: JSON.parse(JSON.stringify(state)),
      action,
      timestamp: Date.now()
    });

    // Limit stack size
    if (this.undoStack.length > this.maxSteps) {
      this.undoStack.shift();
    }
  }

  canUndo() {
    return this.undoStack.length > 0;
  }

  canRedo() {
    return this.redoStack.length > 0;
  }

  undo() {
    if (!this.canUndo()) return null;

    this.isProcessing = true;

    const current = this.undoStack.pop();
    this.redoStack.push(current);

    const previous = this.undoStack.length > 0
      ? this.undoStack[this.undoStack.length - 1]
      : null;

    this.isProcessing = false;

    return previous ? previous.state : null;
  }

  redo() {
    if (!this.canRedo()) return null;

    this.isProcessing = true;

    const next = this.redoStack.pop();
    this.undoStack.push(next);

    this.isProcessing = false;

    return next.state;
  }

  getUndoSize() {
    return this.undoStack.length;
  }

  getRedoSize() {
    return this.redoStack.length;
  }

  clear() {
    this.undoStack = [];
    this.redoStack = [];
  }

  getLastAction() {
    if (this.undoStack.length === 0) return null;
    return this.undoStack[this.undoStack.length - 1].action;
  }

  getNextAction() {
    if (this.redoStack.length === 0) return null;
    return this.redoStack[this.redoStack.length - 1].action;
  }
}

export default HistoryManager;
